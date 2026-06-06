"""LLM clinical-assessment probe over Gan 2026 CandidateSet artifacts."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    SCHEMA_VERSION,
    AggregationPolicy,
    AssessmentKind,
    ClinicalAssessment,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)

PROMPT_VERSION = "gan2026_candidate_set_clinical_assessment_probe_v3"
PIPELINE_FAMILY = "llm_candidate_set_clinical_assessment_probe"
NORMALIZATION_POLICY_ID = "gan2026_clinical_assessment_normalization_v0"
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
    parsed operands.
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
    aggregation_policy: AggregationPolicy
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
                "count, range, period, interval, duration, and cluster operand parsing."
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
                "normalized_burden fields."
            ),
            (
                "Preserve cluster structure: cluster cadence and events per cluster are "
                "separate axes unless the same evidence clearly gives both."
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
) -> tuple[ClinicalAssessment | None, list[str]]:
    """Assemble a clinical assessment from model-owned fields."""

    if draft is None:
        return None, ["assessment_draft_missing"]

    errors = _validate_candidate_references(draft, candidate_set)
    draft, override_issues = _apply_deterministic_assessment_overrides(
        draft,
        candidate_set=candidate_set,
    )
    normalized_burden, normalization_issues = normalize_assessment_burden(
        draft,
        candidate_set=candidate_set,
    )
    normalization_issues = [*override_issues, *normalization_issues]
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
            and not any(issue for issue in issues if issue != "vague_count")
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
) -> tuple[NormalizedBurden, list[str]]:
    """Deterministically parse source-near assessment burden operands."""

    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    issues: list[str] = []
    if not source_phrase:
        issues.append("normalization_source_phrase_missing")

    if draft.assessment_kind == "frequency_rate":
        if draft.aggregation_policy == "additive_same_window":
            burden, additive_issues = _additive_frequency_burden(
                primary_candidates,
                source_phrase=source_phrase,
            )
            issues.extend(additive_issues)
            return burden, issues
        burden, rate_issues = _frequency_burden(source_phrase)
        issues.extend(rate_issues)
        return burden, issues

    if draft.assessment_kind == "cluster_frequency":
        burden, cluster_issues = _cluster_burden(primary_candidates, source_phrase=source_phrase)
        issues.extend(cluster_issues)
        return burden, issues

    if draft.assessment_kind == "seizure_free":
        burden, seizure_free_issues = _seizure_free_burden(source_phrase)
        issues.extend(seizure_free_issues)
        return burden, issues

    return NormalizedBurden(source_normalized_phrase=source_phrase), issues


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


def _frequency_burden(source_phrase: str) -> tuple[NormalizedBurden, list[str]]:
    label = _deterministic_label_from_source_phrase(
        source_phrase,
        preferred_kind=DeterministicCandidateKind.FREQUENCY_RATE,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "frequency_rate_operands_unparsed"
        ]
    burden, issues = _burden_from_label(label, source_phrase=source_phrase)
    if _has_cluster_label(label):
        issues.append("frequency_rate_label_derivation_returned_cluster")
    if _has_seizure_free_label(label):
        issues.append("frequency_rate_label_derivation_returned_seizure_free")
    return burden, issues


def _additive_frequency_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    parsed = [
        _frequency_burden(candidate_source_phrase(candidate) or candidate.evidence_span.text)
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
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            *issues,
            "additive_frequency_period_mismatch",
        ]
    if any(burden.count_low is None or burden.count_high is None for burden in burdens):
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
            "cluster_frequency_operands_unparsed"
        ]
    burden, issues = _cluster_burden_from_label(label, source_phrase=source_phrase)
    return burden, issues


def _seizure_free_burden(source_phrase: str) -> tuple[NormalizedBurden, list[str]]:
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
            "cluster_label_operands_unparsed"
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
            "frequency_label_operands_unparsed"
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
            "seizure_free_label_operands_unparsed"
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
    text = re.sub(r"\s*[-–—]\s*", " to ", text)
    text = re.sub(r"\bper\s+24\s*h(?:ours?)?\b", "per day", text)
    text = re.sub(r"\b24\s*h(?:ours?)?\b", "day", text)
    return " ".join(text.split())


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
    metadata["candidate_set_jsonl_path"] = str(candidate_set_path)
    program = DspyCandidateSetClinicalAssessment()
    lm = None
    adapter = None
    if mode == "live":
        lm = build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )
        adapter = dspy.JSONAdapter()

    rows: list[dict[str, Any]] = []
    for record in records:
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
