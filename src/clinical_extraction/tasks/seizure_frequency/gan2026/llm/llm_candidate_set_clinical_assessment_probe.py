"""LLM clinical-assessment probe over Gan 2026 CandidateSet artifacts."""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
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

PROMPT_VERSION = "gan2026_candidate_set_clinical_assessment_probe_v2"
PIPELINE_FAMILY = "llm_candidate_set_clinical_assessment_probe"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_validation25_gpt41mini_v0_2026-06-05.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_validation25_gpt41mini_v0_2026-06-05.md"
)
DEFAULT_CANDIDATE_SET_JSONL_PATH = selector_probe.DEFAULT_CANDIDATE_SET_JSONL_PATH


class AssessmentDraft(BaseModel):
    """Model-owned clinical assessment fields."""

    model_config = ConfigDict(extra="forbid")

    assessment_kind: AssessmentKind
    primary_candidate_ids: list[str]
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    aggregation_policy: AggregationPolicy
    normalized_burden: NormalizedBurden
    assessment_summary: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)


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
                "normalize the burden source-nearly, and decide whether related "
                "facts are additive, contextual, rejected, or too ambiguous."
            ),
            (
                "Use primary_candidate_ids only for facts that determine the "
                "overarching burden. Put corroborating, trigger, subtype, historical, "
                "or non-additive context in supporting_candidate_ids or rejected_candidate_ids."
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
                "If multiple candidates repeat the same current burden in different "
                "parts of the note, use the most specific source-near candidate as "
                "primary and put the corroborating repeat references in support."
            ),
            (
                "Do not use historical candidates as primary for current burden when "
                "a current or recent candidate is available."
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
                "counts": "count_low/count_high or vague_count with period fields",
                "seizure_free": "seizure_free_duration fields",
                "cluster": "cluster cadence and events_per_cluster fields",
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
    try:
        assessment = ClinicalAssessment(
            source_row_index=candidate_set.source_row_index,
            component_owner="llm_candidate_set_clinical_assessment",
            assessment_kind=draft.assessment_kind,
            primary_candidate_ids=draft.primary_candidate_ids,
            supporting_candidate_ids=draft.supporting_candidate_ids,
            rejected_candidate_ids=draft.rejected_candidate_ids,
            aggregation_policy=draft.aggregation_policy,  # type: ignore[arg-type]
            normalized_burden=draft.normalized_burden,
            assessment_summary=draft.assessment_summary,
            uncertainty_flags=draft.uncertainty_flags,
        )
    except ValidationError as exc:
        errors.extend(_validation_error_messages(exc))
        return None, errors
    if errors:
        return None, errors
    return assessment, errors


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
                "together as frequency evidence."
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
