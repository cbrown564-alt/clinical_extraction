import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_predeclaration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    selective_verifier,
)
from tests.test_gan2026_selective_verifier_predeclaration import _routing_row


def _predeclared_row() -> dict:
    rows, _ = (
        selective_verifier_predeclaration.build_selective_verifier_predeclaration_rows(
            [_routing_row()]
        )
    )
    return rows[0]


def test_binary_verifier_model_input_is_plain_language_and_metadata_free() -> None:
    payload = selective_verifier.build_binary_quote_highest_model_input(
        _predeclared_row(),
        {
            101: (
                "Current seizures occur about once per month. "
                "Recent seizure-free interval is also mentioned."
            )
        },
    )
    payload_text = json.dumps(payload, sort_keys=True)

    assert payload["proposed_answer"] == "1 per month"
    assert "task_design" not in payload
    assert "selected_label" not in payload
    for term in [
        "Gan",
        "benchmark",
        "scorer",
        "source-near",
        "operands",
        "denominator",
        "gold",
        "frozen",
        "control",
        "delta",
    ]:
        assert term not in payload_text


def test_parse_binary_verifier_accepts_single_answer_list() -> None:
    parsed, errors = selective_verifier.parse_binary_quote_highest_output(
        json.dumps(
            {
                "quote_supports_label": True,
                "selected_label_is_highest_frequency": True,
                "certain": True,
                "selected_answer": ["1 per month"],
                "supporting_quotes": ["Current seizures occur about once per month."],
                "reason": "The answer is stated directly.",
            }
        )
    )

    assert errors == []
    assert parsed is not None
    assert parsed.selected_answer == "1 per month"


def test_summarize_saved_binary_verifier_rows_counts_regressions() -> None:
    summary = selective_verifier.summarize_saved_binary_verifier_rows(
        [
            {
                "source_row_index": 1,
                "task_design": selective_verifier.PROMOTED_VERIFIER_DESIGN,
                "call_status": "ok",
                "parsed_output": {"selected_answer": "1 per month"},
                "parse_errors": [],
                "design_action": "1 per month",
                "verifier_vs_routing": {
                    "decision_changed": True,
                    "delta": "W_to_C",
                },
            },
            {
                "source_row_index": 2,
                "task_design": selective_verifier.PROMOTED_VERIFIER_DESIGN,
                "call_status": "ok",
                "parsed_output": {"selected_answer": "unknown"},
                "parse_errors": [],
                "design_action": "unknown",
                "verifier_vs_routing": {
                    "decision_changed": True,
                    "delta": "C_to_W",
                },
            },
            {
                "source_row_index": 3,
                "task_design": "support_parts_fact_check",
                "call_status": "ok",
                "parsed_output": {},
                "parse_errors": [],
                "verifier_vs_routing": {"delta": "W_to_C"},
            },
        ]
    )

    assert summary["row_count"] == 2
    assert summary["w_to_c_vs_routing_rows"] == 1
    assert summary["c_to_w_vs_routing_rows"] == 1
    assert summary["regression_source_row_indices"] == [2]

