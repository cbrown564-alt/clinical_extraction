"""Invariant-focused tests for exectv2 deterministic sf rate rules."""

from __future__ import annotations

from importlib import import_module

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.candidates import (
    AnchorCandidate,
    AttributeExtraction,
    AttributeKind,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_count,
    normalize_unit,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    DEFAULT_ABLATION,
    ExtractionContext,
)

_sf_rules = import_module(
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction"
)
ADVERBIAL_RULE = _sf_rules.ADVERBIAL_RULE
ARTICLE_SEIZURE_COUNT_RULE = _sf_rules.ARTICLE_SEIZURE_COUNT_RULE
BETWEEN_RANGE_PER_PERIOD_RULE = _sf_rules.BETWEEN_RANGE_PER_PERIOD_RULE
CONTROL_PHRASE_RULE = _sf_rules.CONTROL_PHRASE_RULE
COUNT_IN_LAST_PERIOD_RULE = _sf_rules.COUNT_IN_LAST_PERIOD_RULE
COUNT_PER_FORTNIGHT_RULE = _sf_rules.COUNT_PER_FORTNIGHT_RULE
COUNT_PER_PERIOD_RULE = _sf_rules.COUNT_PER_PERIOD_RULE
EVERY_N_PERIODS_RULE = _sf_rules.EVERY_N_PERIODS_RULE
EVERY_PERIOD_RULE = _sf_rules.EVERY_PERIOD_RULE
HEADER_CONTINUATION_RATE_RULE = _sf_rules.HEADER_CONTINUATION_RATE_RULE
N_TIMES_PER_PERIOD_RULE = _sf_rules.N_TIMES_PER_PERIOD_RULE
NO_HAD_DURATION_RULE = _sf_rules.NO_HAD_DURATION_RULE
PERIOD_RANGE_RULE = _sf_rules.PERIOD_RANGE_RULE
RANGE_EVERY_PERIOD_RULE = _sf_rules.RANGE_EVERY_PERIOD_RULE
RANGE_OF_SEIZURE_TERMS_RULE = _sf_rules.RANGE_OF_SEIZURE_TERMS_RULE
RANGE_OVER_PERIOD_RULE = _sf_rules.RANGE_OVER_PERIOD_RULE
RANGE_PER_PERIOD_RULE = _sf_rules.RANGE_PER_PERIOD_RULE
SEVERAL_TIMES_PER_PERIOD_RULE = _sf_rules.SEVERAL_TIMES_PER_PERIOD_RULE
SF_BARE_RULE = _sf_rules.SF_BARE_RULE
SF_WITH_DURATION_RULE = _sf_rules.SF_WITH_DURATION_RULE


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


def test_normalize_count_digit_passthrough() -> None:
    assert normalize_count("3") == "3"
    assert normalize_count("15") == "15"


def test_normalize_count_word_conversion() -> None:
    assert normalize_count("twice") == "2"
    assert normalize_count("three") == "3"
    assert normalize_count("once") == "1"


def test_normalize_unit_canonical() -> None:
    assert normalize_unit("months") == "Month"
    assert normalize_unit("week") == "Week"
    assert normalize_unit("YEARS") == "Year"
    assert normalize_unit("day") == "Day"


def test_count_per_period_basic() -> None:
    results = _apply(COUNT_PER_PERIOD_RULE, "Seizure type and frequency: 3 per month.")
    assert len(results) == 1
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "3"
    assert c.attributes["TimePeriod"] == "Month"
    assert c.attributes["NumberOfTimePeriods"] == "1"
    assert "3 per month" in c.evidence


def test_count_per_period_word_number() -> None:
    results = _apply(COUNT_PER_PERIOD_RULE, "Two episodes per week are reported.")
    assert len(results) >= 1
    assert any(c.attributes["NumberOfSeizures"] == "2" for c in results)


def test_range_per_period() -> None:
    results = _apply(RANGE_PER_PERIOD_RULE, "Seizures: 2-5 per month.")
    assert len(results) == 1
    c = results[0]
    assert c.attributes["LowerNumberOfSeizures"] == "2"
    assert c.attributes["UpperNumberOfSeizures"] == "5"
    assert c.attributes["TimePeriod"] == "Month"


def test_range_of_seizure_terms() -> None:
    results = _apply(RANGE_OF_SEIZURE_TERMS_RULE, "In March she had 2 to 3 of her focal seizures.")
    assert len(results) == 1
    c = results[0]
    assert c.attributes["LowerNumberOfSeizures"] == "2"
    assert c.attributes["UpperNumberOfSeizures"] == "3"


def test_between_range_per_period() -> None:
    results = _apply(
        BETWEEN_RANGE_PER_PERIOD_RULE, "She is having between 3 and 4 seizures per week."
    )
    assert len(results) == 1
    c = results[0]
    assert c.attributes["LowerNumberOfSeizures"] == "3"
    assert c.attributes["UpperNumberOfSeizures"] == "4"
    assert c.attributes["NumberOfTimePeriods"] == "1"
    assert c.attributes["TimePeriod"] == "Week"


def test_n_times_per_period() -> None:
    results = _apply(N_TIMES_PER_PERIOD_RULE, "She has events 3 times per week.")
    assert len(results) == 1
    assert results[0].attributes["NumberOfSeizures"] == "3"
    assert results[0].attributes["TimePeriod"] == "Week"


def test_period_range_every_three_to_four_weeks() -> None:
    results = _apply(PERIOD_RANGE_RULE, "She has seizures every 3 to 4 weeks.")
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["LowerNumberOfTimePeriods"] == "3"
    assert attrs["UpperNumberOfTimePeriods"] == "4"
    assert attrs["TimePeriod"] == "Week"


def test_range_every_period() -> None:
    results = _apply(
        RANGE_EVERY_PERIOD_RULE, "Generalised tonic clonic seizures 1 to 2 every month."
    )
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["LowerNumberOfSeizures"] == "1"
    assert attrs["UpperNumberOfSeizures"] == "2"
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimePeriod"] == "Month"


def test_every_n_periods_digits() -> None:
    results = _apply(EVERY_N_PERIODS_RULE, "Focal seizures occur every 3 weeks.")
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert attrs["TimePeriod"] == "Week"


def test_every_n_periods_word_number() -> None:
    results = _apply(EVERY_N_PERIODS_RULE, "Convulsive seizure approximately every five years.")
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "5"
    assert attrs["TimePeriod"] == "Year"


def test_every_period_without_number() -> None:
    results = _apply(
        EVERY_PERIOD_RULE, "Secondary generalised seizures, they happen about every year."
    )
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimePeriod"] == "Year"


def test_count_per_fortnight() -> None:
    results = _apply(
        COUNT_PER_FORTNIGHT_RULE,
        "Focal seizures with altered awareness approximately 1 per fortnight.",
    )
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "2"
    assert attrs["TimePeriod"] == "Week"


def test_several_times_per_period() -> None:
    results = _apply(SEVERAL_TIMES_PER_PERIOD_RULE, "The absences happen several times a day.")
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "2"
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimePeriod"] == "Day"


def test_range_over_period() -> None:
    results = _apply(
        RANGE_OVER_PERIOD_RULE, "Last week she had around 10-15 of these seizures over 2 days."
    )
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["LowerNumberOfSeizures"] == "10"
    assert attrs["UpperNumberOfSeizures"] == "15"
    assert attrs["NumberOfTimePeriods"] == "2"
    assert attrs["TimePeriod"] == "Day"


def test_header_continuation_rate() -> None:
    text = "focal seizures with altered awareness (right arm movement)\n\t\t1 per week"
    results = _apply(HEADER_CONTINUATION_RATE_RULE, text)
    assert len(results) == 1
    attrs = results[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimePeriod"] == "Week"


def test_adverbial_daily() -> None:
    results = _apply(ADVERBIAL_RULE, "Focal onset seizures are now daily.")
    assert any(
        c.attributes["TimePeriod"] == "Day" and c.attributes["NumberOfSeizures"] == "1"
        for c in results
    )


def test_adverbial_twice_weekly() -> None:
    results = _apply(ADVERBIAL_RULE, "She reports seizures twice weekly.")
    assert any(
        c.attributes["NumberOfSeizures"] == "2" and c.attributes["TimePeriod"] == "Week"
        for c in results
    )


def test_adverbial_fortnightly() -> None:
    # A bare adverbial only fires in seizure context (gate against "daily
    # headaches" / "daily living" / medication-titration "daily").
    results = _apply(ADVERBIAL_RULE, "Her seizure clusters occur fortnightly.")
    assert any(
        c.attributes["TimePeriod"] == "Week" and c.attributes["NumberOfTimePeriods"] == "2"
        for c in results
    )


def test_adverbial_outside_seizure_context_suppressed() -> None:
    assert not _apply(ADVERBIAL_RULE, "She continues to get chronic daily headaches.")


def test_count_in_last_period_with_count() -> None:
    results = _apply(COUNT_IN_LAST_PERIOD_RULE, "He had 5 seizures in the last 3 months.")
    assert len(results) >= 1
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "5"
    assert c.attributes["NumberOfTimePeriods"] == "3"
    assert c.attributes["TimePeriod"] == "Month"
    # No TimeSince: "in the last N months" is a period, not a date/point-in-time
    # (guideline D9/Ex3 L231/L237). Emitting Since here was an over-application.
    assert "TimeSince_or_TimeOfEvent" not in c.attributes


def test_article_seizure_count() -> None:
    results = _apply(
        ARTICLE_SEIZURE_COUNT_RULE,
        "He had a generalised tonic clonic seizure last week.",
    )
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "1"


def test_sf_with_duration() -> None:
    results = _apply(SF_WITH_DURATION_RULE, "She has been seizure free for 3 months.")
    assert len(results) == 1
    c = results[0]
    assert c.attributes["NumberOfSeizures"] == "0"
    assert c.attributes["TimePeriod"] == "Month"
    assert c.attributes["NumberOfTimePeriods"] == "3"
    assert c.kind == AttributeKind.SEIZURE_FREE


def test_sf_with_duration_hyphenated() -> None:
    results = _apply(SF_WITH_DURATION_RULE, "Patient is seizure-free for 2 years.")
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"
    assert results[0].attributes["TimePeriod"] == "Year"


def test_sf_with_duration_suppresses_driving_period() -> None:
    results = _apply(
        SF_WITH_DURATION_RULE,
        "She should refrain from driving until she has been seizure free for 12 months.",
    )
    assert not results


def test_sf_with_duration_suppresses_prior_interval() -> None:
    results = _apply(
        SF_WITH_DURATION_RULE,
        "Before the seizure she had been seizure free for 3 years.",
    )
    assert not results


def test_no_had_duration_specific_type() -> None:
    results = _apply(
        NO_HAD_DURATION_RULE,
        "He has not had one of his bigger focal to bilateral convulsive seizure "
        "for three years now.",
    )
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"
    assert results[0].attributes["NumberOfTimePeriods"] == "3"
    assert results[0].attributes["TimePeriod"] == "Year"


def test_no_happened_duration_pronoun() -> None:
    results = _apply(
        NO_HAD_DURATION_RULE,
        "He also gets focal to bilateral convulsive seizures and these haven't "
        "happened for several years now.",
    )
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"
    assert results[0].attributes["TimePeriod"] == "Year"


def test_sf_bare_basic() -> None:
    results = _apply(SF_BARE_RULE, "He is currently seizure free.")
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"


def test_control_phrase_not_had_any_further_seizures() -> None:
    results = _apply(CONTROL_PHRASE_RULE, "She has not had any further seizures.")
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"
