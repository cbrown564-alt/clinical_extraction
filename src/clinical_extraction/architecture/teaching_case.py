"""Executable teaching cases: one Gan letter and one ExECT letter, all methods.

Every observation in a teaching case is produced by running the real selected
implementation. Nothing here is hand-written prose about what the code *would*
do. Two things are fixtures rather than live output:

* the letters are synthetic, written for this file;
* the raw model outputs are fixtures standing in for one model call.

Both are labelled as such in the generated document. Everything downstream of
the model boundary - repair, normalization, selection resolution, family
transforms, gates, scoring - is the real code path, so a teaching case cannot
drift from the pipeline without this module failing.

Building a teaching case makes no model calls and reads no locked rows.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from clinical_extraction.architecture.stage_manifest import MethodManifest, load_manifest

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

GAN_LETTER_ID = "TEACH-GAN-01"
GAN_NOTE_TEXT = (
    "Epilepsy clinic letter, 14 March 2026.\n"
    "\n"
    "I reviewed Mr A in the epilepsy clinic today. His typical pattern is a "
    "focal seizure monthly, and that remains the case. He has had seven "
    "seizures so far this year. He continues on levetiracetam 500mg twice "
    "daily and reports no side effects. MRI brain was normal."
)
# The Gan gold convention prefers a stated typical recurring rate over a
# year-to-date total. See policy A1 in the clinical selection policy catalog.
GAN_GOLD_LABEL = "1 per month"

# Fixture standing in for one LLM-with-rules structured call. The model
# extracts both statements as events and selects the year-to-date total - the
# mistake the deterministic repair layer exists to catch.
GAN_HYBRID_RAW_OUTPUT = json.dumps(
    {
        "events": [
            {
                "event_id": "evt_1",
                "kind": "frequency_rate",
                "raw_value": "a focal seizure monthly",
                "applies_to": "focal seizures",
                "time_window": "typical",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "His typical pattern is a focal seizure monthly",
                "notes": "stated usual pattern",
            },
            {
                "event_id": "evt_2",
                "kind": "frequency_rate",
                "raw_value": "seven seizures so far this year",
                "applies_to": "all seizures",
                "time_window": "2026 year to date",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "He has had seven seizures so far this year",
                "notes": "year-to-date observation total",
            },
        ],
        "selection": {
            "selected_event_ids": ["evt_2"],
            "final_kind": "frequency",
            "final_label": "7 per year",
            "evidence": "He has had seven seizures so far this year",
            "confidence": "medium",
            "rationale": (
                "The counted total so far this year is the most concrete "
                "figure in the letter."
            ),
        },
    }
)

# Fixture standing in for one LLM-only decision call. The model reaches the
# same wrong answer, and this method has no repair family that can catch it.
GAN_LLM_ONLY_RAW_OUTPUT = json.dumps(
    {
        "final_label": "7 per year",
        "evidence": "He has had seven seizures so far this year",
        "answer_kind": "frequency",
        "selected_seizure_type": "all seizures",
        "time_window": "2026 year to date",
        "applied_rule_families": ["observation_window_total"],
        "confidence": "medium",
        "rationale": (
            "The counted total so far this year is the most concrete figure "
            "in the letter."
        ),
    }
)

EXECT_LETTER_ID = "TEACH-EXECT-01"
EXECT_NOTE_TEXT = (
    "Epilepsy clinic letter, 14 March 2026.\n"
    "\n"
    "Diagnosis: focal epilepsy.\n"
    "\n"
    "Mr B has been seizure free since March 2025. MRI brain was normal. "
    "He continues on levetiracetam 500mg twice daily."
)

# Fixture standing in for one four-family structured call.
EXECT_HYBRID_RAW_OUTPUT = json.dumps(
    {
        "clinical_events": [
            {
                "family": "diagnosis",
                "anchor_text": "focal epilepsy",
                "evidence": "Diagnosis: focal epilepsy",
                "event_state": {},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "focal epilepsy",
                        "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"},
                    }
                ],
                "confidence": "high",
                "rationale": "stated under the diagnosis heading",
            },
            {
                # The model states the seizure-free fact and supplies the
                # seizure count, but not the elapsed-window attributes. The
                # deterministic projection stage is what completes the scored
                # state representation.
                "family": "seizure_frequency",
                "anchor_text": "seizure free since March 2025",
                "evidence": "Mr B has been seizure free since March 2025",
                "event_state": {},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "seizures",
                        "attributes": {"NumberOfSeizures": "0"},
                    }
                ],
                "confidence": "high",
                "rationale": "explicit seizure-free statement",
            },
            {
                "family": "investigation",
                "anchor_text": "MRI brain",
                "evidence": "MRI brain was normal",
                "event_state": {},
                "mentions": [
                    {
                        "entity": "Investigations",
                        "text": "MRI",
                        "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    }
                ],
                "confidence": "high",
                "rationale": "investigation with a stated result",
            },
            {
                "family": "medication",
                "anchor_text": "levetiracetam 500mg twice daily",
                "evidence": "He continues on levetiracetam 500mg twice daily",
                "event_state": {},
                "mentions": [
                    {
                        "entity": "Prescription",
                        "text": "levetiracetam",
                        "attributes": {
                            "DrugName": "levetiracetam",
                            "DrugDose": "500",
                            "DoseUnit": "mg",
                            "Frequency": "2",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "current regimen",
            },
        ]
    }
)

# Fixture standing in for one GEPA LLM-only program output.
EXECT_LLM_ONLY_RAW_OUTPUT = json.dumps(
    {
        "clinical_facts": [
            {
                "family": "diagnosis",
                "concept": "focal epilepsy",
                "evidence": "Diagnosis: focal epilepsy",
                "negation": "affirmed",
            },
            {
                "family": "seizure_frequency",
                "seizure_type": "seizures",
                "state": "seizure_free",
                "evidence": "Mr B has been seizure free since March 2025",
            },
            {
                "family": "investigations",
                "evidence": "MRI brain was normal",
                "modality": "MRI",
                "performed": "yes",
                "result": "normal",
            },
            {
                # dose_unit and frequency are written the way a model writes
                # them, so the adapter's representation normalization is
                # visible in the teaching case rather than assumed.
                "family": "prescription",
                "source_text": "levetiracetam 500mg twice daily",
                "evidence": "He continues on levetiracetam 500mg twice daily",
                "drug": "levetiracetam",
                "dose": "500",
                "dose_unit": "milligrams",
                "frequency": "twice a day",
            },
        ]
    }
)


# --------------------------------------------------------------------------
# Observation records
# --------------------------------------------------------------------------


@dataclass
class StageObservation:
    """What one stage actually did to this letter."""

    stage_id: str
    stage_name: str
    owner: str
    effect_class: str
    input_value: Any
    output_value: Any
    changed: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "owner": self.owner,
            "effect_class": self.effect_class,
            "input": _render(self.input_value),
            "output": _render(self.output_value),
            "changed": self.changed,
            "note": self.note,
        }


@dataclass
class MethodRun:
    """One method's pass over one teaching letter."""

    method_id: str
    manifest: MethodManifest
    observations: list[StageObservation] = field(default_factory=list)
    final_answer: str = ""
    correct: bool | None = None
    correctness_note: str = ""

    def record(
        self,
        stage_id: str,
        *,
        input_value: Any,
        output_value: Any,
        changed: bool | None = None,
        note: str = "",
    ) -> None:
        stage = self.manifest.stage(stage_id)
        self.observations.append(
            StageObservation(
                stage_id=stage.stage_id,
                stage_name=stage.name,
                owner=stage.owner,
                effect_class=stage.effect_class,
                input_value=input_value,
                output_value=output_value,
                changed=(
                    changed
                    if changed is not None
                    else _render(input_value) != _render(output_value)
                ),
                note=note,
            )
        )

    @property
    def changing_stages(self) -> list[StageObservation]:
        return [obs for obs in self.observations if obs.changed]

    def to_dict(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "method_label": self.manifest.method_label,
            "one_sentence": self.manifest.one_sentence,
            "prediction_owner": self.manifest.prediction_owner,
            "final_answer": self.final_answer,
            "correct": self.correct,
            "correctness_note": self.correctness_note,
            "observations": [obs.to_dict() for obs in self.observations],
        }


@dataclass
class TeachingCase:
    """One letter through all three methods of one task."""

    case_id: str
    task: str
    task_label: str
    letter_id: str
    note_text: str
    gold: str
    gold_note: str
    fixture_note: str
    runs: list[MethodRun] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "task": self.task,
            "task_label": self.task_label,
            "letter_id": self.letter_id,
            "note_text": self.note_text,
            "gold": self.gold,
            "gold_note": self.gold_note,
            "fixture_note": self.fixture_note,
            "runs": [run.to_dict() for run in self.runs],
        }


def _render(value: Any) -> str:
    if value is None:
        return "(none)"
    if isinstance(value, str):
        return value
    if isinstance(value, bool | int | float):
        return str(value)
    try:
        return json.dumps(_jsonable(value), sort_keys=True, default=str)
    except (TypeError, ValueError):
        return str(value)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, str | bytes):
        return value if isinstance(value, str) else value.decode("utf-8", "replace")
    if isinstance(value, Sequence):
        return [_jsonable(item) for item in value]
    return value


# --------------------------------------------------------------------------
# Gan teaching case
# --------------------------------------------------------------------------


def _gan_gold_monthly_frequency() -> float:
    """Take the gold monthly rate from the label parser, not from a literal."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )

    return label_to_frequency_record(GAN_GOLD_LABEL).monthly_frequency


def _gan_record() -> Any:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

    gold = label_to_frequency_record(GAN_GOLD_LABEL)
    return GanFrequencyRecord(
        source_row_index=1,
        note_text=GAN_NOTE_TEXT,
        gold_label=GAN_GOLD_LABEL,
        gold_reference="His typical pattern is a focal seizure monthly",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=GAN_GOLD_LABEL,
        gold_label_kind=gold.kind,
        gold_yearly_bounds=gold.yearly_bounds,
        gold_monthly_frequency=gold.monthly_frequency,
    )


def _gan_scoring(run: MethodRun, stage_id: str, final_label: str | None) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
        map_pragmatic,
        map_purist,
    )

    gold_monthly = _gan_gold_monthly_frequency()
    gold_purist = str(map_purist(gold_monthly))
    gold_pragmatic = str(map_pragmatic(gold_monthly))
    if not final_label:
        run.final_answer = "(no scorable label)"
        run.correct = False
        run.correctness_note = "No label reached the scorer."
        run.record(
            stage_id,
            input_value="(no scorable label)",
            output_value=f"gold purist {gold_purist}; no prediction",
            changed=True,
        )
        return
    predicted = label_to_frequency_record(final_label)
    predicted_purist = str(map_purist(predicted.monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
    run.final_answer = final_label
    run.correct = predicted_purist == gold_purist
    run.correctness_note = (
        f"purist predicted {predicted_purist} vs gold {gold_purist}; "
        f"pragmatic predicted {predicted_pragmatic} vs gold {gold_pragmatic}"
    )
    run.record(
        stage_id,
        input_value=f"label {final_label} (monthly {predicted.monthly_frequency})",
        output_value=(
            f"purist {predicted_purist} vs gold {gold_purist}; "
            f"pragmatic {predicted_pragmatic} vs gold {gold_pragmatic}"
        ),
        changed=True,
        note="The scorer turns one label into two categorical verdicts.",
    )


def _gan_rules_only_run() -> MethodRun:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic_canonical,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
        PipelineConfiguration,
    )

    manifest = load_manifest("gan2026_rules_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    result = deterministic_canonical.run_item(
        _gan_record(),
        PipelineConfiguration(architecture="rules"),
    )
    diagnostics = result.diagnostics

    candidates = diagnostics["candidate_events"]
    run.record(
        "gan.rules.extract",
        input_value=GAN_NOTE_TEXT,
        output_value=[_event_summary(event) for event in candidates],
        changed=True,
        note=f"{len(candidates)} candidate event(s) matched by the rules.",
    )
    normalized = diagnostics["normalized_events"]
    run.record(
        "gan.rules.normalize",
        input_value=[_event_summary(event) for event in candidates],
        output_value=[_normalized_summary(event) for event in normalized],
        note="Representation only: the candidate list is unchanged in length.",
    )
    selection = diagnostics["final_selection"]
    run.record(
        "gan.rules.select_and_render",
        input_value=[_normalized_summary(event) for event in normalized],
        output_value=(
            f"selected {selection.get('selected_event_ids')} -> "
            f"{selection.get('final_label')}"
        ),
        changed=True,
        note="The rules own this choice. Nothing before it made a selection.",
    )
    run.record(
        "gan.rules.evidence_trace_check",
        input_value=selection.get("evidence"),
        output_value=f"evidence_valid={diagnostics['evidence_valid']}",
        changed=False,
        note="A gate: it accepts or rejects, it does not rewrite the answer.",
    )
    _gan_scoring(run, "gan.rules.score", result.output.final_value)
    return run


def _gan_llm_only_run() -> MethodRun:
    from clinical_extraction.core.evidence import evidence_is_substring
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm as pipeline,
    )

    manifest = load_manifest("gan2026_llm_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    record = _gan_record()

    prompt_input = pipeline.build_prompt_input(record)
    run.record(
        "gan.llm.build_prompt",
        input_value=GAN_NOTE_TEXT,
        output_value=f"prompt input of {len(prompt_input)} characters",
        changed=True,
        note="Transport only.",
    )
    run.record(
        "gan.llm.model_call",
        input_value="prompt input (fixture: no model call is made)",
        output_value=GAN_LLM_ONLY_RAW_OUTPUT,
        changed=True,
        note="Fixture boundary. Everything after this line is real code.",
    )

    decision, errors, trace = pipeline.parse_decision_json_with_trace(
        GAN_LLM_ONLY_RAW_OUTPUT
    )
    run.record(
        "gan.llm.json_schema_repair",
        input_value=GAN_LLM_ONLY_RAW_OUTPUT,
        output_value=trace["format_repair"],
        changed=bool(trace["format_repair"]["schema_payload_changed"]),
        note="This fixture is already well formed, so nothing is repaired.",
    )
    model_record = trace["model_prediction"]["record"]
    run.record(
        "gan.llm.schema_validation",
        input_value="repaired payload",
        output_value=("validated" if model_record else "schema_validation_error"),
        changed=False,
    )
    adapter = trace["deterministic_adapter"]
    run.record(
        "gan.llm.selected_evidence_repair",
        input_value=adapter["before_label"],
        output_value=adapter["after_label"],
        changed=adapter["before_label"] != adapter["after_label"],
        note=(
            "The one deterministic stage in this method that may change the "
            "clinical answer. Here the model's label already agrees with the "
            "span it quoted, so it does not fire - and nothing else in this "
            "method can catch the selection error."
        ),
    )
    final_label = decision.final_label if decision else None
    run.record(
        "gan.llm.scorable_label_check",
        input_value=final_label,
        output_value=(
            "unscorable"
            if any(str(err).startswith("unscorable_final_label") for err in errors)
            else "scorable"
        ),
        changed=False,
    )
    evidence_valid = (
        evidence_is_substring(GAN_NOTE_TEXT, decision.evidence) if decision else False
    )
    run.record(
        "gan.llm.evidence_containment",
        input_value=decision.evidence if decision else None,
        output_value=f"evidence_valid={evidence_valid}",
        changed=False,
    )
    _gan_scoring(run, "gan.llm.score", final_label)
    return run


def _gan_llm_with_rules_run() -> MethodRun:
    from clinical_extraction.core.evidence import evidence_is_substring
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as hybrid,
    )

    manifest = load_manifest("gan2026_llm_with_rules")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    record = _gan_record()
    repair_config = hybrid.StructuredRepairConfig.for_mode("hybrid_full_stack")

    prompt_input = hybrid.build_prompt_input(record)
    run.record(
        "gan.hybrid.build_prompt",
        input_value=GAN_NOTE_TEXT,
        output_value=f"prompt input of {len(prompt_input)} characters",
        changed=True,
        note="Transport only.",
    )
    run.record(
        "gan.hybrid.model_call",
        input_value="prompt input (fixture: no model call is made)",
        output_value=GAN_HYBRID_RAW_OUTPUT,
        changed=True,
        note=(
            "Fixture boundary. Note what the model returned: two events AND a "
            "selection. The selection is the model's, not a rule's."
        ),
    )

    extraction, normalized_events, errors, trace = hybrid.parse_structured_json_with_trace(
        GAN_HYBRID_RAW_OUTPUT,
        note_text=GAN_NOTE_TEXT,
        repair_config=repair_config,
    )
    run.record(
        "gan.hybrid.json_schema_repair",
        input_value=GAN_HYBRID_RAW_OUTPUT,
        output_value=trace["format_repair"],
        changed=bool(trace["format_repair"]["schema_payload_changed"]),
        note="This fixture is already well formed, so nothing is repaired.",
    )
    run.record(
        "gan.hybrid.format_only_retry",
        input_value="(not eligible: hosted model, first parse succeeded)",
        output_value="(not run)",
        changed=False,
        note="Conditional stage. Fires only for local ollama-served models.",
    )
    run.record(
        "gan.hybrid.schema_validation",
        input_value="repaired payload",
        output_value=("validated" if extraction else "schema_validation_error"),
        changed=False,
    )
    run.record(
        "gan.hybrid.normalize_events",
        input_value=[
            _event_summary(event) for event in trace["model_prediction"]["record"]["events"]
        ],
        output_value=[_normalized_summary(event) for event in normalized_events],
        changed=True,
        note="Every event is normalized, not only the selected one.",
    )

    selection_block = trace["deterministic_selection"]
    run.record(
        "gan.hybrid.resolve_label",
        input_value=(
            f"model selected {selection_block['selected_event_ids']} with "
            f"final_label {selection_block['model_final_label']!r}"
        ),
        output_value=selection_block["resolved_label"],
        changed=True,
        note=(
            "Rendering the model's choice, not re-choosing. The selected "
            "event id came from the model."
        ),
    )

    final_label = (
        extraction.selection.final_label if extraction and extraction.selection else None
    )
    semantic = trace["deterministic_semantic"]
    model_extraction = hybrid.StructuredExtractionRecord.model_validate(
        trace["model_prediction"]["record"]
    )
    walk = _gan_repair_walk(
        model_extraction,
        semantic["before_label"],
        note_text=GAN_NOTE_TEXT,
        repair_config=repair_config,
        expected_final_label=final_label,
    )
    for (family, before, after) in walk:
        run.record(
            f"gan.hybrid.repair.{family}",
            input_value=before,
            output_value=after,
            changed=before != after,
            note=(
                "fired on this letter"
                if before != after
                else "did not fire on this letter"
            ),
        )
    run.record(
        "gan.hybrid.scorable_label_check",
        input_value=final_label,
        output_value=(
            "unscorable"
            if any(str(err).startswith("unscorable_final_label") for err in errors)
            else "scorable"
        ),
        changed=False,
    )
    evidence = extraction.selection.evidence if extraction else ""
    evidence_valid = evidence_is_substring(GAN_NOTE_TEXT, evidence) if evidence else False
    run.record(
        "gan.hybrid.evidence_containment",
        input_value=evidence,
        output_value=f"evidence_valid={evidence_valid}",
        changed=False,
        note=(
            "The evidence checked is the model's original selection evidence. "
            "A repair can change the label without changing this span."
        ),
    )
    _gan_scoring(run, "gan.hybrid.score", final_label)
    return run


class RepairAttributionError(AssertionError):
    """The per-family walk did not reproduce the pipeline's own final label."""


def _gan_repair_walk(
    model_extraction: Any,
    resolved_label: str,
    *,
    note_text: str,
    repair_config: Any,
    expected_final_label: str | None,
) -> list[tuple[str, str, str]]:
    """Attribute each label change to the repair family that actually made it.

    The pipeline records repair events in a flat list, so the family that fired
    cannot be read off the trace. Rather than guess - which is how the
    misleading syn_014 teaching fixture went wrong - this walks the same repair
    families in the same order, calling the same functions on the same
    pre-repair extraction, and then checks that it lands on the label the
    pipeline itself produced. If the two disagree, this raises instead of
    publishing an invented attribution.

    Returns one (family, before, after) triple per repair stage.
    """

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as hybrid,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_structured_repair_families as families,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_monthly_diary import (  # noqa: E501
        monthly_diary_label_from_events,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
        repair_prediction_label_with_evidence,
    )

    label = resolved_label
    walk: list[tuple[str, str, str]] = []

    def step(family: str, candidate: str | None) -> None:
        nonlocal label
        before = label
        after = candidate if candidate else before
        walk.append((family, before, after))
        label = after

    step(
        "selected_evidence",
        repair_prediction_label_with_evidence(
            label, model_extraction.selection.evidence, context_text=note_text
        )
        if repair_config.selected_evidence_repair
        else None,
    )

    diary_label = (
        monthly_diary_label_from_events(model_extraction, note_text=note_text)
        if repair_config.monthly_diary_repair
        else None
    )
    if diary_label and hybrid._should_preserve_label_from_monthly_diary(
        label, extraction=model_extraction
    ):
        diary_label = None
    step("monthly_diary", diary_label)

    step(
        "usual_interval",
        families.usual_interval_label_from_events(model_extraction, label)
        if repair_config.usual_interval_repair
        else None,
    )
    step(
        "typical_over_ytd",
        families.typical_recurring_rate_over_ytd_from_events(model_extraction, label),
    )
    step(
        "breakthrough",
        families.breakthrough_label_from_events(model_extraction, label)
        if repair_config.breakthrough_repair
        else None,
    )
    step(
        "non_epileptic",
        families.non_epileptic_label_from_events(model_extraction, label)
        if repair_config.non_epileptic_repair
        else None,
    )
    step(
        "residual_jerk",
        families.residual_jerk_label_from_events(
            model_extraction, label, note_text=note_text
        )
        if repair_config.residual_jerk_repair
        else None,
    )
    step(
        "post_change_burst",
        families.post_change_burst_label_from_events(
            model_extraction, label, note_text=note_text
        )
        if repair_config.post_change_burst_repair
        else None,
    )
    step(
        "dated_sequence",
        families.dated_sequence_label_from_events(
            model_extraction, label, note_text=note_text
        )
        if repair_config.dated_sequence_repair
        else None,
    )
    elapsed_label = (
        families.elapsed_since_anchor_label_from_events(
            model_extraction, label, note_text=note_text
        )
        if repair_config.elapsed_anchor_repair
        else None
    )
    if elapsed_label and hybrid._should_preserve_sustained_selected_seizure_free(
        model_extraction, label, elapsed_label
    ):
        elapsed_label = None
    step("elapsed_anchor", elapsed_label)

    if expected_final_label is not None and label != expected_final_label:
        raise RepairAttributionError(
            "per-family repair walk produced "
            f"{label!r} but the pipeline produced {expected_final_label!r}; "
            "the teaching case will not publish an attribution it cannot "
            "reproduce"
        )
    return walk


def _event_summary(event: Any) -> str:
    data = _jsonable(event)
    if not isinstance(data, Mapping):
        return str(data)
    identifier = data.get("event_id") or data.get("candidate_id") or "?"
    value = data.get("raw_value") or data.get("evidence") or data.get("source_phrase") or ""
    return f"{identifier}: {value}"


def _normalized_summary(event: Any) -> str:
    data = _jsonable(event)
    if not isinstance(data, Mapping):
        return str(data)
    identifier = data.get("event_id") or data.get("candidate_id") or "?"
    return (
        f"{identifier}: {data.get('normalized_label')} "
        f"(monthly {data.get('monthly_frequency')})"
    )


def build_gan_case() -> TeachingCase:
    case = TeachingCase(
        case_id="gan2026_typical_rate_over_year_to_date",
        task="gan2026",
        task_label="Gan 2026",
        letter_id=GAN_LETTER_ID,
        note_text=GAN_NOTE_TEXT,
        gold=GAN_GOLD_LABEL,
        gold_note=(
            "The Gan gold convention prefers a stated typical recurring rate "
            "over a year-to-date total (policy A1 in the clinical selection "
            "policy catalog). A reader who expects the counted total to win "
            "will read every result on this letter backwards."
        ),
        fixture_note=(
            "The letter is synthetic and the raw model outputs are fixtures "
            "standing in for one model call each. No model call is made when "
            "this case is built. Every stage after the model boundary is the "
            "real selected implementation."
        ),
    )
    case.runs = [
        _gan_rules_only_run(),
        _gan_llm_only_run(),
        _gan_llm_with_rules_run(),
    ]
    return case


# --------------------------------------------------------------------------
# ExECT teaching case
# --------------------------------------------------------------------------


def _exect_letter() -> Any:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

    return ExectLetter(letter_id=EXECT_LETTER_ID, note_text=EXECT_NOTE_TEXT)


def _mention_summary(mention: Any) -> str:
    data = _jsonable(mention)
    if not isinstance(data, Mapping):
        return str(data)
    attributes = data.get("attributes") or {}
    rendered = ", ".join(f"{key}={value}" for key, value in sorted(attributes.items()))
    suffix = f" [{rendered}]" if rendered else ""
    return f"{data.get('entity')}: {data.get('text')}{suffix}"


def _fact_summary(fact: Any) -> str:
    data = _jsonable(fact)
    if not isinstance(data, Mapping):
        return str(data)
    body = ", ".join(
        f"{key}={value}"
        for key, value in sorted(data.items())
        if key not in {"family", "evidence", "attributes"} and value
    )
    return f"{data.get('family')}: {body}"


def _exect_rules_only_run() -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        rules,
    )

    manifest = load_manifest("exectv2_rules_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = _exect_letter()

    result = rules.run_letter(letter)
    for event in result.stage_events[:3]:
        run.record(
            event.stage_id,
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            note=(
                "Nine independent extractors. This baseline covers nine entities "
                "while the model-led comparison covers four."
                if event.stage_id == "exect.rules.extract_entities"
                else "Canonical rules-only stage."
            ),
        )
    _exect_scoring(run, "exect.rules.score", result.prediction.mentions, nine_entity=True)
    return run


def _exect_llm_only_run() -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    manifest = load_manifest("exectv2_llm_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = _exect_letter()

    producer = structured_one_call.produce_structured_letter(
        letter,
        mode="prompt-only",
        raw_output=EXECT_HYBRID_RAW_OUTPUT,
        config=StructuredMethodConfig.selected(),
    )
    result = structured_one_call.run_llm_only_letter(letter, producer)
    for event in result.stage_events:
        if event.stage_id == "exect.llm.score":
            continue
        run.record(
            event.stage_id,
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            note=(
                "Fixture boundary at the one-call producer; downstream stages "
                "are the selected implementation."
                if event.stage_id == "exect.llm.model_call"
                else "Canonical LLM-only stage."
            ),
        )
    _exect_scoring(run, "exect.llm.score", result.prediction.mentions, nine_entity=False)
    return run


def _exect_llm_with_rules_run() -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    manifest = load_manifest("exectv2_llm_with_rules")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = _exect_letter()

    producer = structured_one_call.produce_structured_letter(
        letter,
        mode="prompt-only",
        raw_output=EXECT_HYBRID_RAW_OUTPUT,
        config=StructuredMethodConfig.selected(),
    )
    result = structured_one_call.run_llm_with_rules_letter(
        letter,
        producer,
        config=StructuredMethodConfig.selected(),
    )
    for event in result.stage_events:
        if event.stage_id == "exect.hybrid.score":
            continue
        run.record(
            event.stage_id,
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            note=(
                "Fixture boundary at the one-call producer; no live model call "
                "is made."
                if event.stage_id == "exect.hybrid.model_call"
                else "Canonical LLM-with-rules stage."
            ),
        )
    _exect_scoring(
        run,
        "exect.hybrid.score",
        result.prediction.mentions,
        nine_entity=False,
    )
    return run


def _structured_row(letter: Any, predicted: Any, gate_warnings: Any) -> dict[str, Any]:
    return {
        "letter_id": letter.letter_id,
        "split": "teaching_case",
        "prompt_version": "teaching_case",
        "pipeline_family": "exectv2_teaching_case_single_call",
        "model": "(fixture)",
        "mode": "fixture",
        "component_owner": "single_model_structured",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": list(gate_warnings),
        "predicted_mentions": [
            _jsonable(mention) for mention in predicted.mentions
        ],
        "n_mentions_raw": len(predicted.mentions),
        "n_mentions_scored": len(predicted.mentions),
        "n_evidence_invalid": 0,
        "raw_output": EXECT_HYBRID_RAW_OUTPUT,
        "gold_mentions": [],
    }


def _exect_scoring(
    run: MethodRun, stage_id: str, mentions: Sequence[Any], *, nine_entity: bool
) -> None:
    by_entity: dict[str, int] = {}
    for mention in mentions:
        data = _jsonable(mention)
        entity = str(data.get("entity")) if isinstance(data, Mapping) else "?"
        by_entity[entity] = by_entity.get(entity, 0) + 1
    coverage = "nine entities" if nine_entity else "four families"
    run.final_answer = ", ".join(
        f"{entity} x{count}" for entity, count in sorted(by_entity.items())
    )
    run.correct = None
    run.correctness_note = (
        f"This teaching letter carries no gold annotations, so no correctness "
        f"verdict is claimed. The comparable unit is {coverage}."
    )
    run.record(
        stage_id,
        input_value=f"{len(mentions)} finding(s) over {coverage}",
        output_value=by_entity,
        changed=True,
        note=(
            "Scored against gold in a real run. Here the point is the "
            f"comparison boundary: this method is scored over {coverage}."
        ),
    )


def build_exect_case() -> TeachingCase:
    case = TeachingCase(
        case_id="exectv2_four_family_ordinary_letter",
        task="exectv2",
        task_label="ExECTv2",
        letter_id=EXECT_LETTER_ID,
        note_text=EXECT_NOTE_TEXT,
        gold="(no gold annotations; this is a synthetic teaching letter)",
        gold_note=(
            "This case teaches the shape of the pipeline and the comparison "
            "boundary, not accuracy. The rules-only baseline answers over nine "
            "entities; the two model-led methods answer over four families. "
            "Their overall numbers are not interchangeable."
        ),
        fixture_note=(
            "The letter is synthetic and the raw model outputs are fixtures "
            "standing in for one model call each. No model call is made when "
            "this case is built. Every stage after the model boundary is the "
            "real selected implementation."
        ),
    )
    case.runs = [
        _exect_rules_only_run(),
        _exect_llm_only_run(),
        _exect_llm_with_rules_run(),
    ]
    return case


def build_all_cases() -> tuple[TeachingCase, ...]:
    return (build_gan_case(), build_exect_case())
