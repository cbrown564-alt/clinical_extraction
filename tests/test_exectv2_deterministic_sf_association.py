"""Invariant-focused tests for exectv2 deterministic sf association."""

from __future__ import annotations

from importlib import import_module

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.candidates import (
    AnchorCandidate,
    AttributeExtraction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    DEFAULT_ABLATION,
    ExtractionContext,
)

_sf_rules = import_module(
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction"
)
DATE_MY_RULE = _sf_rules.DATE_MY_RULE
LAST_EVENT_AGO_RULE = _sf_rules.LAST_EVENT_AGO_RULE
LAST_EVENT_DATE_RULE = _sf_rules.LAST_EVENT_DATE_RULE
LAST_SEIZURE_DATE_RULE = _sf_rules.LAST_SEIZURE_DATE_RULE
RATE_RULES = _sf_rules.RATE_RULES
SEIZURE_FREE_RULES = _sf_rules.SEIZURE_FREE_RULES
SEIZURE_TERM_MONTH_YEAR_RULE = _sf_rules.SEIZURE_TERM_MONTH_YEAR_RULE
SEIZURE_TERM_YEAR_RULE = _sf_rules.SEIZURE_TERM_YEAR_RULE
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


def test_seizure_term_year_with_explicit_count() -> None:
    results = _apply(SEIZURE_TERM_YEAR_RULE, "2 generalised tonic clonic seizures 2014.")
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "2"
    assert c.attributes["YearDate"] == "2014"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_seizure_term_year_default_count() -> None:
    results = _apply(SEIZURE_TERM_YEAR_RULE, "absence like seizures 2014.")
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "1"
    assert c.attributes["YearDate"] == "2014"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_seizure_term_month_year_default_count() -> None:
    results = _apply(
        SEIZURE_TERM_MONTH_YEAR_RULE,
        "Focal to bilateral convulsive seizures August 2014.",
    )
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "1"
    assert c.attributes["MonthDate"] == "8"
    assert c.attributes["YearDate"] == "2014"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_seizure_term_month_year_does_not_rewrite_last_event() -> None:
    results = _apply(
        SEIZURE_TERM_MONTH_YEAR_RULE,
        "Generalised tonic clonic seizure-last event July 2016. Previous event December 2015.",
    )
    assert results == []


def test_date_outside_seizure_context_suppressed() -> None:
    # No seizure noun nearby → not a SeizureFrequency date.
    results = _apply(DATE_MY_RULE, "He was diagnosed with epilepsy in March 2014.")
    assert not results


def test_last_seizure_date_zero_since() -> None:
    results = _apply(LAST_SEIZURE_DATE_RULE, "Her last seizure was in September 2012.")
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["MonthDate"] == "9"
    assert c.attributes["YearDate"] == "2012"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_last_event_date_zero_since() -> None:
    results = _apply(
        LAST_EVENT_DATE_RULE, "Focal to bilateral convulsive seizures, last event October 2019."
    )
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["MonthDate"] == "10"
    assert c.attributes["YearDate"] == "2019"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_last_event_christmas_year_zero_since() -> None:
    results = _apply(LAST_EVENT_DATE_RULE, "Convulsive seizures, last event around Christmas 2017.")
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["MonthDate"] == "12"
    assert c.attributes["YearDate"] == "2017"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_last_one_christmas_day_year_zero_since() -> None:
    results = _apply(
        LAST_EVENT_DATE_RULE,
        "Secondary generalised seizures, his last one was on Christmas day 2009.",
    )
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["DayDate"] == "25"
    assert c.attributes["MonthDate"] == "12"
    assert c.attributes["YearDate"] == "2009"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_last_event_ago_zero_period() -> None:
    results = _apply(
        LAST_EVENT_AGO_RULE, "Focal seizures with altered awareness, last event 3 years ago."
    )
    assert results
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["NumberOfTimePeriods"] == "3"
    assert c.attributes["TimePeriod"] == "Year"


def test_no_default_negation_attribute() -> None:
    """Gold SF mentions almost never carry an explicit Negation key (implicitly
    Affirmed), so attribute extractors must not add one by default."""
    texts = [
        "3 per month",
        "seizure free for 6 months",
        "daily",
    ]
    all_rules = RATE_RULES + SEIZURE_FREE_RULES
    for text in texts:
        ctx = ExtractionContext(text=text)
        for spec in all_rules:
            for c in spec.apply(ctx, DEFAULT_ABLATION):
                if isinstance(c, AttributeExtraction):
                    assert "Negation" not in c.attributes, (
                        f"Rule {spec.rule_id!r} should not default Negation"
                    )


def test_anchor_focal_seizures_with_loss_of_awareness() -> None:
    results = _apply_anchors(
        SEIZURE_TYPE_ANCHOR_RULE,
        "focal seizures with loss of awareness approximately 2 to 3 per month.",
    )
    assert any(c.text.lower() == "focal seizures with loss of awareness" for c in results)


def test_anchor_generalised_tonic_clonic_seizures() -> None:
    results = _apply_anchors(
        SEIZURE_TYPE_ANCHOR_RULE,
        "She has generalised tonic clonic seizures occurring twice weekly.",
    )
    assert any("generalised tonic clonic seizures" in c.text.lower() for c in results)


def test_anchor_secondary_generalised_seizures() -> None:
    results = _apply_anchors(
        SEIZURE_TYPE_ANCHOR_RULE,
        "Secondary generalised seizures since the last clinic appointment.",
    )
    assert any("secondary generalised seizures" in c.text.lower() for c in results)


def test_anchor_myoclonic_jerks() -> None:
    results = _apply_anchors(SEIZURE_TYPE_ANCHOR_RULE, "Myoclonic jerks have become more frequent.")
    assert any("myoclonic jerks" in c.text.lower() for c in results)


def test_anchor_motor_and_dyscognitive_phrases() -> None:
    text = (
        "Partial motor seizures monthly. Focal motor seizures weekly. "
        "Dyscognitive seizures are frequent."
    )
    results = _apply_anchors(SEIZURE_TYPE_ANCHOR_RULE, text)
    assert [r.text.lower() for r in results] == [
        "partial motor seizures",
        "focal motor seizures",
        "dyscognitive seizures",
    ]
