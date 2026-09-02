#!/usr/bin/env python3
"""Aggregate-only test450 replay of frozen phase_c_candidate_config().

Protocol:
docs/research/gan2026/gan_rules_only_three_stage_phase_d_protocol_2026-08-29.md
Gate A (dev750 parity) must pass before running this script.
Do not inspect or quote holdout rows from the sealed output.
Per-class holdout deltas are never computed.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split, gan_row_count
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (
    phase_c_candidate_config,
    run_record_three_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from scripts.measure_gan_rules_only_select_keeps_dev750 import build_arms

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/gan2026/"
    "gan_rules_only_three_stage_phase_d_protocol_2026-08-29.md"
)
OUT_JSON = (
    ROOT
    / "experiments/gan_rules_only_three_stage_phase_d_test450_aggregate_20260829.json"
)
SEALED_ROOT = (
    ROOT / "scratch/holdout/gan_rules_only_three_stage_test450_20260829"
)
CITED_SELECT_CORRECT = 321
SPLIT = "test450"
PUBLIC_FORBIDDEN_KEYS = {
    "by_class",
    "classification_report",
    "diagnostics",
    "final_label",
    "gold_label",
    "letter_id",
    "letters",
    "note_text",
    "per_class_deltas",
    "predictions",
    "reference",
    "rows",
    "source_row_index",
    "source_row_indices",
    "traces",
}


def phase_d_verdict(candidate_correct: int, comparator_correct: int) -> str:
    """Return the predeclared Phase D verdict. Binding before the run."""

    if comparator_correct != CITED_SELECT_CORRECT:
        return "blocked_by_comparator_drift"
    if candidate_correct > CITED_SELECT_CORRECT:
        return "promotion_accepted"
    return "disappointing_development_only"


def assert_public_payload_aggregate_only(payload: dict[str, Any]) -> None:
    leaked = sorted(PUBLIC_FORBIDDEN_KEYS.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")
    nested = _nested_forbidden_keys(payload)
    if nested:
        raise ValueError(f"public payload contains nested forbidden keys: {nested}")


def _nested_forbidden_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in PUBLIC_FORBIDDEN_KEYS or (
                str(key) == "rows" and isinstance(item, (dict, list))
            ):
                found.append(path)
            found.extend(_nested_forbidden_keys(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_nested_forbidden_keys(item, f"{prefix}[{index}]"))
    return found


def _assert_frozen_config() -> None:
    config = phase_c_candidate_config()
    kept, overrides = build_arms()["phase_c_candidate"]
    if config.kept_classes != kept or config.select_overrides != overrides:
        raise RuntimeError(
            "phase_c_candidate_config() does not match the Phase C keep-arm union"
        )


def _git_note() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return "dirty" if result.stdout.strip() else "clean"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_sealed(rows: list[dict[str, Any]]) -> Path:
    SEALED_ROOT.mkdir(parents=True, exist_ok=True)
    path = SEALED_ROOT / "rows.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def main() -> None:
    _assert_frozen_config()
    expected_n = gan_row_count(SPLIT)
    records = load_records_for_split(gan_machine_split(SPLIT))
    if len(records) != expected_n:
        raise RuntimeError(
            f"expected {expected_n} {SPLIT} records, found {len(records)}"
        )

    comparator_config = PipelineConfiguration(architecture="rules")
    candidate_config = phase_c_candidate_config()
    sealed_rows: list[dict[str, Any]] = []
    comparator_correct = 0
    candidate_correct = 0
    candidate_stop_correct = {"find": 0, "encode": 0, "select": 0}

    for record in records:
        comparator = gan_rules.run_record(record, comparator_config)
        candidate = run_record_three_stage(record, candidate_config)
        comparator_label = comparator.output.final_value
        if score_label(record, comparator_label)["purist_correct"]:
            comparator_correct += 1
        stop_labels = {
            "find": candidate.stops.find_label,
            "encode": candidate.stops.encode_label,
            "select": candidate.stops.select_label,
        }
        if score_label(record, stop_labels["select"])["purist_correct"]:
            candidate_correct += 1
        for stop, label in stop_labels.items():
            if score_label(record, label)["purist_correct"]:
                candidate_stop_correct[stop] += 1
        sealed_rows.append(
            {
                "source_row_index": record.source_row_index,
                "comparator_label": comparator_label,
                "candidate_find_label": stop_labels["find"],
                "candidate_encode_label": stop_labels["encode"],
                "candidate_select_label": stop_labels["select"],
            }
        )

    if candidate_correct != candidate_stop_correct["select"]:
        raise RuntimeError("select-stop tally drifted from the primary count")

    verdict = phase_d_verdict(candidate_correct, comparator_correct)
    sealed_path = _write_sealed(sealed_rows)
    payload: dict[str, Any] = {
        "schema_version": "gan.rules_only.three_stage.phase_d.test450.v1",
        "protocol": PROTOCOL,
        "generated_on": datetime.now(UTC).date().isoformat(),
        "dirty_tree": _git_note(),
        "split": SPLIT,
        "split_loader": gan_machine_split(SPLIT),
        "row_count": expected_n,
        "row_policy": "aggregate_only",
        "holdout_loaded": True,
        "model_calls": 0,
        "scorer": "purist",
        "candidate_config": "phase_c_candidate_config",
        "comparator": "run_record(architecture=rules), cited test450 321/450",
        "cited_select_purist_correct": CITED_SELECT_CORRECT,
        "comparator_select_purist_correct": comparator_correct,
        "candidate_select_purist_correct": candidate_correct,
        "candidate_select_purist_accuracy": round(candidate_correct / expected_n, 4),
        "delta_vs_cited": candidate_correct - CITED_SELECT_CORRECT,
        "verdict": verdict,
        "history_flagged_keeps": [
            {
                "keep": "keep_nightly_narrative_rate",
                "flag": "G1 Candidate A; prior test450 aggregate -1",
            },
            {
                "keep": "keep_non_epileptic_current_free",
                "flag": "G2 Candidate B; prior holdout inert",
            },
        ],
        "sealed_predictions": {
            "local_path": sealed_path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(sealed_path),
            "bytes": sealed_path.stat().st_size,
            "note": (
                "Sealed under scratch/holdout; not for row inspection "
                "or public copy."
            ),
        },
        "claim_boundary": (
            "Aggregate-only holdout replay of phase_c_candidate_config(). "
            "One Purist select-stop number versus cited 321/450. Per-class "
            "holdout deltas were never computed. Not clinical validation."
        ),
    }
    if verdict == "promotion_accepted":
        payload["candidate_stage_stops"] = {
            stop: {
                "purist_correct": count,
                "accuracy": round(count / expected_n, 4),
            }
            for stop, count in candidate_stop_correct.items()
        }
    assert_public_payload_aggregate_only(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(OUT_JSON)
    print(
        f"comparator select: {comparator_correct}/{expected_n}"
    )
    print(
        f"candidate select: {candidate_correct}/{expected_n} "
        f"({payload['candidate_select_purist_accuracy']:.4f})"
    )
    print(f"verdict: {verdict}")
    if verdict == "promotion_accepted":
        stops = payload["candidate_stage_stops"]
        print(
            "candidate stage stops: "
            f"find {stops['find']['purist_correct']}/{expected_n} "
            f"encode {stops['encode']['purist_correct']}/{expected_n} "
            f"select {stops['select']['purist_correct']}/{expected_n}"
        )


if __name__ == "__main__":
    main()
