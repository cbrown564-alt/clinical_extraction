"""Replay the frozen ExECT model-confidence study without model calls or test60 rows."""

from __future__ import annotations

import argparse
import hashlib
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_reported_confidence as confidence,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_swap,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
OUTPUT = Path("experiments/exectv2_model_reported_confidence_out_of_sample_20260715.json")
REPORT = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_model_reported_confidence_out_of_sample_2026-07-15.md"
)
PROTOCOL = Path(
    "docs/experiments/exectv2/reliability/exectv2_model_reported_confidence_protocol_2026-07-15.md"
)
FAMILIES = (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name)
SOURCE_PRODUCERS = {
    DIAGNOSIS.name: "diagnosis_decomposer",
    SEIZURE_FREQUENCY.name: "sf_model_direct",
    PRESCRIPTION.name: "structured_key_family_event_ledger",
    INVESTIGATIONS.name: "structured_key_family_event_ledger",
}


def main() -> None:
    args = _parse_args()
    configs = [
        model_swap.load_model_swap_config(path) for path in sorted(args.config_dir.glob("*.json"))
    ]
    payload = build_study(configs)
    markdown = render_report(payload)
    if args.write:
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        args.report.write_text(markdown, encoding="utf-8")
    else:
        expected = json.loads(args.output.read_text(encoding="utf-8"))
        if payload != expected:
            raise SystemExit(f"model-reported confidence replay drifted from {args.output}")
        if markdown != args.report.read_text(encoding="utf-8"):
            raise SystemExit(f"model-reported confidence report drifted from {args.report}")
    print(
        json.dumps(
            {
                "status": "pass",
                "models": len(payload["models"]),
                "test60_rows_emitted": 0,
                "new_model_calls": 0,
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )


def build_study(configs: list[model_swap.ModelSwapConfig]) -> dict[str, Any]:
    if not PROTOCOL.exists():
        raise ValueError(f"frozen protocol missing: {PROTOCOL}")
    parity = model_swap.validate_same_core_configs(configs)
    if not parity["component_graph_identical"]:
        raise ValueError(f"configuration mismatch: {parity['mismatched_candidates']}")
    gold = load_letters()[:200]
    if len(gold) != 200:
        raise ValueError(f"expected full200 gold, got {len(gold)}")

    models: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="exectv2-confidence-") as temp:
        root = Path(temp)
        for config in configs:
            replay, producer_meta = _materialize_config(config, root / config.candidate_id)
            run = build_finding_assembly(
                replay.assembly,
                generated_on="2026-07-15",
                gold_loader=lambda _split: gold,
                diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
            )
            models[config.model_label] = _model_result(config, replay, run, gold, producer_meta)

    return {
        "schema_version": "exectv2_model_reported_confidence_out_of_sample_v1",
        "date": "2026-07-15",
        "protocol": PROTOCOL.as_posix(),
        "dataset": "ExECTv2",
        "development_split": "dev140",
        "evaluation_split": "test60",
        "split_sizes": {"dev140": 140, "test60": 60},
        "row_policy": "aggregate_only_no_test60_row_identifiers_text_predictions_or_failures",
        "source_output_revision": configs[0].replay_source_revision,
        "architecture_contract": "decision_0040_model_led",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "scorer": "exact family-cell clinical_headline correctness",
        "confidence_rule": (
            "least confident usable model-source mention; low < medium < high; otherwise missing"
        ),
        "repair_policy": (
            "fixed decision-0040 replay; source and final correctness reported separately"
        ),
        "review_policies": ["low_or_medium", "low_or_medium_or_missing"],
        "stop_rule": {
            "minimum_usable_coverage": 0.8,
            "minimum_failure_auroc": 0.65,
            "minimum_error_catch_rate": 0.5,
            "maximum_review_burden": 0.3,
            "all_required": True,
        },
        "models": models,
        "overall_decision": (
            "confidence_informative_for_at_least_one_named_saved_output"
            if any(model["test60_verdict"]["informative"] for model in models.values())
            else "negative_result_no_confidence_review_policy_adopted"
        ),
        "claim_boundary": (
            "Aggregate out-of-sample evidence for three saved historical model outputs. "
            "Not deployment calibration, independent clinical validation, a six-model "
            "conclusion, or evidence for the final DeepSeek V4 Flash runtime."
        ),
    }


def _model_result(
    config: model_swap.ModelSwapConfig,
    replay: model_swap.ModelSwapConfig,
    run: Any,
    gold: list[Any],
    producer_meta: dict[str, Any],
) -> dict[str, Any]:
    final_by_id = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in run.views["clinical_headline"].predictions
    }
    producer_rows = {
        producer_id: _read_jsonl(replay.assembly.producers[producer_id].artifact)
        for producer_id in set(SOURCE_PRODUCERS.values())
    }
    source_predictions = {
        producer_id: {
            prediction.letter_id: to_exect_letter(prediction)
            for prediction in predictions_from_rows(rows, "predicted_mentions")
        }
        for producer_id, rows in producer_rows.items()
    }
    raw_by_producer = {
        producer_id: {str(row["letter_id"]): row for row in rows}
        for producer_id, rows in producer_rows.items()
    }
    cells_by_split: dict[str, list[dict[str, Any]]] = {"dev140": [], "test60": []}
    for index, letter in enumerate(gold):
        split = "dev140" if index < 140 else "test60"
        for family in FAMILIES:
            producer_id = SOURCE_PRODUCERS[family]
            source_letter = source_predictions[producer_id][letter.letter_id]
            final_letter = final_by_id[letter.letter_id]
            raw_row = raw_by_producer[producer_id][letter.letter_id]
            source_keys = _keys(family, source_letter.annotations, letter.note_text)
            final_keys = _keys(family, final_letter.annotations, letter.note_text)
            gold_keys = _keys(family, letter.annotations, letter.note_text)
            cells_by_split[split].append(
                {
                    "family": family,
                    "confidence": confidence.cell_confidence(
                        raw_row.get("predicted_mentions", []), family
                    ),
                    "source_correct": source_keys == gold_keys,
                    "final_correct": final_keys == gold_keys,
                    "source_final_changed": source_keys != final_keys,
                }
            )

    splits = {}
    for split, cells in cells_by_split.items():
        splits[split] = {
            "overall": confidence.summarize_cells(cells),
            "by_family": {
                family: confidence.summarize_cells(
                    [cell for cell in cells if cell["family"] == family]
                )
                for family in FAMILIES
            },
        }
    return {
        "model": config.model,
        "runtime": config.runtime,
        "prompt_profile": config.prompt_profile,
        "temperature": config.temperature,
        "deepseek_thinking_state": "unrecorded"
        if "deepseek" in config.model.lower()
        else "not_applicable",
        "config_path": config.path.as_posix(),
        "producers": producer_meta,
        "events": _events(producer_rows),
        "splits": splits,
        "test60_verdict": confidence.verdict(splits["test60"]["overall"]),
    }


def _materialize_config(
    config: model_swap.ModelSwapConfig, destination: Path
) -> tuple[model_swap.ModelSwapConfig, dict[str, Any]]:
    destination.mkdir(parents=True, exist_ok=True)
    producers = {}
    metadata = {}
    for producer_id, producer in config.assembly.producers.items():
        result = subprocess.run(
            ["git", "show", f"{config.replay_source_revision}:{producer.artifact.as_posix()}"],
            check=True,
            capture_output=True,
        )
        target = destination / f"{producer_id}.jsonl"
        target.write_bytes(result.stdout)
        producers[producer_id] = replace(producer, artifact=target)
        rows = [
            json.loads(line) for line in result.stdout.decode("utf-8").splitlines() if line.strip()
        ]
        metadata[producer_id] = {
            "source_path": producer.artifact.as_posix(),
            "sha256": hashlib.sha256(result.stdout).hexdigest(),
            "rows": len(rows),
            "prompt_versions": sorted(
                {str(row.get("prompt_version") or "not_recorded") for row in rows}
            ),
            "models": sorted({str(row.get("model") or "not_recorded") for row in rows}),
        }
    replay = replace(config, assembly=replace(config.assembly, producers=producers))
    return replay, metadata


def _events(rows_by_producer: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    rows = [row for producer_rows in rows_by_producer.values() for row in producer_rows]
    return {
        "call_errors": sum(bool(row.get("call_error")) for row in rows),
        "parse_errors": sum(len(row.get("parse_errors") or []) for row in rows),
    }


def _keys(family: str, annotations: Any, note_text: str) -> Counter[Any]:
    selected = [annotation for annotation in annotations if annotation.entity == family]
    return Counter(clinical_headline_unit_keys(family, selected, note_text))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# ExECTv2 model-reported confidence out-of-sample result",
        "",
        "Date: 2026-07-15",
        "",
        "Status: completed aggregate-only negative-result study",
        "",
        "## Answer",
        "",
        "The saved model-reported confidence labels did not satisfy the frozen test60",
        "informativeness rule for any of the three historical models. No confidence-based",
        "review policy is adopted.",
        "",
        "## Aggregate test60 result",
        "",
        (
            "| Model | Usable coverage | Failure AUROC | Low/medium burden | "
            "Low/medium catch | Missing-inclusive burden | Missing-inclusive catch | Decision |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for label, model in payload["models"].items():
        summary = model["splits"]["test60"]["overall"]
        low_med, missing = summary["review_policies"]
        auroc = summary["failure_auroc_usable_labels"]
        lines.append(
            f"| {label} | {summary['usable_confidence_coverage']:.4f} | "
            f"{auroc if auroc is not None else 'N/A'} | {low_med['review_burden']:.4f} | "
            f"{low_med['catch_rate']:.4f} | {missing['review_burden']:.4f} | "
            f"{missing['catch_rate']:.4f} | {model['test60_verdict']['decision']} |"
        )
    lines.extend(
        [
            "",
            "The unit is one letter-family cell across Diagnosis, Seizure Frequency,",
            "Prescription, and Investigations. Confidence is the least-confident usable",
            "label among the model's source mentions. Missing labels remain a separate",
            "category. The primary outcome is exact final `clinical_headline` cell",
            "correctness after the fixed decision-0040 pipeline.",
            "",
            "## Family behavior",
            "",
            "| Model | Family | Coverage | AUROC | Errors |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for label, model in payload["models"].items():
        for family, summary in model["splits"]["test60"]["by_family"].items():
            auroc = summary["failure_auroc_usable_labels"]
            lines.append(
                f"| {label} | {family} | {summary['usable_confidence_coverage']:.4f} | "
                f"{auroc if auroc is not None else 'N/A'} | {summary['error_cells']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation and boundary",
            "",
            "This is a no-call replay of saved historical outputs. Dev140 and test60 are",
            "reported separately, and no test60 row identifier, text, prediction, or failure",
            "was emitted. The result concerns these saved outputs only. The historical",
            "DeepSeek runtime metadata is incomplete. This is not deployment calibration,",
            "independent clinical validation, a six-model conclusion, or evidence for a",
            "final DeepSeek V4 Flash runtime.",
            "",
            f"Protocol: `{payload['protocol']}`",
            "",
            "Machine-readable result:",
            "`experiments/exectv2_model_reported_confidence_out_of_sample_20260715.json`",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
