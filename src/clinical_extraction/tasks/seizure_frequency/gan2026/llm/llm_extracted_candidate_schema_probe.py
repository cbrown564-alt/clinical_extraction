"""LLM candidate-set extractor for the architecture reset schema probe."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    SCHEMA_VERSION,
    CandidateSet,
    ClusterDetails,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    LastEventOnlyDetails,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
    candidate_source_phrase,
    extract_row_context,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "gan2026_extracted_candidate_schema_probe_v6"
PIPELINE_FAMILY = "llm_extracted_candidate_schema_probe"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_extracted_candidate_schema_probe_validation25_gpt41mini_v6_2026-06-05.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_extracted_candidate_schema_probe_validation25_gpt41mini_v6_2026-06-05.md"
)


class CandidateDraft(BaseModel):
    """Model-owned clinical candidate fields only.

    Known provenance, ids, source artifact names, spans, and stage bookkeeping are
    filled deterministically after the model call.
    """

    model_config = ConfigDict(extra="ignore")

    candidate_kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    event_type: Literal["seizure", "seizure_like_event", "non_epileptic_event", "unclear_event"]
    event_subtype: str | None = None
    frequency: FrequencyDetails | None = None
    seizure_free: SeizureFreeDetails | None = None
    last_event_only: LastEventOnlyDetails | None = None
    cluster_details: ClusterDetails | None = None
    unknown_frequency: SourcePhraseOnlyDetails | None = None
    no_reference: SourcePhraseOnlyDetails | None = None
    temporality: Literal["current", "recent", "historical", "unclear"]
    certainty: Literal["certain", "uncertain"]
    certainty_reason: Literal[
        "vague_count",
        "unclear_time_period",
        "approximate_wording",
        "conditional_statement",
        "other",
    ] | None = None
    assertion_status: Literal["asserted", "negated", "uncertain", "conditional"]
    evidence_text: str

    @model_validator(mode="before")
    @classmethod
    def normalize_model_draft(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return value
        draft = dict(value)
        detail = draft.pop("detail", None)
        if isinstance(detail, Mapping):
            for key, detail_value in detail.items():
                draft.setdefault(str(key), detail_value)
        if "frequency_rate" in draft and "frequency" not in draft:
            alias_value = draft.pop("frequency_rate")
            draft["frequency"] = (
                alias_value.get("frequency")
                if isinstance(alias_value, Mapping) and "frequency" in alias_value
                else alias_value
            )
        temporality = draft.get("temporality")
        if temporality not in {"current", "recent", "historical", "unclear"}:
            draft["temporality"] = "unclear"
        if draft.get("certainty") == "uncertain" and not draft.get("certainty_reason"):
            draft["certainty_reason"] = "other"
        if draft.get("certainty") == "certain":
            draft["certainty_reason"] = None
        return _ensure_matching_detail(draft)

    @model_validator(mode="after")
    def validate_kind_detail(self) -> CandidateDraft:
        detail_by_kind = {
            "frequency_rate": self.frequency,
            "cluster_frequency": self.cluster_details,
            "seizure_free": self.seizure_free,
            "last_event_only": self.last_event_only,
            "unknown_frequency": self.unknown_frequency,
            "no_reference": self.no_reference,
        }
        populated = [name for name, value in detail_by_kind.items() if value is not None]
        if populated != [self.candidate_kind]:
            raise ValueError(
                "candidate_kind must have exactly one matching detail object; "
                f"candidate_kind={self.candidate_kind!r}, populated={populated!r}"
            )
        if self.certainty == "certain" and self.certainty_reason is not None:
            raise ValueError("certainty_reason must be null when certainty is certain")
        if self.certainty == "uncertain" and self.certainty_reason is None:
            raise ValueError("certainty_reason is required when certainty is uncertain")
        return self


class CandidateDraftSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[CandidateDraft]

    @model_validator(mode="before")
    @classmethod
    def wrap_bare_candidate_list(cls, value: Any) -> Any:
        if isinstance(value, list):
            return {"candidates": value}
        return value


def _ensure_matching_detail(draft: dict[str, Any]) -> dict[str, Any]:
    kind = draft.get("candidate_kind")
    evidence_text = str(draft.get("evidence_text") or "")
    detail_fields = {
        "frequency_rate": "frequency",
        "cluster_frequency": "cluster_details",
        "seizure_free": "seizure_free",
        "last_event_only": "last_event_only",
        "unknown_frequency": "unknown_frequency",
        "no_reference": "no_reference",
    }
    target_field = detail_fields.get(str(kind))
    if target_field is None:
        return draft
    for field in detail_fields.values():
        if field != target_field:
            draft[field] = None
    detail = draft.get(target_field)
    if target_field == "cluster_details":
        draft[target_field] = _cluster_detail_payload(detail, fallback=evidence_text)
        return draft
    draft[target_field] = _source_phrase_payload(detail, fallback=evidence_text)
    return draft


def _source_phrase_payload(value: Any, *, fallback: str) -> dict[str, str]:
    if isinstance(value, Mapping):
        source_phrase = value.get("source_phrase") or fallback
    elif isinstance(value, str):
        source_phrase = value
    else:
        source_phrase = fallback
    return {"source_phrase": str(source_phrase)}


def _cluster_detail_payload(value: Any, *, fallback: str) -> dict[str, str | None]:
    allowed = {
        "cluster_frequency",
        "events_per_cluster",
        "cluster_count",
        "cluster_period",
    }
    if isinstance(value, Mapping):
        payload = {
            key: str(raw_value)
            for key, raw_value in value.items()
            if key in allowed and raw_value is not None
        }
        if payload:
            return payload
        source_phrase = value.get("source_phrase")
        if source_phrase:
            return {"cluster_frequency": str(source_phrase)}
    if isinstance(value, str):
        return {"cluster_frequency": value}
    return {"cluster_frequency": fallback}


class Gan2026CandidateSetExtractorSignature(dspy.Signature):
    """Extract a row-level candidate set using kind-specific detail objects."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    source_row_index: int = dspy.InputField(desc="Source row index.")
    task_instructions: list[str] = dspy.InputField(desc="Candidate extraction instructions.")
    output_contract: dict[str, Any] = dspy.InputField(desc="CandidateSet schema contract.")
    candidate_draft_set: CandidateDraftSet = dspy.OutputField(
        desc="Clinical candidate drafts only; ids and provenance are filled by code."
    )


class DspyCandidateSetExtractor(dspy.Module):
    """DSPy typed-output extractor for the reset candidate schema."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026CandidateSetExtractorSignature)

    def forward(
        self,
        *,
        note_text: str,
        source_row_index: int,
        task_instructions: list[str],
        output_contract: dict[str, Any],
    ) -> dspy.Prediction:
        return self.predict(
            note_text=note_text,
            source_row_index=source_row_index,
            task_instructions=task_instructions,
            output_contract=output_contract,
        )


def build_candidate_set_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build model-facing schema probe inputs without labels or candidates."""

    return {
        "note_text": record.note_text,
        "source_row_index": record.source_row_index,
        "task_instructions": [
            (
                "Find statements in the note that describe how often seizures or "
                "seizure-like events happen."
            ),
            "Each distinct statement is one candidate.",
            (
                "If the same frequency is repeated without adding new information, "
                "include only the clearest occurrence."
            ),
            "Do not decide which candidate is the best answer.",
            "Copy evidence_text exactly from the note. Preserve symbols such as ≤ and ≥.",
            "Use exactly one detail object for each candidate.",
            (
                "Do not parse counts, ranges, durations, or time periods. Copy the "
                "source phrase and leave parsed fields null."
            ),
            (
                "For an ordinary rate or interval, use frequency and fill only "
                "frequency.source_phrase."
            ),
            "Example: '2 seizures per month' -> frequency.source_phrase '2 seizures per month'.",
            (
                "Example: '≤ four seizures per week' -> frequency.source_phrase "
                "'≤ four seizures per week'."
            ),
            (
                "Example: 'seizures every 1 or 2 weeks' -> frequency.source_phrase "
                "'seizures every 1 or 2 weeks'."
            ),
            (
                "Example: 'multiple times in the past week' -> "
                "frequency.source_phrase 'multiple times in the past week', "
                "certainty uncertain, certainty_reason vague_count."
            ),
            (
                "High-recall unknown-frequency rule: when a statement gives only "
                "vague quantity words such as multiple, several, many, a few, "
                "handful, couple, most days, most weekdays, most shifts, or a few "
                "events, emit an unknown_frequency candidate."
            ),
            (
                "For vague quantity statements, do not use frequency_rate unless "
                "the phrase also contains a directly stated numeric count, numeric "
                "range, or exact interval."
            ),
            (
                "Example: 'several focal seizures last week' -> "
                "unknown_frequency.source_phrase 'several focal seizures last week'."
            ),
            (
                "Example: 'brief absences occurring on most weekdays' -> "
                "unknown_frequency.source_phrase 'brief absences occurring on most "
                "weekdays'."
            ),
            (
                "Example: 'a few events in the preceding month' -> "
                "unknown_frequency.source_phrase 'a few events in the preceding month'."
            ),
            (
                "Example: 'multiple seizures in past day' -> "
                "unknown_frequency.source_phrase 'multiple seizures in past day'."
            ),
            (
                "For seizure clusters, use cluster_details only when the note states "
                "how often clusters happen, how long a cluster lasts, how many "
                "clusters occurred, or how many events happen in a cluster."
            ),
            (
                "For cluster_details, copy the relevant phrase into "
                "cluster_frequency, events_per_cluster, cluster_count, or "
                "cluster_period only if that phrase is directly stated."
            ),
            (
                "Do not create a cluster candidate for generic wording such as "
                "variable clustering, occurring in clusters on stressful days, "
                "clustering around stress, clustering around sleep deprivation, or "
                "often in the afternoon."
            ),
            (
                "Do not create a cluster candidate unless at least one "
                "cluster_details field can be filled with a directly stated cluster "
                "cadence, duration, count, or events-per-cluster phrase."
            ),
            "For seizure-free wording, use seizure_free and fill only seizure_free.source_phrase.",
            (
                "For a dated or relative last seizure without a rate or seizure-free "
                "interval, use last_event_only and fill only last_event_only.source_phrase."
            ),
            (
                "Use unknown_frequency when the note discusses seizure frequency but "
                "does not give a usable value."
            ),
            "Use no_reference only when the note has no usable seizure-frequency statement.",
            "Leave fields null when the note does not state them.",
            "Return only candidate_draft_set.",
        ],
        "output_contract": {
            "schema_version": SCHEMA_VERSION,
            "model_outputs_only": ["candidate_draft_set"],
            "filled_by_code": [
                "candidate_id",
                "component_owner",
                "source_type",
                "source_artifact",
                "source_row_index",
                "evidence_span.start_char",
                "evidence_span.end_char",
                "source_ids",
                "clinical_or_policy",
            ],
            "candidate_kind_values": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "event_type_values": [
                "seizure",
                "seizure_like_event",
                "non_epileptic_event",
                "unclear_event",
            ],
            "temporality_values": ["current", "recent", "historical", "unclear"],
            "certainty_values": ["certain", "uncertain"],
            "certainty_reason_values": [
                "vague_count",
                "unclear_time_period",
                "approximate_wording",
                "conditional_statement",
                "other",
            ],
            "assertion_status_values": ["asserted", "negated", "uncertain", "conditional"],
            "detail_objects": {
                "frequency_rate": {
                    "field": "frequency",
                    "fields": [
                        "count",
                        "count_range",
                        "time_period",
                        "time_period_range",
                        "source_phrase",
                    ],
                    "model_fill": ["source_phrase"],
                    "filled_later_by_normalization": [
                        "count",
                        "count_range",
                        "time_period",
                        "time_period_range",
                    ],
                },
                "cluster_frequency": {
                    "field": "cluster_details",
                    "fields": [
                        "cluster_frequency",
                        "events_per_cluster",
                        "cluster_count",
                        "cluster_period",
                    ],
                    "model_fill": [
                        "cluster_frequency",
                        "events_per_cluster",
                        "cluster_count",
                        "cluster_period",
                    ],
                    "model_fill_rule": (
                        "copy source-near phrases only; do not calculate missing values"
                    ),
                },
                "seizure_free": {
                    "field": "seizure_free",
                    "fields": ["duration", "anchor", "source_phrase"],
                    "model_fill": ["source_phrase"],
                    "filled_later_by_normalization": ["duration", "anchor"],
                },
                "last_event_only": {
                    "field": "last_event_only",
                    "fields": ["event_timing", "event_count", "source_phrase"],
                    "model_fill": ["source_phrase"],
                    "filled_later_by_normalization": ["event_timing", "event_count"],
                },
                "unknown_frequency": {
                    "field": "unknown_frequency",
                    "fields": ["source_phrase"],
                },
                "no_reference": {
                    "field": "no_reference",
                    "fields": ["source_phrase"],
                },
            },
        },
    }


def prediction_to_candidate_draft_set(
    prediction: Any,
) -> tuple[CandidateDraftSet | None, list[str]]:
    """Validate a typed DSPy prediction into model-owned candidate drafts."""

    try:
        return CandidateDraftSet.model_validate(prediction.candidate_draft_set), []
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"candidate_draft_set_parse_or_validation_error: {exc}"]


def assemble_candidate_set(
    draft_set: CandidateDraftSet | None,
    *,
    record: GanFrequencyRecord,
) -> CandidateSet | None:
    """Fill ids, provenance, spans, and source ids deterministically."""

    if draft_set is None:
        return None
    candidates: list[ExtractedCandidate] = []
    assembly_issues: list[str] = []
    for index, draft in enumerate(draft_set.candidates, start=1):
        if _is_trigger_only_cluster_draft(draft):
            assembly_issues.append(
                f"candidate_draft:{index}: skipped_trigger_only_cluster_context"
            )
            continue
        candidates.append(_candidate_from_draft(index, draft, record=record))
    return CandidateSet(
        source_row_index=record.source_row_index,
        component_owner=PIPELINE_FAMILY,
        source_artifacts=[PROMPT_VERSION],
        row_context=extract_row_context(record.note_text),
        candidates=candidates,
        assembly_issues=assembly_issues,
    )


def _is_trigger_only_cluster_draft(draft: CandidateDraft) -> bool:
    if draft.candidate_kind != "cluster_frequency" or draft.cluster_details is None:
        return False
    details = draft.cluster_details
    if details.cluster_count or details.cluster_period or details.events_per_cluster:
        return False
    if not details.cluster_frequency:
        return True
    text = details.cluster_frequency.strip().lower()
    return not bool(
        re.search(
            r"\b(every|per|daily|weekly|monthly|yearly|annually|fortnightly|"
            r"once|twice)\b|\d",
            text,
        )
    )


def _candidate_from_draft(
    index: int,
    draft: CandidateDraft,
    *,
    record: GanFrequencyRecord,
) -> ExtractedCandidate:
    draft = _repair_draft_source_text(draft, note_text=record.note_text)
    span = locate_evidence(record.note_text, draft.evidence_text)
    start_char, end_char = span if span else (None, None)
    source_id = (
        f"note:{record.source_row_index}:span:{start_char}-{end_char}"
        if span
        else f"note:{record.source_row_index}:span:unresolved:{index}"
    )
    return ExtractedCandidate(
        candidate_id=f"llm:{record.source_row_index}:{index}",
        component_owner=PIPELINE_FAMILY,
        source_type="llm_candidate",
        source_artifact=PROMPT_VERSION,
        source_row_index=record.source_row_index,
        candidate_kind=draft.candidate_kind,
        event_type=draft.event_type,
        event_subtype=draft.event_subtype,
        frequency=_source_near_frequency(draft.frequency),
        seizure_free=_source_near_seizure_free(draft.seizure_free),
        last_event_only=_source_near_last_event_only(draft.last_event_only),
        cluster_details=draft.cluster_details,
        unknown_frequency=draft.unknown_frequency,
        no_reference=draft.no_reference,
        temporality=draft.temporality,
        certainty=draft.certainty,
        certainty_reason=draft.certainty_reason,
        assertion_status=draft.assertion_status,
        evidence_span=EvidenceSpan(
            text=draft.evidence_text,
            start_char=start_char,
            end_char=end_char,
        ),
        source_ids=[source_id],
        extraction_issues=[],
        clinical_or_policy="clinical",
    )


def _repair_draft_source_text(
    draft: CandidateDraft,
    *,
    note_text: str,
) -> CandidateDraft:
    updates: dict[str, Any] = {
        "evidence_text": repair_evidence_text_if_source_exact(
            draft.evidence_text,
            note_text,
        )
    }
    if draft.frequency is not None:
        updates["frequency"] = draft.frequency.model_copy(
            update={
                "source_phrase": repair_evidence_text_if_source_exact(
                    draft.frequency.source_phrase,
                    note_text,
                )
            }
        )
    if draft.seizure_free is not None:
        updates["seizure_free"] = draft.seizure_free.model_copy(
            update={
                "source_phrase": repair_evidence_text_if_source_exact(
                    draft.seizure_free.source_phrase,
                    note_text,
                )
            }
        )
    if draft.last_event_only is not None:
        updates["last_event_only"] = draft.last_event_only.model_copy(
            update={
                "source_phrase": repair_evidence_text_if_source_exact(
                    draft.last_event_only.source_phrase,
                    note_text,
                )
            }
        )
    if draft.unknown_frequency is not None:
        updates["unknown_frequency"] = draft.unknown_frequency.model_copy(
            update={
                "source_phrase": repair_evidence_text_if_source_exact(
                    draft.unknown_frequency.source_phrase,
                    note_text,
                )
            }
        )
    if draft.no_reference is not None:
        updates["no_reference"] = draft.no_reference.model_copy(
            update={
                "source_phrase": repair_evidence_text_if_source_exact(
                    draft.no_reference.source_phrase,
                    note_text,
                )
            }
        )
    return draft.model_copy(update=updates)


def _source_near_frequency(details: FrequencyDetails | None) -> FrequencyDetails | None:
    if details is None:
        return None
    return FrequencyDetails(source_phrase=details.source_phrase)


def _source_near_seizure_free(
    details: SeizureFreeDetails | None,
) -> SeizureFreeDetails | None:
    if details is None:
        return None
    return SeizureFreeDetails(source_phrase=details.source_phrase)


def _source_near_last_event_only(
    details: LastEventOnlyDetails | None,
) -> LastEventOnlyDetails | None:
    if details is None:
        return None
    return LastEventOnlyDetails(source_phrase=details.source_phrase)


def validate_candidate_set(
    candidate_set: CandidateSet | None,
    *,
    record: GanFrequencyRecord,
) -> list[str]:
    """Run schema-probe validations that do not use gold labels."""

    if candidate_set is None:
        return []
    errors: list[str] = []
    if candidate_set.source_row_index != record.source_row_index:
        errors.append("candidate_set: source_row_index mismatch")
    ids = [candidate.candidate_id for candidate in candidate_set.candidates]
    if len(ids) != len(set(ids)):
        errors.append("candidate_set: duplicate_candidate_ids")
    for candidate in candidate_set.candidates:
        if not evidence_is_substring(record.note_text, candidate.evidence_span.text):
            errors.append(f"candidate:{candidate.candidate_id}: evidence_not_exact")
        source_phrase = _candidate_source_phrase(candidate)
        if source_phrase and not evidence_is_substring(record.note_text, source_phrase):
            errors.append(f"candidate:{candidate.candidate_id}: source_phrase_not_exact")
    return errors


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
    """Run the schema probe over a split surface."""

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
    program = DspyCandidateSetExtractor()
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
        typed_input = build_candidate_set_inputs(record)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_input)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        draft_set, parse_errors = (
            prediction_to_candidate_draft_set(prediction)
            if prediction is not None
            else (None, ["not_run"])
        )
        candidate_set = assemble_candidate_set(draft_set, record=record)
        validation_errors = validate_candidate_set(candidate_set, record=record)
        row = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_name": PROMPT_VERSION,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "typed_input": typed_input,
            "raw_output": _raw_output_from_candidate_set(candidate_set),
            "call_error": call_error,
            "parse_errors": [*parse_errors, *validation_errors],
            "candidate_draft_set": draft_set.model_dump() if draft_set else None,
            "candidate_set": candidate_set.model_dump() if candidate_set else None,
            "schema_probe": _schema_probe(candidate_set, validation_errors),
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
    """Summarize schema fit without scoring."""

    candidate_sets = [row for row in rows if row.get("candidate_set")]
    candidates = [
        candidate
        for row in candidate_sets
        for candidate in (row.get("candidate_set") or {}).get("candidates", [])
    ]
    kind_counts = Counter(str(candidate.get("candidate_kind")) for candidate in candidates)
    detail_failures = sum(
        int(not (row.get("schema_probe") or {}).get("kind_detail_fit"))
        for row in candidate_sets
    )
    evidence_error_rows = sum(
        any("evidence_not_exact" in str(error) for error in row.get("parse_errors") or [])
        for row in rows
    )
    source_phrase_error_rows = sum(
        any("source_phrase_not_exact" in str(error) for error in row.get("parse_errors") or [])
        for row in rows
    )
    return {
        "examples": len(rows),
        "candidate_sets": len(candidate_sets),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_or_validation_failures": sum(
            bool(row.get("parse_errors")) for row in rows
        ),
        "total_candidates": len(candidates),
        "candidate_kind_counts": dict(sorted(kind_counts.items())),
        "detail_failure_rows": detail_failures,
        "evidence_error_rows": evidence_error_rows,
        "source_phrase_error_rows": source_phrase_error_rows,
        "rows_with_no_candidates": sum(
            not ((row.get("candidate_set") or {}).get("candidates")) for row in rows
        ),
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
    """Write a compact Markdown schema-probe report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 ExtractedCandidate Schema Probe",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline: `{PIPELINE_FAMILY}`",
        f"- Prompt/schema version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        "- Claim language: schema-fit probe only; no scoring and no final labels.",
        "",
        "## Summary",
        "",
        f"- Candidate sets: {summary.get('candidate_sets', 0)}/{summary.get('examples', 0)}",
        f"- Total candidates: {summary.get('total_candidates', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/validation failure rows: {summary.get('parse_or_validation_failures', 0)}",
        f"- Detail failure rows: {summary.get('detail_failure_rows', 0)}",
        f"- Evidence error rows: {summary.get('evidence_error_rows', 0)}",
        f"- Source phrase error rows: {summary.get('source_phrase_error_rows', 0)}",
        f"- Rows with no candidates: {summary.get('rows_with_no_candidates', 0)}",
        "",
        "## Candidate Kinds",
        "",
    ]
    for kind, count in (summary.get("candidate_kind_counts") or {}).items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Row Notes", ""])
    lines.extend(_row_note_lines(rows))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _schema_probe(
    candidate_set: CandidateSet | None,
    validation_errors: Sequence[str],
) -> dict[str, Any]:
    if candidate_set is None:
        return {"kind_detail_fit": False, "candidate_count": 0}
    return {
        "kind_detail_fit": not any(
            "candidate_kind must have" in error for error in validation_errors
        ),
        "candidate_count": len(candidate_set.candidates),
        "candidate_kinds": [candidate.candidate_kind for candidate in candidate_set.candidates],
    }


def _candidate_source_phrase(candidate: ExtractedCandidate) -> str | None:
    return candidate_source_phrase(candidate)


def _raw_output_from_candidate_set(candidate_set: CandidateSet | None) -> str:
    if candidate_set is None:
        return ""
    return json.dumps(candidate_set.model_dump(), sort_keys=True)


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
