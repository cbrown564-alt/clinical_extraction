#!/usr/bin/env python3
"""Phase E gates and stage stops for the Gan rules-only three-stage program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_phase_e_protocol_2026-08-30.md
Development split only; test450 is never loaded; zero model calls.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_extraction import (  # noqa: E501
    extract_wide_candidates,
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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/gan2026_rules_only_three_stage_phase_e_20260830"
EXPECTED_DEFAULT_SELECT = 669
EXPECTED_PHASE_C_SELECT = 691
STOPS = ("find", "encode", "select")


def main() -> None:
    records = sorted(
        load_records_for_split(gan_machine_split("dev750")),
        key=lambda record: record.source_row_index,
    )
    if len(records) != 750:
        raise RuntimeError(f"expected 750 development records, found {len(records)}")

    comparator_config = PipelineConfiguration(architecture="rules")
    promoted = phase_c_candidate_config()
    default_correct = {stop: 0 for stop in STOPS}
    promoted_correct = {stop: 0 for stop in STOPS}
    drop_counts: Counter[str] = Counter()
    anonymous = 0
    find_encode_disagree = 0

    for record in records:
        comparator = gan_rules.run_record(record, comparator_config)
        default = run_record_three_stage(record)
        candidate = run_record_three_stage(record, promoted)

        if default.stops.select_label != comparator.output.final_value:
            raise RuntimeError(
                "gate E1 failed: default select label diverges on "
                f"source_row_index={record.source_row_index}"
            )
        if default.final_selection.evidence != comparator.output.evidence:
            raise RuntimeError(
                "gate E1 failed: default select evidence diverges on "
                f"source_row_index={record.source_row_index}"
            )

        for entry in default.ledger:
            if entry.drop_reason is not None:
                drop_counts[str(entry.drop_reason)] += 1
        for candidate_row in extract_wide_candidates(record.note_text):
            if candidate_row.rule_id == "unknown":
                anonymous += 1

        for stop, label in (
            ("find", default.stops.find_label),
            ("encode", default.stops.encode_label),
            ("select", default.stops.select_label),
        ):
            if score_label(record, label)["purist_correct"]:
                default_correct[stop] += 1
        for stop, label in (
            ("find", candidate.stops.find_label),
            ("encode", candidate.stops.encode_label),
            ("select", candidate.stops.select_label),
        ):
            if score_label(record, label)["purist_correct"]:
                promoted_correct[stop] += 1
        if default.stops.find_label != default.stops.encode_label:
            find_encode_disagree += 1

    if default_correct["select"] != EXPECTED_DEFAULT_SELECT:
        raise RuntimeError(
            "gate E1 failed: default select "
            f"{default_correct['select']}/750 != {EXPECTED_DEFAULT_SELECT}"
        )
    if promoted_correct["select"] != EXPECTED_PHASE_C_SELECT:
        raise RuntimeError(
            "gate E1 failed: promoted select "
            f"{promoted_correct['select']}/750 != {EXPECTED_PHASE_C_SELECT}"
        )
    if anonymous:
        raise RuntimeError(f"gate E3 failed: {anonymous} anonymous wide-ledger rows")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": (
            "docs/research/gan2026/gan_rules_only_three_stage_phase_e_protocol_2026-08-30.md"
        ),
        "holdout_loaded": False,
        "model_calls": 0,
        "row_policy": "development_review_permitted",
        "gates": {
            "e1_default_select_identical_to_run_record": True,
            "e1_promoted_select_reproduces_691": True,
            "e3_anonymous_wide_ledger": 0,
        },
        "default_stops": {
            stop: {"correct": default_correct[stop], "n": 750}
            for stop in STOPS
        },
        "promoted_stops": {
            stop: {"correct": promoted_correct[stop], "n": 750}
            for stop in STOPS
        },
        "find_encode_label_disagree": find_encode_disagree,
        "drop_counts": dict(drop_counts),
        "claim_boundary": (
            "Development instrumentation. Cited five-cell stops stay "
            "292/292/325 until a later aggregate-only replay."
        ),
    }
    (OUT_DIR / "dev750_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
