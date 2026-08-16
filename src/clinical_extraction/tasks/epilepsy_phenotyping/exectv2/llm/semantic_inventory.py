"""Semantic-inventory ExECT research lane.

This module is deliberately parallel to the selected structured-event stack.
It gives the model a clinical fact contract, then keeps semantic parsing,
benchmark projection, and attribution visible for the re-evaluation study.
It does not change the selected ExECT method or its default prompt.
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    diagnosis as diagnosis_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as investigation_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    prescription as prescription_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
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
SEMANTIC_PROMPT_VERSION = "exectv2_semantic_inventory_v2"
SEMANTIC_MODEL = "openai/gpt-5.6-luna"
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

_DOSE_RE = re.compile(r"(?P<dose>\d+(?:\.\d+)?)\s*(?P<unit>mg|mgs|g|grams?)\b", re.I)
_COUNT_RE = re.compile(r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:to|-|–)\s*(?P<upper>\d+(?:\.\d+)?)\b")
_SINGLE_COUNT_RE = re.compile(r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:seizures?|episodes?)\b", re.I)
_MODALITY_RE = re.compile(r"\b(MRI|CT|EEG)\b", re.I)


class SemanticFact(BaseModel):
    """One atomic model-emitted fact."""

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
    return (
        "Extract atomic clinical facts from the supplied clinical letter. "
        "Return the requested JSON exactly."
    )


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
    """Read one clinical letter and return atomic facts with semantic fields."""

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
            "event": "Complete natural-language statement of one atomic fact.",
            "evidence": "Exact clause copied from the letter that supports this fact.",
            "attributes": {
                "Diagnosis": "Use concept, certainty, negation, temporality, and scope.",
                "SeizureFrequency": (
                    "Use type, state, count, lower_count, upper_count, period, "
                    "timeframe, change, and point_in_time."
                ),
                "Prescription": "Use name, dose, unit, schedule, purpose, action, and status.",
                "Investigations": "Use name, status, result, type, and date.",
            },
        }
        task = (
            "Read the letter once. Return every distinct atomic clinical fact in the four "
            "families. Preserve current, historical, planned, resolved, negated, and uncertain "
            "facts separately when the letter states them. Multiple facts may share evidence. "
            "Use natural clinical fields, not scorer field names."
        )
    else:
        fact_schema = {
            "family": "Diagnosis | SeizureFrequency | Prescription | Investigations",
            "event": "Complete natural-language statement of one atomic fact.",
            "evidence": "Exact clause copied from the letter that supports this fact.",
        }
        task = (
            "Read the letter once. Return every distinct atomic clinical fact in the four "
            "families. Preserve current, historical, planned, resolved, negated, and uncertain "
            "facts separately when the letter states them. Multiple facts may share evidence. "
            "Return only family, event, and evidence; do not return clinical attributes."
        )
    payload = {
        "task": task,
        "output_schema": {"facts": [fact_schema]},
        "family_guidance": {
            "Diagnosis": (
                "Epilepsy, seizure-disorder, and named seizure-type diagnoses. "
                "Do not label unrelated comorbidity, cause, history, or medication "
                "as Diagnosis."
            ),
            "SeizureFrequency": (
                "Rates, counts, seizure-free states, last events, type, and temporal scope."
            ),
            "Prescription": (
                "Medication, dose, unit, schedule, purpose, action, and active or planned status."
            ),
            "Investigations": "Investigation, completed or planned status, result, type, and date.",
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


def _stringify_attributes(value: Any, errors: list[str], index: int) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"schema_validation_error: fact[{index}].attributes must be an object")
        return {}
    result: dict[str, str] = {}
    for key, raw_value in value.items():
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
            attributes = _llm_attributes_to_legacy(fact)
            text = _fact_text(fact)
            if fact.family == PRESCRIPTION.name and _is_noncurrent_prescription(fact):
                text = ""
            owner = "model.semantic_inventory"
        elif fact.family in disabled_rule_families:
            attributes = {}
            text = ""
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
            parsed = _parse_emitted_fact(fact)
            attributes = parsed["attributes"]
            text = parsed["text"]
            rule_trace.append(
                {
                    "fact_index": index,
                    "rule_category": parsed["rule_category"],
                    "action": parsed["action"],
                    "evidence": fact.evidence,
                    "before": {},
                    "after": dict(attributes),
                    "changed": bool(attributes),
                    "first_prediction_changing_owner": "deterministic" if attributes else None,
                }
            )
            warnings.extend(f"fact[{index}]: {warning}" for warning in parsed["warnings"])
            owner = f"deterministic.semantic_inventory_rules.{fact.family}"

        semantic_row["legacy_attributes"] = dict(attributes)
        semantic_row["scorer_text"] = text
        if fact.family == PRESCRIPTION.name and _is_noncurrent_prescription(fact):
            semantic_row["projection_status"] = "semantic_only_noncurrent_status"
        else:
            semantic_row["projection_status"] = "materialized" if text and attributes else "partial"
        semantic_facts.append(semantic_row)
        if not text:
            warnings.append(f"fact[{index}]: no_scorer_text")
            continue
        mention = PredictedMention(
            entity=fact.family,
            text=text,
            attributes=attributes,
            evidence=fact.evidence,
            component_owner=owner,
        )
        candidates.append(mention)

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


def _fact_text(fact: SemanticFact) -> str:
    """Select a source-near phrase for scorer projection without adding facts."""

    source = f"{fact.event} {fact.evidence}"
    if fact.family == PRESCRIPTION.name:
        return (
            _longest_surface(source, PRESCRIPTION_SURFACE_FORMS)
            or fact.attributes.get("name", "")
            or fact.event.strip()
        )
    if fact.family == DIAGNOSIS.name:
        return (
            _longest_surface(source, DIAGNOSIS_SURFACE_FORMS)
            or fact.attributes.get("concept", "")
            or fact.event.strip()
        )
    if fact.family == SEIZURE_FREQUENCY.name:
        return (
            _longest_surface(source, _SF_PHRASES)
            or str(fact.attributes.get("type", ""))
            or fact.event.strip()
        )
    modality = _modality(source)
    return modality or str(fact.attributes.get("name", "")) or fact.event.strip()


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
    if fact.family == DIAGNOSIS.name:
        concept = attrs.get("concept") or attrs.get("diagnosis") or _fact_text(fact)
        result = {
            "DiagCategory": _diagnosis_category(concept, attrs.get("type", "")),
            "Certainty": _certainty(attrs.get("certainty", "")),
            "Negation": _negation(attrs.get("negation", attrs.get("assertion", ""))),
        }
        return {key: value for key, value in result.items() if value}
    if fact.family == PRESCRIPTION.name:
        result: dict[str, str] = {}
        if attrs.get("name") or attrs.get("medication") or attrs.get("drug"):
            result["DrugName"] = attrs.get("name") or attrs.get("medication") or attrs.get("drug")
        if attrs.get("dose") or attrs.get("amount"):
            result["DrugDose"] = attrs.get("dose") or attrs.get("amount")
        if attrs.get("unit"):
            result["DoseUnit"] = _dose_unit(attrs["unit"])
        schedule = attrs.get("schedule") or attrs.get("frequency") or attrs.get("dose_frequency")
        if schedule:
            result["Frequency"] = _frequency(schedule)
        return {key: value for key, value in result.items() if value}
    if fact.family == INVESTIGATIONS.name:
        modality = (
            attrs.get("name")
            or attrs.get("modality")
            or attrs.get("investigation")
            or _modality(f"{fact.event} {fact.evidence}")
        ).upper()
        result = attrs.get("result", attrs.get("finding", "")).strip().lower()
        legacy: dict[str, str] = {}
        if modality in {"MRI", "CT", "EEG"}:
            if attrs.get("status", "").lower() not in {"planned", "requested", "future"}:
                legacy[f"{modality}_Performed"] = "Yes"
            if result in {"normal", "abnormal", "unknown"}:
                legacy[f"{modality}_Results"] = result.title()
            if attrs.get("type") and modality == "EEG":
                legacy["EEG_Type"] = attrs["type"]
        return legacy
    return _sf_attributes_to_legacy(attrs)


def _is_noncurrent_prescription(fact: SemanticFact) -> bool:
    status = str(fact.attributes.get("status", "")).lower().strip()
    return status in {"planned", "past", "historical", "stopped", "discontinued", "resolved"}


def _sf_attributes_to_legacy(attrs: dict[str, str]) -> dict[str, str]:
    key_map = {
        "count": "NumberOfSeizures",
        "frequency": "NumberOfSeizures",
        "lower_count": "LowerNumberOfSeizures",
        "upper_count": "UpperNumberOfSeizures",
        "period_count": "NumberOfTimePeriods",
        "lower_period": "LowerNumberOfTimePeriods",
        "upper_period": "UpperNumberOfTimePeriods",
        "period": "TimePeriod",
        "timeframe": "TimeSince_or_TimeOfEvent",
        "temporal_scope": "TimeSince_or_TimeOfEvent",
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
    state = attrs.get("state", attrs.get("status", "")).lower()
    if state in {"seizure-free", "seizure free", "none", "zero"}:
        legacy.setdefault("NumberOfSeizures", "0")
    return legacy


def _diagnosis_category(concept: str, kind: str) -> str:
    normalized = (kind or concept).lower()
    if "single" in normalized or "one" in normalized:
        return "SingleSeizure"
    if "multiple" in normalized or "seizure" in normalized and "epilepsy" not in normalized:
        return "MultipleSeizures"
    return "Epilepsy"


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
    if value.lower() in {"negated", "否定", "no", "not", "absent"}:
        return "Negated"
    return "Affirmed"


def _dose_unit(value: str) -> str:
    lowered = value.lower().replace("milligrams", "mg").replace("grams", "g")
    return "g" if lowered.startswith("g") and not lowered.startswith("mg") else "mg"


def _frequency(value: str) -> str:
    lowered = value.lower().replace("-", " ")
    if lowered in {"prn", "as required", "as needed", "rescue"}:
        return "As_Required"
    if any(token in lowered for token in ("three", "tid", "tds", "thrice")):
        return "3"
    if any(token in lowered for token in ("four", "qid", "qds")):
        return "4"
    if any(token in lowered for token in ("twice", "bd", "bid", "two")):
        return "2"
    if any(token in lowered for token in ("once", "daily", "od", "mane", "nocte", "nightly")):
        return "1"
    return value if value in {"1", "2", "3", "As_Required"} else ""


def _parse_emitted_fact(fact: SemanticFact) -> dict[str, Any]:
    """Parse only the event and exact evidence emitted for one fact."""

    local = ExectLetter(letter_id="semantic-local", note_text=fact.evidence)
    candidates: list[PredictedMention]
    if fact.family == DIAGNOSIS.name:
        candidates = list(diagnosis_rules._extract_diagnoses(fact.evidence))
        category = "clinical_epilepsy"
    elif fact.family == PRESCRIPTION.name:
        candidates = list(prescription_rules._extract_prescriptions(fact.evidence))
        category = "clinical_epilepsy"
    elif fact.family == INVESTIGATIONS.name:
        candidates = list(investigation_rules._extract_investigations(fact.evidence))
        category = "clinical_epilepsy"
    else:
        candidates = list(extract_seizure_frequency(local).mentions)
        category = "seizure_frequency"
    chosen = _choose_candidate(candidates, fact.event)
    if chosen is not None:
        return {
            "text": chosen.text,
            "attributes": dict(chosen.attributes),
            "rule_category": category,
            "action": "parse_emitted_event_and_exact_evidence",
            "warnings": [],
        }
    fallback = _fallback_rule_parse(fact)
    return {
        "text": fallback[0],
        "attributes": fallback[1],
        "rule_category": category,
        "action": "bounded_fallback_parse_of_emitted_event_and_evidence",
        "warnings": ["rule_parse_no_named_candidate"] if not fallback[1] else [],
    }


def _choose_candidate(candidates: list[PredictedMention], event: str) -> PredictedMention | None:
    if not candidates:
        return None
    event_tokens = {token for token in re.findall(r"[a-z0-9]+", event.lower()) if len(token) > 2}
    ranked = sorted(
        candidates,
        key=lambda mention: (
            len(event_tokens & set(re.findall(r"[a-z0-9]+", mention.text.lower()))),
            len(mention.attributes),
            len(mention.text),
        ),
        reverse=True,
    )
    return ranked[0]


def _fallback_rule_parse(fact: SemanticFact) -> tuple[str, dict[str, str]]:
    source = f"{fact.event} {fact.evidence}"
    if fact.family == DIAGNOSIS.name:
        phrase = _longest_surface(source, DIAGNOSIS_SURFACE_FORMS)
        concept = diagnosis_concept(phrase) if phrase else None
        attrs = {"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"}
        if concept:
            attrs.update({"CUI": concept.cui, "CUIPhrase": concept.cui_phrase})
        return phrase or fact.event.strip(), attrs if phrase else {}
    if fact.family == PRESCRIPTION.name:
        phrase = _longest_surface(source, PRESCRIPTION_SURFACE_FORMS)
        dose = _DOSE_RE.search(source)
        attrs = {"DrugName": phrase} if phrase else {}
        if dose:
            attrs.update(
                {"DrugDose": dose.group("dose"), "DoseUnit": _dose_unit(dose.group("unit"))}
            )
        schedule = _frequency(source)
        if schedule:
            attrs["Frequency"] = schedule
        return phrase or fact.event.strip(), attrs
    if fact.family == INVESTIGATIONS.name:
        modality = _modality(source)
        result_match = re.search(r"\b(normal|abnormal|negative|unremarkable)\b", source, re.I)
        result = (
            "Normal"
            if result_match
            and result_match.group(1).lower() in {"normal", "negative", "unremarkable"}
            else "Abnormal"
            if result_match
            else "Unknown"
        )
        attrs = {f"{modality}_Performed": "Yes", f"{modality}_Results": result} if modality else {}
        return modality or fact.event.strip(), attrs
    phrase = _longest_surface(source, _SF_PHRASES) or fact.event.strip()
    attrs: dict[str, str] = {}
    range_match = _COUNT_RE.search(source)
    single = _SINGLE_COUNT_RE.search(source)
    if range_match:
        attrs.update(
            {
                "LowerNumberOfSeizures": range_match.group("count"),
                "UpperNumberOfSeizures": range_match.group("upper"),
            }
        )
    elif single:
        attrs["NumberOfSeizures"] = single.group("count")
    if re.search(r"seizure\s*-?free|no further seizures", source, re.I):
        attrs["NumberOfSeizures"] = "0"
    return phrase, attrs


__all__ = [
    "HYBRID_METHOD",
    "InventoryMaterialization",
    "InventoryParseResult",
    "LLM_METHOD",
    "SEMANTIC_MODEL",
    "SEMANTIC_PROMPT_VERSION",
    "SemanticFact",
    "SemanticInventoryExtractor",
    "SemanticInventoryRecord",
    "build_inventory_prompt",
    "materialize_inventory",
    "parse_inventory_json",
]
