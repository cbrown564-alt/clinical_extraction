#!/usr/bin/env python3
"""Gan unknown-gold leave-one-family-out for repair.breakthrough.

No new model calls. Study-local omit via replay_row; production defaults
unchanged. See docs/research/gan2026/unknown_breakthrough_loo_protocol_2026-08-06.md.
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
EXAMPLES_PER_KEY = 3
TARGET_BUCKET = "unknown_sentinel"
OMIT_STAGE = "repair.breakthrough"
OMIT = frozenset({OMIT_STAGE})

_STAGE_PATH = REPO_ROOT / "scripts/build_gan2026_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("gan_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)
hs = stage.hs


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


def _purist_ok(pred: str | None, gold: str) -> bool:
    return bool(stage._purist_correct(pred, gold))


def _mode(pred: str | None, gold: str, *, purist_ok: bool) -> str:
    return str(stage._error_mode_for(TARGET_BUCKET, pred, purist_ok))


def _stage_fired(replay: dict[str, Any], stage_id: str) -> bool:
    return any(change["stage"] == stage_id for change in replay["changes"])


def _later_stages(replay: dict[str, Any]) -> list[str]:
    breakthrough_idx = stage.REPAIR_STAGE_ORDER.index(OMIT_STAGE)
    return [
        change["stage"]
        for change in replay["changes"]
        if stage.REPAIR_STAGE_ORDER.index(change["stage"]) > breakthrough_idx
    ]


def _pick_examples(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = stage.MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(stage.MODEL_PREFERENCE)
        return model_rank, int(row["source_row_index"]), slug

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


def _arm_summary(
    *,
    n: int,
    correct: int,
    clinical_correct: int,
    modes_final: Counter[str],
    modes_clinical: Counter[str],
) -> dict[str, Any]:
    return {
        "n_cells": n,
        "final_correct": correct,
        "final_accuracy": round(correct / n, 4) if n else None,
        "clinical_selection_correct": clinical_correct,
        "clinical_selection_accuracy": round(clinical_correct / n, 4) if n else None,
        "final_wrong_modes": dict(modes_final.most_common()),
        "clinical_wrong_modes": dict(modes_clinical.most_common()),
    }


def build_artifact() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()

    unknown: dict[str, Any] = {
        "default": {
            "correct": 0,
            "clinical_correct": 0,
            "modes_final": Counter(),
            "modes_clinical": Counter(),
            "n": 0,
        },
        "omit": {
            "correct": 0,
            "clinical_correct": 0,
            "modes_final": Counter(),
            "modes_clinical": Counter(),
            "n": 0,
        },
    }
    full = {
        "default_correct": 0,
        "omit_correct": 0,
        "n": 0,
        "by_bucket": defaultdict(lambda: {"n": 0, "default_correct": 0, "omit_correct": 0}),
    }
    fidelity = {"replayable": 0, "unreplayable": 0}

    unknown_disagree: list[dict[str, Any]] = []
    unknown_rescue: list[dict[str, Any]] = []
    unknown_harm: list[dict[str, Any]] = []
    spillover_unknown: list[dict[str, Any]] = []
    breakthrough_fire_cells = 0
    breakthrough_fire_unknown = 0
    full_rescue = 0
    full_harm = 0
    full_disagree_by_bucket: Counter[str] = Counter()
    full_rescue_by_bucket: Counter[str] = Counter()
    full_harm_by_bucket: Counter[str] = Counter()

    for slug, display in hs.MODEL_SPECS:
        rows = hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_with_rules.jsonl")
        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            gold_label = str(meta["gold_label"])
            bucket = str(meta["a_priori_bucket"])
            default = stage.replay_row(row)
            omit = stage.replay_row(row, omit_stages=OMIT)
            if (
                default is None
                or omit is None
                or not default["replayable"]
                or not omit["replayable"]
            ):
                fidelity["unreplayable"] += 1
                continue
            fidelity["replayable"] += 1

            default_ok = _purist_ok(default["final"], gold_label)
            omit_ok = _purist_ok(omit["final"], gold_label)
            default_clinical_ok = _purist_ok(
                default["band_labels"]["clinical_selection"], gold_label
            )
            omit_clinical_ok = _purist_ok(
                omit["band_labels"]["clinical_selection"], gold_label
            )
            fired = _stage_fired(default, OMIT_STAGE)

            full["n"] += 1
            full["default_correct"] += int(default_ok)
            full["omit_correct"] += int(omit_ok)
            bucket_stats = full["by_bucket"][bucket]
            bucket_stats["n"] += 1
            bucket_stats["default_correct"] += int(default_ok)
            bucket_stats["omit_correct"] += int(omit_ok)

            if fired:
                breakthrough_fire_cells += 1
            if default_ok != omit_ok:
                full_disagree_by_bucket[bucket] += 1
                if omit_ok and not default_ok:
                    full_rescue += 1
                    full_rescue_by_bucket[bucket] += 1
                elif default_ok and not omit_ok:
                    full_harm += 1
                    full_harm_by_bucket[bucket] += 1

            if bucket != TARGET_BUCKET:
                continue

            if fired:
                breakthrough_fire_unknown += 1

            for arm_key, replay, ok, clinical_ok in (
                ("default", default, default_ok, default_clinical_ok),
                ("omit", omit, omit_ok, omit_clinical_ok),
            ):
                arm = unknown[arm_key]
                arm["n"] += 1
                arm["correct"] += int(ok)
                arm["clinical_correct"] += int(clinical_ok)
                if not ok:
                    arm["modes_final"][
                        _mode(replay["final"], gold_label, purist_ok=False)
                    ] += 1
                if not clinical_ok:
                    arm["modes_clinical"][
                        _mode(
                            replay["band_labels"]["clinical_selection"],
                            gold_label,
                            purist_ok=False,
                        )
                    ] += 1

            default_later = _later_stages(default)
            omit_later = _later_stages(omit)
            if set(omit_later) != set(default_later) or (
                omit["final"] != default["final"] and not fired
            ):
                spillover_unknown.append(
                    {
                        "model_slug": slug,
                        "model_display": display,
                        "source_row_index": index,
                        "gold_label": gold_label,
                        "default_final": default["final"],
                        "omit_final": omit["final"],
                        "breakthrough_fired_default": fired,
                        "default_later_stages": default_later,
                        "omit_later_stages": omit_later,
                        "selected_evidence": default.get("selected_evidence"),
                    }
                )

            if default["final"] == omit["final"] and default_ok == omit_ok:
                continue

            cell = {
                "model_slug": slug,
                "model_display": display,
                "source_row_index": index,
                "gold_label": gold_label,
                "breakthrough_fired_default": fired,
                "default_before_breakthrough": next(
                    (
                        change["before"]
                        for change in default["changes"]
                        if change["stage"] == OMIT_STAGE
                    ),
                    None,
                ),
                "default_after_breakthrough": next(
                    (
                        change["after"]
                        for change in default["changes"]
                        if change["stage"] == OMIT_STAGE
                    ),
                    None,
                ),
                "default_final": default["final"],
                "omit_final": omit["final"],
                "default_correct": default_ok,
                "omit_correct": omit_ok,
                "default_clinical_correct": default_clinical_ok,
                "omit_clinical_correct": omit_clinical_ok,
                "default_pathway": stage._pathway_key(default["changes"]),
                "omit_pathway": stage._pathway_key(omit["changes"]),
                "default_mode": _mode(
                    default["final"], gold_label, purist_ok=default_ok
                ),
                "omit_mode": _mode(omit["final"], gold_label, purist_ok=omit_ok),
                "selected_evidence": default.get("selected_evidence"),
            }
            unknown_disagree.append(cell)
            if omit_ok and not default_ok:
                unknown_rescue.append(cell)
            elif default_ok and not omit_ok:
                unknown_harm.append(cell)

    spillover_filtered = spillover_unknown

    unknown_n = unknown["default"]["n"]
    full_n = full["n"]
    by_bucket_out = {}
    for bucket, stats in sorted(full["by_bucket"].items()):
        n = stats["n"]
        by_bucket_out[bucket] = {
            "n_cells": n,
            "default_accuracy": round(stats["default_correct"] / n, 4) if n else None,
            "omit_accuracy": round(stats["omit_correct"] / n, 4) if n else None,
            "default_correct": stats["default_correct"],
            "omit_correct": stats["omit_correct"],
            "delta_correct": stats["omit_correct"] - stats["default_correct"],
            "disagree": full_disagree_by_bucket.get(bucket, 0),
            "rescue_by_omit": full_rescue_by_bucket.get(bucket, 0),
            "harm_by_omit": full_harm_by_bucket.get(bucket, 0),
        }

    mode_delta_final: Counter[str] = Counter()
    for mode, count in unknown["omit"]["modes_final"].items():
        mode_delta_final[mode] += count
    for mode, count in unknown["default"]["modes_final"].items():
        mode_delta_final[mode] -= count

    decision = _decide(
        unknown_rescue=len(unknown_rescue),
        unknown_harm=len(unknown_harm),
        unknown_default_correct=unknown["default"]["correct"],
        unknown_omit_correct=unknown["omit"]["correct"],
        full_rescue=full_rescue,
        full_harm=full_harm,
        full_default_correct=full["default_correct"],
        full_omit_correct=full["omit_correct"],
    )

    return {
        "study_id": "gan2026_unknown_breakthrough_loo",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/gan2026/unknown_breakthrough_loo_protocol_2026-08-06.md"
        ),
        "parent_report": (
            "docs/research/gan2026/unknown_sentinel_clinical_harm_2026-08-06.md"
        ),
        "git": _git_note(),
        "scope": {
            "split": "dev750",
            "surface": "llm_with_rules",
            "primary_bucket": TARGET_BUCKET,
            "omitted_stage": OMIT_STAGE,
            "arms": ["default_full_stack", "omit_breakthrough"],
            "calls": "none",
            "production_defaults_changed": False,
        },
        "fidelity": fidelity,
        "unknown_gold": {
            "default": _arm_summary(
                n=unknown_n,
                correct=unknown["default"]["correct"],
                clinical_correct=unknown["default"]["clinical_correct"],
                modes_final=unknown["default"]["modes_final"],
                modes_clinical=unknown["default"]["modes_clinical"],
            ),
            "omit_breakthrough": _arm_summary(
                n=unknown["omit"]["n"],
                correct=unknown["omit"]["correct"],
                clinical_correct=unknown["omit"]["clinical_correct"],
                modes_final=unknown["omit"]["modes_final"],
                modes_clinical=unknown["omit"]["modes_clinical"],
            ),
            "breakthrough_fires_default": breakthrough_fire_unknown,
            "disagree_cells": len(unknown_disagree),
            "rescue_by_omit": len(unknown_rescue),
            "harm_by_omit": len(unknown_harm),
            "final_wrong_mode_delta_omit_minus_default": dict(
                mode_delta_final.most_common()
            ),
            "examples_rescue": _pick_examples(unknown_rescue),
            "examples_harm": _pick_examples(unknown_harm),
            "examples_disagree": _pick_examples(unknown_disagree),
            "later_family_spillover_cells": len(spillover_filtered),
            "examples_spillover": _pick_examples(spillover_filtered),
        },
        "full_ledger_secondary": {
            "n_cells": full_n,
            "breakthrough_fires_default": breakthrough_fire_cells,
            "default_accuracy": (
                round(full["default_correct"] / full_n, 4) if full_n else None
            ),
            "omit_accuracy": (
                round(full["omit_correct"] / full_n, 4) if full_n else None
            ),
            "default_correct": full["default_correct"],
            "omit_correct": full["omit_correct"],
            "delta_correct": full["omit_correct"] - full["default_correct"],
            "rescue_by_omit": full_rescue,
            "harm_by_omit": full_harm,
            "by_bucket": by_bucket_out,
        },
        "decision": decision,
        "claim_boundary": (
            "Development leave-one-family-out on retained Gan hybrid ledgers. "
            "Not holdout. Not a production repair rewrite. Unknown-gold recovery "
            "with material full-ledger loss supports only a guarded-bucket "
            "hypothesis."
        ),
    }


def _decide(
    *,
    unknown_rescue: int,
    unknown_harm: int,
    unknown_default_correct: int,
    unknown_omit_correct: int,
    full_rescue: int,
    full_harm: int,
    full_default_correct: int,
    full_omit_correct: int,
) -> dict[str, Any]:
    unknown_delta = unknown_omit_correct - unknown_default_correct
    full_delta = full_omit_correct - full_default_correct
    if unknown_rescue > 0 and unknown_harm == 0 and full_delta >= 0:
        label = "necessity_confirmed_low_global_cost"
        summary = (
            "Omitting breakthrough recovers unknown-gold damage with no new "
            "unknown harms and no net full-ledger Purist loss."
        )
    elif unknown_rescue > 0 and unknown_harm == 0 and full_delta < 0:
        label = "necessity_confirmed_with_global_cost"
        summary = (
            "Omitting breakthrough recovers unknown-gold damage with no new "
            "unknown harms, but costs Purist correct cells on the full ledger."
        )
    elif unknown_delta <= 0 and full_delta < 0:
        label = "not_necessary_mixed_or_negative"
        summary = (
            "Omitting breakthrough does not improve unknown gold and harms the "
            "full ledger; first-changer harm is not a net necessity for off."
        )
    else:
        label = "mixed"
        summary = (
            "Omitting breakthrough has mixed unknown and/or full-ledger effects; "
            "not an unconditional family-off authorization."
        )
    return {
        "label": label,
        "summary": summary,
        "unknown_delta_correct": unknown_delta,
        "full_delta_correct": full_delta,
        "unknown_rescue": unknown_rescue,
        "unknown_harm": unknown_harm,
        "full_rescue": full_rescue,
        "full_harm": full_harm,
        "production_rewrite_authorized": False,
    }


def write_report(artifact: dict[str, Any]) -> str:
    unk = artifact["unknown_gold"]
    full = artifact["full_ledger_secondary"]
    decision = artifact["decision"]
    default = unk["default"]
    omit = unk["omit_breakthrough"]

    lines = [
        "# Gan unknown-gold breakthrough leave-one-family-out",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development leave-one-family-out necessity check  ",
        "Protocol: [unknown breakthrough LOO protocol]"
        "(unknown_breakthrough_loo_protocol_2026-08-06.md)  ",
        "Parent: [unknown_sentinel clinical harm]"
        "(unknown_sentinel_clinical_harm_2026-08-06.md)  ",
        "Artifact: "
        f"[`experiments/gan2026_unknown_breakthrough_loo_{DATE_STAMP}.json`]"
        f"(../../experiments/gan2026_unknown_breakthrough_loo_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        (
            f"On {default['n_cells']} unknown-gold cells, omitting "
            f"`{OMIT_STAGE}` changes final Purist from "
            f"**{default['final_accuracy']}** to **{omit['final_accuracy']}** "
            f"({decision['unknown_rescue']} rescue / {decision['unknown_harm']} "
            "harm vs default)."
        ),
        "",
        (
            f"Full-ledger secondary ({full['n_cells']} cells): "
            f"{full['default_accuracy']} → {full['omit_accuracy']} "
            f"(Δ correct {full['delta_correct']:+d}; "
            f"{full['rescue_by_omit']} rescue / {full['harm_by_omit']} harm)."
        ),
        "",
        f"**Decision label:** `{decision['label']}`.",
        "",
        decision["summary"],
        "",
        "Production rewrite: **not authorized**.",
        "",
        "## Unknown-gold arms",
        "",
        "| Arm | Final acc | Clinical-selection acc | Wrong modes (final) |",
        "| --- | ---: | ---: | --- |",
    ]
    for name, arm in (("default", default), ("omit breakthrough", omit)):
        modes = ", ".join(
            f"{mode} {count}"
            for mode, count in list(arm["final_wrong_modes"].items())[:4]
        )
        lines.append(
            f"| {name} | {arm['final_accuracy']} | "
            f"{arm['clinical_selection_accuracy']} | {modes or '—'} |"
        )

    lines.extend(
        [
            "",
            (
                f"Default breakthrough fires on unknown gold: "
                f"{unk['breakthrough_fires_default']}."
            ),
            (
                f"Disagree cells: {unk['disagree_cells']}; "
                f"later-family spillover cells: "
                f"{unk['later_family_spillover_cells']}."
            ),
            "",
            "### Final wrong-mode Δ (omit − default)",
            "",
        ]
    )
    mode_delta = unk["final_wrong_mode_delta_omit_minus_default"]
    if mode_delta:
        lines.append("| Mode | Δ count |")
        lines.append("| --- | ---: |")
        for mode, delta in mode_delta.items():
            lines.append(f"| `{mode}` | {delta:+d} |")
    else:
        lines.append("No wrong-mode count changes.")

    lines.extend(["", "### Recovered unknown cells (omit corrects default wrong)", ""])
    if unk["examples_rescue"]:
        for ex in unk["examples_rescue"]:
            lines.append(
                f"- row {ex['source_row_index']} / {ex['model_display']}: "
                f"`{ex['default_final']}` → `{ex['omit_final']}` "
                f"(gold `{ex['gold_label']}`; pathway `{ex['default_pathway']}`)"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### New unknown harms (omit wrongs default correct)", ""])
    if unk["examples_harm"]:
        for ex in unk["examples_harm"]:
            lines.append(
                f"- row {ex['source_row_index']} / {ex['model_display']}: "
                f"`{ex['default_final']}` → `{ex['omit_final']}` "
                f"(gold `{ex['gold_label']}`)"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Later-family spillover examples", ""])
    if unk["examples_spillover"]:
        for ex in unk["examples_spillover"]:
            lines.append(
                f"- row {ex['source_row_index']} / {ex['model_display']}: "
                f"default later `{ex['default_later_stages']}` vs omit later "
                f"`{ex['omit_later_stages']}` "
                f"(breakthrough fired default={ex['breakthrough_fired_default']})"
            )
    else:
        lines.append("- none material")

    lines.extend(
        [
            "",
            "## Full-ledger secondary (all gold buckets)",
            "",
            "| Bucket | N | Default acc | Omit acc | Δ correct | Rescue | Harm |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for bucket, stats in full["by_bucket"].items():
        lines.append(
            f"| `{bucket}` | {stats['n_cells']} | {stats['default_accuracy']} | "
            f"{stats['omit_accuracy']} | {stats['delta_correct']:+d} | "
            f"{stats['rescue_by_omit']} | {stats['harm_by_omit']} |"
        )
    lines.append(
        f"| **all** | {full['n_cells']} | {full['default_accuracy']} | "
        f"{full['omit_accuracy']} | {full['delta_correct']:+d} | "
        f"{full['rescue_by_omit']} | {full['harm_by_omit']} |"
    )

    git = artifact["git"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            decision["summary"],
            "",
            (
                "This confirms whether the unknown-harm first-changer is "
                "factorial on the omitted family. It does **not** change the "
                "default hybrid repair stack."
            ),
            "",
            "## Next",
            "",
            "1. If label is `necessity_confirmed_with_global_cost`: only a "
            "guarded unknown-gold stand-down is in scope for a later "
            "predeclared repair study.",
            "2. If label is `necessity_confirmed_low_global_cost`: still require "
            "a separate repair-candidate protocol before production change.",
            "3. Operational primary remains the vLLM dev10 task.",
            "",
            "## Method",
            "",
            "- Split: Gan `dev750`; arms = full stack vs study-local "
            f"omit `{OMIT_STAGE}`.",
            "- Replay: `scripts/build_gan2026_hybrid_stage_ablation.py` "
            "`replay_row(..., omit_stages=...)`.",
            f"- Git: `{git.get('commit')}` "
            f"({'dirty tree' if git.get('dirty_tree') else 'clean'}).",
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
        / f"experiments/gan2026_unknown_breakthrough_loo_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/gan2026/unknown_breakthrough_loo_{REPORT_DATE}.md",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n")
    report = write_report(artifact)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report)
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    print(
        "unknown "
        f"{artifact['unknown_gold']['default']['final_accuracy']} -> "
        f"{artifact['unknown_gold']['omit_breakthrough']['final_accuracy']} "
        f"({artifact['decision']['label']}); full Δ "
        f"{artifact['full_ledger_secondary']['delta_correct']:+d}"
    )


if __name__ == "__main__":
    main()
