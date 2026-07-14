"""Invariant-focused tests for exectv2 deterministic sf temporal rules."""

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
CONTROL_PHRASE_RULE = _sf_rules.CONTROL_PHRASE_RULE
DATE_MONTH_RULE = _sf_rules.DATE_MONTH_RULE
DATE_MY_RULE = _sf_rules.DATE_MY_RULE
DECREASED_RULE = _sf_rules.DECREASED_RULE
INCREASED_RULE = _sf_rules.INCREASED_RULE
PIT_SINCE_RULE = _sf_rules.PIT_SINCE_RULE
PIT_STANDALONE_DURING_RULE = _sf_rules.PIT_STANDALONE_DURING_RULE
SAME_RULE = _sf_rules.SAME_RULE
SF_BARE_RULE = _sf_rules.SF_BARE_RULE


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


def test_control_phrase_under_control() -> None:
    results = _apply(CONTROL_PHRASE_RULE, "The focal seizures are completely under control.")
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"


def test_sf_bare_suppresses_required_period() -> None:
    results = _apply(SF_BARE_RULE, "The required seizure-free period is 12 months.")
    assert not results


def test_sf_bare_suppresses_driving_interval() -> None:
    results = _apply(SF_BARE_RULE, "The seizure-free interval before driving must be observed.")
    assert not results


def test_change_decreased() -> None:
    results = _apply(DECREASED_RULE, "Seizure frequency has decreased since starting medication.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Decreased"


def test_change_increased() -> None:
    results = _apply(INCREASED_RULE, "Seizure frequency has increased over the past month.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Increased"


def test_change_same() -> None:
    results = _apply(SAME_RULE, "Seizure frequency remains unchanged.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Same"


def test_pit_since_last_clinic() -> None:
    results = _apply(PIT_SINCE_RULE, "She had two seizures since last being seen.")
    assert results
    assert results[0].attributes["PointInTime"] == "LastClinic"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_pit_since_previous_phone_call() -> None:
    results = _apply(
        PIT_SINCE_RULE, "Since my previous phone call she has had one focal motor seizure."
    )
    assert results
    assert results[0].attributes["PointInTime"] == "LastClinic"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_pit_since_drug_change() -> None:
    results = _apply(PIT_SINCE_RULE, "Since starting lamotrigine his seizure frequency improved.")
    assert results
    assert results[0].attributes["PointInTime"] == "DrugChange"


def test_pit_since_dose_increase_drug_change() -> None:
    results = _apply(PIT_SINCE_RULE, "She has had no seizures since increasing levetiracetam.")
    assert results
    assert results[0].attributes["PointInTime"] == "DrugChange"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_pit_standalone_last_week_during() -> None:
    results = _apply(
        PIT_STANDALONE_DURING_RULE,
        "He had a generalised tonic clonic seizure last week.",
    )
    assert results
    assert results[0].attributes["PointInTime"] == "Last_Week"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_pit_standalone_last_week_before_anchor() -> None:
    results = _apply(
        PIT_STANDALONE_DURING_RULE,
        "He forgot carbamazepine last week and had a generalised tonic clonic seizure.",
    )
    assert results
    assert results[0].attributes["PointInTime"] == "Last_Week"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_date_month_year_during() -> None:
    results = _apply(DATE_MY_RULE, "He had 3 seizures in March 2014.")
    assert results
    c = results[0]
    assert c.attributes["MonthDate"] == "3"
    assert c.attributes["YearDate"] == "2014"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_date_month_year_with_comma() -> None:
    results = _apply(DATE_MY_RULE, "She had a cluster of seizures in August, 2017.")
    assert results
    c = results[0]
    assert c.attributes["MonthDate"] == "8"
    assert c.attributes["YearDate"] == "2017"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_date_month_forward_seizure_context() -> None:
    results = _apply(DATE_MONTH_RULE, "In March she had 2 to 3 of her focal seizures.")
    assert results
    assert results[0].attributes["MonthDate"] == "3"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_date_month_since_last_month_name() -> None:
    results = _apply(
        DATE_MONTH_RULE, "Since last October she had 4 generalised tonic clonic seizures."
    )
    assert results
    assert results[0].attributes["MonthDate"] == "10"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "Since"
