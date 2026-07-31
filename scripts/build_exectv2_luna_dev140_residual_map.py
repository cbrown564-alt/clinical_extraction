"""Build a no-call Luna ExECTv2 single-call residual map on dev140.

Replays saved Luna producers under default and joint Diagnosis/Prescription
policies. Emits a letter×family panel, summary counts, and stratified
exemplars for prompt-variant drafting. Zero model calls; no test60 access.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_led_dev_regressions,
    model_swap,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)

if __package__:
    from scripts import analyze_exectv2_model_led_dev140_regressions as baseline
else:
    import analyze_exectv2_model_led_dev140_regressions as baseline

CONFIG_PATH = Path("configs/exectv2/six_model_comparison/gpt56luna_dev140.json")
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_luna_single_call_dev140_residual_map_protocol_2026-07-31.md"
)
OUTPUT_DIR = Path("experiments/exectv2_luna_single_call_dev140_residual_map_20260731")
GENERATED_ON = "2026-07-31"
SF_MODEL_OWNED_ARTIFACT = Path(
    "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715"
    "_sf_structured_direct.jsonl"
)
SOURCE_PRODUCERS = {
    DIAGNOSIS.name: "structured_key_family_event_ledger",
    SEIZURE_FREQUENCY.name: "sf_structured_direct",
    PRESCRIPTION.name: "structured_key_family_event_ledger",
    INVESTIGATIONS.name: "structured_key_family_event_ledger",
}
FAMILIES = tuple(SOURCE_PRODUCERS)
EXEMPLAR_LIMIT_PER_THEME = 4


def main() -> None:
    args = _parse_args()
    if not args.protocol.exists():
        raise ValueError(f"predeclared protocol is missing: {args.protocol}")
    config = model_swap.load_model_swap_config(args.config)
    payload = build(config, protocol=args.protocol)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "residual_summary.json"
    panel_path = args.output_dir / "residual_panel.jsonl"
    exemplars_path = args.output_dir / "residual_exemplars.json"
    summary_path.write_text(
        json.dumps(payload["summary_payload"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with panel_path.open("w", encoding="utf-8") as handle:
        for row in payload["panel"]:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    exemplars_path.write_text(
        json.dumps(payload["exemplars"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "letters": payload["summary_payload"]["letter_count"],
                "panel_rows": len(payload["panel"]),
                "final_wrong_default": payload["summary_payload"]["default"][
                    "final_wrong_letters_by_family"
                ],
                "output_dir": args.output_dir.as_posix(),
            },
            sort_keys=True,
        )
    )


def build(
    config: model_swap.ModelSwapConfig,
    *,
    protocol: Path,
) -> dict[str, Any]:
    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(gold)}")
    gold_by_id = {letter.letter_id: letter for letter in gold}

    assembly = _local_assembly(config)
    default_run = build_finding_assembly(
        assembly,
        generated_on=GENERATED_ON,
        gold_loader=lambda _split: gold,
        diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
        diagnosis_policy_variant="default",
        prescription_policy_variant="default",
    )
    joint_run = build_finding_assembly(
        assembly,
        generated_on=GENERATED_ON,
        gold_loader=lambda _split: gold,
        diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
        diagnosis_policy_variant="combined",
        prescription_policy_variant="combined",
    )

    producer_rows = _producer_rows(config, assembly)
    model_owned = _model_owned_letters(producer_rows)
    default_final = _final_letters(default_run)
    joint_final = _final_letters(joint_run)
    default_rows = {str(row["letter_id"]): row for row in default_run.rows}
    joint_rows = {str(row["letter_id"]): row for row in joint_run.rows}

    panel: list[dict[str, Any]] = []
    for letter in gold:
        for family in FAMILIES:
            panel.append(
                _panel_row(
                    letter=letter,
                    family=family,
                    config=config,
                    producer_rows=producer_rows,
                    model_owned=model_owned,
                    default_final=default_final,
                    joint_final=joint_final,
                    default_row=default_rows[letter.letter_id],
                    joint_row=joint_rows[letter.letter_id],
                )
            )

    summary = _summary(
        panel,
        default_run=default_run,
        joint_run=joint_run,
        gold=gold,
        protocol=protocol,
        config=config,
    )
    exemplars = _exemplars(panel, gold_by_id=gold_by_id)
    return {
        "panel": panel,
        "summary_payload": summary,
        "exemplars": exemplars,
    }


def _local_assembly(config: model_swap.ModelSwapConfig) -> Any:
    """Use working-tree producer paths already declared in the Luna config."""

    return replace(config.assembly, split="dev", row_count=140)


def _producer_rows(
    config: model_swap.ModelSwapConfig,
    assembly: Any,
) -> dict[str, dict[str, dict[str, Any]]]:
    rows: dict[str, dict[str, dict[str, Any]]] = {}
    for producer_id, producer in assembly.producers.items():
        path = Path(producer.artifact)
        if not path.exists():
            raise FileNotFoundError(path)
        rows[producer_id] = {
            str(row["letter_id"]): row for row in baseline._read_jsonl(path)
        }
    if not SF_MODEL_OWNED_ARTIFACT.exists():
        raise FileNotFoundError(SF_MODEL_OWNED_ARTIFACT)
    rows["sf_structured_direct"] = {
        str(row["letter_id"]): row
        for row in baseline._read_jsonl(SF_MODEL_OWNED_ARTIFACT)
    }
    # Keep config artifact path for provenance even though SF model-owned
    # comes from the dedicated direct adapter file.
    _ = config
    return rows


def _model_owned_letters(
    producer_rows: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    by_family: dict[str, dict[str, Any]] = {}
    for family, producer_id in SOURCE_PRODUCERS.items():
        predictions = predictions_from_rows(
            list(producer_rows[producer_id].values()),
            "predicted_mentions",
        )
        by_family[family] = {
            prediction.letter_id: to_exect_letter(prediction) for prediction in predictions
        }
    return by_family


def _final_letters(run: Any) -> dict[str, Any]:
    return {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in run.views["clinical_headline"].predictions
    }


def _panel_row(
    *,
    letter: Any,
    family: str,
    config: model_swap.ModelSwapConfig,
    producer_rows: dict[str, dict[str, dict[str, Any]]],
    model_owned: dict[str, dict[str, Any]],
    default_final: dict[str, Any],
    joint_final: dict[str, Any],
    default_row: dict[str, Any],
    joint_row: dict[str, Any],
) -> dict[str, Any]:
    producer_id = SOURCE_PRODUCERS[family]
    source_mentions = [
        mention
        for mention in model_owned[family][letter.letter_id].annotations
        if mention.entity == family
    ]
    default_annotations = [
        annotation
        for annotation in default_final[letter.letter_id].annotations
        if annotation.entity == family
    ]
    joint_annotations = [
        annotation
        for annotation in joint_final[letter.letter_id].annotations
        if annotation.entity == family
    ]
    gold_mentions = [
        annotation for annotation in letter.annotations if annotation.entity == family
    ]
    source_keys = Counter(
        clinical_headline_unit_keys(family, source_mentions, letter.note_text)
    )
    default_keys = Counter(
        clinical_headline_unit_keys(family, default_annotations, letter.note_text)
    )
    joint_keys = Counter(
        clinical_headline_unit_keys(family, joint_annotations, letter.note_text)
    )
    gold_keys = Counter(
        clinical_headline_unit_keys(family, gold_mentions, letter.note_text)
    )

    source_correct = source_keys == gold_keys
    default_correct = default_keys == gold_keys
    joint_correct = joint_keys == gold_keys
    default_lane = default_row["lanes"][family]
    joint_lane = joint_row["lanes"][family]
    source_evidence_mentions = [
        mention
        for mention in producer_rows[producer_id][letter.letter_id].get(
            "predicted_mentions", []
        )
        if str(mention.get("entity", "")) == family
    ]
    # SF actions live on the projection/suppression producer used by assembly.
    action_producers = dict(producer_rows)
    if "sf_model_projection_suppression" not in action_producers:
        # Config producer id for Luna SF final path.
        for key in producer_rows:
            if key.startswith("sf_"):
                action_producers.setdefault("sf_model_projection_suppression", producer_rows[key])
    actions = baseline._actions_for_row(
        family,
        default_lane,
        action_producers,
        letter.letter_id,
    )
    evidence = baseline._evidence_record(
        letter.note_text,
        source_evidence_mentions,
        default_lane.get("predicted_mentions", []),
    )
    mechanism_groups = baseline._mechanism_groups(family, actions)
    first_owner = (
        baseline._first_owner(actions, mechanism_groups)
        if source_keys != default_keys
        else "unchanged"
    )
    subproblem, case_tags = baseline._classify_case(family, mechanism_groups)
    theme = _theme(
        family=family,
        gold_keys=gold_keys,
        source_keys=source_keys,
        default_keys=default_keys,
        source_correct=source_correct,
        default_correct=default_correct,
        joint_correct=joint_correct,
        mechanism_groups=mechanism_groups,
    )
    return {
        "schema_version": "exectv2.luna_single_call_dev140_residual_map.v1",
        "dataset": "ExECTv2",
        "split": "dev140",
        "letter_id": letter.letter_id,
        "model": config.model,
        "model_label": config.model_label,
        "family": family,
        "prompt_version": "exectv2_hybrid_key_family_event_ledger_v0.9.24",
        "replay_mode": "saved_output_no_call",
        "source_producer": producer_id,
        "model_owned_keys": baseline._counter_rows(source_keys),
        "default_final_keys": baseline._counter_rows(default_keys),
        "joint_final_keys": baseline._counter_rows(joint_keys),
        "family_local_gold_keys": baseline._counter_rows(gold_keys),
        "model_owned_correct": source_correct,
        "default_final_correct": default_correct,
        "joint_final_correct": joint_correct,
        "default_change_direction": model_led_dev_regressions.change_direction(
            source_correct,
            default_correct,
        )
        if source_keys != default_keys
        else "unchanged",
        "joint_vs_default_direction": model_led_dev_regressions.change_direction(
            default_correct,
            joint_correct,
        )
        if default_keys != joint_keys
        else "unchanged",
        "empty_gold": len(gold_keys) == 0,
        "selected_evidence": evidence["items"],
        "evidence_status": evidence["status"],
        "deterministic_actions": actions if source_keys != default_keys else [],
        "mechanism_groups": mechanism_groups if source_keys != default_keys else [],
        "first_prediction_changing_owner": first_owner,
        "clinical_subproblem": subproblem,
        "case_tags": case_tags,
        "theme": theme,
        "default_fact_origins": _fact_origins(default_lane.get("predicted_mentions", [])),
        "joint_fact_origins": _fact_origins(joint_lane.get("predicted_mentions", [])),
    }


def _theme(
    *,
    family: str,
    gold_keys: Counter[Any],
    source_keys: Counter[Any],
    default_keys: Counter[Any],
    source_correct: bool,
    default_correct: bool,
    joint_correct: bool,
    mechanism_groups: list[str],
) -> str:
    if default_correct and joint_correct and source_correct:
        return "all_correct"
    if len(gold_keys) == 0 and (not source_correct or not default_correct):
        return "annotation_or_empty_gold"
    mechanisms = " ".join(mechanism_groups).lower()
    if family == SEIZURE_FREQUENCY.name:
        blob = json.dumps(
            [
                baseline._jsonable(key)
                for key in list(gold_keys) + list(source_keys) + list(default_keys)
            ],
            sort_keys=True,
        ).lower()
        if any(token in blob for token in ("seizure-free", "seizure_free", "unknown")):
            return "sf_state_boundary"
        if any(token in blob for token in ("rate", "per ", "cluster", "month", "week", "day")):
            return "sf_rate_construction"
        if "seizure_free" in mechanisms or "unknown" in mechanisms:
            return "sf_state_boundary"
        return "sf_rate_construction"
    if family == DIAGNOSIS.name:
        if any(token in mechanisms for token in ("residual", "added", "drop")):
            return "dx_specificity"
        if not default_correct:
            return "dx_specificity"
        return "other"
    if family == PRESCRIPTION.name:
        if not default_correct or not joint_correct:
            return "rx_current_regimen"
        return "other"
    return "other"


def _fact_origins(mentions: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for mention in mentions:
        counts[str(mention.get("fact_origin", "unspecified"))] += 1
    return dict(sorted(counts.items()))


def _summary(
    panel: list[dict[str, Any]],
    *,
    default_run: Any,
    joint_run: Any,
    gold: list[Any],
    protocol: Path,
    config: model_swap.ModelSwapConfig,
) -> dict[str, Any]:
    def _family_counts(correct_field: str) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for family in FAMILIES:
            rows = [row for row in panel if row["family"] == family]
            wrong = [row for row in rows if not row[correct_field]]
            out[family] = {
                "letters": len(rows),
                "correct": len(rows) - len(wrong),
                "wrong": len(wrong),
                "empty_gold_wrong": sum(1 for row in wrong if row["empty_gold"]),
                "exact_evidence_among_wrong": sum(
                    1 for row in wrong if row["evidence_status"] == "exact"
                ),
            }
        return out

    theme_counts = Counter(row["theme"] for row in panel if not row["default_final_correct"])
    prompt_seed_themes = {
        theme: count
        for theme, count in sorted(theme_counts.items())
        if theme
        in {
            "sf_rate_construction",
            "sf_state_boundary",
            "dx_specificity",
        }
    }
    default_ladder = default_run.report["score_ladder"]["headline_target"]
    joint_ladder = joint_run.report["score_ladder"]["headline_target"]
    return {
        "schema_version": "exectv2.luna_single_call_dev140_residual_map.v1",
        "generated_on": GENERATED_ON,
        "protocol": protocol.as_posix(),
        "model": config.model,
        "model_label": config.model_label,
        "prompt_version": "exectv2_hybrid_key_family_event_ledger_v0.9.24",
        "config_path": config.path.as_posix(),
        "letter_count": len(gold),
        "call_mode": "saved_output_no_call",
        "new_model_calls": 0,
        "scorer": "family_local_clinical_headline_unit_keys",
        "default": {
            "policy": {"diagnosis": "default", "prescription": "default"},
            "headline_f1": float(default_ladder["overall"]["f1"]),
            "family_f1": {
                family: float(default_ladder["by_indicator"][family]["f1"])
                for family in FAMILIES
            },
            "model_owned_wrong_letters_by_family": {
                family: counts["wrong"]
                for family, counts in _family_counts("model_owned_correct").items()
            },
            "final_wrong_letters_by_family": {
                family: counts["wrong"]
                for family, counts in _family_counts("default_final_correct").items()
            },
            "family_local_counts": _family_counts("default_final_correct"),
            "model_owned_counts": _family_counts("model_owned_correct"),
            "change_directions": dict(
                Counter(
                    row["default_change_direction"]
                    for row in panel
                    if row["default_change_direction"] != "unchanged"
                )
            ),
        },
        "joint": {
            "policy": {"diagnosis": "combined", "prescription": "combined"},
            "headline_f1": float(joint_ladder["overall"]["f1"]),
            "family_f1": {
                family: float(joint_ladder["by_indicator"][family]["f1"])
                for family in FAMILIES
            },
            "final_wrong_letters_by_family": {
                family: counts["wrong"]
                for family, counts in _family_counts("joint_final_correct").items()
            },
            "family_local_counts": _family_counts("joint_final_correct"),
            "vs_default_directions": dict(
                Counter(
                    row["joint_vs_default_direction"]
                    for row in panel
                    if row["joint_vs_default_direction"] != "unchanged"
                )
            ),
        },
        "themes_on_default_final_wrong": dict(theme_counts),
        "prompt_seed_theme_counts": prompt_seed_themes,
        "prompt_addressable_estimate": {
            "default_final_wrong_letters": sum(
                1 for row in panel if not row["default_final_correct"]
            ),
            "joint_final_wrong_letters": sum(
                1 for row in panel if not row["joint_final_correct"]
            ),
            "seed_theme_wrong_letters": sum(
                1
                for row in panel
                if not row["default_final_correct"]
                and row["theme"]
                in {"sf_rate_construction", "sf_state_boundary", "dx_specificity"}
            ),
            "empty_gold_among_default_final_wrong": sum(
                1
                for row in panel
                if not row["default_final_correct"] and row["empty_gold"]
            ),
        },
        "claim_boundary": (
            "ExECTv2 dev140 development mechanism evidence for GPT-5.6 Luna under "
            "saved single-call producers. Not test60, clinical validation, or "
            "prompt/ruleset promotion."
        ),
    }


def _exemplars(
    panel: list[dict[str, Any]],
    *,
    gold_by_id: dict[str, Any],
) -> dict[str, Any]:
    themes = (
        "sf_rate_construction",
        "sf_state_boundary",
        "dx_specificity",
        "rx_current_regimen",
        "annotation_or_empty_gold",
    )
    by_theme: dict[str, list[dict[str, Any]]] = {theme: [] for theme in themes}
    for row in panel:
        if row["default_final_correct"] and row["joint_final_correct"]:
            continue
        theme = row["theme"]
        if theme not in by_theme:
            continue
        if len(by_theme[theme]) >= EXEMPLAR_LIMIT_PER_THEME:
            continue
        note = gold_by_id[row["letter_id"]].note_text
        evidence_items = [
            item
            for item in row["selected_evidence"]
            if item.get("stage") in {"model_owned", "final"} and item.get("evidence")
        ][:3]
        by_theme[theme].append(
            {
                "letter_id": row["letter_id"],
                "family": row["family"],
                "theme": theme,
                "model_owned_correct": row["model_owned_correct"],
                "default_final_correct": row["default_final_correct"],
                "joint_final_correct": row["joint_final_correct"],
                "empty_gold": row["empty_gold"],
                "evidence_status": row["evidence_status"],
                "first_prediction_changing_owner": row[
                    "first_prediction_changing_owner"
                ],
                "model_owned_keys": row["model_owned_keys"],
                "default_final_keys": row["default_final_keys"],
                "joint_final_keys": row["joint_final_keys"],
                "family_local_gold_keys": row["family_local_gold_keys"],
                "selected_evidence": evidence_items,
                "note_excerpt": _excerpt(note, evidence_items),
                "prompt_variant_hint": {
                    "sf_rate_construction": "B",
                    "sf_state_boundary": "C",
                    "dx_specificity": "C",
                    "rx_current_regimen": "rules_not_prompt",
                    "annotation_or_empty_gold": "diagnostic_only",
                }.get(theme, "other"),
            }
        )
    return {
        "schema_version": "exectv2.luna_single_call_dev140_residual_map.v1",
        "generated_on": GENERATED_ON,
        "selection_rule": (
            f"up to {EXEMPLAR_LIMIT_PER_THEME} default-or-joint final-wrong rows "
            "per theme, first in letter×family order"
        ),
        "by_theme": by_theme,
    }


def _excerpt(note_text: str, evidence_items: list[dict[str, Any]]) -> str:
    for item in evidence_items:
        evidence = str(item.get("evidence", "")).strip()
        if evidence and evidence in note_text:
            idx = note_text.index(evidence)
            start = max(0, idx - 80)
            end = min(len(note_text), idx + len(evidence) + 80)
            return note_text[start:end].replace("\n", " ")
    return note_text[:240].replace("\n", " ")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    main()
