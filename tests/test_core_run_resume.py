"""Tests for core.run_resume — the foundational runner resume helpers."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)


def _write(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )


def test_read_completed_missing_file_is_empty() -> None:
    rows, done = read_completed(Path("does_not_exist.jsonl"))
    assert rows == []
    assert done == set()


def test_read_completed_none_path_is_empty() -> None:
    rows, done = read_completed(None)
    assert rows == [] and done == set()


def test_read_completed_loads_rows_and_keys(tmp_path: Path) -> None:
    p = tmp_path / "ckpt.jsonl"
    _write(p, [{"letter_id": "A", "x": 1}, {"letter_id": "B", "x": 2}])
    rows, done = read_completed(p)
    assert len(rows) == 2
    assert done == {"A", "B"}


def test_read_completed_ignores_blank_lines_and_keyless_rows(tmp_path: Path) -> None:
    p = tmp_path / "ckpt.jsonl"
    p.write_text(
        json.dumps({"letter_id": "A"}) + "\n\n" + json.dumps({"no_key": 1}) + "\n",
        encoding="utf-8",
    )
    rows, done = read_completed(p)
    assert len(rows) == 2  # both rows kept
    assert done == {"A"}  # only the keyed one counts as completed


def test_pending_items_filters_completed() -> None:
    items = ["A", "B", "C", "D"]
    pending = pending_items(items, {"A", "C"}, key_of=lambda s: s)
    assert pending == ["B", "D"]


def test_merge_rows_dedup_and_reorder() -> None:
    existing = [{"letter_id": "A", "v": "old"}, {"letter_id": "B", "v": "x"}]
    new = [{"letter_id": "A", "v": "new"}, {"letter_id": "C", "v": "y"}]
    merged = merge_rows(existing + new, order=["A", "B", "C"])
    assert [r["letter_id"] for r in merged] == ["A", "B", "C"]
    # Last write wins for duplicate keys.
    assert merged[0]["v"] == "new"


def test_merge_rows_appends_unordered_and_keyless() -> None:
    rows = [
        {"letter_id": "B", "v": 1},
        {"letter_id": "Z", "v": 2},  # not in order → appended
        {"no_key": True},  # keyless → appended last
    ]
    merged = merge_rows(rows, order=["A", "B"])
    ids = [r.get("letter_id") for r in merged]
    assert ids[0] == "B"  # ordered first
    assert "Z" in ids  # extra key preserved
    assert merged[-1] == {"no_key": True}  # keyless preserved at end
