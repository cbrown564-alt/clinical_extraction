"""Pipeline v1 infrastructure, ablation, metadata, and selection tests."""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_selection,
    temporal,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    CandidateKind,
    Gan2026PipelineV1,
    _candidate_event,
    _clinic_date,
    _month_span_floor,
    _normalize_candidate,
    _RawCandidate,
    _relative_note_date,
    _select_final_event,
)


def _record(note_text: str, gold_label: str = "unknown") -> GanRecord:
    return GanRecord(
        source_row_index=1,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


def test_pipeline_v1_uses_shared_temporal_helpers() -> None:
    assert _clinic_date is temporal.clinic_date
    assert _relative_note_date is temporal.relative_note_date
    assert _month_span_floor is temporal.month_span_floor

    clinic = _clinic_date("Clinic Date: 6 April 2019. No events since 10 July 2018.")
    anchor = _relative_note_date("10 July", clinic)

    assert clinic == temporal.ParsedMonthDate(year=2019, month=4, day=6)
    assert anchor == temporal.ParsedMonthDate(year=2018, month=7, day=10)
    assert _month_span_floor(anchor, clinic) == 8


def test_pipeline_v1_uses_deterministic_selection_module() -> None:
    assert _select_final_event is deterministic_selection.select_final_event


def test_pipeline_preserves_existing_output_with_default_rule_metadata() -> None:
    note_text = "Present Seizure Frequency: Two events over the last five months."

    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == "2 per 5 month"
    assert result.diagnostics["final_selection"]["evidence"] == (
        "Two events over the last five months"
    )
    event = result.diagnostics["candidate_events"][0]
    assert event["rule_id"] == "rate.there_have_been_count"
    assert event["rule_group"] == RuleGroup.PORTABLE_RATE_EXPRESSIONS
    assert event["portability"] == Portability.SEIZURE_FREQUENCY
    assert event["match_groups"] == {
        "count": "Two",
        "denominator": "five",
        "evidence": "Two events over the last five months",
        "unit": "months",
    }


def test_candidate_event_exposes_rule_metadata_when_present() -> None:
    candidate = _RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="2 per week",
        evidence="two seizures per week",
        rule_id="rate.direct_count_per_period",
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups={"count": "two", "unit": "week"},
    )

    event = _candidate_event(
        index=1,
        candidate=candidate,
        note_text="Current frequency: two seizures per week.",
    )

    assert event.rule_id == "rate.direct_count_per_period"
    assert event.rule_group == RuleGroup.PORTABLE_RATE_EXPRESSIONS
    assert event.portability == Portability.SEIZURE_FREQUENCY
    assert event.match_groups == {"count": "two", "unit": "week"}


def test_pipeline_can_ablate_a_catalogued_rule() -> None:
    note_text = (
        "Possible auras and one episode of anxiety were reviewed. "
        "She describes her seizure control as Better over the past seven months."
    )

    default_result = Gan2026PipelineV1().run(_record(note_text))
    ablated_result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group
                for group in RuleGroup
                if group is not RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS
            )
        )
    ).run(_record(note_text))

    assert default_result.output.final_value == "unknown"
    event = default_result.diagnostics["candidate_events"][0]
    assert event["rule_id"] == "unknown.qualitative_improvement"
    assert event["rule_group"] == RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS
    assert event["portability"] == Portability.SEIZURE_FREQUENCY
    assert event["match_groups"] == {"duration": "seven"}
    assert ablated_result.output.final_value == "no seizure frequency reference"


def test_pipeline_can_ablate_benchmark_repair_during_normalization() -> None:
    candidate = _RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="twice weekly",
        evidence="twice weekly",
    )
    event = _candidate_event(
        index=1,
        candidate=candidate,
        note_text="Current seizure frequency is twice weekly.",
    )

    default_normalized = _normalize_candidate(event, candidate)
    ablated_normalized = _normalize_candidate(
        event,
        candidate,
        AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.BENCHMARK_REPAIR
            )
        ),
    )

    assert default_normalized.normalized_label == "2 per week"
    assert default_normalized.semantic_kind == FrequencyLabelKind.FREQUENCY
    assert ablated_normalized.normalized_label == "unknown"
    assert ablated_normalized.semantic_kind == FrequencyLabelKind.UNKNOWN


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_rule_id"),
    [
        (
            "Since the last appointment, the patient reports no definite seizure events.",
            "seizure free for multiple year",
            "seizure_free.no_definite_events",
        ),
        (
            "Since his last review, seizure freedom continues.",
            "seizure free for multiple year",
            "seizure_free.current_control_phrase",
        ),
        (
            "He described remaining free of his usual attacks over this interval.",
            "seizure free for multiple year",
            "seizure_free.current_control_phrase",
        ),
        (
            "Clinic Date: 23 December 2021. They report Drug-free remission since 20-Jun-2021.",
            "seizure free for 6 month",
            "seizure_free.since_date",
        ),
        (
            "There has been an absence of events for over six months.",
            "seizure free for 6 month",
            "seizure_free.absence_for_duration",
        ),
        (
            "Patient reports no events, warnings, or auras for over 18 months.",
            "seizure free for 18 month",
            "seizure_free.no_events_for_duration",
        ),
        (
            "Present Seizure Frequency: Seizure-free interval extends to eleven months.",
            "seizure free for 11 month",
            "seizure_free.duration_status",
        ),
        (
            "She has now been seizure free for one and a half years.",
            "seizure free for 1.5 year",
            "seizure_free.one_and_half_years",
        ),
        (
            "She last had a clearly epileptic focal event approximately six months ago.",
            "seizure free for 6 month",
            "seizure_free.last_epileptic_event",
        ),
        (
            "She remains free of seizures for two years on the current regimen.",
            "seizure free for 2 year",
            "seizure_free.generic_duration_or_since",
        ),
        (
            "There have been no seizures since the last clinic review.",
            "seizure free for multiple year",
            "seizure_free.generic_duration_or_since",
        ),
    ],
)
def test_pipeline_exposes_catalogued_seizure_free_metadata(
    note_text: str,
    expected_label: str,
    expected_rule_id: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    selected_id = result.diagnostics["final_selection"]["selected_event_ids"][0]
    selected_event = next(
        event
        for event in result.diagnostics["candidate_events"]
        if event["event_id"] == selected_id
    )
    assert selected_event["rule_id"] == expected_rule_id
    assert selected_event["rule_group"] == RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS
    assert selected_event["portability"] == Portability.SEIZURE_FREQUENCY


def test_pipeline_can_ablate_catalogued_seizure_free_group() -> None:
    note_text = "Since his last review, seizure freedom continues."

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group
                for group in RuleGroup
                if group is not RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_rule_id"),
    [
        (
            "Weekly morning clusters reported; number per cluster not documented.",
            "1 cluster per week, multiple per cluster",
            "cluster.adjective_rate",
        ),
        (
            "Diagnosis: Generalised epilepsy with ongoing nocturnal clusters 3x/month.",
            "3 cluster per month, multiple per cluster",
            "cluster.compact_count_per_period",
        ),
        (
            "He describes three clusters this quarter, each lasting 1-2 days "
            "with several brief episodes.",
            "3 cluster per 3 month, multiple per cluster",
            "cluster.count_this_period_vague_size",
        ),
        (
            "Patient reports two clusters this quarter.",
            "2 cluster per 3 month, multiple per cluster",
            "cluster.count_this_period",
        ),
        (
            "Cluster frequency unclear this month; last month ≈three clusters.",
            "3 cluster per month, multiple per cluster",
            "cluster.last_month_count",
        ),
        (
            "Cluster days 2 this month, typically five events in 24 h.",
            "2 cluster per month, 5 per cluster",
            "cluster.rate_with_size",
        ),
        (
            "Monthly clusters, typically 6 to 7 seizures over 24 h.",
            "1 cluster per month, 6 to 7 per cluster",
            "cluster.monthly_rate_with_size",
        ),
        (
            "Clusters characterized by five spells, but frequency unclear.",
            "unknown, 5 per cluster",
            "cluster.unknown_frequency_with_size",
        ),
        (
            "Two clusters this month; each approx six absences.",
            "2 cluster per month, 6 per cluster",
            "cluster.count_this_period_with_size",
        ),
        (
            "Over the past six weeks he has experienced three clusters, "
            "each comprising two to four brief events.",
            "3 cluster per 6 week, 2 to 4 per cluster",
            "cluster.each_comprising",
        ),
        (
            "Two myoclonic clusters over the past three weeks.",
            "2 cluster per 3 week, multiple per cluster",
            "cluster.count_over_period",
        ),
        (
            "Seizure-free for up to two months then clusters of four seizures in a single day.",
            "1 cluster per 2 month, 4 per cluster",
            "cluster.seizure_free_cycle",
        ),
        (
            "Clinic Date: 09 June 2023. Her last convulsive seizure was recorded "
            "in 03/2022, with occasional clusters of myoclonic jerks persisting.",
            "multiple cluster per 15 month, multiple per cluster",
            "cluster.last_convulsive_persistence",
        ),
        (
            "He can sometimes go nearly two week without seizures, but when they "
            "recur he tends to have several in one day, often between 4 and 6.",
            "1 cluster per 2 week, 4 to 6 per cluster",
            "cluster.nearly_interval",
        ),
        (
            "On occasions she is seizure-free for four to five consecutive days, "
            "followed by a day with multiple events, typically two tonic seizures.",
            "1 cluster per 4 to 5 day, 2 per cluster",
            "cluster.seizure_free_interval_day",
        ),
        (
            "He may go 3 days without seizures, but when they happen he often has "
            "them in batches, with four occurring within 24 hours.",
            "1 cluster per 3 day, 4 per cluster",
            "cluster.batch_within_24h",
        ),
        (
            "Over the past fortnight she describes a run of brief events, "
            "with three short episodes occurring on separate days.",
            "1 cluster per 2 week, 3 per cluster",
            "cluster.run_with_separate_days",
        ),
        (
            "Over the past month, the patient reports a cluster of short events on multiple days.",
            "multiple cluster per month, multiple per cluster",
            "cluster.vague_days_over_period",
        ),
        (
            "There have been three clusters this month; each ~4 - 5 events.",
            "3 cluster per month, 4 to 5 per cluster",
            "cluster.broad_count_this_period_with_size",
        ),
        (
            "Cluster burden increased; now weekly, five per cluster.",
            "1 cluster per week, 5 per cluster",
            "cluster.period_with_per_cluster",
        ),
        (
            "Current frequency: weekly clusters, usually three events.",
            "1 cluster per week, 3 per cluster",
            "cluster.descriptor_size",
        ),
        (
            "Clusters on several mornings each week, sometimes repeating two or "
            "three times within the same morning.",
            "multiple cluster per week, 2 to 3 per cluster",
            "cluster.timing_days",
        ),
        (
            "Two cluster days this month.",
            "2 cluster per month, multiple per cluster",
            "cluster.days_this_period",
        ),
        (
            "He suffers clusters of absence seizures on four to five days each week.",
            "4 to 5 cluster per week, multiple per cluster",
            "cluster.seizure_days_per_period",
        ),
        (
            "Short bursts around the beginning of most months.",
            "1 cluster per month, multiple per cluster",
            "cluster.short_burst_monthly",
        ),
        (
            "She reports 1 Travel-related clusters this month; ~4 - 6 events per episode.",
            "1 cluster per month, 4 to 6 per cluster",
            "cluster.count_with_implied_size",
        ),
        (
            "Current pattern is fortnight, about five per event cluster.",
            "1 cluster per 2 week, 5 per cluster",
            "cluster.size_without_count",
        ),
    ],
)
def test_pipeline_exposes_catalogued_cluster_metadata(
    note_text: str,
    expected_label: str,
    expected_rule_id: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    selected_id = result.diagnostics["final_selection"]["selected_event_ids"][0]
    selected_event = next(
        event
        for event in result.diagnostics["candidate_events"]
        if event["event_id"] == selected_id
    )
    assert selected_event["rule_id"] == expected_rule_id
    assert selected_event["rule_group"] == RuleGroup.CLUSTER_ARITHMETIC
    assert selected_event["portability"] == Portability.SEIZURE_FREQUENCY
    assert selected_event["match_groups"]


def test_pipeline_can_ablate_catalogued_cluster_group() -> None:
    note_text = "Weekly morning clusters reported; number per cluster not documented."

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.CLUSTER_ARITHMETIC
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_rule_id"),
    [
        (
            "About three seizure days per week are reported.",
            "3 per week",
            "diary.seizure_days_per_period",
        ),
        (
            "Seizure days: 8/30 this month.",
            "8 per month",
            "diary.seizure_days_fraction",
        ),
        (
            "The diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
            "5 per 2 month",
            "diary.date_list",
        ),
        (
            "Seizures in 2023-2024: January: 4 days, February: 2 days.",
            "6 per 2 month",
            "diary.seizure_day_log",
        ),
        (
            "Seizure: 2022: Jan x1, Feb x0, Mar x1.",
            "2 per 3 month",
            "diary.monthly_count_log",
        ),
        (
            "2025: January 0; February 1; March 2.",
            "3 per 3 month",
            "diary.sparse_full_month_log",
        ),
        (
            "Recorded: January 1 seizure, February 2 seizures, March 0 seizures.",
            "3 per 3 month",
            "diary.recorded_month_log",
        ),
        (
            "Frequency has increased: July x 3 focal aware motor; August x 4 focal "
            "aware motor; September x 5 focal aware motor with two focal to bilateral "
            "tonic-clonic.",
            "5 per month",
            "diary.increasing_monthly_count",
        ),
        (
            "Clinic Date: 10 March 2025. In January she had one seizure during sleep "
            "and two while awake. In February she had one in sleep and one while awake.",
            "5 per 2 month",
            "diary.sleep_awake_month_summary",
        ),
        (
            "Clinic Date: 25 September 2024. She has had no seizures so far this "
            "month, four in August, one in July and 3 in June, with events reported "
            "from both daytime and nocturnal periods.",
            "8 per 4 month",
            "diary.monthly_summary.recent_reported",
        ),
        (
            "Clinic Date: 30 September 2010. She had a convulsion so far in "
            "September, 6 in August, six in July, four in June both from being "
            "awake and asleep.",
            "17 per 4 month",
            "diary.monthly_summary.had_both_from",
        ),
    ],
)
def test_pipeline_exposes_catalogued_diary_metadata(
    note_text: str,
    expected_label: str,
    expected_rule_id: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    selected_id = result.diagnostics["final_selection"]["selected_event_ids"][0]
    selected_event = next(
        event
        for event in result.diagnostics["candidate_events"]
        if event["event_id"] == selected_id
    )
    assert selected_event["rule_id"] == expected_rule_id
    assert selected_event["rule_group"] == RuleGroup.DIARY_LOG_AGGREGATION
    assert selected_event["portability"] == Portability.SEIZURE_FREQUENCY
    assert selected_event["match_groups"]


def test_pipeline_can_ablate_catalogued_diary_group() -> None:
    note_text = "Seizure days: 8/30 this month."

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.DIARY_LOG_AGGREGATION
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_rule_id"),
    [
        (
            "She continues to experience epileptic spasm on a daily basis.",
            "1 per day",
            "rate.daily_basis_current",
        ),
        (
            "His absence seizures are now occurring on two to three days of the week.",
            "2 to 3 per week",
            "rate.days_of_week",
        ),
        (
            "He still has generalised tonic-clonic seizures three nights per week.",
            "3 per week",
            "rate.nights_per_period",
        ),
        (
            "The diary records five focal automatisms per week.",
            "5 per week",
            "rate.descriptor_count_per_period",
        ),
        (
            "She describes 6 to 7 myoclonic per week.",
            "6 to 7 per week",
            "rate.qualified_direct_count_per_period",
        ),
        (
            "Present Seizure Frequency: focal seizures every 6 days.",
            "1 per 6 day",
            "rate.implicit_every_n_interval",
        ),
        (
            "She now describes seizures every night.",
            "1 per day",
            "rate.implicit_every_night_interval",
        ),
        (
            "The current pattern is seizures every other week.",
            "1 per 2 week",
            "rate.implicit_every_other_interval",
        ),
        (
            "The carer reports that seizures are occurring every 2 days on average.",
            "1 per 2 day",
            "rate.occurring_every_n_interval",
        ),
        (
            "Focal events are now occurring only every other month or so.",
            "1 per 2 month",
            "rate.occurring_every_other_interval",
        ),
        (
            "In clinic they report 12 to 30 per quarter.",
            "12 to 30 per 3 month",
            "rate.quarter_direct_count_per_period",
        ),
        (
            "He still has focal seizures four times per day.",
            "4 per day",
            "rate.direct_count_per_period",
        ),
        (
            "Present Seizure Frequency: monthly seizures.",
            "1 per month",
            "rate.seizure_adjective",
        ),
        (
            "Current seizure frequency is daily.",
            "1 per day",
            "rate.standalone_adjective",
        ),
        (
            "She describes her seizures as occurring roughly yearly.",
            "1 per year",
            "rate.occurring_adjective",
        ),
        (
            "Focal events occur no more than twice weekly.",
            "2 per week",
            "rate.no_more_than_adverbial",
        ),
        (
            "Focal seizures occurring once per night.",
            "1 per day",
            "rate.occurring_once_per_night",
        ),
        (
            "Brief myoclonic jerks persist monthly on awakening.",
            "1 per month",
            "rate.persistent_adverbial",
        ),
        (
            "Events are typically four episodes monthly.",
            "4 per month",
            "rate.counted_adverbial",
        ),
        (
            "She now describes a simple partial seizure monthly.",
            "1 per month",
            "rate.simple_partial_adverbial",
        ),
        (
            "He describes three or four seizures last week.",
            "3 to 4 per week",
            "rate.recent_count",
        ),
        (
            "The diary shows 7 to 9 focal onset seizures in the past three weeks.",
            "7 to 9 per 3 week",
            "rate.count_during_recent_window",
        ),
        (
            "There have been four brief episodes over the past three weeks.",
            "4 per 3 week",
            "rate.there_have_been_count",
        ),
        (
            "Seven brief seizures recorded in 2024 so far.",
            "7 per year",
            "rate.recorded_year_count",
        ),
        (
            "The patient reported 1 tonic-clonic seizures yesterday.",
            "1 per day",
            "rate.yesterday_or_today_count",
        ),
        (
            "This week he has had 3 or 4 focal impaired awareness seizures.",
            "3 to 4 per week",
            "rate.period_first_recent_count",
        ),
        (
            "Over the past month, they estimate 3 to 4 seizures.",
            "3 to 4 per month",
            "rate.period_first_recent_count",
        ),
        (
            "Over the last three weeks, there have been four brief episodes featuring "
            "impaired awareness.",
            "4 per 3 week",
            "rate.period_first_featuring_count",
        ),
        (
            "Over the past four months, she reports three events in that timeframe.",
            "3 per 4 month",
            "rate.period_first_timeframe_count",
        ),
        (
            "Over the past six weeks, four episodes have occurred.",
            "4 per 6 week",
            "rate.period_first_occurred_count",
        ),
    ],
)
def test_pipeline_exposes_catalogued_portable_rate_metadata(
    note_text: str,
    expected_label: str,
    expected_rule_id: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    selected_id = result.diagnostics["final_selection"]["selected_event_ids"][0]
    selected_event = next(
        event
        for event in result.diagnostics["candidate_events"]
        if event["event_id"] == selected_id
    )
    assert selected_event["rule_id"] == expected_rule_id
    assert selected_event["rule_group"] == RuleGroup.PORTABLE_RATE_EXPRESSIONS
    assert selected_event["portability"] == Portability.SEIZURE_FREQUENCY
    assert selected_event["match_groups"]


def test_pipeline_can_ablate_catalogued_portable_rate_group() -> None:
    note_text = "She continues to experience epileptic spasm on a daily basis."

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.PORTABLE_RATE_EXPRESSIONS
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_rule_id", "expected_portability"),
    [
        (
            # Phase 2 de-overfitting: digit count, no special separator
            "Clinic shorthand says TC 5/mo.",
            "5 per month",
            "gan_shorthand.tc_sz_count_rate",
            Portability.SEIZURE_FREQUENCY,
        ),
        (
            # abs with no asterisk separator (generalized form)
            "Diary shorthand says abs monthly.",
            "1 per month",
            "gan_shorthand.abs_adjective_rate",
            Portability.SEIZURE_FREQUENCY,
        ),
        (
            "On their calendar, abs 8 monthly over the past three months.",
            "8 per month",
            "gan_shorthand.abs_count_rate",
            Portability.SEIZURE_FREQUENCY,
        ),
        (
            # q-interval with digit denominator (generalized form)
            "The current clinic shorthand is q2 - 3wk.",
            "1 per 2 to 3 week",
            "gan_shorthand.q_interval",
            Portability.CLINICAL_EPILEPSY,
        ),
    ],
)
def test_pipeline_exposes_catalogued_gan_shorthand_metadata(
    note_text: str,
    expected_label: str,
    expected_rule_id: str,
    expected_portability: Portability,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    selected_id = result.diagnostics["final_selection"]["selected_event_ids"][0]
    selected_event = next(
        event
        for event in result.diagnostics["candidate_events"]
        if event["event_id"] == selected_id
    )
    assert selected_event["rule_id"] == expected_rule_id
    assert selected_event["rule_group"] == RuleGroup.GAN_SHORTHAND
    assert selected_event["portability"] == expected_portability
    assert selected_event["match_groups"]


def test_pipeline_can_ablate_catalogued_gan_shorthand_group() -> None:
    # Use digit-form that the generalized rule matches, verify ablation suppresses it
    note_text = "Clinic shorthand says TC 5/mo."

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.GAN_SHORTHAND
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


def test_pipeline_exposes_structured_selection_scores() -> None:
    note_text = (
        "Historical seizures were 2 per month. "
        "Patient reports focal aware sensory episodes only when significantly short on sleep."
    )

    result = Gan2026PipelineV1().run(_record(note_text))
    final_selection = result.diagnostics["final_selection"]

    assert result.output.final_value == "unknown"
    assert final_selection["selected_score"] == {
        "semantic_priority": 6,
        "evidence_priority": 0,
        "monthly_frequency_priority": 0.0,
        "reason": "trigger_conditioned_unknown",
    }
    assert final_selection["selected_decision"] == {
        "event_id": final_selection["selected_event_ids"][0],
        "final_label": "unknown",
        "final_kind": FrequencyLabelKind.UNKNOWN,
        "monthly_frequency": 1000.0,
        "evidence": "only when significantly short on sleep",
        "rationale": "Selected seizure-frequency evidence that could not be converted to a rate.",
        "validation_errors": [],
        "score": final_selection["selected_score"],
        "priority": {
            "semantic": 6,
            "evidence": 0,
            "monthly_frequency": 0.0,
        },
    }
    assert final_selection["selection_candidates"]
    selected_score = next(
        score for score in final_selection["selection_candidates"] if score["selected"] is True
    )
    assert selected_score["event_id"] == final_selection["selected_event_ids"][0]
    assert selected_score["score"] == final_selection["selected_score"]


def test_pipeline_can_ablate_temporal_selection_group() -> None:
    note_text = (
        "Historical seizures were 2 per month. "
        "Patient reports focal aware sensory episodes only when significantly short on sleep."
    )

    result = Gan2026PipelineV1(
        ablation_config=AblationConfig(
            enabled_groups=frozenset(
                group for group in RuleGroup if group is not RuleGroup.TEMPORAL_SELECTION
            )
        )
    ).run(_record(note_text))
    final_selection = result.diagnostics["final_selection"]

    assert result.output.final_value == "2 per month"
    assert final_selection["selected_event_ids"] == ["event_1"]
    assert final_selection["selected_score"]["reason"] == "frequency_monthly_rate_disabled"
    assert {score["score"]["reason"] for score in final_selection["selection_candidates"]} == {
        "frequency_monthly_rate_disabled",
        "trigger_conditioned_unknown_disabled",
    }


def test_pipeline_breakthrough_event_overrides_seizure_free_history() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "She had been seizure free for two years, but now reports three seizures last month."
        )
    )

    assert result.output.final_value == "3 per month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY


def test_pipeline_distinguishes_no_reference_from_unknown_frequency() -> None:
    result = Gan2026PipelineV1().run(
        _record("This appointment was cancelled. Medication list unchanged.")
    )

    assert result.output.final_value == "no seizure frequency reference"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.NO_REFERENCE


def test_pipeline_keeps_cluster_structure_in_diagnostics() -> None:
    result = Gan2026PipelineV1().run(
        _record("Cluster days twice this month; typically six seizures in 24 h.")
    )

    assert result.output.final_value == "2 cluster per month, 6 per cluster"
    assert result.diagnostics["candidate_events"][0]["kind"] == "cluster_frequency"
    assert result.diagnostics["normalized_events"][0]["normalized_label"] == (
        "2 cluster per month, 6 per cluster"
    )
