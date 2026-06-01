from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_io import (
    load_raw_outputs_by_source_index,
    write_jsonl_rows,
)


def test_write_jsonl_rows_writes_sorted_newline_delimited_json(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "rows.jsonl"

    write_jsonl_rows([{"b": 2, "a": 1}, {"c": 3}], path)

    assert path.read_text(encoding="utf-8").splitlines() == [
        '{"a": 1, "b": 2}',
        '{"c": 3}',
    ]


def test_load_raw_outputs_by_source_index_filters_to_reusable_rows(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    rows = [
        {"source_row_index": 10, "raw_output": "kept"},
        {"source_row_index": 11, "raw_output": ""},
        {"source_row_index": "12", "raw_output": "wrong index type"},
        {"source_row_index": 13, "raw_output": 7},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    assert load_raw_outputs_by_source_index(path) == {10: "kept"}


def test_load_raw_outputs_by_source_index_missing_file_returns_empty(
    tmp_path: Path,
) -> None:
    assert load_raw_outputs_by_source_index(tmp_path / "missing.jsonl") == {}
