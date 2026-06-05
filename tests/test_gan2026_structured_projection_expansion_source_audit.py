from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_projection_expansion_source_audit,
)


def test_expansion_source_audit_counts_novel_clean_w_to_c_rows() -> None:
    current_rows = [
        _extractor_row(1, "W_to_C", prediction_bearing=True),
        _extractor_row(2, "not_selected", prediction_bearing=False),
    ]
    candidate_rows = [
        _direct_row(1, "W_to_C"),
        _direct_row(3, "W_to_C"),
        _direct_row(4, "C_to_W"),
        _direct_row(5, "C_to_C"),
    ]

    audit_rows = structured_projection_expansion_source_audit.build_audit_rows(
        current_rows,
        candidate_rows,
    )
    summary = structured_projection_expansion_source_audit.summarize_audit_rows(
        audit_rows,
        current_rows,
    )

    assert summary["current_w_to_c_rows"] == 1
    assert summary["candidate_clean_w_to_c_rows"] == 2
    assert summary["candidate_clean_c_to_w_rows"] == 1
    assert summary["novel_clean_w_to_c_rows"] == 1
    assert summary["safe_to_broaden_from_candidate_source"] is False
    assert summary["decision"] == "direct_labeler_source_rejected_for_broadening"


def test_expansion_source_audit_filters_unclean_candidate_rows() -> None:
    rows = structured_projection_expansion_source_audit.build_audit_rows(
        [],
        [
            _direct_row(1, "W_to_C", exact_evidence=False),
            _direct_row(2, "W_to_C", parse_ok=False),
            _direct_row(3, "W_to_C", issues=["parse_not_ok"]),
        ],
    )
    summary = structured_projection_expansion_source_audit.summarize_audit_rows(
        rows,
        [],
    )

    assert summary["candidate_clean_prediction_bearing_rows"] == 0
    assert summary["novel_clean_w_to_c_rows"] == 0
    assert summary["candidate_unclean_rows"] == 3


def _extractor_row(
    source_row_index: int,
    transition: str,
    *,
    prediction_bearing: bool,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "prediction_bearing": prediction_bearing,
        "transition": transition,
    }


def _direct_row(
    source_row_index: int,
    transition: str,
    *,
    parse_ok: bool = True,
    exact_evidence: bool = True,
    issues: list[str] | None = None,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "candidate_id": f"direct_labeler:{source_row_index}",
        "candidate_source": "llm_candidate",
        "prediction_bearing": True,
        "parse_ok": parse_ok,
        "exact_evidence": exact_evidence,
        "contract_issues": issues or [],
        "transition": transition,
        "current_label": "seizure free for multiple year",
        "proposed_label": "unknown",
        "gold_label": "unknown",
        "event_kind": "unknown_frequency",
        "evidence": "bounded evidence",
    }
