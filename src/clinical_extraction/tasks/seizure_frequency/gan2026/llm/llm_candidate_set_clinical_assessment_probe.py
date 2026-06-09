"""LLM clinical-assessment probe over Gan 2026 CandidateSet artifacts."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_set_union import (  # noqa: E501
    build_candidate_set_union_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
    deterministic_candidate_set_from_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    SCHEMA_VERSION,
    AggregationPolicy,
    AntecedentReference,
    AssessmentKind,
    ClinicalAssessment,
    ComputedDuration,
    DateReference,
    NormalizedBurden,
    SeizureFreeInstrumentation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_text import (
    fallback_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_selector_schema_probe as selector_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_extracted_candidate_schema_probe as candidate_extractor_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)

PROMPT_VERSION = "gan2026_candidate_set_clinical_assessment_probe_v5"
PIPELINE_FAMILY = "llm_candidate_set_clinical_assessment_probe"
NORMALIZATION_POLICY_ID = "gan2026_clinical_assessment_normalization_v0"
DISABLED_SWITCH_ISSUE_PREFIX = "ablation_switch_disabled:"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_validation25_gpt41mini_v0_2026-06-05.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_validation25_gpt41mini_v0_2026-06-05.md"
)
DEFAULT_CANDIDATE_SET_JSONL_PATH = selector_probe.DEFAULT_CANDIDATE_SET_JSONL_PATH


class AssessmentDraftBurden(BaseModel):
    """Lenient model-facing burden draft.

    The final ClinicalAssessment still uses the strict NormalizedBurden contract.
    This draft only preserves the source-near phrase; deterministic assembly owns
    parsed values.
    """

    model_config = ConfigDict(extra="ignore")

    count_low: float | None = None
    count_high: float | None = None
    vague_count: str | None = None
    period_low: float | None = None
    period_high: float | None = None
    period_unit: str | None = None
    seizure_free_duration_low: float | None = None
    seizure_free_duration_high: float | None = None
    seizure_free_duration_unit: str | None = None
    cluster_count_low: float | None = None
    cluster_count_high: float | None = None
    cluster_period_low: float | None = None
    cluster_period_high: float | None = None
    cluster_period_unit: str | None = None
    events_per_cluster_low: float | None = None
    events_per_cluster_high: float | None = None
    source_normalized_phrase: str = ""

    @field_validator(
        "period_unit",
        "seizure_free_duration_unit",
        "cluster_period_unit",
        mode="before",
    )
    @classmethod
    def _normalise_unit(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower().replace("_", " ")
        singular = {
            "days": "day",
            "weeks": "week",
            "months": "month",
            "years": "year",
        }.get(normalized, normalized)
        return singular if singular in {"day", "week", "month", "year"} else None


class AssessmentDraft(BaseModel):
    """Model-owned clinical assessment fields."""

    model_config = ConfigDict(extra="ignore")

    assessment_kind: AssessmentKind
    primary_candidate_ids: list[str]
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    aggregation_policy: AggregationPolicy | None = None
    normalized_burden: AssessmentDraftBurden
    assessment_summary: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)

    @field_validator("normalized_burden", mode="before")
    @classmethod
    def _accept_final_burden_model(cls, value: object) -> object:
        if isinstance(value, NormalizedBurden):
            return value.model_dump()
        return value


class Gan2026CandidateSetClinicalAssessmentSignature(dspy.Signature):
    """Synthesize a clinical seizure-burden assessment from a CandidateSet."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    source_row_index: int = dspy.InputField(desc="Source row index.")
    task_instructions: list[str] = dspy.InputField(desc="Assessment instructions.")
    policy_examples: list[dict[str, str]] = dspy.InputField(
        desc="General examples of grouping and non-grouping policy."
    )
    candidate_set: dict[str, Any] = dspy.InputField(desc="Source-near candidates.")
    output_contract: dict[str, Any] = dspy.InputField(desc="ClinicalAssessment contract.")
    assessment_draft: AssessmentDraft = dspy.OutputField(
        desc="Clinical assessment draft only."
    )


class DspyCandidateSetClinicalAssessment(dspy.Module):
    """DSPy typed-output clinical assessment probe."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026CandidateSetClinicalAssessmentSignature)

    def forward(
        self,
        *,
        note_text: str,
        source_row_index: int,
        task_instructions: list[str],
        policy_examples: list[dict[str, str]],
        candidate_set: dict[str, Any],
        output_contract: dict[str, Any],
    ) -> dspy.Prediction:
        return self.predict(
            note_text=note_text,
            source_row_index=source_row_index,
            task_instructions=task_instructions,
            policy_examples=policy_examples,
            candidate_set=candidate_set,
            output_contract=output_contract,
        )


def build_assessment_inputs(
    record: GanFrequencyRecord,
    candidate_set: CandidateSet,
) -> dict[str, Any]:
    """Build model-facing clinical-assessment inputs."""

    return {
        "note_text": record.note_text,
        "source_row_index": record.source_row_index,
        "task_instructions": [
            (
                "Review the candidate facts and produce one overarching clinical "
                "assessment of the patient's current seizure frequency burden."
            ),
            (
                "You own the clinical synthesis: choose the primary fact or facts, "
                "provide a source-near burden phrase, and decide whether related facts "
                "are additive, contextual, rejected, or too ambiguous."
            ),
            (
                "Do not perform parser-like normalization. Deterministic assembly owns "
                "count, range, period, interval, duration, and cluster value parsing."
            ),
            (
                "Use primary_candidate_ids only for facts that determine the "
                "overarching burden. Put corroborating, trigger, subtype, historical, "
                "or non-additive context in supporting_candidate_ids or rejected_candidate_ids."
            ),
            (
                "Use only candidate_id values that appear in the provided CandidateSet. "
                "Never invent, renumber, or guess candidate ids."
            ),
            (
                "Put each candidate id in at most one role. A candidate cannot be both "
                "supporting and rejected."
            ),
            (
                "Group primary candidates only when they should be normalized together "
                "as one burden assessment."
            ),
            (
                "For single_fact, use exactly one primary candidate. For "
                "primary_with_context, use the one current candidate that determines "
                "the burden as primary; put context and non-additive facts in support."
            ),
            (
                "If multiple current primary facts are separate and additive, use "
                "additive_same_window. Do not use primary_with_context for multiple "
                "additive primary facts."
            ),
            (
                "Use additive_same_window only when all primary candidates are concrete "
                "frequency_rate facts. Do not use additive_same_window for vague "
                "unknown_frequency facts such as 'most weekdays' or 'rare'."
            ),
            (
                "If multiple candidates repeat the same current burden in different "
                "parts of the note, use the most specific source-near candidate as "
                "primary and put the corroborating repeat references in support."
            ),
            (
                "Do not use historical candidates as primary for current burden when "
                "a current or recent candidate is available."
            ),
            (
                "When the CandidateSet contains candidates from multiple concurrent seizure "
                "types, select the candidate with the highest frequency as primary — rank by "
                "how often events occur (events per day over events per week over events per "
                "month), not by clinical severity or seizure type. A daily drop attack or "
                "daily absence seizure candidate takes precedence over a weekly or monthly "
                "tonic-clonic seizure candidate. Exception: when candidates form a true "
                "cluster pattern (recurring grouped episodes separated by seizure-free "
                "intervals), use the cluster cadence candidate as primary rather than a "
                "within-cluster daily burst rate."
            ),
            (
                "If the note has no usable frequency candidate, return unknown_frequency "
                "with unknown_due_to_absence or no_reference with no_reference_boundary; "
                "do not return frequency_rate with zero primary candidates."
            ),
            (
                "Do not group a total count with a subtype or subcount that may already "
                "be included in the total."
            ),
            (
                "Do not group a primary frequency with cluster triggers, catamenial "
                "pattern, or seizure-free-outside-window context as additive burden."
            ),
            (
                "normalized_burden and source_normalized_phrase should describe only "
                "the current primary burden. Put historical comparisons, prior "
                "burden, improvement/worsening language, triggers, and other context "
                "in assessment_summary or supporting candidate roles."
            ),
            (
                "When assessment_kind is frequency_rate, do not fill cluster fields. "
                "When assessment_kind is frequency_rate or cluster_frequency, do not "
                "fill seizure_free_duration fields unless seizure freedom is the "
                "primary burden assessment."
            ),
            (
                "For menstrual, sleep, travel, or other recurring risk windows, keep "
                "seizure-free outside-window statements in supporting context. Do not "
                "copy outside-window seizure-free durations into cluster or frequency "
                "normalized_burden fields. If the note only describes seizures within a "
                "conditional risk window and states seizure freedom outside that window, "
                "assessment_kind should be unknown_frequency — the conditional seizure-free "
                "state is not an unconditional current seizure-free duration. Set "
                "uncertainty_flags to include seizure_free_only_outside_cyclic_risk_window."
            ),
            (
                "If the note describes a recent seizure burst (multiple events in a short "
                "recent period) followed by a current seizure-free run, use the burst "
                "candidate as primary and set assessment_kind to frequency_rate — not "
                "seizure_free. A seizure_free assessment is appropriate only when the "
                "absence of seizures is the primary clinical statement and no recent "
                "burst candidate exists in the CandidateSet."
            ),
            (
                "Preserve cluster structure: cluster cadence and events per cluster are "
                "separate axes unless the same evidence clearly gives both."
            ),
            (
                "Use assessment_kind cluster_frequency only when the CandidateSet candidate "
                "explicitly describes a recurring clinical cluster pattern: grouped multi-event "
                "episodes (e.g., 'seizure clusters', 'cluster days', 'clusters of events') "
                "that recur on a cadence. Do not select cluster_frequency because a candidate's "
                "source phrase incidentally contains the word 'cluster' or 'clustering' as a "
                "general descriptor without describing a recurring grouped-episode pattern."
            ),
            (
                "Do not turn vague words like several, few, many, or multiple into "
                "exact numbers."
            ),
            (
                "Return a clinical assessment only. Keep contextual details separate "
                "from the primary burden."
            ),
            "Rationale should be one short clinical sentence.",
            (
                "uncertainty_flags must contain only values from this exact list; "
                "do not write free-text descriptions: "
                "active_seizures_contradict_seizure_free_claim, "
                "seizure_free_inferred_from_proxy_evidence_only, "
                "cluster_description_axis_unclear, "
                "cluster_rate_unknown_per_cluster_count_known, "
                "dosing_schedule_may_be_misread_as_seizure_rate, "
                "seizure_free_only_outside_cyclic_risk_window, "
                "stated_count_and_time_window_do_not_pair, "
                "seizures_described_only_when_triggered, "
                "only_relative_change_no_current_rate, "
                "multiple_facts_not_reliably_additive, "
                "several_current_facts_compete_unresolved, "
                "answer_supported_but_represents_clinical_borderline."
            ),
            "Return only assessment_draft.",
        ],
        "policy_examples": _policy_examples(),
        "candidate_set": _candidate_set_for_prompt(candidate_set),
        "output_contract": {
            "schema_version": SCHEMA_VERSION,
            "return_object": "assessment_draft",
            "candidate_id_roles": [
                "primary_candidate_ids",
                "supporting_candidate_ids",
                "rejected_candidate_ids",
            ],
            "assessment_kind_values": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "unknown_frequency",
                "no_reference",
                "unresolved_multiple",
            ],
            "aggregation_policy_values": [
                "single_fact",
                "additive_same_window",
                "primary_with_context",
                "cluster_axis",
                "seizure_free_state",
                "unknown_due_to_ambiguity",
                "unknown_due_to_absence",
                "no_reference_boundary",
            ],
            "aggregation_policy_when_to_use": [
                (
                    "single_fact — exactly one candidate is the primary current "
                    "burden; no grouping or combination needed."
                ),
                (
                    "additive_same_window — two or more concrete frequency-rate "
                    "candidates share the same explicit time window and together "
                    "form the combined current burden; do not use for vague facts "
                    "or mixed windows."
                ),
                (
                    "primary_with_context — one candidate is the primary burden; "
                    "the others are contextual (historical, trigger-specific, or "
                    "non-additive supporting facts), not additive."
                ),
                (
                    "cluster_axis — the primary burden is expressed in cluster terms "
                    "(cluster cadence, events per cluster, or both)."
                ),
                (
                    "seizure_free_state — the primary assessment is a seizure-free "
                    "duration, not a seizure rate."
                ),
                (
                    "unknown_due_to_ambiguity — seizures are discussed and at least "
                    "one candidate exists, but competing claims cannot be resolved "
                    "into a single current rate."
                ),
                (
                    "unknown_due_to_absence — seizures are discussed but no usable "
                    "primary candidate was found; nothing is countable or datable "
                    "enough to state a rate."
                ),
                (
                    "no_reference_boundary — the note contains no seizure-frequency "
                    "reference at all."
                ),
            ],
            "uncertainty_flag_values": [
                "active_seizures_contradict_seizure_free_claim",
                "seizure_free_inferred_from_proxy_evidence_only",
                "cluster_description_axis_unclear",
                "cluster_rate_unknown_per_cluster_count_known",
                "dosing_schedule_may_be_misread_as_seizure_rate",
                "seizure_free_only_outside_cyclic_risk_window",
                "stated_count_and_time_window_do_not_pair",
                "seizures_described_only_when_triggered",
                "only_relative_change_no_current_rate",
                "multiple_facts_not_reliably_additive",
                "several_current_facts_compete_unresolved",
                "answer_supported_but_represents_clinical_borderline",
            ],
            "normalized_burden": {
                "model_fill": ["source_normalized_phrase"],
                "deterministic_fill": [
                    "count_low/count_high/vague_count with period fields",
                    "seizure_free_duration fields",
                    "cluster cadence and events_per_cluster fields",
                ],
                "source_normalized_phrase": "short source-near clinical summary phrase",
            },
        },
    }


def assemble_clinical_assessment(
    draft: AssessmentDraft | None,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[ClinicalAssessment | None, list[str]]:
    """Assemble a clinical assessment from model-owned fields."""

    if draft is None:
        return None, ["assessment_draft_missing"]
    disabled_switches = frozenset(disabled_ablation_switches or ())

    draft, role_repair_issues = _repair_candidate_role_ids(draft)
    draft, override_issues = _apply_deterministic_assessment_overrides(
        draft,
        candidate_set=candidate_set,
    )
    draft, repair_issues = _apply_deterministic_assessment_repairs(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )
    draft, post_repair_role_issues = _repair_candidate_role_ids(draft)
    errors = _validate_candidate_references(draft, candidate_set)
    normalized_burden, normalization_issues = normalize_assessment_burden(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )
    seizure_free_instrumentation: SeizureFreeInstrumentation | None = None
    if (
        draft.assessment_kind == "seizure_free"
        and "normalize_seizure_free_duration_date_instrumentation"
        not in disabled_switches
    ):
        (
            normalized_burden,
            seizure_free_instrumentation,
            instrumentation_issues,
        ) = _instrument_seizure_free_duration(
            draft,
            candidate_set=candidate_set,
            normalized_burden=normalized_burden,
            disabled_ablation_switches=disabled_switches,
        )
        normalization_issues.extend(instrumentation_issues)
    elif (
        draft.assessment_kind == "seizure_free"
        and "normalize_seizure_free_duration_date_instrumentation"
        in disabled_switches
        and _is_unrenderable_seizure_free_burden(normalized_burden)
    ):
        normalization_issues.append(
            _disabled_switch_issue(
                "normalize_seizure_free_duration_date_instrumentation"
            )
        )
    normalization_issues = [
        *role_repair_issues,
        *override_issues,
        *repair_issues,
        *post_repair_role_issues,
        *normalization_issues,
    ]
    try:
        assessment = ClinicalAssessment(
            source_row_index=candidate_set.source_row_index,
            component_owner="llm_candidate_set_clinical_assessment",
            assessment_kind=draft.assessment_kind,
            primary_candidate_ids=draft.primary_candidate_ids,
            supporting_candidate_ids=draft.supporting_candidate_ids,
            rejected_candidate_ids=draft.rejected_candidate_ids,
            aggregation_policy=draft.aggregation_policy,  # type: ignore[arg-type]
            normalized_burden=normalized_burden,
            seizure_free_instrumentation=seizure_free_instrumentation,
            normalization_policy_id=NORMALIZATION_POLICY_ID,
            normalization_issues=normalization_issues,
            assessment_summary=draft.assessment_summary,
            uncertainty_flags=draft.uncertainty_flags,
        )
    except ValidationError as exc:
        errors.extend(_validation_error_messages(exc))
        return None, errors
    if errors:
        return None, errors
    return assessment, errors


def _repair_candidate_role_ids(draft: AssessmentDraft) -> tuple[AssessmentDraft, list[str]]:
    """Remove recoverable duplicate and overlapping role ids from a model draft."""

    repairs: list[str] = []
    primary_ids, primary_issues = _dedupe_role_ids(
        draft.primary_candidate_ids,
        role_name="primary_candidate_ids",
    )
    supporting_ids, supporting_issues = _dedupe_role_ids(
        draft.supporting_candidate_ids,
        role_name="supporting_candidate_ids",
    )
    rejected_ids, rejected_issues = _dedupe_role_ids(
        draft.rejected_candidate_ids,
        role_name="rejected_candidate_ids",
    )
    repairs.extend([*primary_issues, *supporting_issues, *rejected_issues])

    primary = set(primary_ids)
    supporting_before = list(supporting_ids)
    supporting_ids = [
        candidate_id for candidate_id in supporting_ids if candidate_id not in primary
    ]
    for candidate_id in supporting_before:
        if candidate_id in primary:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"supporting_candidate_ids:{candidate_id}:kept_primary_candidate_ids"
            )

    kept = {*primary_ids, *supporting_ids}
    rejected_before = list(rejected_ids)
    rejected_ids = [candidate_id for candidate_id in rejected_ids if candidate_id not in kept]
    for candidate_id in rejected_before:
        if candidate_id in primary:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"rejected_candidate_ids:{candidate_id}:kept_primary_candidate_ids"
            )
        elif candidate_id in supporting_ids:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"rejected_candidate_ids:{candidate_id}:kept_supporting_candidate_ids"
            )

    if not repairs:
        return draft, []
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": primary_ids,
                "supporting_candidate_ids": supporting_ids,
                "rejected_candidate_ids": rejected_ids,
            }
        ),
        repairs,
    )


def _dedupe_role_ids(
    candidate_ids: Sequence[str],
    *,
    role_name: str,
) -> tuple[list[str], list[str]]:
    seen: set[str] = set()
    deduped: list[str] = []
    repairs: list[str] = []
    for candidate_id in candidate_ids:
        if candidate_id in seen:
            repairs.append(f"candidate_role_duplicate_removed:{role_name}:{candidate_id}")
            continue
        seen.add(candidate_id)
        deduped.append(candidate_id)
    return deduped, repairs


def _apply_deterministic_assessment_repairs(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[AssessmentDraft, list[str]]:
    """Repair recoverable model policy/role inconsistencies."""

    repairs: list[str] = []
    repaired = draft
    candidate_by_id = {
        candidate.candidate_id: candidate for candidate in candidate_set.candidates
    }
    if repaired.aggregation_policy is None:
        inferred = _infer_missing_aggregation_policy(repaired, candidate_by_id)
        repaired = repaired.model_copy(update={"aggregation_policy": inferred})
        repairs.append(f"aggregation_policy_defaulted:{inferred}")

    repaired, cluster_repairs = _repair_cluster_axis_without_cluster_primary(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(cluster_repairs)

    repaired, single_policy_repairs = _repair_single_primary_policy(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(single_policy_repairs)

    repaired, multi_primary_repairs = _repair_multi_primary_nonadditive_policy(
        repaired,
        candidate_by_id=candidate_by_id,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    repairs.extend(multi_primary_repairs)

    repaired, historical_repairs = _repair_historical_primary(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(historical_repairs)
    return repaired, repairs


def _infer_missing_aggregation_policy(
    draft: AssessmentDraft,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> AggregationPolicy:
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    primary_count = len(draft.primary_candidate_ids)
    if draft.assessment_kind == "seizure_free":
        return "seizure_free_state" if primary_count else "unknown_due_to_absence"
    if draft.assessment_kind == "unknown_frequency":
        return "unknown_due_to_absence" if primary_count == 0 else "unknown_due_to_ambiguity"
    if primary_count == 0:
        return "no_reference_boundary"
    if primary_count == 1:
        return "single_fact"
    if _all_candidate_kind(primary_candidates, "frequency_rate"):
        return "additive_same_window"
    if _all_candidate_kind(primary_candidates, "cluster_frequency"):
        return "cluster_axis"
    return "primary_with_context"


def _repair_single_primary_policy(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    if len(draft.primary_candidate_ids) != 1:
        return draft, []
    primary = candidate_by_id.get(draft.primary_candidate_ids[0])
    if draft.aggregation_policy == "additive_same_window":
        return (
            draft.model_copy(update={"aggregation_policy": "single_fact"}),
            ["single_primary_additive_same_window_to_single_fact"],
        )
    if draft.aggregation_policy != "cluster_axis":
        return draft, []
    if primary is not None and primary.candidate_kind == "cluster_frequency":
        return (
            draft.model_copy(update={"aggregation_policy": "single_fact"}),
            ["single_primary_cluster_axis_to_single_fact"],
        )
    repaired_policy: AggregationPolicy = (
        "primary_with_context" if draft.supporting_candidate_ids else "single_fact"
    )
    return (
        draft.model_copy(update={"aggregation_policy": repaired_policy}),
        [f"single_primary_cluster_axis_to_{repaired_policy}"],
    )


def _repair_cluster_axis_without_cluster_primary(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    if draft.aggregation_policy != "cluster_axis":
        return draft, []
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if any(candidate.candidate_kind == "cluster_frequency" for candidate in primary_candidates):
        return draft, []
    supporting_candidates = _candidate_lookup(
        candidate_by_id, draft.supporting_candidate_ids
    )
    promotable = [
        candidate
        for candidate in supporting_candidates
        if candidate.candidate_kind == "cluster_frequency"
        and _phrase_mentions_cluster_burden(candidate)
    ]
    if promotable:
        promoted = promotable[0].candidate_id
        primary_ids = [*draft.primary_candidate_ids, promoted]
        supporting_ids = [
            candidate_id
            for candidate_id in draft.supporting_candidate_ids
            if candidate_id != promoted
        ]
        return (
            draft.model_copy(
                update={
                    "primary_candidate_ids": primary_ids,
                    "supporting_candidate_ids": supporting_ids,
                }
            ),
            ["cluster_axis_supporting_cluster_promoted_to_primary"],
        )
    return (
        draft.model_copy(update={"aggregation_policy": "primary_with_context"}),
        ["cluster_axis_without_cluster_primary_to_primary_with_context"],
    )


def _repair_multi_primary_nonadditive_policy(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[AssessmentDraft, list[str]]:
    if len(draft.primary_candidate_ids) <= 1:
        return draft, []
    if draft.aggregation_policy in {
        "additive_same_window",
        "cluster_axis",
        "seizure_free_state",
        "unknown_due_to_ambiguity",
    }:
        return draft, []
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if (
        draft.assessment_kind == "frequency_rate"
        and _all_candidate_kind(primary_candidates, "frequency_rate")
        and _same_frequency_window(primary_candidates)
    ):
        return (
            draft.model_copy(update={"aggregation_policy": "additive_same_window"}),
            ["multi_primary_nonadditive_to_additive_same_window"],
        )
    best_primary_id = _best_single_primary_candidate_id(
        primary_candidates,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    if best_primary_id is None:
        return draft, ["multi_primary_nonadditive_unrepaired"]
    supporting_ids = [
        *draft.supporting_candidate_ids,
        *[
            candidate_id
            for candidate_id in draft.primary_candidate_ids
            if candidate_id != best_primary_id
        ],
    ]
    selected_primary = candidate_by_id.get(best_primary_id)
    selected_primary_phrase = (
        candidate_source_phrase(selected_primary) or selected_primary.evidence_span.text
        if selected_primary is not None
        else draft.normalized_burden.source_normalized_phrase
    )
    if selected_primary is not None and _is_major_recent_relapse_candidate(
        selected_primary
    ):
        repair_issues = ["major_recent_relapse_over_background_frequency"]
    elif "project_major_recent_relapse_over_background_frequency" in disabled_ablation_switches:
        repair_issues = [
            _disabled_switch_issue(
                "project_major_recent_relapse_over_background_frequency"
            )
        ]
    else:
        repair_issues = ["multi_primary_nonadditive_demoted_to_supporting"]
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": [best_primary_id],
                "supporting_candidate_ids": _dedupe(supporting_ids),
                "normalized_burden": draft.normalized_burden.model_copy(
                    update={"source_normalized_phrase": selected_primary_phrase}
                ),
            }
        ),
        repair_issues,
    )


def _repair_historical_primary(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if not any(candidate.temporality == "historical" for candidate in primary_candidates):
        return draft, []
    candidate_pool = [
        candidate
        for candidate in candidate_by_id.values()
        if candidate.assertion_status == "asserted"
        and candidate.candidate_kind in {"frequency_rate", "cluster_frequency", "seizure_free"}
        and candidate.temporality in {"current", "recent"}
    ]
    if not candidate_pool:
        return draft, []
    replacement = max(candidate_pool, key=_current_candidate_priority)
    historical_primary_ids = [
        candidate.candidate_id
        for candidate in primary_candidates
        if candidate.temporality == "historical"
    ]
    primary_ids = [
        replacement.candidate_id,
        *[
            candidate_id
            for candidate_id in draft.primary_candidate_ids
            if candidate_id not in historical_primary_ids
            and candidate_id != replacement.candidate_id
        ],
    ]
    supporting_ids = [
        *draft.supporting_candidate_ids,
        *historical_primary_ids,
    ]
    supporting_ids = [
        candidate_id
        for candidate_id in _dedupe(supporting_ids)
        if candidate_id != replacement.candidate_id
    ]
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": _dedupe(primary_ids),
                "supporting_candidate_ids": supporting_ids,
                "aggregation_policy": (
                    "primary_with_context" if supporting_ids else draft.aggregation_policy
                ),
            }
        ),
        [f"historical_primary_replaced_with_current:{replacement.candidate_id}"],
    )


def _candidate_lookup(
    candidate_by_id: Mapping[str, ExtractedCandidate],
    candidate_ids: Sequence[str],
) -> list[ExtractedCandidate]:
    return [
        candidate_by_id[candidate_id]
        for candidate_id in candidate_ids
        if candidate_id in candidate_by_id
    ]


def _all_candidate_kind(
    candidates: Sequence[ExtractedCandidate],
    candidate_kind: str,
) -> bool:
    return bool(candidates) and all(
        candidate.candidate_kind == candidate_kind for candidate in candidates
    )


def _same_frequency_window(candidates: Sequence[ExtractedCandidate]) -> bool:
    parsed = [
        _frequency_burden(candidate_source_phrase(candidate) or candidate.evidence_span.text)
        for candidate in candidates
    ]
    burdens = [burden for burden, issues in parsed if not issues]
    if len(burdens) != len(candidates) or not burdens:
        return False
    first = burdens[0]
    return all(
        burden.period_low == first.period_low
        and burden.period_high == first.period_high
        and burden.period_unit == first.period_unit
        for burden in burdens
    )


def _best_single_primary_candidate_id(
    candidates: Sequence[ExtractedCandidate],
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> str | None:
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda candidate: _single_primary_priority(
            candidate,
            disabled_ablation_switches=disabled_ablation_switches,
        ),
    ).candidate_id


def _single_primary_priority(
    candidate: ExtractedCandidate,
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[int, int, int, int]:
    phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
    major_relapse_enabled = (
        "project_major_recent_relapse_over_background_frequency"
        not in disabled_ablation_switches
    )
    return (
        1 if major_relapse_enabled and _is_major_recent_relapse_candidate(candidate) else 0,
        1 if candidate.temporality in {"current", "recent"} else 0,
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        1 if candidate.source_type == "deterministic_candidate" else 0,
        len(phrase),
    )


def _current_candidate_priority(candidate: ExtractedCandidate) -> tuple[int, int, int]:
    phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
    return (
        1 if candidate.temporality == "current" else 0,
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        len(phrase),
    )


def _is_major_recent_relapse_candidate(candidate: ExtractedCandidate) -> bool:
    phrase = " ".join(
        value.lower()
        for value in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if value
    )
    has_recent_day_cue = any(token in phrase for token in ("yesterday", "today"))
    has_major_semiology = any(
        token in phrase for token in ("tonic-clonic", "convulsive", "generalised", "generalized")
    )
    return (
        candidate.candidate_kind == "frequency_rate"
        and candidate.temporality in {"current", "recent"}
        and has_recent_day_cue
        and has_major_semiology
    )


def _phrase_mentions_cluster_burden(candidate: ExtractedCandidate) -> bool:
    phrase = " ".join(
        value.lower()
        for value in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if value
    )
    return any(marker in phrase for marker in ("cluster", "clusters", "run", "runs"))


def _apply_deterministic_assessment_overrides(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
) -> tuple[AssessmentDraft, list[str]]:
    if draft.assessment_kind != "cluster_frequency":
        return draft, []
    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    existing_cluster_burden, existing_cluster_issues = _cluster_burden(
        primary_candidates,
        source_phrase=source_phrase,
    )
    if _is_renderable_cluster_burden(existing_cluster_burden) and not existing_cluster_issues:
        return draft, []
    override = _best_frequency_override_candidate(draft, candidate_set=candidate_set)
    if override is None:
        return draft, []
    override_candidate_id, burden = override
    adjusted = draft.model_copy(
        update={
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": [override_candidate_id],
            "supporting_candidate_ids": [
                referenced_candidate_id
                for referenced_candidate_id in [
                    *draft.primary_candidate_ids,
                    *draft.supporting_candidate_ids,
                ]
                if referenced_candidate_id != override_candidate_id
            ],
            "aggregation_policy": "single_fact",
            "normalized_burden": AssessmentDraftBurden(
                source_normalized_phrase=burden.source_normalized_phrase
            ),
        }
    )
    return adjusted, ["cluster_assessment_promoted_to_frequency_rate"]


def _best_frequency_override_candidate(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
) -> tuple[str, NormalizedBurden] | None:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    referenced_ids = [*draft.primary_candidate_ids, *draft.supporting_candidate_ids]
    parsed: list[tuple[tuple[int, int, int], str, NormalizedBurden]] = []
    for position, candidate_id in enumerate(referenced_ids):
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        if _is_medication_cadence_candidate(candidate):
            continue
        parsed_burdens = [
            _frequency_burden(phrase)
            for phrase in _frequency_override_phrases(candidate)
        ]
        renderable = [
            burden
            for burden, issues in parsed_burdens
            if _is_renderable_frequency_burden(burden)
            and not any(
                issue
                for issue in issues
                if issue
                not in {
                    "vague_count",
                    "vague_frequency_with_explicit_time_period",
                }
            )
        ]
        if not renderable:
            continue
        burden = max(renderable, key=_frequency_burden_specificity_score)
        parsed.append(
            (
                _frequency_override_score(candidate, burden, position),
                candidate_id,
                burden,
            )
        )
    if not parsed:
        return None
    _, candidate_id, burden = max(parsed, key=lambda item: item[0])
    return candidate_id, burden


def _frequency_override_phrases(candidate: ExtractedCandidate) -> list[str]:
    phrases = _cluster_phrases([candidate]) if candidate.cluster_details else []
    phrases.append(candidate_source_phrase(candidate) or candidate.evidence_span.text)
    phrases.append(candidate.evidence_span.text)
    return [phrase for phrase in _dedupe(phrases) if phrase]


def _frequency_burden_specificity_score(burden: NormalizedBurden) -> tuple[int, int]:
    return (
        1 if burden.count_low is not None and burden.count_high is not None else 0,
        len(burden.source_normalized_phrase),
    )


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _frequency_override_score(
    candidate: ExtractedCandidate,
    burden: NormalizedBurden,
    position: int,
) -> tuple[int, int, int]:
    return (
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        1 if burden.count_low is not None and burden.count_high is not None else 0,
        -position,
    )


def _is_renderable_frequency_burden(burden: NormalizedBurden) -> bool:
    if burden.period_low is None or burden.period_high is None or burden.period_unit is None:
        return False
    return (
        burden.vague_count is not None
        or (burden.count_low is not None and burden.count_high is not None)
    )


def _is_renderable_cluster_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.cluster_count_low is not None
        and burden.cluster_count_high is not None
        and burden.cluster_period_low is not None
        and burden.cluster_period_high is not None
        and burden.cluster_period_unit is not None
    )


def _is_medication_cadence_candidate(candidate: ExtractedCandidate) -> bool:
    text = " ".join(
        phrase.lower()
        for phrase in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if phrase
    )
    return any(
        marker in text
        for marker in (
            "as needed",
            "as-needed",
            "clobazam",
            "rescue medication",
            "patient-led use",
            "treated with",
        )
    )


def normalize_assessment_burden(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    """Deterministically parse source-near assessment burden values."""

    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    issues: list[str] = []
    if not source_phrase:
        issues.append("normalization_source_phrase_missing")

    if draft.assessment_kind == "frequency_rate":
        if draft.aggregation_policy == "additive_same_window":
            burden, additive_issues = _additive_frequency_burden(
                primary_candidates,
                source_phrase=source_phrase,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            issues.extend(additive_issues)
            return burden, issues
        burden, rate_issues = _frequency_burden(
            source_phrase,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if _is_unrenderable_frequency_burden(burden):
            (
                anchor_repair,
                anchor_repair_issues,
                anchor_repair_matched,
            ) = _frequency_burden_from_anchor_window_primary_candidates(
                primary_candidates,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if anchor_repair is not None:
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *anchor_repair_issues,
                    ]
                )
                return anchor_repair, issues
            if anchor_repair_matched:
                issues.extend([*rate_issues, *anchor_repair_issues])
                return burden, issues
            (
                multi_month_bucket_source_repair,
                multi_month_bucket_source_issues,
                multi_month_bucket_source_matched,
            ) = _frequency_burden_from_multi_month_bucket_phrase(
                source_phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if multi_month_bucket_source_repair is not None:
                issues.extend([*rate_issues, *multi_month_bucket_source_issues])
                return multi_month_bucket_source_repair, issues
            if multi_month_bucket_source_matched:
                issues.extend([*rate_issues, *multi_month_bucket_source_issues])
                return burden, issues
            (
                multi_month_bucket_repair,
                multi_month_bucket_issues,
                multi_month_bucket_matched,
            ) = _frequency_burden_from_multi_month_bucket_primary_candidates(
                primary_candidates,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if multi_month_bucket_repair is not None:
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *multi_month_bucket_issues,
                    ]
                )
                return multi_month_bucket_repair, issues
            if multi_month_bucket_matched:
                issues.extend([*rate_issues, *multi_month_bucket_issues])
                return burden, issues
            repaired = _frequency_burden_from_primary_candidates(
                primary_candidates,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if repaired is not None:
                burden, repair_issues = repaired
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *repair_issues,
                    ]
                )
                return burden, issues
        issues.extend(rate_issues)
        return burden, issues

    if draft.assessment_kind == "cluster_frequency":
        burden, cluster_issues = _cluster_burden(primary_candidates, source_phrase=source_phrase)
        issues.extend(cluster_issues)
        return burden, issues

    if draft.assessment_kind == "seizure_free":
        burden, seizure_free_issues = _seizure_free_burden(source_phrase)
        if _is_prior_encounter_relative_interval_phrase(source_phrase):
            seizure_free_issues = [
                *seizure_free_issues,
                "seizure_free_anchor_from_prior_encounter_context",
                "prior_encounter_derived_seizure_free_duration",
            ]
        if _is_unrenderable_seizure_free_burden(burden):
            repaired = _seizure_free_burden_from_primary_candidates(primary_candidates)
            if repaired is not None:
                burden, repair_issues = repaired
                issues.extend(
                    [
                        *seizure_free_issues,
                        "seizure_free_duration_repaired_from_primary_candidate",
                        *repair_issues,
                    ]
                )
                return burden, issues
        issues.extend(seizure_free_issues)
        return burden, issues

    return NormalizedBurden(source_normalized_phrase=source_phrase), issues


def _instrument_seizure_free_duration(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    normalized_burden: NormalizedBurden,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, SeizureFreeInstrumentation | None, list[str]]:
    if not _is_unrenderable_seizure_free_burden(normalized_burden):
        return normalized_burden, None, []

    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    reference = candidate_set.row_context.reference_date
    anchor: DateReference | None = None
    anchor_issues: list[str] = []
    antecedent: AntecedentReference | None = None
    instrumentation_source_phrase = source_phrase
    for phrase in _seizure_free_instrumentation_phrases(draft, primary_candidates):
        anchor, anchor_issues = _extract_seizure_free_anchor_date(
            phrase,
            reference_date=reference.date if reference is not None else None,
        )
        if anchor is not None:
            instrumentation_source_phrase = phrase
            break
    if anchor is None:
        antecedent, anchor_issues = _extract_same_note_since_then_antecedent(
            draft,
            primary_candidates,
            reference_date=reference.date if reference is not None else None,
        )
        if antecedent is not None:
            anchor = antecedent.anchor_date
    if anchor is None and _mentions_prior_encounter_anchor(source_phrase):
        if "normalize_seizure_free_prior_encounter_anchor" in disabled_ablation_switches:
            anchor_issues.append(
                _disabled_switch_issue("normalize_seizure_free_prior_encounter_anchor")
            )
        else:
            prior_encounter = candidate_set.row_context.prior_encounter
            if prior_encounter is not None:
                anchor = DateReference(
                    date=prior_encounter.date,
                    date_precision=prior_encounter.date_precision,
                    source=(
                        "candidate_set.row_context.prior_encounter:"
                        f"{prior_encounter.source}"
                    ),
                    source_phrase=prior_encounter.source_phrase,
                )
                anchor_issues = [
                    "seizure_free_anchor_from_prior_encounter_context",
                    "prior_encounter_derived_seizure_free_duration",
                    *prior_encounter.issues,
                ]
    if anchor is None:
        if _mentions_since_anchor(source_phrase):
            instrumentation = SeizureFreeInstrumentation(
                state_kind="unresolved_anchor",
                source_phrase=source_phrase,
                source_candidate_ids=list(draft.primary_candidate_ids),
                source_ids=_source_ids_from_candidates(primary_candidates),
                instrumentation_issues=["seizure_free_since_date_anchor_unparsed"],
            )
            return (
                normalized_burden,
                instrumentation,
                ["seizure_free_since_date_anchor_unparsed", *anchor_issues],
            )
        return normalized_burden, None, []

    if reference is None:
        instrumentation = SeizureFreeInstrumentation(
            state_kind="unresolved_anchor",
            source_phrase=instrumentation_source_phrase,
            anchor_date=anchor,
            antecedent=antecedent,
            source_candidate_ids=list(draft.primary_candidate_ids),
            source_ids=_source_ids_from_candidates(primary_candidates),
            instrumentation_issues=["reference_date_missing_for_since_date"],
        )
        return normalized_burden, instrumentation, ["reference_date_missing_for_since_date"]

    duration_months = _whole_months_between(anchor.date, reference.date)
    if duration_months is None:
        instrumentation = SeizureFreeInstrumentation(
            state_kind="unresolved_anchor",
            source_phrase=instrumentation_source_phrase,
            anchor_date=anchor,
            antecedent=antecedent,
            reference_date=DateReference(
                date=reference.date,
                date_precision=reference.date_precision,
                source=f"candidate_set.row_context.reference_date:{reference.source}",
                source_phrase=reference.source_phrase,
            ),
            source_candidate_ids=list(draft.primary_candidate_ids),
            source_ids=_source_ids_from_candidates(primary_candidates),
            instrumentation_issues=["seizure_free_since_date_duration_uncomputed"],
        )
        return (
            normalized_burden,
            instrumentation,
            ["seizure_free_since_date_duration_uncomputed"],
        )

    instrumentation = SeizureFreeInstrumentation(
        state_kind="since_date",
        source_phrase=instrumentation_source_phrase,
        anchor_date=anchor,
        antecedent=antecedent,
        reference_date=DateReference(
            date=reference.date,
            date_precision=reference.date_precision,
            source=f"candidate_set.row_context.reference_date:{reference.source}",
            source_phrase=reference.source_phrase,
        ),
        computed_duration=ComputedDuration(
            low=float(duration_months),
            high=float(duration_months),
            unit="month",
        ),
        source_candidate_ids=list(draft.primary_candidate_ids),
        source_ids=_source_ids_from_candidates(primary_candidates),
    )
    return (
        normalized_burden.model_copy(
            update={
                "seizure_free_duration_low": float(duration_months),
                "seizure_free_duration_high": float(duration_months),
                "seizure_free_duration_unit": "month",
            }
        ),
        instrumentation,
        ["seizure_free_duration_instrumented_from_since_date", *anchor_issues],
    )


def _seizure_free_instrumentation_phrases(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> list[str]:
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    phrases = [source_phrase]
    for candidate in primary_candidates:
        phrases.extend(_candidate_parse_phrases(candidate))
    return [
        phrase
        for phrase in _dedupe([_clean_phrase(phrase) for phrase in phrases])
        if phrase
    ]


def _extract_same_note_since_then_antecedent(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    reference_date: str | None,
) -> tuple[AntecedentReference | None, list[str]]:
    if reference_date is None:
        return None, []
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    if not _mentions_since_then_anchor(source_phrase):
        return None, []

    candidates: list[tuple[str, DateReference, list[str]]] = []
    for context in _same_note_antecedent_contexts(draft, primary_candidates):
        for phrase in _antecedent_date_phrases(context):
            anchor, issues = _extract_seizure_free_anchor_date(
                f"since {phrase}",
                reference_date=reference_date,
            )
            if anchor is None:
                continue
            candidates.append(
                (
                    _clean_phrase(_antecedent_source_phrase(context, phrase)),
                    anchor,
                    issues,
                )
            )

    deduped: list[tuple[str, DateReference, list[str]]] = []
    seen: set[tuple[str, str]] = set()
    for source_phrase, anchor, issues in candidates:
        key = (anchor.date, source_phrase.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append((source_phrase, anchor, issues))
    unique_dates = {anchor.date for _, anchor, _ in deduped}
    if len(deduped) != 1 or len(unique_dates) != 1:
        return None, []

    source_phrase, anchor, issues = deduped[0]
    return (
        AntecedentReference(
            source_phrase=source_phrase,
            anchor_date=anchor,
            link_type="local_since_then_antecedent",
            source_candidate_ids=list(draft.primary_candidate_ids),
        ),
        [
            "seizure_free_anchor_from_same_note_antecedent",
            *issues,
        ],
    )


def _mentions_since_then_anchor(source_phrase: str) -> bool:
    normalized = source_phrase.strip().lower()
    return bool(
        re.search(r"\bsince\s+then\b", normalized)
        or re.search(r"\bsince\s*\.?$", normalized)
    )


def _mentions_prior_encounter_anchor(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
            r"(?:appointment|visit|review|consultation|clinic assessment)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _is_prior_encounter_relative_interval_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
            r"(?:appointment|visit|review|consultation|clinic assessment)\s+"
            r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
            r"eleven|twelve)\s+(?:days?|weeks?|months?|years?)\s+ago\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _same_note_antecedent_contexts(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> list[str]:
    contexts = [draft.assessment_summary]
    for candidate in primary_candidates:
        contexts.extend(_candidate_parse_phrases(candidate))
    return [
        context
        for context in _dedupe([_clean_phrase(context) for context in contexts])
        if context
    ]


def _antecedent_date_phrases(context: str) -> list[str]:
    phrases: list[str] = []
    month = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)"
    )
    patterns = [
        rf"\b\d{{1,2}}(?:\s+|-){month}(?:\s+|-)\d{{4}}\b",
        rf"\b\d{{1,2}}(?:\s+|-){month}\b",
        rf"\b(?:early|mid|late)\s+{month}\s+\d{{4}}\b",
        rf"\b(?:early|mid|late)\s+{month}\b",
        rf"\b{month}\s+\d{{4}}\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, context, flags=re.IGNORECASE):
            phrases.append(match.group(0))
    return _dedupe(phrases)


def _antecedent_source_phrase(context: str, phrase: str) -> str:
    lower_context = context.lower()
    lower_phrase = phrase.lower()
    position = lower_context.find(lower_phrase)
    if position < 0:
        return phrase
    punctuation_before = [
        lower_context.rfind(separator, 0, position)
        for separator in (".", ";", ":")
    ]
    start = max(punctuation_before) + 1
    punctuation_after = [
        found
        for separator in (".", ";", ":")
        for found in [lower_context.find(separator, position + len(phrase))]
        if found >= 0
    ]
    end = min(punctuation_after) if punctuation_after else len(context)
    return context[start:end].strip() or phrase


def prediction_to_assessment_draft(
    prediction: Any,
) -> tuple[AssessmentDraft | None, list[str]]:
    """Parse DSPy prediction output into an AssessmentDraft."""

    try:
        value = prediction.assessment_draft
    except AttributeError:
        return None, ["assessment_draft_missing"]
    if isinstance(value, AssessmentDraft):
        return value, []
    try:
        return AssessmentDraft.model_validate(value), []
    except ValidationError as exc:
        return None, _validation_error_messages(exc)


def _candidates_by_ids(
    candidate_set: CandidateSet,
    candidate_ids: Sequence[str],
) -> list[ExtractedCandidate]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return [by_id[candidate_id] for candidate_id in candidate_ids if candidate_id in by_id]


def _normalization_source_phrase(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> str:
    if draft.normalized_burden.source_normalized_phrase.strip():
        return _clean_phrase(draft.normalized_burden.source_normalized_phrase)
    phrases = [
        candidate_source_phrase(candidate) or candidate.evidence_span.text
        for candidate in primary_candidates
    ]
    return _clean_phrase("; ".join(phrase for phrase in phrases if phrase))


def _frequency_burden(
    source_phrase: str,
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    parse_phrase = _normalize_phrase_for_parse(source_phrase)
    if _is_relative_only_trend_phrase(parse_phrase):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "relative_change_without_current_baseline"
        ]
    if _is_conditional_only_trigger_phrase(parse_phrase):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "conditional_only_trigger_without_baseline"
        ]
    selected_evidence_label = (
        selected_evidence_derivation.prediction_label_from_selected_evidence(parse_phrase)
    )
    if (
        selected_evidence_label is not None
        and selected_evidence_label.startswith("multiple per ")
        and _is_vague_frequency_with_explicit_time_period_phrase(parse_phrase)
    ):
        burden, issues = _burden_from_label(
            selected_evidence_label,
            source_phrase=source_phrase,
        )
        return burden, ["vague_frequency_with_explicit_time_period", *issues]
    if (
        _is_previous_month_active_rate_phrase(parse_phrase)
        and "project_previous_active_month_over_current_month_zero"
        not in disabled_ablation_switches
    ):
        return (
            NormalizedBurden(
                vague_count="multiple",
                period_low=1,
                period_high=1,
                period_unit="month",
                source_normalized_phrase=source_phrase,
            ),
            ["previous_month_active_rate_over_current_zero", "vague_count"],
        )
    if (
        _is_previous_month_active_rate_phrase(parse_phrase)
        and "project_previous_active_month_over_current_month_zero"
        in disabled_ablation_switches
    ):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            _disabled_switch_issue(
                "project_previous_active_month_over_current_month_zero"
            )
        ]
    label = _deterministic_label_from_source_phrase(
        parse_phrase,
        preferred_kind=DeterministicCandidateKind.FREQUENCY_RATE,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "frequency_rate_values_unparsed"
        ]
    burden, issues = _burden_from_label(label, source_phrase=source_phrase)
    if (
        not _is_unrenderable_frequency_burden(burden)
        and _is_explicit_summary_rate_phrase(parse_phrase)
        and "project_current_summary_rate_priority" not in disabled_ablation_switches
    ):
        issues = ["explicit_summary_rate_over_long_period_average", *issues]
    elif (
        not _is_unrenderable_frequency_burden(burden)
        and _is_explicit_summary_rate_phrase(parse_phrase)
        and "project_current_summary_rate_priority" in disabled_ablation_switches
    ):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            _disabled_switch_issue("project_current_summary_rate_priority")
        ]
    if _has_cluster_label(label):
        issues.append("frequency_rate_label_derivation_returned_cluster")
    if _has_seizure_free_label(label):
        issues.append("frequency_rate_label_derivation_returned_seizure_free")
    return burden, issues


def _frequency_burden_from_anchor_window_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    matched_any = False
    disabled_issues: list[str] = []
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues, matched = _frequency_burden_from_anchor_window_phrase(
                phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if not matched:
                continue
            matched_any = True
            if burden is None:
                disabled_issues = issues
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    issues,
                )
            )
    if parsed:
        _score, burden, issues = max(parsed, key=lambda item: item[0])
        return burden, issues, True
    return None, disabled_issues, matched_any


def _frequency_burden_from_multi_month_bucket_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    matched_any = False
    disabled_issues: list[str] = []
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues, matched = _frequency_burden_from_multi_month_bucket_phrase(
                phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if not matched:
                continue
            matched_any = True
            if burden is None:
                disabled_issues = issues
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    issues,
                )
            )
    if parsed:
        _score, burden, issues = max(parsed, key=lambda item: item[0])
        return burden, issues, True
    return None, disabled_issues, matched_any


def _frequency_burden_from_multi_month_bucket_phrase(
    source_phrase: str,
    *,
    reference_date: str | None,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    normalized = _normalize_phrase_for_parse(source_phrase)
    if _has_per_cluster_frequency_terms(normalized):
        return None, [], False
    bucket_matches = _extract_frequency_multi_month_bucket_matches(
        normalized,
        reference_date=reference_date,
    )
    current_month_bucket = _extract_frequency_current_month_bucket_match(
        normalized,
        reference_date=reference_date,
    )
    if current_month_bucket is not None and not any(
        match["month_iso"] == current_month_bucket["month_iso"]
        for match in bucket_matches
    ):
        bucket_matches.append(current_month_bucket)
    for article_match in _extract_frequency_article_month_bucket_matches(
        normalized,
        reference_date=reference_date,
    ):
        if any(match["month_iso"] == article_match["month_iso"] for match in bucket_matches):
            continue
        bucket_matches.append(article_match)
    explicit_window_months = _extract_explicit_multi_month_window_months(normalized)
    if not bucket_matches:
        summary_count = _extract_frequency_summary_count_with_month_list(
            normalized,
            reference_date=reference_date,
        )
        if summary_count is None or explicit_window_months is None:
            return None, [], False
        count_low, count_high, inferred_year = summary_count
        if "normalize_frequency_multi_month_bucket_value_recovery" in disabled_ablation_switches:
            return (
                None,
                [_disabled_switch_issue("normalize_frequency_multi_month_bucket_value_recovery")],
                True,
            )
        issues = [
            "frequency_rate_values_repaired_from_multi_month_bucket",
            "frequency_rate_multi_month_window_from_source_phrase",
        ]
        if inferred_year:
            issues.append("frequency_rate_bucket_year_inferred_from_reference_date")
        return (
            NormalizedBurden(
                count_low=count_low,
                count_high=count_high,
                period_low=float(explicit_window_months),
                period_high=float(explicit_window_months),
                period_unit="month",
                source_normalized_phrase=normalized,
            ),
            issues,
            True,
        )
    if len(bucket_matches) < 2 and explicit_window_months is None:
        return None, [], False
    if "normalize_frequency_multi_month_bucket_value_recovery" in disabled_ablation_switches:
        return (
            None,
            [_disabled_switch_issue("normalize_frequency_multi_month_bucket_value_recovery")],
            True,
        )
    count_low = sum(match["count_low"] for match in bucket_matches)
    count_high = sum(match["count_high"] for match in bucket_matches)
    if explicit_window_months is not None:
        denominator_months = explicit_window_months
        denominator_issue = "frequency_rate_multi_month_window_from_source_phrase"
    else:
        denominator_months = _inclusive_month_span(
            [match["month_iso"] for match in bucket_matches]
        )
        denominator_issue = "frequency_rate_multi_month_window_from_named_buckets"
    if denominator_months is None or denominator_months <= 1:
        return None, [], False
    issues = [
        "frequency_rate_values_repaired_from_multi_month_bucket",
        denominator_issue,
    ]
    if any(match["year_inferred"] for match in bucket_matches):
        issues.append("frequency_rate_bucket_year_inferred_from_reference_date")
    return (
        NormalizedBurden(
            count_low=float(count_low),
            count_high=float(count_high),
            period_low=float(denominator_months),
            period_high=float(denominator_months),
            period_unit="month",
            source_normalized_phrase=normalized,
        ),
        issues,
        True,
    )


def _frequency_burden_from_anchor_window_phrase(
    source_phrase: str,
    *,
    reference_date: str | None,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    normalized = _normalize_phrase_for_parse(source_phrase)
    if reference_date is None:
        return None, [], False
    count_match = re.search(
        r"\b(?P<low>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)"
        r"(?:\s+to\s+(?P<high>\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve))?"
        r"(?:\s+\w+){0,4}\s+"
        r"(?:jerks?|seizures?|events?|episodes?|absences?|spasms?)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if count_match is None:
        return None, [], False
    low = _small_number_to_float(count_match.group("low"))
    high = _small_number_to_float(count_match.group("high") or count_match.group("low"))
    if low is None or high is None:
        return None, [], False
    anchor_date, anchor_issues, matched = _extract_frequency_anchor_window_date(
        normalized,
        reference_date=reference_date,
    )
    if anchor_date is None or not matched:
        return None, [], False
    if "normalize_frequency_anchor_window_value_recovery" in disabled_ablation_switches:
        return (
            None,
            [_disabled_switch_issue("normalize_frequency_anchor_window_value_recovery")],
            True,
        )
    elapsed_months = _whole_months_between(anchor_date, reference_date)
    if elapsed_months is None or elapsed_months <= 0:
        return None, [], False
    anchor_bonus = 1 if "frequency_rate_anchor_from_last_event_phrase" in anchor_issues else 0
    return (
        NormalizedBurden(
            count_low=low + anchor_bonus,
            count_high=high + anchor_bonus,
            period_low=float(elapsed_months),
            period_high=float(elapsed_months),
            period_unit="month",
            source_normalized_phrase=normalized,
        ),
        ["frequency_rate_values_repaired_from_anchor_window", *anchor_issues],
        True,
    )


def _frequency_burden_from_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]] | None:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues = _frequency_burden(
                phrase,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if _is_unrenderable_frequency_burden(burden):
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    [issue for issue in issues if issue != "vague_count"],
                )
            )
    if not parsed:
        return None
    _score, burden, issues = max(parsed, key=lambda item: item[0])
    return burden, issues


def _disabled_switch_issue(switch: str) -> str:
    return f"{DISABLED_SWITCH_ISSUE_PREFIX}{switch}"


def _additive_frequency_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    parsed = [
        _frequency_burden(
            candidate_source_phrase(candidate) or candidate.evidence_span.text,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        for candidate in primary_candidates
    ]
    issues = [issue for _, burden_issues in parsed for issue in burden_issues]
    burdens = [burden for burden, _ in parsed]
    if not burdens:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "additive_frequency_primary_candidates_missing"
        ]
    first = burdens[0]
    same_period = all(
        burden.period_low == first.period_low
        and burden.period_high == first.period_high
        and burden.period_unit == first.period_unit
        for burden in burdens
    )
    if not same_period:
        # Fall back to the most specific single primary candidate's rate
        fallback = _frequency_burden_from_primary_candidates(
            primary_candidates,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if fallback is not None:
            fallback_burden, fallback_issues = fallback
            return fallback_burden, [
                *issues,
                "additive_frequency_period_mismatch",
                "additive_frequency_fallback_to_primary_candidate",
                *fallback_issues,
            ]
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            *issues,
            "additive_frequency_period_mismatch",
        ]
    if any(burden.count_low is None or burden.count_high is None for burden in burdens):
        # Fall back to the most specific single primary candidate's rate
        fallback = _frequency_burden_from_primary_candidates(
            primary_candidates,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if fallback is not None:
            fallback_burden, fallback_issues = fallback
            return fallback_burden, [
                *issues,
                "additive_frequency_count_unparsed",
                "additive_frequency_fallback_to_primary_candidate",
                *fallback_issues,
            ]
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            *issues,
            "additive_frequency_count_unparsed",
        ]
    return (
        NormalizedBurden(
            count_low=sum(float(burden.count_low or 0) for burden in burdens),
            count_high=sum(float(burden.count_high or 0) for burden in burdens),
            period_low=first.period_low,
            period_high=first.period_high,
            period_unit=first.period_unit,
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )


def _cluster_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    text = "; ".join(_cluster_phrases(primary_candidates)) or source_phrase
    label = _deterministic_label_from_source_phrase(
        text,
        preferred_kind=DeterministicCandidateKind.CLUSTER_FREQUENCY,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_frequency_values_unparsed"
        ]
    burden, issues = _cluster_burden_from_label(label, source_phrase=source_phrase)
    return burden, issues


def _seizure_free_burden(source_phrase: str) -> tuple[NormalizedBurden, list[str]]:
    prior_encounter_burden = _prior_encounter_relative_duration_burden(source_phrase)
    if prior_encounter_burden is not None:
        return prior_encounter_burden, []
    label = _deterministic_label_from_source_phrase(
        source_phrase,
        preferred_kind=DeterministicCandidateKind.SEIZURE_FREE,
    )
    if label is None or not _has_seizure_free_label(label):
        return (
            NormalizedBurden(source_normalized_phrase=source_phrase),
            ["seizure_free_duration_unparsed"],
        )
    return _burden_from_label(label, source_phrase=source_phrase)


def _prior_encounter_relative_duration_burden(
    source_phrase: str,
) -> NormalizedBurden | None:
    match = re.search(
        r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
        r"(?:appointment|visit|review|consultation|clinic assessment)\s+"
        r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)\s+(?P<unit>days?|weeks?|months?|years?)\s+ago\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    count = _small_number_to_float(match.group("count"))
    unit = _duration_unit(match.group("unit"))
    if count is None or unit is None:
        return None
    return NormalizedBurden(
        seizure_free_duration_low=count,
        seizure_free_duration_high=count,
        seizure_free_duration_unit=unit,
        source_normalized_phrase=source_phrase,
    )


def _small_number_to_float(value: str) -> float | None:
    if value.isdigit():
        return float(value)
    parsed = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }.get(value.strip().lower())
    return float(parsed) if parsed is not None else None


def _extract_frequency_multi_month_bucket_matches(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    count_token = (
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
    )
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    pattern = re.compile(
        rf"\b(?P<low>{count_token})"
        rf"(?:\s+to\s+(?P<high>{count_token}))?"
        r"(?:\s+[A-Za-z][A-Za-z-]*){0,6}?"
        r"\s+(?:in|during|throughout)\s+"
        rf"(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    matches: list[dict[str, Any]] = []
    seen: set[tuple[str, float, float]] = set()
    for match in pattern.finditer(source_phrase):
        count_low = _small_number_to_float(match.group("low"))
        count_high = _small_number_to_float(match.group("high") or match.group("low"))
        if count_low is None or count_high is None:
            continue
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None:
            continue
        key = (month_iso, count_low, count_high)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            {
                "count_low": count_low,
                "count_high": count_high,
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return matches


def _extract_frequency_current_month_bucket_match(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> dict[str, Any] | None:
    month_iso = _reference_month_iso(reference_date)
    if month_iso is None:
        return None
    count_token = (
        r"\d+|no|zero|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve"
    )
    event_token = r"seizures?|events?|episodes?|absences?|spasms?|attacks?|jerks?"
    patterns = [
        re.compile(
            rf"\b(?P<count>{count_token})\s+(?:\w+\s+){{0,3}}?(?:{event_token})\s+"
            r"so\s+far\s+this\s+month\b",
            flags=re.IGNORECASE,
        ),
        re.compile(
            rf"\bthis\s+month\s+so\s+far\b(?:\s+\w+){{0,6}}?\s+(?P<count>{count_token})\s+"
            rf"(?:\w+\s+){{0,3}}?(?:{event_token})\b",
            flags=re.IGNORECASE,
        ),
    ]
    for pattern in patterns:
        match = pattern.search(source_phrase)
        if match is None:
            continue
        count_value = match.groupdict().get("count")
        if not count_value:
            continue
        count = _multi_month_bucket_count_to_float(count_value)
        if count is None:
            continue
        return {
            "count_low": count,
            "count_high": count,
            "month_iso": month_iso,
            "year_inferred": False,
        }
    return None


def _extract_frequency_article_month_bucket_matches(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    event_token = r"seizures?|events?|episodes?|absences?|spasms?|attacks?|jerks?"
    pattern = re.compile(
        rf"\b(?:a|an|another)\s+(?:[A-Za-z][A-Za-z-]*\s+){{0,3}}?"
        rf"(?P<event>(?:{event_token}))\s+(?:in|during|throughout)\s+"
        rf"(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    matches: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in pattern.finditer(source_phrase):
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None or month_iso in seen:
            continue
        seen.add(month_iso)
        matches.append(
            {
                "count_low": 1.0,
                "count_high": 1.0,
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return matches


def _extract_frequency_summary_count_with_month_list(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> tuple[float, float, bool] | None:
    explicit_window = _extract_explicit_multi_month_window_months(source_phrase)
    month_mentions = _extract_month_mentions(source_phrase, reference_date=reference_date)
    if explicit_window is None or len(month_mentions) < 2:
        return None
    count_match = re.search(
        r"\b(?P<low>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)"
        r"(?:\s+to\s+(?P<high>\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve))?"
        r"(?:\s+\w+){0,4}\s+"
        r"(?:jerks?|seizures?|events?|episodes?|absences?|spasms?)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if count_match is None:
        return None
    count_low = _small_number_to_float(count_match.group("low"))
    count_high = _small_number_to_float(count_match.group("high") or count_match.group("low"))
    if count_low is None or count_high is None:
        return None
    inferred_year = any(mention["year_inferred"] for mention in month_mentions)
    return count_low, count_high, inferred_year


def _extract_explicit_multi_month_window_months(source_phrase: str) -> int | None:
    match = re.search(
        r"\b(?:over|during|across|within)\s+(?:the\s+past\s+|past\s+|last\s+)?"
        r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)\s+months?\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    count = _small_number_to_float(match.group("count"))
    if count is None or count <= 1:
        return None
    return int(count)


def _multi_month_bucket_count_to_float(value: str) -> float | None:
    normalized = value.strip().lower()
    if normalized in {"no", "zero"}:
        return 0.0
    return _small_number_to_float(value)


def _extract_month_mentions(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    pattern = re.compile(
        rf"\b(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    mentions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in pattern.finditer(source_phrase):
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None or month_iso in seen:
            continue
        seen.add(month_iso)
        mentions.append(
            {
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return mentions


def _month_token_to_iso(
    month: str,
    *,
    year: str | None,
    reference_date: str | None,
) -> tuple[str | None, bool]:
    if year:
        return _month_year_to_iso(month, year), False
    if reference_date is None:
        return None, False
    return _month_without_year_to_iso(month, reference_date=reference_date), True


def _reference_month_iso(reference_date: str | None) -> str | None:
    if reference_date is None:
        return None
    parts = reference_date.split("-")
    if len(parts) < 2:
        return None
    try:
        year = int(parts[0])
        month = int(parts[1])
    except ValueError:
        return None
    if month < 1 or month > 12:
        return None
    return f"{year:04d}-{month:02d}"


def _inclusive_month_span(month_isos: Sequence[str]) -> int | None:
    if not month_isos:
        return None
    parsed: list[tuple[int, int]] = []
    for month_iso in month_isos:
        parts = month_iso.split("-")
        try:
            parsed.append((int(parts[0]), int(parts[1])))
        except (IndexError, ValueError):
            return None
    start_year, start_month = min(parsed)
    end_year, end_month = max(parsed)
    return (end_year - start_year) * 12 + (end_month - start_month) + 1


def _has_per_cluster_frequency_terms(source_phrase: str) -> bool:
    return bool(
        re.search(r"\bper\s+cluster\b", source_phrase, flags=re.IGNORECASE)
        or re.search(r"\bclusters?\s+every\b", source_phrase, flags=re.IGNORECASE)
    )


def _duration_unit(value: str) -> Literal["day", "week", "month", "year"] | None:
    normalized = value.strip().lower()
    if normalized.startswith("day"):
        return "day"
    if normalized.startswith("week"):
        return "week"
    if normalized.startswith("month"):
        return "month"
    if normalized.startswith("year"):
        return "year"
    return None


def _seizure_free_burden_from_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
) -> tuple[NormalizedBurden, list[str]] | None:
    parsed: list[tuple[int, NormalizedBurden, list[str]]] = []
    for candidate in primary_candidates:
        if candidate.candidate_kind != "seizure_free":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues = _seizure_free_burden(phrase)
            if _is_unrenderable_seizure_free_burden(burden):
                continue
            parsed.append((len(burden.source_normalized_phrase), burden, issues))
    if not parsed:
        return None
    _score, burden, issues = max(parsed, key=lambda item: item[0])
    return burden, issues


def _candidate_parse_phrases(candidate: ExtractedCandidate) -> list[str]:
    phrases = [
        candidate_source_phrase(candidate) or "",
        candidate.evidence_span.text,
    ]
    return [phrase for phrase in _dedupe([_clean_phrase(phrase) for phrase in phrases]) if phrase]


def _is_unrenderable_frequency_burden(burden: NormalizedBurden) -> bool:
    return not _is_renderable_frequency_burden(burden)


def _is_unrenderable_seizure_free_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.seizure_free_duration_low is None
        or burden.seizure_free_duration_high is None
        or burden.seizure_free_duration_unit is None
    )


def _is_relative_only_trend_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bfrequency\s+"
            r"(?:increased|decreased|improved|worsened|reduced)\s+"
            r"(?:by\s+)?(?:about\s+|approximately\s+|~)?"
            r"(?:\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _is_vague_frequency_with_explicit_time_period_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:several|multiple|many|few|a few)\b"
            r".{0,60}\b(?:day|week|month|year)s?\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _is_conditional_only_trigger_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:seizures?|events?|episodes?)\b.*\b(?:only|exclusively)\s+"
            r"(?:after|when|if|with|during)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
        or re.search(
            r"\b(?:seizures?|events?|episodes?)\b.*\b(?:when|if|with|during)\b"
            r".{0,60}\bonly\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _is_explicit_summary_rate_phrase(source_phrase: str) -> bool:
    has_long_window_summary = re.search(
        r"\b(?:so\s+far\s+this\s+year|year\s+to\s+date|this\s+year\s+to\s+date)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    has_current_summary_cue = re.search(
        r"\b(?:at\s+present|currently|now)\b",
        source_phrase,
        flags=re.IGNORECASE,
    ) or re.search(
        r"\b(?:his|her|their|the)\s+(?:current|typical)\s+pattern\s+is\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    has_rate_language = re.search(
        r"\b(?:daily|weekly|monthly|yearly|annually|per\s+day|per\s+week|per\s+month|"
        r"per\s+year|once|twice)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    return bool(has_long_window_summary and has_current_summary_cue and has_rate_language)


def _is_previous_month_active_rate_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:handful|multiple|several|many|few)\b[^.]{0,120}\b"
            r"(?:(?:during|in)\s+(?:the\s+)?(?:previous|last)\s+month|"
            r"occurred\s+(?:the\s+)?last\s+month)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
        and re.search(
            r"\b(?:(?:current|this)\s+month(?:\s+to\s+date)?|so\s+far\s+this\s+month)\b"
            r"[^.]{0,120}\b(?:there\s+have\s+been\s+)?no\s+(?:events?|seizures?|episodes?)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _extract_frequency_anchor_window_date(
    source_phrase: str,
    *,
    reference_date: str,
) -> tuple[str | None, list[str], bool]:
    last_event_month_year = re.search(
        r"\bsince\s+last\s+[^.]{0,40}?\bseizure\s+in\s+"
        r"(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if last_event_month_year is not None:
        parsed = _month_year_to_iso(
            last_event_month_year.group("month"),
            last_event_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, ["frequency_rate_anchor_from_last_event_phrase"], True
    since_month_year = re.search(
        r"\bsince\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if since_month_year is not None:
        parsed = _month_year_to_iso(
            since_month_year.group("month"),
            since_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, [], True
    since_numeric_month_year = re.search(
        r"\bsince\s+(?P<month>\d{1,2})\s*(?:/|-)\s*(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if since_numeric_month_year is not None:
        parsed = _numeric_month_year_to_iso(
            since_numeric_month_year.group("month"),
            since_numeric_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, [], True
    last_event_month_without_year = re.search(
        r"\bsince\s+last\s+[^.]{0,40}?\bseizure\s+in\s+(?P<month>[A-Za-z]+)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if last_event_month_without_year is not None:
        parsed = _month_without_year_to_iso(
            last_event_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return (
                parsed,
                [
                    "frequency_rate_anchor_year_inferred_from_reference_date",
                    "frequency_rate_anchor_from_last_event_phrase",
                ],
                True,
            )
    return None, [], False


def _extract_seizure_free_anchor_date(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> tuple[DateReference | None, list[str]]:
    normalized = _clean_phrase(source_phrase)
    day_numeric = re.search(
        r"\bsince\s+(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_numeric is not None:
        parsed = _numeric_day_month_year_to_iso(
            day_numeric.group("day"),
            day_numeric.group("month"),
            day_numeric.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=day_numeric.group(0),
            ), []
    day_named = re.search(
        r"\bsince\s+(?P<day>\d{1,2})(?:\s+|-)"
        r"(?P<month>[A-Za-z]+)(?:\s+|-)(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_named is not None:
        parsed = _day_month_year_to_iso(
            day_named.group("day"),
            day_named.group("month"),
            day_named.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=day_named.group(0),
            ), []
    event_day_named = re.search(
        r"\b(?:last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})(?:\s+|-)(?P<month>[A-Za-z]+)(?:\s+|-)"
        r"(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_day_named is not None:
        parsed = _day_month_year_to_iso(
            event_day_named.group("day"),
            event_day_named.group("month"),
            event_day_named.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=event_day_named.group(0),
            ), ["seizure_free_anchor_from_last_event_phrase"]
    month_year = re.search(
        r"\bsince\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_year is not None:
        parsed = _month_year_to_iso(
            month_year.group("month"),
            month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase",
                source_phrase=month_year.group(0),
            ), []
    numeric_month_year = re.search(
        r"\bsince\s+(?P<month>\d{1,2})\s*(?:/|-)\s*(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_month_year is not None:
        parsed = _numeric_month_year_to_iso(
            numeric_month_year.group("month"),
            numeric_month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase",
                source_phrase=numeric_month_year.group(0),
            ), []
    event_month_year = re.search(
        r"\b(?:since|commencing|starting|titration|titrating|dose increase|"
        r"dose titration)(?P<context>.{0,80}?)\b(?:at|in|from)\s+"
        r"(?:the\s+)?(?:(?P<qualifier>early|mid|late|end)(?:\s+of)?[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_month_year is not None:
        parsed = _month_year_to_iso(
            event_month_year.group("month"),
            event_month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_event_anchor_month_year",
                source_phrase=event_month_year.group(0),
            ), [
                "seizure_free_anchor_from_event_phrase",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if event_month_year.group("qualifier")
                    else []
                ),
            ]
    day_month_without_year = re.search(
        r"\b(?:since|last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})\s*(?:/|-|\s+)(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_month_without_year is not None and reference_date is not None:
        parsed = _day_month_without_year_to_iso(
            day_month_without_year.group("day"),
            day_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            source = "seizure_free_source_phrase_year_inferred_from_reference_date"
            issues = ["seizure_free_anchor_year_inferred_from_reference_date"]
            if "last" in day_month_without_year.group(0).lower():
                issues.append("seizure_free_anchor_from_last_event_phrase")
            return DateReference(
                date=parsed,
                date_precision="day",
                source=source,
                source_phrase=day_month_without_year.group(0),
            ), issues
    numeric_day_month_without_year = re.search(
        r"\b(?:since|last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})[/-](?P<month>\d{1,2})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_day_month_without_year is not None and reference_date is not None:
        parsed = _numeric_day_month_without_year_to_iso(
            numeric_day_month_without_year.group("day"),
            numeric_day_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            issues = ["seizure_free_anchor_year_inferred_from_reference_date"]
            if "last" in numeric_day_month_without_year.group(0).lower():
                issues.append("seizure_free_anchor_from_last_event_phrase")
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase_year_inferred_from_reference_date",
                source_phrase=numeric_day_month_without_year.group(0),
            ), issues
    approximate_year = re.search(
        r"\bsince\s+(?P<qualifier>early|mid|late)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if approximate_year is not None:
        parsed = _approximate_year_to_iso(
            approximate_year.group("qualifier"),
            approximate_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_approximate_anchor_policy",
                source_phrase=approximate_year.group(0),
            ), ["seizure_free_anchor_approximate_start_month_policy"]
    season_without_year = re.search(
        r"\bsince\s+(?P<qualifier>early|mid|late)?\s*"
        r"(?P<season>spring|summer|autumn|fall|winter)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if season_without_year is not None and reference_date is not None:
        parsed = _season_without_year_to_iso(
            season_without_year.group("season"),
            qualifier=season_without_year.group("qualifier"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_approximate_anchor_policy",
                source_phrase=season_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                "seizure_free_anchor_approximate_start_month_policy",
            ]
    event_month_without_year = re.search(
        r"\b(?:since|commencing|starting|titration|titrating|dose increase|dose titration)"
        r"(?P<context>.{0,80}?)\b(?:at|in|from)\s+"
        r"(?:the\s+)?"
        r"(?:(?P<qualifier>early|mid|late|end)(?:\s+of)?[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_month_without_year is not None and reference_date is not None:
        parsed = _month_without_year_to_iso(
            event_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source=(
                    "seizure_free_event_anchor_month_"
                    "year_inferred_from_reference_date"
                ),
                source_phrase=event_month_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                "seizure_free_anchor_from_event_phrase",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if event_month_without_year.group("qualifier")
                    else []
                ),
            ]
    month_without_year = re.search(
        r"\bsince\s+(?:(?P<qualifier>early|mid|late)[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_without_year is not None and reference_date is not None:
        parsed = _month_without_year_to_iso(
            month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_year_inferred_from_reference_date",
                source_phrase=month_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if month_without_year.group("qualifier")
                    else []
                ),
            ]
    return None, []


def _mentions_since_anchor(source_phrase: str) -> bool:
    return bool(re.search(r"\bsince\b", source_phrase, flags=re.IGNORECASE))


def _month_year_to_iso(month: str, year: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    return f"{int(year):04d}-{month_number:02d}"


def _day_month_year_to_iso(day: str, month: str, year: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    try:
        parsed = date(int(year), month_number, int(day))
    except ValueError:
        return None
    return parsed.isoformat()


def _numeric_day_month_year_to_iso(day: str, month: str, year: str) -> str | None:
    try:
        parsed = date(int(year), int(month), int(day))
    except ValueError:
        return None
    return parsed.isoformat()


def _numeric_month_year_to_iso(month: str, year: str) -> str | None:
    try:
        month_number = int(month)
    except ValueError:
        return None
    if not 1 <= month_number <= 12:
        return None
    return f"{int(year):04d}-{month_number:02d}"


def _day_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    return _day_numeric_month_without_year_to_iso(
        day,
        str(month_number),
        reference_date=reference_date,
    )


def _numeric_day_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    return _day_numeric_month_without_year_to_iso(
        day,
        month,
        reference_date=reference_date,
    )


def _day_numeric_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    try:
        reference = date.fromisoformat(reference_date)
        month_number = int(month)
        day_number = int(day)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    try:
        parsed = date(year, month_number, day_number)
    except ValueError:
        return None
    if parsed > reference:
        try:
            parsed = date(year - 1, month_number, day_number)
        except ValueError:
            return None
    return parsed.isoformat()


def _approximate_year_to_iso(qualifier: str, year: str) -> str | None:
    month = {
        "early": 1,
        "mid": 6,
        "late": 10,
    }.get(qualifier.strip().lower())
    if month is None:
        return None
    return f"{int(year):04d}-{month:02d}"


def _season_without_year_to_iso(
    season: str,
    *,
    qualifier: str | None,
    reference_date: str,
) -> str | None:
    season_key = season.strip().lower()
    season_start_month = {
        "spring": 3,
        "summer": 6,
        "autumn": 9,
        "fall": 9,
        "winter": 12,
    }.get(season_key)
    if season_start_month is None:
        return None
    offset = {
        "early": 0,
        "mid": 1,
        "late": 2,
        None: 0,
    }.get(None if qualifier is None else qualifier.strip().lower(), 0)
    month_number = season_start_month + offset
    if month_number > 12:
        month_number -= 12
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    return f"{year:04d}-{month_number:02d}"


def _month_without_year_to_iso(month: str, *, reference_date: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    return f"{year:04d}-{month_number:02d}"


def _month_number(month: str) -> int | None:
    lookup = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }
    return lookup.get(month.strip().lower())


def _whole_months_between(anchor_date: str, reference_date: str) -> int | None:
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    anchor_parts = anchor_date.split("-")
    try:
        anchor_year = int(anchor_parts[0])
        anchor_month = int(anchor_parts[1])
        anchor_day = int(anchor_parts[2]) if len(anchor_parts) == 3 else 1
        anchor = date(anchor_year, anchor_month, anchor_day)
    except (IndexError, ValueError):
        return None
    months = (reference.year - anchor.year) * 12 + reference.month - anchor.month
    if len(anchor_parts) == 3 and reference.day < anchor.day:
        months -= 1
    return max(months, 0)


def _source_ids_from_candidates(candidates: Sequence[ExtractedCandidate]) -> list[str]:
    return sorted({source_id for candidate in candidates for source_id in candidate.source_ids})


def _cluster_phrases(candidates: Sequence[ExtractedCandidate]) -> list[str]:
    phrases: list[str] = []
    for candidate in candidates:
        if candidate.cluster_details is None:
            phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
            if phrase:
                phrases.append(phrase)
            continue
        details = candidate.cluster_details
        phrases.extend(
            phrase
            for phrase in (
                details.cluster_frequency,
                details.events_per_cluster,
                details.cluster_count,
                details.cluster_period,
                candidate.evidence_span.text,
            )
            if phrase
        )
    return phrases


def _deterministic_label_from_source_phrase(
    source_phrase: str,
    *,
    preferred_kind: DeterministicCandidateKind,
) -> str | None:
    candidates = deterministic_extraction._extract_candidates(source_phrase)
    preferred = [
        candidate.label
        for candidate in candidates
        if candidate.kind is preferred_kind and candidate.label
    ]
    if preferred:
        return _prefer_most_specific_label(preferred)
    fallback = selected_evidence_derivation.prediction_label_from_selected_evidence(
        source_phrase
    )
    return fallback


def _prefer_most_specific_label(labels: Sequence[str]) -> str:
    return max(labels, key=_label_specificity_score)


def _label_specificity_score(label: str) -> tuple[int, int]:
    normalized = label.lower()
    return (
        1 if "multiple" not in normalized and "unknown" not in normalized else 0,
        len(normalized),
    )


def _burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    normalized = " ".join(label.lower().split())
    if _has_seizure_free_label(normalized):
        return _seizure_free_burden_from_label(normalized, source_phrase=source_phrase)
    if _has_cluster_label(normalized):
        return _cluster_burden_from_label(normalized, source_phrase=source_phrase)
    if normalized in {"unknown", "no seizure frequency reference"}:
        return NormalizedBurden(source_normalized_phrase=source_phrase), []
    return _rate_burden_from_label(normalized, source_phrase=source_phrase)


def _cluster_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    normalized = " ".join(label.lower().split())
    if not _has_cluster_label(normalized):
        burden, issues = _rate_burden_from_label(normalized, source_phrase=source_phrase)
        return (
            NormalizedBurden(
                cluster_count_low=burden.count_low,
                cluster_count_high=burden.count_high,
                cluster_period_low=burden.period_low,
                cluster_period_high=burden.period_high,
                cluster_period_unit=burden.period_unit,
                source_normalized_phrase=source_phrase,
            ),
            issues,
        )
    match = re.match(
        r"^(?P<count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"clusters?\s+per\s+"
        r"(?:(?P<period_count>\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+)?"
        r"(?P<period_unit>day|week|month|year),\s+"
        r"(?P<events>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"per\s+cluster$",
        normalized,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_label_values_unparsed"
        ]
    count_low, count_high, count_issue = _parse_label_range(match.group("count"))
    period_low, period_high, period_issue = _parse_label_range(
        match.group("period_count") or "1"
    )
    events_low, events_high, events_issue = _parse_label_range(match.group("events"))
    issues = [
        issue
        for issue in (count_issue, period_issue, events_issue)
        if issue is not None
    ]
    return (
        NormalizedBurden(
            cluster_count_low=count_low,
            cluster_count_high=count_high,
            cluster_period_low=period_low,
            cluster_period_high=period_high,
            cluster_period_unit=match.group("period_unit"),  # type: ignore[arg-type]
            events_per_cluster_low=events_low,
            events_per_cluster_high=events_high,
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )


def _rate_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    match = re.match(
        r"^(?P<count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"per\s+"
        r"(?:(?P<period_count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+)?"
        r"(?P<period_unit>day|week|month|year)$",
        label,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "frequency_label_values_unparsed"
        ]
    count_low, count_high, count_issue = _parse_label_range(match.group("count"))
    period_low, period_high, period_issue = _parse_label_range(
        match.group("period_count") or "1"
    )
    issues = [issue for issue in (count_issue, period_issue) if issue is not None]
    return (
        NormalizedBurden(
            count_low=count_low,
            count_high=count_high,
            vague_count="multiple" if count_issue == "vague_count" else None,
            period_low=period_low,
            period_high=period_high,
            period_unit=match.group("period_unit"),  # type: ignore[arg-type]
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )


def _seizure_free_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    match = re.match(
        r"^seizure free for (?P<count>multiple|\d+(?:\.\d+)?) "
        r"(?P<unit>day|week|month|year)$",
        label,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "seizure_free_label_values_unparsed"
        ]
    low, high, issue = _parse_label_range(match.group("count"))
    return (
        NormalizedBurden(
            seizure_free_duration_low=low,
            seizure_free_duration_high=high,
            seizure_free_duration_unit=match.group("unit"),  # type: ignore[arg-type]
            source_normalized_phrase=source_phrase,
        ),
        [issue] if issue else [],
    )


def _parse_label_range(value: str) -> tuple[float | None, float | None, str | None]:
    if value == "multiple":
        return None, None, "vague_count"
    if " to " in value:
        left, right = value.split(" to ", maxsplit=1)
        left_value = float(left)
        right_value = float(right)
        return min(left_value, right_value), max(left_value, right_value), None
    parsed = float(value)
    return parsed, parsed, None


def _has_cluster_label(label: str) -> bool:
    return "cluster" in label


def _has_seizure_free_label(label: str) -> bool:
    return label.startswith("seizure free for ")


def _clean_phrase(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_phrase_for_parse(value: str) -> str:
    text = value.lower()
    text = re.sub(r"[≈~]", "", text)
    if not re.search(r"\b\d{2}-\d{2}(?:,\s*\d{2}-\d{2})+\b", text):
        text = re.sub(r"(?<=\d)\s*[-–—]\s*(?=\d)", " to ", text)
    text = re.sub(r"\bper\s+24\s*h(?:ours?)?\b", "per day", text)
    text = re.sub(r"\b24\s*h(?:ours?)?\b", "day", text)
    
    # Normalize fortnight patterns to 2 weeks
    text = re.sub(r"\bfortnightly\b", "every 2 weeks", text)
    text = re.sub(r"\ba\s+fortnight\b", "2 weeks", text)
    text = re.sub(r"\bfortnight\b", "2 weeks", text)
    
    # Normalize range patterns like "once every X to Y weeks" -> "1 per X to Y weeks"
    text = re.sub(
        r"\bonce\s+every\s+(\d+)\s+to\s+(\d+)\s+(day|week|month|year)s?\b",
        r"1 per \1 to \2 \3s",
        text,
    )
    text = re.sub(
        r"\b(?:roughly|approximately)?\s*once\s+in\s+(\d+)\s+(day|week|month|year)s?\b",
        r"1 per \1 \2s",
        text,
    )
    text = re.sub(
        r"\b(?:roughly|approximately)?\s*once\s+in\s+a\s+"
        r"(day|week|month|year)\b",
        r"1 per 1 \1",
        text,
    )
    
    return " ".join(text.split())


def _build_candidate_set_live(
    record: GanFrequencyRecord,
    *,
    extractor_program: candidate_extractor_probe.DspyCandidateSetExtractor,
    extractor_lm: Any | None,
    extractor_adapter: Any | None,
    mode: Literal["live", "prompt-only"],
) -> tuple[CandidateSet, dict[str, Any]]:
    """Build one row's CandidateSet live: deterministic + LLM extraction, unioned.

    Replicates the methodology that built the static
    `gan2026_validation250_candidate_set_v2_high_recall.jsonl` artifact
    (deterministic_candidate_set_from_raw -> DspyCandidateSetExtractor ->
    build_candidate_set_union_rows) per record, so `hybrid` covers the full
    surface instead of only the 250 rows someone happened to precompute.
    """
    raw_candidates = deterministic_extraction._extract_candidates(record.note_text)  # noqa: SLF001
    if not raw_candidates:
        raw_candidates = [
            RawCandidate(
                kind=DeterministicCandidateKind.NO_REFERENCE,
                label="no seizure frequency reference",
                evidence=fallback_evidence(record.note_text),
            )
        ]
    deterministic_set = deterministic_candidate_set_from_raw(
        raw_candidates,
        note_text=record.note_text,
        source_row_index=record.source_row_index,
    )

    llm_set: CandidateSet | None = None
    llm_call_error: str | None = None
    llm_parse_errors: list[str] = []
    if mode == "live":
        typed_input = candidate_extractor_probe.build_candidate_set_inputs(record)
        prediction: Any | None = None
        try:
            with dspy.context(lm=extractor_lm, adapter=extractor_adapter):
                prediction = extractor_program(**typed_input)
        except Exception as exc:  # pragma: no cover - live API only.
            llm_call_error = f"{type(exc).__name__}: {exc}"
        if prediction is not None:
            draft_set, llm_parse_errors = (
                candidate_extractor_probe.prediction_to_candidate_draft_set(prediction)
            )
            llm_set = candidate_extractor_probe.assemble_candidate_set(draft_set, record=record)

    deterministic_row = {
        "source_row_index": record.source_row_index,
        "candidate_set": deterministic_set.model_dump(),
    }
    llm_rows = (
        [{"source_row_index": record.source_row_index, "candidate_set": llm_set.model_dump()}]
        if llm_set is not None
        else []
    )
    union_rows, _ = build_candidate_set_union_rows([deterministic_row], llm_rows)
    candidate_set = CandidateSet.model_validate(union_rows[0]["candidate_set"])

    diagnostics = {
        "candidate_set_source": "live_deterministic_llm_union",
        "llm_extraction_call_error": llm_call_error,
        "llm_extraction_parse_errors": llm_parse_errors,
    }
    return candidate_set, diagnostics


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    candidate_set_jsonl_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run clinical-assessment schema probe over records."""

    live_candidate_sets = candidate_set_jsonl_path is None
    candidate_sets: Mapping[int, CandidateSet] = {}
    if not live_candidate_sets:
        candidate_set_path = candidate_set_jsonl_path or DEFAULT_CANDIDATE_SET_JSONL_PATH
        candidate_sets = selector_probe.load_candidate_sets(candidate_set_path)
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["escalation_reason"] = escalation_reason
    if live_candidate_sets:
        metadata["candidate_set_jsonl_path"] = "live"
        metadata["candidate_set_source"] = "live_deterministic_llm_union"
    else:
        metadata["candidate_set_jsonl_path"] = str(candidate_set_path)
        metadata["candidate_set_source"] = "static_artifact"
    program = DspyCandidateSetClinicalAssessment()
    lm = None
    adapter = None
    extractor_program = None
    extractor_lm = None
    extractor_adapter = None
    if mode == "live":
        lm = build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )
        adapter = dspy.JSONAdapter()
    if live_candidate_sets:
        extractor_program = candidate_extractor_probe.DspyCandidateSetExtractor()
        if mode == "live":
            extractor_lm = build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
            extractor_adapter = dspy.JSONAdapter()

    rows: list[dict[str, Any]] = []
    for record in records:
        candidate_set_diagnostics: dict[str, Any] | None = None
        if live_candidate_sets:
            candidate_set, candidate_set_diagnostics = _build_candidate_set_live(
                record,
                extractor_program=extractor_program,
                extractor_lm=extractor_lm,
                extractor_adapter=extractor_adapter,
                mode=mode,
            )
        else:
            candidate_set = candidate_sets.get(record.source_row_index)
            if candidate_set is None:
                rows.append(_missing_candidate_set_row(record, split, split_manifest))
                continue
        typed_input = build_assessment_inputs(record, candidate_set)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_input)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        draft, parse_errors = (
            prediction_to_assessment_draft(prediction)
            if prediction is not None
            else (None, ["not_run"])
        )
        assessment, assembly_errors = assemble_clinical_assessment(
            draft,
            candidate_set=candidate_set,
        )
        row = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_name": PROMPT_VERSION,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "candidate_set": candidate_set.model_dump(),
            "candidate_set_diagnostics": candidate_set_diagnostics,
            "typed_input": typed_input,
            "raw_output": _raw_output_from_assessment(assessment),
            "call_error": call_error,
            "parse_errors": [*parse_errors, *assembly_errors],
            "assessment_draft": draft.model_dump() if draft else None,
            "clinical_assessment": assessment.model_dump() if assessment else None,
            "schema_probe": _schema_probe(assessment),
        }
        rows.append(row)
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_records(rows)
    return rows, metadata


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize clinical-assessment schema fit without scoring."""

    assessments = [row for row in rows if row.get("clinical_assessment")]
    kind_counts = Counter(
        str((row.get("clinical_assessment") or {}).get("assessment_kind"))
        for row in assessments
    )
    policy_counts = Counter(
        str((row.get("clinical_assessment") or {}).get("aggregation_policy"))
        for row in assessments
    )
    return {
        "examples": len(rows),
        "clinical_assessment_rows": len(assessments),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_or_validation_failures": sum(bool(row.get("parse_errors")) for row in rows),
        "missing_candidate_set_rows": sum(
            "candidate_set_missing" in (row.get("parse_errors") or []) for row in rows
        ),
        "assessment_kind_counts": dict(sorted(kind_counts.items())),
        "aggregation_policy_counts": dict(sorted(policy_counts.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    /,
    *,
    jsonl_path: Path,
) -> None:
    """Write a compact Markdown clinical-assessment report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 CandidateSet Clinical Assessment Probe",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline: `{PIPELINE_FAMILY}`",
        f"- Prompt/schema version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- CandidateSet JSONL: `{metadata.get('candidate_set_jsonl_path')}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        (
            "- Claim language: clinical-assessment schema-fit probe only; "
            "no score calculation and no rendered answers."
        ),
        "",
        "## Summary",
        "",
        (
            f"- Clinical assessment rows: {summary.get('clinical_assessment_rows', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/validation failure rows: {summary.get('parse_or_validation_failures', 0)}",
        f"- Missing candidate-set rows: {summary.get('missing_candidate_set_rows', 0)}",
        "",
        "## Assessment Kinds",
        "",
    ]
    for kind, count in (summary.get("assessment_kind_counts") or {}).items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Aggregation Policies", ""])
    for policy, count in (summary.get("aggregation_policy_counts") or {}).items():
        lines.append(f"- `{policy}`: {count}")
    lines.extend(["", "## Row Notes", ""])
    lines.extend(_row_note_lines(rows))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _candidate_set_for_prompt(candidate_set: CandidateSet) -> dict[str, Any]:
    return {
        "source_row_index": candidate_set.source_row_index,
        "component_owner": candidate_set.component_owner,
        "source_artifacts": candidate_set.source_artifacts,
        "row_context": candidate_set.row_context.model_dump(),
        "assembly_issues": candidate_set.assembly_issues,
        "candidates": [
            {
                "candidate_id": candidate.candidate_id,
                "source_type": candidate.source_type,
                "candidate_kind": candidate.candidate_kind,
                "event_type": candidate.event_type,
                "temporality": candidate.temporality,
                "certainty": candidate.certainty,
                "assertion_status": candidate.assertion_status,
                "evidence_text": candidate.evidence_span.text,
                "source_phrase": candidate_source_phrase(candidate),
                "source_ids": candidate.source_ids,
                "extraction_issues": candidate.extraction_issues,
            }
            for candidate in candidate_set.candidates
        ],
    }


def _policy_examples() -> list[dict[str, str]]:
    return [
        {
            "case": "Additive same-window burden",
            "candidates": (
                "A says 3 focal aware seizures this month; B says 2 focal "
                "impaired-awareness seizures this month."
            ),
            "assessment": (
                "Use both as primary with additive_same_window when the note supports "
                "separate event types contributing to the same current burden."
            ),
        },
        {
            "case": "Vague frequency plus isolated concrete event",
            "candidates": (
                "A says brief absences occur on most weekdays; B says one tonic-clonic "
                "seizure occurred in the last eight weeks."
            ),
            "assessment": (
                "Do not use additive_same_window because A is a vague unknown-frequency "
                "burden. Use the clinically dominant current burden as primary and keep "
                "the other fact as supporting context unless the note clearly requires "
                "a combined exact rate."
            ),
        },
        {
            "case": "No usable primary candidate",
            "candidates": "The CandidateSet is empty or contains no seizure-frequency fact.",
            "assessment": (
                "Use unknown_frequency with unknown_due_to_absence, or no_reference with "
                "no_reference_boundary when there is truly no reference. Do not return "
                "frequency_rate with an empty primary_candidate_ids list."
            ),
        },
        {
            "case": "Primary with non-additive context",
            "candidates": (
                "A says brief seizures occur daily; B says there was one short cluster "
                "last week after poor sleep."
            ),
            "assessment": (
                "Use A as the only primary with primary_with_context. Put B in support "
                "and leave cluster fields empty because the current burden is the "
                "daily frequency."
            ),
        },
        {
            "case": "Repeated reference to same burden",
            "candidates": (
                "A says the current average is 4 seizures per month; B later says "
                "the patient remains at about 4 seizures per month."
            ),
            "assessment": (
                "Use the more specific current-burden statement as primary. Put the "
                "repeat reference in supporting_candidate_ids unless the note says it "
                "describes additional non-overlapping events."
            ),
        },
        {
            "case": "Total count plus subtype",
            "candidates": (
                "A says 8 seizures in the past two months; B says 1 was nocturnal."
            ),
            "assessment": (
                "Use A as primary. Put B in supporting or rejected context because "
                "it may already be included in A."
            ),
        },
        {
            "case": "Frequency plus cluster modifier",
            "candidates": (
                "A says 12 seizures per month; B says events sometimes cluster "
                "after sleep loss."
            ),
            "assessment": (
                "Use A as primary with primary_with_context. B is context, not "
                "additive burden."
            ),
        },
        {
            "case": "Current burden plus historical comparison",
            "candidates": (
                "A says current seizures are about once per month; B says the patient "
                "previously had weekly clusters before treatment."
            ),
            "assessment": (
                "Use A as primary. Put B in supporting context. normalized_burden "
                "should contain only the current once-per-month burden, while the "
                "summary may mention improvement."
            ),
        },
        {
            "case": "Recent cluster plus later seizure-free interval",
            "candidates": (
                "A says 5 to 7 focal seizures occurred over three weeks; B says the "
                "patient then had six seizure-free weeks."
            ),
            "assessment": (
                "Use A as primary. Put B in support. Do not fill seizure-free duration "
                "fields unless the assessment is seizure_free."
            ),
        },
        {
            "case": "Cluster cadence plus per-cluster burden",
            "candidates": (
                "A says clusters every 4 weeks; B says each cluster contains 2 to 3 events."
            ),
            "assessment": (
                "Use both as primary with cluster_axis because they describe separate "
                "axes of one cluster assessment."
            ),
        },
        {
            "case": "Seizure-free outside a pattern window",
            "candidates": (
                "A says seizures occur only during a recurring risk window; B says "
                "no seizures outside that window."
            ),
            "assessment": (
                "Use A as primary and B as supporting context. Do not add them "
                "together as frequency evidence, and do not fill seizure_free_duration "
                "fields unless the assessment_kind is seizure_free."
            ),
        },
        {
            "case": "Precise count plus vague bursts",
            "candidates": (
                "A says 2 generalized seizures in six weeks; B says short runs of "
                "brief events over several days."
            ),
            "assessment": (
                "Do not combine into an exact count unless the note clearly says "
                "the vague events are additional and non-overlapping."
            ),
        },
    ]


def _validate_candidate_references(
    draft: AssessmentDraft,
    candidate_set: CandidateSet,
) -> list[str]:
    known = {candidate.candidate_id for candidate in candidate_set.candidates}
    errors: list[str] = []
    for role_name, candidate_ids in (
        ("primary_candidate_ids", draft.primary_candidate_ids),
        ("supporting_candidate_ids", draft.supporting_candidate_ids),
        ("rejected_candidate_ids", draft.rejected_candidate_ids),
    ):
        for candidate_id in candidate_ids:
            if candidate_id not in known:
                errors.append(f"{role_name}:unknown_candidate_id:{candidate_id}")
    return errors


def _validation_error_messages(exc: ValidationError) -> list[str]:
    return [str(error.get("msg", error)) for error in exc.errors()]


def _schema_probe(assessment: ClinicalAssessment | None) -> dict[str, Any]:
    if assessment is None:
        return {"clinical_assessment_fit": False}
    return {
        "clinical_assessment_fit": True,
        "assessment_kind": assessment.assessment_kind,
        "aggregation_policy": assessment.aggregation_policy,
        "primary_candidate_count": len(assessment.primary_candidate_ids),
        "supporting_candidate_count": len(assessment.supporting_candidate_ids),
        "rejected_candidate_count": len(assessment.rejected_candidate_ids),
    }


def _raw_output_from_assessment(assessment: ClinicalAssessment | None) -> str:
    if assessment is None:
        return ""
    return json.dumps(assessment.model_dump(), sort_keys=True)


def _missing_candidate_set_row(
    record: GanFrequencyRecord,
    split: str,
    split_manifest: str,
) -> dict[str, Any]:
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "pipeline_family": PIPELINE_FAMILY,
        "pipeline_name": PROMPT_VERSION,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "typed_input": None,
        "raw_output": "",
        "call_error": None,
        "parse_errors": ["candidate_set_missing"],
        "assessment_draft": None,
        "clinical_assessment": None,
        "schema_probe": {"clinical_assessment_fit": False},
    }


def _row_note_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        if not row.get("parse_errors"):
            continue
        lines.append(
            "- "
            f"{row.get('source_row_index')}: "
            f"{'; '.join(str(error) for error in row.get('parse_errors') or [])}"
        )
    if not lines:
        return ["- No parse or validation errors."]
    return lines


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_records(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    print(
        json.dumps(
            {
                "pipeline": PIPELINE_FAMILY,
                "completed_rows": len(rows),
                "total_rows": total,
                "summary": metadata["summary"],
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None = None,
) -> dict[str, Any]:
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
        extra={
            "architecture": PIPELINE_FAMILY,
            "claim_type": PIPELINE_FAMILY,
            "pipeline_name": PROMPT_VERSION,
            "pipeline_family": "llm_only",
            "typed_output_schema_version": SCHEMA_VERSION,
            "scoring_enabled": False,
            "rendered_answer_forbidden": True,
        },
    )
