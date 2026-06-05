from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h10_raw_identity_sidecar,
)


def test_h10_sidecar_summarizes_artifact_and_pair_identity(tmp_path: Path) -> None:
    left_path = tmp_path / "left.jsonl"
    right_path = tmp_path / "right.jsonl"
    _write_jsonl(
        left_path,
        [
            {
                "source_row_index": 1,
                "raw_output": "same",
                "llm_candidate_raw_output": "left-different",
                "reused_raw_output": True,
                "prompt_version": "v1",
                "score_layers": {"raw": {}, "final": {}},
            },
            {"source_row_index": 2, "raw_output": "same-2"},
        ],
    )
    _write_jsonl(
        right_path,
        [
            {
                "source_row_index": 1,
                "raw_output": "same",
                "llm_candidate_raw_output": "right-different",
                "reused_raw_output": False,
                "prompt_version": "v1",
                "score_layers": {"raw": {}},
            },
            {"source_row_index": 2, "raw_output": "same-2"},
        ],
    )

    artifact = h10_raw_identity_sidecar.build_h10_raw_identity_sidecar(
        artifact_paths=[left_path],
        pair_left_path=left_path,
        pair_right_path=right_path,
    )

    assert artifact["decision"] == "raw_identity_sidecar_ready"
    assert artifact["artifact_summaries"][0]["row_count"] == 2
    assert artifact["artifact_summaries"][0]["source_row_count"] == 2
    assert artifact["artifact_summaries"][0]["raw_field_present_counts"]["raw_output"] == 2
    assert artifact["artifact_summaries"][0]["reuse_flag_counts"] == {
        "reused_raw_output=True": 1
    }
    assert artifact["paired_identity"]["matched_rows"] == 2
    assert artifact["paired_identity"]["raw_field_identity"]["raw_output"] == {
        "present_pairs": 2,
        "identical_pairs": 2,
        "identity_rate": 1.0,
    }
    assert artifact["paired_identity"]["raw_field_identity"]["llm_candidate_raw_output"] == {
        "present_pairs": 1,
        "identical_pairs": 0,
        "identity_rate": 0.0,
    }


def test_h10_sidecar_writes_outputs(tmp_path: Path) -> None:
    left_path = tmp_path / "left.jsonl"
    right_path = tmp_path / "right.jsonl"
    json_path = tmp_path / "sidecar.json"
    report_path = tmp_path / "sidecar.md"
    _write_jsonl(left_path, [{"source_row_index": 1, "raw_output": "same"}])
    _write_jsonl(right_path, [{"source_row_index": 1, "raw_output": "same"}])

    artifact = h10_raw_identity_sidecar.materialize_h10_raw_identity_sidecar(
        artifact_paths=[left_path],
        pair_left_path=left_path,
        pair_right_path=right_path,
        output_json_path=json_path,
        output_report_path=report_path,
    )

    assert artifact["json_artifact"] == str(json_path)
    assert json.loads(json_path.read_text())["decision"] == "raw_identity_sidecar_ready"
    assert "H10 Raw Identity Sidecar" in report_path.read_text()


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
