"""LLM selector schema probe over Gan 2026 CandidateSet artifacts."""

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
    CandidateKind,
    CandidateSet,
    EvidenceSpan,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.selected_fact import (
    SCHEMA_VERSION,
    SelectedClinicalFact,
    SelectionBasis,
    SelectionStatus,
    UnknownBasis,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "gan2026_candidate_set_selector_schema_probe_v0"
PIPELINE_FAMILY = "llm_candidate_set_selector_schema_probe"
DEFAULT_CANDIDATE_SET_JSONL_PATH = Path(
    "experiments/gan2026_validation250_candidate_set_v2_high_recall.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_selector_schema_probe_validation25_gpt41mini_v0_2026-06-05.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_candidate_set_selector_schema_probe_validation25_gpt41mini_v0_2026-06-05.md"
)


class SelectionDraft(BaseModel):
    """Model-owned clinical selection fields only."""

    model_config = ConfigDict(extra="forbid")

    selection_status: SelectionStatus
    selection_basis: SelectionBasis
    clinical_fact_kind: CandidateKind | None = None
    selected_candidate_ids: list[str] = Field(default_factory=list)
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    primary_evidence_texts: list[str] = Field(default_factory=list)
    unknown_basis: UnknownBasis | None = None
    ambiguity_flags: list[str] = Field(default_factory=list)
    conflict_flags: list[str] = Field(default_factory=list)
    source_reliability_flags: list[str] = Field(default_factory=list)
    selection_issues: list[str] = Field(default_factory=list)
    rationale: str = ""


class Gan2026CandidateSetSelectorSignature(dspy.Signature):
    """Select or abstain over a row-level source-near CandidateSet."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    source_row_index: int = dspy.InputField(desc="Source row index.")
    task_instructions: list[str] = dspy.InputField(desc="Selector instructions.")
    candidate_set: dict[str, Any] = dspy.InputField(desc="Source-near candidates.")
    output_contract: dict[str, Any] = dspy.InputField(desc="SelectedClinicalFact contract.")
    selection_draft: SelectionDraft = dspy.OutputField(
        desc="Clinical selection fields only; provenance and spans are filled by code."
    )


class DspyCandidateSetSelector(dspy.Module):
    """DSPy typed-output selector for the reset selected-fact schema."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026CandidateSetSelectorSignature)

    def forward(
        self,
        *,
        note_text: str,
        source_row_index: int,
        task_instructions: list[str],
        candidate_set: dict[str, Any],
        output_contract: dict[str, Any],
    ) -> dspy.Prediction:
        return self.predict(
            note_text=note_text,
            source_row_index=source_row_index,
            task_instructions=task_instructions,
            candidate_set=candidate_set,
            output_contract=output_contract,
        )


def build_selector_inputs(
    record: GanFrequencyRecord,
    candidate_set: CandidateSet,
) -> dict[str, Any]:
    """Build model-facing selector inputs without labels or normalized answers."""

    return {
        "note_text": record.note_text,
        "source_row_index": record.source_row_index,
        "task_instructions": [
            (
                "Select the clinically relevant current seizure-frequency fact from "
                "the candidate_set, or explicitly abstain."
            ),
            (
                "Do not emit a benchmark label, normalized rate, monthly frequency, "
                "yearly frequency, or scorer-facing answer."
            ),
            (
                "Use selected only when one candidate or a small compatible group is "
                "reliable enough to carry forward."
            ),
            (
                "Prefer explicit current frequency_rate, seizure_free, or "
                "cluster_frequency candidates over vague unknown_frequency candidates."
            ),
            (
                "Use no_reliable_candidate when the row has no reliable current "
                "frequency fact, even if vague or low-quality candidates are present."
            ),
            (
                "Use unknown_basis extracted_unknown_candidate only when an "
                "unknown_frequency candidate is itself the best clinical fact to "
                "carry forward."
            ),
            (
                "Use unknown_basis absence_of_usable_frequency_evidence when unknown "
                "is better explained by the absence of reliable usable evidence."
            ),
            (
                "Use ambiguous when multiple plausible candidates cannot be resolved "
                "without policy or verifier help."
            ),
            "Use conflict when candidates make incompatible current claims.",
            "Use human_review when the row is too risky for automatic selection.",
            (
                "Put risky candidates in rejected_candidate_ids when they are "
                "tempting but should not control the selected fact."
            ),
            "Copy primary_evidence_texts exactly from selected candidate evidence when selected.",
            "Return only selection_draft.",
        ],
        "candidate_set": _candidate_set_for_prompt(candidate_set),
        "output_contract": {
            "schema_version": SCHEMA_VERSION,
            "model_outputs_only": ["selection_draft"],
            "filled_by_code": [
                "source_row_index",
                "component_owner",
                "source_artifacts",
                "primary_evidence.start_char",
                "primary_evidence.end_char",
                "source_ids",
                "temporality",
                "certainty",
                "clinical_or_policy",
            ],
            "selection_status_values": [
                "selected",
                "ambiguous",
                "conflict",
                "no_reliable_candidate",
                "human_review",
            ],
            "unknown_basis_values": [
                "extracted_unknown_candidate",
                "absence_of_usable_frequency_evidence",
                "uncertain_only",
                "conflicting_candidates",
                "verifier_required",
                "not_applicable",
            ],
        },
    }


def assemble_selected_fact(
    draft: SelectionDraft | None,
    *,
    candidate_set: CandidateSet,
) -> tuple[SelectedClinicalFact | None, list[str]]:
    """Assemble a full SelectedClinicalFact from model-owned selection fields."""

    if draft is None:
        return None, ["selection_draft_missing"]

    errors = _validate_candidate_references(draft, candidate_set)
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    selected_candidates = [
        candidate_by_id[candidate_id]
        for candidate_id in draft.selected_candidate_ids
        if candidate_id in candidate_by_id
    ]
    primary_evidence = [
        EvidenceSpan(
            text=candidate.evidence_span.text,
            start_char=candidate.evidence_span.start_char,
            end_char=candidate.evidence_span.end_char,
        )
        for candidate in selected_candidates
    ]
    if draft.primary_evidence_texts and selected_candidates:
        selected_evidence = {candidate.evidence_span.text for candidate in selected_candidates}
        missing = [
            text for text in draft.primary_evidence_texts if text not in selected_evidence
        ]
        errors.extend(f"primary_evidence_text_not_selected_candidate:{text}" for text in missing)
    source_ids = [
        source_id
        for candidate in selected_candidates
        for source_id in candidate.source_ids
    ]
    temporality = _common_value([candidate.temporality for candidate in selected_candidates])
    certainty = _common_value([candidate.certainty for candidate in selected_candidates])

    try:
        selection = SelectedClinicalFact(
            source_row_index=candidate_set.source_row_index,
            component_owner="llm_candidate_set_selector",
            source_artifacts=candidate_set.source_artifacts,
            selection_status=draft.selection_status,
            selection_basis=draft.selection_basis,
            clinical_fact_kind=draft.clinical_fact_kind,
            selected_candidate_ids=draft.selected_candidate_ids,
            supporting_candidate_ids=draft.supporting_candidate_ids,
            rejected_candidate_ids=draft.rejected_candidate_ids,
            primary_evidence=primary_evidence,
            source_ids=source_ids,
            temporality=temporality,
            certainty=certainty,
            unknown_basis=draft.unknown_basis,
            ambiguity_flags=draft.ambiguity_flags,
            conflict_flags=draft.conflict_flags,
            source_reliability_flags=draft.source_reliability_flags,
            selection_issues=[*draft.selection_issues, *errors],
            rationale=draft.rationale,
        )
    except ValidationError as exc:
        errors.extend(_validation_error_messages(exc))
        return None, errors
    return selection, errors


def prediction_to_selection_draft(
    prediction: Any,
) -> tuple[SelectionDraft | None, list[str]]:
    """Parse DSPy prediction output into a SelectionDraft."""

    try:
        value = prediction.selection_draft
    except AttributeError:
        return None, ["selection_draft_missing"]
    if isinstance(value, SelectionDraft):
        return value, []
    try:
        return SelectionDraft.model_validate(value), []
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run selector schema probe over records using the default candidate-set artifact."""

    candidate_sets = load_candidate_sets(DEFAULT_CANDIDATE_SET_JSONL_PATH)
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
    metadata["candidate_set_jsonl_path"] = str(DEFAULT_CANDIDATE_SET_JSONL_PATH)
    program = DspyCandidateSetSelector()
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
        typed_input = build_selector_inputs(record, candidate_set)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_input)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        draft, parse_errors = (
            prediction_to_selection_draft(prediction)
            if prediction is not None
            else (None, ["not_run"])
        )
        selection, assembly_errors = assemble_selected_fact(draft, candidate_set=candidate_set)
        row = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_name": PROMPT_VERSION,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "typed_input": typed_input,
            "raw_output": _raw_output_from_selection(selection),
            "call_error": call_error,
            "parse_errors": [*parse_errors, *assembly_errors],
            "selection_draft": draft.model_dump() if draft else None,
            "selected_clinical_fact": selection.model_dump() if selection else None,
            "schema_probe": _schema_probe(selection),
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


def load_candidate_sets(path: Path) -> dict[int, CandidateSet]:
    """Load row-level CandidateSet objects from a JSONL artifact."""

    candidate_sets: dict[int, CandidateSet] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            candidate_set_payload = payload.get("candidate_set") or payload
            candidate_set = CandidateSet.model_validate(candidate_set_payload)
            candidate_sets[candidate_set.source_row_index] = candidate_set
    return candidate_sets


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize selector schema fit without scoring."""

    selections = [row for row in rows if row.get("selected_clinical_fact")]
    status_counts = Counter(
        str((row.get("selected_clinical_fact") or {}).get("selection_status"))
        for row in selections
    )
    basis_counts = Counter(
        str((row.get("selected_clinical_fact") or {}).get("selection_basis"))
        for row in selections
    )
    return {
        "examples": len(rows),
        "selected_fact_rows": len(selections),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_or_validation_failures": sum(bool(row.get("parse_errors")) for row in rows),
        "missing_candidate_set_rows": sum(
            "candidate_set_missing" in (row.get("parse_errors") or []) for row in rows
        ),
        "selection_status_counts": dict(sorted(status_counts.items())),
        "selection_basis_counts": dict(sorted(basis_counts.items())),
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
    """Write a compact Markdown selector schema-probe report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 CandidateSet Selector Schema Probe",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline: `{PIPELINE_FAMILY}`",
        f"- Prompt/schema version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- CandidateSet JSONL: `{metadata.get('candidate_set_jsonl_path')}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        "- Claim language: selector schema-fit probe only; no scoring and no final labels.",
        "",
        "## Summary",
        "",
        (
            f"- Selected fact rows: {summary.get('selected_fact_rows', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/validation failure rows: {summary.get('parse_or_validation_failures', 0)}",
        f"- Missing candidate-set rows: {summary.get('missing_candidate_set_rows', 0)}",
        "",
        "## Selection Status",
        "",
    ]
    for status, count in (summary.get("selection_status_counts") or {}).items():
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Selection Basis", ""])
    for basis, count in (summary.get("selection_basis_counts") or {}).items():
        lines.append(f"- `{basis}`: {count}")
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


def _validate_candidate_references(
    draft: SelectionDraft,
    candidate_set: CandidateSet,
) -> list[str]:
    known = {candidate.candidate_id for candidate in candidate_set.candidates}
    errors: list[str] = []
    for field_name in (
        "selected_candidate_ids",
        "supporting_candidate_ids",
        "rejected_candidate_ids",
    ):
        for candidate_id in getattr(draft, field_name):
            if candidate_id not in known:
                errors.append(f"{field_name}:unknown_candidate_id:{candidate_id}")
    return errors


def _common_value(values: Sequence[str]) -> str | None:
    if not values:
        return None
    return values[0] if len(set(values)) == 1 else "mixed"


def _validation_error_messages(exc: ValidationError) -> list[str]:
    return [str(error.get("msg", error)) for error in exc.errors()]


def _schema_probe(selection: SelectedClinicalFact | None) -> dict[str, Any]:
    if selection is None:
        return {"selected_fact_fit": False}
    return {
        "selected_fact_fit": True,
        "selection_status": selection.selection_status,
        "selection_basis": selection.selection_basis,
        "selected_candidate_count": len(selection.selected_candidate_ids),
        "rejected_candidate_count": len(selection.rejected_candidate_ids),
    }


def _raw_output_from_selection(selection: SelectedClinicalFact | None) -> str:
    if selection is None:
        return ""
    return json.dumps(selection.model_dump(), sort_keys=True)


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
        "selection_draft": None,
        "selected_clinical_fact": None,
        "schema_probe": {"selected_fact_fit": False},
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
            "final_label_forbidden": True,
        },
    )
