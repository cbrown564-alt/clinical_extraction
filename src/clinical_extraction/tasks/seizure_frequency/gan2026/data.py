from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
    label_to_frequency_record,
)

DEFAULT_DATA_PATH = Path("data/Gan (2026)/synthetic_data_subset_1500.json")
SEIZURE_FREQUENCY_KEY = "check__Seizure Frequency Number"


@dataclass(frozen=True)
class GanRecord:
    source_row_index: int
    note_text: str
    gold_label: str
    gold_reference: str
    labels_match_all_categories: bool
    quotes_ok_all_categories: bool
    row_ok: bool
    raw: dict[str, Any]


@dataclass(frozen=True)
class GanFrequencyRecord(GanRecord):
    gold_normalized_label: str
    gold_label_kind: FrequencyLabelKind
    gold_yearly_bounds: tuple[float, float] | None
    gold_monthly_frequency: float


def load_records(path: Path = DEFAULT_DATA_PATH) -> list[GanRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records: list[GanRecord] = []
    for row in data:
        frequency_check = row[SEIZURE_FREQUENCY_KEY]
        records.append(
            GanRecord(
                source_row_index=int(row["source_row_index"]),
                note_text=str(row["clinic_date"]),
                gold_label=_first_value(frequency_check["seizure_frequency_number"]),
                gold_reference=_last_value(frequency_check["reference"]),
                labels_match_all_categories=bool(row["labels_match_all_categories"]),
                quotes_ok_all_categories=bool(row["quotes_ok_all_categories"]),
                row_ok=bool(row["row_ok"]),
                raw=row,
            )
        )
    return records


def load_records_with_monthly_frequency(path: Path = DEFAULT_DATA_PATH) -> list[GanFrequencyRecord]:
    records = []
    for record in load_records(path):
        frequency_record = label_to_frequency_record(record.gold_label)
        records.append(
            GanFrequencyRecord(
                source_row_index=record.source_row_index,
                note_text=record.note_text,
                gold_label=record.gold_label,
                gold_reference=record.gold_reference,
                labels_match_all_categories=record.labels_match_all_categories,
                quotes_ok_all_categories=record.quotes_ok_all_categories,
                row_ok=record.row_ok,
                raw=record.raw,
                gold_normalized_label=frequency_record.normalized_label,
                gold_label_kind=frequency_record.kind,
                gold_yearly_bounds=frequency_record.yearly_bounds,
                gold_monthly_frequency=frequency_record.monthly_frequency,
            )
        )
    return records


def _first_value(value: str | list[str]) -> str:
    if isinstance(value, list):
        return str(value[0])
    return str(value)


def _last_value(value: str | list[str]) -> str:
    if isinstance(value, list):
        return str(value[-1])
    return str(value)
