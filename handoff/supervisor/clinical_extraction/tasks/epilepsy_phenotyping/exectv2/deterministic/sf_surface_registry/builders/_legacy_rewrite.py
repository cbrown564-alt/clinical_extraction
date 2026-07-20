"""Legacy SF convention rewrite functions (Stack B).

.. deprecated::
    Extracted from ``_legacy_impl``; behavior-preserving. Prefer
    ``sf_surface_registry.adapters.convention`` for new imports.
"""
# ruff: noqa: F405 — legacy regex constants are star-imported from ``_legacy_constants``.

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

from ._legacy_constants import *  # noqa: F401,F403 (legacy regex constants)


def sf_convention_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Apply SF benchmark rewrites.

    Returns ``(new_text, new_attributes, rule_id)`` when a rewrite fires, else
    ``None``. Attributes are returned as a fresh dict so callers can replace.
    """

    attrs = dict(attributes)
    phrase = normalize_phrase(text)
    surface = " ".join(part for part in (text, evidence) if part)

    format_rewrite = _sf_operand_format_rewrite(text, surface=surface, attributes=attrs)
    if format_rewrite is not None:
        return format_rewrite

    match = re.search(_SF_GENERIC_EVERY_RANGE_RE, surface)
    if match is not None:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = match.group("low")
        attrs["UpperNumberOfTimePeriods"] = match.group("high")
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_range_phrase_to_generic_seizures"
    if phrase in {"no seizures", "not had any more seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizures", attrs, "rewrite_no_seizures_phrase_to_generic_seizure_free"
    if phrase == "seizures free":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_seizures_free_typo_to_generic"
    if phrase in {"once or twice a month", "3 seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        if phrase == "3 seizures":
            attrs["NumberOfSeizures"] = "3"
        else:
            attrs["LowerNumberOfSeizures"] = "1"
            attrs["UpperNumberOfSeizures"] = "2"
            attrs["NumberOfTimePeriods"] = "1"
            attrs["TimePeriod"] = "Month"
        return "seizures", attrs, "rewrite_generic_rate_phrase_to_cui"
    if phrase == "one seizure" and not _SF_RISK_COUNSELLING_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_one_seizure_phrase_to_cui"
    if phrase in {"fairly frequent seizures", "frequent seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs.pop("NumberOfSeizures", None)
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        return "seizures", attrs, "rewrite_frequent_seizures_phrase_to_unknown_cui"
    if phrase == "one focal motor seizure":
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizure"
        attrs["NumberOfSeizures"] = "1"
        return "focal motor seizure", attrs, "rewrite_one_focal_motor_to_cui"
    if phrase == "single seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_single_seizure_phrase_to_cui"
    if phrase == "last seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizure", attrs, "rewrite_last_seizure_phrase_to_generic_free"
    if phrase == "seizure like this" and re.search(
        r"\bfocal motor seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizures"
        attrs["NumberOfSeizures"] = "0"
        return "focal motor seizures", attrs, "rewrite_anaphoric_focal_motor_free"
    if phrase.startswith("focal seizures with altered awareness") and re.search(
        r"\blast event\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0270834"
        attrs["CUIPhrase"] = "focal seizures with altered awareness"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal seizures with altered awareness",
            attrs,
            "rewrite_fsaw_last_event_to_seizure_free",
        )
    if phrase == "she" and re.search(
        r"\bnow she is having between 3 and 4 per week\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["LowerNumberOfSeizures"] = "3"
        attrs["UpperNumberOfSeizures"] = "4"
        attrs["NumberOfTimePeriods"] = "1"
        attrs["TimePeriod"] = "Week"
        return "seizures", attrs, "rewrite_pronoun_rate_to_generic_seizures"
    if phrase in {"generlised tonic clonic seizure", "generlised tonic clonic seizures"}:
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return "generalised tonic clonic seizures", attrs, "rewrite_typo_gtc_to_cui"
    if phrase == "absence like seizures" and (
        attrs.get("NumberOfSeizures") or attrs.get("YearDate")
    ):
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absence like seizures"
        return (
            "absence like seizures",
            attrs,
            "rewrite_absence_like_dated_occurrence_to_cui",
        )
    if phrase in {"occasional absences", "absence like seizures"}:
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        attrs.pop("NumberOfSeizures", None)
        return "absences", attrs, "rewrite_absence_phrase_to_unknown_absences"
    if phrase == "focal to bilateral convulsive seizure" and _SF_FTB_GENERIC_LAST_EVENT_RE.search(
        evidence
    ):
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_ftb_last_event_to_seizure_free",
        )
    if phrase == "cluster of 3":
        attrs["CUI"] = "C3203523"
        attrs["CUIPhrase"] = "seizure cluster"
        return "seizure cluster", attrs, "rewrite_cluster_of_3_to_seizure_cluster"
    if _REWRITE_THESE_SEIZURES_RE.search(evidence) and attrs.get("CUI") == "C0270834":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_named_to_generic_seizures"
    if re.search(r"typical absences", evidence, re.IGNORECASE) and phrase == "absences":
        attrs["CUI"] = "C4316903"
        attrs["CUIPhrase"] = "typical absences"
        return "typical absences", attrs, "rewrite_absences_to_typical_absences"
    if _REWRITE_UP_TO_RANGE_RE.search(evidence) and attrs.get("CUI") == "C0877017":
        attrs["LowerNumberOfSeizures"] = "0"
        return text, attrs, "rewrite_up_to_range_lower_zero"
    if phrase == "seizures" and re.search(
        r"\bseizures every 3 to 4 weeks\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = "3"
        attrs["UpperNumberOfTimePeriods"] = "4"
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_3_to_4_weeks_timeperiod"
    if _SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE.search(evidence) and attrs.get("CUI") in {
        "C0877017",
        "C0270838",
    }:
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_focal_to_bilateral_last_event_to_seizure_free",
        )
    if attrs.get("CUI") == "C0494475" and _SF_UP_TO_SEIZURE_FREE_RE.search(evidence):
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimeSince_or_TimeOfEvent",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_up_to_seizure_free_to_unknown_state"
    if attrs.get("CUI") == "C0036572" and _SF_RECENT_LAST_SEIZURE_RE.search(evidence):
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return text, attrs, "rewrite_recent_last_seizure_to_seizure_free"
    if attrs.get("CUI") == "C0036572" and re.search(
        r"\bseizure[-\s]+free\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C1299590"
        attrs["CUIPhrase"] = "seizure-free"
        attrs["NumberOfSeizures"] = "0"
        return "seizure-free", attrs, "rewrite_generic_seizure_free_to_state_concept"
    if attrs.get("CUI") == "C0494475" and re.search(_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE, evidence):
        attrs["NumberOfSeizures"] = "1"
        attrs.pop("FrequencyChange", None)
        return text, attrs, "rewrite_gtcs_active_without_count_to_active_rate"
    if (
        attrs.get("CUI") == "C4316903"
        and phrase == "typical absences"
        and attrs.get("PointInTime") == "LastClinic"
        and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    ):
        attrs["FrequencyChange"] = "Same"
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_typical_absences_since_last_clinic_to_same"
    if re.search(r"\bfocal seizures\b.{0,80}\bunder control\b", evidence, re.IGNORECASE):
        attrs["CUI"] = "C0751495"
        attrs["CUIPhrase"] = "focal seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("FrequencyChange", None)
        return "focal seizures", attrs, "rewrite_focal_under_control_to_seizure_free"
    if phrase == "epileptic seizures" and re.search(
        r"\bwell controlled\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_epileptic_seizures_to_generic_seizures"
    if phrase == "further seizures" and re.search(
        r"\bnot\s+had\s+any\s+further\s+seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_no_further_seizures_to_generic_seizures"
    if attrs.get("CUI") == "C0036572" and re.search(_SF_NO_FURTHER_GTC_SINCE_RE, evidence):
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("MonthDate", None)
        attrs.pop("YearDate", None)
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_selected_no_further_gtc_to_named_seizure_free",
        )
    if phrase == "focal to bilateral convulsive seizures" and re.search(
        r"\blast\s+seizures\s+were\s+in\s+his\s+teenage\s+years\b",
        evidence,
        re.IGNORECASE,
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_teenage_last_seizures_to_generic"
    if phrase == "generalised tonic chronic seizures":
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_tonic_chronic_to_tonic_clonic_sf",
        )
    if phrase == "these seizures" and _REWRITE_THESE_SEIZURES_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_these_seizures_to_generic"
    if phrase == "absence seizures":
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        return "absences", attrs, "rewrite_absence_seizures_to_absences"
    return None


def _sf_operand_format_rewrite(
    text: str,
    *,
    surface: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    original = dict(attrs)
    rule_ids: list[str] = []

    if attrs.get("CUI") == "C0036572" and re.search(_SF_NO_FURTHER_GTC_SINCE_RE, surface):
        return None

    every_weeks = re.search(
        r"\bevery\s+(?P<weeks>\d+)\s+weeks?\b",
        surface,
        re.IGNORECASE,
    )
    if every_weeks is not None and not re.search(
        r"\bevery\s+\d+\s+to\s+\d+\s+weeks?\b",
        surface,
        re.IGNORECASE,
    ):
        attrs["NumberOfSeizures"] = attrs.get("NumberOfSeizures") or "1"
        attrs["NumberOfTimePeriods"] = every_weeks.group("weeks")
        attrs["TimePeriod"] = "Week"
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("rewrite_exact_every_weeks_operand_format")

    over_months = re.search(
        r"\b(?P<count>\d+)\s+seizures?\s+over\s+(?P<months>\d+)\s+months?\b",
        surface,
        re.IGNORECASE,
    )
    if over_months is not None:
        attrs["NumberOfSeizures"] = over_months.group("count")
        attrs["NumberOfTimePeriods"] = over_months.group("months")
        attrs["TimePeriod"] = "Month"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("rewrite_exact_count_over_months_operand_format")

    if re.search(r"\bper\s+month\b", surface, re.IGNORECASE) and attrs.get("MonthDate") == "1":
        attrs.pop("MonthDate", None)
        rule_ids.append("drop_per_month_spurious_month_date")

    if attrs.get("LowerNumberOfSeizures") == "0" and not attrs.get("UpperNumberOfSeizures"):
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("LowerNumberOfSeizures", None)
        rule_ids.append("collapse_lower_zero_to_exact_zero_count")

    if attrs.get("LowerNumberOfSeizures") and attrs.get("LowerNumberOfSeizures") == attrs.get(
        "UpperNumberOfSeizures"
    ):
        attrs["NumberOfSeizures"] = attrs["LowerNumberOfSeizures"]
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("collapse_equal_seizure_count_range")

    if attrs.get("LowerNumberOfTimePeriods") and attrs.get("LowerNumberOfTimePeriods") == attrs.get(
        "UpperNumberOfTimePeriods"
    ):
        attrs["NumberOfTimePeriods"] = attrs["LowerNumberOfTimePeriods"]
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("collapse_equal_time_period_range")

    if attrs == original:
        return None
    return text, attrs, "+".join(rule_ids)


__all__ = [
    "sf_convention_rewrite",
    "_sf_operand_format_rewrite",
]
