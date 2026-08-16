"""Semantic-inventory ExECT research lane.

This module is deliberately parallel to the selected structured-event stack.
Fork A v4 uses one list of clinical events. The llm lane also emits coded
mention attributes. Hybrid rules parse the event string only, then may split
or rewrite from a closed table. It does not change the selected ExECT method.
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
    DIAGNOSIS_SURFACE_FORMS,
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
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    parse_json_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    check_evidence,
)

from .mention_unit_shared import (
    HYBRID_METHOD,
    LLM_METHOD,
    InventoryMaterialization,
    _apply_hybrid_letter_rules,
    _certainty,
    _coerce_text,
    _dose_unit,
    _frequency,
    _negation,
    _normalize_family,
    _sf_attributes_to_legacy,
    _stringify_attributes,
    project_hybrid_event,
)
from .pipelines.key_entities_structured import records as structured_records
from .semantic_inventory_trust import (
    project_trust_hybrid,
    project_trust_llm_mentions,
)

SEMANTIC_PROMPT_VERSION = "exectv2_semantic_inventory_v4"
SEMANTIC_MODEL = "openai/gpt-5.6-luna"
SYSTEM_MESSAGE = (
    "Extract the current clinical events from the supplied letter. "
    "Return the requested JSON exactly."
)
SEMANTIC_FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)

_SF_PHRASES = (
    "focal seizures with altered awareness",
    "focal seizures with loss of awareness",
    "focal impaired awareness seizures",
    "focal to bilateral convulsive seizures",
    "secondary generalised seizures",
    "generalised tonic clonic seizures",
    "complex partial seizures",
    "myoclonic jerks",
    "absence like seizures",
    "seizure freedom",
    "seizure free",
    "no further seizures",
    "seizures",
    "seizure",
)

_MODALITY_RE = re.compile(r"\b(MRI|CT|EEG)\b", re.I)

_LLM_ATTRIBUTE_SCHEMA = {
    "concept": "Named diagnosis or seizure-type phrase.",
    "certainty": "certain, probable, possible, or uncertain.",
    "negation": "affirmed or negated.",
    "type": "Seizure type when this is a rate or last-event fact.",
    "state": "current, historical, seizure-free, or last-event.",
    "count": "Number of seizures when the letter states a number.",
    "lower_count": "Lower count when the letter states a range.",
    "upper_count": "Upper count when the letter states a range.",
    "period": "day, week, month, or year when the letter states a rate basis.",
    "timeframe": "When the rate or last event applies.",
    "name": "Drug name or investigation name.",
    "dose": "Dose amount when stated.",
    "unit": "Dose unit when stated.",
    "schedule": "How often the drug is taken.",
    "status": "current, planned, past, or completed.",
    "result": "normal, abnormal, or unknown for a completed test.",
    "action": "continue, start, stop, or change.",
}


class SemanticFact(BaseModel):
    """One model-emitted coded inventory item."""

    model_config = ConfigDict(extra="ignore")

    family: str
    event: str = ""
    evidence: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)


class SemanticInventoryRecord(BaseModel):
    """The shared inventory envelope after transport parsing."""

    model_config = ConfigDict(extra="ignore")

    facts: list[SemanticFact] = Field(default_factory=list)


@dataclass(frozen=True)
class InventoryParseResult:
    record: SemanticInventoryRecord | None
    errors: list[str] = field(default_factory=list)
    forbidden_fields: list[dict[str, Any]] = field(default_factory=list)


def _system_message() -> str:
    return SYSTEM_MESSAGE


class SemanticInventoryChatAdapter(ChatAdapter):
    """Keep DSPy's parser while using a short, plain system message."""

    def format(
        self,
        signature: type[dspy.Signature],
        demos: list[dict[str, object]],
        inputs: dict[str, object],
    ) -> list[dict[str, object]]:
        messages = super().format(signature, demos, inputs)
        messages[0] = {"role": "system", "content": _system_message()}
        return messages


class SemanticInventorySignature(dspy.Signature):
    """Read one clinical letter and return the current coded inventory."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and the extraction instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc="One JSON object with a facts list that follows the supplied output schema."
    )


class SemanticInventoryExtractor(dspy.Module):
    """One-call model program for either semantic method contract."""

    def __init__(self, *, method: Literal["llm", "llm_with_rules"]) -> None:
        super().__init__()
        if method not in {LLM_METHOD, HYBRID_METHOD}:
            raise ValueError(f"unknown semantic method: {method!r}")
        self.method = method
        self.predict = dspy.Predict(SemanticInventorySignature)
        self._adapter = SemanticInventoryChatAdapter()

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        with dspy.context(adapter=self._adapter):
            return self.predict(prompt_input_json=prompt_input_json)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        return self._adapter.format(
            SemanticInventorySignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )


def build_inventory_prompt(
    letter: ExectLetter,
    *,
    method: Literal["llm", "llm_with_rules"],
) -> str:
    """Build the model-facing payload without research metadata."""

    if method not in {LLM_METHOD, HYBRID_METHOD}:
        raise ValueError(f"unknown semantic method: {method!r}")
    if method == LLM_METHOD:
        fact_schema: dict[str, Any] = {
            "family": "Diagnosis | SeizureFrequency | Prescription | Investigations",
            "event": "One current clinical event in ordinary language.",
            "evidence": "Exact clause copied from the letter that supports this event.",
            "attributes": dict(_LLM_ATTRIBUTE_SCHEMA),
        }
        task = (
            "Read the letter once. Return one list of current clinical events for "
            "diagnosis, seizure frequency, medicines, and completed tests. If a "
            "family has no current item, return nothing for that family. For each "
            "event, also fill the attributes. Several events may share evidence."
        )
    else:
        fact_schema = {
            "family": "Diagnosis | SeizureFrequency | Prescription | Investigations",
            "event": "One current clinical event in ordinary language.",
            "evidence": "Exact clause copied from the letter that supports this event.",
        }
        task = (
            "Read the letter once. Return one list of current clinical events for "
            "diagnosis, seizure frequency, medicines, and completed tests. If a "
            "family has no current item, return nothing for that family. Return "
            "only family, event, and evidence. Several events may share evidence."
        )
    payload = {
        "task": task,
        "output_schema": {"facts": [fact_schema]},
        "family_guidance": {
            "Diagnosis": (
                "Named epilepsy and seizure types that apply now. Put seizure types "
                "here. Do not add clumsiness, collapse, or aura-only descriptions."
            ),
            "SeizureFrequency": (
                "Current rates, counts, and seizure-free states. If the last seizure "
                "was long ago, write it as a current zero-count event and use the "
                "named type when the letter names one. Do not add symptoms with no "
                "rate or last event."
            ),
            "Prescription": (
                "Current drug regimens. Do not add a planned drug that has not "
                "started."
            ),
            "Investigations": (
                "Completed tests and their results. Do not add planned or requested "
                "tests."
            ),
        },
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False)


def parse_inventory_json(
    raw_output: str,
    *,
    method: Literal["llm", "llm_with_rules"],
) -> InventoryParseResult:
    """Parse transport JSON and record method-contract violations."""

    if not raw_output.strip():
        return InventoryParseResult(None, ["not_run"])
    try:
        payload, dialect_notes = parse_json_payload(
            raw_output,
            schema_repair=True,
            preferred_roots=("facts",),
        )
    except Exception as exc:
        return InventoryParseResult(None, [f"invalid_json: {exc}"])
    if isinstance(payload, list):
        payload = {"facts": payload}
        dialect_notes = [*dialect_notes, "coerced_top_level_fact_array"]
    if not isinstance(payload, dict) or not isinstance(payload.get("facts"), list):
        return InventoryParseResult(
            None, [*dialect_notes, "schema_validation_error: facts must be a list"]
        )

    errors = list(dialect_notes)
    facts: list[SemanticFact] = []
    forbidden: list[dict[str, Any]] = []
    for index, raw_fact in enumerate(payload["facts"]):
        if not isinstance(raw_fact, dict):
            errors.append(f"schema_validation_error: fact[{index}] must be an object")
            continue
        raw = dict(raw_fact)
        family = _normalize_family(raw.get("family"))
        if family is None:
            errors.append(f"dropped_unknown_family: fact[{index}]")
            continue
        if method == HYBRID_METHOD:
            extra = sorted(str(key) for key in raw if key not in {"family", "event", "evidence"})
            if extra:
                forbidden.append({"fact_index": index, "fields": extra})
                errors.append(f"forbidden_model_fields: fact[{index}] {extra}")
            attributes: dict[str, Any] = {}
        else:
            attributes = _stringify_attributes(raw.get("attributes"), errors, index)
        event = _coerce_text(raw.get("event"), errors, f"fact[{index}].event")
        evidence = _coerce_text(raw.get("evidence"), errors, f"fact[{index}].evidence")
        facts.append(
            SemanticFact(
                family=family,
                event=event,
                evidence=evidence,
                attributes=attributes,
            )
        )
    return InventoryParseResult(SemanticInventoryRecord(facts=facts), errors, forbidden)


def materialize_inventory(
    letter: ExectLetter,
    record: SemanticInventoryRecord,
    *,
    method: Literal["llm", "llm_with_rules"],
    disabled_rule_families: set[str] | None = None,
    projection: Literal["v4", "trust_item"] = "v4",
) -> InventoryMaterialization:
    """Create semantic and scorer views while retaining every emitted fact."""

    semantic_facts: list[dict[str, Any]] = []
    rule_trace: list[dict[str, Any]] = []
    warnings: list[str] = []
    candidates: list[PredictedMention] = []
    evidence_invalid = 0
    disabled_rule_families = disabled_rule_families or set()
    for index, fact in enumerate(record.facts):
        semantic_row = {
            "fact_index": index,
            "family": fact.family,
            "event": fact.event,
            "evidence": fact.evidence,
            "evidence_valid": bool(
                fact.evidence and evidence_is_substring(letter.note_text, fact.evidence)
            ),
            "attributes": dict(fact.attributes),
        }
        if not semantic_row["evidence_valid"]:
            evidence_invalid += 1
            warnings.append(f"fact[{index}]: evidence_not_substring")
            semantic_facts.append(semantic_row)
            continue

        if method == LLM_METHOD:
            if projection == "trust_item" and fact.family in {
                SEIZURE_FREQUENCY.name,
                INVESTIGATIONS.name,
            }:
                projected, status = project_trust_llm_mentions(
                    family=fact.family,
                    event=fact.event,
                    evidence=fact.evidence,
                    attributes=dict(fact.attributes),
                )
                first = projected[0] if projected else {}
                semantic_row["legacy_attributes"] = dict(first.get("attributes", {}))
                semantic_row["scorer_text"] = str(first.get("text", ""))
                semantic_row["projection_status"] = status
                semantic_facts.append(semantic_row)
                if not projected:
                    warnings.append(f"fact[{index}]: no_scorer_text")
                    continue
                for item in projected:
                    candidates.append(
                        PredictedMention(
                            entity=str(item["entity"]),
                            text=str(item["text"]),
                            attributes={
                                str(key): str(value) for key, value in item["attributes"].items()
                            },
                            evidence=str(item.get("evidence") or fact.evidence),
                            component_owner=str(item.get("component_owner") or ""),
                        )
                    )
                continue
            attributes, text, status, owner = _llm_project(fact)
        elif fact.family in disabled_rule_families:
            attributes = {}
            text = ""
            status = "ablation_disabled"
            owner = f"ablation.disabled_rules.{fact.family}"
            rule_trace.append(
                {
                    "fact_index": index,
                    "rule_category": "ablation",
                    "action": "skip_named_family_rule_group",
                    "evidence": fact.evidence,
                    "before": {},
                    "after": {},
                    "changed": False,
                    "first_prediction_changing_owner": None,
                }
            )
        else:
            if projection == "trust_item":
                projected, traces, status = project_trust_hybrid(
                    family=fact.family,
                    event=fact.event,
                    evidence=fact.evidence,
                    index=index,
                )
            else:
                projected, traces, status = project_hybrid_event(
                    family=fact.family,
                    event=fact.event,
                    evidence=fact.evidence,
                    index=index,
                )
            rule_trace.extend(traces)
            first = projected[0] if projected else {}
            semantic_row["legacy_attributes"] = dict(first.get("attributes", {}))
            semantic_row["scorer_text"] = str(first.get("text", ""))
            semantic_row["projection_status"] = status
            semantic_facts.append(semantic_row)
            if not projected:
                warnings.append(f"fact[{index}]: no_scorer_text")
                continue
            for item in projected:
                candidates.append(
                    PredictedMention(
                        entity=str(item["entity"]),
                        text=str(item["text"]),
                        attributes={
                            str(key): str(value) for key, value in item["attributes"].items()
                        },
                        evidence=str(item.get("evidence") or fact.evidence),
                        component_owner=str(item.get("component_owner") or ""),
                    )
                )
            continue

        semantic_row["legacy_attributes"] = dict(attributes)
        semantic_row["scorer_text"] = text
        semantic_row["projection_status"] = status
        semantic_facts.append(semantic_row)
        if not text:
            warnings.append(f"fact[{index}]: no_scorer_text")
            continue
        candidates.append(
            PredictedMention(
                entity=fact.family,
                text=text,
                attributes=attributes,
                evidence=fact.evidence,
                component_owner=owner,
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


def _llm_project(fact: SemanticFact) -> tuple[dict[str, str], str, str, str]:
    attributes = _llm_attributes_to_legacy(fact)
    text = _fact_text(fact)
    owner = "model.semantic_inventory"
    if fact.family == PRESCRIPTION.name and _is_noncurrent_prescription(fact):
        return attributes, "", "semantic_only_noncurrent_status", owner
    if fact.family == INVESTIGATIONS.name and _is_pending_investigation_text(
        text, fact.evidence, attributes
    ):
        return attributes, "", "semantic_only_pending_investigation", owner
    status = "materialized" if text and attributes else "partial"
    return attributes, text, status, owner


def _fact_text(fact: SemanticFact) -> str:
    """Select a source-near phrase for scorer projection without adding facts."""

    if fact.family == PRESCRIPTION.name:
        return (
            _longest_surface(fact.event, PRESCRIPTION_SURFACE_FORMS)
            or fact.attributes.get("name", "")
            or fact.event.strip()
        )
    if fact.family == DIAGNOSIS.name:
        return (
            _longest_surface(fact.event, DIAGNOSIS_SURFACE_FORMS)
            or fact.attributes.get("concept", "")
            or fact.event.strip()
        )
    if fact.family == SEIZURE_FREQUENCY.name:
        return (
            _longest_surface(fact.event, _SF_PHRASES)
            or str(fact.attributes.get("type", ""))
            or fact.event.strip()
        )
    modality = _modality(fact.event)
    return modality or str(fact.attributes.get("name", "")).upper() or fact.event.strip()


def _longest_surface(source: str, surfaces: tuple[str, ...] | list[str]) -> str:
    lowered = source.lower()
    matches = [surface for surface in surfaces if surface.lower() in lowered]
    return max(matches, key=len) if matches else ""


def _modality(text: str) -> str:
    match = _MODALITY_RE.search(text)
    return match.group(1).upper() if match else ""


def _llm_attributes_to_legacy(fact: SemanticFact) -> dict[str, str]:
    attrs = {
        str(key).lower(): str(value) for key, value in fact.attributes.items() if value is not None
    }
    source = fact.event
    if fact.family == DIAGNOSIS.name:
        concept = attrs.get("concept") or attrs.get("diagnosis") or _fact_text(fact)
        result = {
            "DiagCategory": diagnosis_category_for_concept(concept),
            "Certainty": _certainty(attrs.get("certainty", "")),
            "Negation": _negation(attrs.get("negation", attrs.get("assertion", ""))),
        }
        return {key: value for key, value in result.items() if value}
    if fact.family == PRESCRIPTION.name:
        mapped: dict[str, str] = {}
        drug_name = attrs.get("name") or attrs.get("medication") or attrs.get("drug") or ""
        if drug_name:
            mapped["DrugName"] = drug_name
        dose_value = attrs.get("dose") or attrs.get("amount") or ""
        if dose_value:
            mapped["DrugDose"] = dose_value
        if attrs.get("unit"):
            mapped["DoseUnit"] = _dose_unit(attrs["unit"])
        schedule = attrs.get("schedule") or attrs.get("frequency") or attrs.get("dose_frequency")
        if schedule:
            mapped["Frequency"] = _frequency(schedule)
        return {key: value for key, value in mapped.items() if value}
    if fact.family == INVESTIGATIONS.name:
        modality = (
            attrs.get("name")
            or attrs.get("modality")
            or attrs.get("investigation")
            or _modality(source)
        ).upper()
        finding = attrs.get("result", attrs.get("finding", "")).strip().lower()
        legacy: dict[str, str] = {}
        pending_status = attrs.get("status", "").lower() in {"planned", "requested", "future"}
        if modality in {"MRI", "CT", "EEG"} and not pending_status:
            legacy[f"{modality}_Performed"] = "Yes"
            if finding in {"normal", "abnormal", "unknown"}:
                legacy[f"{modality}_Results"] = finding.title()
            if attrs.get("type") and modality == "EEG":
                legacy["EEG_Type"] = attrs["type"]
        return legacy
    return _sf_attributes_to_legacy(attrs, source=source)


def _is_noncurrent_prescription(fact: SemanticFact) -> bool:
    status = str(fact.attributes.get("status", "")).lower().strip()
    return status in {"planned", "past", "historical", "stopped", "discontinued", "resolved"}


def _is_pending_investigation_text(
    text: str, evidence: str, attributes: dict[str, str]
) -> bool:
    return sd.is_pending_investigation(text, evidence=text or evidence, attributes=attributes)


__all__ = [
    "HYBRID_METHOD",
    "InventoryMaterialization",
    "InventoryParseResult",
    "LLM_METHOD",
    "SEMANTIC_MODEL",
    "SEMANTIC_PROMPT_VERSION",
    "SYSTEM_MESSAGE",
    "SemanticFact",
    "SemanticInventoryExtractor",
    "SemanticInventoryRecord",
    "build_inventory_prompt",
    "materialize_inventory",
    "parse_inventory_json",
]
