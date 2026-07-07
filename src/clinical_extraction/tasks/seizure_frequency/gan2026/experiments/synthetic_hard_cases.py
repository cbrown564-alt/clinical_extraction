"""Shared loader and record conversion helpers for synthetic hard cases."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

SYNTHETIC_SOURCE_INDEX_BASE = 900_000
SYNTHETIC_SPLIT_NAME = "synthetic_hard_cases"
SYNTHETIC_SPLIT_MANIFEST = "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01"


def load_synthetic_hard_cases(path: Path) -> list[dict[str, Any]]:
    """Load reviewed synthetic hard-case rows from JSONL."""

    return load_jsonl_rows(path)


def synthetic_records_from_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    source_index_base: int = SYNTHETIC_SOURCE_INDEX_BASE,
) -> list[GanFrequencyRecord]:
    """Convert reviewed hard cases into scored Gan-like records."""

    records = []
    for offset, case in enumerate(cases):
        label_record = label_to_frequency_record(str(case["expected_final_label"]))
        records.append(
            GanFrequencyRecord(
                source_row_index=source_index_base + offset,
                note_text=str(case["source_note_text"]),
                gold_label=str(case["expected_final_label"]),
                gold_reference=str(case["expected_evidence_substring"]),
                labels_match_all_categories=True,
                quotes_ok_all_categories=True,
                row_ok=True,
                raw=dict(case),
                gold_normalized_label=label_record.normalized_label,
                gold_label_kind=label_record.kind,
                gold_yearly_bounds=label_record.yearly_bounds,
                gold_monthly_frequency=label_record.monthly_frequency,
            )
        )
    return records


def attach_hard_case_metadata(
    rows: Sequence[dict[str, Any]],
    cases: Sequence[Mapping[str, Any]],
    *,
    source_index_base: int = SYNTHETIC_SOURCE_INDEX_BASE,
) -> list[dict[str, Any]]:
    """Attach case ids/families to saved hybrid rows without exposing gold in prompts."""

    case_by_index = {source_index_base + offset: case for offset, case in enumerate(cases)}
    enriched = []
    for row in rows:
        row_copy = dict(row)
        case = case_by_index.get(int(row["source_row_index"]))
        if case is not None:
            row_copy["hard_case"] = {
                "case_id": case["case_id"],
                "failure_family": case["failure_family"],
                "expected_answer_kind": case["expected_answer_kind"],
                "allowed_llm_action": case["allowed_llm_action"],
                "deterministic_failure_rationale": case["deterministic_failure_rationale"],
            }
        enriched.append(row_copy)
    return enriched
