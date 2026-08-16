"""Trust-item projection for saved v4 semantic-inventory facts.

Applies landed v9 tables to one emitted item. Does not search the letter
or change the default v4 projector.
"""

from __future__ import annotations

import re
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as investigation_tables,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    MONTH_NAME_PATTERN,
    normalize_count,
    normalize_month,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory_rules import (
    project_hybrid_event,
)

_TYPED_SF_SPANS = (
    "focal seizures with altered awareness",
    "focal seizures with loss of awareness",
    "focal impaired awareness seizures",
    "focal to bilateral convulsive seizures",
    "focal to bilateral convulsive seizure",
    "secondary generalised seizures",
    "generalised tonic clonic seizures",
    "generalized tonic clonic seizures",
    "complex partial seizures",
    "absence like seizures",
    "absence seizures",
    "myoclonic seizures",
    "focal motor seizures",
    "focal seizures",
    "focal seizure",
    "generalised seizures",
    "generalised seizure",
    "temporal lobe seizures",
    "temporal lobe seizure",
    "generalised tonic clonic seizure",
    "generalized tonic clonic seizure",
    "secondary generalised seizure",
    "absence seizure",
    "myoclonic seizure",
    "focal motor seizure",
)
_GENERIC_SF_SPANS = (
    "seizure freedom",
    "seizure free",
    "no further seizures",
    "seizures",
    "seizure",
)
_MODALITY_RE = re.compile(r"\b(MRI|CT|EEG)\b", re.I)
_COUNT_RANGE_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:to|-|–)\s*(?P<upper>\d+(?:\.\d+)?)\b"
)
_DIGIT_COUNT_RE = re.compile(r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:seizures?|episodes?)\b", re.I)
_WORD_COUNT_RE = re.compile(
    r"\b(?P<word>a\s+couple|a\s+few|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|once|none|single|couple|few|several|multiple)\s+"
    r"(?:(?P<type>secondary\s+generalised|secondary\s+generalized|"
    r"generalised\s+tonic[\s-]*clonic|generalized\s+tonic[\s-]*clonic|"
    r"focal\s+to\s+bilateral\s+convulsive|focal\s+motor|focal|"
    r"absence|myoclonic|dyscognitive)\s+)?"
    r"seizures?\b",
    re.I,
)
_DURATION_YEARS_RE = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+years?\b",
    re.I,
)
_EVERY_PERIOD_RE = re.compile(
    r"\bevery\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    r"(?:days?|weeks?|months?|years?)\b",
    re.I,
)
_LAST_CLINIC_RE = re.compile(
    r"\blast(?:\s+clinic(?:\s+appointment)?|\s+being\s+seen)\b",
    re.I,
)
_MONTH_RE = re.compile(rf"\b({MONTH_NAME_PATTERN})\b", re.I)
_TARGET_RESULTS = frozenset({"normal", "abnormal", "unknown"})


def project_trust_llm(
    *,
    family: str,
    event: str,
    evidence: str,
    attributes: dict[str, Any],
) -> tuple[dict[str, str], str, str, str]:
    """Project one llm fact by trusting emitted attributes and source spans."""

    mentions, status = project_trust_llm_mentions(
        family=family,
        event=event,
        evidence=evidence,
        attributes=attributes,
    )
    if not mentions:
        return {}, "", status, "deterministic.semantic_inventory_trust"
    first = mentions[0]
    return (
        dict(first["attributes"]),
        str(first["text"]),
        status,
        str(first["component_owner"]),
    )


def project_trust_llm_mentions(
    *,
    family: str,
    event: str,
    evidence: str,
    attributes: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    """Return every mention the trust-item llm projector emits for one fact."""

    owner = "deterministic.semantic_inventory_trust"
    attrs = {
        str(key).lower(): str(value) for key, value in attributes.items() if value is not None
    }
    if family == SEIZURE_FREQUENCY.name:
        text = _sf_text(event, attrs)
        if not text:
            return [], "partial"
        mention = {
            "entity": SEIZURE_FREQUENCY.name,
            "text": text,
            "attributes": _sf_legacy(attrs, event),
            "evidence": evidence,
            "component_owner": owner,
        }
        mentions = _last_clinic_mentions(mention, event)
        for item in mentions:
            item["component_owner"] = owner
        status = "materialized" if mentions[0]["attributes"] else "partial"
        return mentions, status
    if family == INVESTIGATIONS.name:
        mentions = _owned(_investigation_mentions(event, evidence, attrs), evidence)
        if not mentions:
            return [], "semantic_only_nontarget_or_no_result"
        return mentions, "materialized"
    return [], "partial"


def project_trust_hybrid(
    *,
    family: str,
    event: str,
    evidence: str,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    """Project one hybrid event with landed v9 tables on that item only."""

    if family in {DIAGNOSIS.name, PRESCRIPTION.name}:
        return project_hybrid_event(
            family=family, event=event, evidence=evidence, index=index
        )
    traces: list[dict[str, Any]] = []
    if family == INVESTIGATIONS.name:
        mentions = _investigation_mentions(event, evidence, {})
        if not mentions:
            traces.append(
                _trace(
                    index=index,
                    action="suppress_nontarget_or_resultless_investigation",
                    after={},
                )
            )
            return [], traces, "semantic_only_nontarget_or_no_result"
        traces.append(
            _trace(
                index=index,
                action="list9_result_from_emitted_item",
                after=dict(mentions[0]["attributes"]),
            )
        )
        return _owned(mentions, evidence), traces, "materialized"
    text = _sf_text(event, {})
    if not text:
        traces.append(_trace(index=index, action="suppress_uncoded_sf", after={}))
        return [], traces, "semantic_only_uncoded_phenomenology"
    attributes = _scoped_count_attributes(event)
    mention = {
        "entity": SEIZURE_FREQUENCY.name,
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
    }
    mentions = _last_clinic_mentions(mention, event)
    traces.append(
        _trace(
            index=index,
            action="trust_item_sf_from_event",
            after=dict(mentions[0]["attributes"]),
        )
    )
    return _owned(mentions, evidence), traces, "materialized"


def _sf_text(event: str, attrs: dict[str, str]) -> str:
    concept = str(attrs.get("concept") or "").strip()
    from_concept = _source_span(event, concept)
    if from_concept and from_concept.lower() not in {"focal", "generalised", "generalized"}:
        return from_concept
    typed = _longest_surface(event, _TYPED_SF_SPANS)
    if typed:
        return typed
    return _longest_surface(event, _GENERIC_SF_SPANS)


def _sf_legacy(attrs: dict[str, str], event: str) -> dict[str, str]:
    legacy: dict[str, str] = {}
    if attrs.get("count"):
        mapped = normalize_count(attrs["count"])
        if mapped.isdigit():
            legacy["NumberOfSeizures"] = mapped
    if attrs.get("lower_count"):
        legacy["LowerNumberOfSeizures"] = attrs["lower_count"]
    if attrs.get("upper_count"):
        legacy["UpperNumberOfSeizures"] = attrs["upper_count"]
    if attrs.get("period"):
        legacy["TimePeriod"] = attrs["period"]
    scoped = _scoped_count_attributes(event)
    for key, value in scoped.items():
        legacy.setdefault(key, value)
    state = attrs.get("state", attrs.get("status", "")).lower().replace("_", "-")
    if state in {"last-event", "seizure-free", "seizure free", "none", "zero"}:
        legacy.setdefault("NumberOfSeizures", "0")
    return legacy


def _scoped_count_attributes(event: str) -> dict[str, str]:
    if _EVERY_PERIOD_RE.search(event):
        return {}
    range_match = _COUNT_RANGE_RE.search(event)
    if range_match:
        return {
            "LowerNumberOfSeizures": range_match.group("count"),
            "UpperNumberOfSeizures": range_match.group("upper"),
        }
    digit = _DIGIT_COUNT_RE.search(event)
    if digit:
        return {"NumberOfSeizures": digit.group("count")}
    word = _WORD_COUNT_RE.search(event)
    if word is None:
        return {}
    if _DURATION_YEARS_RE.search(event) and _DURATION_YEARS_RE.search(word.group(0)):
        return {}
    mapped = normalize_count(word.group("word"))
    if not mapped.isdigit():
        return {}
    return {"NumberOfSeizures": mapped}


def _last_clinic_mentions(mention: dict[str, Any], event: str) -> list[dict[str, Any]]:
    attributes = dict(mention.get("attributes") or {})
    if _LAST_CLINIC_RE.search(event):
        attributes.setdefault("PointInTime", "LastClinic")
        attributes.setdefault("TimeSince_or_TimeOfEvent", "Since")
    mention = {**mention, "attributes": attributes}
    month_match = _MONTH_RE.search(event)
    if not (
        _LAST_CLINIC_RE.search(event)
        and month_match
        and (
            attributes.get("NumberOfSeizures")
            or attributes.get("LowerNumberOfSeizures")
        )
    ):
        return [mention]
    dated = {
        **mention,
        "attributes": {
            key: value
            for key, value in attributes.items()
            if key not in {"PointInTime"}
        },
    }
    dated["attributes"]["TimeSince_or_TimeOfEvent"] = "During"
    dated["attributes"]["MonthDate"] = normalize_month(month_match.group(1))
    return [mention, dated]


def _investigation_mentions(
    event: str,
    evidence: str,
    attrs: dict[str, str],
) -> list[dict[str, Any]]:
    haystack = " ".join(part for part in (attrs.get("name", ""), event, evidence) if part)
    modalities = list(
        dict.fromkeys(match.group(1).upper() for match in _MODALITY_RE.finditer(haystack))
    )
    if not modalities:
        return []
    finding = str(attrs.get("result") or attrs.get("finding") or "").strip().lower()
    if finding not in _TARGET_RESULTS:
        classified = investigation_tables.investigation_result_from_span(
            f"{event} {evidence}".replace("-", " ").strip()
        )
        finding = classified.lower() if classified else ""
    if finding not in _TARGET_RESULTS:
        return []
    result = finding.title()
    mentions: list[dict[str, Any]] = []
    for modality in modalities:
        mentions.append(
            {
                "entity": INVESTIGATIONS.name,
                "text": modality,
                "attributes": {
                    f"{modality}_Performed": "Yes",
                    f"{modality}_Results": result,
                },
            }
        )
    return mentions


def _source_span(source: str, needle: str) -> str:
    if not needle:
        return ""
    index = source.lower().find(needle.lower())
    if index >= 0:
        return source[index : index + len(needle)]
    pattern = re.escape(needle).replace(r"\ ", r"[\s-]+")
    match = re.search(pattern, source, re.I)
    return match.group(0) if match else ""


def _longest_surface(source: str, surfaces: tuple[str, ...]) -> str:
    matches = [_source_span(source, surface) for surface in surfaces]
    matches = [match for match in matches if match]
    return max(matches, key=len) if matches else ""


def _owned(mentions: list[dict[str, Any]], evidence: str) -> list[dict[str, Any]]:
    owned: list[dict[str, Any]] = []
    for mention in mentions:
        row = dict(mention)
        row["evidence"] = evidence
        row["component_owner"] = "deterministic.semantic_inventory_trust"
        owned.append(row)
    return owned


def _trace(*, index: int, action: str, after: dict[str, Any]) -> dict[str, Any]:
    return {
        "fact_index": index,
        "rule_category": "seizure_frequency"
        if "sf" in action
        else "clinical_epilepsy",
        "action": action,
        "evidence": "",
        "before": {},
        "after": after,
        "changed": True,
        "first_prediction_changing_owner": "deterministic",
    }


__all__ = [
    "project_trust_hybrid",
    "project_trust_llm",
    "project_trust_llm_mentions",
]
