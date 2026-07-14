from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)


def test_write_jsonl_rows_writes_sorted_newline_delimited_json(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "rows.jsonl"

    write_jsonl_rows([{"b": 2, "a": 1}, {"c": 3}], path)

    assert path.read_text(encoding="utf-8").splitlines() == [
        '{"a": 1, "b": 2}',
        '{"c": 3}',
    ]


def test_load_jsonl_rows_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(
        json.dumps({"source_row_index": 1}) + "\n\n" + json.dumps({"source_row_index": 2}) + "\n",
        encoding="utf-8",
    )

    assert load_jsonl_rows(path) == [{"source_row_index": 1}, {"source_row_index": 2}]
