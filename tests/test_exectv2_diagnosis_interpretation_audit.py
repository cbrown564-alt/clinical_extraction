from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_interpretation_audit import (  # noqa: E501
    ConceptResidual,
    MethodDisagreements,
    match_diagnosis_concepts,
    union_review_rows,
)


def test_match_diagnosis_concepts_uses_exact_and_hierarchy_matches() -> None:
    result = match_diagnosis_concepts(
        gold=("temporal lobe epilepsy", "absence seizures", "status epilepticus"),
        predicted=("focal epilepsy", "absence seizures", "dissociative seizures"),
    )

    assert result.matched == 2
    assert result.gold_unmatched == ("status epilepticus",)
    assert result.predicted_unmatched == ("dissociative seizures",)


def test_union_review_rows_deduplicates_method_review_targets() -> None:
    shared = ConceptResidual(
        letter_id="EA0001",
        direction="missed",
        concept="focal epilepsy",
    )
    rows = union_review_rows(
        (
            MethodDisagreements(method="rules_only", residuals=(shared,)),
            MethodDisagreements(method="llm_only", residuals=(shared,)),
            MethodDisagreements(
                method="llm_with_rules",
                residuals=(
                    ConceptResidual(
                        letter_id="EA0001",
                        direction="spurious",
                        concept="dissociative seizures",
                    ),
                ),
            ),
        )
    )

    assert rows == (
        {
            "review_key": "EA0001|missed|focal epilepsy",
            "letter_id": "EA0001",
            "direction": "missed",
            "normalized_concept": "focal epilepsy",
            "methods": ["llm_only", "rules_only"],
        },
        {
            "review_key": "EA0001|spurious|dissociative seizures",
            "letter_id": "EA0001",
            "direction": "spurious",
            "normalized_concept": "dissociative seizures",
            "methods": ["llm_with_rules"],
        },
    )
