import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ClusterDetails,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    ReferenceDateContext,
    RowContext,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)


def test_assessment_inputs_include_general_grouping_policy_examples() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:301:1", "twelve seizures per month"),
        _cluster_candidate("llm:301:2", "clusters after sleep loss"),
    )
    record = _record(301, "Current baseline is twelve seizures per month.")

    inputs = assessment_probe.build_assessment_inputs(record, candidate_set)

    instructions = " ".join(inputs["task_instructions"])
    prompt_payload = json.dumps(inputs).lower()
    examples = json.dumps(inputs["policy_examples"])
    assert "one overarching clinical assessment" in instructions
    assert "primary_candidate_ids" in instructions
    assert "supporting_candidate_ids" in instructions
    assert "Never invent, renumber, or guess candidate ids" in instructions
    assert "at most one role" in instructions
    assert "Group primary candidates only" in instructions
    assert "For single_fact, use exactly one primary candidate" in instructions
    assert "Use additive_same_window only" in instructions
    assert "repeat the same current burden" in instructions
    assert "Do not use historical candidates as primary" in instructions
    assert "frequency_rate with zero primary candidates" in instructions
    assert "source_normalized_phrase should describe only" in instructions
    assert "do not fill seizure_free_duration fields" in instructions
    assert "outside-window seizure-free durations" in instructions
    assert "Total count plus subtype" in examples
    assert "Vague frequency plus isolated concrete event" in examples
    assert "No usable primary candidate" in examples
    assert "Primary with non-additive context" in examples
    assert "Repeated reference to same burden" in examples
    assert "Frequency plus cluster modifier" in examples
    assert "Current burden plus historical comparison" in examples
    assert "Recent cluster plus later seizure-free interval" in examples
    assert "Cluster cadence plus per-cluster burden" in examples
    assert "benchmark" not in instructions
    assert "scorer" not in instructions
    assert "external evaluator" not in instructions
    assert "final label" not in prompt_payload
    assert "gold" not in prompt_payload


def test_assemble_clinical_assessment_accepts_primary_with_context() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:302:1", "twelve seizures per month"),
        _cluster_candidate("llm:302:2", "clusters after sleep loss"),
        source_row_index=302,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:302:1"],
        supporting_candidate_ids=["llm:302:2"],
        rejected_candidate_ids=[],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            count_low=12,
            count_high=12,
            period_low=1,
            period_high=1,
            period_unit="month",
            source_normalized_phrase="twelve seizures per month",
        ),
        assessment_summary="Monthly frequency controls; clustering is context.",
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:302:1"]
    assert assessment.supporting_candidate_ids == ["llm:302:2"]
    assert assessment.aggregation_policy == "primary_with_context"
    assert assessment.normalization_policy_id == (
        "gan2026_clinical_assessment_normalization_v0"
    )
    assert assessment.normalized_burden.count_low == 12
    assert assessment.normalized_burden.count_high == 12
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalization_issues == []


def test_assemble_clinical_assessment_accepts_additive_same_window() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:303:1", "three focal aware seizures this month"),
        _frequency_candidate("llm:303:2", "two focal impaired-awareness seizures this month"),
        source_row_index=303,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:303:1", "llm:303:2"],
        aggregation_policy="additive_same_window",
        normalized_burden=NormalizedBurden(
            count_low=5,
            count_high=5,
            period_low=1,
            period_high=1,
            period_unit="month",
            source_normalized_phrase="five seizures this month",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:303:1", "llm:303:2"]
    assert assessment.normalized_burden.count_low == 5
    assert assessment.normalized_burden.count_high == 5
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalization_issues == []


def test_assemble_clinical_assessment_ignores_model_value_leak() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:306:1", "two seizures per month"),
        _cluster_candidate("llm:306:2", "clusters after sleep loss"),
        source_row_index=306,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:306:1"],
        supporting_candidate_ids=["llm:306:2"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            count_low=999,
            count_high=999,
            period_low=1,
            period_high=1,
            period_unit="year",
            cluster_count_low=3,
            cluster_count_high=3,
            source_normalized_phrase="two seizures per month",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 2
    assert assessment.normalized_burden.count_high == 2
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalized_burden.cluster_count_low is None


def test_assessment_draft_accepts_qwen_extra_burden_fields() -> None:
    draft = assessment_probe.AssessmentDraft.model_validate(
        {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["det:306:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "two seizures per month",
                "period": "month",
                "rationale": "The current frequency is stated directly.",
                "cluster_cadence": None,
                "events_per_cluster": None,
                "vague_count": "several",
                "period_unit": "months",
            },
            "assessment_summary": "Current rate is directly stated.",
            "rationale": "Qwen sometimes emits this extra explanation field.",
        }
    )

    assert draft.normalized_burden.source_normalized_phrase == "two seizures per month"
    assert draft.normalized_burden.period_unit == "month"
    assert draft.normalized_burden.vague_count == "several"


def test_assemble_clinical_assessment_parses_seizure_free_duration() -> None:
    candidate_set = _candidate_set(
        _seizure_free_candidate("llm:307:1", "seizure free for nine months"),
        source_row_index=307,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="seizure_free",
        primary_candidate_ids=["llm:307:1"],
        aggregation_policy="seizure_free_state",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizure free for nine months",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.seizure_free_duration_low == 9
    assert assessment.normalized_burden.seizure_free_duration_high == 9
    assert assessment.normalized_burden.seizure_free_duration_unit == "month"


def test_assemble_clinical_assessment_parses_cluster_axes() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate("llm:308:1", "3 clusters this month; each two to four events"),
        source_row_index=308,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:308:1"],
        aggregation_policy="cluster_axis",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="3 clusters this month; each two to four events",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.cluster_count_low == 3
    assert assessment.normalized_burden.cluster_period_low == 1
    assert assessment.normalized_burden.cluster_period_unit == "month"
    assert assessment.normalized_burden.events_per_cluster_low == 2
    assert assessment.normalized_burden.events_per_cluster_high == 4


def test_assemble_clinical_assessment_parses_article_rate() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:309:1", "seizures once a week"),
        source_row_index=309,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:309:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(source_normalized_phrase="seizures once a week"),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_parses_every_other_interval() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:310:1", "seizures every other month"),
        source_row_index=310,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:310:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizures every other month"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 2
    assert assessment.normalized_burden.period_unit == "month"


def test_assemble_clinical_assessment_parses_count_over_period_with_spasms() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:311:1", "21 to 28 epileptic spasms in three months"),
        source_row_index=311,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:311:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="21 to 28 epileptic spasms in three months"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 21
    assert assessment.normalized_burden.count_high == 28
    assert assessment.normalized_burden.period_low == 3
    assert assessment.normalized_burden.period_unit == "month"


def test_assemble_clinical_assessment_parses_vague_count_over_period() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:312:1", "multiple seizures in past week"),
        source_row_index=312,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:312:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="multiple seizures in past week"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.vague_count == "multiple"
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_promotes_cluster_when_concrete_frequency_wins() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:313:1",
            "five focal cognitive and six focal non-motors in last week",
        ),
        _cluster_candidate("llm:313:2", "clustered over two consecutive mornings"),
        source_row_index=313,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:313:1", "llm:313:2"],
        aggregation_policy="cluster_axis",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "11 focal seizures over last week with clusters on two mornings"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.assessment_kind == "frequency_rate"
    assert assessment.primary_candidate_ids == ["llm:313:1"]
    assert assessment.normalized_burden.count_low == 11
    assert assessment.normalized_burden.period_unit == "week"
    assert "cluster_assessment_promoted_to_frequency_rate" in assessment.normalization_issues


def test_assemble_clinical_assessment_promotes_supporting_frequency_over_cluster() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate(
            "llm:314:1",
            "roughly once in a fortnight with occasional two close together",
        ),
        _frequency_candidate("det:314:1", "once in a fortnight"),
        source_row_index=314,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:314:1"],
        supporting_candidate_ids=["det:314:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="spells roughly once in a fortnight"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.assessment_kind == "frequency_rate"
    assert assessment.primary_candidate_ids == ["det:314:1"]
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 2
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_projects_vague_multiple_days_in_past_week() -> None:
    candidate_set = _candidate_set(
        _unknown_candidate(
            "llm:315:1",
            "a brief cluster of events occurring on multiple days within the past week",
        ),
        source_row_index=315,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:315:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "a brief cluster of events occurring on multiple days within the past week"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.vague_count == "multiple"
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_promotes_cluster_events_per_day() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate_with_events(
            "llm:316:1",
            cluster_frequency="ongoing daytime clusters",
            events_per_cluster="several episodes per day",
            evidence="ongoing daytime clusters with several episodes per day",
        ),
        source_row_index=316,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:316:1"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="ongoing daytime clusters, several episodes per day"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.assessment_kind == "frequency_rate"
    assert assessment.normalized_burden.vague_count == "multiple"
    assert assessment.normalized_burden.period_unit == "day"


def test_assemble_clinical_assessment_keeps_renderable_cluster_burden() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate_with_events(
            "llm:317:1",
            cluster_frequency="two clusters this month",
            events_per_cluster="four absences per cluster",
            evidence="two clusters this month; each four absences",
        ),
        _unknown_candidate(
            "llm:317:2",
            "brief spells of lost awareness after breakfast on workdays",
        ),
        source_row_index=317,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:317:1"],
        supporting_candidate_ids=["llm:317:2"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="two clusters this month; each four absences"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.assessment_kind == "cluster_frequency"
    assert assessment.primary_candidate_ids == ["llm:317:1"]
    assert assessment.normalized_burden.cluster_count_low == 2
    assert assessment.normalized_burden.events_per_cluster_low == 4


def test_assemble_clinical_assessment_does_not_promote_medication_cadence() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate(
            "llm:318:1",
            "Clobazam as needed for clusters, patient-led use approximately once monthly",
        ),
        source_row_index=318,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:318:1"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="clusters approximately once monthly"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.assessment_kind == "cluster_frequency"
    assert "cluster_assessment_promoted_to_frequency_rate" not in (
        assessment.normalization_issues
    )


def test_prediction_to_assessment_draft_accepts_missing_aggregation_policy() -> None:
    class Prediction:
        assessment_draft = {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["det:319:1"],
            "normalized_burden": {"source_normalized_phrase": "two seizures per month"},
        }

    draft, errors = assessment_probe.prediction_to_assessment_draft(Prediction())

    assert errors == []
    assert draft is not None
    assert draft.aggregation_policy is None


def test_assemble_clinical_assessment_defaults_missing_aggregation_policy() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:319:1", "two seizures per month"),
        source_row_index=319,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:319:1"],
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="two seizures per month"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.aggregation_policy == "single_fact"
    assert "aggregation_policy_defaulted:single_fact" in assessment.normalization_issues


def test_assemble_clinical_assessment_repairs_single_primary_additive_policy() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:320:1", "eleven seizures in the last week"),
        source_row_index=320,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:320:1"],
        aggregation_policy="additive_same_window",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="eleven seizures in the last week"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.aggregation_policy == "single_fact"
    assert (
        "single_primary_additive_same_window_to_single_fact"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_repairs_single_primary_cluster_axis() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate("llm:321:1", "clusters every four weeks"),
        source_row_index=321,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:321:1"],
        aggregation_policy="cluster_axis",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="clusters every four weeks"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.aggregation_policy == "single_fact"
    assert "single_primary_cluster_axis_to_single_fact" in assessment.normalization_issues


def test_assemble_clinical_assessment_repairs_cluster_axis_without_cluster_primary() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:322:1", "two seizures every seven days"),
        _cluster_candidate("llm:322:2", "clusters over one to two days"),
        source_row_index=322,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["det:322:1"],
        supporting_candidate_ids=["llm:322:2"],
        aggregation_policy="cluster_axis",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="two seizures every seven days"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:322:1", "llm:322:2"]
    assert assessment.supporting_candidate_ids == []
    assert (
        "cluster_axis_supporting_cluster_promoted_to_primary"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_repairs_multi_primary_nonadditive_policy() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:323:1", "daily myoclonic jerk"),
        _cluster_candidate("llm:323:2", "occasionally cluster in the morning"),
        source_row_index=323,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:323:1", "llm:323:2"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="daily myoclonic jerk"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:323:1"]
    assert assessment.supporting_candidate_ids == ["llm:323:2"]
    assert (
        "multi_primary_nonadditive_demoted_to_supporting"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_does_not_additive_repair_cluster_assessment() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:325:1", "two seizures this month"),
        _frequency_candidate("llm:325:2", "three seizures this month"),
        source_row_index=325,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["det:325:1", "llm:325:2"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="two seizures this month"
        ),
    )
    candidate_by_id = {
        candidate.candidate_id: candidate for candidate in candidate_set.candidates
    }

    repaired, repair_issues = assessment_probe._repair_multi_primary_nonadditive_policy(
        draft,
        candidate_by_id=candidate_by_id,
    )

    assert repaired.aggregation_policy == "primary_with_context"
    assert repaired.primary_candidate_ids == ["det:325:1"]
    assert repaired.supporting_candidate_ids == ["llm:325:2"]
    assert repair_issues == ["multi_primary_nonadditive_demoted_to_supporting"]


def test_assemble_clinical_assessment_repairs_historical_primary() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:324:1",
            "monthly seizures in 2020",
            temporality="historical",
        ),
        _frequency_candidate(
            "llm:324:2",
            "now has two seizures per month",
            temporality="current",
        ),
        source_row_index=324,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:324:1"],
        supporting_candidate_ids=["llm:324:2"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="monthly seizures in 2020"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["llm:324:2"]
    assert assessment.supporting_candidate_ids == ["llm:324:1"]
    assert (
        "historical_primary_replaced_with_current:llm:324:2"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_repairs_frequency_count_since_month_year_anchor() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:15029:1", "four brief morning jerks since 3/2015"),
        source_row_index=15029,
        row_context=_reference_row_context("2016-06-18"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:15029:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="four brief morning jerks since 3/2015"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 4
    assert assessment.normalized_burden.count_high == 4
    assert assessment.normalized_burden.period_low == 15
    assert assessment.normalized_burden.period_high == 15
    assert assessment.normalized_burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_primary_candidate" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_values_repaired_from_anchor_window" in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_repairs_frequency_since_last_event_anchor() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:15094:1",
            "3 morning jerks since last tonic-clonic seizure in Apr 2022",
        ),
        source_row_index=15094,
        row_context=_reference_row_context("2023-05-10"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:15094:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "3 morning jerks since last tonic-clonic seizure in Apr 2022"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 4
    assert assessment.normalized_burden.count_high == 4
    assert assessment.normalized_burden.period_low == 13
    assert assessment.normalized_burden.period_high == 13
    assert assessment.normalized_burden.period_unit == "month"
    assert "frequency_rate_anchor_from_last_event_phrase" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_values_repaired_from_anchor_window" in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_can_disable_anchor_window_frequency_recovery() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:15029:1", "four brief morning jerks since 3/2015"),
        source_row_index=15029,
        row_context=_reference_row_context("2016-06-18"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:15029:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="four brief morning jerks since 3/2015"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches={
            "normalize_frequency_anchor_window_value_recovery"
        },
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low is None
    assert assessment.normalized_burden.period_low is None
    assert (
        "ablation_switch_disabled:normalize_frequency_anchor_window_value_recovery"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_recovers_multi_month_bucket_frequency_values() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:16758:1",
            "3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr",
        ),
        source_row_index=16758,
        row_context=_reference_row_context("2024-06-18"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:16758:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 9
    assert assessment.normalized_burden.count_high == 9
    assert assessment.normalized_burden.period_low == 5
    assert assessment.normalized_burden.period_high == 5
    assert assessment.normalized_burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_multi_month_window_from_named_buckets" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_bucket_year_inferred_from_reference_date" in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_recovers_explicit_multi_month_window_summary() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:16697:1",
            "Three seizures recorded over six months: September, November, and February",
        ),
        source_row_index=16697,
        row_context=_reference_row_context("2024-03-12"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:16697:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "Three seizures recorded over six months: September, November, and February"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 3
    assert assessment.normalized_burden.count_high == 3
    assert assessment.normalized_burden.period_low == 6
    assert assessment.normalized_burden.period_high == 6
    assert assessment.normalized_burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_multi_month_window_from_source_phrase" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_bucket_year_inferred_from_reference_date" in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_recovers_multi_month_summary_from_assessment_phrase() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "det:16697:1",
            (
                "In September a prolonged focal seizure (~10 minutes) settled "
                "spontaneously. In November a tonic seizure were recorded, and "
                "in February another"
            ),
        ),
        source_row_index=16697,
        row_context=_reference_row_context("2024-03-12"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:16697:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "Three seizures recorded over six months: September, November, "
                "and February"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 3
    assert assessment.normalized_burden.count_high == 3
    assert assessment.normalized_burden.period_low == 6
    assert assessment.normalized_burden.period_high == 6
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_multi_month_window_from_source_phrase" in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_recovers_article_month_bucket_from_assessment_phrase(
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "det:16833:1",
            (
                "A prolonged event occurred in Jul (approximately 12 minutes, "
                "alternating between focal and generalised features, settled "
                "spontaneously). In Oct she had 5 drop attacks, and in Dec two "
                "myoclonic jerks were documented at college"
            ),
        ),
        source_row_index=16833,
        row_context=_reference_row_context("2024-12-20"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:16833:1"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "5 drop attacks in October, 2 myoclonic jerks in December, "
                "and a prolonged event in July"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 8
    assert assessment.normalized_burden.count_high == 8
    assert assessment.normalized_burden.period_low == 6
    assert assessment.normalized_burden.period_high == 6
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in (
        assessment.normalization_issues
    )
    assert "frequency_rate_multi_month_window_from_named_buckets" in (
        assessment.normalization_issues
    )


def test_multi_month_bucket_helper_keeps_current_month_zero_in_multi_month_span() -> None:
    burden, issues, matched = (
        assessment_probe._frequency_burden_from_multi_month_bucket_phrase(
            (
                "This month so far she has no seizures; earlier 4 in February, "
                "0 in January and 7 in December"
            ),
            reference_date="2024-03-24",
        )
    )

    assert matched is True
    assert burden is not None
    assert burden.count_low == 11
    assert burden.count_high == 11
    assert burden.period_low == 4
    assert burden.period_high == 4
    assert burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in issues
    assert "frequency_rate_multi_month_window_from_named_buckets" in issues


def test_multi_month_bucket_helper_adds_numeric_current_month_bucket() -> None:
    burden, issues, matched = (
        assessment_probe._frequency_burden_from_multi_month_bucket_phrase(
            "she has had 6 seizures so far this month, 2 in august, five in july and 3 in june",
            reference_date="2024-09-20",
        )
    )

    assert matched is True
    assert burden is not None
    assert burden.count_low == 16
    assert burden.count_high == 16
    assert burden.period_low == 4
    assert burden.period_high == 4
    assert burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in issues
    assert "frequency_rate_multi_month_window_from_named_buckets" in issues


def test_multi_month_bucket_helper_counts_article_based_month_bucket_event() -> None:
    burden, issues, matched = (
        assessment_probe._frequency_burden_from_multi_month_bucket_phrase(
            (
                "5 drop attacks in October, 2 myoclonic jerks in December, "
                "and a prolonged event in July"
            ),
            reference_date="2024-12-20",
        )
    )

    assert matched is True
    assert burden is not None
    assert burden.count_low == 8
    assert burden.count_high == 8
    assert burden.period_low == 6
    assert burden.period_high == 6
    assert burden.period_unit == "month"
    assert "frequency_rate_values_repaired_from_multi_month_bucket" in issues
    assert "frequency_rate_multi_month_window_from_named_buckets" in issues


def test_normalize_phrase_for_parse_keeps_hyphenated_clinical_terms_intact() -> None:
    assert (
        assessment_probe._normalize_phrase_for_parse("weekly tonic-clonic seizures")
        == "weekly tonic-clonic seizures"
    )
    assert (
        assessment_probe._normalize_phrase_for_parse(
            "two brief generalised tonic–clonic seizures over the past four months"
        )
        == "two brief generalised tonic–clonic seizures over the past four months"
    )


def test_normalize_phrase_for_parse_still_converts_numeric_ranges() -> None:
    assert (
        assessment_probe._normalize_phrase_for_parse(
            "seizures occurring within 24-48 hours of missed doses"
        )
        == "seizures occurring within 24 to 48 hours of missed doses"
    )
    assert (
        assessment_probe._normalize_phrase_for_parse("3-5 seizures per week")
        == "3 to 5 seizures per week"
    )


def test_assemble_clinical_assessment_parses_hyphenated_clinical_term_rate() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:2795:1", "weekly tonic-clonic seizures"),
        source_row_index=2795,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:2795:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="weekly tonic-clonic seizures"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"
    assert "frequency_rate_values_unparsed" not in assessment.normalization_issues


def test_assemble_clinical_assessment_does_not_force_single_month_bucket_without_window() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:14592:1", "Two seizures in June 2024 during sleep"),
        source_row_index=14592,
        row_context=_reference_row_context("2024-10-04"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:14592:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="Two seizures in June 2024 during sleep"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low is None
    assert assessment.normalized_burden.period_low is None
    assert "frequency_rate_values_repaired_from_multi_month_bucket" not in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_can_disable_multi_month_bucket_frequency_recovery(
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:16758:1",
            "3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr",
        ),
        source_row_index=16758,
        row_context=_reference_row_context("2024-06-18"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:16758:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches={
            "normalize_frequency_multi_month_bucket_value_recovery"
        },
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low is None
    assert assessment.normalized_burden.period_low is None
    assert (
        "ablation_switch_disabled:normalize_frequency_multi_month_bucket_value_recovery"
        in assessment.normalization_issues
    )


def test_assemble_clinical_assessment_does_not_force_trigger_only_phrase_into_numeric_rate(
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate(
            "llm:5974:1",
            (
                "Seizures with missed ASM doses, typically occurring within 24-48 "
                "hours of a missed levetiracetam dose"
            ),
        ),
        source_row_index=5974,
        row_context=_reference_row_context("2025-09-20"),
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:5974:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "Seizures with missed ASM doses, typically occurring within 24-48 "
                "hours of a missed levetiracetam dose"
            )
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low is None
    assert assessment.normalized_burden.period_low is None
    assert "frequency_rate_values_unparsed" in assessment.normalization_issues
    assert "frequency_rate_values_repaired_from_anchor_window" not in (
        assessment.normalization_issues
    )


def test_assemble_clinical_assessment_reports_unknown_candidate_id() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:304:1", "two seizures per month"),
        source_row_index=304,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["missing-id"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(source_normalized_phrase="two per month"),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert assessment is None
    assert any("primary_candidate_ids:unknown_candidate_id:missing-id" in error for error in errors)


def test_run_split_prompt_only_uses_default_candidate_set_artifact(
    tmp_path: Path,
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:305:1", "two seizures per month"),
        source_row_index=305,
    )
    candidate_path = tmp_path / "candidate_sets.jsonl"
    candidate_path.write_text(
        json.dumps({"candidate_set": candidate_set.model_dump()}) + "\n",
        encoding="utf-8",
    )
    rows, metadata = assessment_probe.run_split(
        [_record(305, "Current baseline is two seizures per month.")],
        split="validation",
        split_manifest="test_manifest",
        model="test-model",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        candidate_set_jsonl_path=candidate_path,
    )

    assert rows[0]["typed_input"]["candidate_set"]["candidates"][0]["candidate_id"] == "det:305:1"
    assert rows[0]["parse_errors"] == ["not_run", "assessment_draft_missing"]
    assert metadata["candidate_set_jsonl_path"] == str(candidate_path)
    assert metadata["summary"]["examples"] == 1
    assert metadata["summary"]["clinical_assessment_rows"] == 0


def test_run_split_prompt_only_builds_candidate_sets_live_when_path_omitted() -> None:
    rows, metadata = assessment_probe.run_split(
        [
            _record(
                306,
                "The patient reports two seizures per month, unchanged from baseline.",
            )
        ],
        split="validation",
        split_manifest="test_manifest",
        model="test-model",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
    )

    assert metadata["candidate_set_jsonl_path"] == "live"
    assert metadata["candidate_set_source"] == "live_deterministic_llm_union"
    assert metadata["summary"]["missing_candidate_set_rows"] == 0
    assert "candidate_set_missing" not in (rows[0]["parse_errors"] or [])
    candidate_set = rows[0]["candidate_set"]
    assert candidate_set["source_row_index"] == 306
    assert any(
        candidate["candidate_kind"] == "frequency_rate" for candidate in candidate_set["candidates"]
    )
    assert rows[0]["candidate_set_diagnostics"] == {
        "candidate_set_source": "live_deterministic_llm_union",
        "llm_extraction_call_error": None,
        "llm_extraction_parse_errors": [],
    }
    assert rows[0]["typed_input"]["candidate_set"]["candidates"][0]["candidate_id"].startswith(
        "det:306:"
    )


def _candidate_set(
    *candidates: ExtractedCandidate,
    source_row_index: int = 301,
    row_context: RowContext | None = None,
) -> CandidateSet:
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["gan2026_validation250_candidate_set_v2_high_recall"],
        row_context=RowContext() if row_context is None else row_context,
        candidates=list(candidates),
    )


def _reference_row_context(reference_date: str) -> RowContext:
    source_phrase = f"Clinic Date: {reference_date}"
    return RowContext(
        reference_date=ReferenceDateContext(
            date=reference_date,
            date_precision="day",
            source="note_header",
            source_phrase=source_phrase,
            source_span=EvidenceSpan(
                text=source_phrase,
                start_char=0,
                end_char=len(source_phrase),
            ),
        )
    )


def _frequency_candidate(
    candidate_id: str,
    evidence: str,
    *,
    temporality: str = "current",
) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    source_type = (
        "deterministic_candidate" if candidate_id.startswith("det:") else "llm_candidate"
    )
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type=source_type,
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="frequency_rate",
        event_type="seizure",
        frequency=FrequencyDetails(source_phrase=evidence),
        temporality=temporality,
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _cluster_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="cluster_frequency",
        event_type="seizure",
        cluster_details=ClusterDetails(cluster_frequency=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _cluster_candidate_with_events(
    candidate_id: str,
    *,
    cluster_frequency: str,
    events_per_cluster: str,
    evidence: str,
) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="cluster_frequency",
        event_type="seizure",
        cluster_details=ClusterDetails(
            cluster_frequency=cluster_frequency,
            events_per_cluster=events_per_cluster,
        ),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _unknown_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="unknown_frequency",
        event_type="seizure",
        unknown_frequency=SourcePhraseOnlyDetails(source_phrase=evidence),
        temporality="current",
        certainty="uncertain",
        certainty_reason="vague_count",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _seizure_free_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="seizure_free",
        event_type="seizure",
        seizure_free=SeizureFreeDetails(source_phrase=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _record(source_row_index: int, note_text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=0.0,
    )
