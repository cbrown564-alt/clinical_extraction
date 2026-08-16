"""Leftover-form encoder for mention-unit v2 hybrid remasure.

Parses leftover count, period, and investigation-result words from that
item's clinical_name plus evidence. Does not search the letter or change
the landed encoder.
"""

from __future__ import annotations

import re
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as sf_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as investigation_tables,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_count,
    normalize_unit,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory_rules import (
    _is_pending_investigation,
    _is_uncoded_phenomenology,
)

ENCODER_VERSION = "exectv2_mention_unit_leftover_form_v1"
COMPONENT_OWNER = "deterministic_mention_unit_leftover_form"

_MODALITY_RE = re.compile(r"\b(MRI|CT|EEG)\b", re.I)
_EXPLICIT_RESULT_RE = re.compile(r"\b(normal|abnormal|negative|unremarkable)\b", re.I)
_EVERY_PERIOD_RE = re.compile(
    r"\bevery\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    r"(?:days?|weeks?|months?|years?)\b",
    re.I,
)
_COUNT_RANGE_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(?P<upper>\d+(?:\.\d+)?)\b"
)
_DIGIT_SEIZURE_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\b\s*(?:seizures?|episodes?|absences?)\b",
    re.I,
)
_DIGIT_PERIOD_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\b\s+(?:per|a|each)\s+"
    r"(?P<unit>days?|weeks?|months?|years?)\b",
    re.I,
)
_WORD_RE = (
    r"(?:a\s+couple|a\s+few|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"once|twice|none|single|couple|few|several|multiple)"
)
_WORD_SEIZURE_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE})\s+"
    r"(?:(?:secondary\s+generalised|secondary\s+generalized|"
    r"generalised\s+tonic[\s-]*clonic|generalized\s+tonic[\s-]*clonic|"
    r"focal\s+to\s+bilateral\s+convulsive|focal\s+motor|focal|"
    r"absence|myoclonic|dyscognitive)\s+)?"
    r"(?:seizures?|episodes?|absences?)\b",
    re.I,
)
_WORD_PERIOD_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE})\s+(?:per|a|each)\s+"
    r"(?P<unit>days?|weeks?|months?|years?)\b",
    re.I,
)
_PERIOD_RE = re.compile(
    r"\b(?:per|a|each)\s+(?P<unit>days?|weeks?|months?|years?)\b|"
    r"\b(?P<named>daily|weekly|monthly|yearly)\b",
    re.I,
)
_SEIZURE_FREE_RE = re.compile(r"seizure\s*-?free|no further seizures", re.I)
_LAST_EVENT_CUE_RE = re.compile(
    r"\b(last seizure|last seizures|last event|has had none since|none since|"
    r"no further|not had any further|has not had any(?: further)?|"
    r"seizure[- ]free since|no seizures?|no absences)\b",
    re.IGNORECASE,
)
_NAMED_PERIODS = {
    "daily": "Day",
    "weekly": "Week",
    "monthly": "Month",
    "yearly": "Year",
}
_COUNT_KEYS = (
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
)


def project_leftover_form_sf(
    *,
    text: str,
    evidence: str,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    haystack = f"{text} {evidence}".strip()
    traces: list[dict[str, Any]] = []
    seed_attrs, count_action, period_action = leftover_sf_attributes(haystack)
    seed = {
        "entity": SEIZURE_FREQUENCY.name,
        "text": text.strip(),
        "attributes": seed_attrs,
        "evidence": evidence,
    }
    rewritten, actions = sf_encoding.apply_sf_attribute_encoding([seed])
    mention = dict(rewritten[0]) if rewritten else seed
    raw_attrs = mention.get("attributes")
    attrs = {
        str(key): str(value)
        for key, value in (raw_attrs if isinstance(raw_attrs, dict) else {}).items()
    }
    if _zero_state(haystack) and not _has_count(attrs):
        attrs["NumberOfSeizures"] = "0"
        attrs.setdefault("TimeSince_or_TimeOfEvent", "Since")
        mention["attributes"] = attrs
        traces.append(
            _trace(
                index=index,
                action="leftover_form.sf_zero",
                evidence=evidence,
                before={"text": text},
                after=dict(attrs),
            )
        )
    if count_action:
        traces.append(
            _trace(
                index=index,
                action=count_action,
                evidence=evidence,
                before={"text": text},
                after=dict(seed_attrs),
            )
        )
    if period_action:
        traces.append(
            _trace(
                index=index,
                action=period_action,
                evidence=evidence,
                before={"text": text},
                after=dict(seed_attrs),
            )
        )
    for action in actions:
        traces.append(
            _trace(
                index=index,
                action=str(action.get("rule_id") or action.get("action") or ""),
                evidence=evidence,
                before={"text": text},
                after=dict(attrs),
            )
        )
    if _is_uncoded_phenomenology(haystack, attrs):
        traces.append(
            _trace(
                index=index,
                action="suppress_uncoded_or_noise_sf",
                evidence=evidence,
                before={"text": text},
                after={},
            )
        )
        return [], traces, "semantic_only_uncoded_phenomenology"
    mention["attributes"] = attrs
    mention["evidence"] = evidence
    mention.setdefault("component_owner", COMPONENT_OWNER)
    return [mention], traces, "materialized"


def project_leftover_form_investigation(
    *,
    text: str,
    evidence: str,
    index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    haystack = f"{text} {evidence}".strip()
    traces: list[dict[str, Any]] = []
    match = _MODALITY_RE.search(haystack)
    if match is None or _is_pending_investigation(haystack):
        traces.append(
            _trace(
                index=index,
                action="suppress_pending_investigation",
                evidence=evidence,
                before={"text": text},
                after={},
            )
        )
        return [], traces, "semantic_only_pending_investigation"
    modality = match.group(1).upper()
    finding, list9 = leftover_investigation_result(haystack)
    attributes = {f"{modality}_Performed": "Yes", f"{modality}_Results": finding}
    if list9:
        traces.append(
            _trace(
                index=index,
                action="leftover_form.ix_result",
                evidence=evidence,
                before={"text": text},
                after=dict(attributes),
            )
        )
    mention = {
        "entity": INVESTIGATIONS.name,
        "text": modality,
        "attributes": attributes,
        "evidence": evidence,
        "component_owner": COMPONENT_OWNER,
    }
    return [mention], traces, "materialized"


def leftover_sf_attributes(haystack: str) -> tuple[dict[str, str], str, str]:
    attributes: dict[str, str] = {}
    count_action = ""
    period_action = ""
    if _EVERY_PERIOD_RE.search(haystack) or _zero_state(haystack):
        period = _leftover_period(haystack)
        if period and not _EVERY_PERIOD_RE.search(haystack):
            attributes["TimePeriod"] = period
            attributes["NumberOfTimePeriods"] = "1"
            period_action = "leftover_form.sf_period"
        return attributes, count_action, period_action
    range_match = _COUNT_RANGE_RE.search(haystack)
    digit_period = _DIGIT_PERIOD_RE.search(haystack)
    digit_seizure = _DIGIT_SEIZURE_RE.search(haystack)
    word_period = _WORD_PERIOD_RE.search(haystack)
    word_seizure = _WORD_SEIZURE_RE.search(haystack)
    if range_match:
        attributes["LowerNumberOfSeizures"] = range_match.group("count")
        attributes["UpperNumberOfSeizures"] = range_match.group("upper")
        count_action = "leftover_form.sf_count"
    elif digit_period:
        attributes["NumberOfSeizures"] = digit_period.group("count")
        count_action = "leftover_form.sf_count"
    elif digit_seizure:
        attributes["NumberOfSeizures"] = digit_seizure.group("count")
        count_action = "leftover_form.sf_count"
    elif word_period and not _duration_year_count(haystack, word_period.group("word")):
        mapped = normalize_count(word_period.group("word"))
        if mapped.isdigit():
            attributes["NumberOfSeizures"] = mapped
            count_action = "leftover_form.sf_count"
    elif word_seizure and not _duration_year_count(haystack, word_seizure.group("word")):
        mapped = normalize_count(word_seizure.group("word"))
        if mapped.isdigit():
            attributes["NumberOfSeizures"] = mapped
            count_action = "leftover_form.sf_count"
    period = _leftover_period(haystack)
    if period:
        attributes["TimePeriod"] = period
        attributes.setdefault("NumberOfTimePeriods", "1")
        period_action = "leftover_form.sf_period"
    return attributes, count_action, period_action


def leftover_investigation_result(haystack: str) -> tuple[str, bool]:
    explicit = _EXPLICIT_RESULT_RE.search(haystack)
    if explicit:
        token = explicit.group(1).lower()
        finding = "Normal" if token in {"normal", "negative", "unremarkable"} else "Abnormal"
        return finding, False
    classified = investigation_tables.investigation_result_from_span(
        haystack.replace("-", " ").strip()
    )
    if classified in {"Normal", "Abnormal", "Unknown"}:
        return classified, classified != "Unknown"
    return "Unknown", False


def _leftover_period(haystack: str) -> str:
    if _EVERY_PERIOD_RE.search(haystack):
        return ""
    match = _PERIOD_RE.search(haystack)
    if match is None:
        return ""
    named = match.group("named")
    if named:
        return _NAMED_PERIODS[named.lower()]
    return normalize_unit(match.group("unit"))


def _zero_state(haystack: str) -> bool:
    return bool(_LAST_EVENT_CUE_RE.search(haystack) or _SEIZURE_FREE_RE.search(haystack))


def _duration_year_count(haystack: str, word: str) -> bool:
    return bool(re.search(rf"\b{re.escape(word)}\s+years?\b", haystack, re.I))


def _has_count(attributes: dict[str, str]) -> bool:
    return any(attributes.get(key) for key in _COUNT_KEYS)


def _trace(
    *,
    index: int,
    action: str,
    evidence: str,
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    return {
        "fact_index": index,
        "rule_category": "seizure_frequency"
        if action.startswith("leftover_form.sf") or action.startswith("encoding.")
        or action == "suppress_uncoded_or_noise_sf"
        else "clinical_epilepsy",
        "action": action,
        "evidence": evidence,
        "before": before,
        "after": after,
        "changed": True,
        "first_prediction_changing_owner": "deterministic",
    }
