#!/usr/bin/env python3
"""Aggregate-only test450 remasure of living source-near rules find.

Protocol:
docs/research/gan2026/gan_rules_source_near_find_test450_protocol_2026-08-31.md
Do not inspect or quote holdout rows. Public output is stop counts only.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split, gan_row_count
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (
    phase_c_candidate_config,
    run_record_three_stage,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/gan2026/gan_rules_source_near_find_test450_protocol_2026-08-31.md"
)
OUT_JSON = ROOT / "docs/research/gan2026/gan_rules_source_near_find_test450_2026-08-31.json"
SPLIT = "test450"
EXPECTED_SELECT = 325
EXPECTED_ENCODE = 292
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


def assert_public_payload_aggregate_only(payload: dict[str, Any]) -> None:
    leaked = sorted(PUBLIC_FORBIDDEN_KEYS.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")


def main() -> None:
    expected_n = gan_row_count(SPLIT)
    records = load_records_for_split(gan_machine_split(SPLIT))
    if len(records) != expected_n:
        raise RuntimeError(
            f"expected {expected_n} {SPLIT} records, found {len(records)}"
        )

    config = phase_c_candidate_config()
    correct = {"find": 0, "encode": 0, "select": 0}
    for record in records:
        result = run_record_three_stage(record, config)
        for stop, label in (
            ("find", result.stops.find_label),
            ("encode", result.stops.encode_label),
            ("select", result.stops.select_label),
        ):
            if score_label(record, label)["purist_correct"]:
                correct[stop] += 1

    if correct["select"] != EXPECTED_SELECT:
        raise RuntimeError(
            "select drifted from cited 325/450: "
            f"{correct['select']}/{expected_n}"
        )

    payload: dict[str, Any] = {
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": PROTOCOL,
        "split": SPLIT,
        "row_count": expected_n,
        "row_policy": "aggregate_only",
        "holdout_loaded": True,
        "model_calls": 0,
        "scorer": "purist",
        "candidate_config": "phase_c_candidate_config",
        "find_dialect": "gan_llm_extract_raw",
        "stops": {
            stop: {
                "purist_correct": correct[stop],
                "n": expected_n,
                "accuracy": round(correct[stop] / expected_n, 4),
            }
            for stop in ("find", "encode", "select")
        },
        "gates": {
            "select_reproduces_325": correct["select"] == EXPECTED_SELECT,
            "encode_reproduces_292": correct["encode"] == EXPECTED_ENCODE,
        },
        "supersedes_fused_find_purist_correct": 292,
        "claim_boundary": (
            "Aggregate-only remasure of living source-near rules find. "
            "Select stays 325/450. Do not inspect holdout rows."
        ),
    }
    assert_public_payload_aggregate_only(payload)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
