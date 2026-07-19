from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.trace_explorer.index import TraceIndex, build_index

FIXTURE = (
    Path("src")
    / "clinical_extraction"
    / "trace_explorer"
    / "fixtures"
    / "syn_014.json"
)


def test_build_index_keeps_source_text_out_of_sqlite_and_locked_rows_out_of_records(
    tmp_path: Path,
) -> None:
    output = tmp_path / ".trace_explorer"

    manifest = build_index(
        artifacts=[FIXTURE],
        output=output,
        approved_roots=[Path.cwd()],
    )

    assert manifest.schema_version == "trace-index.v1"
    assert manifest.run_count == 3
    assert manifest.trace_count == 2
    assert (output / "index.sqlite3").is_file()
    assert (output / "build-manifest.json").is_file()
    assert b"lamotrigine 150 mg twice daily" not in (output / "index.sqlite3").read_bytes()

    index = TraceIndex(output)
    assert index.list_record_ids("syn-exect-014") == ["SYN-014"]
    assert index.list_record_ids("syn-aggregate-only") == []

    trace = index.get_trace(run_id="syn-exect-014", source_id="SYN-014")
    assert trace is not None
    assert "lamotrigine 150 mg twice daily" in trace.source.text


def test_index_build_rejects_traversal_or_unapproved_artifacts(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"schema_version": "illustrative.fixture.v1"}), encoding="utf-8")

    with pytest.raises(ValueError, match="approved root"):
        build_index(
            artifacts=[outside],
            output=tmp_path / "index",
            approved_roots=[Path.cwd()],
        )


def test_failed_rebuild_leaves_the_previous_index_readable(tmp_path: Path) -> None:
    output = tmp_path / ".trace_explorer"
    build_index(artifacts=[FIXTURE], output=output, approved_roots=[Path.cwd()])
    original = (output / "index.sqlite3").read_bytes()
    broken = tmp_path / "broken.json"
    broken.write_text('{"schema_version": "unknown"}', encoding="utf-8")

    with pytest.raises(ValueError, match="unknown schema"):
        build_index(
            artifacts=[broken],
            output=output,
            approved_roots=[tmp_path],
        )

    assert (output / "index.sqlite3").read_bytes() == original
    assert TraceIndex(output).list_record_ids("syn-exect-014") == ["SYN-014"]
