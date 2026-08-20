"""Schema / format / post boundaries for ExECT mention stacks."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

_NOTE = (
    "Diagnosis: epilepsy – unclassified. She takes Keppra 500 mgs twice daily "
    "and will start clobazam next week. MRI requested. "
    "She has two to three seizures per month."
)


def _mention(
    entity: str,
    text: str,
    *,
    attributes: dict[str, str] | None = None,
    evidence: str | None = None,
) -> PredictedMention:
    return PredictedMention(
        entity=entity,
        text=text,
        attributes=attributes or {},
        evidence=evidence if evidence is not None else text,
        confidence="high",
        rationale="fixture",
    )


def test_schema_keeps_written_findings_without_cui() -> None:
    mentions = [
        _mention(DIAGNOSIS.name, "epilepsy", attributes={"DiagCategory": "Epilepsy"}),
        _mention("PatientHistory", "ignored"),
    ]

    schema = structured.schema_mentions(mentions)

    assert [mention.entity for mention in schema] == [DIAGNOSIS.name]
    assert "CUI" not in schema[0].attributes


def test_format_respells_same_regimen_and_attaches_cui_without_drops() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: epilepsy – unclassified",
        ),
        _mention(
            PRESCRIPTION.name,
            "Keppra 500 mgs twice daily",
            attributes={
                "DrugName": "Keppra",
                "DrugDose": "500",
                "DoseUnit": "mgs",
                "Frequency": "2",
            },
        ),
        _mention(
            PRESCRIPTION.name,
            "clobazam next week",
            attributes={"DrugName": "clobazam"},
            evidence="will start clobazam next week",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizures",
            attributes={"NumberOfSeizures": "2-3", "TimePeriod": "month"},
            evidence="two to three seizures per month",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "unlabelled events",
            attributes={"Negation": "Affirmed"},
            evidence="MRI requested",
        ),
        _mention(
            INVESTIGATIONS.name,
            "MRI",
            attributes={"MRI_Performed": "No", "EEG_Performed": "No"},
            evidence="MRI requested",
        ),
        _mention(
            DIAGNOSIS.name,
            "not in note",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="this evidence is absent",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(mentions, _NOTE)
    texts = [mention.text for mention in formatted]
    rx = next(
        mention
        for mention in formatted
        if mention.entity == PRESCRIPTION.name and "Keppra" in mention.text
    )
    dx = next(
        mention
        for mention in formatted
        if mention.entity == DIAGNOSIS.name and mention.text == "epilepsy"
    )
    sf = next(
        mention
        for mention in formatted
        if mention.entity == SEIZURE_FREQUENCY.name and mention.text == "seizures"
    )
    inv = next(mention for mention in formatted if mention.entity == INVESTIGATIONS.name)

    assert "clobazam next week" in texts
    assert "unlabelled events" in texts
    assert "not in note" in texts
    assert dx.text == "epilepsy"
    assert dx.attributes.get("CUI") == "C0014544"
    assert rx.attributes["DrugName"] == "levetiracetam"
    assert rx.attributes["DoseUnit"] == "mg"
    assert sf.attributes.get("LowerNumberOfSeizures") == "2"
    assert sf.attributes.get("UpperNumberOfSeizures") == "3"
    assert "EEG_Performed" not in inv.attributes


def test_live_gate_still_drops_ungrounded_and_no_state_findings() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "not in note",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="this evidence is absent",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "unlabelled events",
            attributes={"Negation": "Affirmed"},
            evidence="MRI requested",
        ),
        _mention(
            PRESCRIPTION.name,
            "Keppra 500 mgs twice daily",
            attributes={
                "DrugName": "Keppra",
                "DrugDose": "500",
                "DoseUnit": "mgs",
                "Frequency": "2",
            },
        ),
    ]

    letter, warnings = structured.to_predicted_letter(
        "TEST001", mentions, note_text=_NOTE
    )

    assert [mention.entity for mention in letter.mentions] == [PRESCRIPTION.name]
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)
    assert any("dropped_no_frequency_state_rendering" in warning for warning in warnings)
