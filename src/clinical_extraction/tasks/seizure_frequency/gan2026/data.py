from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_DATA_PATH = Path("data/Gan (2026)/synthetic_data_subset_1500.json")


@dataclass(frozen=True)
class GanRecord:
    source_row_index: int
    note_text: str
    raw: dict[str, Any]


def load_records(path: Path = DEFAULT_DATA_PATH) -> list[GanRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records: list[GanRecord] = []
    for row in data:
        records.append(
            GanRecord(
                source_row_index=int(row["source_row_index"]),
                note_text=str(row["clinic_date"]),
                raw=row,
            )
        )
    return records

