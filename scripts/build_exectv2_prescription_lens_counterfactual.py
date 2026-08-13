#!/usr/bin/env python3
"""ExECTv2 Prescription lens default-on vs thin identity counterfactual.

No new model calls. Study-local arms only; production defaults unchanged.
See docs/research/exectv2/exectv2_prescription_lens_counterfactual_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses import (
    LensPolicy,
    lens_from_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.base import (
    PrescriptionLens,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    manifest_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.producers import (
    SavedJsonlProducer,
    findings_from_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection,
    sf_unknown_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as kes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    TARGET_ENTITIES,
    _direct_sf_row,
    _manifest_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_KEY = 2
Arm = Literal["default_on", "lens_off"]

_STAGE_PATH = REPO_ROOT / "scripts/build_exectv2_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("exect_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)
hs = stage.hs
cat = stage.cat
CONFIG = stage.CONFIG
FAMILIES = stage.FAMILIES


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


def _structured_path(main_jsonl: Path) -> Path:
    return main_jsonl.with_name(main_jsonl.name.replace(".jsonl", "_structured.jsonl"))


def _pick_examples(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = stage.MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(stage.MODEL_PREFERENCE)
        return model_rank, 0, str(row["letter_id"])

    picked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in sorted(candidates, key=sort_key):
        letter_id = str(row["letter_id"])
        if letter_id in seen:
            continue
        picked.append(row)
        seen.add(letter_id)
        if len(picked) >= EXAMPLES_PER_KEY:
            break
    return picked


def replay_letter_arm(
    structured_row: dict[str, Any],
    letter: ExectLetter,
    *,
    gold_mentions: list[dict[str, Any]],
    prescription_arm: Arm,
) -> dict[str, Any]:
    """Ordered hybrid replay with study-local Prescription lens arm."""

    events = structured_row.get("structured_events") or []
    if not events:
        return {"replayable": False, "reason": "empty_structured_events"}

    record = kes.records.StructuredExtractionRecord.model_validate(
        {"clinical_events": events}
    )
    flattened = kes.parsing.flatten_events(record)
    projected, _gate_warnings = kes.projection.to_predicted_letter(
        letter.letter_id,
        flattened,
        note_text=letter.note_text,
        prompt_version=str(structured_row.get("prompt_version") or ""),
    )
    gate_rows = [stage._mention_to_row(mention) for mention in projected.mentions]

    structured_for_sf = dict(structured_row)
    structured_for_sf["predicted_mentions"] = gate_rows
    sf_direct = _direct_sf_row(structured_for_sf)
    sf_projected = sf_state_projection.project_row(
        sf_direct, ablation=CONFIG.sf_projection_ablation
    )
    sf_suppressed = sf_unknown_suppression.suppress_row(sf_projected)

    manifest = manifest_from_mapping(
        _manifest_payload(
            Path("structured.jsonl"),
            Path("sf.jsonl"),
            row_count=1,
            config=CONFIG,
        )
    )
    producers = {
        producer_id: SavedJsonlProducer.from_manifest(producer_manifest)
        for producer_id, producer_manifest in manifest.producers.items()
    }
    source_rows = {
        "structured_key_family_event_ledger": {letter.letter_id: structured_for_sf},
        "sf_model_projection_suppression": {letter.letter_id: sf_suppressed},
    }

    store = ClinicalFindingStore(letter.letter_id, letter.note_text)
    family_mentions: dict[str, list[dict[str, Any]]] = {}
    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
        producer = producers[lens_config.producer]
        row = source_rows[lens_config.producer][letter.letter_id]
        source = producer.source_for_row(
            row, source_lane=lens_config.source_lane or producer.source_lane
        )
        store.register_source(source)
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=True,
            )
        )
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=False,
            )
        )
        family_mentions[entity] = [
            finding.to_row()
            for finding in store.findings(
                entity=entity,
                producer_id=lens_config.producer,
                raw_surface=False,
            )
        ]

    current = {entity: list(rows) for entity, rows in family_mentions.items()}
    pre_rx_mentions = stage._all_family_mentions(current)
    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
        producer = producers[lens_config.producer]
        source_lane = lens_config.source_lane or producer.source_lane or lens_config.producer
        if entity == "Prescription" and prescription_arm == "lens_off":
            lens = PrescriptionLens(
                lens_id="prescription_identity_counterfactual",
                entity="Prescription",
            )
        else:
            lens = lens_from_manifest(lens_config)
        result = lens.reconcile(
            store,
            policy=LensPolicy(
                producer_id=lens_config.producer,
                source_lane=source_lane,
                ownership_label=lens_config.ownership_label or producer.ownership_label,
                portability=lens_config.portability,
                diagnosis_policy_variant=CONFIG.diagnosis_policy_variant,
                prescription_policy_variant=CONFIG.prescription_policy_variant,
            ),
        )
        current[entity] = [finding.to_row() for finding in result.findings]

    final_mentions = stage._all_family_mentions(current)
    invalid = [
        mention
        for mention in final_mentions
        if not str(mention.get("evidence", ""))
        or str(mention.get("evidence", "")) not in letter.note_text
    ]
    evidence_ok = not invalid
    scored_mentions = final_mentions if evidence_ok else []

    pre_rx_keys = stage._keys(pre_rx_mentions, gold_mentions, "Prescription")
    final_keys = stage._keys(scored_mentions, gold_mentions, "Prescription")
    gold_keys = headline_keys(
        {"gold_mentions": gold_mentions, "predicted_mentions": []},
        "Prescription",
        field="gold_mentions",
    )
    return {
        "replayable": True,
        "evidence_ok": evidence_ok,
        "n_invalid_evidence": len(invalid),
        "pre_rx_keys": pre_rx_keys,
        "final_keys": final_keys,
        "final_mode": stage._mode(gold_keys, final_keys),
        "pre_rx_mode": stage._mode(gold_keys, pre_rx_keys),
        "final_mentions": scored_mentions,
        "gold_keys": gold_keys,
    }


def _score_pool(
    gold_by_id: dict[str, list[dict[str, Any]]],
    pred_by_id: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    gold_letters: list[ExectLetter] = []
    pred_letters: list[ExectLetter] = []
    for letter_id, gold in gold_by_id.items():
        gold_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(annotation_from_mapping(m) for m in gold),
            )
        )
        pred_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(
                    annotation_from_mapping(m) for m in pred_by_id.get(letter_id, [])
                ),
            )
        )
    family = clinical_headline_scores(gold_letters, pred_letters)
    overall = aggregate_scores(family.values())
    return {
        "clinical_fact_f1": round(float(overall["f1"]), 4),
        "by_family": {
            name: round(float(score["f1"]), 4) for name, score in family.items()
        },
        "prescription": {
            "f1": round(float(family["Prescription"]["f1"]), 4),
            "precision": round(float(family["Prescription"]["precision"]), 4),
            "recall": round(float(family["Prescription"]["recall"]), 4),
            "tp": family["Prescription"]["tp"],
            "fp": family["Prescription"]["fp"],
            "fn": family["Prescription"]["fn"],
        },
    }


def build_artifact() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}

    arm_exact: dict[Arm, int] = {"default_on": 0, "lens_off": 0}
    arm_n = 0
    arm_modes: dict[Arm, list[str]] = {"default_on": [], "lens_off": []}
    evidence_pass: dict[Arm, int] = {"default_on": 0, "lens_off": 0}
    transition = Counter()
    examples_rescue: list[dict[str, Any]] = []
    examples_harm: list[dict[str, Any]] = []
    fidelity = {
        "letter_model_cells": 0,
        "replayable_pairs": 0,
        "unreplayable": 0,
        "default_matches_retained_rx_keys": 0,
    }

    # For F1: pool mentions across models separately then average? Better:
    # compute per-model F1 then mean, matching six-model style.
    per_model_rows: dict[str, dict[Arm, dict[str, list[dict[str, Any]]]]] = {}
    per_model_gold: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for slug, display in hs.MODEL_SPECS:
        main_path = hs.EXECT_JSONL[slug]
        structured_path = _structured_path(main_path)
        main_rows = {str(row["letter_id"]): row for row in hs._read_jsonl(main_path)}
        structured_rows = hs._read_jsonl(structured_path)
        per_model_rows[slug] = {
            "default_on": {},
            "lens_off": {},
        }
        per_model_gold[slug] = {}

        for structured_row in structured_rows:
            letter_id = str(structured_row["letter_id"])
            letter = letters[letter_id]
            main_row = main_rows[letter_id]
            gold = list(main_row.get("gold_mentions") or [])
            fidelity["letter_model_cells"] += 1
            per_model_gold[slug][letter_id] = gold

            arms: dict[Arm, dict[str, Any]] = {}
            ok_pair = True
            for arm in ("default_on", "lens_off"):
                replay = replay_letter_arm(
                    structured_row,
                    letter,
                    gold_mentions=gold,
                    prescription_arm=arm,  # type: ignore[arg-type]
                )
                if not replay.get("replayable"):
                    ok_pair = False
                    break
                arms[arm] = replay  # type: ignore[index]
            if not ok_pair:
                fidelity["unreplayable"] += 1
                continue
            fidelity["replayable_pairs"] += 1
            arm_n += 1

            retained_rx = headline_keys(main_row, "Prescription", field="predicted_mentions")
            if stage._key_sig(retained_rx) == stage._key_sig(
                arms["default_on"]["final_keys"]
            ):
                fidelity["default_matches_retained_rx_keys"] += 1

            for arm in ("default_on", "lens_off"):
                replay = arms[arm]  # type: ignore[index]
                exact = stage._exact(replay["final_mode"])
                if exact:
                    arm_exact[arm] += 1  # type: ignore[index]
                arm_modes[arm].append(replay["final_mode"])  # type: ignore[index]
                if replay["evidence_ok"]:
                    evidence_pass[arm] += 1  # type: ignore[index]
                per_model_rows[slug][arm][letter_id] = replay["final_mentions"]

            default_exact = stage._exact(arms["default_on"]["final_mode"])
            off_exact = stage._exact(arms["lens_off"]["final_mode"])
            if off_exact and not default_exact:
                effect = "lens_off_rescue"
            elif default_exact and not off_exact:
                effect = "lens_off_harm"
            elif arms["default_on"]["final_mode"] != arms["lens_off"]["final_mode"]:
                effect = "mode_reshape_same_exactness"
            else:
                effect = "unchanged"
            transition[effect] += 1

            example = {
                "letter_id": letter_id,
                "model_slug": slug,
                "model_display": display,
                "effect": effect,
                "default_mode": arms["default_on"]["final_mode"],
                "lens_off_mode": arms["lens_off"]["final_mode"],
                "default_keys": stage._compact_keys(arms["default_on"]["final_keys"]),
                "lens_off_keys": stage._compact_keys(arms["lens_off"]["final_keys"]),
                "gold_keys": stage._compact_keys(arms["default_on"]["gold_keys"]),
                "default_evidence_ok": arms["default_on"]["evidence_ok"],
                "lens_off_evidence_ok": arms["lens_off"]["evidence_ok"],
            }
            if effect == "lens_off_rescue":
                examples_rescue.append(example)
            elif effect == "lens_off_harm":
                examples_harm.append(example)

    # Aggregate F1: mean across models of pooled-letter F1
    f1_by_arm: dict[str, dict[str, Any]] = {}
    for arm in ("default_on", "lens_off"):
        model_rx_f1: list[float] = []
        model_overall_f1: list[float] = []
        for slug in per_model_rows:
            scored = _score_pool(per_model_gold[slug], per_model_rows[slug][arm])
            model_rx_f1.append(scored["prescription"]["f1"])
            model_overall_f1.append(scored["clinical_fact_f1"])
        f1_by_arm[arm] = {
            "prescription_f1_mean": round(sum(model_rx_f1) / len(model_rx_f1), 4),
            "prescription_f1_by_model": {
                slug: round(model_rx_f1[i], 4)
                for i, slug in enumerate(per_model_rows)
            },
            "four_family_f1_mean": round(
                sum(model_overall_f1) / len(model_overall_f1), 4
            ),
        }

    def _mode_counts(modes: list[str]) -> dict[str, int]:
        return dict(sorted(Counter(modes).items(), key=lambda item: (-item[1], item[0])))

    artifact = {
        "schema_version": "exectv2.prescription_lens_counterfactual.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/exectv2/exectv2_prescription_lens_counterfactual_protocol_2026-08-06.md"
        ),
        "parent_synthesis": (
            "docs/research/shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md"
        ),
        "git": _git_note(),
        "dataset": "ExECTv2",
        "split": "dev140",
        "surface": "llm_with_rules",
        "arms": {
            "default_on": {
                "prescription_lens": "prescription_dictionary_v09",
                "note": "Selected StructuredMethodConfig default dictionary lens",
            },
            "lens_off": {
                "prescription_lens": "prescription_identity_counterfactual",
                "note": "Thin PrescriptionLens identity; study-local only",
            },
        },
        "policy_fixed": {
            "diagnosis_policy_variant": CONFIG.diagnosis_policy_variant,
            "prescription_policy_variant": CONFIG.prescription_policy_variant,
            "sf_projection_ablation": CONFIG.sf_projection_ablation,
        },
        "n_letter_model_cells": arm_n,
        "fidelity": {
            **fidelity,
            "default_matches_retained_rx_keys_rate": round(
                fidelity["default_matches_retained_rx_keys"]
                / fidelity["replayable_pairs"],
                4,
            )
            if fidelity["replayable_pairs"]
            else 0.0,
        },
        "prescription_letter_exact": {
            arm: {
                "n": arm_n,
                "n_exact": arm_exact[arm],
                "exact_rate": round(arm_exact[arm] / arm_n, 4) if arm_n else 0.0,
                "mode_counts": _mode_counts(arm_modes[arm]),
                "evidence_gate_pass": evidence_pass[arm],
                "evidence_gate_pass_rate": round(evidence_pass[arm] / arm_n, 4)
                if arm_n
                else 0.0,
            }
            for arm in ("default_on", "lens_off")
        },
        "f1": f1_by_arm,
        "transitions_lens_off_vs_default": dict(transition),
        "examples_lens_off_rescue": _pick_examples(examples_rescue),
        "examples_lens_off_harm": _pick_examples(examples_harm),
        "decision": None,  # filled below
        "claim_boundary": (
            "Development Prescription lens on/off counterfactual on ExECT "
            "dev140. Study-local thin-lens arm only. Not a Decision 0046 or "
            "default-policy rewrite. Not holdout competence."
        ),
    }

    default_exact = artifact["prescription_letter_exact"]["default_on"]["exact_rate"]
    off_exact = artifact["prescription_letter_exact"]["lens_off"]["exact_rate"]
    default_f1 = artifact["f1"]["default_on"]["prescription_f1_mean"]
    off_f1 = artifact["f1"]["lens_off"]["prescription_f1_mean"]
    rescues = transition.get("lens_off_rescue", 0)
    harms = transition.get("lens_off_harm", 0)
    if off_exact > default_exact and off_f1 >= default_f1 and rescues > harms:
        decision = (
            "lens_off_helps_on_development: thin identity improves Prescription "
            "letter exactness and does not reduce mean Prescription F1; still "
            "not a default rewrite without holdout protocol."
        )
    elif off_exact > default_exact and off_f1 < default_f1:
        decision = (
            "mixed_metric_split: lens-off raises Prescription letter exactness "
            f"and net cell rescue ({rescues} rescue / {harms} harm) but mean "
            "Prescription F1 does not improve; no default rewrite."
        )
    elif off_exact < default_exact and off_f1 <= default_f1:
        decision = (
            "lens_off_does_not_help: thin identity is worse or no better on "
            "both letter exactness and mean Prescription F1."
        )
    else:
        decision = (
            "mixed: lens-off and default-on trade exactness/F1 or rescue/harm; "
            "no default rewrite."
        )
    artifact["decision"] = decision
    artifact["delta"] = {
        "exact_rate_lens_off_minus_default": round(off_exact - default_exact, 4),
        "prescription_f1_mean_lens_off_minus_default": round(off_f1 - default_f1, 4),
        "four_family_f1_mean_lens_off_minus_default": round(
            artifact["f1"]["lens_off"]["four_family_f1_mean"]
            - artifact["f1"]["default_on"]["four_family_f1_mean"],
            4,
        ),
        "lens_off_rescue_cells": rescues,
        "lens_off_harm_cells": harms,
    }
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    d = artifact["prescription_letter_exact"]["default_on"]
    o = artifact["prescription_letter_exact"]["lens_off"]
    delta = artifact["delta"]
    lines = [
        "# ExECTv2 Prescription lens on/off counterfactual",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development no-call counterfactual  ",
        "Protocol: [Prescription lens counterfactual protocol]"
        "(exectv2_prescription_lens_counterfactual_protocol_2026-08-06.md)  ",
        "Parent: [cross-task hybrid mechanism synthesis]"
        "(cross_task_hybrid_mechanism_synthesis_2026-08-06.md)  ",
        "Companion: [ExECT hybrid stage ablation]"
        "(exectv2_hybrid_stage_ablation_2026-08-06.md)  ",
        f"Artifact: [`experiments/exectv2_prescription_lens_counterfactual_{DATE_STAMP}.json`]"
        f"(../../experiments/exectv2_prescription_lens_counterfactual_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        artifact["decision"],
        "",
        f"On {artifact['n_letter_model_cells']} letter×model cells: Prescription "
        f"letter exactness **{d['exact_rate']:.3f}** (default-on) vs "
        f"**{o['exact_rate']:.3f}** (lens-off); Δ "
        f"{delta['exact_rate_lens_off_minus_default']:+.3f}. Mean Prescription "
        f"F1 **{artifact['f1']['default_on']['prescription_f1_mean']:.3f}** vs "
        f"**{artifact['f1']['lens_off']['prescription_f1_mean']:.3f}**; Δ "
        f"{delta['prescription_f1_mean_lens_off_minus_default']:+.3f}. "
        f"Changed cells: lens-off rescue {delta['lens_off_rescue_cells']}, "
        f"harm {delta['lens_off_harm_cells']}.",
        "",
        "## Arms",
        "",
        "| Arm | Prescription lens |",
        "| --- | --- |",
        "| `default_on` | selected `prescription_dictionary_v09` |",
        "| `lens_off` | thin `PrescriptionLens` identity (study-local) |",
        "",
        "Dx / SF / Investigations lenses, SF projection, and evidence gate stay "
        "on the selected path. Production defaults are not changed.",
        "",
        "## Prescription letter exactness",
        "",
        "| Arm | Exact rate | Evidence-gate pass | Top modes |",
        "| --- | ---: | ---: | --- |",
    ]
    for arm, payload in (
        ("default_on", d),
        ("lens_off", o),
    ):
        modes = ", ".join(
            f"`{k}` {v}" for k, v in list(payload["mode_counts"].items())[:4]
        )
        lines.append(
            f"| `{arm}` | {payload['exact_rate']:.3f} | "
            f"{payload['evidence_gate_pass_rate']:.3f} | {modes} |"
        )

    lines.extend(
        [
            "",
            "## Clinical-headline F1 (mean across six models)",
            "",
            "| Arm | Prescription F1 | Four-family F1 |",
            "| --- | ---: | ---: |",
            f"| `default_on` | "
            f"{artifact['f1']['default_on']['prescription_f1_mean']:.3f} | "
            f"{artifact['f1']['default_on']['four_family_f1_mean']:.3f} |",
            f"| `lens_off` | "
            f"{artifact['f1']['lens_off']['prescription_f1_mean']:.3f} | "
            f"{artifact['f1']['lens_off']['four_family_f1_mean']:.3f} |",
            "",
            "## Transitions (lens-off vs default-on)",
            "",
            "| Transition | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in artifact["transitions_lens_off_vs_default"].items():
        lines.append(f"| `{key}` | {count} |")

    lines.extend(["", "### Rescue examples (lens-off fixes default wrong)", ""])
    if artifact["examples_lens_off_rescue"]:
        for ex in artifact["examples_lens_off_rescue"]:
            lines.append(
                f"- **{ex['letter_id']} / {ex['model_display']}.** "
                f"`{ex['default_mode']}` → `{ex['lens_off_mode']}`. "
                f"Default keys {ex['default_keys']}; lens-off {ex['lens_off_keys']}."
            )
    else:
        lines.append("- None retained under the example picker.")

    lines.extend(["", "### Harm examples (lens-off breaks default correct)", ""])
    if artifact["examples_lens_off_harm"]:
        for ex in artifact["examples_lens_off_harm"]:
            lines.append(
                f"- **{ex['letter_id']} / {ex['model_display']}.** "
                f"`{ex['default_mode']}` → `{ex['lens_off_mode']}`. "
                f"Default keys {ex['default_keys']}; lens-off {ex['lens_off_keys']}."
            )
    else:
        lines.append("- None retained under the example picker.")

    fid = artifact["fidelity"]
    lines.extend(
        [
            "",
            "## Fidelity",
            "",
            f"- Replayable pairs: {fid['replayable_pairs']} / "
            f"{fid['letter_model_cells']}",
            f"- Default-on Rx keys match retained predicted_mentions: "
            f"{fid['default_matches_retained_rx_keys_rate']:.3f}",
            "",
            "## Decision boundary",
            "",
            artifact["decision"],
            "",
            "This does **not** change Decision 0045/0046 defaults. A default "
            "rewrite would need a separate predeclared protocol (including "
            "holdout aggregates if promotion is intended).",
            "",
            "## Next",
            "",
            "1. Operational primary remains the vLLM dev10 task.",
            "2. If policy work continues: only then predeclare a default-change "
            "candidate with holdout gates.",
            "3. Do not merge this thin-lens arm into production manifests from "
            "this page.",
            "",
            "## Method",
            "",
            "- Split: ExECT `dev140`; six retained structured sidecars.",
            "- Dual ordered replay through evidence gate.",
            "- Primary: Prescription unit-key letter exactness.",
            "- Secondary: mean Prescription / four-family clinical-headline F1.",
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
        / f"experiments/exectv2_prescription_lens_counterfactual_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/exectv2/exectv2_prescription_lens_counterfactual_{REPORT_DATE}.md",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    print("decision:", artifact["decision"])
    print("delta:", artifact["delta"])


if __name__ == "__main__":
    main()
