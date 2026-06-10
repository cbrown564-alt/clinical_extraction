"""Unit tests for the ExECTv2 deterministic SeizureFrequency extractor.

Tests are at four levels:
  1. Normalizer / attribute-extraction rule unit tests.
  2. Anchor rule unit tests.
  3. Overlap + association unit tests.
  4. Pipeline smoke tests + registry validation.
"""
from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.association import (
    associate_attributes_to_anchors,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.anchor import (
    ANCHOR_RULES,
    SEIZURE_FREE_ANCHOR_RULE,
    SEIZURE_TYPE_ANCHOR_RULE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.rate import (
    ADVERBIAL_RULE,
    COUNT_IN_LAST_PERIOD_RULE,
    COUNT_PER_PERIOD_RULE,
    N_TIMES_PER_PERIOD_RULE,
    RANGE_PER_PERIOD_RULE,
    RATE_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
    SF_BARE_RULE,
    SF_WITH_DURATION_RULE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.temporal import (
    DATE_MY_RULE,
    LAST_SEIZURE_DATE_RULE,
    PIT_SINCE_RULE,
    TEMPORAL_RULES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Attribute-extraction rules (rate / seizure-free / change)
# ---------------------------------------------------------------------------


def _apply(spec, text: str) -> list[AttributeExtraction]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AttributeExtraction)]


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


def test_n_times_per_period() -> None:
    results = _apply(N_TIMES_PER_PERIOD_RULE, "She has events 3 times per week.")
    assert len(results) == 1
    assert results[0].attributes["NumberOfSeizures"] == "3"
    assert results[0].attributes["TimePeriod"] == "Week"


def test_adverbial_daily() -> None:
    results = _apply(ADVERBIAL_RULE, "Focal onset seizures are now daily.")
    assert any(c.attributes["TimePeriod"] == "Day" and c.attributes["NumberOfSeizures"] == "1" for c in results)


def test_adverbial_twice_weekly() -> None:
    results = _apply(ADVERBIAL_RULE, "She reports seizures twice weekly.")
    assert any(c.attributes["NumberOfSeizures"] == "2" and c.attributes["TimePeriod"] == "Week" for c in results)


def test_adverbial_fortnightly() -> None:
    # A bare adverbial only fires in seizure context (gate against "daily
    # headaches" / "daily living" / medication-titration "daily").
    results = _apply(ADVERBIAL_RULE, "Her seizure clusters occur fortnightly.")
    assert any(c.attributes["TimePeriod"] == "Week" and c.attributes["NumberOfTimePeriods"] == "2" for c in results)


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


def test_sf_bare_basic() -> None:
    results = _apply(SF_BARE_RULE, "He is currently seizure free.")
    assert results
    assert results[0].attributes["NumberOfSeizures"] == "0"


def test_sf_bare_suppresses_required_period() -> None:
    results = _apply(SF_BARE_RULE, "The required seizure-free period is 12 months.")
    assert not results


def test_sf_bare_suppresses_driving_interval() -> None:
    results = _apply(SF_BARE_RULE, "The seizure-free interval before driving must be observed.")
    assert not results


def test_change_decreased() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import DECREASED_RULE
    results = _apply(DECREASED_RULE, "Seizure frequency has decreased since starting medication.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Decreased"


def test_change_increased() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import INCREASED_RULE
    results = _apply(INCREASED_RULE, "Seizure frequency has increased over the past month.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Increased"


def test_change_same() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import SAME_RULE
    results = _apply(SAME_RULE, "Seizure frequency remains unchanged.")
    assert results
    assert results[0].attributes["FrequencyChange"] == "Same"


# ---------------------------------------------------------------------------
# Temporal-anchoring rules
# ---------------------------------------------------------------------------


def test_pit_since_last_clinic() -> None:
    results = _apply(PIT_SINCE_RULE, "She had two seizures since last being seen.")
    assert results
    assert results[0].attributes["PointInTime"] == "LastClinic"
    assert results[0].attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_pit_since_drug_change() -> None:
    results = _apply(PIT_SINCE_RULE, "Since starting lamotrigine his seizure frequency improved.")
    assert results
    assert results[0].attributes["PointInTime"] == "DrugChange"


def test_date_month_year_during() -> None:
    results = _apply(DATE_MY_RULE, "He had 3 seizures in March 2014.")
    assert results
    c = results[0]
    assert c.attributes["MonthDate"] == "3"
    assert c.attributes["YearDate"] == "2014"
    assert c.attributes["TimeSince_or_TimeOfEvent"] == "During"


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


# ---------------------------------------------------------------------------
# Anchor rules
# ---------------------------------------------------------------------------


def _apply_anchors(spec, text: str) -> list[AnchorCandidate]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AnchorCandidate)]


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


def test_anchor_bare_seizures() -> None:
    results = _apply_anchors(SEIZURE_TYPE_ANCHOR_RULE, "No change in seizures over the last year.")
    assert any(c.text.lower() == "seizures" for c in results)


def test_anchor_seizure_free_phrase() -> None:
    results = _apply_anchors(SEIZURE_FREE_ANCHOR_RULE, "She has been seizure-free for 7 months.")
    assert any("seizure-free" == c.text.lower() or "seizure free" == c.text.lower() for c in results)


# ---------------------------------------------------------------------------
# Overlap resolution
# ---------------------------------------------------------------------------


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
        attributes={"LowerNumberOfSeizures": "2", "UpperNumberOfSeizures": "5", "TimePeriod": "Month", "NumberOfTimePeriods": "1"},
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
    a = AttributeExtraction(evidence="3 per month", span=(0, 11), attributes={"NumberOfSeizures": "3", "TimePeriod": "Month"})
    b = AttributeExtraction(evidence="2 per week", span=(20, 30), attributes={"NumberOfSeizures": "2", "TimePeriod": "Week"})
    resolved = resolve_overlapping_attributes([a, b])
    assert len(resolved) == 2


# ---------------------------------------------------------------------------
# Association
# ---------------------------------------------------------------------------


def test_association_merges_nearest_attribute() -> None:
    anchor = AnchorCandidate(text="focal seizures", evidence="focal seizures", span=(0, 14), rule_id="a")
    other_anchor = AnchorCandidate(text="absences", evidence="absences", span=(100, 108), rule_id="b")
    attr = AttributeExtraction(evidence="2 per month", span=(15, 26), attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"})

    pairs = associate_attributes_to_anchors([anchor, other_anchor], [attr])
    assert len(pairs) == 1
    matched_anchor, attrs = pairs[0]
    assert matched_anchor is anchor
    assert attrs["NumberOfSeizures"] == "2"


def test_association_drops_anchors_without_attributes() -> None:
    anchor_with = AnchorCandidate(text="focal seizures", evidence="focal seizures", span=(0, 14), rule_id="a")
    anchor_without = AnchorCandidate(text="absences", evidence="absences", span=(100, 108), rule_id="b")
    attr = AttributeExtraction(evidence="2 per month", span=(15, 26), attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"})

    pairs = associate_attributes_to_anchors([anchor_with, anchor_without], [attr])
    assert len(pairs) == 1
    assert pairs[0][0] is anchor_with


def test_association_no_anchors_returns_empty() -> None:
    attr = AttributeExtraction(evidence="2 per month", span=(15, 26), attributes={"NumberOfSeizures": "2"})
    assert associate_attributes_to_anchors([], [attr]) == []


# ---------------------------------------------------------------------------
# Pipeline smoke tests
# ---------------------------------------------------------------------------


def _make_letter(letter_id: str, note_text: str) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text)


def test_pipeline_produces_predicted_letter() -> None:
    letter = _make_letter(
        "T001",
        "Seizure type and frequency: focal seizures with loss of awareness approximately 3 per month.",
    )
    result = extract_seizure_frequency(letter)
    assert result.letter_id == "T001"
    sf_mentions = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert sf_mentions
    assert sf_mentions[0].text.lower() == "focal seizures with loss of awareness"
    assert sf_mentions[0].attributes["NumberOfSeizures"] == "3"


def test_pipeline_sf_mention_attributes() -> None:
    letter = _make_letter("T002", "She has been seizure free for 6 months.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
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
    text = (
        "Focal seizures occur 3 per month. "
        "Absences occur 2 per week during illness."
    )
    letter = _make_letter("T005", text)
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert len(sf) >= 2


def test_pipeline_anchor_without_nearby_frequency_is_dropped() -> None:
    letter = _make_letter("T006", "Diagnosis: epilepsy with focal seizures.")
    result = extract_seizure_frequency(letter)
    assert result.mentions == ()


def test_pipeline_bare_nonzero_count_is_dropped() -> None:
    # "had 2 seizures" with no time frame is not a frequency statement (L255).
    letter = _make_letter("T007", "In his past history he had 2 seizures as a child.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert all(
        not (set(m.attributes) == {"NumberOfSeizures"} and m.attributes["NumberOfSeizures"] != "0")
        for m in sf
    )


def test_pipeline_count_with_date_is_kept() -> None:
    letter = _make_letter("T008", "He had 5 seizures in May.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert sf
    m = sf[0]
    assert m.attributes["NumberOfSeizures"] == "5"
    assert m.attributes["MonthDate"] == "5"
    assert m.attributes["TimeSince_or_TimeOfEvent"] == "During"


def test_pipeline_implied_count_on_bare_seizures_with_period() -> None:
    # Plural "seizures" with a period but no explicit count ⇒ NumberOfSeizures=2.
    letter = _make_letter("T009", "She has seizures since her last clinic appointment.")
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert sf
    assert any(
        m.attributes.get("NumberOfSeizures") == "2"
        and m.attributes.get("PointInTime") == "LastClinic"
        for m in sf
    )


# ---------------------------------------------------------------------------
# Phrase → CUI lexicon
# ---------------------------------------------------------------------------


def test_lexicon_has_16_distinct_cuis() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        SF_CUI_LEXICON,
    )

    assert len(SF_CUI_LEXICON) == 16
    assert len(set(SF_CUI_LEXICON)) == 16


def test_lexicon_canonical_phrases_map_to_their_cui() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    assert assign_cui("generalised tonic clonic seizures") == "C0494475"
    assert assign_cui("focal seizures with altered awareness") == "C0270834"
    assert assign_cui("secondary generalised seizures") == "C0270838"
    assert assign_cui("myoclonic jerks") == "C0027066"
    assert assign_cui("seizure free") == "C1299590"
    assert assign_cui("absences") == "C0563606"


def test_lexicon_normalizes_surface_variation() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    # Hyphens, case, and "loss of"/"altered" awareness wording all resolve.
    assert assign_cui("Generalised-Tonic-Clonic-Seizures") == "C0494475"
    assert assign_cui("focal seizures with loss of awareness") == "C0270834"


def test_lexicon_collisions_resolve_to_dominant_cui() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    # Bare truncation tokens resolve to the dominant gold CUI, not seizure-free /
    # focal-motor.
    assert assign_cui("seizure") == "C0036572"
    assert assign_cui("seizures") == "C0036572"
    assert assign_cui("focal") == "C0877017"


def test_lexicon_unknown_phrase_returns_none() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    assert assign_cui("photosensitive episodes") is None
    assert assign_cui("") is None


def test_pipeline_emits_cui_for_known_seizure_type() -> None:
    letter = _make_letter(
        "T010",
        "Seizure type and frequency: generalised tonic clonic seizures twice weekly.",
    )
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY]
    assert sf
    assert any(m.attributes.get("CUI") == "C0494475" for m in sf)


# ---------------------------------------------------------------------------
# Registry validation
# ---------------------------------------------------------------------------


def test_no_duplicate_rule_ids() -> None:
    all_rules = ANCHOR_RULES + RATE_RULES + SEIZURE_FREE_RULES + CHANGE_RULES + TEMPORAL_RULES
    ids = [spec.rule_id for spec in all_rules]
    assert len(ids) == len(set(ids)), f"Duplicate rule_ids: {[x for x in ids if ids.count(x) > 1]}"


def test_all_rules_have_examples() -> None:
    all_rules = ANCHOR_RULES + RATE_RULES + SEIZURE_FREE_RULES + CHANGE_RULES + TEMPORAL_RULES
    missing = [spec.rule_id for spec in all_rules if not spec.examples]
    assert not missing, f"Rules without examples: {missing}"


# ---------------------------------------------------------------------------
# Dev-split corpus baseline (pinned) — Phase 2 milestone
# ---------------------------------------------------------------------------
#
# Pinned per-item F1 of the deterministic SF extractor on the 140-letter dev
# split, under the three scoring configs the milestone runner reports. These
# are a DELIBERATELY pinned baseline (Gan 2026 pipeline_v1 discipline): a
# regression below the floor fails CI; a gain above the ceiling also fails, as
# a prompt to re-pin and record the improvement in the error-analysis artifact.
#
# Captured 2026-06-10 (Phase 2 completion batch) on top of the earlier
# guideline-alignment + temporal-family + CUI-lexicon work. This batch added:
# the awareness-suffix fix ("with altered awareness", no "of"); range rules
# accepting a seizure noun / "times" before "per"; dropping TimeSince from
# count_in_last_period (D9); negation-aware implied count (negated ⇒ 0); a
# Christmas⇒December date rule; medication-dose and adverbial seizure-context
# gates; a non-clinical/history/driving zero gate; flexible seizure-free
# duration and "after"/drug-stop point-in-time triggers; "the beginning of
# <month>" date filler; and — the largest precision lever — a same-sentence,
# bounded-gap association rule (drop an extraction with no nearby anchor instead
# of gluing it onto a distant one). Per-statement emission (D8) was implemented
# and measured net-negative, so reverted (see association.py).
#   phrase_only    per-item F1 = 0.382  (per-letter 0.604)
#   sf_semantic    per-item F1 = 0.272  (per-letter 0.482; ignores CUI/CUIPhrase/Certainty/Negation)
#   sf_benchmark   per-item F1 = 0.272  (per-letter 0.482; keeps CUI, == sf_semantic)
# Trajectory across the two 2026-06-10 batches: sf_semantic per-item
# 0.156→0.272 (+74%), per-letter 0.313→0.482; per-letter precision 0.479→0.868.
# Benchmark SF F1 to beat ~0.56 (the published system's hardest entity; its
# overall F1 across the nine entities is >0.90). The remaining recall ceiling is
# dominated by offset-drift–corrupted gold phrases (~20% of mentions, un-winnable
# on exact text) plus singular/plural phrase mismatches and a hard tail.
# See docs/plans/exectv2/02_rules_based_architecture.md for the gap analysis,
# docs/research/exectv2_sf_error_analysis_2026-06-10.md for the row-level audit,
# and docs/research/exectv2_sf_guideline_alignment_2026-06-10.md for the clauses.

_PINNED_DEV_PER_ITEM_F1 = {
    "phrase_only": 0.382,
    "sf_semantic": 0.272,
    "sf_benchmark": 0.272,
}
_F1_BAND = 0.02


def test_dev_split_baseline_pinned() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
        to_exect_letter,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
        run_on_letters,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        PHRASE_ONLY,
        SF_BENCHMARK,
        SF_SEMANTIC,
        score_entity,
    )

    gold = load_letters_for_split("dev")
    preds = run_on_letters(gold)
    pred_exect = [
        to_exect_letter(p, note_text=g.note_text) for p, g in zip(preds, gold)
    ]

    configs = {
        "phrase_only": PHRASE_ONLY,
        "sf_semantic": SF_SEMANTIC,
        "sf_benchmark": SF_BENCHMARK,
    }
    for name, cfg in configs.items():
        f1 = score_entity(gold, pred_exect, SEIZURE_FREQUENCY, cfg).per_item.f1
        pinned = _PINNED_DEV_PER_ITEM_F1[name]
        assert pinned - _F1_BAND <= f1 <= pinned + _F1_BAND, (
            f"dev {name} per-item F1={f1:.3f} drifted from pinned {pinned:.3f} "
            f"(±{_F1_BAND}). If this is a deliberate improvement, re-pin "
            f"_PINNED_DEV_PER_ITEM_F1 and record it in the error-analysis artifact."
        )
