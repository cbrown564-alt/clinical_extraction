"""Semantic-inventory ExECT research lane.

This module is deliberately parallel to the selected structured-event stack.
Fork A asks the model for the current coded four-family inventory, then keeps
semantic parsing, named hybrid rewrite, benchmark projection, and attribution
visible. It does not change the selected ExECT method or its default prompt.
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
    diagnosis_concept,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    parse_json_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    check_evidence,
)

from .pipelines.key_entities_structured import records as structured_records

LLM_METHOD = "llm"
HYBRID_METHOD = "llm_with_rules"
SEMANTIC_PROMPT_VERSION = "exectv2_semantic_inventory_v3"
SEMANTIC_MODEL = "openai/gpt-5.6-luna"
SYSTEM_MESSAGE = (
    "Extract the current coded clinical inventory from the supplied letter. "
    "Return the requested JSON exactly."
)
SEMANTIC_FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)

_FAMILY_ALIASES = {
    "diagnosis": DIAGNOSIS.name,
    "seizure_frequency": SEIZURE_FREQUENCY.name,
    "seizurefrequency": SEIZURE_FREQUENCY.name,
    "prescription": PRESCRIPTION.name,
    "medication": PRESCRIPTION.name,
    "investigation": INVESTIGATIONS.name,
    "investigations": INVESTIGATIONS.name,
}

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

_COUNT_RE = re.compile(r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:to|-|–)\s*(?P<upper>\d+(?:\.\d+)?)\b")
_SINGLE_COUNT_RE = re.compile(r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:seizures?|episodes?)\b", re.I)
_MODALITY_RE = re.compile(r"\b(MRI|CT|EEG)\b", re.I)
_LAST_EVENT_CUE_RE = re.compile(
    r"\b(last seizure|last seizures|last event|has had none since|none since|"
    r"no further|not had any further|has not had any(?: further)?|"
    r"seizure[- ]free since|no seizures?|no absences)\b",
    re.IGNORECASE,
)
_REMOTE_TIMEFRAME_RE = re.compile(
    r"\b(?:teenage(?: years)?|teens|childhood|adolescence|school years)\b",
    re.IGNORECASE,
)
_SEIZURE_FREE_RE = re.compile(r"seizure\s*-?free|no further seizures", re.I)

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


@dataclass(frozen=True)
class InventoryMaterialization:
    prediction: PredictedLetter
    semantic_facts: list[dict[str, Any]]
    rule_trace: list[dict[str, Any]]
    warnings: list[str]
    evidence_invalid: int
    parse_failures: list[str] = field(default_factory=list)


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
            "event": "One current coded fact in ordinary clinical language.",
            "evidence": "Exact clause copied from the letter that supports this fact.",
            "attributes": dict(_LLM_ATTRIBUTE_SCHEMA),
        }
        task = (
            "Read the letter once. Return the current coded inventory for the four "
            "families. If a family has no current coded item, return nothing for that "
            "family. Multiple facts may share evidence."
        )
    else:
        fact_schema = {
            "family": "Diagnosis | SeizureFrequency | Prescription | Investigations",
            "event": "One current coded fact in ordinary clinical language.",
            "evidence": "Exact clause copied from the letter that supports this fact.",
        }
        task = (
            "Read the letter once. Return the current coded inventory for the four "
            "families. If a family has no current coded item, return nothing for that "
            "family. Multiple facts may share evidence. Return only family, event, "
            "and evidence; do not return clinical attributes."
        )
    payload = {
        "task": task,
        "output_schema": {"facts": [fact_schema]},
        "family_guidance": {
            "Diagnosis": (
                "Named epilepsy and seizure-type diagnoses that apply to the patient "
                "now. Put seizure types here when they are diagnoses. Do not add "
                "clumsiness, collapse, aura descriptions, or unrelated illness."
            ),
            "SeizureFrequency": (
                "Current rates, counts, and seizure-free states. Encode a last event "
                "as a zero-count current fact. Use the named seizure type when the "
                "letter names one; otherwise use seizures. Do not add symptoms that "
                "have no rate or last-event statement."
            ),
            "Prescription": (
                "Current drug regimens. Include a planned change only when it "
                "replaces or continues a current regimen. Do not add a planned-only "
                "drug that has not started."
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


def _normalize_family(value: Any) -> str | None:
    return _FAMILY_ALIASES.get(str(value or "").strip().lower().replace(" ", "_"))


def _coerce_text(value: Any, errors: list[str], field_name: str) -> str:
    if value is None:
        return ""
    text = str(value)
    if text != value:
        errors.append(f"coerced_text: {field_name}")
    return text


def _flatten_attribute_object(value: Any, errors: list[str], index: int) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"schema_validation_error: fact[{index}].attributes must be an object")
        return {}
    working = dict(value)
    for key in list(working):
        family = _normalize_family(key)
        nested = working[key]
        if family is None or not isinstance(nested, dict):
            continue
        working.pop(key)
        errors.append(f"unwrapped_nested_family_attributes: fact[{index}].{key}")
        for nested_key, nested_value in nested.items():
            working.setdefault(nested_key, nested_value)
    return working


def _stringify_attributes(value: Any, errors: list[str], index: int) -> dict[str, str]:
    working = _flatten_attribute_object(value, errors, index)
    result: dict[str, str] = {}
    for key, raw_value in working.items():
        if raw_value is None:
            continue
        string_value = str(raw_value)
        if string_value != raw_value:
            errors.append(f"coerced_attribute_value: fact[{index}].{key}")
        result[str(key)] = string_value
    return result


def materialize_inventory(
    letter: ExectLetter,
    record: SemanticInventoryRecord,
    *,
    method: Literal["llm", "llm_with_rules"],
    disabled_rule_families: set[str] | None = None,
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
            attributes, text, status, owner, traces = _hybrid_project_fact(fact, index=index)
            rule_trace.extend(traces)

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
        candidates, letter_traces = _apply_hybrid_letter_rules(letter, candidates)
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


def _hybrid_project_fact(
    fact: SemanticFact, *, index: int
) -> tuple[dict[str, str], str, str, str, list[dict[str, Any]]]:
    parsed = _parse_event_and_evidence(fact)
    attributes = dict(parsed["attributes"])
    text = parsed["text"]
    traces = [
        _trace(
            index=index,
            category=parsed["rule_category"],
            action=parsed["action"],
            evidence=fact.evidence,
            after=dict(attributes),
            changed=bool(attributes),
        )
    ]
    owner = f"deterministic.semantic_inventory_rules.{fact.family}"
    status = "materialized" if text and attributes else "partial"

    if fact.family == SEIZURE_FREQUENCY.name:
        encoded, actions = sf_encoding.apply_sf_attribute_encoding(
            [
                {
                    "entity": fact.family,
                    "text": text,
                    "attributes": attributes,
                    "evidence": fact.evidence,
                }
            ]
        )
        mention = encoded[0]
        attributes = {str(key): str(value) for key, value in mention.get("attributes", {}).items()}
        text = str(mention.get("text") or text)
        for action in actions:
            traces.append(
                _trace(
                    index=index,
                    category="seizure_frequency",
                    action=str(action.get("rule_id") or action.get("action") or ""),
                    evidence=fact.evidence,
                    after=dict(attributes),
                    changed=True,
                )
            )
        rewritten = sd.sf_convention_rewrite(
            text, evidence=fact.evidence, attributes=attributes
        )
        if rewritten is not None:
            text, new_attrs, rule_id = rewritten
            attributes = {str(key): str(value) for key, value in new_attrs.items()}
            traces.append(
                _trace(
                    index=index,
                    category="seizure_frequency",
                    action=rule_id,
                    evidence=fact.evidence,
                    after=dict(attributes),
                    changed=True,
                )
            )
        if sd.is_sf_convention_noise(
            text, evidence=fact.evidence, attributes=attributes
        ) or _is_uncoded_sf_phenomenology(text, fact.evidence, attributes):
            traces.append(
                _trace(
                    index=index,
                    category="seizure_frequency",
                    action="suppress_uncoded_or_noise_sf",
                    evidence=fact.evidence,
                    after={},
                    changed=True,
                )
            )
            return attributes, "", "semantic_only_uncoded_phenomenology", owner, traces
    elif fact.family == DIAGNOSIS.name:
        target = sd.diagnosis_convention_target(text, fact.evidence)
        if target and target != text:
            text = target
            attributes = sd.diagnosis_convention_attribute_repairs(
                text, evidence=fact.evidence, attributes=attributes
            )
            traces.append(
                _trace(
                    index=index,
                    category="benchmark_format",
                    action="diagnosis_convention_rewrite",
                    evidence=fact.evidence,
                    after={"text": text, **attributes},
                    changed=True,
                )
            )
        if sd.is_diagnosis_convention_noise(
            text,
            evidence=fact.evidence,
            diag_category=attributes.get("DiagCategory"),
        ):
            traces.append(
                _trace(
                    index=index,
                    category="benchmark_format",
                    action="suppress_diagnosis_convention_noise",
                    evidence=fact.evidence,
                    after={},
                    changed=True,
                )
            )
            return attributes, "", "semantic_only_diagnosis_noise", owner, traces
    elif fact.family == PRESCRIPTION.name:
        attributes = sd.prescription_convention_attribute_repairs(
            text, evidence=fact.evidence, attributes=attributes
        )
        if sd.is_planned_start_prescription(
            text, evidence=fact.evidence, attributes=attributes
        ) or sd.is_non_antiepileptic_prescription(
            text, evidence=fact.evidence, attributes=attributes
        ):
            traces.append(
                _trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_noncurrent_or_non_epilepsy_prescription",
                    evidence=fact.evidence,
                    after=dict(attributes),
                    changed=True,
                )
            )
            return attributes, "", "semantic_only_noncurrent_status", owner, traces
    elif fact.family == INVESTIGATIONS.name:
        attributes = sd.investigation_convention_attribute_repairs(
            text, evidence=fact.evidence, attributes=attributes
        )
        if _is_pending_investigation_text(text, fact.evidence, attributes):
            traces.append(
                _trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_pending_investigation",
                    evidence=fact.evidence,
                    after=dict(attributes),
                    changed=True,
                )
            )
            return attributes, "", "semantic_only_pending_investigation", owner, traces

    status = "materialized" if text and attributes else "partial"
    return attributes, text, status, owner, traces


def _apply_hybrid_letter_rules(
    letter: ExectLetter,
    mentions: list[PredictedMention],
) -> tuple[list[PredictedMention], list[dict[str, Any]]]:
    traces: list[dict[str, Any]] = []
    diagnoses = [mention for mention in mentions if mention.entity == DIAGNOSIS.name]
    others = [mention for mention in mentions if mention.entity != DIAGNOSIS.name]
    filtered = list(sd.drop_syndrome_covered_phenotypes(diagnoses))
    if len(filtered) != len(diagnoses):
        traces.append(
            _trace(
                index=-1,
                category="clinical_epilepsy",
                action="drop_syndrome_covered_phenotypes",
                evidence="",
                after={"kept": [mention.text for mention in filtered]},
                changed=True,
            )
        )
    working = [*filtered, *others]
    selected_texts = [mention.text for mention in working if mention.entity == DIAGNOSIS.name]
    selected_concepts = {canonicalize_diagnosis_concept(text) for text in selected_texts}
    for text, evidence in sd.diagnosis_residual_additions(letter.note_text):
        concept = canonicalize_diagnosis_concept(text)
        if concept in selected_concepts:
            continue
        if sd.is_redundant_diagnosis_residual_addition(
            text, evidence=evidence, selected_texts=selected_texts
        ):
            continue
        attributes = {
            "DiagCategory": diagnosis_category_for_concept(text),
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        working.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=text,
                attributes=attributes,
                evidence=evidence,
                component_owner="deterministic.semantic_inventory_rules.Diagnosis.residual",
            )
        )
        selected_texts.append(text)
        selected_concepts.add(concept)
        traces.append(
            _trace(
                index=-1,
                category=sd.diagnosis_residual_addition_category(text, evidence),
                action="diagnosis_residual_addition",
                evidence=evidence,
                after={"text": text, **attributes},
                changed=True,
            )
        )
    return working, traces


def _trace(
    *,
    index: int,
    category: str,
    action: str,
    evidence: str,
    after: dict[str, Any],
    changed: bool,
) -> dict[str, Any]:
    return {
        "fact_index": index,
        "rule_category": category,
        "action": action,
        "evidence": evidence,
        "before": {},
        "after": after,
        "changed": changed,
        "first_prediction_changing_owner": "deterministic" if changed else None,
    }


def _fact_text(fact: SemanticFact) -> str:
    """Select a source-near phrase for scorer projection without adding facts."""

    source = f"{fact.event} {fact.evidence}"
    if fact.family == PRESCRIPTION.name:
        return (
            _longest_surface(fact.event, PRESCRIPTION_SURFACE_FORMS)
            or _longest_surface(source, PRESCRIPTION_SURFACE_FORMS)
            or fact.attributes.get("name", "")
            or fact.event.strip()
        )
    if fact.family == DIAGNOSIS.name:
        return (
            _longest_surface(fact.event, DIAGNOSIS_SURFACE_FORMS)
            or _longest_surface(source, DIAGNOSIS_SURFACE_FORMS)
            or fact.attributes.get("concept", "")
            or fact.event.strip()
        )
    if fact.family == SEIZURE_FREQUENCY.name:
        return (
            _longest_surface(fact.event, _SF_PHRASES)
            or _longest_surface(source, _SF_PHRASES)
            or str(fact.attributes.get("type", ""))
            or fact.event.strip()
        )
    modality = _modality(fact.event) or _modality(source)
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
    source = f"{fact.event} {fact.evidence}"
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
    return sd.is_pending_investigation(text, evidence=evidence, attributes=attributes)


def _is_uncoded_sf_phenomenology(
    text: str, evidence: str, attributes: dict[str, str]
) -> bool:
    if any(
        attributes.get(key)
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "TimePeriod",
            "NumberOfTimePeriods",
        )
    ):
        return False
    source = f"{text} {evidence}"
    if _LAST_EVENT_CUE_RE.search(source) or _SEIZURE_FREE_RE.search(source):
        return False
    return not bool(_longest_surface(source, _SF_PHRASES))


def _sf_attributes_to_legacy(attrs: dict[str, str], *, source: str = "") -> dict[str, str]:
    key_map = {
        "count": "NumberOfSeizures",
        "frequency": "NumberOfSeizures",
        "lower_count": "LowerNumberOfSeizures",
        "upper_count": "UpperNumberOfSeizures",
        "period_count": "NumberOfTimePeriods",
        "lower_period": "LowerNumberOfTimePeriods",
        "upper_period": "UpperNumberOfTimePeriods",
        "period": "TimePeriod",
        "change": "FrequencyChange",
        "direction": "FrequencyChange",
        "point_in_time": "PointInTime",
        "day": "DayDate",
        "month": "MonthDate",
        "year": "YearDate",
        "age_lower": "AgeLower",
        "age_upper": "AgeUpper",
        "age_unit": "AgeUnit",
    }
    legacy = {key_map[key]: value for key, value in attrs.items() if key in key_map and value}
    state = attrs.get("state", attrs.get("status", "")).lower().replace("_", "-")
    remote = bool(_REMOTE_TIMEFRAME_RE.search(f"{attrs.get('timeframe', '')} {source}"))
    last_event = bool(_LAST_EVENT_CUE_RE.search(source)) or state in {
        "last-event",
        "seizure-free",
        "seizure free",
        "none",
        "zero",
    }
    if last_event or (state == "historical" and remote):
        legacy.setdefault("NumberOfSeizures", "0")
    return legacy


def _certainty(value: str) -> str:
    mapping = {
        "certain": "5",
        "confirmed": "5",
        "probable": "4",
        "likely": "4",
        "possible": "3",
        "uncertain": "2",
        "unknown": "1",
    }
    return mapping.get(value.lower(), value if value in {"1", "2", "3", "4", "5"} else "5")


def _negation(value: str) -> str:
    if value.lower() in {"negated", "no", "not", "absent"}:
        return "Negated"
    return "Affirmed"


def _dose_unit(value: str) -> str:
    lowered = value.lower().replace("milligrams", "mg").replace("grams", "g")
    return "g" if lowered.startswith("g") and not lowered.startswith("mg") else "mg"


def _frequency(value: str) -> str:
    mapped = sd.frequency_code(value)
    if mapped:
        return mapped
    return value if value in {"1", "2", "3", "As_Required"} else ""


def _parse_event_and_evidence(fact: SemanticFact) -> dict[str, Any]:
    """Parse only the emitted event and its exact evidence. No letter extractors."""

    source = f"{fact.event} {fact.evidence}"
    if fact.family == DIAGNOSIS.name:
        phrase = (
            _longest_surface(fact.event, DIAGNOSIS_SURFACE_FORMS)
            or _longest_surface(source, DIAGNOSIS_SURFACE_FORMS)
            or fact.event.strip()
        )
        concept = diagnosis_concept(phrase) if phrase else None
        dx_attrs = {
            "DiagCategory": diagnosis_category_for_concept(phrase),
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        if concept:
            dx_attrs.update({"CUI": concept.cui, "CUIPhrase": concept.cui_phrase})
        return {
            "text": phrase,
            "attributes": dx_attrs if phrase else {},
            "rule_category": "clinical_epilepsy",
            "action": "parse_emitted_event_and_exact_evidence",
        }
    if fact.family == PRESCRIPTION.name:
        phrase = _longest_surface(fact.event, PRESCRIPTION_SURFACE_FORMS) or _longest_surface(
            source, PRESCRIPTION_SURFACE_FORMS
        )
        drug = sd.normalize_drug_name(phrase) if phrase else None
        rx_attrs = {"DrugName": drug or phrase} if phrase else {}
        dose = sd.dose_from_text(fact.event) or sd.dose_from_text(source)
        if dose:
            rx_attrs["DrugDose"] = dose[0]
            rx_attrs["DoseUnit"] = dose[1]
        schedule = sd.frequency_code(fact.event) or sd.frequency_code(source)
        if schedule:
            rx_attrs["Frequency"] = schedule
        return {
            "text": drug or phrase or fact.event.strip(),
            "attributes": rx_attrs,
            "rule_category": "clinical_epilepsy",
            "action": "parse_emitted_event_and_exact_evidence",
        }
    if fact.family == INVESTIGATIONS.name:
        modality = _modality(fact.event) or _modality(source)
        if modality and sd.is_pending_investigation(
            modality, evidence=source, attributes={}
        ):
            return {
                "text": modality,
                "attributes": {},
                "rule_category": "clinical_epilepsy",
                "action": "parse_emitted_event_and_exact_evidence",
            }
        result_match = re.search(r"\b(normal|abnormal|negative|unremarkable)\b", source, re.I)
        finding = (
            "Normal"
            if result_match
            and result_match.group(1).lower() in {"normal", "negative", "unremarkable"}
            else "Abnormal"
            if result_match
            else "Unknown"
        )
        inv_attrs = (
            {f"{modality}_Performed": "Yes", f"{modality}_Results": finding} if modality else {}
        )
        return {
            "text": modality or fact.event.strip(),
            "attributes": inv_attrs,
            "rule_category": "clinical_epilepsy",
            "action": "parse_emitted_event_and_exact_evidence",
        }
    phrase = (
        _longest_surface(fact.event, _SF_PHRASES)
        or _longest_surface(source, _SF_PHRASES)
        or fact.event.strip()
    )
    sf_attrs: dict[str, str] = {}
    range_match = _COUNT_RE.search(fact.event) or _COUNT_RE.search(source)
    single = _SINGLE_COUNT_RE.search(fact.event) or _SINGLE_COUNT_RE.search(source)
    if range_match:
        sf_attrs.update(
            {
                "LowerNumberOfSeizures": range_match.group("count"),
                "UpperNumberOfSeizures": range_match.group("upper"),
            }
        )
    elif single:
        sf_attrs["NumberOfSeizures"] = single.group("count")
    if _SEIZURE_FREE_RE.search(source):
        sf_attrs["NumberOfSeizures"] = "0"
    return {
        "text": phrase,
        "attributes": sf_attrs,
        "rule_category": "seizure_frequency",
        "action": "parse_emitted_event_and_exact_evidence",
    }


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
