import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_prompt_design_experiment as experiment,
)


def _predeclared_row() -> dict:
    return {
        "source_row_index": 101,
        "development_accounting": {
            "gold_label": "1 per month",
            "routing_policy_action": "route_unknown",
            "routing_policy_label": "unknown",
        },
        "prompt_design_candidates": {
            "veto_first_safety_reviewer": {
                "clinical_text": "Current seizures occur once per month.",
                "proposed_answer": "1 per month",
                "system_prompt": "Review the proposed answer.",
            },
            "support_parts_fact_check": {
                "clinical_text": "Current seizures occur once per month.",
                "proposed_answer": "1 per month",
                "system_prompt": "Check the answer parts.",
            },
            "support_parts_full_letter": {
                "clinical_text": "Full letter says current seizures occur once per month.",
                "evidence_snippet": "Current seizures occur once per month.",
                "proposed_answer": "1 per month",
                "system_prompt": "Check the answer against the full letter.",
            },
            "binary_quote_highest_answer_selector": {
                "clinical_text": "Full letter says current seizures occur once per month.",
                "selected_quote": "Current seizures occur once per month.",
                "proposed_answer": "1 per month",
                "answer_choices": ["1 per month", "unknown", "human_review"],
                "system_prompt": "Check the selected quote and label.",
            },
        },
    }


def test_veto_first_use_proposed_counts_wrong_to_correct() -> None:
    parsed, errors = experiment._parse_output(
        "veto_first_safety_reviewer",
        json.dumps(
            {
                "decision": "use_proposed_answer",
                "blocking_issue": "none",
                "supporting_quotes": ["Current seizures occur once per month."],
                "reason": "The answer is directly stated.",
                "confidence": "high",
            }
        ),
    )

    decision = experiment._design_decision(
        "veto_first_safety_reviewer", parsed, _predeclared_row(), parse_errors=errors
    )
    routing = experiment.base_experiment._routing_decision(_predeclared_row())

    assert decision["label"] == "1 per month"
    assert experiment.base_experiment._delta(decision, routing) == {
        "decision_changed": True,
        "delta": "W_to_C",
    }


def test_support_parts_missing_count_keeps_unknown() -> None:
    parsed, errors = experiment._parse_output(
        "support_parts_fact_check",
        json.dumps(
            {
                "seizure_or_event_type_supported": True,
                "count_supported": False,
                "timeframe_supported": True,
                "current_highest_frequency_supported": True,
                "all_required_parts_supported": False,
                "recommended_action": "use_unknown",
                "missing_or_conflicting_parts": ["count_supported"],
                "quotes": ["Current seizures occur once per month."],
                "reason": "The count is not supported.",
            }
        ),
    )

    decision = experiment._design_decision(
        "support_parts_fact_check", parsed, _predeclared_row(), parse_errors=errors
    )
    routing = experiment.base_experiment._routing_decision(_predeclared_row())

    assert decision["label"] == "unknown"
    assert experiment.base_experiment._delta(decision, routing) == {
        "decision_changed": False,
        "delta": "unchanged",
    }


def test_support_parts_accepts_single_item_action_list() -> None:
    parsed, errors = experiment._parse_output(
        "support_parts_fact_check",
        json.dumps(
            {
                "seizure_or_event_type_supported": "true",
                "count_supported": "false",
                "timeframe_supported": "true",
                "current_highest_frequency_supported": "false",
                "all_required_parts_supported": "false",
                "recommended_action": ["needs_review"],
                "missing_or_conflicting_parts": ["count_supported"],
                "quotes": ["Current seizures occur once per month."],
                "reason": "The count is not supported.",
            }
        ),
    )

    assert errors == []
    assert parsed is not None
    assert parsed.recommended_action == "needs_review"


def test_support_parts_full_letter_uses_supported_schema() -> None:
    parsed, errors = experiment._parse_output(
        "support_parts_full_letter",
        json.dumps(
            {
                "seizure_or_event_type_supported": True,
                "count_supported": True,
                "timeframe_supported": True,
                "current_highest_frequency_supported": True,
                "all_answer_parts_supported": True,
                "recommended_action": "use_proposed_answer",
                "missing_or_conflicting_parts": [],
                "quotes": ["current seizures occur once per month"],
                "reason": "The answer is supported by the full letter.",
            }
        ),
    )

    decision = experiment._design_decision(
        "support_parts_full_letter", parsed, _predeclared_row(), parse_errors=errors
    )

    assert errors == []
    assert decision["label"] == "1 per month"


def test_invalid_action_is_parse_error() -> None:
    parsed, errors = experiment._parse_output(
        "veto_first_safety_reviewer",
        json.dumps(
            {
                "decision": "render_final",
                "blocking_issue": "none",
                "supporting_quotes": ["Current seizures occur once per month."],
                "reason": "Nope.",
                "confidence": "high",
            }
        ),
    )

    assert parsed is None
    assert errors == ["unsupported_decision:render_final"]


def test_binary_design_keeps_supported_highest_label() -> None:
    parsed, errors = experiment._parse_output(
        "binary_quote_highest_answer_selector",
        json.dumps(
            {
                "quote_supports_label": True,
                "selected_label_is_highest_frequency": True,
                "certain": True,
                "selected_answer": "1 per month",
                "supporting_quotes": ["Current seizures occur once per month."],
                "reason": "The selected quote directly supports the label.",
            }
        ),
    )

    decision = experiment._design_decision(
        "binary_quote_highest_answer_selector",
        parsed,
        _predeclared_row(),
        parse_errors=errors,
    )

    assert errors == []
    assert decision["label"] == "1 per month"


def test_binary_design_routes_review_when_not_highest_without_alternative() -> None:
    parsed, errors = experiment._parse_output(
        "binary_quote_highest_answer_selector",
        json.dumps(
            {
                "quote_supports_label": True,
                "selected_label_is_highest_frequency": False,
                "certain": True,
                "selected_answer": "human_review",
                "supporting_quotes": ["Current seizures occur once per month."],
                "reason": "Another seizure type may be more frequent.",
            }
        ),
    )

    decision = experiment._design_decision(
        "binary_quote_highest_answer_selector",
        parsed,
        _predeclared_row(),
        parse_errors=errors,
    )

    assert decision["action"] == "abstain_review"


def test_binary_prompt_forces_false_highest_on_competing_active_events() -> None:
    prompt = experiment.BINARY_SYSTEM_PROMPT

    assert "selected_label_is_highest_frequency to false" in prompt
    assert "any other current or recent seizure type is more frequent" in prompt
    assert "Do not mark a zero-seizure answer as highest" in prompt
    assert "Only answer true when the proposed answer is at least as frequent" in prompt


def test_binary_rendered_payload_is_plain_language_and_metadata_free() -> None:
    payload = experiment._model_input(
        _predeclared_row(),
        "binary_quote_highest_answer_selector",
        {101: "Full letter says current seizures occur once per month."},
    )
    payload_text = json.dumps(payload, sort_keys=True)

    assert payload["proposed_answer"] == "1 per month"
    assert "task_design" not in payload
    assert "selected_label" not in payload
    for term in ["Gan", "benchmark", "scorer", "gold", "frozen", "control", "delta"]:
        assert term not in payload_text
