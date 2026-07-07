"""LLM-only direct-labeler Gan 2026 seizure-frequency extraction experiments."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)

PROMPT_VERSION_V0_5 = "gan2026_llm_only_direct_labeler_v0.5"
PROMPT_VERSION_V0_6 = "gan2026_llm_only_direct_labeler_v0.6"
PROMPT_VERSION_V0_7 = "gan2026_llm_only_direct_labeler_v0.7"
# Active prompt version. Default stays v0.5 so existing drivers are unchanged.
# Cycle-2 evidence-presentation experiments select v0.6 via set_active_prompt_version.
# Cycle-3 label-binding experiments select v0.7 (v0.6 scaffold + sharpened STEP 4
# + a label-binding repair keyed on the model's own emitted answer_kind/rationale).
PROMPT_VERSION = PROMPT_VERSION_V0_5
_SUPPORTED_PROMPT_VERSIONS = frozenset(
    {PROMPT_VERSION_V0_5, PROMPT_VERSION_V0_6, PROMPT_VERSION_V0_7}
)


def set_active_prompt_version(version: str) -> None:
    """Gate which prompt version build_prompt_input/run_split emit (additive).

    v0.5 is the frozen baseline; v0.6 adds a structured triage scaffold to the
    evidence the model attends to; v0.7 keeps that scaffold (with a sharpened
    seizure-free-vs-one-off STEP 4) and additionally binds the emitted
    final_label to the model's own emitted answer_kind/rationale. Switching the
    module-level constant keeps the change minimal and self-contained: scoring,
    gold normalization, and the emitted JSON schema are untouched.
    """

    global PROMPT_VERSION
    if version not in _SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {version!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)}"
        )
    PROMPT_VERSION = version


PROMPT_POLICY_TAXONOMY: list[dict[str, str]] = [
    {
        "policy_id": "dl_v0.schema.strict_json_object",
        "controlled_variable": "prompt_strict_json_object_policy",
        "portability": "general",
        "status": "active",
        "description": "Prompt requires exactly one JSON object with no markdown wrapper.",
    },
    {
        "policy_id": "dl_v0.output.direct_label",
        "controlled_variable": "direct_label_extraction_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt extracts a single final label directly from the note without "
            "intermediate event structures or candidate generation."
        ),
    },
    {
        "policy_id": "dl_v0.evidence.exact_substring",
        "controlled_variable": "prompt_exact_evidence_substring_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": "Prompt requires evidence to be copied as an exact source substring.",
    },
    {
        "policy_id": "dl_v0.boundary.unknown_no_reference_seizure_free",
        "controlled_variable": "prompt_boundary_answer_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt instructs separation of unknown, no seizure frequency reference, "
            "and seizure-free answers."
        ),
    },
    {
        "policy_id": "dl_v0.selection.current_burden_precedence",
        "controlled_variable": "prompt_current_burden_selection_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": (
            "Prompt selects the highest current or recent seizure burden across types."
        ),
    },
]
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_direct_labeler_validation_gpt41mini_2026-05-31.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_direct_labeler_validation_gpt41mini_2026-05-31.md"
)


class LlmOnlyDirectLabelerDecisionRecord(BaseModel):
    """Traceable note-to-label decision emitted by the LLM-only direct-labeler extractor."""

    model_config = ConfigDict(extra="forbid")

    final_label: str
    evidence: str
    answer_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_seizure_type: str | None = None
    time_window: str | None = None
    confidence: Literal["low", "medium", "high"]
    rationale: str


class Gan2026LlmOnlyDirectLabelerExtractorSignature(dspy.Signature):
    """Extract the Gan 2026 seizure-frequency answer directly from one note.

    Return exactly one JSON object with these keys: final_label, evidence,
    answer_kind, selected_seizure_type, time_window, confidence, and rationale.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output fields."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object. final_label must be a normalized label such as "
            "'2 per month', '2 to 3 per week', 'multiple per day', "
            "'seizure free for multiple month', 'unknown', or "
            "'no seizure frequency reference'."
        )
    )


class DspyLlmOnlyDirectLabelerExtractor(dspy.Module):
    """DSPy note-to-label extractor with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026LlmOnlyDirectLabelerExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _v0_5_instructions() -> list[str]:
    return [
        "Read the full clinical note and extract the current seizure-frequency answer.",
        (
            "Return final_label as one normalized string using count, range, or "
            "multiple over a day/week/month/year denominator; seizure-free duration; "
            "unknown; or no seizure frequency reference."
        ),
        (
            "Allowed frequency forms include 1 per day, "
            "2 to 3 per month, multiple per week, 1 cluster per week, 2 to 3 per cluster, "
            "seizure free for 6 month, unknown, no seizure frequency reference."
        ),
        (
            "When a note contains counts across multiple time windows, prefer the most "
            "recent window's rate as the primary label — for example, if the note reports "
            "six events over the year and two in the most recent month, the label is "
            "'2 per month'."
        ),
        (
            "When multiple seizure types are present, select the type with the highest "
            "frequency as the label — rank by how often events occur (events per day, "
            "per week, or per month), not by clinical severity. Daily drop attacks or "
            "daily absences take precedence over weekly or monthly tonic-clonic seizures. "
            "Exception: when events occur in a cluster pattern (grouped multi-event "
            "episodes separated by seizure-free intervals, recurring every few days or "
            "weeks), label using the cluster cadence — not the per-episode daily burst "
            "rate. Events within a single cluster day are not the same as daily ongoing "
            "events."
        ),
        (
            "Plural daily seizures/events should map to multiple per day unless the note "
            "clearly says exactly one per day."
        ),
        (
            "Use unknown when seizures or seizure-like events are discussed but current "
            "frequency cannot be converted to a normalized rate."
        ),
        (
            "Use no seizure frequency reference only when the note contains no usable "
            "seizure-frequency evidence."
        ),
        (
            "Use seizure-free only when the note asserts no seizures/events for a current "
            "duration; do not use seizure-free for a single semiology if other current "
            "seizure-like events remain."
        ),
        (
            "If the note describes a seizure burst (multiple events in a short recent "
            "period) followed by a seizure-free run, the label is the burst frequency — "
            "not the ensuing seizure-free duration. A seizure-free label is appropriate "
            "only when the absence of seizures is the note's primary clinical statement, "
            "not when a recent burst ended and no further events have since occurred."
        ),
        (
            "If seizures are described only as occurring within a conditional window "
            "(perimenstrual, sleep-deprived, missed medication, situational triggers), "
            "do not report the outside-window seizure-free duration as the overall "
            "current frequency — use unknown unless the note gives an unconditional "
            "current rate. A single event reported as 'N weeks ago' or 'N occasions "
            "since [date]' describes a total count in an observation window, not a "
            "recurrent rate — use unknown for these constructions unless the note "
            "explicitly states the events recur at that rate."
        ),
        (
            "For cluster labels, include both cluster rate and events per cluster when both "
            "are stated; use 'multiple per cluster' when the per-cluster count is described "
            "approximately (e.g., 'about five', 'several'). If the note states how often "
            "clusters occur (e.g., 'clusters every 3-4 weeks', 'cluster days four to five "
            "times per week'), that cadence is a usable frequency even when per-cluster "
            "count is unknown — use the cadence as the label and 'multiple per cluster' "
            "unless the count is stated. Drop attacks, status epilepticus episodes, "
            "myoclonic jerks, absence episodes, and behavioural arrest events all count "
            "as seizure events for frequency purposes."
        ),
        (
            "answer_kind must be written as exactly one of these five "
            "words, with no other wording: 'frequency' (the note gives a "
            "usable current seizure-frequency rate or range), "
            "'seizure_free' (the note describes a current seizure-free "
            "duration instead of a rate), 'unknown' (seizures are "
            "discussed but the current frequency cannot be converted to "
            "a normalized rate), 'no_reference' (the note contains no "
            "usable seizure-frequency evidence at all), or "
            "'unresolved_multiple' (several current seizure-frequency "
            "claims conflict and none can be picked as the answer). Do "
            "not write a longer description in this field — choose "
            "exactly one of the five words above."
        ),
        "Evidence must be an exact substring from the note when possible.",
        (
            "confidence describes how certain you are about the answer based on "
            "what the note contains: "
            "'low' when two or more current seizure-frequency facts compete and "
            "none clearly dominates, or when the frequency is only a vague range "
            "with no time window at all; "
            "'medium' when one fact is clearly dominant but some ambiguity remains "
            "— for example, events are only described as conditional on a trigger, "
            "the count is vague but a time window is clear, or only a relative "
            "trend is given with no stated rate; "
            "'high' when there is exactly one unambiguous current fact, no "
            "competing claims, and the evidence can be quoted directly from the note."
        ),
        (
            "Write rationale as one short, plain-language sentence stating "
            "only the deciding evidence and label — for example: 'The note "
            "states two seizures per month for the current period, so the "
            "label is 2 per month.' Do not show step-by-step reasoning, "
            "alternative options you considered and rejected, or "
            "self-questioning; state only the final justification."
        ),
        (
            "Before writing your final_label, verify that the rate described in your "
            "rationale matches it: if your rationale names a concrete frequency, your "
            "final_label must not be 'unknown' or 'no seizure frequency reference'."
        ),
        "Return exactly one JSON object with no markdown.",
    ]


def _v0_6_instructions() -> list[str]:
    """Cycle-2 evidence-presentation scaffold (additive over v0.5).

    Forces a four-finding triage of the reported events BEFORE the label is
    emitted, and binds each finding to a labelling consequence. The emitted JSON
    schema is unchanged; the scaffold lives in the instructions only, so scoring
    and normalization are untouched.
    """

    return [
        "Read the full clinical note and extract the current seizure-frequency answer.",
        (
            "Before choosing a label, work through this four-step triage of the "
            "reported events. The triage decides whether a count establishes a "
            "habitual rate or whether the safer answer is 'unknown'. When the count "
            "OR the time window is unclear, 'unknown' is safer than inventing a rate."
        ),
        (
            "STEP 1 confound_check — Are the reported events tied to a removable "
            "provoking, situational, or adherence factor: missed meals / going a "
            "long time without eating; sleep deprivation, broken nights, jet lag, "
            "long-haul travel, or circadian/body-clock disruption; alcohol; or a "
            "medication-supply gap, running out of medication, or non-adherence? If "
            "YES, the count does NOT establish a habitual baseline -> final_label is "
            "'unknown'. A note that says events stop when the trigger is removed "
            "(e.g. 'no events when eating/sleeping normally') is the provoked "
            "pattern -> 'unknown'."
        ),
        (
            "STEP 2 window_check — Is the observation window the patient's usual, "
            "ongoing habitual baseline, or is it: a transient exacerbation, 'rough "
            "patch', 'bad fortnight', or recent 'period of decline'; a new or "
            "uncertain seizure classification with work-up pending (EEG/EMU "
            "awaited, '?epilepsy', 'TBC'); or a single recent event / a total count "
            "since a date that is NOT stated to recur at that rate? If the window is "
            "NOT a usable habitual baseline -> final_label is 'unknown'. Only a "
            "stable, ongoing, unprovoked pattern over a defined period is a usable "
            "rate."
        ),
        (
            "STEP 3 cluster_check — Do the events arrive in clusters: runs or "
            "groupings of several events over consecutive days, separated by "
            "seizure-free gaps, recurring every few days or weeks? If YES, label "
            "with the CLUSTER CADENCE, e.g. '1 cluster per 3 week, multiple per "
            "cluster' (use 'multiple per cluster' when the per-cluster count is not "
            "logged or only approximate). NEVER flatten a cluster to the per-burst "
            "daily rate (do not call it 'multiple per day'), and NEVER collapse it "
            "to 'unknown' merely because the per-cluster count is unstated — the "
            "cluster recurrence cadence IS a usable frequency. A single isolated "
            "event recurring at an interval, with no grouping, is a plain rate, not "
            "a cluster."
        ),
        (
            "STEP 4 seizure_free_check — Does the note ASSERT a continuous "
            "seizure-free interval ('free of all seizures for N months', 'no events "
            "whatsoever for N months', witness-confirmed)? That is a seizure-free "
            "duration -> 'seizure free for N month'. But if the note gives only a "
            "LAST-EVENT date ('last seizure ~N months ago', 'most recent event in "
            "May') with no asserted interval, or follow-up is incomplete/unobserved "
            "since, you CANNOT assert a seizure-free duration -> final_label is "
            "'unknown' (NOT seizure-free, NOT a rate)."
        ),
        (
            "PRECEDENCE: if STEP 1 confound_check or STEP 2 window_check fails, "
            "'unknown' wins over any apparent count or rate. Otherwise, if STEP 3 "
            "finds a cluster pattern, use the cluster cadence. Otherwise, if STEP 4 "
            "finds an asserted seizure-free interval, use the seizure-free duration. "
            "Otherwise — when all four checks are clean (unprovoked, stable habitual "
            "window, no clusters, no seizure-free assertion) and the note states a "
            "count over a window or an explicit rate — emit that rate. Do NOT "
            "over-withhold: a clean, stable, unprovoked count or rate (e.g. 'about 2 "
            "seizures a month for several months, no triggers, adherence fine') IS a "
            "usable rate and must NOT be forced to 'unknown'."
        ),
        (
            "Return final_label as one normalized string using count, range, or "
            "multiple over a day/week/month/year denominator; seizure-free duration; "
            "unknown; or no seizure frequency reference."
        ),
        (
            "Allowed frequency forms include 1 per day, "
            "2 to 3 per month, multiple per week, 1 cluster per week, 2 to 3 per cluster, "
            "seizure free for 6 month, unknown, no seizure frequency reference."
        ),
        (
            "When a note contains counts across multiple time windows that are all "
            "part of the same stable habitual pattern, prefer the most recent "
            "window's rate as the primary label — for example, six events over the "
            "year and two in the most recent month gives '2 per month'. (This only "
            "applies after the triage above clears the count as a habitual rate.)"
        ),
        (
            "When multiple seizure types are present, select the type with the highest "
            "frequency as the label — rank by how often events occur (events per day, "
            "per week, or per month), not by clinical severity. Daily drop attacks or "
            "daily absences take precedence over weekly or monthly tonic-clonic seizures. "
            "Exception: cluster patterns are labelled by the cluster cadence per STEP 3, "
            "not the per-episode daily burst rate."
        ),
        (
            "Plural daily seizures/events should map to multiple per day unless the note "
            "clearly says exactly one per day. Drop attacks, status epilepticus episodes, "
            "myoclonic jerks, absence episodes, and behavioural arrest events all count "
            "as seizure events for frequency purposes."
        ),
        (
            "Use no seizure frequency reference only when the note contains no usable "
            "seizure-frequency evidence at all (no seizures or seizure-like events "
            "discussed). When seizures ARE discussed but no rate can be established "
            "(per the triage), use unknown, not no seizure frequency reference."
        ),
        (
            "For cluster labels, include both cluster rate and events per cluster when both "
            "are stated; use 'multiple per cluster' when the per-cluster count is described "
            "approximately or is not logged. If the note states how often clusters occur, "
            "that cadence is a usable frequency even when the per-cluster count is unknown."
        ),
        (
            "answer_kind must be written as exactly one of these five "
            "words, with no other wording: 'frequency' (the note gives a "
            "usable current seizure-frequency rate or range), "
            "'seizure_free' (the note asserts a current seizure-free "
            "duration instead of a rate), 'unknown' (seizures are "
            "discussed but the current frequency cannot be converted to "
            "a normalized rate — including provoked, transient, adherence-"
            "confounded, last-event-only, or descriptive-only notes), "
            "'no_reference' (the note contains no usable seizure-frequency "
            "evidence at all), or 'unresolved_multiple' (several current "
            "seizure-frequency claims conflict and none can be picked). Do "
            "not write a longer description in this field."
        ),
        "Evidence must be an exact substring from the note when possible.",
        (
            "confidence describes how certain you are about the answer based on "
            "what the note contains: 'low' when two or more current "
            "seizure-frequency facts compete and none clearly dominates, or when "
            "the frequency is only a vague range with no time window; 'medium' when "
            "one fact is clearly dominant but some ambiguity remains; 'high' when "
            "there is exactly one unambiguous current fact, no competing claims, and "
            "the evidence can be quoted directly from the note."
        ),
        (
            "Write rationale as one short, plain-language sentence stating only the "
            "deciding triage finding and label — for example: 'The two events were "
            "provoked by missed meals, so no habitual rate is established and the "
            "label is unknown.' Do not show step-by-step reasoning or alternatives "
            "you rejected; state only the final justification."
        ),
        (
            "Consistency check: if your rationale concludes the count is provoked, "
            "transient, adherence-confounded, last-event-only, or descriptive-only, "
            "final_label must be 'unknown' (or the seizure-free duration only if a "
            "continuous interval is asserted). If your rationale names a concrete "
            "habitual frequency, final_label must not be 'unknown'."
        ),
        "Return exactly one JSON object with no markdown.",
    ]


def _v0_7_instructions() -> list[str]:
    """Cycle-3 label-binding scaffold (additive over v0.6).

    Identical to v0.6 except STEP 4 (seizure-free vs one-off) and the closing
    consistency check are sharpened so a single past event with no asserted
    ongoing seizure-free interval is 'unknown', not a seizure-free duration. The
    deterministic label-binding repair (see _apply_v0_7_label_binding) is what
    forces final_label to agree with the emitted answer_kind/rationale; this
    instruction set only re-forms the seizure-free finding the repair cannot key
    on. The emitted JSON schema is unchanged.
    """

    instructions = _v0_6_instructions()
    # Sharpen STEP 4: a one-off past event is NOT a seizure-free interval.
    for idx, text in enumerate(instructions):
        if text.startswith("STEP 4 seizure_free_check"):
            instructions[idx] = (
                "STEP 4 seizure_free_check — Does the note ASSERT a CONTINUOUS, "
                "ONGOING interval free of ALL seizure-like events ('free of all "
                "seizures for N months', 'no events whatsoever for N months', "
                "witness-confirmed and still ongoing)? Only that is a seizure-free "
                "duration -> 'seizure free for N month'. A SINGLE recent or past "
                "event — e.g. 'one short spell a fortnight ago', 'the first event "
                "of its kind for many months', 'last seizure ~N months ago' — does "
                "NOT establish a seizure-free interval: it is a last-event-only / "
                "single-event history, and the absence of events BEFORE that one "
                "event is not a witnessed ongoing seizure-free period. When the "
                "only evidence is a single isolated event or a last-event date with "
                "no asserted ongoing all-clear interval, answer_kind is 'unknown' "
                "and final_label is 'unknown' (NOT seizure-free, NOT a rate)."
            )
        elif text.startswith("Consistency check:"):
            instructions[idx] = (
                "Consistency check: final_label MUST agree with answer_kind. If "
                "answer_kind is 'unknown' (count provoked, transient, "
                "adherence-confounded, last-event-only, single isolated event, or "
                "descriptive-only), final_label must be 'unknown'. If answer_kind "
                "is 'no_reference', final_label must be 'no seizure frequency "
                "reference'. If your rationale names a recurring CLUSTER pattern, "
                "final_label must be the cluster cadence form ('1 cluster per N "
                "week, multiple per cluster'), never a flattened daily burst rate "
                "or a single-event interval. If your rationale names a concrete "
                "habitual frequency, final_label must be that rate and not "
                "'unknown'. Only assert 'seizure free for N month' when a "
                "continuous ongoing all-clear interval is explicitly asserted, not "
                "for a single past event."
            )
    return instructions


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the LLM-only direct-labeler prompt payload, excluding gold labels.

    The active prompt version (set via set_active_prompt_version) selects the
    instruction set. v0.5 is the frozen baseline; v0.6 adds the Cycle-2 triage
    scaffold. The JSON output schema and allowed fields are identical across
    versions, so scoring and normalization are unaffected.
    """

    if PROMPT_VERSION == PROMPT_VERSION_V0_7:
        instructions = _v0_7_instructions()
    elif PROMPT_VERSION == PROMPT_VERSION_V0_6:
        instructions = _v0_6_instructions()
    else:
        instructions = _v0_5_instructions()
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency LLM-only direct-labeler extraction",
        "source_row_index": record.source_row_index,
        "instructions": instructions,
        "allowed_decision_fields": [
            "final_label",
            "evidence",
            "answer_kind",
            "selected_seizure_type",
            "time_window",
            "confidence",
            "rationale",
        ],
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_decision_json(
    raw_output: str,
) -> tuple[LlmOnlyDirectLabelerDecisionRecord | None, list[str]]:
    errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            _extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    errors.extend(dialect_notes)
    payload = _filter_decision_payload(repair_decision_payload(raw_payload))

    try:
        decision = LlmOnlyDirectLabelerDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    binding_locked = False
    if PROMPT_VERSION == PROMPT_VERSION_V0_7:
        bound_label, binding_note, binding_locked = _apply_v0_7_label_binding(decision)
        if bound_label != decision.final_label:
            errors.append(binding_note)
            decision = decision.model_copy(update={"final_label": bound_label})

    # When the v0.7 binding has locked the label to the model's own verdict
    # (a no-rate answer_kind, or a cluster cadence it described), the evidence-
    # substring repair must NOT resurrect a rate from the note text — that is
    # exactly the contradiction the binding exists to remove. Only the format
    # normalizer is still applied so the locked label stays scorer-ready.
    if binding_locked:
        repaired_label = repair_prediction_label_format_preserving(decision.final_label)
        # The format-preserving repair deliberately leaves vague quantities
        # untouched, so a locked label may still be unscorable. Never let that
        # break scoring: fall back to the full evidence repair (the same path
        # v0.5/v0.6 use) only when the locked label cannot be scored.
        if not _is_scorable_label(repaired_label):
            repaired_label = repair_prediction_label_with_evidence(
                decision.final_label,
                decision.evidence,
            )
    else:
        repaired_label = repair_prediction_label_with_evidence(
            decision.final_label,
            decision.evidence,
        )
    if repaired_label != decision.final_label:
        errors.append(f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}")
        decision = decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors


def _filter_decision_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of direct-labeler validation."""

    if not isinstance(payload, dict):
        return payload
    allowed = set(LlmOnlyDirectLabelerDecisionRecord.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


# --- v0.7 label-binding repair --------------------------------------------
# Cycle-3: bind the emitted final_label to the model's OWN emitted structured
# reasoning (answer_kind / rationale / time_window / evidence). Keyed purely on
# the model's output; never on gold, row index, or saved-row behaviour. Active
# only when PROMPT_VERSION == v0.7 (additive; v0.5/v0.6 paths are untouched).

_NO_RATE_ANSWER_KINDS = {
    "unknown": "unknown",
    "unresolved_multiple": "unknown",
    "no_reference": "no seizure frequency reference",
}

_NUMBER_WORDS = {
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
}

_CLUSTER_TOKEN = re.compile(
    r"\b(clusters?|runs?|groupings?|group(?:s|ed)?\s+together|arriv\w+\s+in\s+runs)\b",
    re.IGNORECASE,
)
_CLUSTER_RECURRENCE = re.compile(
    r"\b(recur\w*|every|come?\s+round|coming\s+round|round\s+again|repeat\w*)\b",
    re.IGNORECASE,
)
_CLUSTER_NEGATION = re.compile(
    r"\b(no|not|without|never)\b[^.]{0,30}\b(cluster\w*|group\w*|run\b|runs\b)\b",
    re.IGNORECASE,
)
_ALREADY_CLUSTER = re.compile(r"\bcluster\b", re.IGNORECASE)
_WINDOW_UNIT = re.compile(
    r"(?P<lo>\d+|" + "|".join(_NUMBER_WORDS) + r")"
    r"(?:\s*(?:to|-|–|—|or)\s*(?P<hi>\d+|" + "|".join(_NUMBER_WORDS) + r"))?"
    r"\s*(?P<unit>day|week|month|year)s?",
    re.IGNORECASE,
)


def _is_scorable_label(label: str) -> bool:
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True


def _word_to_int(token: str) -> int | None:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _NUMBER_WORDS.get(token)


def _parse_recurrence_window(*texts: str | None) -> str | None:
    """Pull a 'N' or 'N to M <unit>' window from the model's own emitted text.

    Prefers an interval introduced by a recurrence cue ('every', 'recur',
    'round') so we capture the cluster cadence rather than an incidental count.
    Returns a parser-ready window like '4 to 5 week' or '3 week', or None.
    """

    for text in texts:
        if not text:
            continue
        # Prefer a window that follows a recurrence cue within the same clause.
        cue = _CLUSTER_RECURRENCE.search(text)
        search_spans: list[str] = []
        if cue:
            search_spans.append(text[cue.start() :])
        search_spans.append(text)
        for span in search_spans:
            match = _WINDOW_UNIT.search(span)
            if not match:
                continue
            lo = _word_to_int(match.group("lo"))
            if lo is None:
                continue
            unit = match.group("unit").lower()
            hi_raw = match.group("hi")
            hi = _word_to_int(hi_raw) if hi_raw else None
            if hi is not None and hi != lo:
                return f"{lo} to {hi} {unit}"
            return f"{lo} {unit}"
    return None


def _is_cluster_reasoning(rationale: str, evidence: str) -> bool:
    blob = f"{rationale} {evidence}"
    if not _CLUSTER_TOKEN.search(blob):
        return False
    if _CLUSTER_NEGATION.search(blob):
        return False
    return bool(_CLUSTER_RECURRENCE.search(blob))


def _apply_v0_7_label_binding(
    decision: LlmOnlyDirectLabelerDecisionRecord,
) -> tuple[str, str, bool]:
    """Bind final_label to the model's own answer_kind / rationale.

    Returns (possibly-rewritten label, note, locked). ``locked`` is True when the
    label has been pinned to the model's own verdict and must not be re-derived
    from the evidence substring by the downstream repair (the contradiction this
    binding exists to remove). Note is only meaningful when the label changed.
    Two rules, in precedence order:
      1. answer_kind in {unknown, unresolved_multiple, no_reference} -> coerce AND
         lock (so the evidence repair cannot resurrect a rate from the note).
      2. answer_kind == frequency with cluster reasoning + a flattened label ->
         render the cluster cadence form AND lock.
    The seizure_free->unknown one-off finding is handled by the sharpened v0.7
    STEP-4 prompt (the model re-forms answer_kind), not here.
    """

    label = decision.final_label
    answer_kind = decision.answer_kind
    rationale = decision.rationale or ""
    evidence = decision.evidence or ""

    # Rule 1: coerce-to-no-rate when the model's own verdict carries no rate.
    # Lock unconditionally for these answer_kinds: even when the model already
    # emitted the right label, the evidence repair would otherwise rewrite it.
    target = _NO_RATE_ANSWER_KINDS.get(answer_kind)
    if target is not None:
        if label.strip().lower() != target:
            return (
                target,
                (
                    f"v0_7_binding_coerce_no_rate: answer_kind={answer_kind!r} "
                    f"-> {target!r} (was {label!r})"
                ),
                True,
            )
        return label, "", True

    # Rule 2: cluster-cadence render when the model formed a cluster finding.
    if answer_kind == "frequency":
        if _ALREADY_CLUSTER.search(label):
            # The model already emitted a cluster cadence; lock it so the
            # evidence-substring repair cannot flatten it back to a burst/plain
            # rate (e.g. 'multiple per day'). No relabel needed.
            return label, "", True
        if _is_cluster_reasoning(rationale, evidence):
            window = _parse_recurrence_window(decision.time_window, rationale, evidence)
            if window:
                cluster_label = f"1 cluster per {window}, multiple per cluster"
                return (
                    cluster_label,
                    (
                        f"v0_7_binding_cluster_render: cluster reasoning -> "
                        f"{cluster_label!r} (was {label!r})"
                    ),
                    True,
                )

    return label, "", False


# --------------------------------------------------------------------------


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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
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
    program = DspyLlmOnlyDirectLabelerExtractor()
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
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.decision_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        decision, parse_errors = (
            parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
        )
        evidence_valid = (
            evidence_is_substring(record.note_text, decision.evidence)
            if decision and decision.evidence
            else False
        )
        comparison = _compare_to_gold(record, decision) if decision else None
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "evidence_valid": evidence_valid,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
                "comparison": comparison,
            }
        )
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


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    decision_rows = [row for row in rows if row.get("decision_record")]
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    reused_raw_outputs = sum(bool(row.get("reused_raw_output")) for row in rows)
    parse_failures = sum(_has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    repair_notes = sum(_has_repair_note(row.get("parse_errors")) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    evidence_valid = sum(bool(row.get("evidence_valid")) for row in rows)
    final_labels = Counter(
        row["decision_record"]["final_label"] for row in rows if row.get("decision_record")
    )
    return {
        "examples": len(rows),
        "decision_records": len(decision_rows),
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "repair_notes": repair_notes,
        "evidence_valid": evidence_valid,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior JSONL artifact."""

    return load_raw_outputs_by_source_index(path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 LLM-First Validation Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a final "
        "holdout or benchmark result.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan "
        "seizure-frequency interpretation, while deterministic code is limited to label "
        "repair, evidence validation, and scoring.",
        "",
        "Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 "
        "candidate diagnostics are provided to the model.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Rare full-validation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Rare full-validation reason: not applicable for this run size."
        ),
        "Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a "
        "side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role="LLM-only direct-labeler note-to-label extractor",
            deterministic_rule_configuration=(
                "none before prediction; deterministic code only repairs labels, "
                "validates evidence, and scores."
            ),
            summary=summary,
        ),
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        f"- Exact evidence substrings: {summary['evidence_valid']} / {summary['examples']}",
        f"- Purist validation accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic validation accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Rows",
        "",
        "| Row | Final | Gold | Purist | Notes |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        decision = row.get("decision_record") or {}
        comparison = row.get("comparison") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        if not row.get("evidence_valid"):
            evidence_note = "evidence_not_exact_substring"
            notes = f"{notes}; {evidence_note}" if notes else evidence_note
        lines.append(
            f"| {row['source_row_index']} | {decision.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: LlmOnlyDirectLabelerDecisionRecord,
) -> dict[str, Any]:
    predicted_record = label_to_frequency_record(decision.final_label)
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


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "unscorable_final_label:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _has_repair_note(errors: Any) -> bool:
    return any(str(error).startswith("final_label_repaired:") for error in errors or [])


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


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
    )
