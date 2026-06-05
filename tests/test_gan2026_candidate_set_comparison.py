from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_set_comparison,
)


def test_candidate_set_comparison_counts_overlap_and_union() -> None:
    deterministic = [
        _row(1, compatible=True, kinds=["frequency_rate"]),
        _row(2, compatible=False, kinds=[]),
        _row(3, compatible=True, kinds=["seizure_free"]),
        _row(4, compatible=False, kinds=[]),
    ]
    llm = [
        _row(1, compatible=True, kinds=["frequency_rate"]),
        _row(2, compatible=True, kinds=["unknown_frequency"]),
        _row(3, compatible=False, kinds=[]),
        _row(4, compatible=False, kinds=[]),
    ]

    rows, metadata = candidate_set_comparison.build_candidate_set_comparison(
        deterministic,
        llm,
    )

    assert metadata["summary"]["both_compatible_rows"] == 1
    assert metadata["summary"]["llm_only_rows"] == 1
    assert metadata["summary"]["deterministic_only_rows"] == 1
    assert metadata["summary"]["neither_rows"] == 1
    assert metadata["summary"]["union_compatible_rows"] == 3
    assert rows[1]["union_compatible"] is True


def _row(source_row_index: int, *, compatible: bool, kinds: list[str]) -> dict:
    return {
        "source_row_index": source_row_index,
        "gold_label": "unknown",
        "gold_candidate_kind": "unknown_frequency",
        "compatible_candidate_present": compatible,
        "candidate_count": len(kinds),
        "candidate_kinds_present": kinds,
        "candidate_set_status": "present",
        "diagnostic_issues": [],
        "note_excerpt": "Example note.",
    }
