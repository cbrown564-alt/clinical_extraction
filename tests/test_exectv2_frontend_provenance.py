"""Exemplars for ExECT frontend last-rule provenance labels."""

from clinical_extraction.trace_explorer.exectv2_comparison import (
    _project_predicted_cuis,
    last_diverging_provenance_action,
    last_rule_label,
)


def _event(action: str, **detail: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "stage": "entity_lens",
        "action": action,
        "owner": "standard_dictionary",
    }
    if detail:
        payload["detail"] = detail
    return payload


def test_unchanged_model_finding_has_no_last_rule_action() -> None:
    mention = {
        "component_owner": "named_model_structured_facts",
        "provenance": [
            _event("emitted_scored_candidate"),
            _event("applied_standard_dictionary_prescription_repair"),
        ],
    }
    assert last_diverging_provenance_action(mention) == ""


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


def test_prescription_label_names_attribute_before_and_after() -> None:
    mention = {
        "provenance": [
            _event("emitted_scored_candidate"),
            _event(
                "normalized_prescription_from_dictionary",
                attribute_changes=[
                    {
                        "attribute": "DrugName",
                        "before": "tegretol",
                        "after": "carbamazepine",
                    }
                ],
            ),
            _event("applied_standard_dictionary_prescription_repair"),
        ]
    }
    assert (
        last_rule_label(mention)
        == "Dictionary set DrugName from tegretol to carbamazepine"
    )


def test_explorer_repairs_epilepsy_category_on_named_seizure_types() -> None:
    projected = _project_predicted_cuis(
        [
            {
                "entity": "Diagnosis",
                "text": "focal seizures without change in awareness",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "entity": "Diagnosis",
                "text": "secondary generalised seizures",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "entity": "Diagnosis",
                "text": "epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
        ]
    )
    assert projected[0]["attributes"]["DiagCategory"] == "MultipleSeizures"
    assert projected[1]["attributes"]["DiagCategory"] == "MultipleSeizures"
    assert projected[2]["attributes"]["DiagCategory"] == "Epilepsy"
