"""Mention-unit v2 ExECT research lane.

Both methods copy a clinical name from the letter. The llm lane also fills
family-specific number fields. Hybrid leftover words stay in evidence.
Hybrid may rewrite, project, or suppress that item only. It does not search
the letter or change the selected ExECT method.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_SURFACE_FORMS,
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as sf_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_unit,
)

from .mention_unit_leftover_form import (
    project_leftover_form_investigation,
    project_leftover_form_sf,
)
from .mention_unit_shared import (
    HYBRID_METHOD,
    LLM_METHOD,
    InventoryMaterialization,
    _apply_hybrid_letter_rules,
    _certainty,
    _coerce_text,
    _dose_unit,
    _flatten_attribute_object,
    _frequency,
    _heading_split_phrases,
    _is_uncoded_phenomenology,
    _negation,
    _normalize_family,
    _sf_attributes_to_legacy,
    _stringify_attributes,
    project_hybrid_event,
    project_rx_split_once_daily,
)
from .pipelines.key_entities_structured import records as structured_records
from .pipelines.key_entities_structured.prompt_content import (
    candidate_evidence_ledger_for_letter,
)
from .pipelines.key_entities_structured.prompt_plain_language import (
    _clean_ledger_row,
)
from .shared.json_parse import parse_json_payload
from .shared.mention_pipeline import check_evidence

MENTION_ENCODER_PROMPT = "exectv2_mention_encoder"
MENTION_UNIT_PROMPT_VERSION = MENTION_ENCODER_PROMPT
MENTION_UNIT_PROMPT_VERSION_V2 = "exectv2_mention_unit_v2"
MENTION_UNIT_MODEL = "openai/gpt-5.6-luna"
MentionUnitCue5Arm = Literal["heading", "bare_frame", "one_row", "no_join"]
MentionUnitComboArm = Literal["scaffold", "form_guide"]
COMBO_ARM_VERSIONS: dict[MentionUnitComboArm, str] = {
    "scaffold": "exectv2_mention_unit_v2_combo_scaffold",
    "form_guide": "exectv2_mention_unit_v2_combo_form_guide",
}
CUE5_ARM_VERSIONS: dict[MentionUnitCue5Arm, str] = {
    "heading": "exectv2_mention_unit_v2_cue5_heading",
    "bare_frame": "exectv2_mention_unit_v2_cue5_bare_frame",
    "one_row": "exectv2_mention_unit_v2_cue5_one_row",
    "no_join": "exectv2_mention_unit_v2_cue5_no_join",
}
_CUE5_SUFFIXES: dict[MentionUnitCue5Arm, str] = {
    "heading": (
        "A heading that states a rate or dated count is a frequency "
        "statement. Do not replace it with a later vague estimate."
    ),
    "bare_frame": (
        "A seizure-free line, or a line that only says the seizures are "
        "well managed, needs a seizure type or a time frame. Leave it out "
        "if it has neither."
    ),
    "one_row": (
        "One frequency statement is one row. Do not list both seizures and "
        "a named type for the same count."
    ),
    "no_join": (
        "If two types share one count, write the type the count belongs to. "
        "Do not join them as one name."
    ),
}
SYSTEM_MESSAGE = (
    "List each diagnosis, seizure-frequency statement, current medicine, "
    "and completed test with a result. Return the requested JSON exactly."
)
_LLM_CODING_FIELDS = {
    DIAGNOSIS.name: ("certainty", "negation"),
    SEIZURE_FREQUENCY.name: (
        "count",
        "lower_count",
        "upper_count",
        "period_count",
        "lower_period",
        "upper_period",
        "period",
        "state",
        "change",
        "since_or_during",
        "point_in_time",
        "month",
        "year",
    ),
    PRESCRIPTION.name: ("dose", "unit", "schedule", "status"),
    INVESTIGATIONS.name: ("result", "status"),
}
_SHARED_ITEM_KEYS = frozenset(
    {
        "clinical_family",
        "clinical_name",
        "evidence",
        "attributes",
        "family",
        "text",
        "event",
    }
)
_MODALITY_NAMES = frozenset({"MRI", "CT", "EEG"})
_FREQUENCY_CHANGE = frozenset(
    {"Decreased", "Frequent", "Increased", "Infrequent", "Same"}
)
_POINT_IN_TIME = {
    "birthday": "Birthday",
    "drug change": "DrugChange",
    "drugchange": "DrugChange",
    "last clinic": "LastClinic",
    "lastclinic": "LastClinic",
    "last month": "Last_Month",
    "last_month": "Last_Month",
    "last week": "Last_Week",
    "last_week": "Last_Week",
    "last year": "Last_Year",
    "last_year": "Last_Year",
    "surgery": "Surgery",
}
_SHARED_OPENING = (
    "Read the letter once. Return one list that follows the schema. Each row "
    "has a clinical family, a clinical name, and evidence.\n\n"
    "The list has four clinical families:\n\n"
    "- Diagnosis: a named epilepsy or seizure type the letter applies to this "
    "patient, including in history.\n"
    "- SeizureFrequency: a frequency statement — a rate, dated count, last "
    "event, change, or seizure-free duration — including past ones.\n"
    "- Prescription: a current anti-seizure medicine.\n"
    "- Investigations: a completed MRI, CT, or EEG with a result.\n\n"
    "In clinical name, write the diagnosis type, the seizure words, the drug, "
    "or MRI / CT / EEG."
)
_LLM_CONTINUE = (
    "If the letter says “2 to 3 focal seizures a week”, the clinical name is "
    "focal seizures. The “2 to 3” and the “week” go in the number fields, not "
    "in clinical name.\n"
    "In evidence, copy the shortest part of the letter that supports that row.\n"
    "If there is a rate, a date, or seizure freedom, use the form table."
)
_HYBRID_CONTINUE = (
    "If the letter says “2 to 3 focal seizures a week”, the clinical name is "
    "focal seizures. The “2 to 3” and the “week” stay in evidence, not in "
    "clinical name.\n"
    "In evidence, copy the shortest part of the letter that supports that row, "
    "including the number, date, dose, or result."
)
_HYBRID_FORM_GUIDE_CONTINUE = (
    f"{_HYBRID_CONTINUE}\n"
    "If there is a rate, a date, or seizure freedom, use the form table to "
    "know which leftover numbers and dates belong in evidence."
)
_SHARED_CLOSER = (
    "If a clinical family has nothing, skip it. If the same type is both a "
    "diagnosis and a frequency statement, write two rows. They may share evidence."
)
_SELECTION_CUES = (
    "Copy the clinical name from the letter. If a clinical family has "
    "nothing to list, skip it.",
    "Bare absences or myoclonic jerks are not a diagnosis. Named absence "
    "seizures or myoclonic seizures are.",
    "Do not list epilepsy from driving, counselling, or a general "
    "discussion unless the letter attaches it to this patient.",
    "A named type with a count of 0 is still a diagnosis, and also a "
    "seizure-frequency row with count 0. That is two rows. They may share "
    "evidence.",
    "List every frequency statement, including past ones: a rate, a dated "
    "count, a last event, a change, or a seizure-free duration. The "
    "clinical name may be seizures, a named type, absences, or myoclonic "
    "jerks. Do not use events, episodes, or slang. Do not list a seizure "
    "story that has no frequency.",
    "List a completed MRI, CT, or EEG only when the letter states a "
    "result. Do not guess the EEG type.",
    "Current anti-seizure medicines only. Rescue may lack a dose. If the "
    "letter says the same dose and does not state the dose, leave the "
    "drug out.",
)


def selection_cues_for(cue5_arm: MentionUnitCue5Arm | None = None) -> list[str]:
    """Return the seven cues, optionally with one study-only cue-5 suffix."""

    cues = list(_SELECTION_CUES)
    if cue5_arm is None:
        return cues
    if cue5_arm not in _CUE5_SUFFIXES:
        raise ValueError(f"unknown mention-unit cue-5 arm: {cue5_arm!r}")
    cues[4] = f"{cues[4]} {_CUE5_SUFFIXES[cue5_arm]}"
    return cues


def mention_unit_prompt_version(
    cue5_arm: MentionUnitCue5Arm | None = None,
    combo_arm: MentionUnitComboArm | None = None,
) -> str:
    """Return the Mention-encoder identity, or one study-only graft identity."""

    if cue5_arm is not None and combo_arm is not None:
        raise ValueError("cue5_arm and combo_arm cannot be combined")
    if combo_arm is not None:
        if combo_arm not in COMBO_ARM_VERSIONS:
            raise ValueError(f"unknown mention-unit combo arm: {combo_arm!r}")
        return COMBO_ARM_VERSIONS[combo_arm]
    if cue5_arm is None:
        return MENTION_UNIT_PROMPT_VERSION
    return CUE5_ARM_VERSIONS[cue5_arm]


def cheap_stack_suggested_evidence(letter: ExectLetter) -> list[dict[str, Any]]:
    """Return the cheap-stack suggested-evidence rows for one letter."""

    return [
        _clean_ledger_row(row) for row in candidate_evidence_ledger_for_letter(letter)
    ]


_FORM_TABLE = (
    {
        "when": "A single count over a time unit, including every 3 weeks",
        "fill": "count, period_count, period — every 3 weeks is 1 / 3 / week",
    },
    {
        "when": "A count range",
        "fill": "lower_count, upper_count, plus the same time or date fields",
    },
    {
        "when": "A time-unit range",
        "fill": "count, lower_period, upper_period, period",
    },
    {
        "when": "A count in a stated month or year",
        "fill": (
            "count (or the range), date fields, since_or_during=during. "
            "Do not invent period=month unless the letter says per month"
        ),
    },
    {
        "when": "No further / none / not had any since a date",
        "fill": "count=0, since_or_during=since, date fields",
    },
    {
        "when": "Seizure-free for a duration, or last event a stated time ago",
        "fill": "count=0, period_count, period",
    },
    {
        "when": "A count since last clinic or a drug change",
        "fill": "count, since_or_during=since, point_in_time",
    },
    {
        "when": "Returned, worse, improved, frequent, or infrequent, with no count",
        "fill": "change only",
    },
)
_CLOSED_VALUES = {
    "period": ["day", "week", "month", "year"],
    "since_or_during": ["since", "during"],
    "change": ["decreased", "frequent", "increased", "infrequent", "same"],
    "approximate_counts": {"couple": 2, "few": 2, "several": 3},
}


class MentionItem(BaseModel):
    """One model-emitted clinical-name row."""

    model_config = ConfigDict(extra="ignore")

    family: str
    text: str = ""
    evidence: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)


class MentionUnitRecord(BaseModel):
    """The clinical-name envelope after transport parsing."""

    model_config = ConfigDict(extra="ignore")

    items: list[MentionItem] = Field(default_factory=list)

    @property
    def facts(self) -> list[MentionItem]:
        return self.items


@dataclass(frozen=True)
class MentionUnitParseResult:
    record: MentionUnitRecord | None
    errors: list[str] = field(default_factory=list)
    forbidden_fields: list[dict[str, Any]] = field(default_factory=list)


class ClinicalNameChatAdapter(ChatAdapter):
    """Keep DSPy's parser while using a short, plain system message."""

    def format(
        self,
        signature: type[dspy.Signature],
        demos: list[dict[str, object]],
        inputs: dict[str, object],
    ) -> list[dict[str, object]]:
        messages = super().format(signature, demos, inputs)
        messages[0] = {"role": "system", "content": SYSTEM_MESSAGE}
        return messages


class ClinicalNameListSignature(dspy.Signature):
    """Read one clinical letter and return the requested JSON list."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and the extraction instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc="One JSON object with an items list that follows the supplied output schema."
    )


class MentionUnitExtractor(dspy.Module):
    """One-call model program for either clinical-name method contract."""

    def __init__(self, *, method: Literal["llm", "llm_with_rules"]) -> None:
        super().__init__()
        if method not in {LLM_METHOD, HYBRID_METHOD}:
            raise ValueError(f"unknown mention-unit method: {method!r}")
        self.method = method
        self.predict = dspy.Predict(ClinicalNameListSignature)
        self._adapter = ClinicalNameChatAdapter()

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        with dspy.context(adapter=self._adapter):
            return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        return self._adapter.format(
            ClinicalNameListSignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )


def build_mention_unit_prompt(
    letter: ExectLetter,
    *,
    method: Literal["llm", "llm_with_rules"],
    cue5_arm: MentionUnitCue5Arm | None = None,
    combo_arm: MentionUnitComboArm | None = None,
) -> str:
    """Build the model-facing payload without research metadata."""

    if method not in {LLM_METHOD, HYBRID_METHOD}:
        raise ValueError(f"unknown mention-unit method: {method!r}")
    if cue5_arm is not None and combo_arm is not None:
        raise ValueError("cue5_arm and combo_arm cannot be combined")
    if combo_arm is not None and combo_arm not in COMBO_ARM_VERSIONS:
        raise ValueError(f"unknown mention-unit combo arm: {combo_arm!r}")
    if method == LLM_METHOD:
        continue_text = _LLM_CONTINUE
    elif combo_arm == "form_guide":
        continue_text = _HYBRID_FORM_GUIDE_CONTINUE
    else:
        continue_text = _HYBRID_CONTINUE
    task = "\n".join((_SHARED_OPENING, continue_text, _SHARED_CLOSER))
    cues = selection_cues_for(cue5_arm)
    if method == LLM_METHOD:
        item_schema: Any = [
            {
                "clinical_family": "Diagnosis",
                "clinical_name": "The named epilepsy or seizure type copied from the letter.",
                "evidence": "The shortest supporting sentence from the letter.",
                "certainty": "certain, probable, possible, or uncertain.",
                "negation": "affirmed or negated.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": (
                    "The seizure, absence, or myoclonic-jerk words copied from the letter."
                ),
                "evidence": "The shortest supporting sentence from the letter.",
                "count": "Number of seizures when the letter states a number.",
                "lower_count": "Lower count when the letter states a range.",
                "upper_count": "Upper count when the letter states a range.",
                "period_count": "How many time units the count covers, such as 3 in every 3 weeks.",
                "lower_period": "Lower time-unit count when the letter states a range.",
                "upper_period": "Upper time-unit count when the letter states a range.",
                "period": "day, week, month, or year when the letter states a rate basis.",
                "state": "historical, seizure-free, or last-event when the letter states that.",
                "change": "decreased, frequent, increased, infrequent, or same.",
                "since_or_during": "since or during.",
                "point_in_time": "last clinic, drug change, or another stated anchor.",
                "month": "Month number or name when the letter states a month.",
                "year": "Year when the letter states a year.",
            },
            {
                "clinical_family": "Prescription",
                "clinical_name": "The drug or compact regimen copied from the letter.",
                "evidence": "The shortest supporting sentence from the letter.",
                "dose": "Dose amount when stated.",
                "unit": "Dose unit when stated.",
                "schedule": "How often the drug is taken.",
                "status": "current, planned, past, or completed.",
            },
            {
                "clinical_family": "Investigations",
                "clinical_name": "MRI, CT, or EEG copied from the letter.",
                "evidence": "The shortest supporting sentence from the letter.",
                "result": "normal, abnormal, or unknown when the letter states a result.",
                "status": "completed or planned.",
            },
        ]
        payload = {
            "task": task,
            "output_schema": {"items": item_schema},
            "form_table": list(_FORM_TABLE),
            "selection_cues": cues,
            "closed_values": _CLOSED_VALUES,
            "letter_text": letter.note_text,
        }
    else:
        hybrid_schema = {
            "items": {
                "clinical_family": (
                    "Diagnosis | SeizureFrequency | Prescription | Investigations"
                ),
                "clinical_name": (
                    "The diagnosis type, seizure words, drug, or MRI / CT / EEG "
                    "copied from the letter."
                ),
                "evidence": (
                    "The shortest supporting sentence from the letter, including "
                    "the number, date, dose, or result."
                ),
            }
        }
        if combo_arm == "form_guide":
            payload = {
                "task": task,
                "output_schema": hybrid_schema,
                "form_table": list(_FORM_TABLE),
                "selection_cues": cues,
                "letter_text": letter.note_text,
            }
        else:
            payload = {
                "task": task,
                "output_schema": hybrid_schema,
                "selection_cues": cues,
                "letter_text": letter.note_text,
            }
    if combo_arm == "scaffold":
        letter_text = payload.pop("letter_text")
        payload["suggested_evidence"] = cheap_stack_suggested_evidence(letter)
        payload["letter_text"] = letter_text
    return json.dumps(payload, ensure_ascii=False)


def parse_mention_unit_json(
    raw_output: str,
    *,
    method: Literal["llm", "llm_with_rules"],
) -> MentionUnitParseResult:
    """Parse transport JSON and record method-contract violations."""

    if not raw_output.strip():
        return MentionUnitParseResult(None, ["not_run"])
    try:
        payload, dialect_notes = parse_json_payload(
            raw_output,
            schema_repair=True,
            preferred_roots=("items", "facts"),
        )
    except Exception as exc:
        return MentionUnitParseResult(None, [f"invalid_json: {exc}"])
    if isinstance(payload, list):
        payload = {"items": payload}
        dialect_notes = [*dialect_notes, "coerced_top_level_item_array"]
    if not isinstance(payload, dict):
        return MentionUnitParseResult(
            None, [*dialect_notes, "schema_validation_error: items must be a list"]
        )
    raw_items = payload.get("items")
    if raw_items is None and isinstance(payload.get("facts"), list):
        raw_items = payload["facts"]
        dialect_notes = [*dialect_notes, "coerced_facts_to_items"]
    if not isinstance(raw_items, list):
        return MentionUnitParseResult(
            None, [*dialect_notes, "schema_validation_error: items must be a list"]
        )

    errors = list(dialect_notes)
    items: list[MentionItem] = []
    forbidden: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            errors.append(f"schema_validation_error: item[{index}] must be an object")
            continue
        raw = dict(raw_item)
        family = _normalize_family(raw.get("clinical_family") or raw.get("family"))
        if family is None:
            errors.append(f"dropped_unknown_family: item[{index}]")
            continue
        text = _coerce_text(
            _first_text(raw, "clinical_name", "text", "event"),
            errors,
            f"item[{index}].clinical_name",
        )
        if not raw.get("clinical_name") and (raw.get("text") or raw.get("event")):
            errors.append(f"missing_clinical_name_used_text: item[{index}]")
        evidence = _coerce_text(raw.get("evidence"), errors, f"item[{index}].evidence")
        extra = sorted(str(key) for key in raw if key not in _SHARED_ITEM_KEYS)
        if method == HYBRID_METHOD:
            if extra:
                forbidden.append({"item_index": index, "fields": extra})
                errors.append(f"forbidden_model_fields: item[{index}] {extra}")
            attributes: dict[str, Any] = {}
        else:
            attributes = _llm_coding_fields(family, raw, extra, errors, index)
        items.append(
            MentionItem(family=family, text=text, evidence=evidence, attributes=attributes)
        )
    return MentionUnitParseResult(MentionUnitRecord(items=items), errors, forbidden)


def materialize_mention_unit(
    letter: ExectLetter,
    record: MentionUnitRecord,
    *,
    method: Literal["llm", "llm_with_rules"],
    form_recovery: bool = False,
) -> InventoryMaterialization:
    """Create semantic and scorer views while retaining every emitted item.

    form_recovery reads leftover count, period, and test-result words from
    that item's name and evidence. It may drop remote history, rewrite a
    name, or split two stated once-daily doses. It does not search the
    letter.
    """

    semantic_facts: list[dict[str, Any]] = []
    rule_trace: list[dict[str, Any]] = []
    warnings: list[str] = []
    candidates: list[PredictedMention] = []
    evidence_invalid = 0
    span_mode = "span_fold" if form_recovery else "exact"
    for index, item in enumerate(record.items):
        text_valid = _span_in_letter(letter.note_text, item.text, mode=span_mode)
        evidence_valid = _span_in_letter(
            letter.note_text, item.evidence, mode=span_mode
        )
        semantic_row = {
            "fact_index": index,
            "family": item.family,
            "clinical_family": item.family,
            "text": item.text,
            "clinical_name": item.text,
            "evidence": item.evidence,
            "text_valid": text_valid,
            "evidence_valid": evidence_valid,
            "attributes": dict(item.attributes),
        }
        if not evidence_valid:
            evidence_invalid += 1
            warnings.append(f"item[{index}]: evidence_not_substring")
            semantic_facts.append(semantic_row)
            continue
        if not text_valid:
            warnings.append(f"item[{index}]: text_not_substring")
            semantic_facts.append(semantic_row)
            continue
        if form_recovery and item.family == SEIZURE_FREQUENCY.name:
            if _is_childhood_febrile_history(item.text, item.evidence):
                warnings.append(f"item[{index}]: childhood_febrile_history")
                semantic_facts.append(semantic_row)
                continue
            if _is_remote_history(item.evidence):
                warnings.append(f"item[{index}]: remote_history")
                semantic_facts.append(semantic_row)
                continue
            if _is_negated_unused_type(item.evidence):
                warnings.append(f"item[{index}]: negated_unused_type")
                semantic_facts.append(semantic_row)
                continue

        if method == LLM_METHOD:
            projected, status, owner = _llm_project(item)
        else:
            projected, traces, status = _hybrid_project(
                item, index, form_recovery=form_recovery
            )
            if form_recovery:
                projected, cluster_traces = _apply_cluster_name(
                    projected, item, index
                )
                traces.extend(cluster_traces)
                projected, awareness_traces = _apply_awareness_name(
                    projected, item, index
                )
                traces.extend(awareness_traces)
            rule_trace.extend(traces)
            owner = ""

        first = projected[0] if projected else {}
        semantic_row["legacy_attributes"] = dict(first.get("attributes", {}))
        semantic_row["scorer_text"] = str(first.get("text", ""))
        semantic_row["projection_status"] = status
        semantic_facts.append(semantic_row)
        if not projected:
            warnings.append(f"item[{index}]: no_scorer_text")
            continue
        for row in projected:
            candidates.append(
                PredictedMention(
                    entity=str(row["entity"]),
                    text=str(row["text"]),
                    attributes={
                        str(key): str(value) for key, value in row["attributes"].items()
                    },
                    evidence=str(row.get("evidence") or item.evidence),
                    component_owner=str(row.get("component_owner") or owner),
                )
            )

    if method == HYBRID_METHOD:
        candidates, letter_traces = _apply_hybrid_letter_rules(candidates)
        rule_trace.extend(letter_traces)

    evidence_mentions, invalid_mentions, evidence_warnings = check_evidence(
        [
            structured_records.MentionForEvidence(
                entity=mention.entity,
                text=mention.text,
                attributes=dict(mention.attributes),
                evidence=mention.evidence,
            )
            for mention in candidates
        ],
        note_text=letter.note_text,
    )
    warnings.extend(evidence_warnings)
    evidence_invalid += len(invalid_mentions)
    projected_input = PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(
            PredictedMention(
                entity=mention.entity,
                text=mention.text,
                attributes=dict(mention.attributes),
                evidence=mention.evidence,
                component_owner=next(
                    (
                        candidate.component_owner
                        for candidate in candidates
                        if candidate.entity == mention.entity
                        and candidate.text == mention.text
                        and candidate.evidence == mention.evidence
                    ),
                    "",
                ),
            )
            for mention in evidence_mentions
        ),
    )
    prediction = project_cuis(projected_input)
    return InventoryMaterialization(
        prediction=prediction,
        semantic_facts=semantic_facts,
        rule_trace=rule_trace,
        warnings=warnings,
        evidence_invalid=evidence_invalid,
    )


_CHILDHOOD_FEBRILE_AGE_RE = re.compile(
    r"\b(?:(?:at|between)\s+)?the\s+ages?\s+of\b.{0,80}?"
    r"(?:\d+\s+months?|\b1\s+years?|\b[1-5]\b|"
    r"\b(?:one|two|three|four|five)\b)",
    re.I | re.S,
)


def _is_childhood_febrile_history(text: str, evidence: str) -> bool:
    if "febrile" not in _fold_span(text):
        return False
    return bool(_CHILDHOOD_FEBRILE_AGE_RE.search(_fold_span(evidence)))


_REMOTE_LIFE_STAGE_RE = re.compile(
    r"\b(?:teenage(?:\s+years)?|teens|adolescence|school years)\b",
    re.I,
)
_REMOTE_CONTINUATION_RE = re.compile(
    r"\b(?:continued|continues|continue|continuing|every since|"
    r"ever since|still\s+(?:has|have|having)|currently|ongoing)\b",
    re.I,
)


def _is_remote_history(evidence: str) -> bool:
    haystack = _fold_span(evidence)
    if _REMOTE_CONTINUATION_RE.search(haystack):
        return False
    if _REMOTE_LIFE_STAGE_RE.search(haystack):
        return True
    return "febrile" in haystack and bool(_CHILDHOOD_FEBRILE_AGE_RE.search(haystack))


_NEGATED_RESEMBLANCE_RE = re.compile(
    r"\b(?:has|have)\s+not\s+had\s+any\s+events?\s+which\s+resemble\b",
    re.I,
)


def _is_negated_unused_type(evidence: str) -> bool:
    return bool(_NEGATED_RESEMBLANCE_RE.search(_fold_span(evidence)))


_CLUSTER_OF_SEIZURES_RE = re.compile(r"\bclusters?\s+of\s+seizures?\b", re.I)
_GENERIC_SEIZURE_NAMES = frozenset({"seizure", "seizures"})
_CLUSTER_NAME = "cluster of seizures"


def _cluster_name_for(text: str, evidence: str) -> str | None:
    if _fold_span(text) not in _GENERIC_SEIZURE_NAMES:
        return None
    if _CLUSTER_OF_SEIZURES_RE.search(evidence):
        return _CLUSTER_NAME
    return None


def _apply_cluster_name(
    projected: list[dict[str, Any]],
    item: MentionItem,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _rewrite_projected_name(
        projected,
        item,
        index,
        name=_cluster_name_for(item.text, item.evidence),
        action="form_recovery.cluster_name",
    )


_AWARENESS_PHRASE_RE = re.compile(
    r"\bfocal seizures with (?:altered|impaired) awareness\b|"
    r"\bfocal impaired awareness seizures\b",
    re.I,
)
_WITHOUT_AWARENESS_RE = re.compile(r"\bwithout\b.{0,40}\bawareness\b", re.I)
_AWARENESS_NAME = "focal seizures with altered awareness"


def _awareness_name_for(text: str, evidence: str) -> str | None:
    if _fold_span(text) != "focal seizures":
        return None
    if _WITHOUT_AWARENESS_RE.search(_fold_span(evidence)):
        return None
    if _AWARENESS_PHRASE_RE.search(evidence):
        return _AWARENESS_NAME
    return None


def _apply_awareness_name(
    projected: list[dict[str, Any]],
    item: MentionItem,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _rewrite_projected_name(
        projected,
        item,
        index,
        name=_awareness_name_for(item.text, item.evidence),
        action="form_recovery.awareness_name",
    )


def _rewrite_projected_name(
    projected: list[dict[str, Any]],
    item: MentionItem,
    index: int,
    *,
    name: str | None,
    action: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if name is None:
        return projected, []
    rewritten: list[dict[str, Any]] = []
    for row in projected:
        attrs = {
            str(key): str(value)
            for key, value in dict(row.get("attributes") or {}).items()
        }
        cui = assign_cui(name)
        if cui:
            attrs["CUI"] = cui
            attrs["CUIPhrase"] = name
        rewritten.append({**row, "text": name, "attributes": attrs})
    return rewritten, [
        {
            "fact_index": index,
            "rule_category": "seizure_frequency",
            "action": action,
            "evidence": item.evidence,
            "before": {"text": item.text},
            "after": {"text": name},
            "changed": True,
            "first_prediction_changing_owner": "deterministic",
        }
    ]


def _fold_span(text: str) -> str:
    return " ".join(text.casefold().replace("-", " ").split())


def _span_in_letter(note_text: str, span: str, *, mode: str) -> bool:
    if not span:
        return False
    if evidence_is_substring(note_text, span):
        return True
    if mode == "casefold":
        return span.casefold() in note_text.casefold()
    if mode == "span_fold":
        return _fold_span(span) in _fold_span(note_text)
    return False


def _first_text(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in {None, ""}:
            return value
    return ""


def _llm_coding_fields(
    family: str,
    raw: dict[str, Any],
    extra: list[str],
    errors: list[str],
    index: int,
) -> dict[str, str]:
    allowed = _LLM_CODING_FIELDS[family]
    working = _flatten_attribute_object(raw.get("attributes"), errors, index)
    unused = [key for key in extra if key not in allowed]
    if unused:
        errors.append(f"dropped_unused_keys: item[{index}] {unused}")
    for key in allowed:
        if key in raw and key not in working:
            working[key] = raw[key]
    kept = {key: working[key] for key in allowed if key in working}
    return _stringify_attributes(kept, errors, index)


def _llm_project(item: MentionItem) -> tuple[list[dict[str, Any]], str, str]:
    owner = "model.mention_unit"
    if item.family == PRESCRIPTION.name and _is_noncurrent(item.attributes):
        return [], "semantic_only_noncurrent_status", owner
    pending = item.family == INVESTIGATIONS.name and _is_pending(
        item.attributes, item.text, item.evidence
    )
    if pending:
        return [], "semantic_only_pending_investigation", owner
    text = _adapter_text(item)
    if item.family == INVESTIGATIONS.name and text not in _MODALITY_NAMES:
        return [], "semantic_only_nontarget_or_no_result", owner
    attributes = _llm_legacy(item, text)
    if not text:
        return [], "partial", owner
    return (
        [
            {
                "entity": item.family,
                "text": text,
                "attributes": attributes,
                "evidence": item.evidence,
                "component_owner": owner,
            }
        ],
        "materialized" if attributes else "partial",
        owner,
    )


def _hybrid_project(
    item: MentionItem,
    index: int,
    *,
    form_recovery: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if form_recovery and item.family == SEIZURE_FREQUENCY.name:
        return project_leftover_form_sf(
            text=item.text,
            evidence=item.evidence,
            index=index,
        )
    if form_recovery and item.family == INVESTIGATIONS.name:
        return project_leftover_form_investigation(
            text=item.text, evidence=item.evidence, index=index
        )
    if item.family == DIAGNOSIS.name:
        phrases = _heading_split_phrases(item.text)
        if phrases:
            mentions: list[dict[str, Any]] = []
            traces: list[dict[str, Any]] = [
                {
                    "fact_index": index,
                    "rule_category": "clinical_epilepsy",
                    "action": "convention_split_heading",
                    "evidence": item.evidence,
                    "before": {"text": item.text},
                    "after": {"phrases": list(phrases)},
                    "changed": True,
                    "first_prediction_changing_owner": "deterministic",
                }
            ]
            for phrase in phrases:
                projected, phrase_traces, _status = project_hybrid_event(
                    family=item.family,
                    event=phrase,
                    evidence=item.evidence,
                    index=index,
                    dual_family=False,
                )
                mentions.extend(projected)
                traces.extend(phrase_traces)
            return mentions, traces, "materialized" if mentions else "partial"
        return project_hybrid_event(
            family=item.family,
            event=item.text,
            evidence=item.evidence,
            index=index,
            dual_family=False,
        )
    if item.family == PRESCRIPTION.name:
        if form_recovery:
            split = project_rx_split_once_daily(
                name=item.text, evidence=item.evidence, index=index
            )
            if split is not None:
                return split
        return project_hybrid_event(
            family=item.family,
            event=f"{item.text} {item.evidence}".strip(),
            evidence=item.evidence,
            index=index,
            dual_family=False,
        )
    if item.family == INVESTIGATIONS.name:
        return project_hybrid_event(
            family=item.family,
            event=f"{item.text} {item.evidence}".strip(),
            evidence=item.evidence,
            index=index,
            dual_family=False,
        )
    return _hybrid_sf_project(item, index)


def _hybrid_sf_project(
    item: MentionItem,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    haystack = f"{item.text} {item.evidence}".strip()
    traces: list[dict[str, Any]] = []
    if _is_uncoded_phenomenology(haystack, {}):
        traces.append(
            {
                "fact_index": index,
                "rule_category": "seizure_frequency",
                "action": "suppress_uncoded_or_noise_sf",
                "evidence": item.evidence,
                "before": {"text": item.text},
                "after": {},
                "changed": True,
                "first_prediction_changing_owner": "deterministic",
            }
        )
        return [], traces, "semantic_only_uncoded_phenomenology"
    seed = {
        "entity": SEIZURE_FREQUENCY.name,
        "text": item.text.strip(),
        "attributes": {},
        "evidence": item.evidence,
    }
    rewritten, actions = sf_encoding.apply_sf_attribute_encoding([seed])
    for action in actions:
        traces.append(
            {
                "fact_index": index,
                "rule_category": "seizure_frequency",
                "action": str(action.get("rule_id") or action.get("action") or ""),
                "evidence": item.evidence,
                "before": {"text": item.text},
                "after": dict(rewritten[0].get("attributes", {})) if rewritten else {},
                "changed": True,
                "first_prediction_changing_owner": "deterministic",
            }
        )
    mentions: list[dict[str, Any]] = []
    for row in rewritten:
        mention = dict(row)
        mention["evidence"] = item.evidence
        mention.setdefault("component_owner", "deterministic_sf_attribute_encoding")
        mentions.append(mention)
    return mentions, traces, "materialized" if mentions else "partial"


def _adapter_text(item: MentionItem) -> str:
    if item.family == PRESCRIPTION.name:
        lowered = item.text.lower()
        matches = [
            surface for surface in PRESCRIPTION_SURFACE_FORMS if surface.lower() in lowered
        ]
        return max(matches, key=len) if matches else item.text.strip()
    if item.family == INVESTIGATIONS.name:
        lowered = item.text.upper()
        for modality in ("MRI", "EEG", "CT"):
            if modality in lowered:
                return modality
        return ""
    return item.text.strip()


def _llm_legacy(item: MentionItem, text: str) -> dict[str, str]:
    attrs = {
        str(key).lower(): str(value)
        for key, value in item.attributes.items()
        if value is not None
    }
    source = f"{item.text} {item.evidence}"
    if item.family == DIAGNOSIS.name:
        result = {
            "DiagCategory": diagnosis_category_for_concept(text),
            "Certainty": _certainty(attrs.get("certainty", "")),
            "Negation": _negation(attrs.get("negation", "")),
        }
        return {key: value for key, value in result.items() if value}
    if item.family == PRESCRIPTION.name:
        mapped: dict[str, str] = {"DrugName": text}
        if attrs.get("dose"):
            mapped["DrugDose"] = attrs["dose"]
        if attrs.get("unit"):
            mapped["DoseUnit"] = _dose_unit(attrs["unit"])
        if attrs.get("schedule"):
            mapped["Frequency"] = _frequency(attrs["schedule"])
        return {key: value for key, value in mapped.items() if value}
    if item.family == INVESTIGATIONS.name:
        finding = attrs.get("result", "").strip().lower()
        legacy = {f"{text}_Performed": "Yes"}
        if finding in {"normal", "abnormal", "unknown"}:
            legacy[f"{text}_Results"] = finding.title()
        return legacy
    legacy = _sf_attributes_to_legacy(attrs, source=source)
    since = attrs.get("since_or_during", "").strip().title()
    if since in {"Since", "During"}:
        legacy.setdefault("TimeSince_or_TimeOfEvent", since)
    if "TimePeriod" in legacy:
        legacy["TimePeriod"] = normalize_unit(legacy["TimePeriod"])
    change = str(legacy.get("FrequencyChange") or "").strip().title()
    if change in _FREQUENCY_CHANGE:
        legacy["FrequencyChange"] = change
    point = _point_in_time(attrs.get("point_in_time", ""))
    if point:
        legacy["PointInTime"] = point
    return legacy


def _point_in_time(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    if raw in {
        "Birthday",
        "DrugChange",
        "LastClinic",
        "Last_Month",
        "Last_Week",
        "Last_Year",
        "Surgery",
    }:
        return raw
    return _POINT_IN_TIME.get(raw.lower().replace("-", " ")) or ""


def _is_noncurrent(attributes: dict[str, Any]) -> bool:
    status = str(attributes.get("status", "")).lower().strip()
    return status in {
        "planned",
        "past",
        "historical",
        "stopped",
        "discontinued",
        "resolved",
    }


def _is_pending(attributes: dict[str, Any], text: str, evidence: str) -> bool:
    status = str(attributes.get("status", "")).lower().strip()
    if status in {"planned", "requested", "future"}:
        return True
    haystack = f"{text} {evidence}"
    return bool(
        any(token in haystack.lower() for token in ("plan", "planned", "arrange", "request"))
        and any(modality in haystack.upper() for modality in _MODALITY_NAMES)
    )


__all__ = [
    "HYBRID_METHOD",
    "LLM_METHOD",
    "MENTION_UNIT_MODEL",
    "COMBO_ARM_VERSIONS",
    "CUE5_ARM_VERSIONS",
    "MENTION_UNIT_PROMPT_VERSION",
    "MENTION_UNIT_PROMPT_VERSION_V2",
    "MENTION_ENCODER_PROMPT",
    "SYSTEM_MESSAGE",
    "mention_unit_prompt_version",
    "selection_cues_for",
    "MentionItem",
    "MentionUnitExtractor",
    "MentionUnitParseResult",
    "MentionUnitRecord",
    "build_mention_unit_prompt",
    "materialize_mention_unit",
    "parse_mention_unit_json",
]
