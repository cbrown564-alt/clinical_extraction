"""Event-local hybrid rules for the semantic-inventory research lane.

Rules may read only the emitted event string and a closed convention table.
They may not grow mentions from the evidence span or the letter.
"""

from __future__ import annotations

import re
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
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
_SEIZURE_FREE_RE = re.compile(r"seizure\s*-?free|no further seizures", re.I)
_NONCURRENT_RE = re.compile(
    r"\b(previous|past|historical|planned|future|requested|stopped|discontinued)\b",
    re.I,
)


def project_hybrid_event(
    *,
    family: str,
    event: str,
    evidence: str,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Return mention dicts, traces, and a projection status from one event."""

    traces: list[dict[str, Any]] = []
    mentions: list[dict[str, Any]] = []
    event = event.strip()
    if family == DIAGNOSIS.name:
        rewritten_event, rewrite_action = _closed_rewrite(event)
        if rewrite_action:
            traces.append(
                _trace(
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
                _trace(
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
        if _has_typed_rate(event):
            sf_mention = _seizure_frequency_mention(event)
            if sf_mention is not None:
                mentions.append(sf_mention)
                traces.append(
                    _trace(
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
                _trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_noncurrent_or_unparsed_prescription",
                    after={},
                )
            )
            return [], traces, "semantic_only_noncurrent_status"
        traces.append(
            _trace(
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
                _trace(
                    index=index,
                    category="clinical_epilepsy",
                    action="suppress_pending_investigation",
                    after={},
                )
            )
            return [], traces, "semantic_only_pending_investigation"
        traces.append(
            _trace(
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
            _trace(
                index=index,
                category="seizure_frequency",
                action="suppress_uncoded_or_noise_sf",
                after={},
            )
        )
        return [], traces, "semantic_only_uncoded_phenomenology"
    traces.append(
        _trace(
            index=index,
            category="seizure_frequency",
            action="parse_emitted_event",
            after=dict(mention["attributes"]),
        )
    )
    mentions.append(mention)
    type_phrase = _longest_surface(event, _DUAL_FAMILY_TYPES)
    if type_phrase:
        dx = _diagnosis_mention(type_phrase, event)
        if dx is not None:
            mentions.append(dx)
            traces.append(
                _trace(
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


def _trace(*, index: int, category: str, action: str, after: dict[str, Any]) -> dict[str, Any]:
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


__all__ = ["project_hybrid_event"]
