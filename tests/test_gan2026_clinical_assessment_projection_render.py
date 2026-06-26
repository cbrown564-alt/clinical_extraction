"""Routing and direct project_and_render tests for Gan2026 clinical assessment."""

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
