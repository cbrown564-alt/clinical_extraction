"""Invariant-focused tests for exectv2 deterministic sf pipeline."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.association import (
    associate_attributes_to_anchors,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.candidates import (
    AnchorCandidate,
    AttributeExtraction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.overlap import (
    resolve_overlapping_anchors,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)


def _make_letter(letter_id: str, note_text: str) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text)


def test_overlap_anchors_prefers_longer_span() -> None:
    short = AnchorCandidate(text="seizures", evidence="seizures", span=(10, 18), rule_id="a")
    long = AnchorCandidate(
        text="focal seizures with loss of awareness",
        evidence="focal seizures with loss of awareness",
        span=(4, 42),
        rule_id="b",
    )
    resolved = resolve_overlapping_anchors([short, long])
    assert len(resolved) == 1
    assert resolved[0] is long


def test_association_merges_nearest_attribute() -> None:
    anchor = AnchorCandidate(
        text="focal seizures", evidence="focal seizures", span=(0, 14), rule_id="a"
    )
    other_anchor = AnchorCandidate(
        text="absences", evidence="absences", span=(100, 108), rule_id="b"
    )
    attr = AttributeExtraction(
        evidence="2 per month",
        span=(15, 26),
        attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
    )

    pairs = associate_attributes_to_anchors([anchor, other_anchor], [attr])
    assert len(pairs) == 1
    matched_anchor, attrs = pairs[0]
    assert matched_anchor is anchor
    assert attrs["NumberOfSeizures"] == "2"


def test_pipeline_produces_predicted_letter() -> None:
    letter = _make_letter(
        "T001",
        "Seizure type and frequency: focal seizures with loss of awareness "
        "approximately 3 per month.",
    )
    result = extract_seizure_frequency(letter)
    assert result.letter_id == "T001"
    sf_mentions = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert sf_mentions
    assert sf_mentions[0].text.lower() == "focal seizures with loss of awareness"
    assert sf_mentions[0].attributes["NumberOfSeizures"] == "3"


def test_pipeline_statement_seizure_free_projection_keeps_c129_same() -> None:
    text = "Richard tells me that he remains seizure free which is good news."
    letter = _make_letter("T006I", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "seizure"
        and m.attributes.get("CUI") == "C1299590"
        and m.attributes.get("NumberOfSeizures") == "0"
        and m.attributes.get("FrequencyChange") == "Same"
        for m in sf
    )
    assert not any(
        m.text.lower() == "seizure"
        and m.attributes.get("CUI") == "C1299590"
        and set(m.attributes) <= {"NumberOfSeizures", "CUI", "CUIPhrase"}
        for m in sf
    )


def test_pipeline_frequency_section_date_list_emits_multiple_mentions() -> None:
    text = (
        "Seizure type and frequency: focal seizures with altered awareness (right arm movement)\n"
        "                1 per week\n"
        "                Focal to bilateral convulsive seizures August 2014 and September 2015\n"
        "Current medication: Lamotrigine 150mg bd\n"
    )
    letter = _make_letter("T006A", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "focal seizures with altered awareness"
        and m.attributes.get("NumberOfSeizures") == "1"
        and m.attributes.get("TimePeriod") == "Week"
        for m in sf
    )
    dated = [
        m
        for m in sf
        if m.text.lower() == "focal to bilateral convulsive seizures"
        and m.attributes.get("NumberOfSeizures") == "1"
    ]
    assert {m.attributes.get("MonthDate") for m in dated} == {"8", "9"}
    assert {m.attributes.get("YearDate") for m in dated} == {"2014", "2015"}
