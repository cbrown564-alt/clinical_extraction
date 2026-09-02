#!/usr/bin/env python3
"""Score atomic, codebook, and living source-near rules find on the same pick.

Living ``find_label`` is the source-near dialect. Atomic tags are
read from the ledger. Codebook projection is bundled find-and-encode.

Protocol: docs/research/gan2026/gan_rules_find_llm_dialects_protocol_2026-08-31.md
Development split only; test450 is never loaded; zero model calls.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split
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

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/gan2026_rules_find_llm_dialects_20260831"
EXPECTED_DEFAULT_SELECT = 669
EXPECTED_PHASE_C_SELECT = 691
FIND_DIALECTS = ("atomic", "gan_llm_extract", "gan_llm_extract_raw")


def main() -> None:
    records = sorted(
        load_records_for_split(gan_machine_split("dev750")),
        key=lambda record: record.source_row_index,
    )
    if len(records) != 750:
        raise RuntimeError(f"expected 750 development records, found {len(records)}")

    comparator_config = PipelineConfiguration(architecture="rules")
    promoted = phase_c_candidate_config()
    default_counts = {
        "atomic": 0,
        "gan_llm_extract": 0,
        "gan_llm_extract_raw": 0,
        "encode": 0,
        "select": 0,
    }
    promoted_counts = dict(default_counts)
    codebook_encode_disagree = 0

    for record in records:
        comparator = gan_rules.run_record(record, comparator_config)
        default = run_record_three_stage(record)
        candidate = run_record_three_stage(record, promoted)
        if default.stops.select_label != comparator.output.final_value:
            raise RuntimeError(
                "gate D3 failed: default select label diverges on "
                f"source_row_index={record.source_row_index}"
            )
        if default.stops.find_extract_label != default.stops.encode_label:
            codebook_encode_disagree += 1
        for stop, label in (
            (
                "atomic",
                default.ledger[default.stops.find_pick_ledger_index].find_tag
                if default.stops.find_pick_ledger_index is not None
                else default.stops.find_label,
            ),
            ("gan_llm_extract", default.stops.find_extract_label),
            ("gan_llm_extract_raw", default.stops.find_label),
            ("encode", default.stops.encode_label),
            ("select", default.stops.select_label),
        ):
            if score_label(record, label)["purist_correct"]:
                default_counts[stop] += 1
        for stop, label in (
            (
                "atomic",
                candidate.ledger[candidate.stops.find_pick_ledger_index].find_tag
                if candidate.stops.find_pick_ledger_index is not None
                else candidate.stops.find_label,
            ),
            ("gan_llm_extract", candidate.stops.find_extract_label),
            ("gan_llm_extract_raw", candidate.stops.find_label),
            ("encode", candidate.stops.encode_label),
            ("select", candidate.stops.select_label),
        ):
            if score_label(record, label)["purist_correct"]:
                promoted_counts[stop] += 1

    if default_counts["select"] != EXPECTED_DEFAULT_SELECT:
        raise RuntimeError(
            "gate D3 failed: default select "
            f"{default_counts['select']}/750 != {EXPECTED_DEFAULT_SELECT}"
        )
    if promoted_counts["select"] != EXPECTED_PHASE_C_SELECT:
        raise RuntimeError(
            "gate D3 failed: promoted select "
            f"{promoted_counts['select']}/750 != {EXPECTED_PHASE_C_SELECT}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": (
            "docs/research/gan2026/gan_rules_find_llm_dialects_protocol_2026-08-31.md"
        ),
        "holdout_loaded": False,
        "model_calls": 0,
        "row_policy": "development_review_permitted",
        "find_dialects": list(FIND_DIALECTS),
        "default_stops": {
            name: {"correct": default_counts[name], "n": 750}
            for name in (*FIND_DIALECTS, "encode", "select")
        },
        "promoted_stops": {
            name: {"correct": promoted_counts[name], "n": 750}
            for name in (*FIND_DIALECTS, "encode", "select")
        },
        "codebook_find_encode_label_disagree": codebook_encode_disagree,
        "gates": {
            "d3_default_select_identical_to_run_record": True,
            "d3_promoted_select_reproduces_691": True,
        },
        "claim_boundary": (
            "Development instrumentation. Cited five-cell stops stay "
            "292/292/325. Living rules find is source-near "
            "(gan_llm_extract_raw). gan_llm_extract is bundled "
            "find-and-encode."
        ),
    }
    (OUT_DIR / "dev750_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
