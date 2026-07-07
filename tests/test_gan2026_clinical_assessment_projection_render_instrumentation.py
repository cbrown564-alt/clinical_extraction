"""Seizure-free date instrumentation and prior-encounter tests for Gan2026 projection/render.

Split from test_gan2026_clinical_assessment_projection_render.py."""

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from tests.helpers.gan2026_projection_render_fixtures import (
    row_context as _row_context,
)
from tests.helpers.gan2026_projection_render_fixtures import (
    seizure_free_candidate as _seizure_free_candidate,
)


def test_build_projection_render_can_disable_seizure_free_date_instrumentation() -> None:
    row = {
        "source_row_index": 126,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:126:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "no seizures since March 2025"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            126: CandidateSet(
                source_row_index=126,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2026-06-06"),
                candidates=[
                    _seizure_free_candidate(
                        126,
                        "llm:126:1",
                        "She has had no seizures since March 2025.",
                    )
                ],
            )
        },
        disabled_ablation_switches={"normalize_seizure_free_duration_date_instrumentation"},
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"] is None
    assert (
        "ablation_switch_disabled:normalize_seizure_free_duration_date_instrumentation"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def test_build_projection_render_instruments_seizure_free_since_date_from_row_context() -> None:
    row = {
        "source_row_index": 26,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:26:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "no seizures since March 2025"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            26: CandidateSet(
                source_row_index=26,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2026-06-06"),
                candidates=[
                    _seizure_free_candidate(
                        26,
                        "llm:26:1",
                        "She has had no seizures since March 2025.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["normalized_burden"]["seizure_free_duration_low"] == 15
    assert assessment["normalized_burden"]["seizure_free_duration_unit"] == "month"
    assert (
        "seizure_free_duration_instrumented_from_since_date" in assessment["normalization_issues"]
    )
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["state_kind"] == "since_date"
    assert instrumentation["anchor_date"]["date"] == "2025-03"
    assert instrumentation["anchor_date"]["date_precision"] == "month"
    assert instrumentation["reference_date"]["date"] == "2026-06-06"
    assert instrumentation["computed_duration"] == {
        "low": 15.0,
        "high": 15.0,
        "unit": "month",
    }
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 15 month")


def test_build_projection_render_instruments_numeric_since_date() -> None:
    row = {
        "source_row_index": 28,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:28:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "seizure-free since 29/09/2017"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            28: CandidateSet(
                source_row_index=28,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        28,
                        "llm:28:1",
                        "She has been seizure-free since 29/09/2017.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == ("2017-09-29")
    assert assessment["normalized_burden"]["seizure_free_duration_low"] == 96
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 96 month")


def test_build_projection_render_instruments_month_without_year_with_trace() -> None:
    row = {
        "source_row_index": 29,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:29:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "no further events since early August"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            29: CandidateSet(
                source_row_index=29,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        29,
                        "llm:29:1",
                        "There have been no further events since early August.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2025-08"
    assert instrumentation["anchor_date"]["date_precision"] == "month"
    assert instrumentation["anchor_date"]["source"] == (
        "seizure_free_source_phrase_year_inferred_from_reference_date"
    )
    assert (
        "seizure_free_anchor_year_inferred_from_reference_date"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 2 month")


def test_build_projection_render_instruments_last_event_day_month_anchor() -> None:
    row = {
        "source_row_index": 30,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:30:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "no further seizures recorded since last event on 31-May"
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            30: CandidateSet(
                source_row_index=30,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        30,
                        "llm:30:1",
                        "No further seizures recorded since last event on 31-May.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2025-05-31"
    assert "seizure_free_anchor_from_last_event_phrase" in assessment["normalization_issues"]
    assert (
        "seizure_free_anchor_year_inferred_from_reference_date"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 4 month")


def test_build_projection_render_instruments_approximate_season_anchor() -> None:
    row = {
        "source_row_index": 31,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:31:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "no recognized seizures since early summer"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            31: CandidateSet(
                source_row_index=31,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        31,
                        "llm:31:1",
                        "No recognized seizures since early summer.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2025-06"
    assert instrumentation["anchor_date"]["source"] == (
        "seizure_free_source_phrase_approximate_anchor_policy"
    )
    assert (
        "seizure_free_anchor_approximate_start_month_policy" in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 4 month")


def test_build_projection_render_instruments_approximate_year_anchor() -> None:
    row = {
        "source_row_index": 32,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:32:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": ("she cannot recall any episodes since early 2024")
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            32: CandidateSet(
                source_row_index=32,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        32,
                        "llm:32:1",
                        "She cannot recall any episodes since early 2024.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == ("2024-01")
    assert (
        "seizure_free_anchor_approximate_start_month_policy" in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 21 month")


def test_build_projection_render_instruments_hyphenated_mid_month_anchor() -> None:
    row = {
        "source_row_index": 33,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:33:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "seizure-free status since mid-January"
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            33: CandidateSet(
                source_row_index=33,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        33,
                        "llm:33:1",
                        "She has remained seizure-free since mid-January.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == ("2025-01")
    assert (
        "seizure_free_anchor_approximate_start_month_policy" in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 9 month")


def test_build_projection_render_instruments_event_month_from_primary_candidate() -> None:
    row = {
        "source_row_index": 34,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:34:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": ("no further seizures since starting current regimen")
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            34: CandidateSet(
                source_row_index=34,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2017-03-03"),
                candidates=[
                    _seizure_free_candidate(
                        34,
                        "llm:34:1",
                        (
                            "Since commencing the current regimen at the end of "
                            "November, there have been no further events."
                        ),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["source_phrase"].startswith("Since commencing")
    assert instrumentation["anchor_date"]["date"] == "2016-11"
    assert instrumentation["anchor_date"]["source"] == (
        "seizure_free_event_anchor_month_year_inferred_from_reference_date"
    )
    assert "seizure_free_anchor_from_event_phrase" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 4 month")


def test_build_projection_render_preserves_event_month_year_from_primary_candidate() -> None:
    row = {
        "source_row_index": 35,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:35:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "complete seizure control"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            35: CandidateSet(
                source_row_index=35,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        35,
                        "llm:35:1",
                        (
                            "Since starting Levetiracetam in March 2023, he "
                            "reports complete seizure control."
                        ),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2023-03"
    assert instrumentation["anchor_date"]["source"] == ("seizure_free_event_anchor_month_year")
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 31 month")


def test_build_projection_render_preserves_last_event_full_year_from_primary_candidate() -> None:
    row = {
        "source_row_index": 36,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:36:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "no events over the last year"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            36: CandidateSet(
                source_row_index=36,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        36,
                        "llm:36:1",
                        (
                            "He reports no events over the last year, with the "
                            "last seizure on 12-Apr-2023."
                        ),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2023-04-12"
    assert "seizure_free_anchor_from_last_event_phrase" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 29 month")


def test_build_projection_render_resolves_since_then_from_single_summary_antecedent() -> None:
    row = {
        "source_row_index": 37,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:37:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "She has remained seizure-free since then."
            },
            "assessment_summary": (
                "The patient experienced 2 to 3 seizures shortly after "
                "discontinuing valproate on 10 Jul. Since then, she has "
                "remained seizure-free with improved adherence."
            ),
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            37: CandidateSet(
                source_row_index=37,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        37,
                        "llm:37:1",
                        "She has remained seizure-free since then.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2025-07-10"
    assert instrumentation["antecedent"]["link_type"] == "local_since_then_antecedent"
    assert instrumentation["antecedent"]["anchor_date"]["date"] == "2025-07-10"
    assert instrumentation["antecedent"]["source_phrase"] == (
        "The patient experienced 2 to 3 seizures shortly after discontinuing valproate on 10 Jul"
    )
    assert "seizure_free_anchor_from_same_note_antecedent" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 2 month")


def test_build_projection_render_keeps_since_then_with_multiple_antecedents_unresolved() -> None:
    row = {
        "source_row_index": 38,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:38:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": "She has remained seizure-free since then."
            },
            "assessment_summary": (
                "The patient had seizures after stopping valproate on 10 Jul "
                "and another event after missed medication on 18 Aug. Since "
                "then, she has remained seizure-free."
            ),
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            38: CandidateSet(
                source_row_index=38,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        38,
                        "llm:38:1",
                        "She has remained seizure-free since then.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"]["state_kind"] == ("unresolved_anchor")
    assert assessment["seizure_free_instrumentation"]["antecedent"] is None
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def test_build_projection_render_does_not_use_antecedent_for_duration_phrase() -> None:
    row = {
        "source_row_index": 39,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:39:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "seizure-free for over 4 weeks"},
            "assessment_summary": (
                "Previous focal seizure occurred on 19 May. The patient is "
                "now seizure-free for over 4 weeks."
            ),
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            39: CandidateSet(
                source_row_index=39,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-10-02"),
                candidates=[
                    _seizure_free_candidate(
                        39,
                        "llm:39:1",
                        (
                            "Previous focal seizure occurred on 19 May. The "
                            "patient is now seizure-free for over 4 weeks."
                        ),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert assessment["seizure_free_instrumentation"] is None
    assert "seizure_free_anchor_from_same_note_antecedent" not in assessment["normalization_issues"]


def test_build_projection_render_uses_prior_encounter_context_with_policy_trace() -> None:
    row = {
        "source_row_index": 40,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:40:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "No seizures since last visit"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            40: CandidateSet(
                source_row_index=40,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context(
                    "2021-11-05",
                    prior_encounter_date="2021-05-05",
                    prior_encounter_phrase="last appointment six months ago",
                ),
                candidates=[
                    _seizure_free_candidate(
                        40,
                        "llm:40:1",
                        "No seizures since last visit.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert instrumentation["anchor_date"]["date"] == "2021-05-05"
    assert instrumentation["anchor_date"]["source"] == (
        "candidate_set.row_context.prior_encounter:explicit_relative_interval"
    )
    assert "prior_encounter_derived_seizure_free_duration" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 6 month")


def test_build_projection_render_traces_renderable_prior_encounter_interval() -> None:
    row = {
        "source_row_index": 41,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:41:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {
                "source_normalized_phrase": (
                    "no events suggestive of seizures since his last review twelve months ago"
                )
            },
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            41: CandidateSet(
                source_row_index=41,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2025-09-21"),
                candidates=[
                    _seizure_free_candidate(
                        41,
                        "llm:41:1",
                        ("No events suggestive of seizures since last review twelve months ago."),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "prior_encounter_derived_seizure_free_duration" in assessment["normalization_issues"]
    assert artifact_row["final_rendered_label"]["rendered_label"] == ("seizure free for 12 month")


def test_build_projection_render_keeps_relative_since_anchor_unresolved() -> None:
    row = {
        "source_row_index": 27,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:27:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "no seizures since last visit"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            27: CandidateSet(
                source_row_index=27,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context("2026-06-06"),
                candidates=[
                    _seizure_free_candidate(
                        27,
                        "llm:27:1",
                        "She has had no seizures since last visit.",
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert "seizure_free_since_date_anchor_unparsed" in assessment["normalization_issues"]
    assert assessment["seizure_free_instrumentation"]["state_kind"] == ("unresolved_anchor")
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def test_build_projection_render_prior_encounter_context_ablation() -> None:
    row = {
        "source_row_index": 42,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": "test_prompt",
        "schema_version": "test_schema",
        "parse_errors": [],
        "assessment_draft": {
            "assessment_kind": "seizure_free",
            "primary_candidate_ids": ["llm:42:1"],
            "supporting_candidate_ids": [],
            "rejected_candidate_ids": [],
            "aggregation_policy": "seizure_free_state",
            "normalized_burden": {"source_normalized_phrase": "No seizures since last visit"},
        },
    }

    artifact_row = projection_render.build_projection_render_row(
        row,
        candidate_sets={
            42: CandidateSet(
                source_row_index=42,
                component_owner="candidate_set_union",
                source_artifacts=["test"],
                row_context=_row_context(
                    "2021-11-05",
                    prior_encounter_date="2021-05-05",
                    prior_encounter_phrase="last appointment six months ago",
                ),
                candidates=[
                    _seizure_free_candidate(
                        42,
                        "llm:42:1",
                        "No seizures since last visit.",
                    )
                ],
            )
        },
        disabled_ablation_switches={"normalize_seizure_free_prior_encounter_anchor"},
    )

    assessment = artifact_row["clinical_assessment"]
    instrumentation = assessment["seizure_free_instrumentation"]
    assert (
        "ablation_switch_disabled:normalize_seizure_free_prior_encounter_anchor"
        in assessment["normalization_issues"]
    )
    assert instrumentation["state_kind"] == "unresolved_anchor"
    assert artifact_row["final_rendered_label"]["rendered_label"] is None
