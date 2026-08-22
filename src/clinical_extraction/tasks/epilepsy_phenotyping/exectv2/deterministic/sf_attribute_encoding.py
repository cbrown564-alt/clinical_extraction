"""Gold-free SF attribute encoding on already-emitted hybrid mentions.

Guideline List 11 and the v0.9.24 prompt codebook. Rewrites attributes or
mention text on model-selected SeizureFrequency mentions. Does not invent
events and does not import the rules-only extractor.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    evidence_refined_seizure_type_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_count,
    normalize_unit,
)

COMPONENT_OWNER = "deterministic_sf_attribute_encoding"
ENCODING_VERSION = "exectv2_hybrid_sf_attribute_encoding_v0.3"

_RANGE_IN_FIELD_RE = re.compile(
    r"^\s*(?P<low>\d+)\s*(?:-|–|to|or)\s*(?P<high>\d+)\s*$",
    re.IGNORECASE,
)
_INTERVAL_RE = re.compile(
    r"\bevery\s+(?:"
    r"(?P<low>\d+)\s*(?:to|or|-|–)\s*"
    r")?(?P<high>\d+)\s+(?P<unit>days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
_SEIZURE_WORD_RE = re.compile(r"\bseizures?\b", re.IGNORECASE)
_SEIZURE_FREQUENCY_TEXT_RE = re.compile(r"^\s*seizure\s+frequency\s*$", re.IGNORECASE)
_LAST_EVENT_CUE_RE = re.compile(
    r"\b(last seizure|last seizures|last event|has had none since|none since|"
    r"no further|not had any further|has not had any(?: further)?|"
    r"seizure[- ]free since|no seizures?|no absences)\b",
    re.IGNORECASE,
)
_REMOTE_SINCE_RE = re.compile(
    r"\bsince (?:her |his |the )?(?:early )?(?:teenage(?: years)?|teens|"
    r"childhood|adolescence|school years)\b",
    re.IGNORECASE,
)
_LAST_CLINIC_FRAME_RE = re.compile(
    r"\blast clinic\b",
    re.IGNORECASE,
)
_BLANK_LAST_EVENT_COUNT = frozenset({"", "no", "none", "n/a", "na"})
_LAST_CLINIC_RE = re.compile(
    r"\bsince (?:her |his |the )?last clinic\b",
    re.IGNORECASE,
)
_EXPLICIT_FURTHER_SEIZURES_RE = re.compile(
    r"\b(?:has|have|had)\s+had\s+further\b[^.;\n]{0,120}\bseizures?\b",
    re.IGNORECASE,
)


def apply_sf_attribute_encoding(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Rewrite emitted SF attributes. Returns mentions and action records."""

    out: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        working = _copy_mention(mention)
        if str(working.get("entity") or "") != SEIZURE_FREQUENCY.name:
            out.append(working)
            continue
        for rule_id, apply in (
            ("encoding.word_number", _rewrite_word_number),
            ("encoding.range_split", _rewrite_range),
            ("encoding.interval_completer", _complete_interval),
            ("encoding.last_event_zero", _complete_last_event_zero),
            ("encoding.last_clinic_frame", _complete_last_clinic),
            ("encoding.dated_heading_count", _complete_dated_heading),
            ("encoding.mention_text_cleanup", _cleanup_mention_text),
        ):
            rewritten = apply(working)
            if rewritten is not working:
                actions.append(
                    {
                        "action": "repair",
                        "rule_id": rule_id,
                        "text": str(working.get("text") or ""),
                    }
                )
                working = _copy_mention(rewritten)
        out.append(working)
    return out, actions


SF_SELECT_NAMED_TYPE_RULE = "selection.sf_named_type_from_evidence"
SF_SELECT_RECURRENCE_BOUND_RULE = "selection.sf_explicit_recurrence_lower_bound"


def apply_sf_select_local_evidence(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Apply select-authority SF type and recurrence rewrites."""

    out: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        working = _copy_mention(mention)
        if str(working.get("entity") or "") != SEIZURE_FREQUENCY.name:
            out.append(working)
            continue
        bound = complete_explicit_nonzero_state(working)
        if bound is not working:
            working = _copy_mention(bound)
            actions.append(
                {
                    "action": "repair",
                    "rule_id": SF_SELECT_RECURRENCE_BOUND_RULE,
                    "text": str(working.get("text") or ""),
                }
            )
        attrs = dict(working.get("attributes") or {})
        if attrs.get("NumberOfSeizures") != "0":
            text = str(working.get("text") or "")
            refined = evidence_refined_seizure_type_name(
                text, str(working.get("evidence") or "")
            )
            if refined != text:
                working["text"] = refined
                actions.append(
                    {
                        "action": "repair",
                        "rule_id": SF_SELECT_NAMED_TYPE_RULE,
                        "text": text,
                    }
                )
        out.append(working)
    return out, actions


def complete_explicit_nonzero_state(
    mention: Mapping[str, Any],
) -> dict[str, Any] | Mapping[str, Any]:
    """Select a nonzero lower bound from explicit ``has had further seizures``.

    The wording proves recurrence but not an exact count, so the rule writes a
    lower bound of one rather than fabricating a point estimate. It only acts on
    an already-selected seizure-frequency mention with no count attributes.
    """

    attrs = dict(mention.get("attributes") or {})
    if any(
        attrs.get(key)
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        return mention
    evidence = str(mention.get("evidence") or "")
    if _EXPLICIT_FURTHER_SEIZURES_RE.search(evidence) is None:
        return mention
    repaired = _copy_mention(mention)
    attrs["LowerNumberOfSeizures"] = "1"
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _rewrite_word_number(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    attrs = dict(mention.get("attributes") or {})
    raw = str(attrs.get("NumberOfSeizures") or "").strip()
    if not raw or raw.isdigit():
        return mention
    mapped = normalize_count(raw)
    if mapped == raw or not mapped.isdigit():
        return mention
    repaired = _copy_mention(mention)
    attrs["NumberOfSeizures"] = mapped
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _rewrite_range(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    attrs = dict(mention.get("attributes") or {})
    raw = str(attrs.get("NumberOfSeizures") or "").strip()
    match = _RANGE_IN_FIELD_RE.fullmatch(raw)
    if match is None:
        return mention
    repaired = _copy_mention(mention)
    attrs.pop("NumberOfSeizures", None)
    attrs["LowerNumberOfSeizures"] = match.group("low")
    attrs["UpperNumberOfSeizures"] = match.group("high")
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _complete_interval(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    attrs = dict(mention.get("attributes") or {})
    if attrs.get("NumberOfSeizures") or attrs.get("LowerNumberOfSeizures"):
        return mention
    evidence = " ".join(
        part
        for part in (str(mention.get("text") or ""), str(mention.get("evidence") or ""))
        if part
    )
    match = _INTERVAL_RE.search(evidence)
    if match is None:
        return mention
    repaired = _copy_mention(mention)
    attrs["NumberOfSeizures"] = "1"
    unit = normalize_unit(match.group("unit"))
    attrs["TimePeriod"] = unit
    if match.group("low"):
        attrs["LowerNumberOfTimePeriods"] = match.group("low")
        attrs["UpperNumberOfTimePeriods"] = match.group("high")
        attrs.pop("NumberOfTimePeriods", None)
    else:
        attrs["NumberOfTimePeriods"] = match.group("high")
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _complete_last_event_zero(
    mention: Mapping[str, Any],
) -> dict[str, Any] | Mapping[str, Any]:
    """Map last-event / none-since language to NumberOfSeizures=0.

    Applies only to already-emitted mentions. Does not invent events.
    Fires when the count is missing, a negation word, or a year token
    parked in NumberOfSeizures.
    """

    haystack = " ".join(
        part
        for part in (str(mention.get("text") or ""), str(mention.get("evidence") or ""))
        if part
    )
    attrs = dict(mention.get("attributes") or {})
    last_clinic = bool(
        attrs.get("PointInTime") == "LastClinic" or _LAST_CLINIC_FRAME_RE.search(haystack)
    )
    remote_since = bool(_REMOTE_SINCE_RE.search(haystack))
    last_event = bool(_LAST_EVENT_CUE_RE.search(haystack))
    if not last_event and not remote_since:
        return mention
    raw = str(attrs.get("NumberOfSeizures") or "").strip()
    already_free = raw == "0" and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    if already_free:
        return mention
    year_as_count = bool(_YEAR_RE.fullmatch(raw))
    has_range = bool(attrs.get("LowerNumberOfSeizures") or attrs.get("UpperNumberOfSeizures"))
    blank_or_year = raw in _BLANK_LAST_EVENT_COUNT or year_as_count or raw == "0"
    if last_clinic and not blank_or_year:
        return mention
    if last_clinic and has_range:
        return mention
    range_or_remote = remote_since and (has_range or not blank_or_year)
    last_event_range = last_event and has_range and not last_clinic
    if not blank_or_year and not range_or_remote and not last_event_range:
        return mention
    repaired = _copy_mention(mention)
    new_attrs = dict(attrs)
    new_attrs["NumberOfSeizures"] = "0"
    new_attrs["TimeSince_or_TimeOfEvent"] = "Since"
    if range_or_remote or has_range:
        new_attrs.pop("LowerNumberOfSeizures", None)
        new_attrs.pop("UpperNumberOfSeizures", None)
    if year_as_count and not new_attrs.get("YearDate"):
        new_attrs["YearDate"] = raw
    repaired["attributes"] = new_attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _complete_last_clinic(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    evidence = str(mention.get("evidence") or "")
    if not _LAST_CLINIC_RE.search(evidence):
        return mention
    attrs = dict(mention.get("attributes") or {})
    already_framed = (
        attrs.get("PointInTime") == "LastClinic"
        and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    )
    if already_framed:
        return mention
    repaired = _copy_mention(mention)
    attrs["PointInTime"] = "LastClinic"
    attrs["TimeSince_or_TimeOfEvent"] = "Since"
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _complete_dated_heading(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    attrs = dict(mention.get("attributes") or {})
    if any(
        attrs.get(key)
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "FrequencyChange",
        )
    ):
        return mention
    evidence = str(mention.get("evidence") or "")
    if _LAST_EVENT_CUE_RE.search(evidence):
        return mention
    year = attrs.get("YearDate")
    if not year:
        year_match = _YEAR_RE.search(evidence)
        if year_match is None:
            return mention
        year = year_match.group(1)
    if not _SEIZURE_WORD_RE.search(evidence) and not _SEIZURE_WORD_RE.search(
        str(mention.get("text") or "")
    ):
        return mention
    repaired = _copy_mention(mention)
    attrs["NumberOfSeizures"] = "1"
    attrs["YearDate"] = str(year)
    attrs["TimeSince_or_TimeOfEvent"] = "During"
    repaired["attributes"] = attrs
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _cleanup_mention_text(mention: Mapping[str, Any]) -> dict[str, Any] | Mapping[str, Any]:
    text = str(mention.get("text") or "")
    if not _SEIZURE_FREQUENCY_TEXT_RE.match(text):
        return mention
    evidence = str(mention.get("evidence") or "")
    replacement = "seizures" if re.search(r"\bseizures\b", evidence, re.I) else "seizure"
    if replacement.lower() not in evidence.lower() and replacement.lower() not in text.lower():
        return mention
    if replacement == text:
        return mention
    repaired = _copy_mention(mention)
    repaired["text"] = replacement
    repaired["component_owner"] = COMPONENT_OWNER
    return repaired


def _copy_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    copied = dict(mention)
    copied["attributes"] = {
        str(key): str(value) for key, value in dict(mention.get("attributes") or {}).items()
    }
    return copied
