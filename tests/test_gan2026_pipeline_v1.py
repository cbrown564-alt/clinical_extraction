import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_frequency_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    CandidateKind,
    Gan2026PipelineV1,
    _candidate_event,
    _RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
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
            "Seizure-free for up to two months then clusters of four seizures "
            "in a single day.",
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
            "Over the past month, the patient reports a cluster of short events "
            "on multiple days.",
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
            "Seizure days: six/30 this month.",
            "6 per month",
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
    note_text = "Seizure days: six/30 this month."

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
                group
                for group in RuleGroup
                if group is not RuleGroup.PORTABLE_RATE_EXPRESSIONS
            )
        )
    ).run(_record(note_text))

    assert result.output.final_value == "no seizure frequency reference"


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_kind"),
    [
        (
            "Present Seizure Frequency: Two events over the last five months.",
            "2 per 5 month",
            FrequencyLabelKind.FREQUENCY,
        ),
        (
            "Regarding current events, he still has focal onset seizures four times per day, "
            "and tonic-clonic seizures 2 times per month.",
            "4 per day",
            FrequencyLabelKind.FREQUENCY,
        ),
        (
            "Over the past three months they describe several episodes per week of brief "
            "generalised events.",
            "multiple per week",
            FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        ),
    ],
)
def test_pipeline_extracts_simple_current_frequency_rates(
    note_text: str,
    expected_label: str,
    expected_kind: FrequencyLabelKind,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == expected_kind
    assert result.diagnostics["final_selection"]["monthly_frequency"] is not None
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "These events have been occurring multiple times in past week.",
            "multiple per week",
            "occurring multiple times in past week",
        ),
        (
            "Current status: Several episodes per week, plus two tonic-clonic events "
            "over the past six months.",
            "multiple per week",
            "Several episodes per week",
        ),
        (
            "Brief focal episodes are now happening on most nights of the week.",
            "multiple per week",
            "happening on most nights of the week",
        ),
        (
            "Petit mal occur on a near-daily basis, sometimes dozens in a day, "
            "making accurate quantification challenging.",
            "multiple per day",
            "Petit mal occur on a near-daily basis, sometimes dozens in a day",
        ),
        (
            "Generalised tonic-clonic seizures are rare, typically 3 events per year. "
            "Focal sensory episodes occur several times each week, particularly in "
            "the evenings.",
            "multiple per week",
            "Focal sensory episodes occur several times each week",
        ),
        (
            "Focal tonic events occur several times per week, with convulsions only "
            "twice per year.",
            "multiple per week",
            "Focal tonic events occur several times per week",
        ),
        (
            "Generalised convulsions are rare. Focal non-motor occur several times "
            "each week, particularly in the evenings.",
            "multiple per week",
            "Focal non-motor occur several times each week",
        ),
        (
            "Generalised tonic-clonic seizures are rare. Focal sensory occur several "
            "times each week.",
            "multiple per week",
            "Focal sensory occur several times each week",
        ),
        (
            "She describes brief absence-like spells on most days, with two "
            "generalised tonic-clonic seizures in the past eight weeks.",
            "multiple per week",
            "She describes brief absence-like spells on most days",
        ),
    ],
)
def test_pipeline_prioritizes_qualitative_high_frequency_current_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] in {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Present Seizure Frequency: focal seizures every 6 days.",
            "1 per 6 day",
            "seizures every 6 days",
        ),
        (
            "Present Seizure Frequency: focal seizures every seven to nine days.",
            "1 per 7 to 9 day",
            "seizures every seven to nine days",
        ),
        (
            "Present Seizure Frequency: tonic-clonic seizures once a week.",
            "1 per week",
            "seizures once a week",
        ),
        (
            "Present Seizure Frequency: monthly seizures.",
            "1 per month",
            "monthly seizures",
        ),
        (
            "Present Seizure Frequency: bimonthly seizures.",
            "1 per 2 month",
            "bimonthly seizures",
        ),
        (
            "The carer reports that seizures are occurring every 2 days on average.",
            "1 per 2 day",
            "occurring every 2 days",
        ),
        (
            "Since review, events tend to cluster every seven to nine days.",
            "1 per 7 to 9 day",
            "cluster every seven to nine days",
        ),
        (
            "The patient reports ongoing episodes occurring every 3 - 4 weeks.",
            "1 per 3 to 4 week",
            "occurring every 3 - 4 weeks",
        ),
        (
            "Frequency is now reported as twice a month.",
            "2 per month",
            "twice a month",
        ),
        (
            "She describes her seizures as occurring roughly yearly.",
            "1 per year",
            "occurring roughly yearly",
        ),
        (
            "She notes the events are occurring bimonthly on average.",
            "1 per 2 month",
            "occurring bimonthly",
        ),
        (
            "Current seizure frequency is daily.",
            "1 per day",
            "daily",
        ),
        (
            "The caregiver says brief episodes occur daily.",
            "1 per day",
            "occur daily",
        ),
        (
            "In clinic they report 12 to 30 per quarter.",
            "12 to 30 per 3 month",
            "12 to 30 per quarter",
        ),
        (
            "They believe there were 3 or 5 seizures last month.",
            "3 to 5 per month",
            "3 or 5 seizures last month",
        ),
        (
            "He describes three or four seizures last week.",
            "3 to 4 per week",
            "three or four seizures last week",
        ),
        (
            "The diary shows 7 to 9 focal onset seizures in three weeks.",
            "7 to 9 per 3 week",
            "7 to 9 focal onset seizures in three weeks",
        ),
        (
            "The diary shows 21 to 28 epileptic spasms in three months.",
            "21 to 28 per 3 month",
            "21 to 28 epileptic spasms in three months",
        ),
        (
            "The diary lists six or eight petit mal over the past month.",
            "6 to 8 per month",
            "six or eight petit mal over the past month",
        ),
        (
            "The family reports 3 or 5 tonic-clonic over the past month.",
            "3 to 5 per month",
            "3 or 5 tonic-clonic over the past month",
        ),
        (
            "Family counted 3 or 4 focal impaired awareness seizures this week.",
            "3 to 4 per week",
            "3 or 4 focal impaired awareness seizures this week",
        ),
        (
            "She describes 6 to 7 myoclonic per week.",
            "6 to 7 per week",
            "6 to 7 myoclonic per week",
        ),
        (
            "The patient describes two or four seizures over the past year.",
            "2 to 4 per year",
            "two or four seizures over the past year",
        ),
        (
            "The patient reported 1 tonic-clonic seizures yesterday.",
            "1 per day",
            "1 tonic-clonic seizures yesterday",
        ),
        (
            "These have become frequent, with seizures every other day.",
            "1 per 2 day",
            "seizures every other day",
        ),
        (
            "The current pattern is seizures every other week.",
            "1 per 2 week",
            "seizures every other week",
        ),
        (
            "Focal impaired-awareness events are now occurring only every other month or so.",
            "1 per 2 month",
            "occurring only every other month",
        ),
        (
            "This week he has had 3 or 4 focal impaired awareness seizures.",
            "3 to 4 per week",
            "This week he has had 3 or 4 focal impaired awareness seizures",
        ),
        (
            "Over the past month, they estimate 3 to 4 seizures.",
            "3 to 4 per month",
            "Over the past month, they estimate 3 to 4 seizures",
        ),
        (
            "She now describes seizures every night.",
            "1 per day",
            "seizures every night",
        ),
        (
            "The current pattern is tonic-clonic every night.",
            "1 per day",
            "tonic-clonic every night",
        ),
        (
            "They report a myoclonic jerk daily.",
            "1 per day",
            "myoclonic jerk daily",
        ),
        (
            "Current diary summary: focal cognitive monthly.",
            "1 per month",
            "focal cognitive monthly",
        ),
        (
            "They report larger convulsive events occurring tonic-clonic daily.",
            "1 per day",
            "tonic-clonic daily",
        ),
        (
            "In terms of timing, he tends to experience a spell roughly once in a fortnight.",
            "1 per 2 week",
            "once in a fortnight",
        ),
        (
            "He phrased it as happening about every second week.",
            "1 per 2 week",
            "happening about every second week",
        ),
        (
            "Importantly, the median inter-seizure interval ≈ six weeks.",
            "1 per 6 week",
            "median inter-seizure interval ≈ six weeks",
        ),
        (
            "Current seizure control: Median inter-seizure interval ≈ four months.",
            "1 per 4 month",
            "Median inter-seizure interval ≈ four months",
        ),
        (
            "Seizures: Patient reports events occurring with intervals ranging 14 - 21 days.",
            "1 per 14 to 21 day",
            "events occurring with intervals ranging 14 - 21 days",
        ),
        (
            "They report intervals ranging three - four days between focal aware seizures.",
            "1 per 3 to 4 day",
            "intervals ranging three - four days",
        ),
        (
            "Event pattern: Every 8 days on average.",
            "1 per 8 day",
            "Every 8 days on average",
        ),
        (
            "Current seizure control: Median inter-seizure interval ≈ four months. "
            "Background to improvement: Prior to this, events clustered approximately "
            "every four to five days.",
            "1 per 4 month",
            "Median inter-seizure interval ≈ four months",
        ),
    ],
)
def test_pipeline_extracts_implicit_one_event_rates(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "The diary records one tonic-clonic and six petit mal in last week.",
            "7 per week",
            "one tonic-clonic and six petit mal in last week",
        ),
        (
            "Family report two focal epileptic spasms and one focal non-motor in last month.",
            "3 per month",
            "two focal epileptic spasms and one focal non-motor in last month",
        ),
        (
            "She has had two drop attacks and nine absence seizures in the past six months.",
            "11 per 6 month",
            "two drop attacks and nine absence seizures in the past six months",
        ),
        (
            "He has had four absence seizures and one myoclonic this month.",
            "5 per month",
            "four absence seizures and one myoclonic this month",
        ),
        (
            "He described a single very brief event last month after night duties.",
            "1 per month",
            "single very brief event last month",
        ),
        (
            "Over the past four months, she reports three events in that timeframe.",
            "3 per 4 month",
            "Over the past four months, she reports three events in that timeframe",
        ),
        (
            "Over the past four months, she describes seizure activity separated by clear "
            "periods without symptoms, with intermittent episodes punctuated by normal "
            "intervals. She reports three events in that timeframe: two morning episodes "
            "and one evening event.",
            "3 per 4 month",
            (
                "Over the past four months, she describes seizure activity separated by clear "
                "periods without symptoms, with intermittent episodes punctuated by normal "
                "intervals. She reports three events in that timeframe"
            ),
        ),
    ],
)
def test_pipeline_sums_distributed_recent_event_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Current frequency and recent course: By his account, events have been occurring "
            "intermittently over the past three months, with two generalised convulsions in "
            "that period and approximately four focal impaired-awareness episodes, often "
            "clustering after a week of late shifts.",
            "6 per 3 month",
            (
                "over the past three months, with two generalised convulsions in that period "
                "and approximately four focal impaired-awareness episodes"
            ),
        ),
        (
            "Seizures: Over the past three months they report two brief myoclonic jerks on "
            "awakening and one generalised tonic-clonic event at approximately 03:00 in early "
            "September.",
            "3 per 3 month",
            (
                "Over the past three months they report two brief myoclonic jerks on "
                "awakening and one generalised tonic-clonic event"
            ),
        ),
        (
            "Present Seizure Frequency: Patient describes brief events most commonly "
            "clustering as they are drifting off to sleep. Over the past six weeks, four "
            "episodes have occurred, each lasting under two minutes.",
            "4 per 6 week",
            "Over the past six weeks, four episodes have occurred",
        ),
        (
            "He and his partner report that the spells tend to cluster during periods of "
            "heightened psychological pressure at work. Over the past three months he notes "
            "approximately 3-5 focal seizures per month.",
            "3 to 5 per month",
            "3-5 focal seizures per month",
        ),
    ],
)
def test_pipeline_extracts_contextual_period_first_frequency_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Against this backdrop, he reports an increase in brief absence episodes and "
            "two myoclonic clusters over the past three weeks, alongside one generalised "
            "tonic-clonic seizure occurring late morning at work.",
            "2 cluster per 3 week, multiple per cluster",
            "two myoclonic clusters over the past three weeks",
        ),
        (
            "Seizures: The diary shows infrequent events predominantly aligned with delayed "
            "or missed ASM doses. Specifically: - 2025: January 0; February 1 generalised "
            "convulsion after missing evening valproate; March 0; April 0; May 1 absence "
            "cluster after late morning lamotrigine; June 0; July 0; August 1 generalised "
            "convulsion following two late doses; September 0.",
            "3 per 9 month",
            (
                "2025: January 0; February 1 generalised convulsion after missing evening "
                "valproate; March 0; April 0; May 1 absence cluster after late morning "
                "lamotrigine; June 0; July 0; August 1 generalised convulsion following "
                "two late doses; September 0"
            ),
        ),
        (
            "Frequency has increased: July x 3 focal aware motor; August x 4 focal aware "
            "motor; September x 5 focal aware motor with two focal to bilateral "
            "tonic-clonic.",
            "5 per month",
            "September x 5 focal aware motor",
        ),
        (
            "Seizures: Patient describes rare events that occur exclusively during prolonged "
            "physical exertion at work. Last event: 3 weeks ago on-site following extended "
            "machinery loading; prior to that, one event in late May 2025 during a "
            "high-demand shift.",
            "1 per 1 to 2 month",
            (
                "Last event: 3 weeks ago on-site following extended machinery loading; "
                "prior to that, one event in late May 2025"
            ),
        ),
    ],
)
def test_pipeline_extracts_contextual_trigger_and_diary_frequency_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "There were two generalised tonic-clonic seizures in the past fortnight after "
            "many months without a convulsion.",
            "2 per 2 week",
            "two generalised tonic-clonic seizures in the past fortnight",
        ),
        (
            "Over the last three weeks, there have been four brief episodes featuring "
            "impaired awareness and post-event fatigue.",
            "4 per 3 week",
            (
                "Over the last three weeks, there have been four brief episodes featuring "
                "impaired awareness"
            ),
        ),
        (
            "Clips recorded on the family phone over the last eight weeks indicate brief "
            "generalised episodes occurring approximately twice weekly.",
            "2 per week",
            "occurring approximately twice weekly",
        ),
        (
            "Over the past six weeks he has experienced three clusters requiring recovery "
            "time off work, each comprising two to four brief events over 24-48 hours.",
            "3 cluster per 6 week, 2 to 4 per cluster",
            (
                "Over the past six weeks he has experienced three clusters requiring recovery "
                "time off work, each comprising two to four brief events"
            ),
        ),
        (
            "Clustering over the past six weeks (four focal impaired-awareness episodes "
            "and two focal aware auras).",
            "6 per 6 week",
            (
                "over the past six weeks (four focal impaired-awareness episodes "
                "and two focal aware auras"
            ),
        ),
        (
            "Over the last 12 weeks he recorded: July 0, August 2 brief events over one "
            "weekend, September 1 isolated event; no prolonged confusion reported.",
            "3 per 3 month",
            (
                "July 0, August 2 brief events over one weekend, September 1 isolated event"
            ),
        ),
        (
            "She describes two clusters in the past six weeks, each comprising 1-2 brief "
            "focal-feeling spells with transient confusion and no injury.",
            "2 cluster per 6 week, 1 to 2 per cluster",
            (
                "two clusters in the past six weeks, each comprising 1-2 brief "
                "focal-feeling spells"
            ),
        ),
        (
            "Since commencing ketogenic diet therapy, the family notes only seven brief "
            "seizures recorded in 2024 so far.",
            "7 per year",
            "seven brief seizures recorded in 2024 so far",
        ),
        (
            "Prior to commencing Lacosamide, episodes occurred at a rate of three to five "
            "focal sensory per week. Since titration to the current dose, the frequency has "
            "remained unchanged.",
            "3 to 5 per week",
            "rate of three to five focal sensory per week",
        ),
        (
            "The diary over the past two months records five focal automatisms per week on "
            "average, often clustering in the evening.",
            "5 per week",
            "records five focal automatisms per week",
        ),
        (
            "He describes warning features and reports 2 to 4 focal non-motor per week, "
            "usually clustering in the late afternoon.",
            "2 to 4 per week",
            "reports 2 to 4 focal non-motor per week",
        ),
        (
            "Weekly morning clusters reported; number per cluster not documented.",
            "1 cluster per week, multiple per cluster",
            "Weekly morning clusters reported",
        ),
        (
            "Seizure History This Quarter: Patient reports two clusters this quarter, both "
            "occurring in the context of poor sleep. Within each cluster, events were brief "
            "focal aware seizures.",
            "2 cluster per 3 month, multiple per cluster",
            "two clusters this quarter",
        ),
        (
            "With respect to seizures, he describes three clusters this quarter, each "
            "lasting 1-2 days with several brief episodes.",
            "3 cluster per 3 month, multiple per cluster",
            "three clusters this quarter, each lasting 1-2 days with several brief episodes",
        ),
        (
            "Diagnosis: Generalised epilepsy with ongoing nocturnal clusters 3x/month; good "
            "response to valproate.",
            "3 cluster per month, multiple per cluster",
            "nocturnal clusters 3x/month",
        ),
        (
            "Cluster frequency unclear this month; last month ≈4 clusters.",
            "4 cluster per month, multiple per cluster",
            "last month ≈4 clusters",
        ),
        (
            "Cluster frequency unclear this month; last month ≈three clusters.",
            "3 cluster per month, multiple per cluster",
            "last month ≈three clusters",
        ),
    ],
)
def test_pipeline_extracts_trigger_assertion_heavy_frequency_rows(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_preserves_seizure_free_as_semantic_state() -> None:
    result = Gan2026PipelineV1().run(
        _record("He has been seizure free for a long duration and over several years.")
    )

    assert result.output.final_value == "seizure free for multiple year"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.SEIZURE_FREE


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "She remains free of seizures for two years on the current regimen.",
            "seizure free for 2 year",
            "free of seizures for two years",
        ),
        (
            "There have been no seizures since the last clinic review.",
            "seizure free for multiple year",
            "no seizures since",
        ),
        (
            "Clinic Date: 28 December 2021. She reports excellent stability with a "
            "seizure-free interval since 25/06/2021.",
            "seizure free for 6 month",
            "seizure-free interval since 25/06/2021",
        ),
        (
            "The diary shows no recorded events or auras since May. They have maintained "
            "an absence of events for over four months.",
            "seizure free for 4 month",
            "absence of events for over four months",
        ),
        (
            "Since our last appointment, she has not experienced any seizures.",
            "seizure free for multiple year",
            "has not experienced any seizures",
        ),
        (
            "Present Seizure Frequency: No recurrence.",
            "seizure free for multiple year",
            "No recurrence",
        ),
        (
            "Since his last review, he reports excellent stability and seizure freedom continues.",
            "seizure free for multiple year",
            "seizure freedom continues",
        ),
        (
            "The family report that there have been No clinical seizures observed since referral.",
            "seizure free for multiple year",
            "No clinical seizures observed since",
        ),
        (
            "Seizures remain settled without recent breakthrough events, "
            "indicating ongoing control.",
            "seizure free for multiple year",
            "Seizures remain settled without recent breakthrough events",
        ),
        (
            "She confirms complete control of seizures since her last review.",
            "seizure free for multiple year",
            "complete control of seizures",
        ),
        (
            "There has been no occurrence of events suggestive of seizures since his last review "
            "twelve months ago.",
            "seizure free for 12 month",
            (
                "no occurrence of events suggestive of seizures since his last review "
                "twelve months ago"
            ),
        ),
        (
            "He described remaining free of his usual attacks over this interval.",
            "seizure free for multiple year",
            "free of his usual attacks over this interval",
        ),
        (
            "The patient reports no auras, warnings, or witnessed events for an extended period.",
            "seizure free for multiple year",
            "no auras, warnings, or witnessed events for an extended period",
        ),
        (
            "Since April, he has not described any further events suggestive of seizures.",
            "seizure free for multiple year",
            "has not described any further events suggestive of seizures",
        ),
        (
            "Recent spells are dissociative. She last had a clearly epileptic focal event "
            "approximately six months ago.",
            "seizure free for 6 month",
            "last had a clearly epileptic focal event approximately six months ago",
        ),
        (
            "Seizures: Patient reports no events, warnings, or auras for over 18 months. "
            "The note header says daily seizures.",
            "seizure free for 18 month",
            "no events, warnings, or auras for over 18 months",
        ),
        (
            "There have been effectively no spell-like events suggestive of seizures "
            "over the past six months. For context, his first seizure occurred in 2014.",
            "seizure free for 6 month",
            "no spell-like events suggestive of seizures over the past six months",
        ),
        (
            "She describes \"No events suggestive of seizures\" over this interval, "
            "although sleep is disrupted on two to three nights per week.",
            "seizure free for multiple year",
            "No events suggestive of seizures",
        ),
        (
            "The patient reports no recent events suggestive of seizures, "
            "with the last confirmed episode occurring over two years ago.",
            "seizure free for multiple year",
            "no recent events suggestive of seizures",
        ),
        (
            "Prior to improvement, she described weekly clusters, usually 6 events. "
            "After surgery she has had Sustained postoperative seizure freedom.",
            "seizure free for multiple year",
            "Sustained postoperative seizure freedom",
        ),
        (
            "He performs light exercise three times per week. His seizure diary shows "
            "no recorded events since June last year.",
            "seizure free for multiple year",
            "no recorded events since",
        ),
        (
            "Present Seizure Frequency: Seizure-free interval extends to eleven months.",
            "seizure free for 11 month",
            "Seizure-free interval extends to eleven months",
        ),
        (
            "The smartwatch log was reviewed. Interval history negative for seizures.",
            "seizure free for multiple year",
            "Interval history negative for seizures",
        ),
        (
            "She reports durable seizure control over the past several months.",
            "seizure free for multiple year",
            "durable seizure control",
        ),
        (
            "Clinic Date: 23 December 2021. They report Drug-free remission since 20-Jun-2021.",
            "seizure free for 6 month",
            "Drug-free remission since 20-Jun-2021",
        ),
        (
            "Clinic Date: 22 November 2017. They volunteered a clear timepoint: "
            "No focal clonic since 19-Mar-2017.",
            "seizure free for 8 month",
            "No focal clonic since 19-Mar-2017",
        ),
        (
            "The device dashboard indicates a recorded seizure rate at zero over the "
            "last six months.",
            "seizure free for 6 month",
            "recorded seizure rate at zero over the last six months",
        ),
        (
            "Entries confirm Seizure cessation following initiation of last ASM.",
            "seizure free for multiple year",
            "Seizure cessation following initiation of last ASM",
        ),
        (
            "Clinic Date: 02 October 2025. Patient reports that the prior cluster "
            "pattern resolved since 11 Aug 2023.",
            "seizure free for 25 month",
            "prior cluster pattern resolved since 11 Aug 2023",
        ),
        (
            "Clinic Date: 02 October 2025. Seizure control: Sustained remission "
            "since 29-May-2023.",
            "seizure free for 28 month",
            "Sustained remission since 29-May-2023",
        ),
        (
            "There have been no witnessed or reported seizures since the last review.",
            "seizure free for multiple year",
            "no witnessed or reported seizures since",
        ),
        (
            "The diary shows no episodes brought to attention by carers or bystanders, "
            "nor any events he has recognised as seizures, since early summer.",
            "seizure free for multiple year",
            (
                "no episodes brought to attention by carers or bystanders, nor any "
                "events he has recognised as seizures"
            ),
        ),
        (
            "Present Seizure Frequency: She has now been seizure free for one and "
            "a half years.",
            "seizure free for 1.5 year",
            "seizure free for one and a half years",
        ),
        (
            "He previously had daily absences, but has remained seizure free for a "
            "prolonged period, not experiencing any seizures in one and a half years.",
            "seizure free for 1.5 year",
            "not experiencing any seizures in one and a half years",
        ),
        (
            "He previously had convulsive events 2 times per year, but is currently "
            "in long-term remission, having been seizure free for years.",
            "seizure free for multiple year",
            "currently in long-term remission, having been seizure free for years",
        ),
        (
            "He and his family feel he is in a steady run without clear seizures at present.",
            "seizure free for multiple year",
            "steady run without clear seizures at present",
        ),
    ],
)
def test_pipeline_extracts_common_seizure_free_phrasing(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.SEIZURE_FREE
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "He remained seizure-free for 8 months after starting levetiracetam, "
            "before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, "
            "preceded by a cluster of absences.",
            "2 per 8 month",
            (
                "seizure-free for 8 months after starting levetiracetam, "
                "before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, "
                "preceded by a cluster of absences"
            ),
        ),
        (
            "On carbamazepine monotherapy he was seizure-free for five months, "
            "until a focal impaired-awareness seizure occurred three Thursdays ago.",
            "1 per 5 month",
            (
                "seizure-free for five months, until a focal impaired-awareness "
                "seizure occurred three Thursdays ago"
            ),
        ),
        (
            "She had no seizures for nearly a year following initiation of valproate, "
            "then developed myoclonic jerks leading to 3 tonic seizure 2 Saturdays ago.",
            "3 per year",
            (
                "no seizures for nearly a year following initiation of valproate, "
                "then developed myoclonic jerks leading to 3 tonic seizure 2 Saturdays ago"
            ),
        ),
        (
            "She may remain seizure-free for up to two month, but then will experience "
            "clusters of four seizures in a single day.",
            "1 cluster per 2 month, 4 per cluster",
            (
                "seizure-free for up to two month, but then will experience "
                "clusters of four seizures in a single day"
            ),
        ),
        (
            "She may remain seizure-free for up to 4 month, but then will experience "
            "clusters of three - four seizures in a single day.",
            "1 cluster per 4 month, 3 to 4 per cluster",
            (
                "seizure-free for up to 4 month, but then will experience "
                "clusters of three - four seizures in a single day"
            ),
        ),
        (
            "The driving plan is to reassess after the seizure-free interval. "
            "Follow-up in three months by video.",
            "no seizure frequency reference",
            "The driving plan is to reassess after the seizure-free interval.",
        ),
    ],
)
def test_pipeline_handles_temporal_seizure_free_distractors(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 10 August 2019. She discontinued Valproate on 10 Jul. "
            "Shortly afterwards, she experienced 2 to 3 seizures, one triggered by "
            "missed medication. She has remained seizure-free since then.",
            "2 to 3 per month",
            "Shortly afterwards, she experienced 2 to 3 seizures",
        ),
        (
            "Clinic Date: 24 March 2017. He came off Levetiracetam on 21-Feb. "
            "In the following week, he had two to three seizures, one associated "
            "with sleep deprivation. No further seizures have occurred since.",
            "2 to 3 per month",
            "In the following week, he had two to three seizures",
        ),
        (
            "Clinic Date: 05 June 2017. Lamotrigine was stopped on 4 Apr. Around "
            "that period, she had 4 seizures, one following alcohol intake. She has "
            "not had any further events since.",
            "4 per 2 month",
            "Around that period, she had 4 seizures",
        ),
        (
            "Clinic Date: 16 April 2019. He withdrew from Clobazam on 13-Jan. At "
            "that time, he had 3 - 4 seizures, one precipitated by illness. He has "
            "remained stable without seizures since.",
            "3 to 4 per 3 month",
            "At that time, he had 3 - 4 seizures",
        ),
    ],
)
def test_pipeline_extracts_medication_withdrawal_bursts_before_since_then_stability(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 14 November 2014. His initial event was in July 2014 in "
            "Germany, arising from sleep. A second event occurred in Italy the "
            "following October 2014, once more during the night. He has had no "
            "further events since surgical intervention.",
            "2 per 3 month",
            (
                "His initial event was in July 2014 in Germany, arising from sleep. "
                "A second event occurred in Italy the following October 2014"
            ),
        ),
        (
            "Clinic Date: 14 November 2017. The first seizure was reported in March "
            "2017 while visiting relatives in Canada. The second and third event "
            "took place in November 2017 in the USA, again from sleep. There have "
            "been no further episodes since starting her current regimen.",
            "3 per 8 month",
            (
                "The first seizure was reported in March 2017 while visiting "
                "relatives in Canada. The second and third event took place in "
                "November 2017"
            ),
        ),
        (
            "Clinic Date: 10 April 2016. No further tonic-clonic seizures have "
            "occurred since Jan-2015, although 2 to 3 single jerks remain. There "
            "have been no absences reported by the patient or observed by family "
            "since late 2015.",
            "2 to 3 per 15 month",
            (
                "No further tonic-clonic seizures have occurred since Jan-2015, "
                "although 2 to 3 single jerks remain"
            ),
        ),
    ],
)
def test_pipeline_extracts_dated_historical_current_frequency_spans(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Her seizure control is variable but acceptable; she continues to "
            "experience epileptic spasm on a daily basis, myoclonic jerks in "
            "morning clusters, and occasional generalised tonic-clonic seizures.",
            "1 per day",
            "continues to experience epileptic spasm on a daily basis",
        ),
        (
            "Although his seizures fluctuate, his parents consider him reasonably "
            "well controlled, he still has generalised tonic-clonic seizures three "
            "nights per week, drop attacks occurring in batches.",
            "3 per week",
            "still has generalised tonic-clonic seizures three nights per week",
        ),
        (
            "Clinic Date: 23 April 2014. Seizure burden has been substantially "
            "reduced following dose adjustment, with only six focal "
            "impaired-awareness seizures reported so far this year.",
            "6 per 4 month",
            "six focal impaired-awareness seizures reported so far this year",
        ),
        (
            "Clinic Date: 24 February 2016. Following introduction of lamotrigine, "
            "there has been a clear improvement in control, with just five "
            "generalised tonic-clonic seizures documented this year to date.",
            "5 per 2 month",
            "five generalised tonic-clonic seizures documented this year to date",
        ),
        (
            "Clinic Date: 24 January 2015. His mother notes an overall improvement "
            "compared with previous years, with four tonic seizures documented in "
            "2015 so far.",
            "4 per month",
            "four tonic seizures documented in 2015 so far",
        ),
        (
            "Clinic Date: 20 May 2024. The family feel seizure frequency has "
            "decreased markedly since starting medication, with only five seizures "
            "so far this year.",
            "5 per 5 month",
            "five seizures so far this year",
        ),
    ],
)
def test_pipeline_extracts_current_daily_and_year_to_date_frequency_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 02 October 2025. After commencing Clobazam 10 mg nocte, "
            "she had a five month remission, then sustained a drop attack 3 Mondays "
            "ago, preceded by myoclonic jerks.",
            "2 per 5 month",
            (
                "five month remission, then sustained a drop attack 3 Mondays ago, "
                "preceded by myoclonic jerks"
            ),
        ),
        (
            "Clinic Date: 03 March 2023. On 31 January, following medication, the "
            "absences became less frequent. The last such episode occurred on 06 "
            "February and she has been stable since.",
            "1 per month",
            "last such episode occurred on 06 February",
        ),
        (
            "Clinic Date: 4 February 2021. In Nov he had 3 seizures during sleep "
            "and 1 while awake. In Jan he had five in sleep and one while awake.",
            "10 per 3 month",
            (
                "In Nov he had 3 seizures during sleep and 1 while awake. In Jan "
                "he had five in sleep and one while awake"
            ),
        ),
    ],
)
def test_pipeline_extracts_remission_date_and_monthly_summary_frequency_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 02 October 2025. She had no seizures for nearly a year "
            "following initiation of Valproate, then developed myoclonic jerks "
            "leading to a tonic seizure two Saturdays ago.",
            "1 per year",
            (
                "no seizures for nearly a year following initiation of Valproate, "
                "then developed myoclonic jerks leading to a tonic seizure two "
                "Saturdays ago"
            ),
        ),
        (
            "Clinic Date: 29 December 2021. He did not have seizures for over 6 "
            "months, but then reported two generalised tonic-clonic seizures two "
            "Fridays ago, each preceded by myoclonic jerks.",
            "4 per 6 month",
            (
                "did not have seizures for over 6 months, but then reported two "
                "generalised tonic-clonic seizures two Fridays ago, each preceded "
                "by myoclonic jerks"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_free_interval_then_breakthrough_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 14 November 2017. She first experienced a seizure in May "
            "2017 while living abroad. It occurred during sleep. Her next seizure "
            "came in November 2017 the same year, once more from sleep.",
            "2 per 6 month",
            (
                "She first experienced a seizure in May 2017 while living abroad. "
                "It occurred during sleep. Her next seizure came in November 2017"
            ),
        ),
        (
            "Clinic Date: 14 November 2016. She first experienced a seizure in July "
            "2016 while living abroad. Her next 4 seizure came in November 2016 "
            "the same year, once more from sleep.",
            "5 per 4 month",
            (
                "She first experienced a seizure in July 2016 while living abroad. "
                "Her next 4 seizure came in November 2016"
            ),
        ),
        (
            "Clinic Date: 20 June 2024. His first seizure occurred in January 2024 "
            "in Ireland, at night while asleep. The second and third event was in "
            "June 2024 in Scotland, also during sleep.",
            "3 per 5 month",
            (
                "His first seizure occurred in January 2024 in Ireland, at night "
                "while asleep. The second and third event was in June 2024"
            ),
        ),
    ],
)
def test_pipeline_extracts_first_next_event_narrative_spans(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 10 May 2015. Seizures in 2014-2015: May: 5 days with "
            "more severe seizures June: 5 days with seizures July: 12 days August: "
            "3 days, most of them at sleep time, September: 12 days, October: 3 "
            "days with seizures November: 7 days with seizures, December: 5 days "
            "with more severe seizures January: 4 days, February: 2 days with "
            "seizures March: 5 days with more severe seizures, April: 1 days with "
            "seizures.",
            "64 per 12 month",
            (
                "Seizures in 2014-2015: May: 5 days with more severe seizures "
                "June: 5 days with seizures July: 12 days August: 3 days, most of "
                "them at sleep time, September: 12 days, October: 3 days with "
                "seizures November: 7 days with seizures, December: 5 days with "
                "more severe seizures January: 4 days, February: 2 days with "
                "seizures March: 5 days with more severe seizures, April: 1 days "
                "with seizures"
            ),
        ),
        (
            "Clinic Date: 22 April 2025. Seizures in 2024-2025: Aug: 6 days, most "
            "of them at sleep time, Sep: 11 days with seizures, Oct: 1 days, Nov: "
            "7 days, most of them at sleep time, Dec: 8 days with seizures Jan: "
            "9 days, Feb: 8 days with seizures Mar: 2 days.",
            "52 per 8 month",
            (
                "Seizures in 2024-2025: Aug: 6 days, most of them at sleep time, "
                "Sep: 11 days with seizures, Oct: 1 days, Nov: 7 days, most of "
                "them at sleep time, Dec: 8 days with seizures Jan: 9 days, Feb: "
                "8 days with seizures Mar: 2 days"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_day_annual_logs(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 25 February 2022. On 25/Jan his absences improved after "
            "medication adjustment. His last event was on 30/Jan and he has "
            "remained well since.",
            "1 per month",
            "His last event was on 30/Jan",
        ),
        (
            "Clinic Date: 29 June 2020. On 28/Apr his absences improved after "
            "medication adjustment. His last event was on 03/May and he has "
            "remained well since.",
            "1 per 2 month",
            "His last event was on 03/May",
        ),
        (
            "From: Dr Thomas Reed Sent: 29 June 2020 10:15 To: epilepsy.clinic@nhs.net. "
            "On 28/Apr his absences improved after medication adjustment. His last "
            "event was on 03/May and he has remained well since.",
            "1 per 2 month",
            "His last event was on 03/May",
        ),
        (
            "Clinic Date: 16 January 2022. On 15 October his absences settled with "
            "treatment. The most recent episode was on 23 October, and since then "
            "he has been well.",
            "1 per 3 month",
            "The most recent episode was on 23 October",
        ),
    ],
)
def test_pipeline_extracts_last_event_date_summaries(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 09 May 2023. Last tonic-clonic seizure was in Apr/2022, "
            "with 3 morning jerks since then.",
            "4 per 13 month",
            "Last tonic-clonic seizure was in Apr/2022, with 3 morning jerks since then",
        ),
        (
            "Clinic Date: 10 April 2025. Last tonic-clonic seizure was in 1 - 2024, "
            "with 2 to 3 morning jerks since then.",
            "3 to 4 per 15 month",
            (
                "Last tonic-clonic seizure was in 1 - 2024, with 2 to 3 morning "
                "jerks since then"
            ),
        ),
        (
            "Clinic Date: 08 June 2016. Her last clearly witnessed tonic-clonic "
            "seizure was in 3/2015, with four morning jerks since then.",
            "4 per 15 month",
            (
                "last clearly witnessed tonic-clonic seizure was in 3/2015, with "
                "four morning jerks since then"
            ),
        ),
        (
            "Clinic Date: 09 August 2018. No further tonic-clonic seizures have "
            "occurred since 06/2017, although three single jerks remain.",
            "3 per 14 month",
            (
                "No further tonic-clonic seizures have occurred since 06/2017, "
                "although three single jerks remain"
            ),
        ),
        (
            "From: Dr Alice Morgan Date: 11 March 2022 To: neurology.team@nhs.net. "
            "No further tonic-clonic seizures have occurred since 12/2020, although "
            "two to three single jerks remain.",
            "2 to 3 per 15 month",
            (
                "No further tonic-clonic seizures have occurred since 12/2020, "
                "although two to three single jerks remain"
            ),
        ),
    ],
)
def test_pipeline_extracts_numeric_month_year_residual_jerk_spans(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 09 June 2023. Her last convulsive seizure was recorded "
            "in 03/2022, with occasional clusters of myoclonic jerks persisting.",
            "multiple cluster per 15 month, multiple per cluster",
            (
                "Her last convulsive seizure was recorded in 03/2022, with "
                "occasional clusters of myoclonic jerks persisting"
            ),
        ),
        (
            "Clinic Date: 09 July 2019. Her last convulsive seizure was recorded "
            "in June 2018, with occasional clusters of myoclonic jerks persisting.",
            "multiple cluster per 13 month, multiple per cluster",
            (
                "Her last convulsive seizure was recorded in June 2018, with "
                "occasional clusters of myoclonic jerks persisting"
            ),
        ),
    ],
)
def test_pipeline_extracts_last_convulsive_cluster_persistence_spans(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "He can sometimes go nearly two week without seizures, but when they "
            "recur he tends to have several in one day, often between 4 and 6.",
            "1 cluster per 2 week, 4 to 6 per cluster",
            (
                "go nearly two week without seizures, but when they recur he tends "
                "to have several in one day, often between 4 and 6"
            ),
        ),
        (
            "On occasions she is seizure-free for four to five consecutive days, "
            "followed by a day with multiple events, typically two tonic seizures.",
            "1 cluster per 4 to 5 day, 2 per cluster",
            (
                "seizure-free for four to five consecutive days, followed by a day "
                "with multiple events, typically two tonic seizures"
            ),
        ),
        (
            "He may go 3 days without seizures, but when they happen he often has "
            "them in batches, with four occurring within 24 hours.",
            "1 cluster per 3 day, 4 per cluster",
            (
                "go 3 days without seizures, but when they happen he often has them "
                "in batches, with four occurring within 24 hours"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_free_interval_cluster_cycles(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "His absence seizures are now occurring on two to three days of the "
            "week, whereas previously they were restricted to once every couple "
            "of weeks.",
            "2 to 3 per week",
            "absence seizures are now occurring on two to three days of the week",
        ),
        (
            "His absence seizures are now occurring on four days of the week, "
            "whereas previously they were restricted to once every couple of weeks.",
            "4 per week",
            "absence seizures are now occurring on four days of the week",
        ),
    ],
)
def test_pipeline_extracts_current_days_of_week_frequency(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 13 January 2024. In October he had two seizures during "
            "sleep and none while awake. In December he had three in sleep and no "
            "while awake.",
            "5 per 3 month",
            (
                "In October he had two seizures during sleep and none while awake. "
                "In December he had three in sleep and no while awake"
            ),
        ),
        (
            "Clinic Date: 25 July 2014. In Jun he had a nocturnal seizure but no "
            "daytime events. In July he had three nocturnal seizures and 5 while awake.",
            "9 per 2 month",
            (
                "In Jun he had a nocturnal seizure but no daytime events. In July "
                "he had three nocturnal seizures and 5 while awake"
            ),
        ),
        (
            "Clinic Date: 7 May 2023. In Feb he had 3 in sleep and one while awake. "
            "In Apr he had five in sleep and no while awake.",
            "9 per 3 month",
            (
                "In Feb he had 3 in sleep and one while awake. In Apr he had five "
                "in sleep and no while awake"
            ),
        ),
    ],
)
def test_pipeline_extracts_two_month_sleep_awake_diary_summaries(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 25 September 2024. She has had no seizures so far this "
            "month, four in August, one in July and 3 in June, with events reported "
            "from both daytime and nocturnal periods.",
            "8 per 4 month",
            (
                "She has had no seizures so far this month, four in August, one in "
                "July and 3 in June"
            ),
        ),
        (
            "Clinic Date: 24 September 2011. He experienced 2 generalised "
            "tonic-clonic seizures so far in Sep, one in Aug, and 0 in Jul, "
            "occurring during both wakefulness and sleep.",
            "3 per 3 month",
            (
                "2 generalised tonic-clonic seizures so far in Sep, one in Aug, "
                "and 0 in Jul"
            ),
        ),
        (
            "Clinic Date: 24 March 2024. This month so far she has no seizures; "
            "earlier 4 in February, 0 in January and 7 in December, over waking "
            "hours and sleep.",
            "11 per 4 month",
            (
                "This month so far she has no seizures; earlier 4 in February, "
                "0 in January and 7 in December"
            ),
        ),
    ],
)
def test_pipeline_extracts_recent_month_count_diary_summaries(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 23 September 2022. He reports 6 seizure events in "
            "September, 6 in August and four in July, and 2 in June, from both "
            "daytime and nocturnal periods.",
            "18 per 4 month",
            (
                "He reports 6 seizure events in September, 6 in August and four in "
                "July, and 2 in June"
            ),
        ),
        (
            "Clinic Date: 5 July 2019. She noted no seizures in June, four in May, "
            "and four in April, all from mixed awake/asleep states.",
            "8 per 3 month",
            "She noted no seizures in June, four in May, and four in April",
        ),
        (
            "Clinic Date: 5 October 2018. He has recorded three seizures to date in "
            "September, 4 in August and three in July, including nocturnal and "
            "daytime periods.",
            "10 per 3 month",
            (
                "He has recorded three seizures to date in September, 4 in August "
                "and three in July"
            ),
        ),
    ],
)
def test_pipeline_extracts_reported_monthly_count_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 20 February 2024. He had a cluster of three seizures in "
            "August. In November he had a nocturnal seizure, and in February a "
            "single tonic seizure was recorded during respite care.",
            "5 per 7 month",
            (
                "He had a cluster of three seizures in August. In November he had "
                "a nocturnal seizure, and in February a single tonic seizure was "
                "recorded"
            ),
        ),
        (
            "Clinic Date: 10 October 2020. In Apr she experienced four short "
            "absences in a cluster. In Jul there was 2 further brief absences, and "
            "in Sep another at school.",
            "7 per 6 month",
            (
                "In Apr she experienced four short absences in a cluster. In Jul "
                "there was 2 further brief absences, and in Sep another"
            ),
        ),
    ],
)
def test_pipeline_extracts_sparse_cluster_and_event_month_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 6 April 2019. He has recorded 2 seizures to date in "
            "March, 7 in February and six in January, including nocturnal and "
            "daytime periods. He will continue daily seizure recording.",
            "15 per 3 month",
            (
                "He has recorded 2 seizures to date in March, 7 in February and "
                "six in January"
            ),
        ),
        (
            "Clinic Date: 24 January 2013. This month, she has had six convulsions; "
            "0 were in December and 5 in November, across day and night.",
            "11 per 3 month",
            (
                "This month, she has had six convulsions; 0 were in December and "
                "5 in November"
            ),
        ),
        (
            "Clinic Date: 25 September 2014. As of this month she reports four "
            "seizure events; 3 in August, three in July and five in June during "
            "both sleep and wakefulness.",
            "15 per 4 month",
            (
                "As of this month she reports four seizure events; 3 in August, "
                "three in July and five in June"
            ),
        ),
    ],
)
def test_pipeline_extracts_extended_month_count_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "His seizures typically occur in clusters, generally spaced four days "
            "apart, though brief periods of daily seizures have been reported.",
            "1 per 4 day",
            "seizures typically occur in clusters, generally spaced four days apart",
        ),
        (
            "His seizures typically occur in clusters, generally spaced four to "
            "five days apart, though brief periods of daily seizures have been "
            "reported.",
            "1 per 4 to 5 day",
            (
                "seizures typically occur in clusters, generally spaced four to "
                "five days apart"
            ),
        ),
        (
            "His seizures typically occur in clusters, generally spaced 5 days "
            "apart, though brief periods of daily seizures have been reported.",
            "1 per 5 day",
            "seizures typically occur in clusters, generally spaced 5 days apart",
        ),
    ],
)
def test_pipeline_prefers_cluster_spacing_over_incidental_daily_mentions(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 21 April 2011. He had a cluster of three seizures in "
            "Dec (short, not full convulsions, fluctuating awareness, "
            "self-terminating). In Feb he had 7 nocturnal seizures, and in Apr "
            "a single tonic seizure was recorded during respite care.",
            "11 per 5 month",
            (
                "He had a cluster of three seizures in Dec (short, not full "
                "convulsions, fluctuating awareness, self-terminating). In Feb "
                "he had 7 nocturnal seizures, and in Apr a single tonic seizure "
                "was recorded"
            ),
        ),
        (
            "Clinic Date: 24 August 2012. In March he had a run of six seizures "
            "within half an hour (not full generalised tonic-clonic, fluctuating "
            "in intensity, resolved without medication). In June there was two "
            "further seizures at night, and in August another during physiotherapy.",
            "9 per 6 month",
            (
                "In March he had a run of six seizures within half an hour (not "
                "full generalised tonic-clonic, fluctuating in intensity, resolved "
                "without medication). In June there was two further seizures at "
                "night, and in August another"
            ),
        ),
    ],
)
def test_pipeline_extracts_sparse_parenthetical_month_event_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize("count", ["two", "3", "four"])
def test_pipeline_selects_more_frequent_no_more_than_weekly_semiology(count: str) -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Over the past year seizure control has been relatively stable. "
            f"She experiences {count} generalised tonic-clonic seizures every "
            "2 months. Absence seizures remain infrequent, usually no more than "
            "twice weekly, and myoclonic jerks are reported only occasionally."
        )
    )

    assert result.output.final_value == "2 per week"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "no more than twice weekly"
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "He suffers clusters of absence seizures on four to five days each week. "
            "Nocturnal tonic seizures continue to occur around once per year.",
            "4 to 5 cluster per week, multiple per cluster",
            "clusters of absence seizures on four to five days each week",
        ),
        (
            "He suffers clusters of absence seizures on five days each month. "
            "Nocturnal tonic seizures continue to occur around once per year.",
            "5 cluster per month, multiple per cluster",
            "clusters of absence seizures on five days each month",
        ),
    ],
)
def test_pipeline_extracts_cluster_days_per_period(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("period", "expected_label"),
    [("daily", "1 per day"), ("weekly", "1 per week"), ("monthly", "1 per month")],
)
def test_pipeline_extracts_persistent_adverbial_semiology_rates(
    period: str,
    expected_label: str,
) -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Only a single tonic-clonic seizure occurred over the past six months. "
            f"Brief myoclonic jerks persist {period} on awakening but are considered "
            "tolerable."
        )
    )

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        f"Brief myoclonic jerks persist {period}"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_extracts_counted_adverbial_monthly_events() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "He has experienced ongoing focal impaired-awareness seizures, typically "
            "four episodes monthly. These resolve spontaneously."
        )
    )

    assert result.output.final_value == "4 per month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "typically four episodes monthly"
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Prior to this period the seizures were occurring every 1 or 2 weeks. "
            "Over the past year, however, the current pattern is <= two or four per year.",
            "2 to 4 per year",
            "two or four per year",
        ),
        (
            "Previously, the seizure frequency was weekly clusters, usually three events. "
            "Over the past five months on the present regimen, events have reduced to "
            "<= once per month.",
            "1 per month",
            "once per month",
        ),
        (
            "Prior to recent lifestyle changes, the patient reports five focal onset "
            "seizures and four focal automatisms in the past two months. The patient "
            "now describes a simple partial seizure monthly.",
            "1 per month",
            "simple partial seizure monthly",
        ),
    ],
)
def test_pipeline_prefers_current_improved_frequency_over_historical_baseline(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Dose is levetiracetam 1 g twice a day. Patient reports 5 or 7 epileptic "
            "spasms this year.",
            "5 to 7 per year",
            "5 or 7 epileptic spasms this year",
        ),
        (
            "Current treatment is levetiracetam 500 mg twice a day. Over the last "
            "two months he has documented five to six focal automatisms during the "
            "last two months.",
            "5 to 6 per 2 month",
            "five to six focal automatisms during the last two months",
        ),
        (
            "Carbamazepine dose is 200 mg twice a day. Patient reports an absence "
            "seizure every other week.",
            "1 per 2 week",
            "seizure every other week",
        ),
    ],
)
def test_pipeline_ignores_medication_dose_frequencies(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "She reports brief absences occurring on most weekdays, often clustering "
            "around late afternoon. There has been one tonic-clonic seizure in the "
            "last eight weeks.",
            "multiple per week",
            "brief absences occurring on most weekdays",
        ),
        (
            "Since the last review, the patient reports several focal seizures last "
            "week characterised by brief behavioural arrest.",
            "multiple per week",
            "several focal seizures last week",
        ),
        (
            "She reports nocturnal episodes occurring once per night on average for "
            "the past three months. Sumatriptan is used <=4 per month for migraine.",
            "1 per day",
            "occurring once per night",
        ),
    ],
)
def test_pipeline_extracts_current_qualitative_high_frequency_phrasing(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] in {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_prefers_convulsive_event_count_over_nonprogressive_myoclonic_jerks() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "He described a clear increase in events over the last quarter, noting "
            "two drop attacks and nine convulsions in the past three months. The "
            "diary still records intermittent myoclonic jerks upon awakening once "
            "or twice per week without progression to convulsion."
        )
    )

    assert result.output.final_value == "11 per 3 month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        "two drop attacks and nine convulsions in the past three months"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_breakthrough_event_overrides_seizure_free_history() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "She had been seizure free for two years, but now reports "
            "three seizures last month."
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


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Over the past fortnight she describes a run of brief events, "
            "with three short episodes occurring on separate days.",
            "1 cluster per 2 week, 3 per cluster",
            (
                "Over the past fortnight she describes a run of brief events, "
                "with three short episodes occurring on separate days"
            ),
        ),
        (
            "Over the past month, the patient reports a cluster of short events "
            "on multiple days.",
            "multiple cluster per month, multiple per cluster",
            (
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days"
            ),
        ),
        (
            "Over the past four weeks he reports 2 clusters this month; "
            "each approx five absences in the morning.",
            "2 cluster per month, 5 per cluster",
            "2 clusters this month; each approx five absences",
        ),
        (
            "Cluster burden increased since 07/Dec/2023; now weekly, five per cluster.",
            "1 cluster per week, 5 per cluster",
            "weekly, five per cluster",
        ),
        (
            "Since his last review, he reports brief episodes after work with clusters on "
            "several mornings each week, sometimes repeating two or three times within the "
            "same morning.",
            "multiple cluster per week, 2 to 3 per cluster",
            "on several mornings each week",
        ),
        (
            "Over the past six weeks, he has brief nocturnal bunching on 3-4 nights "
            "per week, with several brief episodes grouped together during the night.",
            "3 to 4 cluster per week, multiple per cluster",
            "on 3-4 nights per week",
        ),
        (
            "He has been having clusters on several evenings per fortnight, and on "
            "average each cluster involves roughly five brief spells.",
            "multiple cluster per 2 week, 5 per cluster",
            "on several evenings per fortnight",
        ),
        (
            "Monthly clusters, typically 6 to 7 seizures over 24 h.",
            "1 cluster per month, 6 to 7 per cluster",
            "Monthly clusters, typically 6 to 7 seizures over 24 h",
        ),
        (
            "New nocturnal clustering with early-morning spillover; two nocturnal "
            "clusters this month; each ~four - five events.",
            "2 cluster per month, 4 to 5 per cluster",
            "two nocturnal clusters this month; each ~four - five events",
        ),
        (
            "There have been three nocturnal clusters this month; each ~4 - 5 events.",
            "3 cluster per month, 4 to 5 per cluster",
            "three nocturnal clusters this month; each ~4 - 5 events",
        ),
        (
            "She reports 1 Travel-related clusters this month; ~4 - 6 events per episode.",
            "1 cluster per month, 4 to 6 per cluster",
            "1 Travel-related clusters this month; ~4 - 6 events per episode",
        ),
    ],
)
def test_pipeline_extracts_validation_cluster_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Seizure days: six/30 this month.",
            "6 per month",
            "Seizure days: six/30 this month",
        ),
        (
            "About three seizure days per week are reported.",
            "3 per week",
            "About three seizure days per week",
        ),
        (
            "Clinic shorthand says TC *nine/mo.",
            "9 per month",
            "TC *nine/mo",
        ),
        (
            "Clinic shorthand says TC *5/wk.",
            "5 per week",
            "TC *5/wk",
        ),
        (
            "Diary summary says TC nine/mo.",
            "9 per month",
            "TC nine/mo",
        ),
        (
            "Current frequency reported as: sz ×nine/mo.",
            "9 per month",
            "sz ×nine/mo",
        ),
        (
            "Seizures worsen, up to seven in bad weeks.",
            "7 per week",
            "up to seven in bad weeks",
        ),
        (
            "Diary shorthand says abs *monthly.",
            "1 per month",
            "abs *monthly",
        ),
        (
            "Diary shorthand says abs Xmonthly.",
            "1 per month",
            "abs Xmonthly",
        ),
        (
            "On their calendar, abs 8 monthly over the past three months.",
            "8 per month",
            "abs 8 monthly",
        ),
        (
            "The current clinic shorthand is qtwo - threewk.",
            "1 per 2 to 3 week",
            "qtwo - threewk",
        ),
        (
            "The current clinic shorthand is q2 - 3wk.",
            "1 per 2 to 3 week",
            "q2 - 3wk",
        ),
        (
            "The current clinic shorthand is q1 - 2d.",
            "1 per 1 to 2 day",
            "q1 - 2d",
        ),
        (
            "Recent diary: seven to eight absence seizures this quarter.",
            "7 to 8 per 3 month",
            "seven to eight absence seizures this quarter",
        ),
        (
            "There were nineteen episode of status epilepticus in the past week.",
            "19 per week",
            "nineteen episode of status epilepticus in the past week",
        ),
        (
            "The diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
            "5 per 2 month",
            "Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24",
        ),
        (
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1.",
            "7 per 7 month",
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1",
        ),
    ],
)
def test_pipeline_extracts_validation_shorthand_frequency_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_kind", "expected_evidence"),
    [
        (
            "Clinic Date: 05 July 2018. Importantly, Liam has been seizure-free since 29/09/2017. "
            "Earlier in the year she had five seizures during sleep.",
            "seizure free for 9 month",
            FrequencyLabelKind.SEIZURE_FREE,
            "seizure-free since 29/09/2017",
        ),
        (
            "Clinic Date: 12 January 2019. Prior to the current improvement he had "
            "4-5 seizures per week. "
            "Last seizure on 03-Sep-2017.",
            "seizure free for 16 month",
            FrequencyLabelKind.SEIZURE_FREE,
            "Last seizure on 03-Sep-2017",
        ),
        (
            "Since the last appointment, the patient reports no definite seizure events.",
            "seizure free for multiple year",
            FrequencyLabelKind.SEIZURE_FREE,
            "no definite seizure events",
        ),
        (
            "Patient reports focal aware sensory episodes only when significantly short on sleep. "
            "The last event was on 10 September 2025 after an overnight shift.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "only when significantly short on sleep",
        ),
        (
            "Seizures happen when perimenstrual only (days -3 to +3). "
            "Outside this window she reports no events over the last six months.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "Seizures happen when perimenstrual only (days -3 to +3)",
        ),
        (
            "Summary mentions smoker, rolled tobacco, ~3 per day. Seizures occur abs *monthly.",
            "1 per month",
            FrequencyLabelKind.FREQUENCY,
            "abs *monthly",
        ),
        (
            "Current medication is lamotrigine twice daily. "
            "Seizures: Seizure days: 8/30 this month.",
            "8 per month",
            FrequencyLabelKind.FREQUENCY,
            "Seizure days: 8/30 this month",
        ),
        (
            "Maintain daily seizure diary entries. Present Seizure Frequency: "
            "roughly one brief absence episode "
            "in a typical month.",
            "1 per month",
            FrequencyLabelKind.FREQUENCY,
            "one brief absence episode in a typical month",
        ),
        (
            "Currently events are occurring qone to twod on workdays, with near-daily auras.",
            "1 per 1 to 2 day",
            FrequencyLabelKind.FREQUENCY,
            "qone to twod",
        ),
        (
            "The median inter-seizure interval ≈ two months, with occasional clustering "
            "when sleep is restricted offshore. "
            "Warning symptoms may occur weekly.",
            "1 per 2 month",
            FrequencyLabelKind.FREQUENCY,
            "median inter-seizure interval ≈ two months",
        ),
        (
            "Possible auras and one episode of anxiety were reviewed. "
            "She describes her seizure control as "
            "Better over the past seven months.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "Better over the past seven months",
        ),
    ],
)
def test_pipeline_handles_late_validation_saturation_patterns(
    note_text: str,
    expected_label: str,
    expected_kind: FrequencyLabelKind,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == expected_kind
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_handles_cluster_size_with_unknown_frequency() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Clusters characterized by two focal impaired-awareness seizures; frequency unclear."
        )
    )

    assert result.output.final_value == "unknown, 2 per cluster"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.UNKNOWN


def test_pipeline_can_score_a_small_known_row_subset() -> None:
    records = {
        record.source_row_index: record
        for record in load_records_with_monthly_frequency()
        if record.source_row_index in {11118, 12383, 5555, 13485, 11434}
    }
    pipeline = Gan2026PipelineV1()
    scored_rows = []
    for record in records.values():
        result = pipeline.run(record)
        scored_rows.append(
            {
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "prediction": result.diagnostics["final_selection"]["monthly_frequency"],
            }
        )

    metrics = evaluate_frequency_records(scored_rows, prediction_key="prediction", method="purist")

    assert metrics["micro"]["accuracy"] >= 0.8
