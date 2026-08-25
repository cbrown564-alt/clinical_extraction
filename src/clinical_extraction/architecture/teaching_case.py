"""Executable teaching cases: one canonical Gan letter, a Gan letter library,
and one ExECT letter, all methods.

Every observation in a teaching case is produced by running the real selected
implementation. Nothing here is hand-written prose about what the code *would*
do. Two things are fixtures rather than live output:

* the letters are synthetic, written for this file;
* the raw model outputs are fixtures standing in for one model call.

Both are labelled as such in the generated document. Everything downstream of
the model boundary - repair, normalization, selection resolution, family
transforms, gates, scoring - is the real code path, so a teaching case cannot
drift from the pipeline without this module failing.

``build_all_cases()`` returns the synthetic pair used by vertical-slice
tests. ``build_teaching_letters()`` returns the four paper flagship
letters (G1, G3, E1, E2) for the explainer and the generated architecture
teaching documents. The Gan letter library remains available separately.

Building a teaching case makes no model calls and reads no locked rows.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from clinical_extraction.architecture.fact_lineage import (
    GoldUnit,
    PredictedFact,
    attach_run_gold,
    build_exect_facts,
    build_gan_hybrid_facts,
    build_gan_llm_facts,
    build_gan_rules_facts,
    empty_gold_unit,
)
from clinical_extraction.architecture.stage_manifest import MethodManifest, load_manifest
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GanCaseSpec:
    """Everything one synthetic Gan teaching letter needs: text, gold, and
    the two fixture model outputs. All pipeline behaviour below the model
    boundary is executed, never scripted. The prose fields teach *about* the
    fixture and are versioned with it; they never describe pipeline behaviour
    the runs do not demonstrate."""

    case_id: str
    letter_id: str
    note_text: str
    gold: str
    gold_reference: str
    gold_note: str
    story: str
    card_why: dict[str, str]
    mechanism_title: str
    mechanism: str
    hybrid_raw_output: str
    llm_only_raw_output: str
    source_row_index: int = 1
    fixture_note: str | None = None
    extract_label_forms_raw: str = ""
    pre_post_label_forms_raw: str = ""
    select_from_extract_raw: str = ""


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

GAN_SPEC = GanCaseSpec(
    case_id="gan2026_typical_rate_over_year_to_date",
    letter_id=GAN_LETTER_ID,
    note_text=GAN_NOTE_TEXT,
    gold=GAN_GOLD_LABEL,
    gold_reference="His typical pattern is a focal seizure monthly",
    gold_note=(
        "The Gan gold convention prefers a stated typical recurring rate "
        "over a year-to-date total (policy A1 in the clinical selection "
        "policy catalog). A reader who expects the counted total to win "
        "will read every result on this letter backwards."
    ),
    story=(
        "The model prefers the concrete year-to-date count over the stated "
        "typical pattern, and one deterministic repair family rewrites it."
    ),
    card_why={
        "rules": (
            "Code finds every seizure-frequency statement, normalizes it, "
            "and applies the convention directly. No model involved."
        ),
        "llm": (
            "The model prefers the concrete counted total. It is a plausible "
            "reading - and this method has no later stage allowed to overrule "
            "the selection."
        ),
        "llm_with_rules": (
            "The model makes the same choice - then one deterministic repair "
            "family rewrites it to the stated typical rate."
        ),
    },
    mechanism_title="Why the model alone gets this one wrong",
    mechanism=(
        "The letter offers two numbers: a stated typical pattern - a focal "
        "seizure monthly - and a concrete count - seven seizures so far this "
        "year. The benchmark's gold convention prefers the typical pattern, "
        "because a year-to-date count is not a rate. A language model, "
        "reading like a person in a hurry, prefers the count. LLM-only has "
        "no stage after the model that is allowed to change a selection, so "
        "the mistake stands. LLM-with-rules adds deterministic repair "
        "families that are allowed to - and on this letter exactly one fires."
    ),
    hybrid_raw_output=GAN_HYBRID_RAW_OUTPUT,
    llm_only_raw_output=GAN_LLM_ONLY_RAW_OUTPUT,
)

# --------------------------------------------------------------------------
# Letter library: TEACH-GAN-02 isolates the monthly-diary repair.
# --------------------------------------------------------------------------

GAN_DIARY_LETTER_ID = "TEACH-GAN-02"
GAN_DIARY_NOTE_TEXT = (
    "Epilepsy clinic letter. Clinic date: 10 July 2026.\n"
    "\n"
    "I reviewed Ms C in the epilepsy clinic today. Her seizure diary shows "
    "one seizure in January, one seizure in February, and two seizures in "
    "June. She remains on lamotrigine 200mg twice daily and tolerates it "
    "well."
)
# The diary convention: a completed diary is a rate over its recorded span
# (4 seizures over 6 months), not the rate of its most recent month.
GAN_DIARY_GOLD_LABEL = "4 per 6 month"

# Fixture standing in for one LLM-with-rules structured call. The model
# extracts the diary correctly but selects only the most recent month - the
# recency bias the monthly-diary repair family exists to correct.
GAN_DIARY_HYBRID_RAW_OUTPUT = json.dumps(
    {
        "events": [
            {
                "event_id": "evt_1",
                "kind": "frequency_rate",
                "raw_value": "one seizure in January, one seizure in February",
                "applies_to": "all seizures",
                "time_window": "2026 diary, January-February",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "one seizure in January, one seizure in February",
                "notes": "diary months with one seizure each",
            },
            {
                "event_id": "evt_2",
                "kind": "frequency_rate",
                "raw_value": "two seizures in June",
                "applies_to": "all seizures",
                "time_window": "June 2026",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "two seizures in June",
                "notes": "most recent diary month",
            },
        ],
        "selection": {
            "selected_event_ids": ["evt_2"],
            "final_kind": "frequency",
            "final_label": "2 per month",
            "evidence": "two seizures in June",
            "confidence": "medium",
            "rationale": (
                "The most recent month is the best guide to the current rate."
            ),
        },
    }
)

# Fixture standing in for one LLM-only decision call: the same recency-biased
# answer, with no repair family downstream to correct it.
GAN_DIARY_LLM_ONLY_RAW_OUTPUT = json.dumps(
    {
        "final_label": "2 per month",
        "evidence": "two seizures in June",
        "answer_kind": "frequency",
        "selected_seizure_type": "all seizures",
        "time_window": "June 2026",
        "applied_rule_families": ["recency"],
        "confidence": "medium",
        "rationale": (
            "The most recent month is the best guide to the current rate."
        ),
    }
)

GAN_DIARY_SPEC = GanCaseSpec(
    case_id="gan2026_diary_span_over_recent_month",
    letter_id=GAN_DIARY_LETTER_ID,
    note_text=GAN_DIARY_NOTE_TEXT,
    gold=GAN_DIARY_GOLD_LABEL,
    gold_reference=(
        "Her seizure diary shows one seizure in January, one seizure in "
        "February, and two seizures in June"
    ),
    gold_note=(
        "A completed diary is a rate over its recorded span: four seizures "
        "across six recorded months, not two per month from the most recent "
        "month alone. This is the same span-rate convention seen in gold "
        "rows such as '11 events in 3 months' -> '11 per 3 month'."
    ),
    story=(
        "Rules find nothing to grab in a bare diary line; the model reads "
        "the diary but answers from the most recent month; the monthly-diary "
        "repair recomputes the rate over the whole recorded span."
    ),
    card_why={
        "rules": (
            "The deterministic extractors find nothing to grab in a bare "
            "diary line. A real coverage boundary: no frequency phrase, no "
            "extraction."
        ),
        "llm": (
            "The model reads the diary but answers from the most recent "
            "month. Two seizures in June is not a monthly rate - and nothing "
            "here can catch that."
        ),
        "llm_with_rules": (
            "The model makes the same recency pick - then the monthly-diary "
            "repair recomputes the rate over the whole recorded span."
        ),
    },
    mechanism_title="The model reads the diary; it just believes the latest month",
    mechanism=(
        "A completed diary is a rate over its recorded span: one seizure in "
        "January, one in February, two in June - four seizures over six "
        "recorded months. The deterministic extractors cannot parse the bare "
        "diary lines at all, so rules-only reports no reference. The model "
        "extracts the diary correctly but selects only June - two seizures - "
        "and renders 2 per month. The monthly-diary repair counts every "
        "recorded month and rewrites the answer to 4 per 6 month."
    ),
    hybrid_raw_output=GAN_DIARY_HYBRID_RAW_OUTPUT,
    llm_only_raw_output=GAN_DIARY_LLM_ONLY_RAW_OUTPUT,
)

# --------------------------------------------------------------------------
# Letter library: TEACH-GAN-03 isolates a preservation stand-down.
# --------------------------------------------------------------------------

GAN_FREE_LETTER_ID = "TEACH-GAN-03"
GAN_FREE_NOTE_TEXT = (
    "Epilepsy clinic letter. Clinic date: 12 June 2026.\n"
    "\n"
    "I reviewed Mr D in the epilepsy clinic today. He has remained "
    "seizure-free since March 2025 with levetiracetam 500mg twice daily. "
    "MRI brain was normal."
)
GAN_FREE_GOLD_LABEL = "seizure free since March 2025"

# Fixture standing in for one LLM-with-rules structured call. The model
# selects the sustained seizure-free event. Elapsed-anchor then converts
# "since March 2025" plus the clinic date into a month duration.
GAN_FREE_HYBRID_RAW_OUTPUT = json.dumps(
    {
        "events": [
            {
                "event_id": "evt_1",
                "kind": "seizure_free",
                "raw_value": "remained seizure-free since March 2025",
                "applies_to": "all seizures",
                "time_window": "since March 2025",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "He has remained seizure-free since March 2025",
                "notes": "sustained freedom on stable medication",
            }
        ],
        "selection": {
            "selected_event_ids": ["evt_1"],
            "final_kind": "seizure_free",
            "final_label": "seizure free since March 2025",
            "evidence": "He has remained seizure-free since March 2025",
            "confidence": "high",
            "rationale": (
                "The letter reports sustained seizure freedom since March 2025."
            ),
        },
    }
)

GAN_FREE_LLM_ONLY_RAW_OUTPUT = json.dumps(
    {
        "final_label": "seizure free since March 2025",
        "evidence": "He has remained seizure-free since March 2025",
        "answer_kind": "seizure_free",
        "selected_seizure_type": "all seizures",
        "time_window": "since March 2025",
        "applied_rule_families": [],
        "confidence": "high",
        "rationale": (
            "The letter reports sustained seizure freedom since March 2025."
        ),
    }
)

GAN_FREE_SPEC = GanCaseSpec(
    case_id="gan2026_seizure_free_preservation_standdown",
    letter_id=GAN_FREE_LETTER_ID,
    note_text=GAN_FREE_NOTE_TEXT,
    gold=GAN_FREE_GOLD_LABEL,
    gold_reference="He has remained seizure-free since March 2025",
    gold_note=(
        "A stated sustained seizure-free period is the answer. Format "
        "repair turns 'since March 2025' into 'seizure free for multiple "
        "month'. Living hybrid select does not convert that window from "
        "the clinic date."
    ),
    story=(
        "The model is right about seizure freedom. Living hybrid select "
        "renders the since-date as a vague month window and stops there."
    ),
    card_why={
        "rules": (
            "Deterministic code extracts the sustained seizure-free "
            "statement and normalizes it. No model involved."
        ),
        "llm": (
            "The model selects the seizure-free event directly. This letter "
            "shows the method can also be right."
        ),
        "llm_with_rules": (
            "Selected-evidence first makes the phrasing scorable. "
            "Living hybrid select keeps the vague month window; it does "
            "not count months from the clinic date."
        ),
    },
    mechanism_title="Since-date stays a vague month window",
    mechanism=(
        "The model selects the seizure-free statement. Selected-evidence "
        "canonicalizes 'since March 2025' to 'seizure free for multiple "
        "month'. Elapsed-anchor is off on the living hybrid select stack."
    ),
    hybrid_raw_output=GAN_FREE_HYBRID_RAW_OUTPUT,
    llm_only_raw_output=GAN_FREE_LLM_ONLY_RAW_OUTPUT,
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

# Fixture standing in for one LLM-only program output.
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
    facts: list[PredictedFact] = field(default_factory=list)
    gold_unit: GoldUnit = field(default_factory=lambda: empty_gold_unit(""))
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
        owner: str | None = None,
        stage_name: str | None = None,
        effect_class: str | None = None,
    ) -> None:
        try:
            stage = self.manifest.stage(stage_id)
            stage_name = stage.name
            owner = stage.owner
            effect_class = stage.effect_class
        except KeyError:
            if owner is None or stage_name is None or effect_class is None:
                raise
        self.observations.append(
            StageObservation(
                stage_id=stage_id,
                stage_name=stage_name,
                owner=owner,
                effect_class=effect_class,
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
            "facts": [fact.to_dict() for fact in self.facts],
            "gold_unit": self.gold_unit.to_dict(),
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
    story: str = ""
    gold_reference: str = ""
    card_why: dict[str, str] = field(default_factory=dict)
    mechanism_title: str = ""
    mechanism: str = ""
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
            "story": self.story,
            "gold_reference": self.gold_reference,
            "card_why": self.card_why,
            "mechanism_title": self.mechanism_title,
            "mechanism": self.mechanism,
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


def _gan_gold_monthly_frequency(gold_label: str) -> float:
    """Take the gold monthly rate from the label parser, not from a literal."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )

    return label_to_frequency_record(gold_label).monthly_frequency


def _gan_record(spec: GanCaseSpec) -> Any:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

    gold = label_to_frequency_record(spec.gold)
    return GanFrequencyRecord(
        source_row_index=spec.source_row_index,
        note_text=spec.note_text,
        gold_label=spec.gold,
        gold_reference=spec.gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=spec.gold,
        gold_label_kind=gold.kind,
        gold_yearly_bounds=gold.yearly_bounds,
        gold_monthly_frequency=gold.monthly_frequency,
    )


def _gan_scoring(
    run: MethodRun, stage_id: str, final_label: str | None, *, gold_label: str
) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
        map_pragmatic,
        map_purist,
    )

    gold_monthly = _gan_gold_monthly_frequency(gold_label)
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
            owner="scorer",
            stage_name="Score",
            effect_class="benchmark_projection",
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
            owner="scorer",
            stage_name="Score",
            effect_class="benchmark_projection",
    )


def _gan_rules_only_run(spec: GanCaseSpec) -> MethodRun:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic_canonical,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
        PipelineConfiguration,
    )

    manifest = load_manifest("gan2026_rules_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    result = deterministic_canonical.run_item(
        _gan_record(spec),
        PipelineConfiguration(architecture="rules"),
    )
    diagnostics = result.diagnostics

    candidates = diagnostics["candidate_events"]
    run.record(
        "gan.rules.extract",
        input_value=spec.note_text,
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
    _gan_scoring(run, "gan.rules.score", result.output.final_value, gold_label=spec.gold)
    run.facts = build_gan_rules_facts(
        spec.note_text,
        candidates,
        normalized,
        selection,
        result.output.final_value,
        run,
        gold_label=spec.gold,
    )
    attach_run_gold(run, spec.gold, spec.gold_note)
    return run


def _gan_llm_only_run(spec: GanCaseSpec) -> MethodRun:
    from clinical_extraction.core.evidence import evidence_is_substring
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm as pipeline,
    )

    manifest = load_manifest("gan2026_llm_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    record = _gan_record(spec)

    prompt_input = pipeline.build_prompt_input(record)
    run.record(
        "gan.llm.build_prompt",
        input_value=spec.note_text,
        output_value=prompt_input,
        changed=True,
        note="Transport only.",
    )
    run.record(
        "gan.llm.model_call",
        input_value="prompt input (fixture: no model call is made)",
        output_value=spec.llm_only_raw_output,
        changed=True,
        note="Fixture boundary. Everything after this line is real code.",
    )

    decision, errors, trace = pipeline.parse_decision_json_with_trace(
        spec.llm_only_raw_output
    )
    run.record(
        "gan.llm.json_schema_repair",
        input_value=spec.llm_only_raw_output,
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
        evidence_is_substring(spec.note_text, decision.evidence) if decision else False
    )
    run.record(
        "gan.llm.evidence_containment",
        input_value=decision.evidence if decision else None,
        output_value=f"evidence_valid={evidence_valid}",
        changed=False,
    )
    _gan_scoring(run, "gan.llm.score", final_label, gold_label=spec.gold)
    run.facts = build_gan_llm_facts(
        spec.note_text,
        decision.evidence if decision else "",
        str(adapter["before_label"] or ""),
        str(adapter["after_label"] or ""),
        final_label,
        run,
        gold_label=spec.gold,
        method_prefix="gan.llm",
    )
    attach_run_gold(run, spec.gold, spec.gold_note)
    return run


def _gan_llm_extract_raw_run(
    spec: GanCaseSpec,
    *,
    repair_mode: str = "llm_select",
    method_id: str | None = None,
    raw_output: str | None = None,
) -> MethodRun:
    from clinical_extraction.core.evidence import evidence_is_substring
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as hybrid,
    )

    manifest = load_manifest("gan2026_llm_with_rules")
    run = MethodRun(method_id=method_id or manifest.method_id, manifest=manifest)
    record = _gan_record(spec)
    repair_config = hybrid.StructuredRepairConfig.for_mode(repair_mode)
    hybrid_raw = raw_output if raw_output is not None else spec.hybrid_raw_output

    prompt_input = hybrid.build_prompt_input(record)
    run.record(
        "gan.llm_with_rules.build_prompt",
        input_value=spec.note_text,
        output_value=prompt_input,
        changed=True,
        note="Transport only.",
    )
    run.record(
        "gan.llm_with_rules.model_call",
        input_value="prompt input (fixture: no model call is made)",
        output_value=hybrid_raw,
        changed=True,
        note=(
            "Fixture boundary. Note what the model returned: two events AND a "
            "selection. The selection is the model's, not a rule's."
        ),
    )

    extraction, normalized_events, errors, trace = hybrid.parse_structured_json_with_trace(
        hybrid_raw,
        note_text=spec.note_text,
        repair_config=repair_config,
    )
    run.record(
        "gan.llm_with_rules.json_schema_repair",
        input_value=hybrid_raw,
        output_value=trace["format_repair"],
        changed=bool(trace["format_repair"]["schema_payload_changed"]),
        note="This fixture is already well formed, so nothing is repaired.",
    )
    run.record(
        "gan.llm_with_rules.format_only_retry",
        input_value="(not eligible: hosted model, first parse succeeded)",
        output_value="(not run)",
        changed=False,
        note="Conditional stage. Fires only for local ollama-served models.",
    )
    run.record(
        "gan.llm_with_rules.schema_validation",
        input_value="repaired payload",
        output_value=("validated" if extraction else "schema_validation_error"),
        changed=False,
    )
    run.record(
        "gan.llm_with_rules.normalize_events",
        input_value=[
            _event_summary(event) for event in trace["model_prediction"]["record"]["events"]
        ],
        output_value=[_normalized_summary(event) for event in normalized_events],
        changed=True,
        note="Every event is normalized, not only the selected one.",
    )

    selection_block = trace["deterministic_selection"]
    run.record(
        "gan.llm_with_rules.resolve_label",
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
        note_text=spec.note_text,
        repair_config=repair_config,
        expected_final_label=final_label,
    )
    for (family, before, after, vetoed_with) in walk:
        if before != after:
            note = "fired on this letter"
        elif vetoed_with:
            note = (
                f"computed {vetoed_with}, withheld by the preservation rule - "
                "the model's answer was left standing"
            )
        else:
            note = "did not fire on this letter"
        run.record(
            f"gan.llm_with_rules.repair.{family}",
            input_value=before,
            output_value=after,
            changed=before != after,
            note=note,
            owner="deterministic",
            stage_name=f"Repair {family}",
            effect_class="clinical_meaning",
        )
    run.record(
        "gan.llm_with_rules.scorable_label_check",
        input_value=final_label,
        output_value=(
            "unscorable"
            if any(str(err).startswith("unscorable_final_label") for err in errors)
            else "scorable"
        ),
        changed=False,
    )
    evidence = extraction.selection.evidence if extraction else ""
    evidence_valid = evidence_is_substring(spec.note_text, evidence) if evidence else False
    run.record(
        "gan.llm_with_rules.evidence_containment",
        input_value=evidence,
        output_value=f"evidence_valid={evidence_valid}",
        changed=False,
        note=(
            "The evidence checked is the model's original selection evidence. "
            "A repair can change the label without changing this span."
        ),
    )
    _gan_scoring(run, "gan.llm_with_rules.score", final_label, gold_label=spec.gold)
    model_events = []
    if extraction is not None:
        model_events = list(extraction.events)
    elif trace["model_prediction"]["record"]:
        model_events = list(trace["model_prediction"]["record"].get("events") or [])
    selection_record = extraction.selection if extraction is not None else None
    run.facts = build_gan_hybrid_facts(
        spec.note_text,
        model_events,
        normalized_events,
        {
            "selected_event_ids": selection_block["selected_event_ids"],
            "model_final_label": selection_block["model_final_label"],
            "resolved_label": selection_block["resolved_label"],
            "evidence": evidence,
            "confidence": getattr(selection_record, "confidence", None),
            "rationale": getattr(selection_record, "rationale", None),
            "final_kind": getattr(selection_record, "final_kind", None),
            "final_label": getattr(selection_record, "final_label", None) or final_label,
        },
        walk,
        final_label,
        run,
        gold_label=spec.gold,
    )
    attach_run_gold(run, spec.gold, spec.gold_note)
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
) -> list[tuple[str, str, str, str | None]]:
    """Attribute each label change to the repair family that actually made it.

    The pipeline records repair events in a flat list, so the family that fired
    cannot be read off the trace. Rather than guess - which is how the
    misleading syn_014 teaching fixture went wrong - this walks the same repair
    families in the same order, calling the same functions on the same
    pre-repair extraction, and then checks that it lands on the label the
    pipeline itself produced. If the two disagree, this raises instead of
    publishing an invented attribution.

    Returns one (family, before, after, vetoed_with) quadruple per repair
    stage. ``vetoed_with`` carries the candidate a preservation rule withheld,
    so a deliberate stand-down is visible rather than indistinguishable from
    a family that found nothing to do.
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
    walk: list[tuple[str, str, str, str | None]] = []

    def step(family: str, candidate: str | None, vetoed_with: str | None = None) -> None:
        nonlocal label
        before = label
        after = candidate if candidate else before
        walk.append((family, before, after, vetoed_with))
        label = after

    step(
        "selected_evidence",
        repair_prediction_label_with_evidence(
            label, model_extraction.selection.evidence, context_text=note_text
        )
        if repair_config.selected_evidence_repair
        else None,
    )
    if repair_config.codebook_label_repair:
        from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
            codebook_encode,
        )

        repair_codebook_label_with_evidence = (
            codebook_encode.repair_codebook_label_with_evidence
        )

        selected_ids = set(model_extraction.selection.selected_event_ids)
        selected_kinds = [
            str(event.kind)
            for event in model_extraction.events
            if event.event_id in selected_ids
        ]
        codebook_trace = repair_codebook_label_with_evidence(
            label,
            model_extraction.selection.evidence,
            selected_event_kinds=selected_kinds,
            context_text=note_text,
        )
        codebook_after = label
        for event in codebook_trace.events:
            codebook_after = event.after
        step("codebook", codebook_after if codebook_after != label else None)

    diary_label = (
        monthly_diary_label_from_events(model_extraction, note_text=note_text)
        if repair_config.monthly_diary_repair
        else None
    )
    diary_vetoed = None
    if diary_label and hybrid._should_preserve_label_from_monthly_diary(
        label, extraction=model_extraction
    ):
        diary_vetoed, diary_label = diary_label, None
    step("monthly_diary", diary_label, vetoed_with=diary_vetoed)

    step(
        "usual_interval",
        families.usual_interval_label_from_events(model_extraction, label)
        if repair_config.usual_interval_repair
        else None,
    )
    step(
        "typical_over_ytd",
        families.typical_recurring_rate_over_ytd_from_events(model_extraction, label)
        if repair_config.typical_over_ytd_repair
        else None,
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
    elapsed_vetoed = None
    if elapsed_label and hybrid._should_preserve_sustained_selected_seizure_free(
        model_extraction, label, elapsed_label
    ):
        elapsed_vetoed, elapsed_label = elapsed_label, None
    step("elapsed_anchor", elapsed_label, vetoed_with=elapsed_vetoed)

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


def _gan_case(spec: GanCaseSpec) -> TeachingCase:
    case = TeachingCase(
        case_id=spec.case_id,
        task="gan2026",
        task_label="Gan 2026",
        letter_id=spec.letter_id,
        note_text=spec.note_text,
        gold=spec.gold,
        gold_note=spec.gold_note,
        fixture_note=spec.fixture_note
        or (
            "The letter is synthetic and the raw model outputs are fixtures "
            "standing in for one model call each. No model call is made when "
            "this case is built. Prediction-bearing stages and evidence gates "
            "after the model boundary use the real selected implementation; "
            "the Gan score projection is run over the synthetic gold label."
        ),
        story=spec.story,
        gold_reference=spec.gold_reference,
        card_why=spec.card_why,
        mechanism_title=spec.mechanism_title,
        mechanism=spec.mechanism,
    )
    case.runs = [
        _gan_rules_only_run(spec),
        _gan_llm_only_run(spec),
        _gan_llm_extract_raw_run(spec),
    ]
    return case


def build_gan_case() -> TeachingCase:
    return _gan_case(GAN_SPEC)


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


def _exect_rules_only_run(letter: Any | None = None) -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    manifest = load_manifest("exectv2_rules_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = letter or _exect_letter()

    result = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(method="rules")
    ).run(letter).result
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
    _exect_scoring(
        run,
        "exect.rules.score",
        result.prediction.mentions,
        nine_entity=True,
        letter=letter,
    )
    comparison = getattr(result, "comparison_projection", None)
    mentions = comparison.mentions if comparison is not None else result.prediction.mentions
    run.facts = build_exect_facts(
        letter,
        mentions,
        result.stage_events,
        run,
        gold_label=_exect_gold_label(letter),
    )
    attach_run_gold(run, _exect_gold_label(letter))
    return run


def _exect_llm_only_run(
    letter: Any | None = None, raw_output: str | None = None
) -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    manifest = load_manifest("exectv2_llm_only")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = letter or _exect_letter()

    producer = structured_one_call.produce_structured_letter(
        letter,
        mode="replay",
        raw_output=raw_output or EXECT_HYBRID_RAW_OUTPUT,
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
    _exect_scoring(
        run,
        "exect.llm.score",
        result.prediction.mentions,
        nine_entity=False,
        letter=letter,
    )
    run.facts = build_exect_facts(
        letter,
        result.prediction.mentions,
        result.stage_events,
        run,
        gold_label=_exect_gold_label(letter),
    )
    attach_run_gold(run, _exect_gold_label(letter))
    return run


def _exect_llm_pre_post_run(
    letter: Any | None = None, raw_output: str | None = None
) -> MethodRun:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    manifest = load_manifest("exectv2_llm_pre_post")
    run = MethodRun(method_id=manifest.method_id, manifest=manifest)
    letter = letter or _exect_letter()

    producer = structured_one_call.produce_structured_letter(
        letter,
        mode="replay",
        raw_output=raw_output or EXECT_HYBRID_RAW_OUTPUT,
        config=StructuredMethodConfig.selected(),
    )
    result = structured_one_call.run_llm_pre_post_letter(
        letter,
        producer,
        config=StructuredMethodConfig.selected(),
    )
    for event in result.stage_events:
        if event.stage_id == "exect.llm_pre_post.score":
            continue
        if ".lens." in event.stage_id:
            run.record(
                event.stage_id,
                input_value=_summarize_findings(event.input_value),
                output_value=_summarize_findings(event.output_value),
                changed=_lens_clinically_changed(event.output_value),
                note=_lens_teaching_note(event.output_value),
            )
            continue
        run.record(
            event.stage_id,
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            note=(
                "Fixture boundary at the one-call producer; no live model call "
                "is made."
                if event.stage_id == "exect.llm_pre_post.model_call"
                else ""
            ),
        )
    _exect_scoring(
        run,
        "exect.llm_pre_post.score",
        result.prediction.mentions,
        nine_entity=False,
        letter=letter,
    )
    run.facts = build_exect_facts(
        letter,
        result.prediction.mentions,
        result.stage_events,
        run,
        gold_label=_exect_gold_label(letter),
    )
    attach_run_gold(run, _exect_gold_label(letter))
    return run


def _exect_gold_label(letter: Any) -> str:
    annotations = getattr(letter, "annotations", None)
    if annotations:
        return f"{len(annotations)} gold annotations"
    return "(no gold annotations)"


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


def _exect_letter_has_gold(letter: Any) -> bool:
    return bool(getattr(letter, "annotations", None))


_HEADLINE_FAMILIES = (
    ("Diagnosis", "Diagnosis"),
    ("SeizureFrequency", "Seizure frequency"),
    ("Prescription", "Prescription"),
    ("Investigations", "Investigations"),
)


def _format_headline_key(family: str, key: Any, letter: ExectLetter) -> str:
    if family == "Diagnosis" and isinstance(key, tuple) and len(key) >= 2:
        return str(key[1])
    if family == "SeizureFrequency":
        state = key[1] if isinstance(key, tuple) and len(key) >= 2 else ""
        for annotation in letter.entities(family):
            if key in clinical_headline_unit_keys(family, [annotation], letter.note_text):
                phrase = annotation.text.replace("-", " ")
                return f"{phrase} ({state})" if state else phrase
        type_key = key[0] if isinstance(key, tuple) else key
        type_label = (
            type_key[1] if isinstance(type_key, tuple) and len(type_key) >= 2 else type_key
        )
        return f"{type_label} ({state})" if state else str(type_label)
    if family == "Prescription" and isinstance(key, tuple) and key:
        if key[0] == "ordinary" and len(key) >= 5:
            _kind, name, dose, unit, freq = key[:5]
            return f"{name} {dose} {unit} ×{freq}"
        if key[0] == "rescue" and len(key) >= 2:
            return f"{key[1]} as required"
    if family == "Investigations" and isinstance(key, tuple) and len(key) >= 3:
        modality, performed, result = key[0], key[1], key[2]
        parts = [str(modality)]
        if performed == "Yes":
            parts.append("performed")
        elif performed:
            parts.append(str(performed))
        if result:
            parts.append(str(result).lower())
        return " ".join(parts)
    if isinstance(key, tuple):
        return " ".join(str(part) for part in key if part not in {None, ""})
    return str(key)


def _headline_family_labels(letter: ExectLetter, family: str) -> list[str]:
    keys = clinical_headline_unit_keys(family, letter.entities(family), letter.note_text)
    return [_format_headline_key(family, key, letter) for key in keys]


def _join_labels(labels: Sequence[str]) -> str:
    return "; ".join(labels) if labels else "(none)"


def _family_output_lines(predicted: ExectLetter) -> list[str]:
    return [
        f"{label}: {_join_labels(_headline_family_labels(predicted, family))}"
        for family, label in _HEADLINE_FAMILIES
    ]


def _as_finding_items(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        return parsed if isinstance(parsed, list) else [parsed]
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    return [value]


def _as_mapping(item: Any) -> Mapping[str, Any] | None:
    if isinstance(item, Mapping):
        return item
    if hasattr(item, "model_dump"):
        dumped = item.model_dump()
        return dumped if isinstance(dumped, Mapping) else None
    return None


def _summarize_findings(value: Any) -> str:
    lines: list[str] = []
    for item in _as_finding_items(value):
        data = _as_mapping(item)
        if data is None:
            text = str(item).strip()
            if text:
                lines.append(text)
            continue
        entity = str(data.get("entity") or "").strip()
        text = str(data.get("text") or "").strip()
        line = f"{entity}: {text}" if entity and text else text or entity
        if line:
            lines.append(line)
    return "\n".join(lines) if lines else "(none)"


def _lens_clinically_changed(output_value: Any) -> bool:
    for item in _as_finding_items(output_value):
        data = _as_mapping(item)
        if data is None:
            continue
        for step in data.get("provenance") or []:
            if not isinstance(step, Mapping):
                continue
            action = str(step.get("action") or "")
            raw_detail = step.get("detail")
            detail = raw_detail if isinstance(raw_detail, Mapping) else {}
            if action == "rewrote_diagnosis_convention_from_dictionary":
                return True
            if action == "applied_standard_dictionary_diagnosis_repair" and (
                int(detail.get("rewritten_count") or 0)
                or int(detail.get("added_count") or 0)
                or int(detail.get("dropped_count") or 0)
            ):
                return True
            if action == "applied_standard_dictionary_prescription_repair" and (
                int(detail.get("normalized_count") or 0)
                or int(detail.get("split_regimen_count") or 0)
                or int(detail.get("dropped_non_antiepileptic_count") or 0)
            ):
                return True
    return False


def _lens_teaching_note(output_value: Any) -> str:
    notes: list[str] = []
    for item in _as_finding_items(output_value):
        data = _as_mapping(item)
        if data is None:
            continue
        for step in data.get("provenance") or []:
            if not isinstance(step, Mapping):
                continue
            action = str(step.get("action") or "")
            raw_detail = step.get("detail")
            detail = raw_detail if isinstance(raw_detail, Mapping) else {}
            if action == "rewrote_diagnosis_convention_from_dictionary":
                source = detail.get("source_text")
                target = detail.get("target_text")
                if source and target:
                    notes.append(f"Dictionary rewrote diagnosis: {source} → {target}.")
    unique = list(dict.fromkeys(notes))
    if unique:
        return " ".join(unique)
    return "Assembled this family; no further clinical rewrite."


def _mention_mapping(mention: Any) -> dict[str, Any]:
    if hasattr(mention, "model_dump"):
        data = mention.model_dump()
    elif isinstance(mention, Mapping):
        data = dict(mention)
    else:
        rendered = _jsonable(mention)
        data = dict(rendered) if isinstance(rendered, Mapping) else {}
    attributes = data.get("attributes") or {}
    return {
        "entity": str(data.get("entity", "")),
        "text": str(data.get("text", mention)),
        "attributes": {
            str(key): str(value)
            for key, value in dict(attributes).items()
            if value is not None
        },
    }


def _exect_scoring(
    run: MethodRun,
    stage_id: str,
    mentions: Sequence[Any],
    *,
    nine_entity: bool,
    letter: Any | None = None,
) -> None:
    by_entity: dict[str, int] = {}
    for mention in mentions:
        data = _mention_mapping(mention)
        entity = data.get("entity") or "?"
        by_entity[entity] = by_entity.get(entity, 0) + 1
    coverage = "nine entities" if nine_entity else "four families"
    has_gold = letter is not None and _exect_letter_has_gold(letter)
    if has_gold:
        assert letter is not None
        predicted = ExectLetter(
            letter_id=str(letter.letter_id),
            note_text=letter.note_text,
            annotations=tuple(
                annotation_from_mapping(_mention_mapping(mention))
                for mention in mentions
            ),
        )
        emitted = _family_output_lines(predicted)
        run.final_answer = "\n".join(emitted)
        run.correct = None
        boundary = (
            "Rules extract nine entities; this station shows the four-family "
            "units that left the line. "
            if nine_entity
            else ""
        )
        run.correctness_note = (
            f"{boundary}Gold comparison lives on Workbench."
        )
        score_note = "What left the line. Gold comparison lives on Workbench."
        output_value: Any = "\n".join(emitted)
        input_value = f"{len(mentions)} finding(s) entering the scorer"
    else:
        run.final_answer = ", ".join(
            f"{entity} x{count}" for entity, count in sorted(by_entity.items())
        )
        run.correct = None
        run.correctness_note = (
            f"This teaching letter carries no gold annotations, so no "
            f"correctness verdict is claimed. The comparable unit is {coverage}."
        )
        score_note = (
            "Unscored scorer-boundary illustration: this synthetic letter has "
            "no gold annotations. A real run scores the comparison over "
            f"{coverage}."
        )
        output_value = by_entity
        input_value = f"{len(mentions)} finding(s) over {coverage}"
    run.record(
        stage_id,
        input_value=input_value,
        output_value=output_value,
        changed=True,
        note=score_note,
        owner="scorer",
        stage_name="Score",
        effect_class="benchmark_projection",
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
            "this case is built. Prediction-bearing stages and post-model "
            "gates use the real selected implementation; the final ExECT "
            "score entry is an unscored scorer-boundary illustration because "
            "this letter has no gold annotations."
        ),
        story=(
            "One model call proposes findings across four families; the "
            "hybrid adds deterministic family transforms, and the rules "
            "baseline answers a different, nine-entity question."
        ),
        card_why={
            "rules": (
                "Nine independent deterministic extractors produce the "
                "all-nine baseline. No model involved."
            ),
            "llm": (
                "One structured call proposes findings for four families, "
                "scored as proposed, before any deterministic transform."
            ),
            "llm_with_rules": (
                "The same one call - then deterministic family transforms "
                "reconcile the findings into the scored representation."
            ),
        },
        mechanism_title="What the deterministic layer adds around one model call",
        mechanism=(
            "One model call proposes findings across four families - "
            "diagnosis, seizure frequency, prescriptions, investigations. "
            "LLM-only scores them as proposed. LLM-with-rules passes them "
            "through deterministic family transforms that complete state "
            "representations and reconcile findings before scoring. This "
            "letter is chosen for shape, so both model-led methods produce "
            "the same four families here; the stage tables below show "
            "exactly which transforms sit between the call and the score."
        ),
    )
    case.runs = [
        _exect_rules_only_run(),
        _exect_llm_only_run(),
        _exect_llm_pre_post_run(),
    ]
    return case


def build_all_cases() -> tuple[TeachingCase, ...]:
    return (build_gan_case(), build_exect_case())


def build_gan_letter_library() -> tuple[TeachingCase, ...]:
    """Additional Gan letters, each isolating one mechanism for the
    interactive explainer. Not part of the canonical architecture-document
    reading order."""

    return (_gan_case(GAN_DIARY_SPEC), _gan_case(GAN_FREE_SPEC))


def build_teaching_letters() -> tuple[TeachingCase, ...]:
    """Explainer letters: paper flagship G1, G3, E1, and E2."""

    from clinical_extraction.architecture.paper_teaching_cases import (
        build_paper_teaching_letters,
    )

    return build_paper_teaching_letters()
