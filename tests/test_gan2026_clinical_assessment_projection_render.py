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


def test_project_and_render_frequency_rate_label() -> None:
    assessment = ClinicalAssessment(
        source_row_index=10,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:10:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=4,
            count_high=4,
            period_low=1,
            period_high=1,
            period_unit="day",
            source_normalized_phrase="up to four seizures per day",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(10, evidence="up to four seizures per day"),
    )

    assert projection.projected_label_semantics == "4 per day"
    assert projection.projection_basis == "frequency_rate"
    assert projection.projection_owner == "rate_projection_policy"
    assert projection.projection_rule_id == "frequency_rate_values_v0"
    assert projection.source_ids == ["note:10:span:0-20"]
    assert projection.selected_evidence_status == {
        "exact_trace": True,
        "source_id_status": "valid",
        "source_id_trace": {
            "selected_source_ids": ["note:10:span:0-20"],
            "expected_source_ids": ["note:10:span:0-20"],
            "missing_expected_source_ids": [],
            "unexpected_source_ids": [],
            "trace_basis": "primary_candidate_exact_evidence",
        },
    }
    assert rendered.rendered_label == "4 per day"
    assert rendered.projection_owner == "rate_projection_policy"
    assert rendered.scoring_enabled is False


def test_project_and_render_unknown_preserves_internal_state_then_renders_unknown() -> None:
    assessment = ClinicalAssessment(
        source_row_index=11,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="unknown_frequency",
        primary_candidate_ids=[],
        aggregation_policy="unknown_due_to_ambiguity",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="episodes occur most shifts"
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(11),
    )

    assert projection.projection_kind == "unknown_frequency"
    assert projection.projection_basis == "unknown_frequency_internal_state"
    assert projection.projection_owner == "benchmark_renderer"
    assert projection.projected_label_semantics == "unknown"
    assert rendered.rendered_label == "unknown"


def test_project_and_render_requires_seizure_free_duration() -> None:
    assessment = ClinicalAssessment(
        source_row_index=12,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="seizure_free",
        primary_candidate_ids=["llm:12:1"],
        aggregation_policy="seizure_free_state",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="no seizures in current month to date"
        ),
        normalization_issues=["seizure_free_duration_unparsed"],
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(12),
    )

    assert projection.projected_label_semantics == ""
    assert projection.projection_issues == [
        "seizure_free_duration_unparsed",
        "seizure_free_duration_required",
    ]
    assert rendered.rendered_label is None
    assert rendered.render_issues == ["projection_semantics_missing"]


def test_project_and_render_blocks_seizure_free_proxy_evidence() -> None:
    assessment = ClinicalAssessment(
        source_row_index=21,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="seizure_free",
        primary_candidate_ids=["llm:21:1", "llm:21:2"],
        aggregation_policy="seizure_free_state",
        normalized_burden=NormalizedBurden(
            seizure_free_duration_low=7,
            seizure_free_duration_high=7,
            seizure_free_duration_unit="month",
            source_normalized_phrase="seizure free for past seven months",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=CandidateSet(
            source_row_index=21,
            component_owner="candidate_set_union",
            source_artifacts=["test"],
            candidates=[
                _seizure_free_candidate(
                    21,
                    "llm:21:1",
                    "not required in the past seven months",
                ),
                _seizure_free_candidate(
                    21,
                    "llm:21:2",
                    "If breakthrough events recur, she will contact us sooner.",
                    source_ids=["note:21:span:unresolved:1"],
                ),
            ],
        ),
    )

    assert projection.projection_basis == "seizure_free_proxy_evidence"
    assert projection.projection_rule_id == "seizure_free_proxy_evidence_block_v0"
    assert "seizure_free_proxy_evidence_overreach" in projection.projection_issues
    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None


def test_project_and_render_allows_explicit_seizure_free_evidence() -> None:
    assessment = ClinicalAssessment(
        source_row_index=22,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="seizure_free",
        primary_candidate_ids=["llm:22:1"],
        aggregation_policy="seizure_free_state",
        normalized_burden=NormalizedBurden(
            seizure_free_duration_low=7,
            seizure_free_duration_high=7,
            seizure_free_duration_unit="month",
            source_normalized_phrase="no seizures for seven months",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=CandidateSet(
            source_row_index=22,
            component_owner="candidate_set_union",
            source_artifacts=["test"],
            candidates=[
                _seizure_free_candidate(
                    22,
                    "llm:22:1",
                    "She has had no seizures for seven months.",
                ),
            ],
        ),
    )

    assert projection.projection_basis == "seizure_free_duration"
    assert projection.projected_label_semantics == "seizure free for 7 month"
    assert rendered.rendered_label == "seizure free for 7 month"


def test_project_and_render_cluster_cadence_without_size_as_simple_rate() -> None:
    assessment = ClinicalAssessment(
        source_row_index=13,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:13:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            cluster_count_low=1,
            cluster_count_high=1,
            cluster_period_low=7,
            cluster_period_high=9,
            cluster_period_unit="day",
            source_normalized_phrase="clusters every 7 to 9 days",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(13),
    )

    assert projection.projection_basis == "cluster_cadence_without_size"
    assert projection.projection_owner == "cluster_projection_policy"
    assert (
        projection.projection_rule_id
        == "cluster_cadence_default_multiple_per_cluster_v0"
    )
    assert projection.projected_label_semantics == "1 cluster per 7 to 9 day, multiple per cluster"
    assert rendered.rendered_label == "1 cluster per 7 to 9 day, multiple per cluster"


def test_project_and_render_blocks_medication_cadence_cluster_projection() -> None:
    assessment = ClinicalAssessment(
        source_row_index=16,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:16:1"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            cluster_period_low=1,
            cluster_period_high=1,
            cluster_period_unit="month",
            source_normalized_phrase="clusters approximately once monthly",
        ),
        normalization_issues=["cluster_frequency_values_unparsed"],
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            16,
            evidence=(
                "Clobazam 5 mg at night as needed for clusters "
                "(patient-led use approximately once monthly)"
            ),
            candidate_kind="cluster_frequency",
        ),
    )

    assert projection.projection_owner == "cluster_projection_policy"
    assert "medication_cadence_ambiguity" in projection.projection_issues
    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None


def test_project_and_render_unknown_cadence_multiple_per_cluster() -> None:
    assessment = ClinicalAssessment(
        source_row_index=17,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:17:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "cluster of multiple short seizure episodes over one day"
            ),
        ),
        normalization_issues=["cluster_frequency_values_unparsed"],
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            17,
            evidence=(
                "a cluster of events over a single day, reporting multiple short "
                "episodes within that 24-hour period"
            ),
            candidate_kind="cluster_frequency",
            events_per_cluster="multiple short episodes within that 24-hour period",
            cluster_frequency="cluster of events over a single day",
            cluster_period="single day",
        ),
    )

    assert projection.projection_owner == "cluster_projection_policy"
    assert projection.projection_basis == "unknown_cadence_cluster_burden"
    assert projection.projection_rule_id == "unknown_cadence_multiple_per_cluster_v0"
    assert projection.projected_label_semantics == "unknown, multiple per cluster"
    assert rendered.rendered_label == "unknown, multiple per cluster"


def test_project_and_render_cyclic_window_without_event_count_routes() -> None:
    assessment = ClinicalAssessment(
        source_row_index=18,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:18:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizures happen perimenstrually only"
        ),
        normalization_issues=["cluster_frequency_values_unparsed"],
    )

    # 1. Default routing (switch enabled)
    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            18,
            evidence="Seizures happen when perimenstrual only (days -3 to +3).",
            candidate_kind="cluster_frequency",
            cluster_frequency="perimenstrual only (days -3 to +3)",
        ),
    )

    assert projection.projection_basis == "cyclic_window_pattern"
    assert projection.projection_rule_id == "cyclic_window_pattern_routed_v0"
    assert "cyclic_window_pattern_routed" in projection.projection_issues
    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None

    # 2. Revert to old behavior when ablation switch is disabled
    projection_ablated, rendered_ablated = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            18,
            evidence="Seizures happen when perimenstrual only (days -3 to +3).",
            candidate_kind="cluster_frequency",
            cluster_frequency="perimenstrual only (days -3 to +3)",
        ),
        disabled_ablation_switches=frozenset(["route_cyclic_window_patterns"]),
    )

    assert projection_ablated.projection_basis == "cluster_frequency"
    assert projection_ablated.projection_rule_id == "cluster_cadence_values_required_v0"
    assert "cyclic_window_without_event_count" in projection_ablated.projection_issues
    assert rendered_ablated.rendered_label is None


def test_project_and_render_sleep_restricted_pattern_routes() -> None:
    assessment = ClinicalAssessment(
        source_row_index=180,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:180:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizures after sleep deprivation"
        ),
        normalization_issues=["cluster_frequency_values_unparsed"],
    )

    # 1. Default routing (switch enabled)
    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            180,
            evidence="seizures only reported after sleep deprivation",
            candidate_kind="cluster_frequency",
            cluster_frequency="after sleep deprivation",
        ),
    )

    assert projection.projection_basis == "sleep_restricted_pattern"
    assert projection.projection_rule_id == "sleep_restricted_pattern_routed_v0"
    assert "sleep_restricted_pattern_routed" in projection.projection_issues
    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None

    # 2. Revert to old behavior when ablation switch is disabled
    projection_ablated, rendered_ablated = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            180,
            evidence="seizures only reported after sleep deprivation",
            candidate_kind="cluster_frequency",
            cluster_frequency="after sleep deprivation",
        ),
        disabled_ablation_switches=frozenset(["route_sleep_restricted_patterns"]),
    )

    assert projection_ablated.projection_basis == "cluster_frequency"
    assert projection_ablated.projection_rule_id == "cluster_cadence_values_required_v0"
    assert rendered_ablated.rendered_label is None


def test_project_and_render_cyclic_pattern_with_explicit_operands() -> None:
    assessment = ClinicalAssessment(
        source_row_index=181,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:181:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            cluster_count_low=3,
            cluster_count_high=3,
            cluster_period_low=1,
            cluster_period_high=1,
            cluster_period_unit="month",
            source_normalized_phrase="three clusters per month perimenstrually"
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            181,
            evidence="three clusters per month perimenstrually",
            candidate_kind="cluster_frequency",
            cluster_frequency="perimenstrually",
        ),
    )

    assert projection.projection_rule_id == "cyclic_pattern_with_explicit_operands_rendered_v0"
    assert projection.projected_label_semantics == "3 cluster per month, multiple per cluster"
    assert rendered.rendered_label == "3 cluster per month, multiple per cluster"



def test_project_and_render_renderable_cluster_beats_unknown_cadence_sentinel() -> None:
    assessment = ClinicalAssessment(
        source_row_index=19,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:19:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            cluster_count_low=1,
            cluster_count_high=1,
            cluster_period_low=2,
            cluster_period_high=2,
            cluster_period_unit="week",
            events_per_cluster_low=3,
            events_per_cluster_high=3,
            source_normalized_phrase="three episodes over the past fortnight",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            19,
            evidence="three short episodes occurring on separate days",
            candidate_kind="cluster_frequency",
            cluster_period="over the past fortnight",
            events_per_cluster="three short episodes",
        ),
    )

    assert projection.projection_basis == "cluster_cadence_with_events_per_cluster"
    assert (
        projection.projection_rule_id
        == "cluster_cadence_with_events_per_cluster_v0"
    )
    assert projection.projected_label_semantics == "1 cluster per 2 week, 3 per cluster"
    assert rendered.rendered_label == "1 cluster per 2 week, 3 per cluster"


def test_project_and_render_dominant_vague_current_burden() -> None:
    assessment = ClinicalAssessment(
        source_row_index=20,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:20:1", "llm:20:2"],
        aggregation_policy="additive_same_window",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase=(
                "brief absences on most weekdays plus one GTC in last 8 weeks"
            ),
        ),
        normalization_issues=["vague_count", "additive_frequency_period_mismatch"],
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=CandidateSet(
            source_row_index=20,
            component_owner="candidate_set_union",
            source_artifacts=["test"],
            candidates=[
                _unknown_candidate(
                    20,
                    "llm:20:1",
                    "Over the past two months she reports brief absences "
                    "occurring on most weekdays",
                    event_type="seizure_like_event",
                ),
                _unknown_candidate(
                    20,
                    "llm:20:2",
                    "There has been one generalised tonic\u2013clonic seizure "
                    "in the last eight weeks",
                ),
            ],
        ),
    )

    assert projection.projection_basis == "dominant_vague_current_burden"
    assert projection.projection_rule_id == "dominant_vague_current_burden_v0"
    assert projection.projected_label_semantics == "multiple per week"
    assert rendered.rendered_label == "multiple per week"


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


def test_project_and_render_marks_absence_rows_as_provenance_not_applicable() -> None:
    assessment = ClinicalAssessment(
        source_row_index=49,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="no_reference",
        primary_candidate_ids=[],
        aggregation_policy="no_reference_boundary",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="No seizure frequency or burden information present"
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(49),
    )

    assert projection.selected_evidence_status == {
        "exact_trace": None,
        "source_id_status": "not_applicable",
        "source_id_trace": {
            "selected_source_ids": [],
            "expected_source_ids": [],
            "missing_expected_source_ids": [],
            "unexpected_source_ids": [],
            "trace_basis": "no_primary_candidate",
        },
    }
    assert rendered.rendered_label == "no seizure frequency reference"


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
            "normalized_burden": {
                "source_normalized_phrase": "no seizures since March 2025"
            },
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
        disabled_ablation_switches={
            "normalize_seizure_free_duration_date_instrumentation"
        },
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
            "normalized_burden": {
                "source_normalized_phrase": "no seizures since March 2025"
            },
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
        "seizure_free_duration_instrumented_from_since_date"
        in assessment["normalization_issues"]
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
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 15 month"
    )


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
            "normalized_burden": {
                "source_normalized_phrase": "seizure-free since 29/09/2017"
            },
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
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == (
        "2017-09-29"
    )
    assert assessment["normalized_burden"]["seizure_free_duration_low"] == 96
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 96 month"
    )


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
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 2 month"
    )


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
    assert (
        "seizure_free_anchor_from_last_event_phrase"
        in assessment["normalization_issues"]
    )
    assert (
        "seizure_free_anchor_year_inferred_from_reference_date"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 4 month"
    )


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
        "seizure_free_anchor_approximate_start_month_policy"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 4 month"
    )


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
                "source_normalized_phrase": (
                    "she cannot recall any episodes since early 2024"
                )
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
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == (
        "2024-01"
    )
    assert (
        "seizure_free_anchor_approximate_start_month_policy"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 21 month"
    )


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
    assert assessment["seizure_free_instrumentation"]["anchor_date"]["date"] == (
        "2025-01"
    )
    assert (
        "seizure_free_anchor_approximate_start_month_policy"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 9 month"
    )


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
                "source_normalized_phrase": (
                    "no further seizures since starting current regimen"
                )
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
    assert (
        "seizure_free_anchor_from_event_phrase"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 4 month"
    )


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
            "normalized_burden": {
                "source_normalized_phrase": "complete seizure control"
            },
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
    assert instrumentation["anchor_date"]["source"] == (
        "seizure_free_event_anchor_month_year"
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 31 month"
    )


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
            "normalized_burden": {
                "source_normalized_phrase": "no events over the last year"
            },
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
    assert (
        "seizure_free_anchor_from_last_event_phrase"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 29 month"
    )


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
        "The patient experienced 2 to 3 seizures shortly after "
        "discontinuing valproate on 10 Jul"
    )
    assert (
        "seizure_free_anchor_from_same_note_antecedent"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 2 month"
    )


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
    assert assessment["seizure_free_instrumentation"]["state_kind"] == (
        "unresolved_anchor"
    )
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
            "normalized_burden": {
                "source_normalized_phrase": "seizure-free for over 4 weeks"
            },
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
    assert (
        "seizure_free_anchor_from_same_note_antecedent"
        not in assessment["normalization_issues"]
    )


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
            "normalized_burden": {
                "source_normalized_phrase": "No seizures since last visit"
            },
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
    assert (
        "prior_encounter_derived_seizure_free_duration"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 6 month"
    )


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
                    "no events suggestive of seizures since his last review "
                    "twelve months ago"
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
                        (
                            "No events suggestive of seizures since last review "
                            "twelve months ago."
                        ),
                    )
                ],
            )
        },
    )

    assessment = artifact_row["clinical_assessment"]
    assert (
        "prior_encounter_derived_seizure_free_duration"
        in assessment["normalization_issues"]
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] == (
        "seizure free for 12 month"
    )


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
            "normalized_burden": {
                "source_normalized_phrase": "no seizures since last visit"
            },
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
    assert (
        "seizure_free_since_date_anchor_unparsed"
        in assessment["normalization_issues"]
    )
    assert assessment["seizure_free_instrumentation"]["state_kind"] == (
        "unresolved_anchor"
    )
    assert artifact_row["final_rendered_label"]["rendered_label"] is None


def _candidate_set(
    source_row_index: int,
    *,
    evidence: str = "two seizures per month",
    candidate_kind: str = "frequency_rate",
    cluster_frequency: str = "approximately once monthly",
    cluster_period: str | None = None,
    events_per_cluster: str | None = None,
) -> CandidateSet:
    frequency = (
        FrequencyDetails(source_phrase=evidence)
        if candidate_kind == "frequency_rate"
        else None
    )
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["test"],
        candidates=[
            ExtractedCandidate(
                candidate_id=f"llm:{source_row_index}:1",
                component_owner="test",
                source_type="llm_candidate",
                source_artifact="test",
                source_row_index=source_row_index,
                candidate_kind=candidate_kind,
                event_type="seizure",
                frequency=frequency,
                cluster_details=(
                    {
                        "cluster_frequency": cluster_frequency,
                        "events_per_cluster": events_per_cluster,
                        "cluster_count": None,
                        "cluster_period": cluster_period,
                    }
                    if candidate_kind == "cluster_frequency"
                    else None
                ),
                temporality="current",
                certainty="certain",
                assertion_status="asserted",
                evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=20),
                source_ids=[f"note:{source_row_index}:span:0-20"],
                clinical_or_policy="clinical",
            )
        ],
    )


def _row_context(
    reference_date: str,
    *,
    prior_encounter_date: str | None = None,
    prior_encounter_phrase: str | None = None,
) -> RowContext:
    return RowContext(
        reference_date=ReferenceDateContext(
            date=reference_date,
            date_precision="day",
            source="note_header",
            source_phrase=f"Clinic Date: {reference_date}",
            source_span=EvidenceSpan(
                text=f"Clinic Date: {reference_date}",
                start_char=0,
                end_char=len(f"Clinic Date: {reference_date}"),
            ),
        ),
        prior_encounter=(
            PriorEncounterContext(
                date=prior_encounter_date,
                date_precision="day",
                source="explicit_relative_interval",
                source_phrase=prior_encounter_phrase or "",
                source_span=EvidenceSpan(
                    text=prior_encounter_phrase or "",
                    start_char=0,
                    end_char=len(prior_encounter_phrase or ""),
                ),
                issues=["prior_encounter_date_inferred_from_relative_interval"],
            )
            if prior_encounter_date is not None
            else None
        ),
    )


def _unknown_candidate(
    source_row_index: int,
    candidate_id: str,
    evidence: str,
    *,
    event_type: str = "seizure",
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="unknown_frequency",
        event_type=event_type,
        unknown_frequency=SourcePhraseOnlyDetails(source_phrase=evidence),
        temporality="recent",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _seizure_free_candidate(
    source_row_index: int,
    candidate_id: str,
    evidence: str,
    *,
    source_ids: list[str] | None = None,
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="seizure_free",
        event_type="seizure",
        seizure_free=SeizureFreeDetails(source_phrase=evidence),
        temporality="recent",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=source_ids or [f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def test_project_and_render_ytd_denominator_normalizes_to_months() -> None:
    assessment = ClinicalAssessment(
        source_row_index=101,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:101:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            source_normalized_phrase="6 seizures so far this year",
        ),
    )

    candidate_set = _candidate_set(101, evidence="6 seizures so far this year")
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    assert projection.projected_label_semantics == "6 per 4 month"
    assert projection.projection_basis == "date_anchored_ytd_denominator"
    assert projection.projection_rule_id == "date_anchored_ytd_denominator_v0"
    assert projection.ytd_instrumentation == {
        "ytd_anchor_start": "2026-01-01",
        "ytd_reference_date": "2026-04-15",
        "elapsed_months": 4,
        "source_phrase": "6 seizures so far this year",
        "candidate_id": "llm:101:1",
    }
    assert rendered.rendered_label == "6 per 4 month"


def test_project_and_render_ytd_denominator_ablation() -> None:
    assessment = ClinicalAssessment(
        source_row_index=102,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:102:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            source_normalized_phrase="6 seizures so far this year",
        ),
    )

    candidate_set = _candidate_set(102, evidence="6 seizures so far this year")
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
        disabled_ablation_switches={"project_date_anchored_ytd_denominator"},
    )

    # When ablated, it should fall back to the baseline projection path without synthetic issues.
    assert projection.projected_label_semantics == ""
    assert projection.ytd_instrumentation is None
    assert rendered.rendered_label is None


def test_project_and_render_ytd_denominator_missing_reference_date() -> None:
    assessment = ClinicalAssessment(
        source_row_index=103,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:103:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            source_normalized_phrase="6 seizures so far this year",
        ),
    )

    candidate_set = _candidate_set(103, evidence="6 seizures so far this year")
    candidate_set.row_context = RowContext(context_issues=["reference_date_missing"])

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None


def test_project_and_render_ytd_denominator_non_ytd_yearly_phrase() -> None:
    assessment = ClinicalAssessment(
        source_row_index=104,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:104:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            source_normalized_phrase="6 seizures per year",
        ),
    )

    candidate_set = _candidate_set(104, evidence="6 seizures per year")
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    # Since it's not YTD, it shouldn't trigger G1.
    # It might still render if the standard parser handles it.
    assert projection.projection_rule_id != "date_anchored_ytd_denominator_v0"


def test_project_and_render_ytd_explicit_denominator_wins_over_ytd_phrase() -> None:
    assessment = ClinicalAssessment(
        source_row_index=105,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:105:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            period_low=7,
            period_high=7,
            period_unit="month",
            source_normalized_phrase="6 seizures over 7 months so far this year",
        ),
    )

    candidate_set = _candidate_set(
        105,
        evidence="6 seizures over 7 months so far this year",
    )
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    assert projection.projection_rule_id == "frequency_rate_values_v0"
    assert projection.projected_label_semantics == "6 per 7 month"
    assert projection.ytd_instrumentation is None
    assert rendered.rendered_label == "6 per 7 month"


def test_project_and_render_ytd_overrides_normalized_annual_period() -> None:
    assessment = ClinicalAssessment(
        source_row_index=106,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:106:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=6,
            count_high=6,
            period_low=1,
            period_high=1,
            period_unit="year",
            source_normalized_phrase="6 seizures so far this year",
        ),
    )

    candidate_set = _candidate_set(106, evidence="6 seizures so far this year")
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    assert projection.projected_label_semantics == "6 per 4 month"
    assert projection.projection_rule_id == "date_anchored_ytd_denominator_v0"
    assert rendered.rendered_label == "6 per 4 month"


def test_project_and_render_plain_this_year_phrase_triggers_ytd() -> None:
    assessment = ClinicalAssessment(
        source_row_index=107,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:107:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            count_low=7,
            count_high=7,
            period_low=1,
            period_high=1,
            period_unit="year",
            source_normalized_phrase="seven generalised tonic-clonic seizures this year",
        ),
    )

    candidate_set = _candidate_set(
        107,
        evidence="seven generalised tonic-clonic seizures this year",
    )
    candidate_set.row_context = _row_context("2026-04-15")

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=candidate_set,
    )

    assert projection.projected_label_semantics == "7 per 4 month"
    assert projection.projection_rule_id == "date_anchored_ytd_denominator_v0"
    assert rendered.rendered_label == "7 per 4 month"


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
            "normalized_burden": {
                "source_normalized_phrase": "No seizures since last visit"
            },
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


def test_project_and_render_cluster_cadence_default_multiple_per_cluster() -> None:
    assessment = ClinicalAssessment(
        source_row_index=13,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:13:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            cluster_count_low=1,
            cluster_count_high=1,
            cluster_period_low=7,
            cluster_period_high=9,
            cluster_period_unit="day",
            source_normalized_phrase="clusters every 7 to 9 days",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(13),
    )

    assert projection.projection_basis == "cluster_cadence_without_size"
    assert projection.projection_owner == "cluster_projection_policy"
    assert (
        projection.projection_rule_id
        == "cluster_cadence_default_multiple_per_cluster_v0"
    )
    assert projection.projected_label_semantics == "1 cluster per 7 to 9 day, multiple per cluster"
    assert rendered.rendered_label == "1 cluster per 7 to 9 day, multiple per cluster"


def test_project_and_render_cluster_cadence_default_multiple_per_cluster_ablation() -> None:
    assessment = ClinicalAssessment(
        source_row_index=13,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:13:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            cluster_count_low=1,
            cluster_count_high=1,
            cluster_period_low=7,
            cluster_period_high=9,
            cluster_period_unit="day",
            source_normalized_phrase="clusters every 7 to 9 days",
        ),
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(13),
        disabled_ablation_switches={"project_cluster_cadence_default_multiple_per_cluster"},
    )

    assert projection.projection_basis == "cluster_cadence_without_size"
    assert projection.projection_owner == "cluster_projection_policy"
    assert (
        projection.projection_rule_id
        == "cluster_cadence_as_event_rate_when_size_absent_v0"
    )
    assert projection.projected_label_semantics == "1 per 7 to 9 day"
    assert rendered.rendered_label == "1 per 7 to 9 day"




