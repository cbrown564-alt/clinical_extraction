"""Frequency repair and policy tests for Gan2026 clinical assessment projection/render.

Split from test_gan2026_clinical_assessment_projection_render.py."""

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    PriorEncounterContext,
    ReferenceDateContext,
    RowContext,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)

from tests.helpers.gan2026_projection_render_fixtures import (
    candidate_set as _candidate_set,
    row_context as _row_context,
    seizure_free_candidate as _seizure_free_candidate,
    unknown_candidate as _unknown_candidate,
)

def test_build_projection_render_row_contains_both_schema_objects() -> None:
    row = {
        "source_row_index": 14,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:14:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "two seizures per month"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={14: _candidate_set(14, evidence="two seizures per month")},
    )

    assert artifact_row["projection_decision"]["projected_label_semantics"] == "2 per month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "2 per month"
    assert artifact_row["scoring_enabled"] is False
    assert "benchmark-comparable" in artifact_row["claim_boundary"]


def test_build_projection_render_repairs_duplicate_and_overlapping_role_ids() -> None:
    row = {
        "source_row_index": 23,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:23:1", "llm:23:1"],
            "supporting_candidate_ids": ["llm:23:1"],
            "rejected_candidate_ids": ["llm:23:1"],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "two seizures per month"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={23: _candidate_set(23, evidence="two seizures per month")},
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["primary_candidate_ids"] == ["llm:23:1"]
    assert assessment["supporting_candidate_ids"] == []
    assert assessment["rejected_candidate_ids"] == []
    assert artifact_row["row_issues"] == []
    assert {
        "candidate_role_duplicate_removed:primary_candidate_ids:llm:23:1",
        (
            "candidate_role_overlap_removed:"
            "supporting_candidate_ids:llm:23:1:kept_primary_candidate_ids"
        ),
        (
            "candidate_role_overlap_removed:"
            "rejected_candidate_ids:llm:23:1:kept_primary_candidate_ids"
        ),
    }.issubset(set(assessment["normalization_issues"]))
    assert artifact_row["final_rendered_label"]["rendered_label"] == "2 per month"


def test_build_projection_render_repairs_frequency_values_from_primary_candidate() -> None:
    row = {
        "source_row_index": 24,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:24:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={24: _candidate_set(24, evidence="two seizures per month")},
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["source_normalized_phrase"] == (
        "two seizures per month"
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == "2 per month"


def test_build_projection_render_repairs_once_per_night_from_primary_candidate() -> None:
    row = {
        "source_row_index": 26,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:26:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            26: _candidate_set(
                26,
                evidence="Nocturnal seizures occurring once per night on average.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["source_normalized_phrase"] == (
        "Nocturnal seizures occurring once per night on average."
    )
    assert assessment["normalized_burden"]["count_low"] == 1.0
    assert assessment["normalized_burden"]["count_high"] == 1.0
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "1 per day"


def test_build_projection_render_repairs_twice_per_night_from_primary_candidate() -> None:
    row = {
        "source_row_index": 27,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:27:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            27: _candidate_set(
                27,
                evidence="Nocturnal seizures occurring twice per night on average.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 2.0
    assert assessment["normalized_burden"]["count_high"] == 2.0
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "2 per day"


def test_build_projection_render_repairs_each_night_from_primary_candidate() -> None:
    row = {
        "source_row_index": 28,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:28:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            28: _candidate_set(
                28,
                evidence="One seizure each night with no daytime events.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 1.0
    assert assessment["normalized_burden"]["count_high"] == 1.0
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "1 per day"


def test_build_projection_render_repairs_twice_nightly_from_primary_candidate() -> None:
    row = {
        "source_row_index": 29,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:29:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            29: _candidate_set(
                29,
                evidence="Twice nightly focal seizures with preserved awareness.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 2.0
    assert assessment["normalized_burden"]["count_high"] == 2.0
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "2 per day"


def test_build_projection_render_repairs_three_seizures_nightly_from_primary_candidate() -> None:
    row = {
        "source_row_index": 30,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:30:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            30: _candidate_set(
                30,
                evidence="Three seizures nightly despite adherence.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 3.0
    assert assessment["normalized_burden"]["count_high"] == 3.0
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "3 per day"


def test_build_projection_render_repairs_several_occasions_each_week_from_primary_candidate(
) -> None:
    row = {
        "source_row_index": 31,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:31:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            31: _candidate_set(
                31,
                evidence=(
                    "Brief staring spells with loss of awareness on several "
                    "occasions each week."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "week"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per week"


def test_build_projection_render_repairs_most_weeks_from_primary_candidate() -> None:
    row = {
        "source_row_index": 32,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:32:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            32: _candidate_set(
                32,
                evidence=(
                    "Focal aware seizures most weeks, occasionally progressing "
                    "to focal impaired awareness."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_low"] == 1.0
    assert assessment["normalized_burden"]["period_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "week"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per week"


def test_build_projection_render_repairs_several_seizures_each_week_as_weekly_not_daily() -> None:
    row = {
        "source_row_index": 33,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:33:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            33: _candidate_set(
                33,
                evidence="Several seizures each week despite treatment.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_unit"] == "week"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per week"


def test_build_projection_render_repairs_several_seizures_typical_month_from_primary_candidate(
) -> None:
    row = {
        "source_row_index": 34,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:34:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            34: _candidate_set(
                34,
                evidence="Several seizures in a typical month despite treatment.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per month"


def test_build_projection_render_repairs_many_events_every_year_from_primary_candidate() -> None:
    row = {
        "source_row_index": 35,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:35:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            35: _candidate_set(
                35,
                evidence="Many events every year with no reliable numeric count.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert "vague_frequency_with_explicit_time_period" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_unit"] == "year"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per year"


def test_build_projection_render_relative_only_trend_stays_unrendered() -> None:
    row = {
        "source_row_index": 36,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:36:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "Frequency increased by about 50% after dose reduction."
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            36: _candidate_set(
                36,
                evidence="Frequency increased by about 50% after dose reduction.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "relative_change_without_current_baseline" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] is None
    assert (
        "frequency_rate_values_incomplete"
        in artifact_row["projection_decision"]["projection_issues"]
    )


def test_build_projection_render_conditional_only_trigger_missed_medication_stays_unrendered(
) -> None:
    row = {
        "source_row_index": 37,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:37:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "Seizures occur only when medication doses are missed."
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            37: _candidate_set(
                37,
                evidence="Seizures occur only when medication doses are missed.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "conditional_only_trigger_without_baseline" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] is None
    assert (
        "frequency_rate_values_incomplete"
        in artifact_row["projection_decision"]["projection_issues"]
    )


def test_build_projection_render_conditional_only_trigger_sleep_stays_unrendered() -> None:
    row = {
        "source_row_index": 38,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:38:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "Seizures occur only after nights of curtailed sleep."
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            38: _candidate_set(
                38,
                evidence="Seizures occur only after nights of curtailed sleep.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "conditional_only_trigger_without_baseline" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] is None
    assert (
        "sleep_restricted_pattern_routed"
        in artifact_row["projection_decision"]["projection_issues"]
    )
    assert (
        artifact_row["projection_decision"]["projection_rule_id"]
        == "sleep_restricted_pattern_routed_v0"
    )


def test_build_projection_render_repairs_diary_prefixed_numeric_date_list() -> None:
    row = {
        "source_row_index": 39,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:39:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            39: _candidate_set(
                39,
                evidence="Diary lists seizures on 03-07, 03-27, 05-15, 05-19, 05-24.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 5.0
    assert assessment["normalized_burden"]["count_high"] == 5.0
    assert assessment["normalized_burden"]["period_low"] == 2.0
    assert assessment["normalized_burden"]["period_high"] == 2.0
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "5 per 2 month"


def test_build_projection_render_repairs_named_month_date_list() -> None:
    row = {
        "source_row_index": 40,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:40:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "the current described seizure burden"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            40: _candidate_set(
                40,
                evidence="Recorded seizures on March 7, March 27, May 15, May 19, and May 24.",
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "frequency_rate_values_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["count_low"] == 5.0
    assert assessment["normalized_burden"]["count_high"] == 5.0
    assert assessment["normalized_burden"]["period_low"] == 2.0
    assert assessment["normalized_burden"]["period_high"] == 2.0
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "5 per 2 month"


def test_build_projection_render_marks_explicit_summary_rate_over_long_period_average() -> None:
    row = {
        "source_row_index": 41,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:41:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Only seven focal impaired-awareness seizures reported so far this year. "
                    "At present, his typical pattern is a focal seizure monthly."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            41: _candidate_set(
                41,
                evidence=(
                    "Only seven focal impaired-awareness seizures reported so far this year. "
                    "At present, his typical pattern is a focal seizure monthly."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "explicit_summary_rate_over_long_period_average" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["count_low"] == 1.0
    assert assessment["normalized_burden"]["count_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "1 per month"


def test_build_projection_render_marks_current_summary_over_year_to_date_variant() -> None:
    row = {
        "source_row_index": 43,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:43:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Year to date he has had only two focal seizures. "
                    "Currently, his typical pattern is a focal seizure monthly."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            43: _candidate_set(
                43,
                evidence=(
                    "Year to date he has had only two focal seizures. "
                    "Currently, his typical pattern is a focal seizure monthly."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "explicit_summary_rate_over_long_period_average" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["count_low"] == 1.0
    assert assessment["normalized_burden"]["count_high"] == 1.0
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "1 per month"


def test_build_projection_render_can_disable_current_summary_rate_priority() -> None:
    row = {
        "source_row_index": 143,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:143:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Year to date he has had only two focal seizures. "
                    "Currently, his typical pattern is a focal seizure monthly."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            143: _candidate_set(
                143,
                evidence=(
                    "Year to date he has had only two focal seizures. "
                    "Currently, his typical pattern is a focal seizure monthly."
                ),
            )
        },
        disabled_ablation_switches={"project_current_summary_rate_priority"},
    )

    assessment = artifact_row["clinical_assessment"]
    assert "explicit_summary_rate_over_long_period_average" not in (
        assessment["normalization_issues"]
    )
    assert (
        "ablation_switch_disabled:project_current_summary_rate_priority"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def test_build_projection_render_repairs_previous_month_active_rate_over_current_zero() -> None:
    row = {
        "source_row_index": 42,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:42:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "There were a handful of short focal events during the previous month. "
                    "In the current month to date, no events have been recorded."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            42: _candidate_set(
                42,
                evidence=(
                    "There were a handful of short focal events during the previous month. "
                    "In the current month to date, no events have been recorded."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "previous_month_active_rate_over_current_zero" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per month"


def test_build_projection_render_can_disable_previous_month_active_rate_policy() -> None:
    row = {
        "source_row_index": 142,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:142:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "There were a handful of short focal events during the previous month. "
                    "In the current month to date, no events have been recorded."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            142: _candidate_set(
                142,
                evidence=(
                    "There were a handful of short focal events during the previous month. "
                    "In the current month to date, no events have been recorded."
                ),
            )
        },
        disabled_ablation_switches={
            "project_previous_active_month_over_current_month_zero"
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "previous_month_active_rate_over_current_zero" not in (
        assessment["normalization_issues"]
    )
    assert (
        "ablation_switch_disabled:"
        "project_previous_active_month_over_current_month_zero"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def test_build_projection_render_repairs_last_month_active_rate_over_so_far_this_month_zero(
) -> None:
    row = {
        "source_row_index": 44,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:44:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Several focal events occurred last month. "
                    "So far this month there have been no events."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            44: _candidate_set(
                44,
                evidence=(
                    "Several focal events occurred last month. "
                    "So far this month there have been no events."
                ),
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "previous_month_active_rate_over_current_zero" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["vague_count"] == "multiple"
    assert assessment["normalized_burden"]["period_unit"] == "month"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per month"


def test_build_projection_render_prioritizes_major_recent_relapse_over_background_aura_rate(
) -> None:
    row = {
        "source_row_index": 45,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:45:1", "llm:45:2"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "primary_with_context",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Yesterday he experienced three tonic-clonic seizures yesterday. "
                    "He describes interictal brief auras occurring approximately once or "
                    "twice per week."
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            45: CandidateSet(
                source_row_index=45,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                candidates=[
                    ExtractedCandidate(
                        candidate_id="llm:45:1",
                        component_owner="test",
                        source_type="llm_candidate",
                        source_artifact="test",
                        source_row_index=45,
                        candidate_kind="frequency_rate",
                        event_type="seizure",
                        frequency=FrequencyDetails(
                            source_phrase="three tonic-clonic seizures yesterday"
                        ),
                        temporality="current",
                        certainty="certain",
                        assertion_status="asserted",
                        evidence_span=EvidenceSpan(
                            text="Yesterday he experienced three tonic-clonic seizures yesterday.",
                            start_char=0,
                            end_char=63,
                        ),
                        source_ids=["note:45:span:0-63"],
                        clinical_or_policy="clinical",
                    ),
                    ExtractedCandidate(
                        candidate_id="llm:45:2",
                        component_owner="test",
                        source_type="llm_candidate",
                        source_artifact="test",
                        source_row_index=45,
                        candidate_kind="frequency_rate",
                        event_type="seizure",
                        frequency=FrequencyDetails(
                            source_phrase=(
                                "interictal brief auras occurring approximately "
                                "once or twice per week"
                            )
                        ),
                        temporality="current",
                        certainty="certain",
                        assertion_status="asserted",
                        evidence_span=EvidenceSpan(
                            text=(
                                "He describes interictal brief auras occurring "
                                "approximately once or "
                                "twice per week."
                            ),
                            start_char=65,
                            end_char=149,
                        ),
                        source_ids=["note:45:span:65-149"],
                        clinical_or_policy="clinical",
                    ),
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["primary_candidate_ids"] == ["llm:45:1"]
    assert assessment["supporting_candidate_ids"] == ["llm:45:2"]
    assert "major_recent_relapse_over_background_frequency" in assessment["normalization_issues"]
    assert assessment["normalized_burden"]["count_low"] == 3.0
    assert assessment["normalized_burden"]["count_high"] == 3.0
    assert assessment["normalized_burden"]["period_unit"] == "day"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "3 per day"


def test_build_projection_render_can_disable_major_recent_relapse_priority() -> None:
    row = {
        "source_row_index": 145,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:145:1", "llm:145:2"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "primary_with_context",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "Yesterday he experienced three tonic-clonic seizures. "
                    "He describes interictal brief auras occurring approximately "
                    "once or twice per week."
                )
            },
        },
    }
    candidate_set = CandidateSet(
        source_row_index=145,
        component_owner="candidate_set_union",
        source_artifacts=["test"],
        candidates=[
            ExtractedCandidate(
                candidate_id="llm:145:1",
                component_owner="test",
                source_type="llm_candidate",
                source_artifact="test",
                source_row_index=145,
                candidate_kind="frequency_rate",
                event_type="seizure",
                frequency=FrequencyDetails(
                    source_phrase="three tonic-clonic seizures yesterday"
                ),
                temporality="current",
                certainty="certain",
                assertion_status="asserted",
                evidence_span=EvidenceSpan(
                    text="Yesterday he experienced three tonic-clonic seizures.",
                    start_char=0,
                    end_char=54,
                ),
                source_ids=["note:145:span:0-54"],
                clinical_or_policy="clinical",
            ),
            ExtractedCandidate(
                candidate_id="llm:145:2",
                component_owner="test",
                source_type="llm_candidate",
                source_artifact="test",
                source_row_index=145,
                candidate_kind="frequency_rate",
                event_type="seizure",
                frequency=FrequencyDetails(
                    source_phrase=(
                        "interictal brief auras occurring approximately "
                        "once or twice per week"
                    )
                ),
                temporality="current",
                certainty="certain",
                assertion_status="asserted",
                evidence_span=EvidenceSpan(
                    text=(
                        "He describes interictal brief auras occurring approximately "
                        "once or twice per week."
                    ),
                    start_char=56,
                    end_char=141,
                ),
                source_ids=["note:145:span:56-141"],
                clinical_or_policy="clinical",
            ),
        ],
    )

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={145: candidate_set},
        disabled_ablation_switches={
            "project_major_recent_relapse_over_background_frequency"
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["primary_candidate_ids"] == ["llm:145:2"]
    assert "major_recent_relapse_over_background_frequency" not in (
        assessment["normalization_issues"]
    )
    assert (
        "ablation_switch_disabled:project_major_recent_relapse_over_background_frequency"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "1 to 2 per week"
    )


def test_build_projection_render_marks_non_exact_selected_evidence_trace() -> None:
    row = {
        "source_row_index": 46,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:46:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "patient is having about two seizures each week"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            46: _candidate_set(
                46,
                evidence="having 2 seizures per week",
            )
        },
    )

    projection = artifact_row["projection_decision"]
    assert projection["selected_evidence_status"]["exact_trace"] is True
    assert projection["selected_evidence_status"]["source_id_status"] == "valid"
    assert projection["selected_evidence_status"]["source_id_trace"] == {
        "selected_source_ids": ["note:46:span:0-20"],
        "expected_source_ids": ["note:46:span:0-20"],
        "missing_expected_source_ids": [],
        "unexpected_source_ids": [],
        "trace_basis": "primary_candidate_exact_evidence",
    }


def test_build_projection_render_marks_invalid_source_id_for_exact_trace() -> None:
    row = {
        "source_row_index": 47,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:47:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "having 2 seizures per week"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            47: CandidateSet(
                source_row_index=47,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                candidates=[
                    ExtractedCandidate(
                        candidate_id="llm:47:1",
                        component_owner="test",
                        source_type="llm_candidate",
                        source_artifact="test",
                        source_row_index=47,
                        candidate_kind="frequency_rate",
                        event_type="seizure",
                        frequency=FrequencyDetails(
                            source_phrase="having 2 seizures per week"
                        ),
                        temporality="current",
                        certainty="certain",
                        assertion_status="asserted",
                        evidence_span=EvidenceSpan(
                            text="having 2 seizures per week",
                            start_char=0,
                            end_char=26,
                        ),
                        source_ids=["note:47:span:unresolved:0"],
                        clinical_or_policy="clinical",
                    )
                ],
            )
        },
    )

    projection = artifact_row["projection_decision"]
    assert projection["selected_evidence_status"]["exact_trace"] is True
    assert projection["selected_evidence_status"]["source_id_status"] == "invalid"
    assert projection["selected_evidence_status"]["source_id_trace"] == {
        "selected_source_ids": ["note:47:span:unresolved:0"],
        "expected_source_ids": ["note:47:span:unresolved:0"],
        "missing_expected_source_ids": [],
        "unexpected_source_ids": [],
        "trace_basis": "primary_candidate_exact_evidence",
    }


def test_build_projection_render_carries_source_phrase_for_denominator_window_review() -> None:
    row = {
        "source_row_index": 48,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": ["llm:48:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "single_fact",
            "normalized_burden": {
                "source_normalized_phrase": "brief absences occur on most weekdays"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            48: _candidate_set(
                48,
                evidence="brief absences occur on most weekdays",
            )
        },
    )

    projection = artifact_row["projection_decision"]
    assert projection["source_normalized_phrase"] == "brief absences occur on most weekdays"
    assert artifact_row["final_rendered_label"]["rendered_label"] == "multiple per week"


def test_build_projection_render_repairs_seizure_free_duration_from_primary_candidate() -> None:
    row = {
        "source_row_index": 25,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:25:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "currently seizure free"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            25: CandidateSet(
                source_row_index=25,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                candidates=[
                    _seizure_free_candidate(
                        25,
                        "llm:25:1",
                        "She has had no seizures for seven months.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "seizure_free_duration_repaired_from_primary_candidate"
        in assessment["normalization_issues"]
    )
    assert assessment["normalized_burden"]["source_normalized_phrase"] == (
        "She has had no seizures for seven months."
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 7 month"
    )
