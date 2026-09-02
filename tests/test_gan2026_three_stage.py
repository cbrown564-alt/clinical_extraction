"""Phase A three-stage instrumentation tests for the Gan rules-only program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md
The three-stage runner must be score-neutral to the living ``run_record``
(gate A1), tag relocated select drops without narrowing the find
ledger, and implement the predeclared document-order stop policy.
"""

from __future__ import annotations

import re

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_extraction import (  # noqa: E501
    _extract_candidates,
    extract_wide_candidates,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_text import (
    normalize_note_text,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.recall_first import (
    ALL_PROVISIONAL_CLASSES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    rules as gan_rules,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (
    GanThreeStageConfig,
    LedgerDropReason,
    collect_exclusion_records,
    phase_c_candidate_config,
    run_record_three_stage,
    tag_ledger_drops,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def _record(note_text: str) -> GanRecord:
    return GanRecord(
        source_row_index=1,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


IDENTITY_NOTES = (
    # Cluster spacing beats incidental daily mention (existing pipeline fixture).
    "His seizures typically occur in clusters, generally spaced four days "
    "apart, though brief periods of daily seizures have been reported.",
    # Sparse parenthetical month lists (existing pipeline fixture).
    "Clinic Date: 21 April 2011. He had a cluster of three seizures in "
    "Dec (short, not full convulsions, fluctuating awareness, "
    "self-terminating). In Feb he had 7 nocturnal seizures, and in Apr "
    "a single tonic seizure was recorded during respite care.",
    # Competing rates (existing pipeline fixture).
    "Over the past year seizure control has been relatively stable. "
    "She experiences two generalised tonic-clonic seizures every "
    "2 months. Absence seizures remain infrequent, usually no more than "
    "twice weekly, and myoclonic jerks are reported only occasionally.",
    # Unknown trigger plus direct rate.
    "Frequency unclear at this stage. He still has focal seizures four "
    "times per day.",
    # Seizure-free assertion.
    "She remains free of seizures for two years on the current regimen.",
    # No seizure-frequency reference at all.
    "Routine follow-up for medication review. No concerns were raised.",
)


def test_three_stage_select_stop_is_identical_to_run_record() -> None:
    config = PipelineConfiguration(architecture="rules")
    for note_text in IDENTITY_NOTES:
        record = _record(note_text)
        comparator = gan_rules.run_record(record, config)
        candidate = run_record_three_stage(record)
        assert candidate.stops.select_label == comparator.output.final_value
        assert candidate.final_selection.evidence == comparator.output.evidence


def test_tagged_pool_equals_comparator_post_prune_candidates() -> None:
    # Gate A2 mechanics: the surviving competition pool must be exactly the
    # comparator's dedupe-then-prune output on the same wide ledger.
    for note_text in IDENTITY_NOTES:
        wide = extract_wide_candidates(note_text)
        pool, _ = tag_ledger_drops(wide, normalize_note_text(note_text))
        assert list(pool) == _extract_candidates(note_text)


def test_tag_ledger_drops_marks_duplicates_and_keeps_first() -> None:
    duplicate = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="4 per day",
        evidence="four times per day",
    )
    wide = [duplicate, duplicate]
    pool, reasons = tag_ledger_drops(wide, "four times per day")
    assert len(pool) == 1
    assert reasons == {1: LedgerDropReason.DUPLICATE}


def test_tag_ledger_drops_marks_historical_rate_when_current_exists() -> None:
    text = "Previously four times per day. Now stabilised at once per month."
    historical = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="4 per day",
        evidence="four times per day",
    )
    current = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="1 per month",
        evidence="once per month",
    )
    pool, reasons = tag_ledger_drops([historical, current], text)
    assert list(pool) == [current]
    assert reasons == {0: LedgerDropReason.HISTORICAL_RATE}


def test_tag_ledger_drops_marks_contained_monthly_list_fragment() -> None:
    container_evidence = (
        "He had a cluster of three seizures in Dec and in Feb he had 7 "
        "nocturnal seizures"
    )
    fragment_evidence = "in Feb he had 7 nocturnal seizures"
    container = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="10 per 3 month",
        evidence=container_evidence,
    )
    fragment = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="7 per month",
        evidence=fragment_evidence,
    )
    pool, reasons = tag_ledger_drops([container, fragment], container_evidence + ".")
    assert list(pool) == [container]
    assert reasons == {1: LedgerDropReason.CONTAINED_FRAGMENT}


def test_find_stop_is_document_order_first_over_wide_ledger() -> None:
    record = _record(
        "Frequency unclear at this stage. He still has focal seizures four "
        "times per day."
    )
    result = run_record_three_stage(record)
    # Document order: the unknown trigger precedes the rate mention, so the
    # find and encode stops read "unknown" while Select prefers the rate.
    assert result.stops.find_label == "unknown"
    assert result.stops.encode_label == "unknown"
    assert result.stops.select_label == "4 per day"


def test_empty_note_reports_no_reference_at_every_stop() -> None:
    record = _record("Routine follow-up for medication review.")
    result = run_record_three_stage(record)
    assert result.stops.find_label == "no seizure frequency reference"
    assert result.stops.encode_label == "no seizure frequency reference"
    assert result.stops.select_label == "no seizure frequency reference"
    assert len(result.ledger) == 1
    assert result.ledger[0].is_fallback


def test_dropped_entries_stay_visible_in_the_ledger() -> None:
    record = _record(
        "His seizures typically occur in clusters, generally spaced four days "
        "apart, though brief periods of daily seizures have been reported."
    )
    result = run_record_three_stage(record)
    surviving = [entry for entry in result.ledger if entry.drop_reason is None]
    assert len(result.ledger) >= len(surviving)
    assert all(entry.evidence for entry in result.ledger)


def test_collect_exclusion_records_reports_suppressed_matches() -> None:
    def _always_exclude(match: re.Match[str], context: object) -> bool:
        return True

    spec = RuleSpec(
        rule_id="test.always_excluded_rate",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Test-only spec whose matches are always excluded.",
        pattern=re.compile(r"twice daily", re.IGNORECASE),
        build=lambda match, context: None,
        exclude=(_always_exclude,),
        examples=(RuleExample(text="twice daily", expected_label=None),),
    )
    records = collect_exclusion_records(
        "Levetiracetam is taken twice daily with food.",
        AblationConfig(),
        specs=(spec,),
    )
    assert len(records) == 1
    assert records[0].rule_id == "test.always_excluded_rate"
    assert records[0].matched_text.lower() == "twice daily"

    disabled = collect_exclusion_records(
        "Levetiracetam is taken twice daily with food.",
        AblationConfig(disabled_rule_ids=frozenset({"test.always_excluded_rate"})),
        specs=(spec,),
    )
    assert disabled == ()


def test_provisional_classes_leave_select_stop_identical() -> None:
    config = GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES)
    comparator_config = PipelineConfiguration(architecture="rules")
    notes = IDENTITY_NOTES + (
        "Seizures after alcohol intake were described; control otherwise stable.",
        "Electrographic seizures frequent on EEG (~9/h) during admission.",
    )
    for note_text in notes:
        record = _record(note_text)
        comparator = gan_rules.run_record(record, comparator_config)
        candidate = run_record_three_stage(record, config)
        assert candidate.stops.select_label == comparator.output.final_value
        assert candidate.final_selection.evidence == comparator.output.evidence


def test_provisional_candidates_are_tagged_and_gated_not_competed() -> None:
    record = _record(
        "Seizures after alcohol intake were described; control otherwise stable."
    )
    result = run_record_three_stage(
        record, GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES)
    )
    provisional = [
        entry for entry in result.ledger if entry.provisional_class is not None
    ]
    assert provisional
    assert all(
        entry.drop_reason is LedgerDropReason.PROVISIONAL_UNSUPPORTED
        for entry in provisional
    )
    assert any(
        entry.provisional_class == "provisional.trigger_conditioned_unknown"
        and entry.normalized_label == "unknown"
        for entry in provisional
    )
    # Default config produces no provisional entries.
    default_result = run_record_three_stage(record)
    assert all(
        entry.provisional_class is None for entry in default_result.ledger
    )


def test_electrographic_producer_emits_multiple_per_day() -> None:
    record = _record("Electrographic seizures frequent on EEG (~ten/h) overnight.")
    result = run_record_three_stage(
        record, GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES)
    )
    assert any(
        entry.provisional_class == "provisional.electrographic_hourly_rate"
        and entry.normalized_label == "multiple per day"
        for entry in result.ledger
    )


def test_kept_class_competes_and_wins_by_ladder() -> None:
    # Nightly narrative (1 per day, monthly frequency 30) outranks the
    # yearly rate (same semantic priority 4, lower monthly frequency).
    record = _record(
        "Historically events occurred 2 times per year. She continues to "
        "have nightly generalised tonic-clonic seizures."
    )
    gated = run_record_three_stage(
        record, GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES)
    )
    kept = run_record_three_stage(
        record,
        GanThreeStageConfig(
            provisional_classes=ALL_PROVISIONAL_CLASSES,
            kept_classes=frozenset({"provisional.nightly_narrative_rate"}),
        ),
    )
    assert gated.stops.select_label != "1 per day"
    assert kept.stops.select_label == "1 per day"
    kept_entries = [
        entry
        for entry in kept.ledger
        if entry.provisional_class == "provisional.nightly_narrative_rate"
    ]
    assert kept_entries and all(
        entry.drop_reason is None for entry in kept_entries
    )
    still_gated = [
        entry
        for entry in kept.ledger
        if entry.provisional_class is not None
        and entry.provisional_class != "provisional.nightly_narrative_rate"
    ]
    assert all(
        entry.drop_reason is LedgerDropReason.PROVISIONAL_UNSUPPORTED
        for entry in still_gated
    )


def test_kept_class_replaces_fallback_when_pool_is_empty() -> None:
    record = _record(
        "Events at present are considered non-epileptic and are more "
        "manageable now."
    )
    kept = run_record_three_stage(
        record,
        GanThreeStageConfig(
            kept_classes=frozenset({"provisional.non_epileptic_current_free"}),
        ),
    )
    assert kept.stops.select_label == "seizure free for multiple month"
    assert not any(entry.is_fallback for entry in kept.ledger)


def test_exclusive_trigger_override_beats_competing_rate() -> None:
    record = _record(
        "Historically events occurred 2 times per year. Seizures occurring "
        "exclusively after nights of curtailed sleep were reported."
    )
    bare_keep = GanThreeStageConfig(
        kept_classes=frozenset({"provisional.trigger_conditioned_unknown"}),
    )
    with_override = GanThreeStageConfig(
        kept_classes=frozenset({"provisional.trigger_conditioned_unknown"}),
        select_overrides=frozenset(
            {"select.override.exclusive_trigger_conditioned_unknown"}
        ),
    )
    assert run_record_three_stage(record, bare_keep).stops.select_label == "2 per year"
    assert (
        run_record_three_stage(record, with_override).stops.select_label == "unknown"
    )


def test_exclusive_trigger_override_ignores_non_exclusive_spans() -> None:
    # "catamenial exacerbation" describes worsening of a countable
    # frequency; the override must not fire without an exclusivity marker.
    record = _record(
        "Seizure rate is 2 per year overall, with catamenial exacerbation "
        "noted around menses."
    )
    config = GanThreeStageConfig(
        kept_classes=frozenset({"provisional.trigger_conditioned_unknown"}),
        select_overrides=frozenset(
            {"select.override.exclusive_trigger_conditioned_unknown"}
        ),
    )
    assert run_record_three_stage(record, config).stops.select_label == "2 per year"


def test_single_dated_event_override_beats_competing_state() -> None:
    record = _record(
        "She has been well controlled; seizure free for 8 weeks was noted, "
        "but the patient reported a seizure on 22/Aug."
    )
    config = GanThreeStageConfig(
        kept_classes=frozenset({"provisional.single_dated_event_unknown"}),
        select_overrides=frozenset(
            {"select.override.single_dated_event_unknown"}
        ),
    )
    assert run_record_three_stage(record, config).stops.select_label == "unknown"


def test_unknown_override_name_is_rejected() -> None:
    record = _record("No relevant text.")
    config = GanThreeStageConfig(
        select_overrides=frozenset({"select.override.not_a_rule"})
    )
    with pytest.raises(ValueError, match="unknown select overrides"):
        run_record_three_stage(record, config)


def test_phase_c_candidate_config_is_frozen() -> None:
    config = phase_c_candidate_config()
    assert config.provisional_classes == ALL_PROVISIONAL_CLASSES
    assert config.kept_classes == ALL_PROVISIONAL_CLASSES
    assert config.select_overrides == frozenset(
        {
            "select.override.exclusive_trigger_conditioned_unknown",
            "select.override.single_dated_event_unknown",
        }
    )


def test_living_find_is_source_near_for_word_number_rate() -> None:
    record = _record("He still has focal seizures four times per day.")
    result = run_record_three_stage(record)
    assert result.stops.find_label == "four per day"
    assert result.stops.find_extract_label == "4 per day"
    assert result.stops.find_extract_raw_label == "four per day"
    assert result.stops.encode_label == "4 per day"
    assert result.stops.select_label == "4 per day"
    pick = result.ledger[result.stops.find_pick_ledger_index]
    assert pick.find_tag == "four/day"


def test_living_cluster_find_is_source_near() -> None:
    record = _record(
        "Weekly morning clusters reported; number per cluster not documented."
    )
    result = run_record_three_stage(record)
    assert result.stops.find_label == "1 cluster per Weekly, multiple per cluster"
    assert result.stops.find_extract_raw_label == result.stops.find_label
    assert result.stops.encode_label == "1 cluster per week, multiple per cluster"
    pick = result.ledger[result.stops.find_pick_ledger_index]
    assert pick.find_tag == "cluster:1/Weekly:multiple"


def test_seizure_free_find_tag_is_state_only() -> None:
    record = _record(
        "She remains free of seizures for two years on the current regimen."
    )
    result = run_record_three_stage(record)
    assert result.stops.find_label.startswith("seizure free")
    assert result.stops.find_label == result.stops.find_extract_raw_label
    assert result.stops.encode_label.startswith("seizure free")
    assert result.stops.select_label == result.stops.encode_label
    pick = result.ledger[result.stops.find_pick_ledger_index]
    assert pick.find_tag == "seizure_free"


def test_excluded_and_distractor_spans_enter_ledger_and_leave_select() -> None:
    medication = (
        "Her current medication is levetiracetam 500 mg, taken two times "
        "per day with breakfast and dinner."
    )
    record = _record(medication)
    comparator = gan_rules.run_record(
        record, PipelineConfiguration(architecture="rules")
    )
    result = run_record_three_stage(record)
    assert result.stops.select_label == comparator.output.final_value
    assert result.final_selection.evidence == comparator.output.evidence
    dropped = [
        entry
        for entry in result.ledger
        if entry.drop_reason
        in {
            LedgerDropReason.RULE_EXCLUDE,
            LedgerDropReason.MEDICATION_DOSE_DISTRACTOR,
        }
    ]
    assert dropped
    competing = [
        candidate
        for candidate in extract_wide_candidates(medication)
        if candidate.deferred_drop
    ]
    assert competing
    assert all(not candidate.deferred_drop for candidate in _extract_candidates(medication))


def test_wide_ledger_producers_are_named() -> None:
    notes = IDENTITY_NOTES + (
        "Her current medication is levetiracetam 500 mg, taken two times "
        "per day with breakfast and dinner.",
        "Every 3 weeks on average she has a cluster.",
    )
    for note_text in notes:
        wide = extract_wide_candidates(note_text)
        assert all(
            candidate.rule_id != "unknown" for candidate in wide
        ), note_text


def test_registry_exclusion_scan_covers_declared_exclude_rules() -> None:
    # The real registry scan must at least see the medication-distractor
    # guarded direct-rate rule; a medication context suppresses the match.
    records = collect_exclusion_records(
        "Her current medication is levetiracetam 500 mg, taken two times "
        "per day with breakfast and dinner.",
        AblationConfig(),
    )
    assert any(record.rule_id.startswith("rate.") for record in records)
