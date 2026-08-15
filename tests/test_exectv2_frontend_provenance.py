from clinical_extraction.trace_explorer.exectv2_comparison import (
    last_diverging_provenance_action,
)


def _event(action: str) -> dict[str, str]:
    return {"stage": "entity_lens", "action": action, "owner": "standard_dictionary"}


def test_unchanged_model_finding_has_no_last_rule_action() -> None:
    mention = {
        "component_owner": "named_model_structured_facts",
        "provenance": [
            _event("emitted_scored_candidate"),
            _event("applied_standard_dictionary_prescription_repair"),
        ],
    }
    assert last_diverging_provenance_action(mention) == ""


def test_last_diverging_action_skips_wrap_up_event() -> None:
    mention = {
        "component_owner": "named_model_structured_facts+standard_dictionary_prescription",
        "provenance": [
            _event("emitted_scored_candidate"),
            _event("normalized_prescription_from_dictionary"),
            _event("applied_standard_dictionary_prescription_repair"),
        ],
    }
    assert (
        last_diverging_provenance_action(mention)
        == "normalized_prescription_from_dictionary"
    )


def test_added_residual_is_the_diverging_action() -> None:
    mention = {
        "provenance": [
            _event("added_diagnosis_residual_from_dictionary"),
            _event("applied_standard_dictionary_diagnosis_repair"),
        ]
    }
    assert (
        last_diverging_provenance_action(mention)
        == "added_diagnosis_residual_from_dictionary"
    )


def test_missing_or_gold_provenance_is_blank() -> None:
    assert last_diverging_provenance_action({}) == ""
    assert last_diverging_provenance_action({"provenance": "not-a-list"}) == ""
