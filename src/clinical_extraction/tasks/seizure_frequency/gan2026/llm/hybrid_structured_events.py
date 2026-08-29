"""Hybrid structured-events Gan 2026 seizure-frequency extraction.

Architecture: LLM extracts structured events from raw note text (open-text → schema);
the same deterministic normalize/project/render/score stages used by the candidate-set
hybrid then process the output.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.core.local_structured_output import (
    FormatOnlyJsonRetry,
    assess_structured_output,
    build_format_only_retry_input,
    raw_output_from_adapter_error,
    validate_format_retry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_selected_answer_payload,
    repair_structured_extraction_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_structured_temporal,
    prompt_llm_extract_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_monthly_diary import (
    monthly_diary_label_from_events as _monthly_diary_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    breakthrough_label_from_events as _breakthrough_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    dated_sequence_label_from_events as _dated_sequence_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    elapsed_since_anchor_label_from_events as _elapsed_since_anchor_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    last_event_well_since_label_from_events as _last_event_well_since_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    non_epileptic_label_from_events as _non_epileptic_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    post_change_burst_label_from_events as _post_change_burst_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    residual_jerk_label_from_events as _residual_jerk_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    typical_recurring_rate_over_ytd_from_events as _typical_recurring_rate_over_ytd_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    usual_interval_label_from_events as _usual_interval_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object as _extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    has_blocking_parse_issue as _has_blocking_parse_issue,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    has_repair_note as _has_repair_note,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_and_rules_extract import (
    GAN_LLM_AND_RULES_EXTRACT,
    build_llm_and_rules_extract_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
    build_llm_extract_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    build_llm_extract_raw_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.post_stack_fix_flags import (
    post_stack_fix_flags,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence.codebook_encode import (
    repair_codebook_label_with_evidence,
)

_clinic_date = llm_structured_temporal.clinic_date
_clinic_month_year = llm_structured_temporal.clinic_month_year
_duration_from_event_dates = llm_structured_temporal.duration_from_event_dates
_duration_from_events = llm_structured_temporal.duration_from_events
_duration_from_text = llm_structured_temporal.duration_from_text
_elapsed_months = llm_structured_temporal.elapsed_months
_elapsed_months_from_nearest_event_date = (
    llm_structured_temporal.elapsed_months_from_nearest_event_date
)
_elapsed_months_from_nearest_event_date_precise = (
    llm_structured_temporal.elapsed_months_from_nearest_event_date_precise
)
_event_month_year = llm_structured_temporal.event_month_year
_event_text = llm_structured_temporal.event_text
_month_number = llm_structured_temporal.month_number
_nearest_event_date = llm_structured_temporal.nearest_event_date
_nearest_event_month_year = llm_structured_temporal.nearest_event_month_year
_small_number_words_to_digits = llm_structured_temporal.small_number_words_to_digits

GAN_LLM_EXTRACT_RAW = "gan_llm_extract_raw"
GAN_LLM_WITH_RULES = GAN_LLM_EXTRACT_RAW
LLM_EXTRACT_RAW_AUTHORED_KEYS = prompt_llm_extract_raw.LLM_EXTRACT_RAW_AUTHORED_KEYS
LLM_WITH_RULES_AUTHORED_KEYS = LLM_EXTRACT_RAW_AUTHORED_KEYS
PROMPT_VERSION = GAN_LLM_EXTRACT_RAW
ROW_TRACE_SCHEMA_VERSION = "gan2026.row_trace.v1"
PROMPT_VERSION_ALIASES = {
    "gan_llm_with_rules": GAN_LLM_EXTRACT_RAW,
    "gan_llm_extract_label_forms": GAN_LLM_EXTRACT,
    "gan_llm_pre_post_label_forms": GAN_LLM_AND_RULES_EXTRACT,
}
_SUPPORTED_PROMPT_VERSIONS = frozenset(
    {
        GAN_LLM_EXTRACT_RAW,
        GAN_LLM_AND_RULES_EXTRACT,
        GAN_LLM_EXTRACT,
        *PROMPT_VERSION_ALIASES,
    }
)


PROMPT_POLICY_TAXONOMY: list[dict[str, str]] = [
    {
        "policy_id": "se_v0.schema.events_plus_selection",
        "controlled_variable": "events_plus_selection_schema_policy",
        "portability": "general",
        "status": "active",
        "description": (
            "Prompt requires a two-part JSON object: a list of slim clinical events "
            "and a separate selection block with final_label and rationale."
        ),
    },
    {
        "policy_id": "se_v0.event.source_near_raw_value",
        "controlled_variable": "source_near_raw_value_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Events use raw_value for the source-near expression rather than fully "
            "normalized labels at the extraction stage."
        ),
    },
    {
        "policy_id": "se_v0.event.kind_taxonomy",
        "controlled_variable": "event_kind_taxonomy_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Events must be typed as one of frequency_rate, cluster_frequency, seizure_free, "
            "last_event_only, unknown_frequency, or no_reference."
        ),
    },
    {
        "policy_id": "se_v0.selection.aggregation_strategy",
        "controlled_variable": "aggregation_strategy_policy",
        "portability": "gan2026_specific",
        "status": "active",
        "description": (
            "Selection block includes an explicit aggregation_strategy describing how "
            "the final label was derived from events."
        ),
    },
    {
        "policy_id": "se_v0.evidence.exact_substring",
        "controlled_variable": "prompt_exact_evidence_substring_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": "Every evidence value must be an exact substring from the note.",
    },
]
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_hybrid_structured_events_validation_gpt41mini_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_hybrid_structured_events_validation_gpt41mini_2026-06-01.md"
)
StructuredRepairMode = Literal[
    "strict_json_raw_model",
    "json_dialect_only",
    "raw_model",
    "llm_encode",
    "gan_rules_encode",
    "llm_select",
    "llm_select_after_codebook",
    "llm_select_only",
    "custom",
]
# Sealed artifacts and older CLI flags may still emit these strings.
_STRUCTURED_REPAIR_MODE_ALIASES: dict[str, StructuredRepairMode] = {
    "selected_evidence_derivation": "llm_encode",
    "hybrid_full_stack": "llm_select",
    "encode": "llm_encode",
    "revise": "llm_select",
    "llm_revise": "llm_select",
    "select": "llm_select",
    "gan_rules_encode": "gan_rules_encode",
}


class StructuredEventRecord(BaseModel):
    """Slim source-near event fact extracted by the LLM."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    raw_value: str | None = None
    applies_to: str | None = None
    time_window: str | None = None
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "historical", "hypothetical", "unknown"]
    evidence: str
    notes: str | None = None


class StructuredSelectionRecord(BaseModel):
    """LLM clinical selection over the source-near events."""

    model_config = ConfigDict(extra="forbid")

    selected_event_ids: list[str]
    final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    final_label: str | None = None
    evidence: str
    confidence: Literal["low", "medium", "high"]
    rationale: str


class StructuredExtractionRecord(BaseModel):
    """Full structured extraction returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    events: list[StructuredEventRecord]
    selection: StructuredSelectionRecord


class NormalizedEventRecord(BaseModel):
    """Deterministic Gan normalization attached after LLM event extraction."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    normalized_label: str | None
    semantic_kind: str | None
    monthly_frequency: float | None
    yearly_bounds: tuple[float, float] | None
    repair_applied: bool
    validation_errors: list[str]


DEFAULT_SEMANTIC_FAMILY_ORDER: tuple[str, ...] = (
    "usual_interval",
    "typical_over_ytd",
    "breakthrough",
    "non_epileptic",
    "residual_jerk",
    "post_change_burst",
    "last_event_well_since",
    "dated_sequence",
    "elapsed_anchor",
    "monthly_diary",
)

_SEMANTIC_FAMILY_FLAG: dict[str, str] = {
    "usual_interval": "usual_interval_repair",
    "typical_over_ytd": "typical_over_ytd_repair",
    "breakthrough": "breakthrough_repair",
    "non_epileptic": "non_epileptic_repair",
    "residual_jerk": "residual_jerk_repair",
    "post_change_burst": "post_change_burst_repair",
    "last_event_well_since": "last_event_well_since_repair",
    "dated_sequence": "dated_sequence_repair",
    "elapsed_anchor": "elapsed_anchor_repair",
    "monthly_diary": "monthly_diary_repair",
}


def adjacent_semantic_family_orders(
    order: Sequence[str] = DEFAULT_SEMANTIC_FAMILY_ORDER,
) -> tuple[tuple[tuple[str, str], tuple[str, ...]], ...]:
    """Return each adjacent swap of the clinical post-stack families."""

    swaps: list[tuple[tuple[str, str], tuple[str, ...]]] = []
    for index in range(len(order) - 1):
        swapped = list(order)
        swapped[index], swapped[index + 1] = swapped[index + 1], swapped[index]
        swaps.append(((order[index], order[index + 1]), tuple(swapped)))
    return tuple(swaps)


@dataclass(frozen=True)
class StructuredRepairConfig:
    """Controls deterministic repair families applied after LLM-only structured-events output."""

    repair_mode: StructuredRepairMode | None = None
    json_dialect_repair: bool = True
    basic_label_repair: bool = True
    selected_evidence_repair: bool = True
    codebook_label_repair: bool = False
    monthly_diary_repair: bool = True
    usual_interval_repair: bool = True
    typical_over_ytd_repair: bool = True
    breakthrough_repair: bool = True
    non_epileptic_repair: bool = True
    residual_jerk_repair: bool = False
    post_change_burst_repair: bool = True
    last_event_well_since_repair: bool = True
    dated_sequence_repair: bool = True
    elapsed_anchor_repair: bool = False
    semantic_family_order: tuple[str, ...] = DEFAULT_SEMANTIC_FAMILY_ORDER

    @classmethod
    def for_mode(cls, mode: StructuredRepairMode | str) -> StructuredRepairConfig:
        """Build one of the named repair modes used in run metadata and reports.

        Legacy names ``selected_evidence_derivation``, ``hybrid_full_stack``,
        and ``llm_revise`` still load as aliases for ``encode`` and ``select``.
        """

        mode = cast(StructuredRepairMode, _STRUCTURED_REPAIR_MODE_ALIASES.get(mode, mode))
        if mode == "strict_json_raw_model":
            return cls(
                repair_mode=mode,
                json_dialect_repair=False,
                basic_label_repair=False,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                typical_over_ytd_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                last_event_well_since_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "json_dialect_only":
            return cls(
                repair_mode=mode,
                json_dialect_repair=True,
                basic_label_repair=False,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                typical_over_ytd_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                last_event_well_since_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "raw_model":
            return cls(
                repair_mode=mode,
                basic_label_repair=False,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                typical_over_ytd_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                last_event_well_since_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "llm_encode":
            return cls(
                repair_mode=mode,
                basic_label_repair=True,
                selected_evidence_repair=True,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                typical_over_ytd_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                last_event_well_since_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "gan_rules_encode":
            return cls(
                repair_mode=mode,
                basic_label_repair=False,
                selected_evidence_repair=False,
                codebook_label_repair=True,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                typical_over_ytd_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                last_event_well_since_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "llm_select":
            return cls(repair_mode=mode)
        if mode == "llm_select_after_codebook":
            return cls(
                repair_mode=mode,
                basic_label_repair=False,
                selected_evidence_repair=False,
                codebook_label_repair=True,
            )
        if mode == "llm_select_only":
            return cls(
                repair_mode=mode,
                basic_label_repair=False,
                selected_evidence_repair=False,
            )
        return cls(repair_mode=mode)  # type: ignore[arg-type]

    @property
    def resolved_repair_mode(self) -> StructuredRepairMode:
        """Return the named mode when flags match one; otherwise mark it custom."""

        flags = self._flags()
        for mode in (
            "strict_json_raw_model",
            "json_dialect_only",
            "raw_model",
            "llm_encode",
            "gan_rules_encode",
            "llm_select",
            "llm_select_after_codebook",
            "llm_select_only",
        ):
            named = StructuredRepairConfig.for_mode(mode)
            if (
                flags == named._flags()
                and self.semantic_family_order == named.semantic_family_order
            ):
                return mode
        return "custom"

    def encode_enabled(self) -> bool:
        """True when this mode may write a designed-form label."""

        return (
            self.selected_evidence_repair
            or self.basic_label_repair
            or self.codebook_label_repair
        )

    def select_enabled(self) -> bool:
        """True when a named select family may change the facts."""

        return any(
            getattr(self, flag_name) for flag_name in _SEMANTIC_FAMILY_FLAG.values()
        )

    def _flags(self) -> dict[str, bool]:
        return {
            "json_dialect_repair": self.json_dialect_repair,
            "basic_label_repair": self.basic_label_repair,
            "selected_evidence_repair": self.selected_evidence_repair,
            "codebook_label_repair": self.codebook_label_repair,
            "monthly_diary_repair": self.monthly_diary_repair,
            "usual_interval_repair": self.usual_interval_repair,
            "typical_over_ytd_repair": self.typical_over_ytd_repair,
            "breakthrough_repair": self.breakthrough_repair,
            "non_epileptic_repair": self.non_epileptic_repair,
            "residual_jerk_repair": self.residual_jerk_repair,
            "post_change_burst_repair": self.post_change_burst_repair,
            "last_event_well_since_repair": self.last_event_well_since_repair,
            "dated_sequence_repair": self.dated_sequence_repair,
            "elapsed_anchor_repair": self.elapsed_anchor_repair,
        }


class Gan2026StructuredExtractorSignature(dspy.Signature):
    """Extract source-near seizure-frequency events and choose a final answer.

    Return exactly one JSON object with two keys: events and selection.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output schemas."
    )
    structured_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object with events and selection. Events are source-near facts; "
            "selection chooses the clinically appropriate answer from those events."
        )
    )


class DspyStructuredExtractor(dspy.Module):
    """DSPy structured extractor with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026StructuredExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        """Render the initial model request without making a model call."""

        return ChatAdapter().format(
            Gan2026StructuredExtractorSignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )


def normalize_prompt_version(prompt_version: str) -> str:
    """Map a sealed or live prompt identity onto the current name."""

    return PROMPT_VERSION_ALIASES.get(prompt_version, prompt_version)


def build_prompt_input(
    record: GanFrequencyRecord,
    *,
    prompt_version: str | None = None,
) -> str:
    """Dispatch to the paper extract prompt or the both-extract variant."""

    selected_prompt_version = normalize_prompt_version(prompt_version or PROMPT_VERSION)
    if selected_prompt_version not in _SUPPORTED_PROMPT_VERSIONS - set(
        PROMPT_VERSION_ALIASES
    ):
        raise ValueError(
            f"unsupported prompt version {selected_prompt_version!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)}"
        )

    if selected_prompt_version == GAN_LLM_AND_RULES_EXTRACT:
        return build_llm_and_rules_extract_prompt_input(record)
    if selected_prompt_version == GAN_LLM_EXTRACT:
        return build_llm_extract_prompt_input(record)
    return build_llm_extract_raw_prompt_input(record)


def parse_structured_json(
    raw_output: str,
    *,
    note_text: str | None = None,
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[StructuredExtractionRecord | None, list[NormalizedEventRecord], list[str]]:
    extraction, normalized_events, errors, _ = parse_structured_json_with_trace(
        raw_output,
        note_text=note_text,
        repair_config=repair_config,
    )
    return extraction, normalized_events, errors


def parse_structured_json_with_trace(
    raw_output: str,
    *,
    note_text: str | None = None,
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[
    StructuredExtractionRecord | None,
    list[NormalizedEventRecord],
    list[str],
    dict[str, Any],
]:
    """Parse structured output and retain the model boundary and repair stages."""

    repair_config = repair_config or StructuredRepairConfig()
    try:
        raw_payload, errors = parse_json_payload_with_schema_repair(
            _extract_json_object(raw_output),
            python_literal_dialect_repair=repair_config.json_dialect_repair,
        )
        structurally_repaired, structural_notes, _ = repair_selected_answer_payload(raw_payload)
        payload = _filter_structured_payload(
            repair_structured_extraction_payload(structurally_repaired)
        )
        payload, quarantine_notes, _ = repair_selected_answer_payload(
            payload,
            event_validator=StructuredEventRecord.model_validate,
        )
        errors.extend(structural_notes)
        errors.extend(quarantine_notes)
    except json.JSONDecodeError as exc:
        errors = [f"invalid_json: {exc.msg}"]
        return None, [], errors, _hybrid_row_trace(
            model_extraction=None,
            schema_payload_changed=False,
            format_events=errors,
            resolved_label=None,
            final_label=None,
            semantic_events=[],
        )
    schema_payload_changed = payload != raw_payload
    format_events = list(errors)

    try:
        extraction = StructuredExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        errors.append(f"schema_validation_error: {exc.errors()[0]['msg']}")
        return None, [], errors, _hybrid_row_trace(
            model_extraction=None,
            schema_payload_changed=schema_payload_changed,
            format_events=errors,
            resolved_label=None,
            final_label=None,
            semantic_events=[],
        )
    model_extraction = extraction
    hops: list[dict[str, Any]] = []
    evidence = extraction.selection.evidence
    operands = list(extraction.selection.selected_event_ids)
    evidence_exact = (
        evidence_is_substring(note_text, evidence) if note_text and evidence else None
    )
    hops.append(
        _answer_hop(
            stage_id="gan.model.selection",
            owner="model",
            effect_class="extract",
            before=None,
            after=extraction.selection.final_label,
            evidence=evidence,
            evidence_exact=evidence_exact,
            operands=operands,
            cell_id="llm_extract",
        )
    )

    if not repair_config.encode_enabled() and not repair_config.select_enabled():
        return extraction, [], errors, _hybrid_row_trace(
            model_extraction=model_extraction,
            schema_payload_changed=schema_payload_changed,
            format_events=format_events,
            resolved_label=None,
            final_label=extraction.selection.final_label,
            semantic_events=[],
            answer_states=hops,
        )

    normalized_events = [
        _normalize_event(event, note_text=note_text) for event in extraction.events
    ]
    model_label = extraction.selection.final_label
    resolved_label = model_label
    if repair_config.encode_enabled():
        resolved_label = _resolve_final_label(extraction, normalized_events)
        if resolved_label != model_label:
            hops.append(
                _answer_hop(
                    stage_id="gan.encode.resolve_label",
                    owner="replay",
                    effect_class="encode",
                    before=model_label,
                    after=resolved_label,
                    evidence=evidence,
                    evidence_exact=evidence_exact,
                    operands=operands,
                    cell_id="llm_encode",
                )
            )
    if resolved_label is None:
        errors.append("unscorable_final_label: no selected event normalized to a Gan label")
        return extraction, normalized_events, errors, _hybrid_row_trace(
            model_extraction=model_extraction,
            schema_payload_changed=schema_payload_changed,
            format_events=format_events,
            resolved_label=None,
            final_label=None,
            semantic_events=[],
            answer_states=hops,
        )

    repaired_label = resolved_label
    if repair_config.basic_label_repair and not repair_config.selected_evidence_repair:
        next_label = repair_prediction_label(repaired_label)
        repaired_label = _record_label_repair(
            errors,
            hops,
            stage_id="gan.render.basic_label",
            effect_class="encode",
            cell_id="llm_encode",
            before=repaired_label,
            after=next_label,
            evidence=evidence,
            evidence_exact=evidence_exact,
            operands=operands,
        )
    if repair_config.selected_evidence_repair:
        next_label = repair_prediction_label_with_evidence(
            repaired_label,
            extraction.selection.evidence,
            context_text=note_text,
        )
        repaired_label = _record_label_repair(
            errors,
            hops,
            stage_id="gan.render.selected_evidence",
            effect_class="encode",
            cell_id="llm_encode",
            before=repaired_label,
            after=next_label,
            evidence=evidence,
            evidence_exact=evidence_exact,
            operands=operands,
        )
    if repair_config.codebook_label_repair:
        selected_ids = set(extraction.selection.selected_event_ids)
        selected_kinds = [
            str(event.kind) for event in extraction.events if event.event_id in selected_ids
        ]
        codebook_trace = repair_codebook_label_with_evidence(
            repaired_label,
            extraction.selection.evidence,
            selected_event_kinds=selected_kinds,
            context_text=note_text,
        )
        for event in codebook_trace.events:
            repaired_label = _record_label_repair(
                errors,
                hops,
                stage_id=event.rule_id,
                effect_class="encode",
                cell_id="llm_encode",
                before=repaired_label,
                after=event.after,
                evidence=evidence,
                evidence_exact=evidence_exact,
                operands=operands,
            )
    repaired_label = _apply_semantic_families(
        extraction,
        repaired_label,
        note_text=note_text or "",
        repair_config=repair_config,
        errors=errors,
        hops=hops,
        evidence=evidence,
        evidence_exact=evidence_exact,
        operands=operands,
    )
    try:
        label_to_frequency_record(repaired_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")
    if repaired_label != extraction.selection.final_label:
        extraction = extraction.model_copy(
            update={
                "selection": extraction.selection.model_copy(update={"final_label": repaired_label})
            }
        )
    semantic_events = [
        error for error in errors if str(error).startswith("final_label_repaired:")
    ]
    return extraction, normalized_events, errors, _hybrid_row_trace(
        model_extraction=model_extraction,
        schema_payload_changed=schema_payload_changed,
        format_events=format_events,
        resolved_label=resolved_label,
        final_label=repaired_label,
        semantic_events=semantic_events,
        answer_states=hops,
    )


def _apply_semantic_families(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str,
    repair_config: StructuredRepairConfig,
    errors: list[str],
    hops: list[dict[str, Any]],
    evidence: str | None,
    evidence_exact: bool | None,
    operands: Sequence[str],
) -> str:
    """Apply clinical post-stack families in the configured order."""

    for family_id in repair_config.semantic_family_order:
        flag_name = _SEMANTIC_FAMILY_FLAG.get(family_id)
        if flag_name is None:
            raise ValueError(f"unknown semantic family: {family_id}")
        if not getattr(repair_config, flag_name):
            continue
        proposed, vetoed = _semantic_family_proposal(
            family_id,
            extraction,
            repaired_label,
            note_text=note_text,
        )
        next_label = proposed or repaired_label
        repaired_label = _record_label_repair(
            errors,
            hops,
            stage_id=f"gan.select.{family_id}",
            effect_class="select",
            cell_id="llm_select",
            before=repaired_label,
            after=next_label,
            evidence=evidence,
            evidence_exact=evidence_exact,
            operands=operands,
            vetoed=vetoed,
        )
    return repaired_label


def _semantic_family_proposal(
    family_id: str,
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str,
) -> tuple[str | None, str | None]:
    if family_id == "usual_interval":
        return _usual_interval_label_from_events(extraction, repaired_label), None
    if family_id == "typical_over_ytd":
        return _typical_recurring_rate_over_ytd_from_events(extraction, repaired_label), None
    if family_id == "breakthrough":
        return _breakthrough_label_from_events(extraction, repaired_label), None
    if family_id == "non_epileptic":
        return _non_epileptic_label_from_events(extraction, repaired_label), None
    if family_id == "residual_jerk":
        return _residual_jerk_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        ), None
    if family_id == "post_change_burst":
        return _post_change_burst_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        ), None
    if family_id == "last_event_well_since":
        return _last_event_well_since_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        ), None
    if family_id == "dated_sequence":
        return _dated_sequence_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        ), None
    if family_id == "elapsed_anchor":
        elapsed_window_label = _elapsed_since_anchor_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        )
        if elapsed_window_label and _should_preserve_sustained_selected_seizure_free(
            extraction,
            repaired_label,
            elapsed_window_label,
        ):
            return None, elapsed_window_label
        return elapsed_window_label, None
    if family_id == "monthly_diary":
        monthly_diary_label = _monthly_diary_label_from_events(
            extraction,
            note_text=note_text,
        )
        if monthly_diary_label and _should_preserve_label_from_monthly_diary(
            repaired_label,
            extraction=extraction,
        ):
            return None, monthly_diary_label
        return monthly_diary_label, None
    raise ValueError(f"unknown semantic family: {family_id}")


def _answer_hop(
    *,
    stage_id: str,
    owner: str,
    effect_class: str,
    before: str | None,
    after: str | None,
    evidence: str | None,
    evidence_exact: bool | None,
    operands: Sequence[str],
    cell_id: str,
    vetoed: str | None = None,
) -> dict[str, Any]:
    from clinical_extraction.paper.cells import CELL_ORDER, normalize_cell_id

    resolved = normalize_cell_id(cell_id)
    return {
        "stage_id": stage_id,
        "owner": owner,
        "effect_class": effect_class,
        "before": before,
        "after": after,
        "evidence": evidence,
        "evidence_exact": evidence_exact,
        "operands": list(operands),
        "vetoed": vetoed,
        "cell_id": resolved,
        "cell_order": CELL_ORDER[resolved],
        "changed": before != after,
    }


def _record_label_repair(
    errors: list[str],
    hops: list[dict[str, Any]],
    *,
    stage_id: str,
    effect_class: str,
    cell_id: str,
    before: str,
    after: str,
    evidence: str | None,
    evidence_exact: bool | None,
    operands: Sequence[str],
    vetoed: str | None = None,
) -> str:
    hops.append(
        _answer_hop(
            stage_id=stage_id,
            owner="replay",
            effect_class=effect_class,
            before=before,
            after=after,
            evidence=evidence,
            evidence_exact=evidence_exact,
            operands=operands,
            cell_id=cell_id,
            vetoed=vetoed,
        )
    )
    return _replace_repaired_label(errors, before, after)


def _hybrid_row_trace(
    *,
    model_extraction: StructuredExtractionRecord | None,
    schema_payload_changed: bool,
    format_events: Sequence[str],
    resolved_label: str | None,
    final_label: str | None,
    semantic_events: Sequence[str],
    answer_states: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    selection = model_extraction.selection if model_extraction else None
    return {
        "schema_version": ROW_TRACE_SCHEMA_VERSION,
        "method": "llm_with_rules",
        "model_prediction": {
            "raw_output_field": "raw_output",
            "record": model_extraction.model_dump() if model_extraction else None,
        },
        "format_repair": {
            "schema_payload_changed": schema_payload_changed,
            "events": list(format_events),
        },
        "deterministic_selection": {
            "selected_event_ids": list(selection.selected_event_ids) if selection else [],
            "model_final_label": selection.final_label if selection else None,
            "resolved_label": resolved_label,
            "normalized_events_field": "normalized_events",
        },
        "deterministic_semantic": {
            "rule_category": "seizure_frequency",
            "before_label": resolved_label,
            "after_label": final_label,
            "events": list(semantic_events),
        },
        "answer_states": list(answer_states or []),
        "evidence_validation": None,
        "scoring": None,
    }


def _filter_structured_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of structured-events validation."""

    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    event_fields = set(StructuredEventRecord.model_fields)
    selection_fields = set(StructuredSelectionRecord.model_fields)
    events = repaired.get("events")
    if isinstance(events, list):
        repaired["events"] = [
            {key: value for key, value in event.items() if key in event_fields}
            if isinstance(event, dict)
            else event
            for event in events
        ]
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired["selection"] = {
            key: value for key, value in selection.items() if key in selection_fields
        }
    return repaired


def _replace_repaired_label(errors: list[str], old_label: str, new_label: str) -> str:
    if new_label != old_label:
        errors.append(f"final_label_repaired: {old_label!r} -> {new_label!r}")
    return new_label


def _should_preserve_label_from_monthly_diary(
    repaired_label: str,
    *,
    extraction: StructuredExtractionRecord | None = None,
) -> bool:
    """Block diary aggregation from overwriting selected seizure-free or week-scale rates.

    Portability: ``seizure_frequency``. Applied after elapsed-anchor so a
    sustained dated freedom (four or more months, or any year-scale window)
    is not replaced by a later month log. Vague ``seizure free for multiple *``
    and shorter free tails remain eligible for diary override. Current-month
    seizure-free selections also stay eligible.
    """
    label = (repaired_label or "").strip().lower()
    if not label:
        return False
    if label.startswith("seizure free"):
        if post_stack_fix_flags().vague_seizure_free_diary:
            if re.search(r"\bseizure free for multiple\b", label):
                return False
            duration = re.fullmatch(
                r"seizure free for (?P<count>\d+) (?P<unit>day|week|month|year)",
                label,
            )
            if duration:
                count = int(duration.group("count"))
                unit = duration.group("unit")
                if unit == "year" or (unit == "month" and count >= 4):
                    return True
                return False
        # Basic repair may inflate "this month" to multiple year; inspect selection.
        if extraction is not None:
            selection_text = " ".join(
                str(part or "")
                for part in (
                    extraction.selection.final_label,
                    extraction.selection.evidence,
                    extraction.selection.rationale,
                )
            ).lower()
            if re.search(
                r"seizure[- ]free for (?:this|the current|current|1) month\b",
                selection_text,
            ):
                return False
        return True
    if not re.search(r"\bper\s+(?:\d+(?:\s*to\s+\d+)?\s+)?(?:day|week)\b", label):
        return False
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True


def _should_preserve_sustained_selected_seizure_free(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    elapsed_window_label: str,
) -> bool:
    if extraction.selection.final_kind != "seizure_free":
        return False
    if not repaired_label.startswith("seizure free"):
        return False
    match = re.fullmatch(r"1 per (?P<months>\d+) month", elapsed_window_label)
    if not match or int(match.group("months")) < 4:
        return False
    selected_event_ids = set(extraction.selection.selected_event_ids)
    selected_events = [event for event in extraction.events if event.event_id in selected_event_ids]
    if not selected_events or any(event.kind != "seizure_free" for event in selected_events):
        return False
    support_text = " ".join(
        str(value or "")
        for event in selected_events
        for value in (event.raw_value, event.time_window, event.evidence, event.notes)
    )
    support_text = (
        f"{support_text} {extraction.selection.evidence} {extraction.selection.rationale}"
    )
    support_text = support_text.lower()
    return bool(
        re.search(
            r"\b(?:absence of events|no recorded|no further|no unprovoked|"
            r"seizure[- ]free|remission|no events|none since)\b",
            support_text,
        )
    )


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
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility facade; prediction order lives in orchestration.llm_with_rules."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm_with_rules import (
        run_split as canonical_run_split,
    )

    return canonical_run_split(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        reuse_raw_outputs=reuse_raw_outputs,
        reuse_source=reuse_source,
        escalation_reason=escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
        repair_config=repair_config,
    )


def _legacy_run_split(
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
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
        repair_mode_metadata,
    )

    repair_config = repair_config or StructuredRepairConfig()
    reuse_raw_outputs = reuse_raw_outputs or {}
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
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    metadata["repair_mode"] = repair_config.resolved_repair_mode
    metadata["repair_mode_metadata"] = repair_mode_metadata(repair_config.resolved_repair_mode)
    metadata["repair_config"] = asdict(repair_config)
    program = DspyStructuredExtractor()
    format_retry_program = FormatOnlyJsonRetry()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    rows: list[dict[str, Any]] = []
    for record in records:
        prompt_input_json = build_prompt_input(record)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        adapter_repair_notes: list[str] = []
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.structured_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"
                recovered = raw_output_from_adapter_error(call_error)
                if recovered:
                    raw_output = recovered
                    call_error = None
                    adapter_repair_notes.append(
                        "adapter_output_field_repaired: structured_json_missing"
                    )

        extraction, normalized_events, parse_errors, row_trace = (
            parse_structured_json_with_trace(
                raw_output,
                note_text=record.note_text,
                repair_config=repair_config,
            )
            if raw_output
            else (
                None,
                [],
                ["not_run"],
                _hybrid_row_trace(
                    model_extraction=None,
                    schema_payload_changed=False,
                    format_events=["not_run"],
                    resolved_label=None,
                    final_label=None,
                    semantic_events=[],
                ),
            )
        )
        initial_parse_errors = list(parse_errors)
        assessment = assess_structured_output(
            raw_output, initial_parse_errors, call_error=call_error
        )
        format_retry_output = ""
        format_retry_notes: list[str] = []
        if mode == "live" and model.startswith("ollama_chat/") and assessment.retry_eligible:
            try:
                retry_prediction = format_retry_program(
                    retry_input_json=build_format_only_retry_input(
                        malformed_output=raw_output,
                        schema=StructuredExtractionRecord.model_json_schema(),
                    )
                )
                format_retry_output = str(retry_prediction.repaired_json)
                retry_validation = validate_format_retry(
                    raw_output, initial_parse_errors, format_retry_output
                )
                retry_extraction, retry_events, retry_errors, retry_row_trace = (
                    parse_structured_json_with_trace(
                    format_retry_output,
                    note_text=record.note_text,
                    repair_config=repair_config,
                )
                )
                format_retry_notes = list(retry_validation.notes)
                if retry_validation.accepted and retry_extraction is not None:
                    extraction = retry_extraction
                    normalized_events = retry_events
                    row_trace = retry_row_trace
                    row_trace["model_prediction"]["raw_output_field"] = "format_retry_output"
                    parse_errors = [*retry_errors, *format_retry_notes]
                elif retry_validation.accepted:
                    format_retry_notes = ["format_retry_rejected: schema_validation"]
                    parse_errors = [*initial_parse_errors, *format_retry_notes]
                else:
                    parse_errors = [*initial_parse_errors, *format_retry_notes]
            except Exception as exc:  # pragma: no cover - live provider behavior.
                format_retry_notes = [
                    f"format_retry_rejected: provider_error:{type(exc).__name__}"
                ]
                parse_errors = [*initial_parse_errors, *format_retry_notes]
        parse_errors = [*adapter_repair_notes, *parse_errors]
        evidence_valid = (
            evidence_is_substring(record.note_text, extraction.selection.evidence)
            if extraction and extraction.selection.evidence
            else False
        )
        comparison = _compare_to_gold(record, extraction) if extraction else None
        row_trace["format_repair"]["events"] = [
            *adapter_repair_notes,
            *row_trace["format_repair"]["events"],
            *format_retry_notes,
        ]
        row_trace["evidence_validation"] = {
            "evidence": extraction.selection.evidence if extraction else "",
            "exact_substring": evidence_valid,
        }
        row_trace["scoring"] = comparison
        row: dict[str, Any] = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "prompt_version": PROMPT_VERSION,
            "prompt_input_json": prompt_input_json,
            "raw_output": raw_output,
            "reused_raw_output": reused_raw_output,
            "call_error": call_error,
            "initial_parse_errors": initial_parse_errors,
            "parse_errors": parse_errors,
            "structured_output_failure_codes": list(assessment.failure_codes),
            "format_retry_output": format_retry_output,
            "format_retry_notes": format_retry_notes,
            "structured_record": extraction.model_dump() if extraction else None,
            "normalized_events": [event.model_dump() for event in normalized_events],
            "evidence_valid": evidence_valid,
            "row_trace": row_trace,
            "reference": {
                "gold_label": record.gold_label,
                "gold_normalized_label": record.gold_normalized_label,
                "gold_label_kind": str(record.gold_label_kind),
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "row_ok": record.row_ok,
            },
            "comparison": comparison,
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
    structured_rows = [row for row in rows if row.get("structured_record")]
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    reused_raw_outputs = sum(bool(row.get("reused_raw_output")) for row in rows)
    parse_failures = sum(_has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    initial_parse_failures = sum(
        _has_blocking_parse_issue(row.get("initial_parse_errors")) for row in rows
    )
    json_dialect_repairs = sum(_has_json_dialect_repair(row.get("parse_errors")) for row in rows)
    repair_notes = sum(_has_repair_note(row.get("parse_errors")) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    evidence_valid = sum(bool(row.get("evidence_valid")) for row in rows)
    final_labels = Counter(
        final_label
        for row in rows
        if row.get("structured_record")
        for final_label in [row["structured_record"]["selection"].get("final_label")]
        if isinstance(final_label, str)
    )
    predicted_candidate_count = sum(_row_candidate_count(row) for row in rows)
    return {
        "examples": len(rows),
        "structured_records": len(structured_rows),
        "predicted_candidate_count": predicted_candidate_count,
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "initial_parse_or_validation_failures": initial_parse_failures,
        "format_retries_applied": sum(
            "format_retry_applied" in (row.get("format_retry_notes") or []) for row in rows
        ),
        "format_retries_rejected": sum(
            any(
                str(note).startswith("format_retry_rejected:")
                for note in (row.get("format_retry_notes") or [])
            )
            for row in rows
        ),
        "json_dialect_repairs": json_dialect_repairs,
        "repair_notes": repair_notes,
        "evidence_valid": evidence_valid,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
    }


def _row_candidate_count(row: Mapping[str, Any]) -> int:
    encoded = row.get("encoded_events")
    if encoded is not None:
        return len(encoded)
    structured = row.get("structured_record")
    if isinstance(structured, Mapping):
        return len(structured.get("events") or [])
    return len(row.get("normalized_events") or [])


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        write_jsonl_rows,
    )

    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.reports.llm_structured_events_report import (  # noqa: E501
        write_report as write_structured_report,
    )

    write_structured_report(rows, metadata, path, jsonl_path=jsonl_path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior JSONL artifact."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.replay_io import (
        load_raw_outputs_by_source_index,
    )

    return load_raw_outputs_by_source_index(path)


def _normalize_event(
    event: StructuredEventRecord,
    *,
    note_text: str | None = None,
) -> NormalizedEventRecord:
    raw_label = _event_raw_label(event)
    if raw_label is None:
        return NormalizedEventRecord(
            event_id=event.event_id,
            normalized_label=None,
            semantic_kind=None,
            monthly_frequency=None,
            yearly_bounds=None,
            repair_applied=False,
            validation_errors=["no_normalizable_event_label"],
        )
    repaired = repair_prediction_label_with_evidence(
        raw_label,
        event.evidence,
        context_text=note_text,
    )
    try:
        frequency = label_to_frequency_record(repaired)
    except ValueError as exc:
        return NormalizedEventRecord(
            event_id=event.event_id,
            normalized_label=repaired,
            semantic_kind=None,
            monthly_frequency=None,
            yearly_bounds=None,
            repair_applied=repaired != raw_label,
            validation_errors=[str(exc)],
        )
    return NormalizedEventRecord(
        event_id=event.event_id,
        normalized_label=frequency.normalized_label,
        semantic_kind=str(frequency.kind),
        monthly_frequency=frequency.monthly_frequency,
        yearly_bounds=frequency.yearly_bounds,
        repair_applied=repaired != raw_label,
        validation_errors=[],
    )


def _event_raw_label(event: StructuredEventRecord) -> str | None:
    if event.kind == "no_reference":
        return "no seizure frequency reference"
    if event.kind in {"unknown_frequency", "last_event_only"}:
        return "unknown"
    if event.kind == "seizure_free" and event.raw_value:
        return event.raw_value
    if event.kind in {"frequency_rate", "cluster_frequency"} and event.raw_value:
        return event.raw_value
    return None


def _resolve_final_label(
    extraction: StructuredExtractionRecord,
    normalized_events: Sequence[NormalizedEventRecord],
) -> str | None:
    if extraction.selection.final_label:
        return extraction.selection.final_label
    normalized_by_id = {event.event_id: event for event in normalized_events}
    for event_id in extraction.selection.selected_event_ids:
        normalized = normalized_by_id.get(event_id)
        if normalized and normalized.normalized_label and not normalized.validation_errors:
            return normalized.normalized_label
    return _default_label_for_final_kind(extraction.selection.final_kind)


def _default_label_for_final_kind(final_kind: str) -> str | None:
    if final_kind == "unknown":
        return "unknown"
    if final_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _compare_to_gold(
    record: GanFrequencyRecord,
    extraction: StructuredExtractionRecord,
) -> dict[str, Any]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
        map_pragmatic,
        map_purist,
    )

    if extraction.selection.final_label is None:
        return {}
    try:
        predicted_record = label_to_frequency_record(extraction.selection.final_label)
    except ValueError:
        return {}
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "predicted_monthly_frequency": predicted_record.monthly_frequency,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


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
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": metadata["summary"]["call_failures"],
        "parse_or_validation_failures": metadata["summary"]["parse_or_validation_failures"],
        "purist_accuracy_so_far": metadata["summary"]["purist_accuracy"],
        "pragmatic_accuracy_so_far": metadata["summary"]["pragmatic_accuracy"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _has_json_dialect_repair(errors: Any) -> bool:
    return any(str(error).startswith("json_dialect_repaired:") for error in errors or [])


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
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
        build_run_metadata,
    )

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
    )
