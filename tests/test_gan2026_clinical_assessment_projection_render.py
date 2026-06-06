from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
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
        candidate_set=_candidate_set(10),
    )

    assert projection.projected_label_semantics == "4 per day"
    assert projection.projection_basis == "frequency_rate"
    assert projection.projection_owner == "rate_projection_policy"
    assert projection.projection_rule_id == "frequency_rate_operands_v0"
    assert projection.source_ids == ["note:10:span:0-20"]
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
        == "cluster_cadence_as_event_rate_when_size_absent_v0"
    )
    assert projection.projected_label_semantics == "1 per 7 to 9 day"
    assert rendered.rendered_label == "1 per 7 to 9 day"


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
        normalization_issues=["cluster_frequency_operands_unparsed"],
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
        normalization_issues=["cluster_frequency_operands_unparsed"],
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


def test_project_and_render_cyclic_window_without_event_count_stays_null() -> None:
    assessment = ClinicalAssessment(
        source_row_index=18,
        component_owner="llm_candidate_set_clinical_assessment",
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:18:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizures happen perimenstrually only"
        ),
        normalization_issues=["cluster_frequency_operands_unparsed"],
    )

    projection, rendered = projection_render.project_and_render(
        assessment,
        candidate_set=_candidate_set(
            18,
            evidence="Seizures happen when perimenstrual only (days -3 to +3).",
            candidate_kind="cluster_frequency",
            cluster_frequency="perimenstrual only (days -3 to +3)",
        ),
    )

    assert projection.projection_basis == "cluster_frequency"
    assert "cyclic_window_without_event_count" in projection.projection_issues
    assert projection.projected_label_semantics == ""
    assert rendered.rendered_label is None


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
