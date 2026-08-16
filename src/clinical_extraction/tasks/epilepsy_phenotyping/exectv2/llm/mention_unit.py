"""Mention-unit v1 ExECT research lane.

Both methods emit exact letter spans. The llm lane also fills family-specific
coding fields. Hybrid may rewrite, project, or suppress that item only. It
does not search the letter or change the selected ExECT method.
"""

from __future__ import annotations

import json
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)

from .pipelines.key_entities_structured import records as structured_records
from .semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    InventoryMaterialization,
    _apply_hybrid_letter_rules,
    _certainty,
    _coerce_text,
    _dose_unit,
    _flatten_attribute_object,
    _frequency,
    _negation,
    _normalize_family,
    _sf_attributes_to_legacy,
    _stringify_attributes,
)
from .semantic_inventory_rules import _heading_split_phrases, project_hybrid_event
from .semantic_inventory_trust import project_trust_hybrid
from .shared.json_parse import parse_json_payload
from .shared.mention_pipeline import check_evidence

MENTION_UNIT_PROMPT_VERSION = "exectv2_mention_unit_v1"
MENTION_UNIT_MODEL = "openai/gpt-5.6-luna"
SYSTEM_MESSAGE = (
    "Extract the current mentions as exact letter spans. "
    "Return the requested JSON exactly."
)
_LLM_CODING_FIELDS = {
    DIAGNOSIS.name: ("certainty", "negation"),
    SEIZURE_FREQUENCY.name: (
        "count",
        "lower_count",
        "upper_count",
        "period",
        "state",
    ),
    PRESCRIPTION.name: ("dose", "unit", "schedule", "status"),
    INVESTIGATIONS.name: ("result", "status"),
}
_SHARED_ITEM_KEYS = frozenset({"family", "text", "evidence", "attributes"})
_MODALITY_NAMES = frozenset({"MRI", "CT", "EEG"})


class MentionItem(BaseModel):
    """One model-emitted mention unit."""

    model_config = ConfigDict(extra="ignore")

    family: str
    text: str = ""
    evidence: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)


class MentionUnitRecord(BaseModel):
    """The mention-unit envelope after transport parsing."""

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


class MentionUnitChatAdapter(ChatAdapter):
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


class MentionUnitSignature(dspy.Signature):
    """Read one clinical letter and return the current mention units."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and the extraction instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc="One JSON object with an items list that follows the supplied output schema."
    )


class MentionUnitExtractor(dspy.Module):
    """One-call model program for either mention-unit method contract."""

    def __init__(self, *, method: Literal["llm", "llm_with_rules"]) -> None:
        super().__init__()
        if method not in {LLM_METHOD, HYBRID_METHOD}:
            raise ValueError(f"unknown mention-unit method: {method!r}")
        self.method = method
        self.predict = dspy.Predict(MentionUnitSignature)
        self._adapter = MentionUnitChatAdapter()

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        with dspy.context(adapter=self._adapter):
            return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        return self._adapter.format(
            MentionUnitSignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )


def build_mention_unit_prompt(
    letter: ExectLetter,
    *,
    method: Literal["llm", "llm_with_rules"],
) -> str:
    """Build the model-facing payload without research metadata."""

    if method not in {LLM_METHOD, HYBRID_METHOD}:
        raise ValueError(f"unknown mention-unit method: {method!r}")
    if method == LLM_METHOD:
        item_schema: Any = [
            {
                "family": "Diagnosis",
                "text": "Exact named epilepsy or seizure span copied from the letter.",
                "evidence": "Exact letter span that supports this mention.",
                "certainty": "certain, probable, possible, or uncertain.",
                "negation": "affirmed or negated.",
            },
            {
                "family": "SeizureFrequency",
                "text": "Exact seizure, absence, or myoclonic-jerk span copied from the letter.",
                "evidence": "Exact letter span that supports this mention.",
                "count": "Number of seizures when the letter states a number.",
                "lower_count": "Lower count when the letter states a range.",
                "upper_count": "Upper count when the letter states a range.",
                "period": "day, week, month, or year when the letter states a rate basis.",
                "state": "current, historical, seizure-free, or last-event.",
            },
            {
                "family": "Prescription",
                "text": "Exact drug or compact regimen span copied from the letter.",
                "evidence": "Exact letter span that supports this mention.",
                "dose": "Dose amount when stated.",
                "unit": "Dose unit when stated.",
                "schedule": "How often the drug is taken.",
                "status": "current, planned, past, or completed.",
            },
            {
                "family": "Investigations",
                "text": "Exact completed MRI, CT, or EEG span copied from the letter.",
                "evidence": "Exact letter span that supports this mention.",
                "result": "normal, abnormal, or unknown when the letter states a result.",
                "status": "completed or planned.",
            },
        ]
        task = (
            "Read the letter once. Return one list of current mentions. Each item "
            "is an exact letter span. If a family has no current mention, return "
            "nothing for that family. One item is one mention. A fact that belongs "
            "to two families is two items; they may share evidence. For each item, "
            "also fill only the coding fields for that family."
        )
    else:
        item_schema = {
            "family": "Diagnosis | SeizureFrequency | Prescription | Investigations",
            "text": "Exact letter span for this mention.",
            "evidence": "Exact letter span that supports this mention.",
        }
        task = (
            "Read the letter once. Return one list of current mentions. Each item "
            "is an exact letter span. If a family has no current mention, return "
            "nothing for that family. One item is one mention. A fact that belongs "
            "to two families is two items; they may share evidence. Return only "
            "family, text, and evidence."
        )
    payload = {
        "task": task,
        "output_schema": {"items": item_schema},
        "family_guidance": {
            "Diagnosis": (
                "Bare absences or myoclonic jerks are not diagnosis mentions. "
                "Named absence seizures or myoclonic seizures are. Do not emit "
                "epilepsy from driving, counselling, or a general discussion "
                "unless the letter attaches it to this patient. A named type "
                "with a zero count is still an affirmed diagnosis mention."
            ),
            "SeizureFrequency": (
                "May use seizures, a named type, absences, or myoclonic jerks. "
                "Do not use events, episodes, or slang. A named type with a "
                "zero count is a seizure-frequency item of 0."
            ),
            "Prescription": (
                "Current anti-seizure regimens only. Rescue may lack a dose. "
                "If the sentence says same dose and does not state the dose, "
                "omit the drug."
            ),
            "Investigations": (
                "Emit a completed MRI, CT, or EEG only when the letter states "
                "a result. Do not assume EEG type."
            ),
        },
        "letter_text": letter.note_text,
    }
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
        family = _normalize_family(raw.get("family"))
        if family is None:
            errors.append(f"dropped_unknown_family: item[{index}]")
            continue
        text = _coerce_text(
            raw.get("text") if raw.get("text") not in {None, ""} else raw.get("event"),
            errors,
            f"item[{index}].text",
        )
        if not raw.get("text") and raw.get("event"):
            errors.append(f"missing_text_used_event: item[{index}]")
        evidence = _coerce_text(raw.get("evidence"), errors, f"item[{index}].evidence")
        extra = sorted(
            str(key)
            for key in raw
            if key not in _SHARED_ITEM_KEYS and key != "event"
        )
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
) -> InventoryMaterialization:
    """Create semantic and scorer views while retaining every emitted item."""

    semantic_facts: list[dict[str, Any]] = []
    rule_trace: list[dict[str, Any]] = []
    warnings: list[str] = []
    candidates: list[PredictedMention] = []
    evidence_invalid = 0
    for index, item in enumerate(record.items):
        text_valid = bool(item.text and evidence_is_substring(letter.note_text, item.text))
        evidence_valid = bool(
            item.evidence and evidence_is_substring(letter.note_text, item.evidence)
        )
        semantic_row = {
            "fact_index": index,
            "family": item.family,
            "text": item.text,
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

        if method == LLM_METHOD:
            projected, status, owner = _llm_project(item)
        else:
            projected, traces, status = _hybrid_project(item, index)
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
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
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
        return project_hybrid_event(
            family=item.family,
            event=item.text,
            evidence=item.evidence,
            index=index,
            dual_family=False,
        )
    haystack = f"{item.text} {item.evidence}".strip()
    projected, traces, status = project_trust_hybrid(
        family=item.family,
        event=haystack,
        evidence=item.evidence,
        index=index,
    )
    if item.family == SEIZURE_FREQUENCY.name:
        rewritten: list[dict[str, Any]] = []
        for row in projected:
            mention = dict(row)
            mention["text"] = item.text
            rewritten.append(mention)
        return rewritten, traces, status
    return projected, traces, status


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
    return _sf_attributes_to_legacy(attrs, source=source)


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
    "MENTION_UNIT_PROMPT_VERSION",
    "SYSTEM_MESSAGE",
    "MentionItem",
    "MentionUnitExtractor",
    "MentionUnitParseResult",
    "MentionUnitRecord",
    "build_mention_unit_prompt",
    "materialize_mention_unit",
    "parse_mention_unit_json",
]
