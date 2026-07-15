"""Analyze decision-0040 deterministic changes on permitted ExECTv2 dev140.

This no-call study rehydrates historical full200 producer blobs, copies only
declared dev140 rows into temporary files, then assembles and compares the
model-owned and post-rule family outputs. It never writes test60 row content.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import EvidenceGrade, grade_evidence, is_grounded
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    _target_surface,
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.reporting import (
    architecture_report,
)

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
OUTPUT_PATH = Path("experiments/exectv2_model_led_dev140_regression_analysis_20260715.json")
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_model_led_dev140_regression_analysis_protocol_2026-07-15.md"
)
GENERATED_ON = "2026-07-15"
SOURCE_PRODUCERS = {
    DIAGNOSIS.name: "diagnosis_decomposer",
    SEIZURE_FREQUENCY.name: "sf_model_direct",
    PRESCRIPTION.name: "structured_key_family_event_ledger",
    INVESTIGATIONS.name: "structured_key_family_event_ledger",
}
FAMILIES = tuple(SOURCE_PRODUCERS)


def main() -> None:
    args = _parse_args()
    configs = [
        model_swap.load_model_swap_config(path)
        for path in sorted(args.config_dir.glob("*.json"))
    ]
    payload = analyze(configs)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "models": len(payload["models"]),
                "changed_rows": len(payload["rows"]),
                "correct_to_wrong": payload["summary"]["primary_family_local"][
                    "directions"
                ].get("correct_to_wrong", 0),
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )


def analyze(configs: list[model_swap.ModelSwapConfig]) -> dict[str, Any]:
    if not PROTOCOL_PATH.exists():
        raise ValueError(f"predeclared protocol is missing: {PROTOCOL_PATH}")
    parity = model_swap.validate_same_core_configs(configs)
    if not parity["component_graph_identical"]:
        raise ValueError(f"model-led configurations differ: {parity['mismatched_candidates']}")
    for config in configs:
        contract = model_swap.validate_model_led_architecture(config)
        if contract["status"] != "pass":
            raise ValueError(f"{config.path}: {contract['violations']}")

    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(gold)}")
    dev_ids = {letter.letter_id for letter in gold}
    records: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="exectv2-model-led-dev140-") as temp:
        root = Path(temp)
        for config in configs:
            replay_config = _materialize_dev_config(
                config,
                root / config.candidate_id,
                dev_ids,
            )
            run = build_finding_assembly(
                replay_config.assembly,
                generated_on=GENERATED_ON,
                gold_loader=lambda _split: gold,
                diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
            )
            model_records = _changed_records(config, replay_config, run, gold)
            records.extend(model_records)
            models[config.model_label] = {
                **_model_summary(model_records),
                "stage_scores": _stage_scores(replay_config, run, gold),
            }

    records.sort(key=lambda row: (row["model_label"], row["family"], row["letter_id"]))
    if any(str(row["letter_id"]) not in dev_ids for row in records):
        raise ValueError("analysis retained a non-dev letter")
    summary = _summary(records)
    return {
        "schema_version": "exectv2_model_led_dev140_regression_analysis_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "architecture_contract": "decision_0040_model_led",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "scorer": (
            "primary family-local clinical_headline_unit_keys; secondary compatibility "
            "view reproduces the full200 audit's entity-agnostic gold surface"
        ),
        "source_output_revision": configs[0].replay_source_revision,
        "config_paths": [config.path.as_posix() for config in configs],
        "dev_letter_count": len(dev_ids),
        "models": models,
        "summary": summary,
        "rows": records,
        "claim_boundary": (
            "Inspected dev140 mechanism evidence only. No test60 row was assembled, "
            "scored, serialized, or inspected; this does not establish holdout transfer, "
            "clinical validity, or a promoted final policy."
        ),
    }


def _materialize_dev_config(
    config: model_swap.ModelSwapConfig,
    destination: Path,
    dev_ids: set[str],
) -> model_swap.ModelSwapConfig:
    destination.mkdir(parents=True, exist_ok=True)
    producers = {}
    for producer_id, producer in config.assembly.producers.items():
        result = subprocess.run(
            [
                "git",
                "show",
                f"{config.replay_source_revision}:{producer.artifact.as_posix()}",
            ],
            check=True,
            capture_output=True,
        )
        target = destination / f"{producer_id}.jsonl"
        target.write_bytes(
            model_led_dev_regressions.filter_jsonl_bytes(
                result.stdout,
                allowed_ids=dev_ids,
            )
        )
        producers[producer_id] = replace(producer, artifact=target)
    assembly = replace(
        config.assembly,
        split="dev",
        row_count=len(dev_ids),
        producers=producers,
    )
    return replace(config, assembly=assembly)


def _changed_records(
    config: model_swap.ModelSwapConfig,
    replay_config: model_swap.ModelSwapConfig,
    run: Any,
    gold: list[Any],
) -> list[dict[str, Any]]:
    final_rows = {str(row["letter_id"]): row for row in run.rows}
    final_predictions = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in run.views["clinical_headline"].predictions
    }
    source_by_family: dict[str, dict[str, Any]] = {}
    producer_rows: dict[str, dict[str, dict[str, Any]]] = {}
    for producer_id, producer in replay_config.assembly.producers.items():
        rows = _read_jsonl(producer.artifact)
        producer_rows[producer_id] = {str(row["letter_id"]): row for row in rows}
    for family, producer_id in SOURCE_PRODUCERS.items():
        predictions = predictions_from_rows(
            list(producer_rows[producer_id].values()),
            "predicted_mentions",
        )
        source_by_family[family] = {
            prediction.letter_id: to_exect_letter(prediction) for prediction in predictions
        }

    records: list[dict[str, Any]] = []
    for letter in gold:
        final_row = final_rows[letter.letter_id]
        for family, producer_id in SOURCE_PRODUCERS.items():
            source_mentions = [
                mention
                for mention in source_by_family[family][letter.letter_id].annotations
                if mention.entity == family
            ]
            source_evidence_mentions = [
                mention
                for mention in producer_rows[producer_id][letter.letter_id].get(
                    "predicted_mentions", []
                )
                if str(mention.get("entity", "")) == family
            ]
            lane = final_row["lanes"][family]
            final_mentions = lane["predicted_mentions"]
            final_annotations = [
                annotation
                for annotation in final_predictions[letter.letter_id].annotations
                if annotation.entity == family
            ]
            gold_mentions = [
                annotation for annotation in letter.annotations if annotation.entity == family
            ]
            source_keys = Counter(
                clinical_headline_unit_keys(family, source_mentions, letter.note_text)
            )
            final_keys = Counter(
                clinical_headline_unit_keys(family, final_annotations, letter.note_text)
            )
            if source_keys == final_keys:
                continue
            family_local_gold_keys = Counter(
                clinical_headline_unit_keys(family, gold_mentions, letter.note_text)
            )
            compatibility_gold_keys = Counter(
                clinical_headline_unit_keys(family, letter.annotations, letter.note_text)
            )
            source_correct = source_keys == compatibility_gold_keys
            final_correct = final_keys == compatibility_gold_keys
            family_local_source_correct = source_keys == family_local_gold_keys
            family_local_final_correct = final_keys == family_local_gold_keys
            actions = _actions_for_row(
                family,
                lane,
                producer_rows,
                letter.letter_id,
            )
            evidence = _evidence_record(
                letter.note_text,
                source_evidence_mentions,
                final_mentions,
            )
            mechanism_groups = _mechanism_groups(family, actions)
            first_owner = _first_owner(actions, mechanism_groups)
            subproblem, case_tags = _classify_case(family, mechanism_groups)
            records.append(
                {
                    "dataset": "ExECTv2",
                    "split": "dev140",
                    "letter_id": letter.letter_id,
                    "model": config.model,
                    "model_label": config.model_label,
                    "family": family,
                    "replay_mode": "saved_output_no_call",
                    "source_producer": producer_id,
                    "source_artifact": config.assembly.producers[producer_id].artifact.as_posix(),
                    "source_revision": config.replay_source_revision,
                    "scorer": "clinical_headline_unit_keys",
                    "model_owned_keys": _counter_rows(source_keys),
                    "final_keys": _counter_rows(final_keys),
                    "compatibility_gold_keys": _counter_rows(compatibility_gold_keys),
                    "family_local_gold_keys": _counter_rows(family_local_gold_keys),
                    "model_owned_correct": source_correct,
                    "final_correct": final_correct,
                    "change_direction": model_led_dev_regressions.change_direction(
                        source_correct,
                        final_correct,
                    ),
                    "family_local_model_owned_correct": family_local_source_correct,
                    "family_local_final_correct": family_local_final_correct,
                    "family_local_change_direction": (
                        model_led_dev_regressions.change_direction(
                            family_local_source_correct,
                            family_local_final_correct,
                        )
                    ),
                    "selected_evidence": evidence["items"],
                    "evidence_status": evidence["status"],
                    "deterministic_actions": actions,
                    "mechanism_groups": mechanism_groups,
                    "first_prediction_changing_owner": first_owner,
                    "clinical_subproblem": subproblem,
                    "case_tags": case_tags,
                }
            )
    return records


def _actions_for_row(
    family: str,
    lane: dict[str, Any],
    producer_rows: dict[str, dict[str, dict[str, Any]]],
    letter_id: str,
) -> list[dict[str, Any]]:
    if family == SEIZURE_FREQUENCY.name:
        row = producer_rows["sf_model_projection_suppression"][letter_id]
        actions = []
        for stage, key in (
            ("seizure_frequency_projection", "projection_actions"),
            ("seizure_frequency_suppression", "suppression_actions"),
        ):
            for action in row.get(key, []):
                actions.append(
                    {
                        "stage": stage,
                        "action": str(action.get("action", "unknown")),
                        "mechanism": str(action.get("rule_id", "unresolved")),
                        "owner": "deterministic_sf_post_processing",
                        "detail": {
                            str(k): v
                            for k, v in action.items()
                            if k not in {"evidence", "text"}
                        },
                    }
                )
        return actions or [_unresolved_action(family)]

    actions_by_key: dict[str, dict[str, Any]] = {}
    ignored = {
        "emitted_raw_candidate",
        "emitted_scored_candidate",
        "selected_saved_artifact_mentions",
        "applied_standard_dictionary_diagnosis_repair",
        "applied_standard_dictionary_prescription_repair",
    }
    for mention in lane.get("predicted_mentions", []):
        for event in mention.get("provenance", []):
            action = str(event.get("action", ""))
            if not action or action in ignored:
                continue
            key = json.dumps(event, sort_keys=True)
            actions_by_key[key] = {
                "stage": str(event.get("stage", "entity_lens")),
                "action": action,
                "mechanism": action,
                "owner": str(event.get("owner", "unresolved")),
                "portability": event.get("portability"),
                "detail": dict(event.get("detail", {})),
            }
    diagnostics = lane.get("lens_diagnostics", {})
    for name, value in diagnostics.items():
        if not name.endswith("_findings") or not isinstance(value, int) or value <= 0:
            continue
        if name == "selected_findings":
            continue
        mechanism = name.removesuffix("_findings")
        action = {
            "stage": "entity_lens_summary",
            "action": mechanism,
            "mechanism": mechanism,
            "owner": "standard_dictionary",
            "count": value,
        }
        actions_by_key.setdefault(json.dumps(action, sort_keys=True), action)
    return sorted(actions_by_key.values(), key=lambda row: json.dumps(row, sort_keys=True)) or [
        _unresolved_action(family)
    ]


def _unresolved_action(family: str) -> dict[str, str]:
    return {
        "stage": "unresolved",
        "action": "unresolved",
        "mechanism": f"{family}_changed_without_specific_retained_action",
        "owner": "unresolved",
    }


def _mechanism_groups(family: str, actions: list[dict[str, Any]]) -> list[str]:
    groups: set[str] = set()
    for action in actions:
        mechanism = str(action.get("mechanism", "unresolved"))
        lowered = mechanism.lower()
        if family == DIAGNOSIS.name:
            if "focal_epilepsy" in lowered or "heading_recovery" in lowered:
                groups.add("diagnosis_heading_recovery")
            elif "added" in lowered or "residual" in lowered:
                groups.add("diagnosis_residual_addition")
            elif "dropped" in lowered:
                groups.add("diagnosis_drop")
            elif "repair" in lowered or "rewrite" in lowered:
                groups.add("diagnosis_attribute_or_concept_rewrite")
            else:
                groups.add("diagnosis_unresolved")
        elif family == PRESCRIPTION.name:
            if "added" in lowered or "residual" in lowered:
                groups.add("prescription_residual_addition")
            elif "dropped" in lowered:
                groups.add("prescription_drop")
            elif "split" in lowered:
                groups.add("prescription_regimen_split")
            elif "normal" in lowered:
                groups.add("prescription_normalization")
            else:
                groups.add("prescription_unresolved")
        elif family == SEIZURE_FREQUENCY.name:
            groups.add(mechanism)
        else:
            groups.add("investigations_thin_adapter")
    return sorted(groups)


def _first_owner(
    actions: list[dict[str, Any]],
    mechanism_groups: list[str],
) -> str:
    owners = {str(action.get("owner", "unresolved")) for action in actions}
    if len(owners) == 1 and len(mechanism_groups) == 1:
        return f"{next(iter(owners))}:{mechanism_groups[0]}"
    return "unresolved_multiple_candidate_actions"


def _classify_case(family: str, mechanism_groups: list[str]) -> tuple[str, list[str]]:
    mechanisms = " ".join(mechanism_groups).lower()
    if family == DIAGNOSIS.name:
        subproblem = (
            "candidate_generation"
            if any(token in mechanisms for token in ("added", "dropped", "residual"))
            else "benchmark_formatting"
        )
    elif family == SEIZURE_FREQUENCY.name:
        if any(token in mechanisms for token in ("seizure_free", "last_event")):
            subproblem = "seizure_free_boundary"
        elif any(token in mechanisms for token in ("rate", "time", "period", "denominator")):
            subproblem = "rate_denominator"
        elif "ownership" in mechanisms:
            subproblem = "competing_event_selection"
        else:
            subproblem = "uncertainty_boundary"
    elif family == PRESCRIPTION.name:
        subproblem = (
            "candidate_generation"
            if any(token in mechanisms for token in ("added", "dropped", "residual"))
            else "benchmark_formatting"
        )
    else:
        subproblem = "evidence_selection"
    tags = sorted(
        {
            family.lower(),
            *(group.lower().replace(" ", "_") for group in mechanism_groups),
        }
    )
    return subproblem, tags


def _evidence_record(
    note_text: str,
    source_mentions: list[dict[str, Any]],
    final_mentions: list[dict[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, str]] = []
    for stage, mentions in (
        ("model_owned", source_mentions),
        ("final", final_mentions),
    ):
        for mention in mentions:
            evidence = str(mention.get("evidence", ""))
            grade = grade_evidence(note_text, evidence)
            items.append({"stage": stage, "evidence": evidence, "grade": grade.value})
    grades = [EvidenceGrade(item["grade"]) for item in items]
    if not items or all(grade == EvidenceGrade.EMPTY for grade in grades):
        status = "missing"
    elif any(not is_grounded(grade) for grade in grades):
        status = "invalid"
    elif all(grade == EvidenceGrade.EXACT for grade in grades):
        status = "exact"
    else:
        status = "source-near"
    return {"items": items, "status": status}


def _counter_rows(counter: Counter[Any]) -> list[dict[str, Any]]:
    rows = [{"key": _jsonable(key), "count": count} for key, count in counter.items()]
    return sorted(rows, key=lambda row: json.dumps(row["key"], sort_keys=True))


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _model_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return _summary(records)


def _stage_scores(
    config: model_swap.ModelSwapConfig,
    run: Any,
    gold: list[Any],
) -> dict[str, Any]:
    source_predictions: dict[str, dict[str, PredictedLetter]] = {}
    for family, producer_id in SOURCE_PRODUCERS.items():
        predictions = predictions_from_rows(
            _read_jsonl(config.assembly.producers[producer_id].artifact),
            "predicted_mentions",
        )
        source_predictions[family] = {
            prediction.letter_id: prediction for prediction in predictions
        }
    combined = [
        PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                mention
                for family in FAMILIES
                for mention in source_predictions[family][letter.letter_id].mentions
                if mention.entity == family
            ),
        )
        for letter in gold
    ]
    source_arch = architecture_report(
        name="model_owned_dev140",
        ownership="named_model_before_deterministic_clinical_changes",
        gold_letters=gold,
        pred_letters=combined,
        entities=FAMILIES,
    )
    source = _target_surface(source_arch, projected=True)
    final = run.report["score_ladder"]["headline_target"]
    return {
        "model_owned": _score_rows(source),
        "final_post_rule": _score_rows(final),
    }


def _score_rows(payload: dict[str, Any]) -> dict[str, float]:
    return {
        "overall": round(float(payload["overall"]["f1"]), 4),
        **{
            family: round(float(payload["by_indicator"][family]["f1"]), 4)
            for family in FAMILIES
        },
    }


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    compatibility = _direction_summary(records, "change_direction")
    family_local = _direction_summary(records, "family_local_change_direction")
    evidence_status = Counter(str(row["evidence_status"]) for row in records)
    return {
        "changed_rows": len(records),
        "primary_family_local": family_local,
        "compatibility_audit": compatibility,
        "evidence_status": dict(sorted(evidence_status.items())),
    }


def _direction_summary(
    records: list[dict[str, Any]],
    direction_field: str,
) -> dict[str, Any]:
    directions = Counter(str(row[direction_field]) for row in records)
    families: dict[str, Counter[str]] = defaultdict(Counter)
    mechanisms: dict[str, Counter[str]] = defaultdict(Counter)
    for row in records:
        family = str(row["family"])
        direction = str(row[direction_field])
        families[family][direction] += 1
        for mechanism in row["mechanism_groups"]:
            mechanisms[str(mechanism)][direction] += 1
    return {
        "directions": dict(sorted(directions.items())),
        "by_family": {
            family: dict(sorted(counts.items())) for family, counts in sorted(families.items())
        },
        "by_mechanism": {
            mechanism: dict(sorted(counts.items()))
            for mechanism, counts in sorted(mechanisms.items())
        },
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
