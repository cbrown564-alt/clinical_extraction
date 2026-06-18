"""Tests for the ExECTv2 clinical-recovery error ledger."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    clinical_recovery_error_ledger as ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_error_ledger import (  # noqa: E501
    build_combined_predictions_from_rows,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _pred(entity: str, text: str, **attrs: str) -> PredictedMention:
    return PredictedMention(entity=entity, text=text, attributes=dict(attrs), evidence=text)


def test_error_ledger_reports_class_a_headline_keys() -> None:
    gold = ExectLetter(
        "L1",
        "Lamotrigine 100 mg twice daily. MRI normal. No seizures since 2019.",
        (
            _ann(
                PRESCRIPTION.name,
                "Lamotrigine 100 mg twice daily",
                DrugName="lamotrigine",
                DrugDose="100",
                DoseUnit="mg",
                Frequency="2",
            ),
            _ann(INVESTIGATIONS.name, "MRI normal", MRI_Performed="1", MRI_Results="0"),
            _ann(
                SEIZURE_FREQUENCY.name,
                "seizures",
                CUI="C0036572",
                NumberOfSeizures="0",
            ),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L1",
        mentions=(
            _pred(
                PRESCRIPTION.name,
                "Lamotrigine 100 mg twice daily",
                DrugName="lamotrigine",
                DrugDose="100",
                DoseUnit="mg",
                Frequency="2",
            ),
            _pred(INVESTIGATIONS.name, "MRI normal", MRI_Performed="1", MRI_Results="1"),
            _pred(
                SEIZURE_FREQUENCY.name,
                "seizures",
                CUI="C0036572",
                NumberOfSeizures="1",
            ),
        ),
    )

    result = ledger.build_error_ledger([gold], [prediction])

    assert result["summary"]["per_entity"][PRESCRIPTION.name]["headline"]["f1"] == 1.0
    assert result["summary"]["per_entity"][INVESTIGATIONS.name]["headline"]["fn"] == 1
    assert result["summary"]["per_entity"][INVESTIGATIONS.name]["headline"]["fp"] == 1
    assert result["summary"]["per_entity"][SEIZURE_FREQUENCY.name]["headline"]["fn"] == 1
    assert result["summary"]["per_entity"][SEIZURE_FREQUENCY.name]["headline"]["fp"] == 1
    inv_records = [
        record for record in result["records"] if record["entity"] == INVESTIGATIONS.name
    ]
    assert {record["side"] for record in inv_records} == {"gold", "predicted"}


def test_error_ledger_summarizes_sf_residuals_by_side_and_state() -> None:
    gold = ExectLetter(
        "L1",
        "Two seizures per month. No tonic clonic seizures since surgery.",
        (
            _ann(
                SEIZURE_FREQUENCY.name,
                "seizures",
                CUI="C0036572",
                NumberOfSeizures="2",
            ),
            _ann(
                SEIZURE_FREQUENCY.name,
                "tonic clonic seizures",
                CUI="C0494475",
                NumberOfSeizures="0",
            ),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L1",
        mentions=(
            _pred(
                SEIZURE_FREQUENCY.name,
                "seizures",
                CUI="C0036572",
                FrequencyChange="Increased",
            ),
        ),
    )

    result = ledger.build_error_ledger([gold], [prediction], entities=(SEIZURE_FREQUENCY.name,))

    entry = result["summary"]["per_entity"][SEIZURE_FREQUENCY.name]
    assert entry["residual_error_counts"] == {
        "candidate_miss": 2,
        "wrong_detail_selection": 1,
    }
    assert entry["residual_state_counts"] == {
        "gold": {"active-rate": 1, "seizure-free": 1, "unknown": 0},
        "predicted": {"active-rate": 0, "seizure-free": 0, "unknown": 1},
    }


def test_error_ledger_uses_entity_agnostic_diagnosis_recall_pool() -> None:
    gold = ExectLetter(
        "L2",
        "Diagnosis: generalised tonic clonic seizures.",
        (
            _ann(
                DIAGNOSIS.name,
                "generalised tonic clonic seizures",
                Certainty="5",
                Negation="Affirmed",
                DiagCategory="MultipleSeizures",
            ),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L2",
        mentions=(
            _pred(
                PATIENT_HISTORY.name,
                "generalised tonic clonic seizures",
                Certainty="5",
                Negation="Affirmed",
                DiagCategory="MultipleSeizures",
            ),
        ),
    )

    result = ledger.build_error_ledger([gold], [prediction], entities=(DIAGNOSIS.name,))

    entry = result["summary"]["per_entity"][DIAGNOSIS.name]
    assert entry["headline"]["recall"] == 1.0
    assert entry["headline"]["fn"] == 0
    assert result["records"] == []


def test_build_combined_predictions_prefers_family_overrides() -> None:
    gold = [ExectLetter("L3", "note")]
    structured_rows = [
        {
            "letter_id": "L3",
            "predicted_mentions": [
                {"entity": PRESCRIPTION.name, "text": "lamotrigine", "attributes": {}},
                {"entity": DIAGNOSIS.name, "text": "old diagnosis", "attributes": {}},
                {"entity": SEIZURE_FREQUENCY.name, "text": "old sf", "attributes": {}},
            ],
        }
    ]
    diagnosis_rows = [
        {
            "letter_id": "L3",
            "predicted_mentions": [
                {"entity": DIAGNOSIS.name, "text": "verified diagnosis", "attributes": {}}
            ],
        }
    ]
    sf_rows = [
        {
            "letter_id": "L3",
            "predicted_mentions": [
                {"entity": SEIZURE_FREQUENCY.name, "text": "verified sf", "attributes": {}}
            ],
        }
    ]
    investigations_rows = [
        {
            "letter_id": "L3",
            "predicted_mentions": [
                {
                    "entity": INVESTIGATIONS.name,
                    "text": "verified investigation",
                    "attributes": {},
                }
            ],
        }
    ]

    combined = build_combined_predictions_from_rows(
        gold,
        structured_rows,
        diagnosis_rows=diagnosis_rows,
        sf_rows=sf_rows,
        investigations_rows=investigations_rows,
    )

    assert [mention.text for mention in combined[0].mentions] == [
        "lamotrigine",
        "verified investigation",
        "verified diagnosis",
        "verified sf",
    ]
