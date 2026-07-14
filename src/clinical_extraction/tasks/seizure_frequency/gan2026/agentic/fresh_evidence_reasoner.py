"""Fresh-evidence reasoner over saved Gan structured-event agents.

This V12 candidate is broader than a saved-output selector but narrower than a
free direct labeler. The model may keep the GPT structured-event final answer or
replace it with a newly reasoned final label from exact raw-note evidence after
reviewing GPT, Qwen, and DeepSeek structured-event traces. Deterministic code
only validates JSON, performs format-only label repair, validates cited evidence
as source substrings, renders keep/fallback actions from the original GPT
structured-event final, and scores after the decision.

``run_split`` delegates row-loop ceremony to :mod:`run_driver`.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.claim_policy import fresh_evidence_claim_boundary_for_split
from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator as cross_model_base,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    family_cv_promotion,
    family_transitions,
    llm_event_reasoner,
    precision_gated_selector,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    SplitRunParams,
    run_cross_model_structured_event_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_fresh_evidence_reasoner_v0_6"
PROMPT_VERSION_V0_10 = "gan2026_fresh_evidence_reasoner_v0_10_triage"
# A3 simplest-architecture variant: identical policy/guards to v0.6 but the model
# reviews ONLY the saved GPT structured-event trace (Qwen + DeepSeek dropped from
# the prompt). Tests whether the reasoner's lift survives without the peer
# ensemble, collapsing 3 upstream models to 1.
# Plan: docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md
PROMPT_VERSION_V0_11_GPT_ONLY = "gan2026_fresh_evidence_reasoner_v0_11_gpt_only"
# A4 simplest-architecture variant: GPT + exactly ONE peer trace (2 upstream
# models). Same policy/guards as v0.6; the included peer is selected via
# set_active_two_model_peer(). Tests the minimal ensemble that preserves the
# cross-model corroboration A3 proved the reasoner needs to replace safely.
PROMPT_VERSION_V0_12_TWO_MODEL = "gan2026_fresh_evidence_reasoner_v0_12_two_model"
SAFETY_GATE_VERSION = "gan2026_fresh_evidence_safety_gate_v0_9"

# Peer agent included alongside "gpt" for the v0_12 two-model variant.
_ACTIVE_TWO_MODEL_PEER: cross_model_base.AgentId = "deepseek"


def set_active_two_model_peer(peer_agent_id: str) -> None:
    """Select the single peer trace shown in the v0_12 two-model variant."""
    global _ACTIVE_TWO_MODEL_PEER  # noqa: PLW0603
    if peer_agent_id not in cross_model_base.AGENT_IDS or peer_agent_id == "gpt":
        raise ValueError(f"peer_agent_id must be a non-gpt agent in {cross_model_base.AGENT_IDS}")
    _ACTIVE_TWO_MODEL_PEER = peer_agent_id


def get_active_two_model_peer() -> cross_model_base.AgentId:
    """Return the peer agent id currently selected for the v0_12 variant."""
    return _ACTIVE_TWO_MODEL_PEER


PIPELINE_FAMILY = "fresh_evidence_reasoner"

# Active prompt version — call set_active_prompt_version() before run_split to
# switch to v0.10; the module default stays v0.6 so existing callers are not
# affected.
_ACTIVE_PROMPT_VERSION: str = PROMPT_VERSION


def set_active_prompt_version(version: str) -> None:
    """Switch the module-level active prompt version (call before run_split)."""
    global _ACTIVE_PROMPT_VERSION  # noqa: PLW0603
    _ACTIVE_PROMPT_VERSION = version


def get_active_prompt_version() -> str:
    """Return the currently active prompt version."""
    return _ACTIVE_PROMPT_VERSION


DEFAULT_STRUCTURED_EVENT_JSONL_PATH = llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH = cross_model_base.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = (
    cross_model_base.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
)
TEST_GPT_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_"
    "gpt41mini_2026-06-09.jsonl"
)
TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_agentic_structured_event_patch_recent_unresolved_burden_"
    "test450_qwen3635b_2026-06-13.jsonl"
)
TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_fresh_evidence_reasoner_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_fresh_evidence_reasoner_validation.md")

FreshEvidenceAction = Literal[
    "keep_original_structured_event_final",
    "replace_with_fresh_evidence_final",
]
FRESH_EVIDENCE_ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_fresh_evidence_final",
)
AmbiguityClassification = Literal[
    "explicit_count_window",
    "unknown_count_or_window",
    "last_event_only_unknown",
    "explicit_seizure_free_duration",
    "no_seizure_frequency_reference",
    "cluster_axis_complete",
    "cluster_axis_incomplete",
    "not_applicable",
]
AMBIGUITY_CLASSIFICATION_VALUES = (
    "explicit_count_window",
    "unknown_count_or_window",
    "last_event_only_unknown",
    "explicit_seizure_free_duration",
    "no_seizure_frequency_reference",
    "cluster_axis_complete",
    "cluster_axis_incomplete",
    "not_applicable",
)
UNKNOWN_FREQUENCY_POLICY_INSTRUCTIONS = (
    (
        "Unknown-frequency boundary: when either the number of seizures or the "
        "relevant time period is unclear, prefer unknown over an inferred rate."
    ),
    (
        "Last-event-only evidence is unknown: a most-recent seizure date does "
        "not prove one seizure in a defined period, and no-seizures-since-last-event "
        "does not by itself create a Gan frequency or seizure-free label."
    ),
    (
        "Do not label seizure_free when the support is only a last seizure date "
        "plus no seizures since; choose unknown unless the note independently "
        "states a seizure-free/no-seizures duration as the current frequency state."
    ),
    (
        "Open-ended 'since starting/beginning medication or diet' evidence is "
        "unknown unless both the number of events and the relevant time period "
        "are explicit enough to define the denominator."
    ),
    (
        "A medication or diet start date alone is not a denominator for 'N events "
        "since starting X'; choose unknown unless the note defines the observation "
        "or follow-up period for the event count."
    ),
    (
        "A single provoked breakthrough event on a date is a single event, not a "
        "frequency; use unknown unless the note defines the observation period "
        "for that count."
    ),
    (
        "An explicit seizure count plus a usable follow-up period can support a "
        "frequency label, especially when the surrounding timeline defines the "
        "period and states no further seizures after those counted events."
    ),
)


# v0.10 triage reason values — only these two high-confidence reasons permit
# demotion to unknown; all other triage outcomes are rendering/precedence
# fixes that do not gate on confidence.
TriageReason = Literal[
    "single_anchor_last_event",
    "explicitly_provoked_or_transient",
    "cluster_retention",
    "seizure_free_check",
    "usable_rate",
    "no_triage_issue",
]
TRIAGE_REASON_VALUES = (
    "single_anchor_last_event",
    "explicitly_provoked_or_transient",
    "cluster_retention",
    "seizure_free_check",
    "usable_rate",
    "no_triage_issue",
)

# Only these two reasons may gate a demote-to-unknown replacement (confidence
# gate from the predeclaration).
CONFIDENCE_GATED_UNKNOWN_DEMOTION_REASONS: frozenset[str] = frozenset(
    ("single_anchor_last_event", "explicitly_provoked_or_transient")
)


class TriageResult(BaseModel):
    """Output of the v0.10 triage scaffold (4 steps evaluated before label)."""

    model_config = ConfigDict(extra="ignore")

    confound_check: str = ""
    window_check: str = ""
    cluster_check: str = ""
    seizure_free_check: str = ""
    triage_reason: TriageReason | None = None
    triage_notes: str = ""


class FreshEvidenceDecision(BaseModel):
    """Prediction schema for V12 fresh-evidence replacement."""

    model_config = ConfigDict(extra="forbid")

    action: FreshEvidenceAction
    final_label: str
    final_kind: llm_event_reasoner.DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    boundary_profile: tuple[str, ...] = Field(default_factory=tuple)
    ambiguity_classification: AmbiguityClassification | None = None
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: llm_event_reasoner.Uncertainty
    tool_calls: tuple[llm_event_reasoner.ToolTrace, ...] = Field(default_factory=tuple)
    attribution: llm_event_reasoner.DecisionAttribution
    triage_result: TriageResult | None = None


class ParsedFreshEvidenceDecision(BaseModel):
    """Raw, format-only, and evidence-gated views of one V12 output."""

    model_config = ConfigDict(extra="forbid")

    raw_fresh_decision: FreshEvidenceDecision | None
    raw_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    format_only_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    final_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    parse_errors: list[str] = Field(default_factory=list)
    format_repair_events: list[dict[str, Any]] = Field(default_factory=list)
    action_render_events: list[str] = Field(default_factory=list)


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool,
    api_base: str | None,
    escalation_reason: str | None,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    candidate_set_jsonl_path: Path | None = None,
    structured_event_jsonl_path: Path | None = None,
    structured_event_rows: Sequence[Mapping[str, Any]] | None = None,
    structured_event_source_path: Path | None = None,
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or prompt-smoke the fresh-evidence reasoner."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = _gpt_structured_event_source_path(
        split,
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
    )
    agent_sources = _structured_event_source_paths_for_split(split, source_path)
    active_prompt_version = _ACTIVE_PROMPT_VERSION
    params = SplitRunParams(
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
    )
    rows, metadata = run_cross_model_structured_event_split(
        records,
        params=params,
        prompt_version=active_prompt_version,
        metadata_extra={
            "artifact_kind": "gan2026_fresh_evidence_reasoner_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": f"{active_prompt_version}+{SAFETY_GATE_VERSION}",
            "safety_gate_version": SAFETY_GATE_VERSION,
            "structured_event_source_role": (
                "GPT, Qwen, and DeepSeek saved LLM structured-event traces are "
                "evidence scaffolds. The prediction-bearing replacement, when "
                "made, is a fresh model-owned interpretation from exact raw-note "
                "evidence. Deterministic top labels are not shown or used."
            ),
            "claim_boundary": fresh_evidence_claim_boundary_for_split(split),
        },
        build_row=_build_row,
        summarize_rows=lambda split_rows: summarize_rows(split_rows, split=split),
        gpt_structured_event_source_path=source_path,
        agent_source_paths=agent_sources,
        gpt_structured_event_rows=structured_event_rows,
        agent_rows_by_id=agent_rows_by_id,
        gate_interpretation=llm_event_reasoner.gate_interpretation,
        write_report=write_report,
        row_kwargs={"prompt_version": active_prompt_version},
    )
    if split != "test":
        # Per-family breakdown and the held-out-family CV promotion verdict are
        # validation-only instruments; the holdout protocol is aggregate-only,
        # so neither is attached for `test`.
        summary_by_family = family_transitions.summarize_transitions_by_family(
            rows, **family_transitions.FRESH_EVIDENCE_PATHS
        )
        metadata["summary_by_family"] = summary_by_family
        metadata["family_holdout_cv"] = family_cv_promotion.summarize_family_holdout_cv(
            summary_by_family
        )
        metadata["precision_gated_selector"] = (
            precision_gated_selector.summarize_precision_gated_selector(
                rows,
                transition_path=family_transitions.FRESH_EVIDENCE_PATHS["transition_path"],
                label_changed_path=family_transitions.FRESH_EVIDENCE_PATHS["label_changed_path"],
                baseline_correct_path=family_transitions.FRESH_EVIDENCE_PATHS[
                    "baseline_correct_path"
                ],
                candidate_correct_path=family_transitions.FRESH_EVIDENCE_PATHS[
                    "candidate_correct_path"
                ],
            )
        )
    return rows, metadata


def _gpt_structured_event_source_path(
    split: str,
    requested_path: Path,
) -> Path:
    if split == "test" and requested_path == DEFAULT_STRUCTURED_EVENT_JSONL_PATH:
        return TEST_GPT_STRUCTURED_EVENT_JSONL_PATH
    return requested_path


def _structured_event_source_paths_for_split(
    split: str,
    gpt_source_path: Path,
) -> dict[str, Path]:
    if split == "test":
        return {
            "gpt": gpt_source_path,
            "qwen": TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH,
            "deepseek": TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
        }
    return {
        "gpt": gpt_source_path,
        "qwen": DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH,
        "deepseek": DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
    }


def build_prompt_input(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
    prompt_version: str | None = None,
) -> str:
    """Build a split-neutral fresh-evidence payload."""

    effective_version = prompt_version if prompt_version is not None else _ACTIVE_PROMPT_VERSION
    if effective_version == PROMPT_VERSION_V0_10:
        return _build_prompt_input_v0_10(record, agent_rows, note_excerpt_chars=note_excerpt_chars)
    if effective_version == PROMPT_VERSION_V0_11_GPT_ONLY:
        return _build_prompt_input_v0_11_gpt_only(
            record, agent_rows, note_excerpt_chars=note_excerpt_chars
        )
    if effective_version == PROMPT_VERSION_V0_12_TWO_MODEL:
        return _build_prompt_input_v0_12_two_model(
            record, agent_rows, note_excerpt_chars=note_excerpt_chars
        )
    return _build_prompt_input_v0_6(record, agent_rows, note_excerpt_chars=note_excerpt_chars)


def _build_prompt_input_v0_6(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
) -> str:
    """Original v0.6 prompt (unchanged)."""

    agent_inputs = [
        cross_model_base._agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in cross_model_base.AGENT_IDS
    ]
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 fresh-evidence seizure-frequency reasoning",
        "variant": "V12_fresh_evidence_reasoner",
        "instructions": [
            (
                "Decide whether to keep the GPT structured-event final answer or "
                "replace it with one freshly reasoned Gan label from exact raw-note evidence."
            ),
            (
                "Use the three saved LLM structured-event traces as scaffolding, not "
                "as a vote. If a peer trace seems right, cite the raw evidence and "
                "produce the replacement yourself."
            ),
            (
                "Use keep_original_structured_event_final unless exact raw-note "
                "evidence proves a better current seizure-frequency interpretation."
            ),
            (
                "Replacement is for represented-evidence or clinical-selection misses: "
                "current/recent frequency, denominator/window, cluster burden, "
                "seizure-free conflict, unknown/no-reference boundary, or highest "
                "active semiology."
            ),
            (
                "Do not use outside final-answer sources, row IDs, split membership, "
                "gold labels, scoring metadata, deterministic rules, deterministic "
                "top labels, or benchmark feedback."
            ),
            (
                "For frequency labels, state the numerator, denominator, and window "
                "in calculation_trace. Do not turn one-off since-last-review counts "
                "into rates unless the interval length or recurring cadence is explicit."
            ),
            (
                "Before choosing final_label, set ambiguity_classification to the "
                "boundary class that explains whether count and window are usable. "
                "Use unknown_count_or_window when seizure evidence exists but either "
                "the number of events or the relevant time period is unclear."
            ),
            *UNKNOWN_FREQUENCY_POLICY_INSTRUCTIONS,
            (
                "Do not replace explicit numeric or range frequency evidence such as "
                "'twice per week' with 'multiple per week'; render the numeric/range "
                "frequency or keep the original structured-event final."
            ),
            (
                "For unknown, require evidence that seizure-frequency information "
                "exists but cannot be converted to a current recurring rate."
            ),
            (
                "For no_reference, require positive absence of seizure-frequency "
                "evidence; do not use it when awkward but usable frequency evidence exists."
            ),
            (
                "For seizure_free, require exact no-events-since or absence-duration "
                "evidence and no conflicting current/recent frequency evidence."
            ),
            (
                "Do not replace an original seizure-free structured-event final with "
                "unknown or no_reference merely because the note discusses non-epileptic "
                "spells, medication status, or qualitative improvement."
            ),
            (
                "Do not output bare 'seizure free'. If the duration is not explicit "
                "enough to render a Gan seizure-free label with a duration, keep the "
                "original structured-event final."
            ),
            (
                "Do not replace a frequency original with seizure_free for only "
                "days, weeks, or about one month after a recent last event; keep the "
                "frequency original on that short last-event-only boundary."
            ),
            (
                "For clusters, keep cluster cadence separate from events per cluster; "
                "only multiply or render cluster labels when both axes are supported."
            ),
            (
                "For multiple active semiologies, select the highest current clinically "
                "active burden, not the first-mentioned or most severe seizure type."
            ),
            "Evidence entries must be exact substrings copied from the note.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(FRESH_EVIDENCE_ACTION_VALUES),
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": (
                "saved event IDs or fresh_evidence_1 when replacement comes from raw text"
            ),
            "rejected_event_ids": "saved event IDs or agent finals explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list of targeted profile keys driving the choice",
            "ambiguity_classification": list(AMBIGUITY_CLASSIFICATION_VALUES),
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this V12 scaffold",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "saved_structured_event_agents": agent_inputs,
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_prompt_input_v0_11_gpt_only(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
) -> str:
    """A3 variant: v0.6 policy/guards, but only the saved GPT trace is shown.

    Identical to ``_build_prompt_input_v0_6`` except (1) the peer traces (Qwen,
    DeepSeek) are dropped from ``saved_structured_event_agents`` and (2) the two
    instruction lines that referred to "three traces" / "a peer trace" are
    reworded to the single GPT trace. Every clinical/unknown/boundary policy line
    is byte-identical to v0.6 so the only variable vs the 3-agent reasoner is the
    presence of the peer ensemble.
    """

    agent_inputs = [cross_model_base._agent_prompt_summary("gpt", agent_rows.get("gpt"))]
    payload = {
        "prompt_version": PROMPT_VERSION_V0_11_GPT_ONLY,
        "task": "Gan 2026 fresh-evidence seizure-frequency reasoning",
        "variant": "V12_fresh_evidence_reasoner_v0_11_gpt_only",
        "instructions": [
            (
                "Decide whether to keep the GPT structured-event final answer or "
                "replace it with one freshly reasoned Gan label from exact raw-note evidence."
            ),
            (
                "Use the saved GPT structured-event trace as scaffolding, not as an "
                "answer to copy. Cite the raw evidence and produce the replacement "
                "yourself when the trace is wrong or incomplete."
            ),
            (
                "Use keep_original_structured_event_final unless exact raw-note "
                "evidence proves a better current seizure-frequency interpretation."
            ),
            (
                "Replacement is for represented-evidence or clinical-selection misses: "
                "current/recent frequency, denominator/window, cluster burden, "
                "seizure-free conflict, unknown/no-reference boundary, or highest "
                "active semiology."
            ),
            (
                "Do not use outside final-answer sources, row IDs, split membership, "
                "gold labels, scoring metadata, deterministic rules, deterministic "
                "top labels, or benchmark feedback."
            ),
            (
                "For frequency labels, state the numerator, denominator, and window "
                "in calculation_trace. Do not turn one-off since-last-review counts "
                "into rates unless the interval length or recurring cadence is explicit."
            ),
            (
                "Before choosing final_label, set ambiguity_classification to the "
                "boundary class that explains whether count and window are usable. "
                "Use unknown_count_or_window when seizure evidence exists but either "
                "the number of events or the relevant time period is unclear."
            ),
            *UNKNOWN_FREQUENCY_POLICY_INSTRUCTIONS,
            (
                "Do not replace explicit numeric or range frequency evidence such as "
                "'twice per week' with 'multiple per week'; render the numeric/range "
                "frequency or keep the original structured-event final."
            ),
            (
                "For unknown, require evidence that seizure-frequency information "
                "exists but cannot be converted to a current recurring rate."
            ),
            (
                "For no_reference, require positive absence of seizure-frequency "
                "evidence; do not use it when awkward but usable frequency evidence exists."
            ),
            (
                "For seizure_free, require exact no-events-since or absence-duration "
                "evidence and no conflicting current/recent frequency evidence."
            ),
            (
                "Do not replace an original seizure-free structured-event final with "
                "unknown or no_reference merely because the note discusses non-epileptic "
                "spells, medication status, or qualitative improvement."
            ),
            (
                "Do not output bare 'seizure free'. If the duration is not explicit "
                "enough to render a Gan seizure-free label with a duration, keep the "
                "original structured-event final."
            ),
            (
                "Do not replace a frequency original with seizure_free for only "
                "days, weeks, or about one month after a recent last event; keep the "
                "frequency original on that short last-event-only boundary."
            ),
            (
                "For clusters, keep cluster cadence separate from events per cluster; "
                "only multiply or render cluster labels when both axes are supported."
            ),
            (
                "For multiple active semiologies, select the highest current clinically "
                "active burden, not the first-mentioned or most severe seizure type."
            ),
            "Evidence entries must be exact substrings copied from the note.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(FRESH_EVIDENCE_ACTION_VALUES),
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": (
                "saved event IDs or fresh_evidence_1 when replacement comes from raw text"
            ),
            "rejected_event_ids": "saved event IDs or agent finals explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list of targeted profile keys driving the choice",
            "ambiguity_classification": list(AMBIGUITY_CLASSIFICATION_VALUES),
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this V12 scaffold",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "saved_structured_event_agents": agent_inputs,
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_prompt_input_v0_12_two_model(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
) -> str:
    """A4 variant: v0.6 policy/guards, but only GPT + one peer trace are shown.

    Identical to ``_build_prompt_input_v0_6`` except the saved traces are limited
    to ("gpt", peer) where peer is selected via set_active_two_model_peer(), and
    the two trace-referencing lines are reworded from "three" to "two" traces.
    Every clinical/unknown/boundary policy line is byte-identical to v0.6 so the
    only variable vs the 3-agent reasoner is the dropped third model.
    """

    peer = _ACTIVE_TWO_MODEL_PEER
    agent_ids: tuple[cross_model_base.AgentId, ...] = ("gpt", peer)
    agent_inputs = [
        cross_model_base._agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in agent_ids
    ]
    payload = {
        "prompt_version": PROMPT_VERSION_V0_12_TWO_MODEL,
        "task": "Gan 2026 fresh-evidence seizure-frequency reasoning",
        "variant": f"V12_fresh_evidence_reasoner_v0_12_two_model_gpt_{peer}",
        "instructions": [
            (
                "Decide whether to keep the GPT structured-event final answer or "
                "replace it with one freshly reasoned Gan label from exact raw-note evidence."
            ),
            (
                "Use the two saved LLM structured-event traces as scaffolding, not "
                "as a vote. If a peer trace seems right, cite the raw evidence and "
                "produce the replacement yourself."
            ),
            (
                "Use keep_original_structured_event_final unless exact raw-note "
                "evidence proves a better current seizure-frequency interpretation."
            ),
            (
                "Replacement is for represented-evidence or clinical-selection misses: "
                "current/recent frequency, denominator/window, cluster burden, "
                "seizure-free conflict, unknown/no-reference boundary, or highest "
                "active semiology."
            ),
            (
                "Do not use outside final-answer sources, row IDs, split membership, "
                "gold labels, scoring metadata, deterministic rules, deterministic "
                "top labels, or benchmark feedback."
            ),
            (
                "For frequency labels, state the numerator, denominator, and window "
                "in calculation_trace. Do not turn one-off since-last-review counts "
                "into rates unless the interval length or recurring cadence is explicit."
            ),
            (
                "Before choosing final_label, set ambiguity_classification to the "
                "boundary class that explains whether count and window are usable. "
                "Use unknown_count_or_window when seizure evidence exists but either "
                "the number of events or the relevant time period is unclear."
            ),
            *UNKNOWN_FREQUENCY_POLICY_INSTRUCTIONS,
            (
                "Do not replace explicit numeric or range frequency evidence such as "
                "'twice per week' with 'multiple per week'; render the numeric/range "
                "frequency or keep the original structured-event final."
            ),
            (
                "For unknown, require evidence that seizure-frequency information "
                "exists but cannot be converted to a current recurring rate."
            ),
            (
                "For no_reference, require positive absence of seizure-frequency "
                "evidence; do not use it when awkward but usable frequency evidence exists."
            ),
            (
                "For seizure_free, require exact no-events-since or absence-duration "
                "evidence and no conflicting current/recent frequency evidence."
            ),
            (
                "Do not replace an original seizure-free structured-event final with "
                "unknown or no_reference merely because the note discusses non-epileptic "
                "spells, medication status, or qualitative improvement."
            ),
            (
                "Do not output bare 'seizure free'. If the duration is not explicit "
                "enough to render a Gan seizure-free label with a duration, keep the "
                "original structured-event final."
            ),
            (
                "Do not replace a frequency original with seizure_free for only "
                "days, weeks, or about one month after a recent last event; keep the "
                "frequency original on that short last-event-only boundary."
            ),
            (
                "For clusters, keep cluster cadence separate from events per cluster; "
                "only multiply or render cluster labels when both axes are supported."
            ),
            (
                "For multiple active semiologies, select the highest current clinically "
                "active burden, not the first-mentioned or most severe seizure type."
            ),
            "Evidence entries must be exact substrings copied from the note.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(FRESH_EVIDENCE_ACTION_VALUES),
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": (
                "saved event IDs or fresh_evidence_1 when replacement comes from raw text"
            ),
            "rejected_event_ids": "saved event IDs or agent finals explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list of targeted profile keys driving the choice",
            "ambiguity_classification": list(AMBIGUITY_CLASSIFICATION_VALUES),
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this V12 scaffold",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "saved_structured_event_agents": agent_inputs,
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


# v0.10 triage scaffold instructions inserted BEFORE label rendering.
_V0_10_TRIAGE_SCAFFOLD_INSTRUCTIONS = [
    (
        "TRIAGE SCAFFOLD (mandatory — evaluate ALL four steps from the raw note "
        "BEFORE choosing final_label or action):"
    ),
    (
        "STEP 1 — confound_check: Are the documented events provoked or situational "
        "(missed meals, sleep deprivation, travel/jet-lag, alcohol, medication-supply "
        "gaps/non-adherence) or a transient exacerbation / new-or-uncertain "
        "classification with work-up still pending? If yes AND the underlying habitual "
        "rate is absent or genuinely unknowable, set triage_reason = "
        "'explicitly_provoked_or_transient'. Otherwise continue."
    ),
    (
        "STEP 2 — window_check: Is the observation window a usable habitual baseline "
        "(a defined follow-up period with a recurring event count), or is the ONLY "
        "anchor a single dated last-event with NO stated recurring rate? A single "
        "dated last-event with no stated recurring rate is NOT a denominator — the "
        "count cannot be converted to a per-period rate. If the only anchor is a "
        "single dated last-event and there is no separately stated habitual rate, "
        "set triage_reason = 'single_anchor_last_event'. If a usable habitual "
        "baseline or count+window IS present, continue — do NOT demote it to unknown."
    ),
    (
        "STEP 3 — cluster_check: Do the events arrive in discrete clusters (a burst "
        "of multiple seizures on one day or in a short run, then a cluster-free "
        "interval before the next burst)? If yes, preserve BOTH the cluster cadence "
        "(e.g. 1 cluster per month) AND the per-cluster burden (e.g. multiple per "
        "cluster) as a two-axis label. Never flatten cluster patterns to a simple "
        "per-period rate. Set triage_reason = 'cluster_retention' if clusters are "
        "present and you are preserving the two-axis form. This step is a rendering "
        "fix — it does NOT gate unknown demotion."
    ),
    (
        "STEP 4 — seizure_free_check: Is a continuous seizure-free interval "
        "EXPLICITLY ASSERTED (e.g. 'no seizures for X months'), or is there only a "
        "last-event date with no asserted ongoing interval? A last-event date without "
        "an explicit seizure-free duration is NOT a seizure-free label; choose unknown "
        "instead. If the note explicitly asserts a seizure-free interval, set "
        "triage_reason = 'seizure_free_check'. This step is a rendering fix — it "
        "does NOT gate unknown demotion unless the ONLY evidence is a last-event date."
    ),
    (
        "CONFIDENCE GATE (critical): You may demote the structured-event answer to "
        "'unknown' ONLY when triage_reason is 'single_anchor_last_event' OR "
        "'explicitly_provoked_or_transient'. Do NOT demote on a bare/low-confidence "
        "concern, a clearly stated habitual rate, or a usable count+window baseline. "
        "If the triage yields 'cluster_retention' or 'seizure_free_check', those are "
        "rendering fixes that do not require a demote-to-unknown. If the triage yields "
        "'usable_rate' or 'no_triage_issue', keep the original or replace with the "
        "better rate — do NOT demote to unknown."
    ),
    (
        "After evaluating all four steps, populate triage_result with: "
        "confound_check (brief finding), window_check (brief finding), "
        "cluster_check (brief finding), seizure_free_check (brief finding), "
        "triage_reason (one value from the allowed list), triage_notes (summary). "
        "Then choose action and final_label consistent with the triage."
    ),
]

_V0_10_TRIAGE_OUTPUT_SCHEMA_ADDITION = {
    "triage_result": {
        "confound_check": "brief finding from STEP 1",
        "window_check": "brief finding from STEP 2",
        "cluster_check": "brief finding from STEP 3",
        "seizure_free_check": "brief finding from STEP 4",
        "triage_reason": list(TRIAGE_REASON_VALUES),
        "triage_notes": "one-sentence summary of the dominant triage finding",
    }
}


def _build_prompt_input_v0_10(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
) -> str:
    """v0.10 triage scaffold prompt — inserts 4-step triage BEFORE label choice."""

    agent_inputs = [
        cross_model_base._agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in cross_model_base.AGENT_IDS
    ]
    # Build v0.10 instructions: triage scaffold first, then existing policy rules.
    instructions_v0_10 = [
        (
            "Decide whether to keep the GPT structured-event final answer or "
            "replace it with one freshly reasoned Gan label from exact raw-note evidence."
        ),
        (
            "Use the three saved LLM structured-event traces as scaffolding, not "
            "as a vote. If a peer trace seems right, cite the raw evidence and "
            "produce the replacement yourself."
        ),
        (
            "Use keep_original_structured_event_final unless exact raw-note "
            "evidence proves a better current seizure-frequency interpretation."
        ),
        (
            "Replacement is for represented-evidence or clinical-selection misses: "
            "current/recent frequency, denominator/window, cluster burden, "
            "seizure-free conflict, unknown/no-reference boundary, or highest "
            "active semiology."
        ),
        (
            "Do not use outside final-answer sources, row IDs, split membership, "
            "gold labels, scoring metadata, deterministic rules, deterministic "
            "top labels, or benchmark feedback."
        ),
        *_V0_10_TRIAGE_SCAFFOLD_INSTRUCTIONS,
        (
            "For frequency labels, state the numerator, denominator, and window "
            "in calculation_trace. Do not turn one-off since-last-review counts "
            "into rates unless the interval length or recurring cadence is explicit."
        ),
        (
            "Before choosing final_label, set ambiguity_classification to the "
            "boundary class that explains whether count and window are usable. "
            "Use unknown_count_or_window when seizure evidence exists but either "
            "the number of events or the relevant time period is unclear."
        ),
        *UNKNOWN_FREQUENCY_POLICY_INSTRUCTIONS,
        (
            "Do not replace explicit numeric or range frequency evidence such as "
            "'twice per week' with 'multiple per week'; render the numeric/range "
            "frequency or keep the original structured-event final."
        ),
        (
            "For unknown, require evidence that seizure-frequency information "
            "exists but cannot be converted to a current recurring rate."
        ),
        (
            "For no_reference, require positive absence of seizure-frequency "
            "evidence; do not use it when awkward but usable frequency evidence exists."
        ),
        (
            "For seizure_free, require exact no-events-since or absence-duration "
            "evidence and no conflicting current/recent frequency evidence."
        ),
        (
            "Do not replace an original seizure-free structured-event final with "
            "unknown or no_reference merely because the note discusses non-epileptic "
            "spells, medication status, or qualitative improvement."
        ),
        (
            "Do not output bare 'seizure free'. If the duration is not explicit "
            "enough to render a Gan seizure-free label with a duration, keep the "
            "original structured-event final."
        ),
        (
            "Do not replace a frequency original with seizure_free for only "
            "days, weeks, or about one month after a recent last event; keep the "
            "frequency original on that short last-event-only boundary."
        ),
        (
            "For clusters, keep cluster cadence separate from events per cluster; "
            "only multiply or render cluster labels when both axes are supported."
        ),
        (
            "For multiple active semiologies, select the highest current clinically "
            "active burden, not the first-mentioned or most severe seizure type."
        ),
        "Evidence entries must be exact substrings copied from the note.",
        (
            "final_label must be a valid Gan label only: unknown, no seizure "
            "frequency reference, seizure free, multiple per day/week/month/year, "
            "or '<number> [to <number>] per day/week/month/year'."
        ),
        (
            "action, final_kind, uncertainty, and attribution must each be one "
            "string, not an array of options."
        ),
    ]
    required_schema = {
        "action": list(FRESH_EVIDENCE_ACTION_VALUES),
        "final_label": "Gan-style label string",
        "final_kind": [
            "frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        ],
        "selected_event_ids": (
            "saved event IDs or fresh_evidence_1 when replacement comes from raw text"
        ),
        "rejected_event_ids": "saved event IDs or agent finals explicitly rejected",
        "evidence": "list of exact evidence substrings supporting the final choice",
        "boundary_profile": "list of targeted profile keys driving the choice",
        "ambiguity_classification": list(AMBIGUITY_CLASSIFICATION_VALUES),
        "calculation_trace": "short arithmetic or boundary trace, or null",
        "clinical_rationale": "brief clinical rationale",
        "uncertainty": "one string: low | medium | high",
        "tool_calls": "empty list for this V12 scaffold",
        "attribution": (
            "one string: llm_selected_tool_rendered | "
            "llm_selected_format_repaired | llm_original_structured_event_kept"
        ),
        **_V0_10_TRIAGE_OUTPUT_SCHEMA_ADDITION,
    }
    payload = {
        "prompt_version": PROMPT_VERSION_V0_10,
        "task": "Gan 2026 fresh-evidence seizure-frequency reasoning with triage scaffold",
        "variant": "V12_fresh_evidence_reasoner_v0_10_triage",
        "instructions": instructions_v0_10,
        "required_output_schema": required_schema,
        "saved_structured_event_agents": agent_inputs,
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_fresh_evidence_decision_json(
    raw_output: str,
    *,
    note_text: str,
    structured_event_row: Mapping[str, Any] | None,
) -> ParsedFreshEvidenceDecision:
    """Parse a fresh-evidence decision and apply the evidence gate."""

    parse_errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            llm_event_reasoner._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[f"invalid_json: {exc.msg}"],
        )
    parse_errors.extend(dialect_notes)
    payload, shape_notes = _repair_fresh_shape(repair_decision_payload(raw_payload))
    payload = _filter_fresh_payload(payload)
    parse_errors.extend(shape_notes)
    try:
        raw_fresh = FreshEvidenceDecision.model_validate(payload)
    except ValidationError as exc:
        return ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[
                *parse_errors,
                f"schema_validation_error: {exc.errors()[0]['msg']}",
            ],
        )

    raw_common = _common_decision_from_fresh(raw_fresh)
    format_decision, repair_events, format_notes = _format_only_decision(raw_common)
    parse_errors.extend(format_notes)
    final_decision, action_events, action_notes = _render_fresh_action(
        raw_fresh,
        format_decision,
        note_text=note_text,
        structured_event_row=structured_event_row,
    )
    parse_errors.extend(action_notes)
    return ParsedFreshEvidenceDecision(
        raw_fresh_decision=raw_fresh,
        raw_decision=raw_common,
        format_only_decision=format_decision,
        final_decision=final_decision,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
        action_render_events=action_events,
    )


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str | None = None,
) -> dict[str, Any]:
    """Summarize V12 rows across raw, format-only, final, and V0 layers."""

    summary = llm_event_reasoner.summarize_rows(rows)
    summary["fresh_evidence_replace_actions"] = 0
    summary["fresh_evidence_gate_fallbacks"] = 0
    profiles: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("fresh_evidence_decision_record") or {})
        action = str(decision.get("action") or "")
        if action:
            actions[action] += 1
        if action == "replace_with_fresh_evidence_final":
            summary["fresh_evidence_replace_actions"] += 1
        if any(
            str(event).startswith("fresh_evidence_gate_fallback:")
            for event in row.get("action_render_events") or []
        ):
            summary["fresh_evidence_gate_fallbacks"] += 1
        for profile in decision.get("boundary_profile") or []:
            profiles[str(profile)] += 1
    summary["fresh_evidence_actions"] = dict(sorted(actions.items()))
    summary["fresh_evidence_profiles"] = dict(sorted(profiles.items()))
    if split == "test":
        _redact_holdout_summary(summary)
    return summary


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = dict(metadata.get("summary") or {})
    gate = dict(metadata.get("gate") or {})
    split = str(metadata.get("split") or "validation")
    split_manifest = str(metadata.get("split_manifest") or "gan2026_split_v1")
    is_test_split = split == "test"
    artifact_kind = (
        "This is a frozen aggregate-only V12 fresh-evidence holdout audit artifact."
        if is_test_split
        else "This is a validation-development V12 fresh-evidence reasoning artifact."
    )
    lines = [
        "# Gan 2026 Fresh-Evidence Reasoner",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        artifact_kind,
        "The model may replace the GPT structured-event final only from exact raw-note evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V12 fresh-evidence reasoner over saved structured events.",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Split: `{split}`, manifest `{split_manifest}`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Fresh-evidence replace actions: {summary.get('fresh_evidence_replace_actions', 0)}",
        f"- Evidence-gate fallbacks: {summary.get('fresh_evidence_gate_fallbacks', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        (f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}"),
        (f"- V0 Pragmatic: {summary.get('v0_pragmatic_correct', 0)}/{summary.get('rows', 0)}"),
        (
            f"- Raw model Purist: {summary.get('raw_model_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Raw model Pragmatic: {summary.get('raw_model_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Format-only Purist: {summary.get('format_only_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            "- Format-only Pragmatic: "
            f"{summary.get('format_only_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (f"- Final Purist: {summary.get('final_purist_correct', 0)}/{summary.get('rows', 0)}"),
        (
            f"- Final Pragmatic: {summary.get('final_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (f"- Changed-label precision vs V0: {summary.get('changed_label_precision_vs_v0')}"),
        f"- Actions: `{summary.get('fresh_evidence_actions', {})}`",
        (
            "- Profiles: omitted from the test report to keep the first readout aggregate-only."
            if is_test_split
            else f"- Profiles: `{summary.get('fresh_evidence_profiles', {})}`"
        ),
        "",
        "## Gate",
        "",
        f"- Status: `{gate.get('status')}`",
        f"- Interpretation: {gate.get('interpretation')}",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
    ]
    if is_test_split:
        lines.extend(
            [
                "",
                "## Aggregate-Only Holdout Readout",
                "",
                (
                    "Row-level test details are intentionally omitted from this Markdown "
                    "report. Do not inspect the JSONL or row-level failures before "
                    "starting a separately authorized validation-only follow-up cycle."
                ),
            ]
        )
        write_markdown_report(path, lines)
        return

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        fresh_record = dict(row.get("fresh_evidence_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        render_events = "; ".join(str(event) for event in row.get("action_render_events") or [])
        if render_events:
            notes = f"{notes}; {render_events}" if notes else render_events
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{fresh_record.get('action')}` | "
            f"`{fresh_record.get('boundary_profile')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _redact_holdout_summary(summary: dict[str, Any]) -> None:
    """Keep locked-test stdout/report summaries inside the first-readout policy."""

    omitted_fields = []
    for field_name in ("final_labels", "fresh_evidence_profiles"):
        if field_name in summary:
            summary.pop(field_name)
            omitted_fields.append(field_name)
    if omitted_fields:
        summary["aggregate_only_omitted_fields"] = sorted(omitted_fields)


class FreshEvidenceSignature(dspy.Signature):
    """Reason from raw evidence and emit one keep-or-replace JSON decision."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with saved structured-event traces and a raw-note excerpt."
    )
    decision_json: str = dspy.OutputField(desc="Strict JSON object matching FreshEvidenceDecision.")


class DspyFreshEvidenceCaller(dspy.Module):
    """DSPy caller for the V12 fresh-evidence reasoner."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(FreshEvidenceSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _build_row(
    record: GanFrequencyRecord,
    *,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    prompt_version: str = PROMPT_VERSION,
) -> dict[str, Any]:
    gpt_row = agent_rows.get("gpt")
    prompt_input_json = build_prompt_input(record, agent_rows, prompt_version=prompt_version)
    raw_output = ""
    call_error: str | None = None
    model_call_attempted = False
    if mode == "live":
        model_call_attempted = True
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    parsed = (
        parse_fresh_evidence_decision_json(
            raw_output,
            note_text=record.note_text,
            structured_event_row=gpt_row,
        )
        if raw_output
        else ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    v0_reference = llm_event_reasoner._v0_reference(gpt_row)
    score_layers = {
        "raw_model": llm_event_reasoner._score_layer(record, parsed.raw_decision),
        "format_only": llm_event_reasoner._score_layer(
            record,
            parsed.format_only_decision,
        ),
        "final": llm_event_reasoner._score_layer(record, final_decision),
    }
    evidence_valid = llm_event_reasoner._decision_evidence_valid(
        record.note_text,
        final_decision,
    )
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": prompt_version,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "structured_event_input_available": gpt_row is not None,
        "agent_input_available": {
            agent_id: agent_rows.get(agent_id) is not None
            for agent_id in cross_model_base.AGENT_IDS
        },
        "v0_reference": v0_reference,
        "hidden_families": list(
            family_transitions.tag_hidden_families(
                note_text=record.note_text,
                gold_per_month=record.gold_monthly_frequency,
            )
        ),
        "model_call_attempted": model_call_attempted,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parsed.parse_errors,
        "format_repair_events": parsed.format_repair_events,
        "action_render_events": parsed.action_render_events,
        "fresh_evidence_decision_record": (
            parsed.raw_fresh_decision.model_dump(mode="json") if parsed.raw_fresh_decision else None
        ),
        "raw_decision_record": (
            parsed.raw_decision.model_dump(mode="json") if parsed.raw_decision else None
        ),
        "format_only_decision_record": (
            parsed.format_only_decision.model_dump(mode="json")
            if parsed.format_only_decision
            else None
        ),
        "decision_record": final_decision.model_dump(mode="json") if final_decision else None,
        "evidence_valid": evidence_valid,
        "score_layers": score_layers,
        "transition_vs_v0": llm_event_reasoner._transition_vs_v0(
            v0_reference=v0_reference,
            final_layer=score_layers["final"],
        ),
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "trace_warnings": (["prompt_only_no_prediction"] if mode == "prompt-only" else [])
        + (["missing_structured_event_row"] if gpt_row is None else []),
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyFreshEvidenceCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _filter_fresh_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(FreshEvidenceDecision.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_fresh_shape(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    if "clinical_rationale" not in repaired and "rationale" in repaired:
        repaired["clinical_rationale"] = str(repaired["rationale"])
        notes.append("decision_field_shape_repaired:clinical_rationale_alias")
    for field_name in (
        "selected_event_ids",
        "rejected_event_ids",
        "evidence",
        "boundary_profile",
    ):
        value = repaired.get(field_name)
        normalized = _string_tuple(value)
        if normalized != value:
            repaired[field_name] = normalized
            notes.append(f"decision_field_shape_repaired:{field_name}")
    tool_calls = repaired.get("tool_calls")
    if tool_calls is None:
        repaired["tool_calls"] = []
    elif isinstance(tool_calls, dict):
        repaired["tool_calls"] = [tool_calls]
        notes.append("decision_field_shape_repaired:tool_calls")
    for field_name, allowed_values in (
        ("action", FRESH_EVIDENCE_ACTION_VALUES),
        ("ambiguity_classification", AMBIGUITY_CLASSIFICATION_VALUES),
        ("uncertainty", llm_event_reasoner.UNCERTAINTY_VALUES),
        ("attribution", llm_event_reasoner.DECISION_ATTRIBUTION_VALUES),
    ):
        value = repaired.get(field_name)
        if isinstance(value, (list, tuple)):
            selected_value = next(
                (str(item) for item in value if str(item) in allowed_values),
                None,
            )
            if selected_value is not None:
                repaired[field_name] = selected_value
                notes.append(f"decision_enum_shape_repaired:{field_name}")
    calculation_trace = repaired.get("calculation_trace")
    if calculation_trace is not None and not isinstance(calculation_trace, str):
        repaired["calculation_trace"] = json.dumps(
            calculation_trace,
            ensure_ascii=False,
            sort_keys=True,
        )
        notes.append("decision_field_shape_repaired:calculation_trace")
    return repaired, notes


def _common_decision_from_fresh(
    decision: FreshEvidenceDecision,
) -> llm_event_reasoner.ReasonedFrequencyDecision:
    return llm_event_reasoner.ReasonedFrequencyDecision(
        final_label=decision.final_label,
        final_kind=decision.final_kind,
        selected_event_ids=decision.selected_event_ids,
        rejected_event_ids=decision.rejected_event_ids,
        evidence=decision.evidence,
        boundary_profile=decision.boundary_profile,
        calculation_trace=decision.calculation_trace,
        clinical_rationale=decision.clinical_rationale,
        uncertainty=decision.uncertainty,
        tool_calls=decision.tool_calls,
        attribution=decision.attribution,
    )


def _format_only_decision(
    raw_decision: llm_event_reasoner.ReasonedFrequencyDecision,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision, list[dict[str, Any]], list[str]]:
    parse_notes: list[str] = []
    repair_trace = repair_prediction_label_format_preserving_with_trace(raw_decision.final_label)
    repair_events = [
        llm_event_reasoner._repair_event_to_dict(event) for event in repair_trace.events
    ]
    format_decision = raw_decision
    if repair_trace.final_label != raw_decision.final_label:
        parse_notes.append(
            "final_label_format_repaired: "
            f"{raw_decision.final_label!r} -> {repair_trace.final_label!r}"
        )
        format_decision = raw_decision.model_copy(
            update={
                "final_label": repair_trace.final_label,
                "attribution": "llm_selected_format_repaired",
            }
        )
    return format_decision, repair_events, parse_notes


def _render_fresh_action(
    raw_fresh: FreshEvidenceDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    *,
    note_text: str,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    if raw_fresh.action == "keep_original_structured_event_final":
        decision, error = _render_keep_original_action(
            format_decision,
            structured_event_row,
        )
        if error:
            return None, [], [error]
        return (
            decision,
            ["fresh_evidence_action_rendered:keep_original_structured_event_final"],
            [],
        )

    original_reference = llm_event_reasoner._v0_reference(structured_event_row)
    render_notes: list[str] = []
    safety_reason = _fresh_evidence_safety_gate_reason(
        raw_fresh,
        format_decision,
        original_reference=original_reference,
    )
    if safety_reason is not None:
        unknown_fallback_reason = _original_no_reference_should_fallback_to_unknown_reason(
            raw_fresh,
            original_reference=original_reference,
        )
        if unknown_fallback_reason is None:
            return _fallback_to_original(
                format_decision,
                structured_event_row,
                safety_reason,
            )
        format_decision = format_decision.model_copy(
            update={
                "final_label": "unknown",
                "final_kind": "unknown",
                "attribution": "llm_selected_format_repaired",
            }
        )
        render_notes.extend([safety_reason, unknown_fallback_reason])

    unknown_repair_reason = _no_reference_should_be_unknown_reason(
        raw_fresh,
        format_decision,
    )
    if unknown_repair_reason is not None:
        format_decision = format_decision.model_copy(
            update={
                "final_label": "unknown",
                "final_kind": "unknown",
                "attribution": "llm_selected_format_repaired",
            }
        )
        render_notes.append(unknown_repair_reason)
    try:
        label_to_frequency_record(format_decision.final_label)
    except ValueError as exc:
        return _fallback_to_original(
            format_decision,
            structured_event_row,
            f"fresh_evidence_gate_fallback: unscorable_fresh_label: {exc}",
        )
    exact_evidence = tuple(
        evidence
        for evidence in format_decision.evidence
        if evidence_is_substring(note_text, evidence)
    )
    if not exact_evidence:
        return _fallback_to_original(
            format_decision,
            structured_event_row,
            "fresh_evidence_gate_fallback: evidence_not_exact",
        )
    if exact_evidence != format_decision.evidence:
        format_decision = format_decision.model_copy(update={"evidence": exact_evidence})
        render_notes.append("fresh_evidence_shape_repaired:filtered_non_exact_evidence")
    if not format_decision.selected_event_ids:
        format_decision = format_decision.model_copy(
            update={"selected_event_ids": ("fresh_evidence_1",)}
        )
        render_notes.append("fresh_evidence_shape_repaired:selected_event_ids")
    return (
        format_decision,
        [
            *render_notes,
            "fresh_evidence_action_rendered:replace_with_fresh_evidence_final",
        ],
        [],
    )


def _fallback_to_original(
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
    reason: str,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    decision, error = _render_keep_original_action(
        format_decision,
        structured_event_row,
    )
    if error:
        return None, [], [error]
    return (
        decision,
        [reason, "fresh_evidence_action_rendered:fallback_original_structured_event_final"],
        [reason],
    )


def _render_keep_original_action(
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None]:
    selection = _structured_selection(structured_event_row)
    label = _as_optional_str(selection.get("final_label"))
    if label is None:
        return None, "action_render_error: missing_original_final_label"
    try:
        label_record = label_to_frequency_record(label)
    except ValueError as exc:
        return None, f"action_render_error: original_final_label_unscorable: {exc}"
    selected_ids = _string_tuple(selection.get("selected_event_ids"))
    evidence = _evidence_tuple(selection.get("evidence")) or format_decision.evidence
    return (
        format_decision.model_copy(
            update={
                "final_label": label_record.normalized_label,
                "final_kind": str(label_record.kind),
                "selected_event_ids": selected_ids,
                "evidence": evidence,
                "attribution": "llm_original_structured_event_kept",
            }
        ),
        None,
    )


def _structured_selection(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {}
    record = dict(structured_event_row.get("structured_record") or {})
    return dict(record.get("selection") or {})


def _evidence_tuple(value: Any) -> tuple[str, ...]:
    return tuple(item for item in _string_tuple(value) if item)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _fresh_evidence_safety_gate_reason(
    raw_fresh: FreshEvidenceDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    *,
    original_reference: Mapping[str, Any],
) -> str | None:
    raw_label = raw_fresh.final_label.strip().lower()
    if raw_fresh.final_kind == "seizure_free" and raw_label == "seizure free":
        return "fresh_evidence_gate_fallback: bare_seizure_free_replacement"

    original_kind = str(original_reference.get("final_kind") or "")
    original_label = str(original_reference.get("final_label") or "")
    original_is_boundary_state = original_kind in {"unknown", "no_reference"} or (
        original_label.strip().lower() in {"unknown", "no seizure frequency reference"}
    )
    if _is_open_ended_treatment_start_denominator(raw_fresh) and original_is_boundary_state:
        return "fresh_evidence_gate_fallback: open_ended_treatment_start_denominator"
    if _is_seizure_free_replacement_of_frequency_original(raw_fresh, original_label):
        return "fresh_evidence_gate_fallback: seizure_free_replacement_of_frequency_original"
    if _is_vague_multiple_exactification(raw_fresh, original_label):
        return "fresh_evidence_gate_fallback: vague_multiple_exactification"
    if _is_same_day_cluster_downgrade(raw_fresh, original_label):
        return "fresh_evidence_gate_fallback: same_day_cluster_downgrade"
    original_is_seizure_free = (
        original_kind == "seizure_free" or original_label.strip().lower().startswith("seizure free")
    )
    replacement_is_boundary_state = format_decision.final_kind in {
        "unknown",
        "no_reference",
    }
    selective_unknown_boundary = _is_selective_unknown_frequency_boundary(raw_fresh)
    if (
        original_is_seizure_free
        and replacement_is_boundary_state
        and not selective_unknown_boundary
    ):
        return "fresh_evidence_gate_fallback: original_seizure_free_to_unknown_or_no_reference"
    if format_decision.final_kind == "unknown" and not selective_unknown_boundary:
        return "fresh_evidence_gate_fallback: unknown_replacement_not_selective"
    if raw_fresh.final_kind == "seizure_free" and original_kind == "frequency":
        decision_text = " ".join(
            (
                raw_label,
                raw_fresh.calculation_trace or "",
                raw_fresh.clinical_rationale,
                " ".join(raw_fresh.evidence),
            )
        ).lower()
        short_last_event_boundary = (
            "week" in decision_text
            or "for 1 month" in decision_text
            or "for one month" in decision_text
        )
        if short_last_event_boundary:
            return (
                "fresh_evidence_gate_fallback: "
                "short_seizure_free_replacement_from_frequency_original"
            )
    if format_decision.final_label.strip().lower().startswith("multiple per"):
        decision_text = " ".join(
            (
                raw_label,
                raw_fresh.calculation_trace or "",
                raw_fresh.clinical_rationale,
                " ".join(raw_fresh.evidence),
            )
        ).lower()
        explicit_numeric_boundary = (
            "twice per" in decision_text
            or "<=2 per" in decision_text
            or "<= 2 per" in decision_text
            or "≤2 per" in decision_text
            or "≤ 2 per" in decision_text
        )
        if explicit_numeric_boundary:
            return "fresh_evidence_gate_fallback: multiple_label_for_explicit_numeric_frequency"
    return None


def _no_reference_should_be_unknown_reason(
    raw_fresh: FreshEvidenceDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
) -> str | None:
    """Preserve the unknown/no-reference semantic boundary.

    Gan scoring collapses both labels, but the annotation rule does not: when
    the note contains seizure evidence and either count or period is unclear,
    the safer semantic label is ``unknown``, not ``no seizure frequency
    reference``.
    """

    if format_decision.final_kind != "no_reference":
        return None
    decision_text = _fresh_decision_text(raw_fresh)
    if _decision_text_supports_unknown_frequency(decision_text):
        return "fresh_evidence_semantic_repaired:no_reference_to_unknown"
    return None


def _original_no_reference_should_fallback_to_unknown_reason(
    raw_fresh: FreshEvidenceDecision,
    *,
    original_reference: Mapping[str, Any],
) -> str | None:
    original_kind = str(original_reference.get("final_kind") or "")
    original_label = str(original_reference.get("final_label") or "").strip().lower()
    if original_kind != "no_reference" and original_label != "no seizure frequency reference":
        return None
    decision_text = _fresh_decision_text(raw_fresh)
    if _decision_text_supports_unknown_frequency(decision_text):
        return "fresh_evidence_semantic_repaired:original_no_reference_to_unknown"
    return None


def _fresh_decision_text(raw_fresh: FreshEvidenceDecision) -> str:
    return " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            raw_fresh.ambiguity_classification or "",
            " ".join(raw_fresh.boundary_profile),
            " ".join(raw_fresh.evidence),
        )
    ).lower()


def _decision_text_supports_unknown_frequency(decision_text: str) -> bool:
    absence_of_frequency_evidence = (
        "no seizure frequency evidence" in decision_text
        or "absence of seizure frequency evidence" in decision_text
        or "no seizure frequency information" in decision_text
        or "no clinical data" in decision_text
        or "diagnosis only" in decision_text
        or "administrative" in decision_text
    )
    if absence_of_frequency_evidence:
        return False
    seizure_evidence_present = any(
        token in decision_text
        for token in (
            "seizure",
            "seizures",
            "event",
            "events",
            "attack",
            "attacks",
            "drop",
            "tonic-clonic",
            "myoclonic",
            "convulsion",
            "convulsive",
            "absence",
            "cluster",
        )
    )
    unclear_count_or_window = any(
        token in decision_text
        for token in (
            "unknown",
            "unclear",
            "not fully specified",
            "not specified",
            "cannot calculate",
            "cannot be converted",
            "cannot determine",
            "no explicit count",
            "no explicit denominator",
            "no defined period",
            "no defined window",
            "no time window",
            "last-event-only",
            "last event only",
            "last seizure date",
            "most recent seizure",
            "since starting",
            "since beginning",
            "since commencing",
        )
    )
    if seizure_evidence_present and unclear_count_or_window:
        return True
    return False


def _is_selective_last_event_unknown_boundary(raw_fresh: FreshEvidenceDecision) -> bool:
    if raw_fresh.final_kind != "unknown":
        return False
    decision_text_without_profiles = " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            " ".join(raw_fresh.evidence),
        )
    ).lower()
    has_last_event_evidence = (
        "last seizure on" in decision_text_without_profiles
        or "last seizure was" in decision_text_without_profiles
        or "last seizure occurred" in decision_text_without_profiles
        or "last event on" in decision_text_without_profiles
        or "last event was" in decision_text_without_profiles
        or "last cluster was" in decision_text_without_profiles
        or "most recent seizure on" in decision_text_without_profiles
    )
    has_no_since_boundary = (
        "no seizures since" in decision_text_without_profiles
        or "no-seizures-since" in decision_text_without_profiles
    )
    return has_last_event_evidence and has_no_since_boundary


def _is_selective_unknown_frequency_boundary(raw_fresh: FreshEvidenceDecision) -> bool:
    if raw_fresh.final_kind != "unknown":
        return False
    # v0.10 confidence gate: triage emitted a high-confidence specific reason.
    if raw_fresh.triage_result is not None:
        triage_reason = raw_fresh.triage_result.triage_reason
        if triage_reason in CONFIDENCE_GATED_UNKNOWN_DEMOTION_REASONS:
            return True
        # Low-confidence or rendering-only triage reasons must NOT demote.
        if triage_reason not in (None,):
            # triage was evaluated but did not emit a confidence-gated reason;
            # fall through to the ambiguity_classification check.
            pass
    if raw_fresh.ambiguity_classification in {
        "unknown_count_or_window",
        "last_event_only_unknown",
        "cluster_axis_incomplete",
    }:
        return True
    return _is_selective_last_event_unknown_boundary(raw_fresh)


def _is_open_ended_treatment_start_denominator(raw_fresh: FreshEvidenceDecision) -> bool:
    if raw_fresh.final_kind != "frequency":
        return False
    decision_text = " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            " ".join(raw_fresh.boundary_profile),
            " ".join(raw_fresh.evidence),
        )
    ).lower()
    has_since_treatment_start = (
        "since beginning" in decision_text
        or "since starting" in decision_text
        or "since commencing" in decision_text
        or "since commenced" in decision_text
    )
    has_treatment_anchor = any(
        token in decision_text
        for token in (
            "clobazam",
            "ketogenic diet",
            "medication",
            "treatment",
            "topiramate",
            "drug",
        )
    )
    has_usable_followup_exception = any(
        token in decision_text
        for token in (
            "remission",
            "follow-up period",
            "follow up period",
            "no seizures since",
            "no further seizures",
            "no further events",
            "soon afterwards",
        )
    )
    return has_since_treatment_start and has_treatment_anchor and not has_usable_followup_exception


def _is_seizure_free_replacement_of_frequency_original(
    raw_fresh: FreshEvidenceDecision,
    original_label: str,
) -> bool:
    if raw_fresh.final_kind != "seizure_free":
        return False
    original_label_lower = original_label.strip().lower()
    original_label_is_frequency = (
        original_label_lower
        and original_label_lower not in {"unknown", "no seizure frequency reference"}
        and not original_label_lower.startswith("seizure free")
    )
    if not original_label_is_frequency:
        return False
    decision_text = " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            " ".join(raw_fresh.boundary_profile),
            " ".join(raw_fresh.evidence),
        )
    ).lower()
    return "historical frequency" in decision_text


def _is_vague_multiple_exactification(
    raw_fresh: FreshEvidenceDecision,
    original_label: str,
) -> bool:
    if raw_fresh.final_kind != "frequency":
        return False
    original_label_lower = original_label.strip().lower()
    if not original_label_lower.startswith("multiple per "):
        return False
    final_label_lower = raw_fresh.final_label.strip().lower()
    if "multiple per " in final_label_lower:
        return False
    decision_text = " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            " ".join(raw_fresh.boundary_profile),
            " ".join(raw_fresh.evidence),
        )
    ).lower()
    vague_quantifier_present = any(
        token in decision_text
        for token in (
            "a few",
            "few events",
            "couple of",
            "several",
        )
    )
    exactified_vague_count = any(
        token in decision_text
        for token in (
            "3-5",
            "3 to 5",
            "5-7",
            "5 to 7",
        )
    )
    return vague_quantifier_present and exactified_vague_count


def _is_same_day_cluster_downgrade(
    raw_fresh: FreshEvidenceDecision,
    original_label: str,
) -> bool:
    if raw_fresh.final_kind != "frequency":
        return False
    original_label_lower = original_label.strip().lower()
    final_label_lower = raw_fresh.final_label.strip().lower()
    if " per day" not in original_label_lower or " per day" in final_label_lower:
        return False
    decision_text = " ".join(
        (
            raw_fresh.final_label,
            raw_fresh.calculation_trace or "",
            raw_fresh.clinical_rationale,
            " ".join(raw_fresh.boundary_profile),
            " ".join(raw_fresh.evidence),
        )
    ).lower()
    has_same_day_cluster = (
        "yesterday" in decision_text or "today" in decision_text or "single day" in decision_text
    ) and any(
        token in decision_text
        for token in (
            "cluster",
            "tonic-clonic seizures",
            "seizures in 1 day",
            "seizures yesterday",
        )
    )
    rejects_daily_rate = any(
        token in decision_text
        for token in (
            "not a recurring daily rate",
            "no evidence that this is a recurring daily rate",
            "for that day only",
            "should not be extrapolated to a daily rate",
        )
    )
    return has_same_day_cluster and rejects_daily_rate
