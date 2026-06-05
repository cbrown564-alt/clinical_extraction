from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
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
        candidate_set=_candidate_set(10),
    )

    assert projection.projected_label_semantics == "4 per day"
    assert projection.projection_basis == "frequency_rate"
    assert projection.source_ids == ["note:10:span:0-20"]
    assert rendered.rendered_label == "4 per day"
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
    assert projection.projected_label_semantics == "1 per 7 to 9 day"
    assert rendered.rendered_label == "1 per 7 to 9 day"


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


def _candidate_set(
    source_row_index: int,
    *,
    evidence: str = "two seizures per month",
) -> CandidateSet:
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
                candidate_kind="frequency_rate",
                event_type="seizure",
                frequency=FrequencyDetails(source_phrase=evidence),
                temporality="current",
                certainty="certain",
                assertion_status="asserted",
                evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=20),
                source_ids=[f"note:{source_row_index}:span:0-20"],
                clinical_or_policy="clinical",
            )
        ],
    )
