"""Gan record loading and construction for Observatory routes."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException

from clinical_extraction.observatory.models import ObservatorySettings, RunNoteRequest
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_for_split,
)


def request_record(request: RunNoteRequest) -> GanRecord:
    gold_label = request.gold_label.strip() or "unknown"
    try:
        gold_record = label_to_frequency_record(gold_label)
    except ValueError:
        gold_record = label_to_frequency_record("unknown")
    return GanRecord(
        source_row_index=request.source_row_index,
        note_text=request.note_text,
        gold_label=gold_record.normalized_label,
        gold_reference=request.gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={"source": "observatory_run_note"},
    )


def load_split_records(settings: ObservatorySettings, split: str) -> Sequence[Any]:
    try:
        return load_records_for_split(
            split,
            data_path=settings.data_path,
            manifest_path=settings.split_manifest_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
