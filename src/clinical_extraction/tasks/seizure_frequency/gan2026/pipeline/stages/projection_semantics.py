"""Core projection semantics for ClinicalAssessment label projection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    ProjectionOwner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    evidence_gating,
    label_render,
)


@dataclass(frozen=True)
class ProjectionOutcome:
    label: str | None
    basis: str
    owner: ProjectionOwner
    rule_id: str
    issues: list[str]
    ytd_instrumentation: dict[str, Any] | None = None


def project_label_semantics(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> ProjectionOutcome:
    disabled_switches = frozenset(disabled_ablation_switches or ())
    burden = assessment.normalized_burden
    if assessment.assessment_kind == "frequency_rate":
        dominant_vague_label = evidence_gating.dominant_vague_current_burden_label(
            assessment,
            candidate_set,
        )
        if dominant_vague_label is not None:
            return ProjectionOutcome(
                dominant_vague_label,
                "dominant_vague_current_burden",
                "rate_projection_policy",
                "dominant_vague_current_burden_v0",
                [],
            )

        by_id = {
            candidate.candidate_id: candidate for candidate in candidate_set.candidates
        }
        primary_candidates = [
            by_id[cid] for cid in assessment.primary_candidate_ids if cid in by_id
        ]

        ytd_candidate = None
        for candidate in primary_candidates:
            phrase = " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
            if is_ytd_phrase(phrase):
                ytd_candidate = candidate
                break

        is_ytd = ytd_candidate is not None or is_ytd_phrase(
            burden.source_normalized_phrase
        )
        explicit_period_blocks_ytd = has_explicit_rate_period(
            burden
        ) and not has_overrideable_ytd_annual_period(burden)
        if is_ytd and not explicit_period_blocks_ytd:
            ref_date_ctx = candidate_set.row_context.reference_date
            if ref_date_ctx is not None:
                if "project_date_anchored_ytd_denominator" not in disabled_switches:
                    try:
                        ref_date = date.fromisoformat(ref_date_ctx.date)
                        elapsed_months = ref_date.month
                        ytd_burden = burden.model_copy(
                            update={
                                "period_low": float(elapsed_months),
                                "period_high": float(elapsed_months),
                                "period_unit": "month",
                            }
                        )
                        label = label_render.rate_label(ytd_burden)
                        if label is not None:
                            source_phrase = (
                                ytd_candidate.evidence_span.text
                                if ytd_candidate
                                else burden.source_normalized_phrase
                            )
                            candidate_id = (
                                ytd_candidate.candidate_id
                                if ytd_candidate
                                else (
                                    assessment.primary_candidate_ids[0]
                                    if assessment.primary_candidate_ids
                                    else "unknown"
                                )
                            )
                            return ProjectionOutcome(
                                label,
                                "date_anchored_ytd_denominator",
                                "rate_projection_policy",
                                "date_anchored_ytd_denominator_v0",
                                [],
                                ytd_instrumentation={
                                    "ytd_anchor_start": f"{ref_date.year}-01-01",
                                    "ytd_reference_date": ref_date_ctx.date,
                                    "elapsed_months": elapsed_months,
                                    "source_phrase": source_phrase,
                                    "candidate_id": candidate_id,
                                },
                            )
                    except ValueError:
                        pass

        label = label_render.rate_label(burden)
        if label is None:
            is_cyclic = evidence_gating.has_primary_cyclic_window_pattern_general(
                assessment,
                candidate_set,
            )
            is_sleep = evidence_gating.has_primary_sleep_restricted_pattern(
                assessment,
                candidate_set,
            )
            if is_cyclic and "route_cyclic_window_patterns" not in disabled_switches:
                return ProjectionOutcome(
                    None,
                    "cyclic_window_pattern",
                    "boundary_projection_policy",
                    "cyclic_window_pattern_routed_v0",
                    ["cyclic_window_pattern_routed"],
                )
            if is_sleep and "route_sleep_restricted_patterns" not in disabled_switches:
                return ProjectionOutcome(
                    None,
                    "sleep_restricted_pattern",
                    "boundary_projection_policy",
                    "sleep_restricted_pattern_routed_v0",
                    ["sleep_restricted_pattern_routed"],
                )
            return ProjectionOutcome(
                None,
                "frequency_rate",
                "rate_projection_policy",
                "frequency_rate_values_v0",
                ["frequency_rate_values_incomplete"],
            )
        rule_id = "frequency_rate_values_v0"
        is_cyclic = evidence_gating.has_primary_cyclic_window_pattern_general(
            assessment,
            candidate_set,
        )
        if is_cyclic and "route_cyclic_window_patterns" not in disabled_switches:
            rule_id = "cyclic_pattern_with_explicit_operands_rendered_v0"
        return ProjectionOutcome(
            label,
            "frequency_rate",
            "rate_projection_policy",
            rule_id,
            [],
        )
    if assessment.assessment_kind == "cluster_frequency":
        return cluster_label(
            assessment,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_switches,
        )
    if assessment.assessment_kind == "seizure_free":
        label = label_render.seizure_free_label(burden)
        if label is None:
            return ProjectionOutcome(
                None,
                "seizure_free_duration",
                "boundary_projection_policy",
                "seizure_free_duration_required_v0",
                ["seizure_free_duration_required"],
            )
        if evidence_gating.has_seizure_free_proxy_evidence_overreach(
            assessment,
            candidate_set,
        ):
            return ProjectionOutcome(
                None,
                "seizure_free_proxy_evidence",
                "boundary_projection_policy",
                "seizure_free_proxy_evidence_block_v0",
                ["seizure_free_proxy_evidence_overreach"],
            )
        return ProjectionOutcome(
            label,
            "seizure_free_duration",
            "boundary_projection_policy",
            "seizure_free_duration_projection_v0",
            [],
        )
    if assessment.assessment_kind == "unknown_frequency":
        return ProjectionOutcome(
            "unknown",
            "unknown_frequency_internal_state",
            "benchmark_renderer",
            "unknown_frequency_sentinel_render_v0",
            [],
        )
    if assessment.assessment_kind == "no_reference":
        return ProjectionOutcome(
            "no seizure frequency reference",
            "no_reference_internal_state",
            "benchmark_renderer",
            "no_reference_sentinel_render_v0",
            [],
        )
    return ProjectionOutcome(
        None,
        "unresolved_multiple",
        "benchmark_renderer",
        "unresolved_multiple_no_render_v0",
        ["unresolved_multiple_not_renderable"],
    )


def cluster_label(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> ProjectionOutcome:
    burden = assessment.normalized_burden
    medication_cadence = evidence_gating.has_primary_medication_cadence(
        assessment,
        candidate_set,
    )
    if (
        not medication_cadence
        and not evidence_gating.has_normalized_cluster_cadence(burden)
        and evidence_gating.has_unknown_cadence_multiple_cluster_burden(
            assessment,
            candidate_set,
        )
    ):
        return ProjectionOutcome(
            "unknown, multiple per cluster",
            "unknown_cadence_cluster_burden",
            "cluster_projection_policy",
            "unknown_cadence_multiple_per_cluster_v0",
            ["cluster_cadence_unknown_with_per_cluster_burden"],
        )
    cyclic_window = evidence_gating.has_primary_cyclic_vulnerability_window(
        assessment,
        candidate_set,
    )
    if (
        burden.cluster_count_low is None
        or burden.cluster_count_high is None
        or burden.cluster_period_low is None
        or burden.cluster_period_high is None
        or burden.cluster_period_unit is None
    ):
        if cyclic_window and "route_cyclic_window_patterns" not in disabled_ablation_switches:
            return ProjectionOutcome(
                None,
                "cyclic_window_pattern",
                "boundary_projection_policy",
                "cyclic_window_pattern_routed_v0",
                ["cyclic_window_pattern_routed"],
            )
        is_sleep = evidence_gating.has_primary_sleep_restricted_pattern(
            assessment,
            candidate_set,
        )
        if is_sleep and "route_sleep_restricted_patterns" not in disabled_ablation_switches:
            return ProjectionOutcome(
                None,
                "sleep_restricted_pattern",
                "boundary_projection_policy",
                "sleep_restricted_pattern_routed_v0",
                ["sleep_restricted_pattern_routed"],
            )
        issues = ["cluster_cadence_values_incomplete"]
        if medication_cadence:
            issues.append("medication_cadence_ambiguity")
        if cyclic_window:
            issues.append("cyclic_window_without_event_count")
        return ProjectionOutcome(
            None,
            "cluster_frequency",
            "cluster_projection_policy",
            "cluster_cadence_values_required_v0",
            issues,
        )
    cadence = (
        f"{label_render.format_range(burden.cluster_count_low, burden.cluster_count_high)} "
        f"cluster per {label_render.format_cluster_period(burden)}"
    )
    if burden.events_per_cluster_low is None or burden.events_per_cluster_high is None:
        if medication_cadence:
            return ProjectionOutcome(
                None,
                "cluster_frequency",
                "cluster_projection_policy",
                "cluster_cadence_as_event_rate_when_size_absent_v0",
                ["medication_cadence_ambiguity"],
            )
        if "project_cluster_cadence_default_multiple_per_cluster" not in disabled_ablation_switches:
            default_cluster_label = f"{cadence}, multiple per cluster"
            rule_id = "cluster_cadence_default_multiple_per_cluster_v0"
            if cyclic_window and "route_cyclic_window_patterns" not in disabled_ablation_switches:
                rule_id = "cyclic_pattern_with_explicit_operands_rendered_v0"
            return ProjectionOutcome(
                default_cluster_label,
                "cluster_cadence_without_size",
                "cluster_projection_policy",
                rule_id,
                [],
            )
        simple_rate = (
            f"{label_render.format_range(burden.cluster_count_low, burden.cluster_count_high)} "
            f"per {label_render.format_cluster_period(burden)}"
        )
        return ProjectionOutcome(
            simple_rate,
            "cluster_cadence_without_size",
            "cluster_projection_policy",
            "cluster_cadence_as_event_rate_when_size_absent_v0",
            [],
        )
    label = (
        f"{cadence}, "
        f"{label_render.format_range(burden.events_per_cluster_low, burden.events_per_cluster_high)} "
        "per cluster"
    )
    rule_id = "cluster_cadence_with_events_per_cluster_v0"
    if cyclic_window and "route_cyclic_window_patterns" not in disabled_ablation_switches:
        rule_id = "cyclic_pattern_with_explicit_operands_rendered_v0"
    return ProjectionOutcome(
        label,
        "cluster_cadence_with_events_per_cluster",
        "cluster_projection_policy",
        rule_id,
        [],
    )


def is_ytd_phrase(phrase: str) -> bool:
    lower = phrase.strip().lower()
    return bool(
        re.search(
            (
                r"\b(?:ytd|year[- ]to[- ]date|so far this year|this year so far|"
                r"since the beginning of the year|since (?:january|jan)|"
                r"this year(?:\b| to date\b))"
            ),
            lower,
        )
    )


def has_explicit_rate_period(burden: NormalizedBurden) -> bool:
    return (
        burden.period_low is not None
        and burden.period_high is not None
        and burden.period_unit is not None
    )


def has_overrideable_ytd_annual_period(burden: NormalizedBurden) -> bool:
    return (
        burden.period_low == 1
        and burden.period_high == 1
        and burden.period_unit == "year"
    )
