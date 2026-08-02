from __future__ import annotations

from scripts import check_canonical_orchestrator_development_parity as parity


def test_compare_rows_reports_field_level_mismatches() -> None:
    result = parity._compare_rows(
        [{"source_row_index": 1, "prediction": "a", "evidence": "x"}],
        [{"source_row_index": 1, "prediction": "b", "evidence": "x"}],
        ("source_row_index", "prediction", "evidence"),
    )

    assert result["passed"] is False
    assert result["mismatches_by_field"] == {"prediction": 1}
    assert result["first_mismatch_ids"] == ["1"]


def test_artifact_comparison_ignores_only_source_commit() -> None:
    expected = {"source_commit": "generation", "result": "pass"}
    actual = {"source_commit": "containing-commit", "result": "pass"}

    assert parity._matches(expected, actual)
