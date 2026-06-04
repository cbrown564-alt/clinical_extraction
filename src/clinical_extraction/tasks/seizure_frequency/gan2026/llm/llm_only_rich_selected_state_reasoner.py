"""Rich selected-state surface for RQ3 schema experiments."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "gan2026_llm_only_rich_selected_state_reasoner_v0"
PIPELINE_FAMILY = "llm_only_rich_selected_state_reasoner"
RICH_SELECTED_STATE_SCHEMA_VERSION = "rich_selected_state_v0"
DEFAULT_FIVE_ROW_JSONL_PATH = Path(
    "experiments/gan2026_rich_selected_state_five_letter_2026-06-04.jsonl"
)
DEFAULT_FIVE_ROW_REPORT_PATH = Path(
    "experiments/gan2026_rich_selected_state_five_letter_2026-06-04.md"
)
DEFAULT_FIVE_ROW_SOURCE_IDS = (10, 280, 3356, 10618, 2748)


class RichRateDetails(BaseModel):
    """Selected rate details copied from the evidence."""

    model_config = ConfigDict(extra="forbid")

    count_low: float | None = Field(default=None, description="Lowest stated event count.")
    count_high: float | None = Field(default=None, description="Highest stated event count.")
    count_is_upper_bound: bool = Field(
        default=False,
        description="Whether the count is stated as an upper limit.",
    )
    count_is_multiple: bool = Field(
        default=False,
        description="Whether the evidence says multiple events without an exact count.",
    )
    time_count_low: float | None = Field(
        default=None,
        description="Lowest stated time count for a rate.",
    )
    time_count_high: float | None = Field(
        default=None,
        description="Highest stated time count for a rate.",
    )
    time_unit: Literal["day", "week", "month", "year"] | None = Field(
        default=None,
        description="Time unit for the selected rate.",
    )
    rate_time_basis_known: bool = Field(
        default=False,
        description="Whether the evidence gives enough time basis for a rate.",
    )
    rate_text: str = Field(default="", description="Short rate phrase copied from the evidence.")


class RichClusterDetails(BaseModel):
    """Selected cluster details copied from the evidence."""

    model_config = ConfigDict(extra="forbid")

    has_cluster_pattern: bool = Field(
        default=False,
        description="Whether the evidence describes events grouped in clusters.",
    )
    cluster_cadence_known: bool = Field(
        default=False,
        description="Whether the evidence says how often clusters occur.",
    )
    cluster_cadence_text: str = Field(
        default="",
        description="Phrase describing how often clusters occur.",
    )
    seizures_per_cluster_low: float | None = Field(
        default=None,
        description="Lowest stated events within each cluster.",
    )
    seizures_per_cluster_high: float | None = Field(
        default=None,
        description="Highest stated events within each cluster.",
    )
    cluster_uncertainty: str = Field(
        default="",
        description="Short reason cluster details are incomplete or unclear.",
    )


class RichSeizureFreeBoundary(BaseModel):
    """Selected seizure-free boundary details."""

    model_config = ConfigDict(extra="forbid")

    has_no_event_claim: bool = Field(
        default=False,
        description="Whether the evidence says there were no events.",
    )
    duration_count: float | None = Field(
        default=None,
        description="Stated seizure-free duration count.",
    )
    duration_unit: Literal["day", "week", "month", "year"] | None = Field(
        default=None,
        description="Time unit for seizure-free duration.",
    )
    applies_to_all_seizure_types: bool = Field(
        default=False,
        description="Whether the no-event claim applies to all seizure types.",
    )
    has_recent_events_or_conditions: bool = Field(
        default=False,
        description=(
            "Whether the note also describes recent events or conditions that block "
            "a simple seizure-free answer."
        ),
    )
    boundary_note: str = Field(
        default="",
        description="Short explanation of the seizure-free boundary.",
    )


class RichSelectedState(BaseModel):
    """One selected clinical state with explicit boundary fields."""

    model_config = ConfigDict(extra="forbid")

    state_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ] = Field(description="Broad type of the selected state.")
    selected_evidence: str = Field(
        description="Exact note substring supporting the selected state."
    )
    raw_source_phrase: str = Field(
        description="Short phrase copied from selected_evidence."
    )
    currentness: Literal["current", "recent", "historical", "future", "conditional", "unclear"] = (
        Field(description="Whether the selected state is current, old, planned, or conditional.")
    )
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"] = Field(
        description="Whether the note asserts, negates, hypothesizes, or is unsure."
    )
    applies_to: str = Field(
        default="",
        description="Seizure type or event type described by the selected state.",
    )
    rate: RichRateDetails = Field(default_factory=RichRateDetails)
    cluster: RichClusterDetails = Field(default_factory=RichClusterDetails)
    seizure_free_boundary: RichSeizureFreeBoundary = Field(
        default_factory=RichSeizureFreeBoundary
    )
    conditionality_note: str = Field(
        default="",
        description="Condition that must hold for the state to apply, if any.",
    )
    ambiguity_flags: list[str] = Field(
        default_factory=list,
        description="Short notes about ambiguity or missing details.",
    )
    competing_state_summary: str = Field(
        default="",
        description="Short note about competing evidence or states.",
    )
    selection_reason: str = Field(
        default="",
        description="Brief reason this state was selected.",
    )
    raw_model_label_hint: str = Field(
        default="",
        description="Optional answer phrase suggested by the model before deterministic rendering.",
    )


class RichSelectedStateExtractionRecord(BaseModel):
    """Full rich selected-state extraction."""

    model_config = ConfigDict(extra="forbid")

    selected_state: RichSelectedState


class Gan2026RichSelectedStateReasonerSignature(dspy.Signature):
    """Select one typed seizure-frequency state from a clinical note."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Plain-language instructions for selecting and typing one state."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Output fields and allowed values."
    )
    selected_state: RichSelectedState = dspy.OutputField(
        desc="One selected clinical state with exact evidence and boundary fields."
    )


class DspyRichSelectedStateReasoner(dspy.Module):
    """DSPy typed-output program for the rich selected-state lane."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026RichSelectedStateReasonerSignature)

    def forward(
        self,
        *,
        note_text: str,
        task_instructions: list[str],
        output_contract: dict[str, Any],
    ) -> dspy.Prediction:
        return self.predict(
            note_text=note_text,
            task_instructions=task_instructions,
            output_contract=output_contract,
        )


def build_rich_selected_state_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build model-facing inputs without labels, candidates, or graph hints."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Read the full clinical note.",
            "Select one seizure-frequency state that should be carried forward.",
            "Copy selected_evidence as an exact non-empty substring from the note.",
            "Use raw_source_phrase for a short phrase copied from that evidence.",
            (
                "Keep ordinary frequency, seizure freedom, unclear frequency, no "
                "frequency reference, and unresolved multiple-event states distinct."
            ),
            (
                "Record currentness, conditional statements, cluster burden, rate time "
                "basis, seizure-free boundary, ambiguity, and competing states when present."
            ),
            (
                "If events occur only under a condition, describe the condition and do "
                "not turn that into seizure freedom."
            ),
            (
                "If the evidence gives events within clusters but not how often clusters "
                "occur, keep the cluster burden and mark the cadence as unknown."
            ),
            (
                "If the evidence says multiple events in a day, week, month, or year, "
                "preserve the multiple wording instead of forcing a numeric count."
            ),
            "Return exactly one selected_state object.",
        ],
        "output_contract": {
            "top_level_outputs": ["selected_state"],
            "selected_state_fields": [
                "state_kind",
                "selected_evidence",
                "raw_source_phrase",
                "currentness",
                "assertion_status",
                "applies_to",
                "rate",
                "cluster",
                "seizure_free_boundary",
                "conditionality_note",
                "ambiguity_flags",
                "competing_state_summary",
                "selection_reason",
                "raw_model_label_hint",
            ],
            "field_descriptions": {
                "state_kind": "Broad type of selected state.",
                "selected_evidence": "Exact note substring supporting the selected state.",
                "raw_source_phrase": "Short phrase copied from selected_evidence.",
                "currentness": "Whether the state is current, old, planned, or conditional.",
                "assertion_status": "Whether the note asserts or is unsure about the state.",
                "applies_to": "Seizure or event type described by the selected state.",
                "rate": "Count and time basis for a selected rate.",
                "cluster": "Cluster burden and how often clusters occur.",
                "seizure_free_boundary": "Details needed before calling a row seizure-free.",
                "conditionality_note": "Condition that must hold for the state to apply.",
                "ambiguity_flags": "Short notes about ambiguity or missing details.",
                "competing_state_summary": "Short note about competing states.",
                "selection_reason": "Brief reason this state was selected.",
                "raw_model_label_hint": "Optional answer phrase before deterministic rendering.",
            },
            "state_kind_values": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "currentness_values": [
                "current",
                "recent",
                "historical",
                "future",
                "conditional",
                "unclear",
            ],
            "evidence_copy_rule": "selected_evidence must be an exact note substring.",
        },
    }


def prediction_to_extraction(
    prediction: Any,
    *,
    note_text: str | None = None,
) -> tuple[RichSelectedStateExtractionRecord | None, list[str]]:
    """Validate a typed prediction into a rich selected-state record."""

    try:
        extraction = RichSelectedStateExtractionRecord.model_validate(
            {"selected_state": prediction.selected_state}
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"rich_selected_state_parse_or_validation_error: {exc}"]
    if note_text is not None:
        state = extraction.selected_state
        extraction = extraction.model_copy(
            update={
                "selected_state": state.model_copy(
                    update={
                        "selected_evidence": repair_evidence_text_if_source_exact(
                            state.selected_evidence,
                            note_text,
                        ),
                        "raw_source_phrase": repair_evidence_text_if_source_exact(
                            state.raw_source_phrase,
                            note_text,
                        ),
                    }
                )
            }
        )
    return extraction, []


def validate_rich_selected_state(
    extraction: RichSelectedStateExtractionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Validate evidence, trace, and boundary consistency."""

    if extraction is None:
        return []
    errors: list[str] = []
    state = extraction.selected_state
    evidence_valid = True
    if not state.selected_evidence.strip():
        errors.append("evidence: missing selected evidence")
        evidence_valid = False
    if note_text is not None and not evidence_is_substring(note_text, state.selected_evidence):
        errors.append("evidence: invalid selected evidence")
        evidence_valid = False
    if (
        evidence_valid
        and state.raw_source_phrase
        and state.raw_source_phrase not in state.selected_evidence
    ):
        errors.append("selected_state_trace: raw_source_phrase not in selected_evidence")
    if state.state_kind == "no_reference" and (
        _has_rate_value(state.rate)
        or state.cluster.has_cluster_pattern
        or state.seizure_free_boundary.has_no_event_claim
    ):
        errors.append("boundary: no_reference state contains clinical frequency details")
    if (
        state.state_kind == "seizure_free"
        and state.seizure_free_boundary.has_recent_events_or_conditions
    ):
        errors.append("boundary: seizure_free state has recent events or conditions")
    if state.currentness == "conditional" and not state.conditionality_note.strip():
        errors.append("boundary: conditional state missing conditionality_note")
    return errors


def deterministic_project_selected_state(
    extraction: RichSelectedStateExtractionRecord | None,
) -> str | None:
    """Render a rich selected state into Gan-compatible syntax when safe."""

    if extraction is None:
        return None
    state = extraction.selected_state
    if state.currentness in {"historical", "future"} and state.state_kind != "no_reference":
        return "unknown"
    if state.state_kind == "no_reference":
        return "no seizure frequency reference"
    if state.state_kind == "seizure_free":
        return _render_seizure_free(state)
    if state.state_kind == "unresolved_multiple":
        return _render_unresolved_multiple(state) or _parseable_hint(state)
    if state.state_kind == "unknown":
        return _render_unknown(state)
    if state.state_kind == "frequency":
        return _render_frequency(state) or _render_unknown(state) or _parseable_hint(state)
    return None


def _render_frequency(state: RichSelectedState) -> str | None:
    rate = state.rate
    if _conditionality_blocks_frequency(state):
        return _render_unknown(state)
    if _rate_boundary_blocks_frequency(state):
        return _render_unknown(state)
    if _vague_increase_without_count(state):
        return "unknown"
    if cluster_label := _render_cluster_frequency(state):
        return cluster_label
    if _cluster_quiescence_blocks_bare_rate(state):
        return _render_unknown(state)
    if (
        state.cluster.has_cluster_pattern
        and not state.cluster.cluster_cadence_known
        and (
            state.cluster.seizures_per_cluster_low is not None
            or state.cluster.seizures_per_cluster_high is not None
        )
    ):
        return _render_unknown(state)
    if rate.count_is_multiple and rate.time_unit:
        return f"multiple per {rate.time_unit}"
    if (rate.count_low is not None or rate.count_high is not None) and rate.time_unit:
        count = _format_range(rate.count_low, rate.count_high)
        period = _format_period(rate.time_count_low, rate.time_count_high, rate.time_unit)
        return f"{count} per {period}"
    return None


def _render_cluster_frequency(state: RichSelectedState) -> str | None:
    cluster = state.cluster
    if not cluster.has_cluster_pattern:
        return None

    cadence_period = _cluster_cadence_period(state)
    if cadence_period is None:
        return None

    cluster_count = _cluster_cadence_count(state)
    burden = _cluster_burden(cluster, default_multiple=_cluster_burden_is_unknown(state))
    if burden is None or burden == "1":
        return f"{cluster_count} per {cadence_period}"
    return f"{cluster_count} cluster per {cadence_period}, {burden} per cluster"


def _render_unresolved_multiple(state: RichSelectedState) -> str | None:
    if state.rate.count_is_multiple and state.rate.time_unit:
        return f"multiple per {state.rate.time_unit}"
    return None


def _render_unknown(state: RichSelectedState) -> str:
    cluster = state.cluster
    if cluster.has_cluster_pattern and (
        cluster.seizures_per_cluster_low is not None
        or cluster.seizures_per_cluster_high is not None
    ):
        burden = _format_range(
            cluster.seizures_per_cluster_low,
            cluster.seizures_per_cluster_high,
            multiple_text="multiple",
        )
        return f"unknown, {burden} per cluster"
    if state.rate.count_is_multiple and not state.rate.rate_time_basis_known:
        return "unknown"
    return "unknown"


def _conditionality_blocks_frequency(state: RichSelectedState) -> bool:
    note = state.conditionality_note.strip().lower()
    if not note:
        return False
    if state.currentness == "conditional":
        return True
    blocking_patterns = (
        r"\bonly\s+(?:after|when|if|with|during)\b",
        r"\bexclusively\s+(?:after|when|if|with|during)\b",
        r"\bno events?\b.*\b(?:when|if|with)\b",
    )
    return any(re.search(pattern, note) for pattern in blocking_patterns)


def _vague_increase_without_count(state: RichSelectedState) -> bool:
    text = " ".join(
        [
            state.rate.rate_text,
            state.raw_source_phrase,
            " ".join(state.ambiguity_flags),
            state.raw_model_label_hint,
        ]
    ).lower()
    if not re.search(r"\b(more frequent|increased|increase|worse|worsening)\b", text):
        return False
    return bool(
        state.rate.count_is_multiple
        and any(
            "exact" in flag.lower() and "not stated" in flag.lower()
            for flag in state.ambiguity_flags
        )
    )


def _rate_boundary_blocks_frequency(state: RichSelectedState) -> bool:
    text = " ".join(
        [
            state.selected_evidence,
            state.raw_source_phrase,
            state.rate.rate_text,
            state.competing_state_summary,
            " ".join(state.ambiguity_flags),
        ]
    ).lower()
    blockers = (
        "single breakthrough",
        "exact frequency outside",
        "indirect report",
        "second-hand",
        "exact dates and counts",
        "prior to last event",
        "since starting",
    )
    return any(blocker in text for blocker in blockers)


def _cluster_quiescence_blocks_bare_rate(state: RichSelectedState) -> bool:
    if not state.cluster.has_cluster_pattern or state.cluster.cluster_cadence_known:
        return False
    if (
        state.cluster.seizures_per_cluster_low is not None
        or state.cluster.seizures_per_cluster_high is not None
    ):
        return False
    text = f"{state.selected_evidence} {state.cluster.cluster_cadence_text}".lower()
    return "followed by quiescence" in text or "weeks without events" in text


def _cluster_cadence_period(state: RichSelectedState) -> str | None:
    cluster = state.cluster
    rate = state.rate
    if cluster.cluster_cadence_known:
        if period := _period_from_cluster_text(cluster.cluster_cadence_text):
            return period
        if rate.rate_time_basis_known and rate.time_unit:
            return _format_period(rate.time_count_low, rate.time_count_high, rate.time_unit)

    if _rate_window_describes_single_cluster(state):
        return _format_period(rate.time_count_low, rate.time_count_high, rate.time_unit)

    boundary = state.seizure_free_boundary
    boundary_text = f"{boundary.boundary_note} {state.selected_evidence}".lower()
    if (
        boundary.duration_count is not None
        and boundary.duration_unit
        and re.search(r"\bfollowed by\b.*\b(cluster|clustering|burst)", boundary_text)
    ):
        return _format_period(boundary.duration_count, None, boundary.duration_unit)
    return None


def _cluster_cadence_count(state: RichSelectedState) -> str:
    rate = state.rate
    cluster = state.cluster
    burden_low = cluster.seizures_per_cluster_low
    burden_high = cluster.seizures_per_cluster_high
    if (
        cluster.cluster_cadence_known
        and rate.count_low is not None
        and not _range_matches(rate.count_low, rate.count_high, burden_low, burden_high)
    ):
        return _format_range(rate.count_low, rate.count_high)
    return "1"


def _cluster_burden(cluster: RichClusterDetails, *, default_multiple: bool) -> str | None:
    if (
        cluster.seizures_per_cluster_low is not None
        or cluster.seizures_per_cluster_high is not None
    ):
        return _format_range(
            cluster.seizures_per_cluster_low,
            cluster.seizures_per_cluster_high,
            multiple_text="multiple",
        )
    if default_multiple:
        return "multiple"
    return None


def _cluster_burden_is_unknown(state: RichSelectedState) -> bool:
    text = " ".join(
        [
            state.cluster.cluster_uncertainty,
            " ".join(state.ambiguity_flags),
            state.raw_model_label_hint,
        ]
    ).lower()
    return bool(re.search(r"\b(number|count|episodes|events).*\b(not|unclear|unknown)", text))


def _rate_window_describes_single_cluster(state: RichSelectedState) -> bool:
    rate = state.rate
    cadence_text = state.cluster.cluster_cadence_text.lower()
    if "when they occur" in cadence_text or "on days when" in state.selected_evidence.lower():
        return False
    if (
        not rate.rate_time_basis_known
        or rate.time_unit is None
        or (
            state.cluster.seizures_per_cluster_low is None
            and state.cluster.seizures_per_cluster_high is None
        )
        or not _range_matches(
            rate.count_low,
            rate.count_high,
            state.cluster.seizures_per_cluster_low,
            state.cluster.seizures_per_cluster_high,
        )
    ):
        return False
    text = f"{rate.rate_text} {state.selected_evidence}".lower()
    return bool(re.search(r"\b(over|past|preceding|previous|within)\b", text))


def _range_matches(
    left_low: float | None,
    left_high: float | None,
    right_low: float | None,
    right_high: float | None,
) -> bool:
    return left_low == right_low and (left_high or left_low) == (right_high or right_low)


def _period_from_cluster_text(text: str) -> str | None:
    normalized = text.lower().replace("-", " ")
    if re.search(r"\b(weekly|each week|every week|once a week|once weekly)\b", normalized):
        return "week"
    if re.search(r"\b(monthly|each month|every month|once a month|once monthly)\b", normalized):
        return "month"
    match = re.search(
        r"\b(?:every|once every|roughly every|approximately every)\s+"
        r"(\d+(?:\s+to\s+\d+)?)\s+(day|week|month|year)s?\b",
        normalized,
    )
    if match:
        return f"{match.group(1)} {match.group(2)}"
    word_range = re.search(
        r"\b(?:every|once every|roughly every|approximately every)\s+"
        r"(four|five|six|seven|eight)(?:\s+to\s+(four|five|six|seven|eight))?\s+"
        r"(day|week|month|year)s?\b",
        normalized,
    )
    if word_range:
        low = _word_number(word_range.group(1))
        high_word = word_range.group(2)
        high = _word_number(high_word) if high_word else low
        count = str(low) if low == high else f"{low} to {high}"
        return f"{count} {word_range.group(3)}"
    return None


def _word_number(word: str | None) -> int:
    numbers = {
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
    }
    return numbers[str(word)]


def _render_seizure_free(state: RichSelectedState) -> str:
    boundary = state.seizure_free_boundary
    if not boundary.applies_to_all_seizure_types or boundary.has_recent_events_or_conditions:
        return "unknown"
    if boundary.duration_count is not None and boundary.duration_unit:
        duration_count = _format_number(boundary.duration_count)
        return f"seizure free for {duration_count} {boundary.duration_unit}"
    return "seizure free for multiple month"


def _parseable_hint(state: RichSelectedState) -> str | None:
    hint = state.raw_model_label_hint.strip().lower()
    if not hint:
        return None
    try:
        return label_to_frequency_record(hint).normalized_label
    except ValueError:
        return None


def _has_rate_value(rate: RichRateDetails) -> bool:
    return any(
        value is not None
        for value in (
            rate.count_low,
            rate.count_high,
            rate.time_count_low,
            rate.time_count_high,
            rate.time_unit,
        )
    ) or rate.count_is_multiple


def _format_period(
    low: float | None,
    high: float | None,
    unit: Literal["day", "week", "month", "year"],
) -> str:
    if unit == "day" and low is not None and (high is None or high == low) and low % 7 == 0:
        week_count = low / 7
        return _format_period(week_count, None, "week")
    if low is None or ((high is None or high == low) and low == 1):
        return unit
    return f"{_format_range(low, high)} {unit}"


def _format_range(
    low: float | None,
    high: float | None,
    *,
    multiple_text: str | None = None,
) -> str:
    if low is None and high is None:
        return multiple_text or ""
    if low is None:
        return _format_number(high)
    if high is None or high == low:
        return _format_number(low)
    return f"{_format_number(low)} to {_format_number(high)}"


def _format_number(value: float | None) -> str:
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def metadata() -> dict[str, str]:
    """Research-facing metadata for this experimental surface."""

    return {
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
        "typed_output_schema_version": RICH_SELECTED_STATE_SCHEMA_VERSION,
    }


def run_records(
    records: list[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or render the rich selected-state focused experiment."""

    lm = None
    adapter = None
    program = DspyRichSelectedStateReasoner()
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
        typed_input = build_rich_selected_state_inputs(record)
        prediction = None
        call_error = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_input)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        extraction, parse_errors = (
            prediction_to_extraction(prediction, note_text=record.note_text)
            if prediction is not None
            else (None, ["not_run"])
        )
        validation_errors = validate_rich_selected_state(
            extraction,
            note_text=record.note_text,
        )
        deterministic_label = deterministic_project_selected_state(extraction)
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_family": PIPELINE_FAMILY,
                "prompt_version": PROMPT_VERSION,
                "typed_output_schema_version": RICH_SELECTED_STATE_SCHEMA_VERSION,
                "typed_input": typed_input,
                "call_error": call_error,
                "parse_errors": [*parse_errors, *validation_errors],
                "structured_record": extraction.model_dump() if extraction else None,
                "deterministic_projected_label": deterministic_label,
                "deterministic_projected_label_parseable": _label_parseable(
                    deterministic_label
                ),
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "row_ok": record.row_ok,
                },
            }
        )

    metadata = {
        **metadata_base(
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            api_base=api_base,
        ),
        "summary": summarize_rows(rows),
    }
    return rows, metadata


def metadata_base(
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None,
) -> dict[str, Any]:
    """Return research-facing metadata for a run."""

    return {
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
        "typed_output_schema_version": RICH_SELECTED_STATE_SCHEMA_VERSION,
        "split": split,
        "split_manifest": split_manifest,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "api_base": api_base,
        "claim_boundary": "validation-development rich selected-state component study",
    }


def summarize_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize rich selected-state rows."""

    errors = Counter(
        str(error).split(":", maxsplit=1)[0]
        for row in rows
        for error in row.get("parse_errors") or []
    )
    return {
        "rows": len(rows),
        "structured_records": sum(bool(row.get("structured_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "rows_with_errors": sum(bool(row.get("parse_errors")) for row in rows),
        "deterministic_projected": sum(
            bool(row.get("deterministic_projected_label")) for row in rows
        ),
        "deterministic_projected_parseable": sum(
            bool(row.get("deterministic_projected_label_parseable")) for row in rows
        ),
        "error_families": dict(sorted(errors.items())),
    }


def write_jsonl(rows: list[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: list[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a focused rich selected-state report."""

    summary = metadata.get("summary") or summarize_rows(rows)
    lines = [
        "# Gan 2026 Rich Selected-State Five-Letter Run",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Architecture: `{PIPELINE_FAMILY}`",
        f"- Prompt version: `{PROMPT_VERSION}`",
        f"- Schema version: `{RICH_SELECTED_STATE_SCHEMA_VERSION}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        "- Claim boundary: validation-development component study, not F1.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Structured records: {summary.get('structured_records', 0)}",
        f"- Rows with parse/boundary errors: {summary.get('rows_with_errors', 0)}",
        f"- Deterministic projected labels: {summary.get('deterministic_projected', 0)}",
        (
            "- Deterministic projected parseable labels: "
            f"{summary.get('deterministic_projected_parseable', 0)}"
        ),
        f"- Error families: `{summary.get('error_families', {})}`",
        "",
        "## Rows",
        "",
        "| Row | Gold | State kind | Evidence exact | Boundary errors | Projected label |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        state = ((row.get("structured_record") or {}).get("selected_state") or {})
        errors = row.get("parse_errors") or []
        evidence_exact = "unknown"
        if state.get("selected_evidence"):
            evidence_exact = "valid" if not any(
                str(error).startswith("evidence:") for error in errors
            ) else "invalid"
        lines.append(
            f"| {row['source_row_index']} | "
            f"`{_md((row.get('reference') or {}).get('gold_normalized_label'))}` | "
            f"`{state.get('state_kind', '')}` | `{evidence_exact}` | "
            f"`{'; '.join(errors)}` | "
            f"`{_md(row.get('deterministic_projected_label'))}` |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _label_parseable(label: str | None) -> bool:
    if not label:
        return False
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def main() -> None:
    """CLI for prompt-only or live five-row runs."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="prompt-only")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=3000)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--split-manifest", default="gan2026_split_v1")
    parser.add_argument(
        "--source-row-index",
        type=int,
        nargs="+",
        default=list(DEFAULT_FIVE_ROW_SOURCE_IDS),
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_FIVE_ROW_JSONL_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_FIVE_ROW_REPORT_PATH)
    args = parser.parse_args()

    records_by_source = {
        record.source_row_index: record for record in load_records_for_split(args.split)
    }
    records = [
        records_by_source[source_row_index]
        for source_row_index in args.source_row_index
        if source_row_index in records_by_source
    ]
    rows, run_metadata = run_records(
        records,
        split=args.split,
        split_manifest=args.split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
    )
    write_jsonl(rows, args.jsonl_path)
    write_report(rows, run_metadata, args.report_path, jsonl_path=args.jsonl_path)
    print(f"Wrote {args.jsonl_path}")
    print(f"Wrote {args.report_path}")


if __name__ == "__main__":
    main()
