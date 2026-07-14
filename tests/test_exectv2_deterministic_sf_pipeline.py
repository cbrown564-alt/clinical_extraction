"""Invariant-focused tests for exectv2 deterministic sf pipeline."""

from __future__ import annotations

from importlib import import_module

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
    resolve_overlapping_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    DEFAULT_ABLATION,
    ExtractionContext,
)

_sf_rules = import_module(
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction"
)
SEIZURE_FREE_ANCHOR_RULE = _sf_rules.SEIZURE_FREE_ANCHOR_RULE
SEIZURE_TYPE_ANCHOR_RULE = _sf_rules.SEIZURE_TYPE_ANCHOR_RULE


def _apply(spec, text: str) -> list[AttributeExtraction]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AttributeExtraction)]


def _apply_anchors(spec, text: str) -> list[AnchorCandidate]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AnchorCandidate)]


def _make_letter(letter_id: str, note_text: str) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text)


_PINNED_DEV_PER_ITEM_F1 = {
    "phrase_only": 0.756,
    "sf_semantic": 0.705,
    "sf_benchmark": 0.705,
}

_F1_BAND = 0.02


def test_anchor_frontal_lobe_and_convulsion_phrases() -> None:
    text = "Frontal lobe seizures occur monthly. He has not had generalised convulsions for years."
    results = _apply_anchors(SEIZURE_TYPE_ANCHOR_RULE, text)
    assert [r.text.lower() for r in results] == [
        "frontal lobe seizures",
        "generalised convulsions",
    ]


def test_anchor_bare_seizures() -> None:
    results = _apply_anchors(SEIZURE_TYPE_ANCHOR_RULE, "No change in seizures over the last year.")
    assert any(c.text.lower() == "seizures" for c in results)


def test_anchor_seizure_free_phrase() -> None:
    results = _apply_anchors(SEIZURE_FREE_ANCHOR_RULE, "She has been seizure-free for 7 months.")
    assert any(
        "seizure-free" == c.text.lower() or "seizure free" == c.text.lower() for c in results
    )


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


def test_overlap_anchors_keeps_non_overlapping() -> None:
    a = AnchorCandidate(text="focal seizures", evidence="focal seizures", span=(0, 14), rule_id="a")
    b = AnchorCandidate(text="absences", evidence="absences", span=(20, 28), rule_id="b")
    resolved = resolve_overlapping_anchors([a, b])
    assert len(resolved) == 2


def test_overlap_attributes_prefers_more_specific() -> None:
    text = "2-5 per month"
    range_extraction = AttributeExtraction(
        evidence=text,
        span=(0, len(text)),
        attributes={
            "LowerNumberOfSeizures": "2",
            "UpperNumberOfSeizures": "5",
            "TimePeriod": "Month",
            "NumberOfTimePeriods": "1",
        },
        rule_id="range",
    )
    count_extraction = AttributeExtraction(
        evidence="5 per month",
        span=(2, len(text)),
        attributes={"NumberOfSeizures": "5", "TimePeriod": "Month"},
        rule_id="count",
    )
    resolved = resolve_overlapping_attributes([range_extraction, count_extraction])
    assert len(resolved) == 1
    assert resolved[0].rule_id == "range"


def test_overlap_attributes_keeps_non_overlapping() -> None:
    a = AttributeExtraction(
        evidence="3 per month",
        span=(0, 11),
        attributes={"NumberOfSeizures": "3", "TimePeriod": "Month"},
    )
    b = AttributeExtraction(
        evidence="2 per week",
        span=(20, 30),
        attributes={"NumberOfSeizures": "2", "TimePeriod": "Week"},
    )
    resolved = resolve_overlapping_attributes([a, b])
    assert len(resolved) == 2


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


def test_association_drops_anchors_without_attributes() -> None:
    anchor_with = AnchorCandidate(
        text="focal seizures", evidence="focal seizures", span=(0, 14), rule_id="a"
    )
    anchor_without = AnchorCandidate(
        text="absences", evidence="absences", span=(100, 108), rule_id="b"
    )
    attr = AttributeExtraction(
        evidence="2 per month",
        span=(15, 26),
        attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
    )

    pairs = associate_attributes_to_anchors([anchor_with, anchor_without], [attr])
    assert len(pairs) == 1
    assert pairs[0][0] is anchor_with


def test_association_no_anchors_returns_empty() -> None:
    attr = AttributeExtraction(
        evidence="2 per month", span=(15, 26), attributes={"NumberOfSeizures": "2"}
    )
    assert associate_attributes_to_anchors([], [attr]) == []


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


def test_pipeline_sf_mention_attributes() -> None:
    letter = _make_letter("T002", "She has been seizure free for 6 months.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert sf
    assert any(m.attributes.get("NumberOfSeizures") == "0" for m in sf)


def test_pipeline_evidence_is_substring() -> None:
    letter = _make_letter("T003", "He experiences focal seizures, 2 to 5 per week.")
    result = extract_seizure_frequency(letter)
    for mention in result.mentions:
        assert mention.evidence in letter.note_text, (
            f"Evidence not a substring: {mention.evidence!r}"
        )


def test_pipeline_empty_text_produces_no_mentions() -> None:
    letter = _make_letter("T004", "")
    result = extract_seizure_frequency(letter)
    assert result.mentions == ()


def test_pipeline_multiple_mentions_in_one_letter() -> None:
    text = "Focal seizures occur 3 per month. Absences occur 2 per week during illness."
    letter = _make_letter("T005", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert len(sf) >= 2


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


def test_pipeline_frequency_section_statement_rows() -> None:
    text = (
        "Seizure type and frequency: generalised tonic clonic seizures, "
        "1 since previous appointment\n"
        "Myoclonic jerks weekly\n"
        "Occasional absences.\n"
        "Current medication: Lamotrigine 150mg bd\n"
    )
    letter = _make_letter("T006C", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "generalised tonic clonic seizures"
        and m.attributes.get("NumberOfSeizures") == "1"
        and m.attributes.get("PointInTime") == "LastClinic"
        and m.attributes.get("TimeSince_or_TimeOfEvent") == "Since"
        for m in sf
    )
    assert any(
        m.text.lower() == "myoclonic jerks"
        and m.attributes.get("NumberOfSeizures") == "1"
        and m.attributes.get("TimePeriod") == "Week"
        for m in sf
    )
    assert any(
        m.text.lower() == "absences" and m.attributes.get("FrequencyChange") == "Infrequent"
        for m in sf
    )


def test_pipeline_statement_dated_range_rate() -> None:
    text = (
        "Although she did have a cluster of seizures in August, 2017 where "
        "she had 6-9 seizures every week."
    )
    letter = _make_letter("T006H", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "seizures"
        and m.attributes.get("LowerNumberOfSeizures") == "6"
        and m.attributes.get("UpperNumberOfSeizures") == "9"
        and m.attributes.get("TimePeriod") == "Week"
        and m.attributes.get("MonthDate") == "8"
        and m.attributes.get("YearDate") == "2017"
        and m.attributes.get("TimeSince_or_TimeOfEvent") == "During"
        for m in sf
    )


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


def test_pipeline_statement_normalizes_feburary_date() -> None:
    text = "However, since Feburary 6th he has not had any more seizures."
    letter = _make_letter("T006J", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "seizures"
        and m.attributes.get("NumberOfSeizures") == "0"
        and m.attributes.get("MonthDate") == "2"
        and m.attributes.get("DayDate") == "6"
        and m.attributes.get("TimeSince_or_TimeOfEvent") == "Since"
        for m in sf
    )


def test_pipeline_splits_rate_and_last_event_date_for_same_anchor() -> None:
    text = (
        "He has secondary generalised seizures, they happen about every year, "
        "his last one was on Christmas day 2009."
    )
    letter = _make_letter("T006B", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "secondary generalised seizures"
        and m.attributes.get("NumberOfSeizures") == "1"
        and m.attributes.get("TimePeriod") == "Year"
        and "MonthDate" not in m.attributes
        for m in sf
    )
    assert any(
        m.text.lower() == "secondary generalised seizures"
        and m.attributes.get("NumberOfSeizures") == "0"
        and m.attributes.get("DayDate") == "25"
        and m.attributes.get("MonthDate") == "12"
        and m.attributes.get("YearDate") == "2009"
        and m.attributes.get("TimeSince_or_TimeOfEvent") == "Since"
        for m in sf
    )


def test_pipeline_pronoun_rate_uses_previous_anchor() -> None:
    text = "He has partial motor seizures involving left arm twitching. He gets these every month."
    letter = _make_letter("T006D", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "partial motor seizures"
        and m.attributes.get("NumberOfSeizures") == "1"
        and m.attributes.get("NumberOfTimePeriods") == "1"
        and m.attributes.get("TimePeriod") == "Month"
        for m in sf
    )


def test_pipeline_pronoun_zero_duration_uses_previous_anchor() -> None:
    text = (
        "He used to have focal motor seizures without changes in awareness. "
        "He has not had a seizure like this for around two years now."
    )
    letter = _make_letter("T006E", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "focal motor seizures"
        and m.attributes.get("NumberOfSeizures") == "0"
        and m.attributes.get("NumberOfTimePeriods") == "2"
        and m.attributes.get("TimePeriod") == "Year"
        for m in sf
    )


def test_pipeline_projection_alias_for_singular_range_phrase() -> None:
    text = "Seizure type and frequency: Complex partial seizures 1-2 per month"
    letter = _make_letter("T006F", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "complex partial seizure"
        and m.attributes.get("LowerNumberOfSeizures") == "1"
        and m.attributes.get("UpperNumberOfSeizures") == "2"
        and m.attributes.get("CUI") == "C0149958"
        for m in sf
    )


def test_pipeline_projection_alias_for_change_only() -> None:
    text = (
        "His seizure frequency has reduced from about once a year to one seizure every two years."
    )
    letter = _make_letter("T006G", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]

    assert any(
        m.text.lower() == "seizure"
        and m.attributes.get("FrequencyChange") == "Decreased"
        and "TimePeriod" not in m.attributes
        for m in sf
    )


def test_pipeline_anchor_without_nearby_frequency_is_dropped() -> None:
    letter = _make_letter("T006", "Diagnosis: epilepsy with focal seizures.")
    result = extract_seizure_frequency(letter)
    assert result.mentions == ()


def test_pipeline_bare_nonzero_count_is_dropped() -> None:
    # "had 2 seizures" with no time frame is not a frequency statement (L255).
    letter = _make_letter("T007", "In his past history he had 2 seizures as a child.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert all(
        not (set(m.attributes) == {"NumberOfSeizures"} and m.attributes["NumberOfSeizures"] != "0")
        for m in sf
    )


def test_pipeline_count_with_date_is_kept() -> None:
    letter = _make_letter("T008", "He had 5 seizures in May.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert sf
    m = sf[0]
    assert m.attributes["NumberOfSeizures"] == "5"
    assert m.attributes["MonthDate"] == "5"
    assert m.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_pipeline_implied_count_on_bare_seizures_with_period() -> None:
    # Plural "seizures" with a period but no explicit count ⇒ NumberOfSeizures=2.
    letter = _make_letter("T009", "She has seizures since her last clinic appointment.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert sf
    assert any(
        m.attributes.get("NumberOfSeizures") == "2"
        and m.attributes.get("PointInTime") == "LastClinic"
        for m in sf
    )


def test_lexicon_has_16_distinct_cuis() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        SF_CUI_LEXICON,
    )

    assert len(SF_CUI_LEXICON) == 16
    assert len(set(SF_CUI_LEXICON)) == 16
