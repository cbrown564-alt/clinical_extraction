from scripts.summarize_gan2026_six_model_validation_comparison import (
    compare_method_rows,
    summarize_condition_rows,
)


def _row(
    index: int,
    *,
    method: str,
    label: str,
    purist_correct: bool,
    pragmatic_correct: bool,
    evidence_valid: bool = True,
    model_label: str | None = None,
) -> dict:
    trace = {
        "schema_version": "gan2026.row_trace.v1",
        "method": method,
        "model_prediction": {"record": {"final_label": model_label or label}},
    }
    row = {
        "source_row_index": index,
        "row_trace": trace,
        "call_error": None,
        "parse_errors": [],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": pragmatic_correct,
        },
    }
    if method == "llm_only":
        row["decision_record"] = {"final_label": label}
        row["evidence_text_contained"] = evidence_valid
    else:
        row["structured_record"] = {"selection": {"final_label": label}}
        row["evidence_valid"] = evidence_valid
    return row


def test_summarize_condition_rows_checks_trace_and_model_boundary() -> None:
    rows = [
        _row(
            10,
            method="llm_only",
            label="2 per month",
            model_label=" 2 PER MONTH ",
            purist_correct=True,
            pragmatic_correct=True,
        ),
        _row(
            11,
            method="llm_only",
            label="unknown",
            purist_correct=False,
            pragmatic_correct=True,
            evidence_valid=False,
        ),
    ]

    summary = summarize_condition_rows(
        rows,
        expected_indices={10, 11},
        method="llm_only",
    )

    assert summary["complete"] is True
    assert summary["trace_rows"] == 2
    assert summary["model_to_final_changed"] == 1
    assert summary["evidence_valid"] == 1
    assert summary["purist_correct"] == 1
    assert summary["pragmatic_correct"] == 2


def test_compare_method_rows_counts_direction_and_changed_evidence() -> None:
    llm_only = [
        _row(
            10,
            method="llm_only",
            label="unknown",
            purist_correct=False,
            pragmatic_correct=False,
        ),
        _row(
            11,
            method="llm_only",
            label="2 per month",
            purist_correct=True,
            pragmatic_correct=True,
            evidence_valid=False,
        ),
    ]
    llm_with_rules = [
        _row(
            10,
            method="llm_with_rules",
            label="2 per month",
            purist_correct=True,
            pragmatic_correct=True,
        ),
        _row(
            11,
            method="llm_with_rules",
            label="unknown",
            purist_correct=False,
            pragmatic_correct=False,
        ),
    ]

    comparison = compare_method_rows(llm_only, llm_with_rules)

    assert comparison["changed_labels"] == 2
    assert comparison["llm_only_wrong_to_rules_correct"] == 1
    assert comparison["llm_only_correct_to_rules_wrong"] == 1
    assert comparison["changed_rows_both_evidence_valid"] == 1
