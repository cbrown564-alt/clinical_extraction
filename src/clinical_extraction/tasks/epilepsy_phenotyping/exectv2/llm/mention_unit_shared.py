"""Shared helpers for mention-unit materialization and hybrid projection.

Owns the helpers formerly shared with the semantic-inventory research lane so
mention_unit can stand alone after that lane is removed. Do not import this
module from prompt bodies; it is projection and parsing only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    DIAGNOSIS_SURFACE_FORMS,
    PRESCRIPTION_SURFACE_FORMS,
    diagnosis_concept,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as sf_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)

LLM_METHOD = "llm"
HYBRID_METHOD = "llm_with_rules"

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
_DUAL_FAMILY_TYPES = (
    "focal seizures with altered awareness",
    "focal seizures with loss of awareness",
    "focal impaired awareness seizures",
    "focal to bilateral convulsive seizures",
    "secondary generalised seizures",
    "generalised tonic clonic seizures",
    "complex partial seizures",
    "absence like seizures",
    "focal seizures",
    "focal motor seizures",
    "generalised seizures",
)
_HEADING_SPLITS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("focal epilepsy", "temporal"), ("focal epilepsy", "temporal lobe epilepsy")),
    (("epilepsy", "possibly generalised"), ("epilepsy", "generalised epilepsy")),
    (("epilepsy", "possible generalised"), ("epilepsy", "generalised epilepsy")),
)
_CLOSED_REWRITES = {
    "symptomatic structural epilepsy": "symptomatic structural focal epilepsy",
}
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
_NONCURRENT_RE = re.compile(
    r"\b(previous|past|historical|planned|future|requested|stopped|discontinued)\b",
    re.I,
)
_RX_FUTURE_PLAN_RE = re.compile(
    r"\b(?:please\s+start|to\s+start|start(?:ing)?|commence|"
    r"increas(?:e|ing)|to\s+increase|reduc(?:e|ing)|to\s+reduce|"
    r"every\s+(?:two\s+)?weeks|every\s+fortnight|target\s+dose)\b",
    re.I,
)
_RX_ONCE_DAILY_PAIR_RE = re.compile(
    r"(?P<dose>\d+(?:\.\d+)?)\s*(?P<unit>mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)"
    r"(?:\s+in\s+the)?\s+"
    r"(?P<tod>mane|nocte|nokte|morning|evening|afternoon|am|pm)\b",
    re.I,
)


@dataclass(frozen=True)
class InventoryMaterialization:
    prediction: PredictedLetter
    semantic_facts: list[dict[str, Any]]
    rule_trace: list[dict[str, Any]]
    warnings: list[str]
    evidence_invalid: int
    parse_failures: list[str] = field(default_factory=list)


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


def _apply_hybrid_letter_rules(
    mentions: list[PredictedMention],
) -> tuple[list[PredictedMention], list[dict[str, Any]]]:
    traces: list[dict[str, Any]] = []
    diagnoses = [mention for mention in mentions if mention.entity == DIAGNOSIS.name]
    others = [mention for mention in mentions if mention.entity != DIAGNOSIS.name]
    filtered = list(sd.drop_syndrome_covered_phenotypes(diagnoses))
    if len(filtered) != len(diagnoses):
        traces.append(
            _letter_rule_trace(
                index=-1,
                category="clinical_epilepsy",
                action="drop_syndrome_covered_phenotypes",
                evidence="",
                after={"kept": [mention.text for mention in filtered]},
                changed=True,
            )
        )
    working = [*filtered, *others]
    encoded: list[PredictedMention] = []
    for mention in working:
        if mention.entity != SEIZURE_FREQUENCY.name:
            encoded.append(mention)
            continue
        rewritten, actions = sf_encoding.apply_sf_attribute_encoding(
            [
                {
                    "entity": mention.entity,
                    "text": mention.text,
                    "attributes": dict(mention.attributes),
                    "evidence": mention.evidence,
                }
            ]
        )
        row = rewritten[0]
        encoded.append(
            PredictedMention(
                entity=mention.entity,
                text=str(row.get("text") or mention.text),
                attributes={
                    str(key): str(value) for key, value in row.get("attributes", {}).items()
                },
                evidence=mention.evidence,
                component_owner=mention.component_owner,
            )
        )
        for action in actions:
            traces.append(
                _letter_rule_trace(
                    index=-1,
                    category="seizure_frequency",
                    action=str(action.get("rule_id") or action.get("action") or ""),
                    evidence=mention.evidence,
                    after=dict(encoded[-1].attributes),
                    changed=True,
                )
            )
    return encoded, traces


def _letter_rule_trace(
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


def project_hybrid_event(
    *,
    family: str,
    event: str,
    evidence: str,
    index: int,
    dual_family: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Return mention dicts, traces, and a projection status from one event."""

    traces: list[dict[str, Any]] = []
    mentions: list[dict[str, Any]] = []
    event = event.strip()
    if family == DIAGNOSIS.name:
        rewritten_event, rewrite_action = _closed_rewrite(event)
        if rewrite_action:
            traces.append(
                _event_rule_trace(
                    index=index,
                    category="benchmark_format",
                    action=rewrite_action,
                    after={"text": rewritten_event},
                )
            )
            event = rewritten_event
        phrases = _heading_split_phrases(event)
        if phrases:
            traces.append(
                _event_rule_trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="convention_split_heading",
                    after={"phrases": list(phrases)},
                )
            )
        else:
            phrases = (_diagnosis_phrase(event),)
        for phrase in phrases:
            mention = _diagnosis_mention(phrase, event)
            if mention is None:
                continue
            mentions.append(mention)
        if dual_family and _has_typed_rate(event):
            sf_mention = _seizure_frequency_mention(event)
            if sf_mention is not None:
                mentions.append(sf_mention)
                traces.append(
                    _event_rule_trace(
                        index=index,
                        category="seizure_frequency",
                        action="dual_family_reuse",
                        after={"text": sf_mention["text"]},
                    )
                )
        return _finalize(
            mentions, traces, family=family, evidence=evidence, status="materialized"
        )

    if family == PRESCRIPTION.name:
        mention = _prescription_mention(event)
        if mention is None or _NONCURRENT_RE.search(event):
            traces.append(
                _event_rule_trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_noncurrent_or_unparsed_prescription",
                    after={},
                )
            )
            return [], traces, "semantic_only_noncurrent_status"
        traces.append(
            _event_rule_trace(
                index=index,
                category="clinical_epilepsy",
                action="parse_emitted_event",
                after=dict(mention["attributes"]),
            )
        )
        return _finalize(
            [mention], traces, family=family, evidence=evidence, status="materialized"
        )

    if family == INVESTIGATIONS.name:
        mention = _investigation_mention(event)
        if mention is None or _is_pending_investigation(event):
            traces.append(
                _event_rule_trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_pending_investigation",
                    after={},
                )
            )
            return [], traces, "semantic_only_pending_investigation"
        traces.append(
            _event_rule_trace(
                index=index,
                category="clinical_epilepsy",
                action="parse_emitted_event",
                after=dict(mention["attributes"]),
            )
        )
        return _finalize(
            [mention], traces, family=family, evidence=evidence, status="materialized"
        )

    mention = _seizure_frequency_mention(event)
    if mention is None or _is_uncoded_phenomenology(event, mention["attributes"]):
        traces.append(
            _event_rule_trace(
                index=index,
                category="seizure_frequency",
                action="suppress_uncoded_or_noise_sf",
                after={},
            )
        )
        return [], traces, "semantic_only_uncoded_phenomenology"
    traces.append(
        _event_rule_trace(
            index=index,
            category="seizure_frequency",
            action="parse_emitted_event",
            after=dict(mention["attributes"]),
        )
    )
    mentions.append(mention)
    type_phrase = _longest_surface(event, _DUAL_FAMILY_TYPES)
    if dual_family and type_phrase:
        dx = _diagnosis_mention(type_phrase, event)
        if dx is not None:
            mentions.append(dx)
            traces.append(
                _event_rule_trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="dual_family_reuse",
                    after={"text": dx["text"]},
                )
            )
    return _finalize(
        mentions, traces, family=family, evidence=evidence, status="materialized"
    )


def _finalize(
    mentions: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    *,
    family: str,
    evidence: str,
    status: str = "materialized",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    # Keep historical owner string so attribution stays stable after the move.
    owner = f"deterministic.semantic_inventory_rules.{family}"
    for mention in mentions:
        mention["component_owner"] = owner
        mention["evidence"] = evidence
    return mentions, traces, status if mentions else "partial"


def _heading_split_phrases(event: str) -> tuple[str, ...]:
    lowered = event.lower()
    for needles, phrases in _HEADING_SPLITS:
        if all(needle in lowered for needle in needles):
            return phrases
    return ()


def _closed_rewrite(phrase: str) -> tuple[str, str]:
    surface = " ".join(phrase.lower().replace("-", " ").split())
    target = _CLOSED_REWRITES.get(surface)
    if target:
        return target, "closed_table_rewrite"
    convention = sd.diagnosis_convention_target(phrase, phrase)
    if convention and convention != phrase:
        return convention, "closed_table_rewrite"
    return phrase, ""


def _diagnosis_phrase(event: str) -> str:
    normalized = " ".join(event.lower().replace("-", " ").split())
    if normalized in _CLOSED_REWRITES or normalized in _CLOSED_REWRITES.values():
        return _CLOSED_REWRITES.get(normalized, event)
    return _longest_surface(event, DIAGNOSIS_SURFACE_FORMS) or event.strip()


def _diagnosis_mention(phrase: str, event: str) -> dict[str, Any] | None:
    if not phrase or sd.is_diagnosis_convention_noise(phrase, evidence=event, diag_category=None):
        return None
    probable = bool(re.search(r"\bprobable|probably\b", event, re.I))
    certainty = "4" if probable and "temporal" in phrase else "5"
    attributes = {
        "DiagCategory": diagnosis_category_for_concept(phrase),
        "Certainty": certainty,
        "Negation": "Affirmed",
    }
    concept = diagnosis_concept(phrase)
    if concept:
        attributes.update({"CUI": concept.cui, "CUIPhrase": concept.cui_phrase})
    return {"entity": DIAGNOSIS.name, "text": phrase, "attributes": attributes}


def project_rx_split_once_daily(
    *,
    name: str,
    evidence: str,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str] | None:
    """Split one emitted current unequal once-daily pair into two mentions.

    Gold-free: both doses must already sit in the emitted name plus evidence,
    each bound to a once-daily time-of-day cue. Truncate at a future-plan cue
    so titration tails are not split. Does not search the letter.
    """

    event = f"{name} {evidence}".strip()
    if _NONCURRENT_RE.search(event):
        return None
    future = _RX_FUTURE_PLAN_RE.search(event)
    head = event[: future.start()] if future else event
    pairs = list(_RX_ONCE_DAILY_PAIR_RE.finditer(head))
    if len(pairs) < 2:
        return None
    seed = _prescription_mention(name) or _prescription_mention(event)
    if seed is None:
        return None
    drug = str(seed["text"])
    selected = pairs[:2]
    doses = [match.group("dose") for match in selected]
    mentions: list[dict[str, Any]] = [
        {
            "entity": PRESCRIPTION.name,
            "text": drug,
            "attributes": {
                "DrugName": drug,
                "DrugDose": match.group("dose"),
                "DoseUnit": sd.normalize_dose_unit(match.group("unit")),
                "Frequency": "1",
            },
        }
        for match in selected
    ]
    traces = [
        _event_rule_trace(
            index=index,
            category="clinical_epilepsy",
            action="leftover_form.rx_split_once_daily",
            after={"doses": doses},
        )
    ]
    return _finalize(
        mentions, traces, family=PRESCRIPTION.name, evidence=evidence, status="materialized"
    )


def _prescription_mention(event: str) -> dict[str, Any] | None:
    phrase = _longest_surface(event, PRESCRIPTION_SURFACE_FORMS)
    if not phrase:
        return None
    drug = sd.normalize_drug_name(phrase) or phrase
    attributes = {"DrugName": drug}
    dose = sd.dose_from_text(event)
    if dose:
        attributes["DrugDose"] = dose[0]
        attributes["DoseUnit"] = dose[1]
    schedule = sd.frequency_code(event)
    if schedule:
        attributes["Frequency"] = schedule
    if sd.is_non_antiepileptic_prescription(drug, evidence=event, attributes=attributes):
        return None
    return {"entity": PRESCRIPTION.name, "text": drug, "attributes": attributes}


def _investigation_mention(event: str) -> dict[str, Any] | None:
    match = _MODALITY_RE.search(event)
    if match is None:
        return None
    modality = match.group(1).upper()
    result_match = re.search(r"\b(normal|abnormal|negative|unremarkable)\b", event, re.I)
    finding = (
        "Normal"
        if result_match and result_match.group(1).lower() in {"normal", "negative", "unremarkable"}
        else "Abnormal"
        if result_match
        else "Unknown"
    )
    return {
        "entity": INVESTIGATIONS.name,
        "text": modality,
        "attributes": {f"{modality}_Performed": "Yes", f"{modality}_Results": finding},
    }


def _seizure_frequency_mention(event: str) -> dict[str, Any] | None:
    phrase = _longest_surface(event, _SF_PHRASES) or event.strip()
    if not phrase:
        return None
    attributes: dict[str, str] = {}
    range_match = _COUNT_RE.search(event)
    single = _SINGLE_COUNT_RE.search(event)
    if range_match:
        attributes["LowerNumberOfSeizures"] = range_match.group("count")
        attributes["UpperNumberOfSeizures"] = range_match.group("upper")
    elif single:
        attributes["NumberOfSeizures"] = single.group("count")
    if _SEIZURE_FREE_RE.search(event) or _LAST_EVENT_CUE_RE.search(event):
        attributes.setdefault("NumberOfSeizures", "0")
    return {"entity": SEIZURE_FREQUENCY.name, "text": phrase, "attributes": attributes}


def _has_typed_rate(event: str) -> bool:
    return bool(_longest_surface(event, _DUAL_FAMILY_TYPES)) and bool(
        _COUNT_RE.search(event) or _SINGLE_COUNT_RE.search(event)
    )


def _is_pending_investigation(event: str) -> bool:
    return bool(
        re.search(r"\b(plan|planned|arrange|request|will|repeat)\b", event, re.I)
        and _MODALITY_RE.search(event)
    )


def _is_uncoded_phenomenology(event: str, attributes: dict[str, str]) -> bool:
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
    if _LAST_EVENT_CUE_RE.search(event) or _SEIZURE_FREE_RE.search(event):
        return False
    return not bool(_longest_surface(event, _SF_PHRASES))


def _longest_surface(source: str, surfaces: tuple[str, ...] | list[str]) -> str:
    lowered = source.lower()
    matches = [surface for surface in surfaces if surface.lower() in lowered]
    return max(matches, key=len) if matches else ""


def _event_rule_trace(
    *, index: int, category: str, action: str, after: dict[str, Any]
) -> dict[str, Any]:
    return {
        "fact_index": index,
        "rule_category": category,
        "action": action,
        "evidence": "",
        "before": {},
        "after": after,
        "changed": True,
        "first_prediction_changing_owner": "deterministic",
    }


__all__ = [
    "HYBRID_METHOD",
    "InventoryMaterialization",
    "LLM_METHOD",
    "_apply_hybrid_letter_rules",
    "_certainty",
    "_coerce_text",
    "_dose_unit",
    "_flatten_attribute_object",
    "_frequency",
    "_heading_split_phrases",
    "_is_pending_investigation",
    "_is_uncoded_phenomenology",
    "_negation",
    "_normalize_family",
    "_sf_attributes_to_legacy",
    "_stringify_attributes",
    "project_hybrid_event",
    "project_rx_split_once_daily",
]
