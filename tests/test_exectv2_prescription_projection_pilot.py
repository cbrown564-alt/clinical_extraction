from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    prescription_projection_pilot as pilot,
)


def _rx(text: str, **attrs: str) -> dict[str, object]:
    return {"entity": "Prescription", "text": text, "attributes": dict(attrs)}


def test_prescription_projection_taxonomy_separates_allowed_and_boundary_rules() -> None:
    rules = {rule.rule_id: rule for rule in pilot.PRESCRIPTION_PROJECTION_RULES}

    assert rules["prescription_drugname_cui_projection"].score_line is (
        pilot.ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION
    )
    assert rules["prescription_missing_medication_rescue"].score_line is (
        pilot.ProjectionScoreLine.HYBRID_RESCUE
    )
    assert rules["prescription_unsupported_medication_rejection"].score_line is (
        pilot.ProjectionScoreLine.VERIFIER_FILTERED
    )
    assert rules["prescription_missing_dose_or_frequency_completion"].allowed_in_llm_only is False
    assert rules["prescription_drugname_cui_projection"].portability_category == (
        "benchmark_format"
    )


def test_prescription_projection_pilot_counts_projection_without_rescue() -> None:
    rows = [
        {
            "letter_id": "RX1",
            "gold_mentions": [
                _rx(
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                ),
                _rx(
                    "Lamotrigine-100mg-bd",
                    DrugName="Lamotrigine",
                    DrugDose="100",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ],
            "structured_mentions_final": [
                _rx(
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                )
            ],
            "predicted_mentions": [
                _rx(
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                    CUIPhrase="levetiracetam",
                )
            ],
        },
        {
            "letter_id": "RX2",
            "gold_mentions": [],
            "structured_mentions_final": [_rx("planned lamotrigine", DrugName="lamotrigine")],
            "predicted_mentions": [_rx("planned lamotrigine", DrugName="lamotrigine")],
        },
    ]

    result = pilot.build_prescription_projection_pilot(rows)

    assert result["rule_counts"]["prescription_drugname_cui_projection"] == 1
    assert result["boundary_counts"]["prescription_missing_medication_rescue"] == 1
    assert result["boundary_counts"]["prescription_unsupported_medication_rejection"] == 1
    assert result["boundary_counts"]["prescription_missing_dose_or_frequency_completion"] == 1
    assert result["score_lines"]["hybrid_rescue"]["status"] == "not_applied"
    assert result["score_lines"]["verifier_filtered"]["status"] == "not_applied"
    assert (
        result["score_lines"]["llm_only_meaning_preserving_projection"]["scores"][
            "drugname_cui_projection"
        ]["f1"]
        == 1.0
    )


def test_prescription_projection_pilot_markdown_reports_score_lines_and_examples() -> None:
    rows = [
        {
            "letter_id": "RX1",
            "gold_mentions": [
                _rx(
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                )
            ],
            "structured_mentions_final": [
                _rx(
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                )
            ],
            "predicted_mentions": [
                _rx(
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                )
            ],
        }
    ]

    text = pilot.render_prescription_projection_pilot_markdown(
        pilot.build_prescription_projection_pilot(rows)
    )

    assert "# ExECTv2 Phase 5 Prescription Projection Pilot" in text
    assert "llm_only_meaning_preserving_projection" in text
    assert "prescription_drugname_cui_projection" in text
    assert "Accepted Projection Examples" in text
