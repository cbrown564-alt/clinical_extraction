#!/usr/bin/env python3
"""Gan unknown_sentinel clinical-selection / free-interval harm audit.

No new model calls. See
docs/research/gan2026_unknown_sentinel_clinical_harm_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_KEY = 2
TARGET_BUCKET = "unknown_sentinel"

_STAGE_PATH = REPO_ROOT / "scripts/build_gan2026_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("gan_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)
cat = stage.cat
hs = stage.hs

CLINICAL_AND_FREE = tuple(
    name
    for name in stage.REPAIR_STAGE_ORDER
    if stage.STAGE_BAND[name] in {"clinical_selection", "free_interval"}
)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _pick_examples(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = stage.MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(stage.MODEL_PREFERENCE)
        effect_rank = 0 if row.get("effect") == "harm" else 1
        return effect_rank, model_rank, str(row["source_row_index"])

    picked: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for row in sorted(candidates, key=sort_key):
        key = (str(row["model_slug"]), int(row["source_row_index"]))
        if key in seen:
            continue
        picked.append(row)
        seen.add(key)
        if len(picked) >= EXAMPLES_PER_KEY:
            break
    return picked


def build_artifact() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()
    band_modes: dict[str, list[str]] = defaultdict(list)
    band_correct: Counter[str] = Counter()
    n_cells = 0
    fidelity = {"replayable": 0, "unreplayable": 0}

    family_stats: dict[str, dict[str, Any]] = {
        name: {
            "band": stage.STAGE_BAND[name],
            "fires": 0,
            "first_changer": 0,
            "first_rescue": 0,
            "first_harm": 0,
            "any_rescue": 0,
            "any_harm": 0,
            "examples_rescue": [],
            "examples_harm": [],
            "harm_mode_after": Counter(),
        }
        for name in CLINICAL_AND_FREE
    }
    pathway_counter: Counter[str] = Counter()
    residual = Counter()
    evidence_to_clinical_delta: Counter[str] = Counter()
    clinical_to_final_delta: Counter[str] = Counter()

    for slug, display in hs.MODEL_SPECS:
        rows = hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_with_rules.jsonl")
        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            if str(meta["a_priori_bucket"]) != TARGET_BUCKET:
                continue
            gold_label = str(meta["gold_label"])
            replay = stage.replay_row(row)
            if replay is None or not replay["replayable"]:
                fidelity["unreplayable"] += 1
                continue
            fidelity["replayable"] += 1
            n_cells += 1

            band_labels = replay["band_labels"]
            band_ok: dict[str, bool] = {}
            band_mode: dict[str, str] = {}
            for band in (
                "evidence_reconcile",
                "clinical_selection",
                "free_interval",
            ):
                pred = band_labels.get(band)
                ok = stage._purist_correct(pred, gold_label) if pred else False
                mode = stage._error_mode_for(TARGET_BUCKET, pred, ok)
                band_ok[band] = ok
                band_mode[band] = mode
                band_modes[band].append(mode)
                if ok:
                    band_correct[band] += 1

            clinical_free_changes = [
                change
                for change in replay["changes"]
                if change["stage"] in CLINICAL_AND_FREE
            ]
            pathway = (
                "no_clinical_or_free_change"
                if not clinical_free_changes
                else " → ".join(
                    item["stage"].removeprefix("repair.")
                    for item in clinical_free_changes
                )
            )
            pathway_counter[pathway] += 1

            first_marked = False
            for change in clinical_free_changes:
                stage_id = change["stage"]
                stats = family_stats[stage_id]
                stats["fires"] += 1
                before_ok = stage._purist_correct(change["before"], gold_label)
                after_ok = stage._purist_correct(change["after"], gold_label)
                effect = "neutral"
                if after_ok and not before_ok:
                    effect = "rescue"
                    stats["any_rescue"] += 1
                elif before_ok and not after_ok:
                    effect = "harm"
                    stats["any_harm"] += 1
                    after_mode = stage._error_mode_for(
                        TARGET_BUCKET, change["after"], False
                    )
                    stats["harm_mode_after"][after_mode] += 1

                example = {
                    "stage": stage_id,
                    "band": stage.STAGE_BAND[stage_id],
                    "effect": effect,
                    "before_label": change["before"],
                    "after_label": change["after"],
                    "final_label": replay["final"],
                    "gold_label": gold_label,
                    "before_purist_ok": before_ok,
                    "after_purist_ok": after_ok,
                    "model_slug": slug,
                    "model_display": display,
                    "source_row_index": index,
                    "selected_evidence": replay.get("selected_evidence"),
                    "pathway": pathway,
                }
                if effect == "rescue":
                    stats["examples_rescue"].append(example)
                elif effect == "harm":
                    stats["examples_harm"].append(example)

                if not first_marked:
                    first_marked = True
                    stats["first_changer"] += 1
                    if effect == "rescue":
                        stats["first_rescue"] += 1
                    elif effect == "harm":
                        stats["first_harm"] += 1

            if band_ok["free_interval"]:
                if clinical_free_changes:
                    residual["final_correct_after_clinical_or_free"] += 1
                else:
                    residual["final_correct_no_clinical_or_free"] += 1
            elif clinical_free_changes:
                residual["final_wrong_after_clinical_or_free"] += 1
            else:
                residual["final_wrong_no_clinical_or_free"] += 1

    evidence_modes = Counter(band_modes["evidence_reconcile"])
    clinical_modes = Counter(band_modes["clinical_selection"])
    final_modes = Counter(band_modes["free_interval"])
    for mode in set(evidence_modes) | set(clinical_modes):
        if mode == "correct":
            continue
        delta = clinical_modes.get(mode, 0) - evidence_modes.get(mode, 0)
        if delta:
            evidence_to_clinical_delta[mode] = delta
    for mode in set(clinical_modes) | set(final_modes):
        if mode == "correct":
            continue
        delta = final_modes.get(mode, 0) - clinical_modes.get(mode, 0)
        if delta:
            clinical_to_final_delta[mode] = delta

    families_out = {}
    for name, stats in family_stats.items():
        families_out[name] = {
            "band": stats["band"],
            "fires": stats["fires"],
            "first_changer": stats["first_changer"],
            "first_rescue": stats["first_rescue"],
            "first_harm": stats["first_harm"],
            "any_rescue": stats["any_rescue"],
            "any_harm": stats["any_harm"],
            "harm_mode_after": dict(
                sorted(
                    stats["harm_mode_after"].items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "examples_rescue": _pick_examples(stats["examples_rescue"]),
            "examples_harm": _pick_examples(stats["examples_harm"]),
        }

    band_table = {}
    for band in ("evidence_reconcile", "clinical_selection", "free_interval"):
        modes = Counter(band_modes[band])
        wrong = {k: v for k, v in modes.items() if k != "correct"}
        band_table[band] = {
            "n": n_cells,
            "accuracy": round(band_correct[band] / n_cells, 4) if n_cells else 0.0,
            "n_correct": band_correct[band],
            "wrong_mode_counts": dict(
                sorted(wrong.items(), key=lambda item: (-item[1], item[0]))
            ),
        }

    artifact = {
        "schema_version": "gan2026.unknown_sentinel_clinical_harm.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/gan2026_unknown_sentinel_clinical_harm_protocol_2026-08-06.md"
        ),
        "parent_synthesis": (
            "docs/research/cross_task_hybrid_mechanism_synthesis_2026-08-06.md"
        ),
        "git": _git_note(),
        "dataset": "Gan 2026",
        "split": "validation / dev750",
        "surface": "llm_with_rules",
        "gold_bucket": TARGET_BUCKET,
        "n_row_model_cells": n_cells,
        "fidelity": fidelity,
        "bands": band_table,
        "mode_delta_evidence_to_clinical": dict(
            sorted(
                evidence_to_clinical_delta.items(),
                key=lambda item: (-abs(item[1]), item[0]),
            )
        ),
        "mode_delta_clinical_to_final": dict(
            sorted(
                clinical_to_final_delta.items(),
                key=lambda item: (-abs(item[1]), item[0]),
            )
        ),
        "families": families_out,
        "top_pathways": [
            {"pathway": path, "count": count}
            for path, count in pathway_counter.most_common(12)
        ],
        "residual_ownership": dict(residual),
        "claim_boundary": (
            "Development unknown-gold clinical/free harm audit on Gan dev750. "
            "Not leave-one-family-out; not a repair rewrite; not holdout."
        ),
    }
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    bands = artifact["bands"]
    families = artifact["families"]
    harm_ranked = sorted(
        (
            (name, stats)
            for name, stats in families.items()
            if stats["any_harm"] or stats["fires"]
        ),
        key=lambda item: (-item[1]["any_harm"], -item[1]["fires"], item[0]),
    )
    top_harm = next(
        (name for name, stats in harm_ranked if stats["any_harm"] > 0),
        None,
    )
    lines = [
        "# Gan unknown_sentinel clinical-selection harm",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development residual audit on unknown gold  ",
        "Protocol: [unknown_sentinel clinical harm protocol]"
        "(gan2026_unknown_sentinel_clinical_harm_protocol_2026-08-06.md)  ",
        "Parent: [cross-task hybrid mechanism synthesis]"
        "(cross_task_hybrid_mechanism_synthesis_2026-08-06.md)  ",
        "Companion: [Gan hybrid stage ablation]"
        "(gan2026_hybrid_stage_ablation_2026-08-06.md)  ",
        f"Artifact: [`experiments/gan2026_unknown_sentinel_clinical_harm_{DATE_STAMP}.json`]"
        f"(../../experiments/gan2026_unknown_sentinel_clinical_harm_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
    ]
    ev = bands["evidence_reconcile"]["accuracy"]
    clin = bands["clinical_selection"]["accuracy"]
    final = bands["free_interval"]["accuracy"]
    lines.extend(
        [
            f"On {artifact['n_row_model_cells']} unknown-gold row×model cells, "
            f"Purist accuracy is **{ev:.2f}** after evidence reconcile, "
            f"**{clin:.2f}** after clinical selection, and **{final:.2f}** at final.",
            "",
        ]
    )
    if clin < ev:
        lines.append(
            "Clinical selection is the accuracy drop. It asserts active rates or "
            "seizure-free labels onto abstention gold."
        )
    else:
        lines.append(
            "Clinical selection does not show a large accuracy drop on this replay; "
            "inspect family harm counts below."
        )
    if top_harm:
        stats = families[top_harm]
        lines.append(
            f"Largest any-harm family: `{top_harm}` "
            f"({stats['any_harm']} any-harm / {stats['any_rescue']} any-rescue)."
        )
    lines.extend(
        [
            "",
            "## Band endpoints on unknown gold",
            "",
            "| Band | Acc | Top wrong modes |",
            "| --- | ---: | --- |",
        ]
    )
    for band, label in (
        ("evidence_reconcile", "After evidence reconcile"),
        ("clinical_selection", "After clinical selection"),
        ("free_interval", "Final"),
    ):
        payload = bands[band]
        modes = ", ".join(
            f"`{k}` {v}" for k, v in list(payload["wrong_mode_counts"].items())[:3]
        )
        lines.append(f"| {label} | {payload['accuracy']:.2f} | {modes or '—'} |")

    delta = artifact["mode_delta_evidence_to_clinical"]
    if delta:
        lines.extend(
            [
                "",
                "Mode Δ evidence → clinical (negative = mode shrank): "
                + ", ".join(f"`{k}` {v:+d}" for k, v in delta.items())
                + ".",
            ]
        )

    lines.extend(
        [
            "",
            "## Clinical / free-interval family ledger (unknown gold only)",
            "",
            "| Stage | Band | Fires | First | Rescue | Harm | Any+ | Any- |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name in CLINICAL_AND_FREE:
        stats = families[name]
        lines.append(
            f"| `{name}` | {stats['band']} | {stats['fires']} | "
            f"{stats['first_changer']} | {stats['first_rescue']} | "
            f"{stats['first_harm']} | {stats['any_rescue']} | "
            f"{stats['any_harm']} |"
        )

    lines.extend(["", "### Harm shapes by family", ""])
    for name, stats in harm_ranked:
        if not stats["any_harm"]:
            continue
        modes = ", ".join(
            f"`{k}` {v}" for k, v in list(stats["harm_mode_after"].items())[:4]
        )
        lines.append(f"- `{name}`: {modes or '—'}")
        for ex in stats["examples_harm"][:1]:
            lines.append(
                f"  - Example: row {ex['source_row_index']} / {ex['model_display']}: "
                f"`{ex['before_label']}` → `{ex['after_label']}` "
                f"(gold `{ex['gold_label']}`)."
            )

    lines.extend(
        [
            "",
            "## Residual ownership after clinical/free hops",
            "",
            "| Outcome | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in artifact["residual_ownership"].items():
        lines.append(f"| `{key}` | {count} |")

    lines.extend(
        [
            "",
            "## Top pathways (clinical/free only)",
            "",
            "| Pathway | Count |",
            "| --- | ---: |",
        ]
    )
    for row in artifact["top_pathways"][:8]:
        lines.append(f"| `{row['pathway']}` | {row['count']} |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Unknown-gold hybrid damage after evidence reconcile is concentrated "
            "in clinical-selection assertion families, not missing format cleanup. "
            "This audit localizes the harm; it does **not** authorize turning those "
            "families off without a predeclared leave-one-family-out or guarded "
            "repair study.",
            "",
            "## Next",
            "",
            "1. Optional: leave-one-family-out on the top harm family for unknown "
            "gold only (still no-call).",
            "2. Do not change production repairs from this page alone.",
            "3. Operational primary remains the vLLM dev10 task.",
            "",
            "## Method",
            "",
            "- Split: Gan `dev750`, gold bucket `unknown_sentinel` only.",
            "- Replay: same ordered stack as the Gan hybrid stage ablation.",
            "- Attribution: first clinical/free label-changing hop; any-rescue/"
            "harm count later hops too.",
            f"- Git: `{artifact['git']['commit']}`"
            f"{' (dirty tree)' if artifact['git']['dirty_tree'] else ''}.",
            "",
            "## Claim boundary",
            "",
            artifact["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT
        / f"experiments/gan2026_unknown_sentinel_clinical_harm_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/gan2026_unknown_sentinel_clinical_harm_{REPORT_DATE}.md",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    print(
        "cells",
        artifact["n_row_model_cells"],
        "ev",
        artifact["bands"]["evidence_reconcile"]["accuracy"],
        "clin",
        artifact["bands"]["clinical_selection"]["accuracy"],
        "final",
        artifact["bands"]["free_interval"]["accuracy"],
    )


if __name__ == "__main__":
    main()
