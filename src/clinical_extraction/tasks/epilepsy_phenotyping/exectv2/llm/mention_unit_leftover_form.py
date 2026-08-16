"""Leftover-form encoder for mention-unit v2 hybrid remasure.

Parses leftover count, period, and investigation-result words from that
item's clinical_name plus evidence. Does not search the letter or change
the landed encoder.
"""

from __future__ import annotations

import re
from typing import Any, Literal

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit_shared import (
    _is_pending_investigation,
    _is_uncoded_phenomenology,
)

ENCODER_VERSION = "exectv2_mention_unit_leftover_form_v1"
ENCODER_VERSION_V2 = "exectv2_mention_unit_leftover_form_v2"
ENCODER_VERSION_V3 = "exectv2_mention_unit_leftover_form_v3"
ENCODER_VERSION_V4 = "exectv2_mention_unit_leftover_form_v4"
COMPONENT_OWNER = "deterministic_mention_unit_leftover_form"
LeftoverFormVariant = Literal[
    "v1",
    "intervening",
    "intervening_v3",
    "episodes_v4",
    "implicit_v4",
    "last_event_v4",
    "implicit_period",
    "last_event",
]

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
_SEIZURE_FREE_WIDE_RE = re.compile(
    r"seizure\s*-?free|seizures\s+free|seizrue\s+free|no further seizures",
    re.I,
)
_LAST_EVENT_CUE_RE = re.compile(
    r"\b(last seizure|last seizures|last event|has had none since|none since|"
    r"no further|not had any further|has not had any(?: further)?|"
    r"seizure[- ]free since|no seizures?|no absences)\b",
    re.IGNORECASE,
)
_LAST_EVENT_CUE_WIDE_RE = re.compile(
    r"\b(last seizure|last seizures|last event|has had none since|none since|"
    r"no further|not had any further|has not had any(?: further)?|"
    r"seizure[- ]free since|no seizures?|no absences|"
    r"(?:seizures?|events?|episodes?)\s+last\s+(?:month|week|year)|"
    r"no events? since)\b",
    re.IGNORECASE,
)
_BARE_EVERY_PERIOD_RE = re.compile(
    r"\bevery\s+(?P<unit>days?|weeks?|months?|years?)\b",
    re.I,
)
_TIMES_PERIOD_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\s+times\s+(?:per|a|each)\s+"
    r"(?P<unit>days?|weeks?|months?|years?)\b",
    re.I,
)
_IN_THE_LAST_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\s+in the last\s+"
    r"(?P<n>one|two|three|four|five|six|seven|eight|nine|ten|\d+)?\s*"
    r"(?P<unit>days?|weeks?|months?|years?)\b",
    re.I,
)
_COUNT_SINCE_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\s+since\b",
    re.I,
)
_INTERVENING_DIGIT_SEIZURE_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\b(?:\s+\w+){0,4}\s+"
    r"(?:seizures?|absences?|jerks?)\b",
    re.I,
)
_INTERVENING_WORD_SEIZURE_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE})\b(?:\s+\w+){{0,4}}\s+"
    r"(?:seizures?|absences?|jerks?)\b",
    re.I,
)
_SEIZURE_THEN_COUNT_RE = re.compile(
    rf"(?:seizures?|absences?|jerks?)\b.{{0,40}}?\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\b",
    re.I,
)
_DURATION_COUNT_RE = re.compile(
    rf"\b(?:for\s+(?:around\s+)?)?(?:{_WORD_RE}|\d+)\s+years?\b",
    re.I,
)
_TIME_UNIT_RE = r"(?:days?|weeks?|months?|years?)"
_MONTH_NAME_RE = (
    r"(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)"
)
_EPISODE_RANGE_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\s+(?:or|to|-|–)\s+"
    rf"(?P<upper>{_WORD_RE}|\d+(?:\.\d+)?)\s+"
    r"(?:further\s+)?(?:events?|episodes?)\b",
    re.I,
)
_EPISODE_DIGIT_RE = re.compile(
    r"\b(?P<count>\d+(?:\.\d+)?)\b(?:\s+\w+){0,4}\s+(?:events?|episodes?)\b",
    re.I,
)
_EPISODE_WORD_RE = re.compile(
    rf"\b(?P<word>{_WORD_RE})\b(?:\s+\w+){{0,4}}\s+(?:events?|episodes?)\b",
    re.I,
)
_EVENT_THEN_COUNT_RE = re.compile(
    rf"(?:events?|episodes?)\b.{{0,40}}?\b(?P<word>{_WORD_RE}|\d+(?:\.\d+)?)\b",
    re.I,
)
_COLLAPSE_EPISODE_RE = re.compile(
    r"\b(?:collapse|faint(?:ing)?|fall|syncop(?:e|al))\b",
    re.I,
)
_STOPPED_EPISODES_RE = re.compile(
    r"\b(?:stopp(?:ed|ing)|has stopped|have stopped)\s+(?:the\s+)?(?:episodes?|events?)\b",
    re.I,
)
_CLUSTER_COUNT_RE = re.compile(
    rf"\bcluster of\s+(?:{_WORD_RE}|\d+(?:\.\d+)?)\b",
    re.I,
)
_IMPLICIT_AGO_RE = re.compile(rf"\b(?:a\s+)?{_TIME_UNIT_RE}\s+ago\b", re.I)
_IMPLICIT_RATE_RE = re.compile(
    rf"\b(?:{_WORD_RE}|\d+(?:\.\d+)?)\s+(?:or\s+(?:{_WORD_RE}|\d+(?:\.\d+)?)\s+)?"
    r"times\b",
    re.I,
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
    variant: LeftoverFormVariant = "v1",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    haystack = f"{text} {evidence}".strip()
    traces: list[dict[str, Any]] = []
    seed_attrs, count_action, period_action = leftover_sf_attributes(
        haystack, variant=variant
    )
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
    should_zero = (
        _last_event_v4_zero(evidence)
        if variant == "last_event_v4"
        else _zero_state(haystack, variant=variant)
    )
    if should_zero and not _has_count(attrs):
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


def leftover_sf_attributes(
    haystack: str, *, variant: LeftoverFormVariant = "v1"
) -> tuple[dict[str, str], str, str]:
    attributes: dict[str, str] = {}
    count_action = ""
    period_action = ""
    early_zero = variant != "last_event_v4" and _zero_state(
        haystack, variant=variant
    )
    if _EVERY_PERIOD_RE.search(haystack) or early_zero:
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
    elif variant == "intervening":
        attributes, count_action, period_action = _intervening_form(haystack)
    elif variant in {
        "intervening_v3",
        "episodes_v4",
        "implicit_v4",
        "last_event_v4",
    }:
        if variant == "episodes_v4":
            attributes, count_action, period_action = _episode_form(haystack)
        if not _has_count(attributes):
            attributes, count_action, period_action = _intervening_form(
                haystack, guarded=True
            )
    period = _leftover_period(haystack)
    if variant in {"implicit_period", "implicit_v4"}:
        bare = _bare_every_period(haystack)
        if bare:
            period = bare
    if period:
        attributes["TimePeriod"] = period
        attributes.setdefault("NumberOfTimePeriods", "1")
        period_action = period_action or "leftover_form.sf_period"
        if variant == "implicit_period" and not _has_count(attributes):
            attributes["NumberOfSeizures"] = "1"
            count_action = count_action or "leftover_form.sf_count"
        if (
            variant == "implicit_v4"
            and not _has_count(attributes)
            and not _implicit_period_blocked(haystack)
        ):
            attributes["NumberOfSeizures"] = "1"
            count_action = count_action or "leftover_form.sf_count"
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


def _zero_state(haystack: str, *, variant: LeftoverFormVariant = "v1") -> bool:
    if variant == "last_event":
        return bool(
            _LAST_EVENT_CUE_WIDE_RE.search(haystack)
            or _SEIZURE_FREE_WIDE_RE.search(haystack)
        )
    return bool(_LAST_EVENT_CUE_RE.search(haystack) or _SEIZURE_FREE_RE.search(haystack))


def _bare_every_period(haystack: str) -> str:
    if _EVERY_PERIOD_RE.search(haystack):
        return ""
    match = _BARE_EVERY_PERIOD_RE.search(haystack)
    if match is None:
        return ""
    return normalize_unit(match.group("unit"))


def leftover_count_span_is_false_read(haystack: str, start: int, end: int) -> bool:
    """Age, duration / last-event span, or calendar date at this count span."""
    left = haystack[max(0, start - 48) : start]
    right = haystack[end : min(len(haystack), end + 48)]
    if re.search(r"\b(?:at\s+the\s+)?age\s+of\s+$", left, re.I) or re.search(
        r"\baged\s+$", left, re.I
    ):
        return True
    if re.search(rf"^\s+{_TIME_UNIT_RE}\b", right, re.I):
        return True
    if re.search(rf"^\s+{_MONTH_NAME_RE}\b", right, re.I):
        return True
    return bool(re.search(rf"\b{_MONTH_NAME_RE}\s+$", left, re.I))


def leftover_recovered_count_is_guard_failure(haystack: str, token: str) -> bool:
    """True when every occurrence of token in haystack is a guarded span."""
    found = False
    unguarded = False
    for match in re.finditer(rf"\b{re.escape(token)}\b", haystack, re.I):
        found = True
        if not leftover_count_span_is_false_read(haystack, match.start(), match.end()):
            unguarded = True
    return found and not unguarded


def _episode_form(haystack: str) -> tuple[dict[str, str], str, str]:
    if _COLLAPSE_EPISODE_RE.search(haystack) or _STOPPED_EPISODES_RE.search(haystack):
        return {}, "", ""
    attributes: dict[str, str] = {}
    range_match = _first_intervening_match(
        _EPISODE_RANGE_RE, haystack, "word", guarded=True
    )
    if range_match is not None:
        lower = _mapped_count(range_match.group("word"))
        upper = _mapped_count(range_match.group("upper"))
        if lower and upper:
            attributes["LowerNumberOfSeizures"] = lower
            attributes["UpperNumberOfSeizures"] = upper
            return attributes, "leftover_form.sf_count", ""
    digit = _first_intervening_match(
        _EPISODE_DIGIT_RE, haystack, "count", guarded=True
    )
    if digit is not None:
        attributes["NumberOfSeizures"] = digit.group("count")
        return attributes, "leftover_form.sf_count", ""
    word = _first_intervening_match(
        _EPISODE_WORD_RE, haystack, "word", guarded=True
    )
    if word is not None:
        mapped = _mapped_count(word.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            return attributes, "leftover_form.sf_count", ""
    later = _first_intervening_match(
        _EVENT_THEN_COUNT_RE, haystack, "word", guarded=True
    )
    if later is not None:
        mapped = _mapped_count(later.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            return attributes, "leftover_form.sf_count", ""
    return attributes, "", ""


def _implicit_period_blocked(haystack: str) -> bool:
    return bool(_IMPLICIT_AGO_RE.search(haystack) or _IMPLICIT_RATE_RE.search(haystack))


def _last_event_v4_zero(evidence: str) -> bool:
    if _CLUSTER_COUNT_RE.search(evidence):
        return False
    return bool(
        _LAST_EVENT_CUE_WIDE_RE.search(evidence)
        or _SEIZURE_FREE_WIDE_RE.search(evidence)
    )


def _intervening_form(
    haystack: str, *, guarded: bool = False
) -> tuple[dict[str, str], str, str]:
    attributes: dict[str, str] = {}
    times = _first_intervening_match(
        _TIMES_PERIOD_RE, haystack, "word", guarded=guarded
    )
    if times is not None:
        mapped = _mapped_count(times.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            attributes["TimePeriod"] = normalize_unit(times.group("unit"))
            attributes["NumberOfTimePeriods"] = "1"
            return attributes, "leftover_form.sf_count", "leftover_form.sf_period"
    window = _first_intervening_match(
        _IN_THE_LAST_RE, haystack, "word", guarded=guarded
    )
    if window is not None:
        mapped = _mapped_count(window.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            attributes["TimePeriod"] = normalize_unit(window.group("unit"))
            period_n = window.group("n")
            attributes["NumberOfTimePeriods"] = (
                _mapped_count(period_n) if period_n else "1"
            )
            return attributes, "leftover_form.sf_count", "leftover_form.sf_period"
    since = _first_intervening_match(
        _COUNT_SINCE_RE, haystack, "word", guarded=guarded
    )
    if since is not None:
        mapped = _mapped_count(since.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            attributes["TimeSince_or_TimeOfEvent"] = "Since"
            return attributes, "leftover_form.sf_count", ""
    digit = _first_intervening_match(
        _INTERVENING_DIGIT_SEIZURE_RE, haystack, "count", guarded=guarded
    )
    if digit is not None:
        attributes["NumberOfSeizures"] = digit.group("count")
        return attributes, "leftover_form.sf_count", ""
    word = _first_intervening_match(
        _INTERVENING_WORD_SEIZURE_RE, haystack, "word", guarded=guarded
    )
    if word is not None:
        mapped = _mapped_count(word.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            return attributes, "leftover_form.sf_count", ""
    later = _first_intervening_match(
        _SEIZURE_THEN_COUNT_RE, haystack, "word", guarded=guarded
    )
    if later is not None:
        mapped = _mapped_count(later.group("word"))
        if mapped:
            attributes["NumberOfSeizures"] = mapped
            return attributes, "leftover_form.sf_count", ""
    return attributes, "", ""


def _first_intervening_match(
    pattern: re.Pattern[str],
    haystack: str,
    group: str,
    *,
    guarded: bool,
) -> re.Match[str] | None:
    matches: list[re.Match[str] | None]
    if guarded:
        matches = list(pattern.finditer(haystack))
    else:
        matches = [pattern.search(haystack)]
    for match in matches:
        if match is None:
            continue
        token = match.group(group)
        if not token or _duration_count(haystack, token):
            continue
        if guarded and leftover_count_span_is_false_read(
            haystack, *_token_span(match, token)
        ):
            continue
        if _mapped_count(token):
            return match
    return None


def _token_span(match: re.Match[str], token: str) -> tuple[int, int]:
    for name in ("count", "word"):
        grouped = match.groupdict().get(name)
        if grouped and grouped.casefold() == token.casefold():
            return match.span(name)
    return match.span()


def _mapped_count(token: str) -> str:
    if token.isdigit() or re.fullmatch(r"\d+(?:\.\d+)?", token):
        return token
    mapped = normalize_count(token)
    return mapped if mapped.isdigit() else ""


def _duration_count(haystack: str, word: str) -> bool:
    return bool(
        _duration_year_count(haystack, word)
        or re.search(
            rf"\b(?:for\s+(?:around\s+)?)?{re.escape(word)}\s+years?\b",
            haystack,
            re.I,
        )
        or _DURATION_COUNT_RE.search(haystack)
        and re.search(rf"\b{re.escape(word)}\s+years?\b", haystack, re.I)
    )


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
