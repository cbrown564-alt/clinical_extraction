"""Reproduce the decision-0040 ExECT architecture audit without model calls.

The historical full200 producer outputs stay in the recorded Git revision. This
check materializes them in a temporary directory, computes aggregate-only
scores and attribution diagnostics, and compares them with the retained audit
artifact. It never prints or serializes full200 rows.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    score_frequency_state,
)

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
AUDIT_PATH = Path("experiments/exectv2_llm_with_rules_component_audit_full200_20260714.json")
REPLAY_PATH = Path("experiments/exectv2_model_led_architecture_replay_full200_20260715.json")
GENERATED_ON = "2026-07-15"


def main() -> None:
    args = _parse_args()
    configs = [
        model_swap.load_model_swap_config(path)
        for path in sorted(args.config_dir.glob("*.json"))
    ]
    payload = reproduce_audit(configs)
    expected = json.loads(args.audit.read_text(encoding="utf-8"))
    _assert_audit_scores(payload, expected)
    if args.write:
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        retained = json.loads(args.output.read_text(encoding="utf-8"))
        if retained != payload:
            raise SystemExit(f"model-led replay drifted from {args.output}")
    print(
        json.dumps(
            {
                "status": "pass",
                "models": len(payload["models"]),
                "architecture_contract": payload["architecture_contract"],
                "row_policy": payload["row_policy"],
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )


def reproduce_audit(configs: list[model_swap.ModelSwapConfig]) -> dict[str, Any]:
    parity = model_swap.validate_same_core_configs(configs)
    if not parity["component_graph_identical"]:
        raise ValueError(f"model-led configurations differ: {parity['mismatched_candidates']}")
    for config in configs:
        contract = model_swap.validate_model_led_architecture(config)
        if contract["status"] != "pass":
            raise ValueError(f"{config.path}: {contract['violations']}")

    gold = load_letters()[:200]
    models: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="exectv2-model-led-audit-") as temp:
        root = Path(temp)
        for config in configs:
            replay_config = _materialize_config(config, root / config.candidate_id)
            run = build_finding_assembly(
                replay_config.assembly,
                generated_on=GENERATED_ON,
                gold_loader=lambda _split: gold,
                diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
            )
            models[config.model_label] = _aggregate_result(config, replay_config, run, gold)

    return {
        "schema_version": "exectv2_model_led_architecture_replay_v1",
        "generated_on": GENERATED_ON,
        "architecture_contract": "decision_0040_model_led",
        "source_output_revision": configs[0].replay_source_revision,
        "dataset": "ExECTv2",
        "split": "full200",
        "row_policy": "aggregate_only_no_test60_or_full200_row_inspection",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "scorer": "current clinical_headline plus seizure-frequency state_profile",
        "config_paths": [config.path.as_posix() for config in configs],
        "component_graph_identical": True,
        "models": models,
        "claim_boundary": (
            "Development-inclusive aggregate-only architecture replay. It does not establish "
            "an independent holdout, clinical validation, or the final six-model comparison."
        ),
    }


def _materialize_config(
    config: model_swap.ModelSwapConfig,
    destination: Path,
) -> model_swap.ModelSwapConfig:
    destination.mkdir(parents=True, exist_ok=True)
    producers = {}
    for producer_id, producer in config.assembly.producers.items():
        target = destination / f"{producer_id}.jsonl"
        result = subprocess.run(
            [
                "git",
                "show",
                f"{config.replay_source_revision}:{producer.artifact.as_posix()}",
            ],
            check=True,
            capture_output=True,
        )
        target.write_bytes(result.stdout)
        producers[producer_id] = replace(producer, artifact=target)
    return replace(config, assembly=replace(config.assembly, producers=producers))


def _aggregate_result(
    config: model_swap.ModelSwapConfig,
    replay_config: model_swap.ModelSwapConfig,
    run: Any,
    gold: list[Any],
) -> dict[str, Any]:
    headline = run.report["score_ladder"]["headline_target"]
    prediction_letters = [
        to_exect_letter(prediction) for prediction in run.views["clinical_headline"].predictions
    ]
    sf_scores = score_frequency_state(gold, prediction_letters)
    lane_diagnostics = run.report.get("lane_diagnostics", {})
    diagnostic_rows = [
        value for value in lane_diagnostics.values() if isinstance(value, dict)
    ]
    sf_rows = _read_jsonl(
        replay_config.assembly.producers["sf_model_projection_suppression"].artifact
    )
    return {
        "model": config.model,
        "scores": {
            "overall": _rounded(headline["overall"]["f1"]),
            **{
                _snake_case(entity): _rounded(headline["by_indicator"][entity]["f1"])
                for entity in TARGET_INDICATORS
            },
            "seizure_frequency_state_profile": _rounded(sf_scores.state_profile.f1),
        },
        "diagnostics": {
            "call_failures": sum(int(row.get("call_failures", 0)) for row in diagnostic_rows),
            "parse_schema_failures": sum(
                int(row.get("parse_schema_failures", 0)) for row in diagnostic_rows
            ),
            "evidence_invalid_dropped": sum(
                int(row.get("evidence_invalid_dropped", 0)) for row in diagnostic_rows
            ),
            "minimum_exact_evidence_rate": min(
                [float(row.get("exact_evidence_rate", 0.0)) for row in diagnostic_rows]
                or [1.0]
            ),
        },
        "post_model_actions": {
            "seizure_frequency_projection": sum(
                len(row.get("projection_actions", [])) for row in sf_rows
            ),
            "seizure_frequency_suppression": sum(
                len(row.get("suppression_actions", [])) for row in sf_rows
            ),
        },
        "deterministic_regression_accounting": _regression_accounting(
            replay_config,
            run,
            gold,
        ),
        "fact_origin_accounting": run.report.get("fact_origin_accounting", {}),
        "lane_sources": _stable_lane_sources(config, run.report.get("lane_sources", {})),
        "diagnosis_resolution_candidate": run.report["diagnosis_resolution_candidate"],
    }


def _regression_accounting(
    config: model_swap.ModelSwapConfig,
    run: Any,
    gold: list[Any],
) -> dict[str, dict[str, int]]:
    source_producer = {
        DIAGNOSIS.name: "diagnosis_decomposer",
        SEIZURE_FREQUENCY.name: "sf_model_direct",
        PRESCRIPTION.name: "structured_key_family_event_ledger",
        INVESTIGATIONS.name: "structured_key_family_event_ledger",
    }
    final_by_id = {
        prediction.letter_id: prediction
        for prediction in run.views["clinical_headline"].predictions
    }
    accounting: dict[str, dict[str, int]] = {}
    for entity, producer_id in source_producer.items():
        source_rows = _read_jsonl(config.assembly.producers[producer_id].artifact)
        source_by_id = {
            prediction.letter_id: prediction
            for prediction in predictions_from_rows(source_rows, "predicted_mentions")
        }
        counts = Counter()
        for letter in gold:
            gold_keys = _headline_keys(entity, letter.annotations, letter.note_text)
            source_keys = _headline_keys(
                entity,
                [
                    mention
                    for mention in to_exect_letter(source_by_id[letter.letter_id]).annotations
                    if mention.entity == entity
                ],
                letter.note_text,
            )
            final_keys = _headline_keys(
                entity,
                [
                    mention
                    for mention in to_exect_letter(final_by_id[letter.letter_id]).annotations
                    if mention.entity == entity
                ],
                letter.note_text,
            )
            source_correct = source_keys == gold_keys
            final_correct = final_keys == gold_keys
            changed = source_keys != final_keys
            counts["changed_rows"] += int(changed)
            counts["wrong_to_correct"] += int(not source_correct and final_correct)
            counts["correct_to_wrong"] += int(source_correct and not final_correct)
        accounting[_snake_case(entity)] = dict(counts)
    return accounting


def _headline_keys(entity: str, annotations: Any, note_text: str) -> Counter[Any]:
    return Counter(clinical_headline_unit_keys(entity, annotations, note_text))


def _stable_lane_sources(
    config: model_swap.ModelSwapConfig,
    lane_sources: dict[str, Any],
) -> dict[str, Any]:
    stable = json.loads(json.dumps(lane_sources))
    for entity, payload in stable.items():
        lens = config.assembly.lenses[entity]
        payload["artifact"] = config.assembly.producers[lens.producer].artifact.as_posix()
    return stable


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _assert_audit_scores(payload: dict[str, Any], audit: dict[str, Any]) -> None:
    expected_models = audit["intended_model_led_replay"]
    for label, result in payload["models"].items():
        expected = expected_models[label]["scores"]
        actual = result["scores"]
        for metric, expected_value in expected.items():
            if actual[metric] != expected_value:
                raise ValueError(
                    f"{label} {metric}: replay={actual[metric]} audit={expected_value}"
                )


def _rounded(value: float) -> float:
    return round(float(value), 4)


def _snake_case(value: str) -> str:
    chars: list[str] = []
    for char in value:
        if char.isupper() and chars:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--audit", type=Path, default=AUDIT_PATH)
    parser.add_argument("--output", type=Path, default=REPLAY_PATH)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
