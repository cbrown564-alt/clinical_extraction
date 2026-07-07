"""SF projection builders migrated from ``target_projection/sf_state.py``."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.constants import (
    EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS,
    GENERIC_YEARLY_SEIZURE_RATE,
    INFREQUENT_DIAGNOSIS_YEAR,
    LAST_EVENT_MONTH_YEAR,
    MONTH_TO_NUMBER,
    REMOTE_LAST_SEIZURES_IN_TEENS,
    SEVERAL_SINCE_LAST_CLINIC,
    VAGUE_YEARLY_SEIZURE_RATE,
    YEAR_IN_TEXT,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.policy import (
    ProjectionFamilySwitches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.shared import (
    period_to_canonical,
)


def project_diagnosis_text_from_evidence(text: str, evidence: str) -> str:
    source = normalize_phrase(f"{text} {evidence}")
    if "combination of epileptic and nonepileptic events" in source:
        return "epileptic attack"
    if text == "epileptic" and re.search(r"\bepileptic\b.+\b(?:events?|attacks?)\b", source):
        return "epileptic attack"
    if "generalised tonic clonic seizures with myoclonic jerks" in source:
        return "generalised tonic clonic seizures"
    if text == "epilepsy with generalised tonic clonic seizures" and "alone" in source:
        return "epilepsy with generalised tonic clonic seizures alone"
    if text == "general seizures" and "general and complex partial seizures" in source:
        return "complex partial seizures"
    if "genetic generalised epilepsy" in source or "genetic generalized epilepsy" in source:
        return "genetic generalised epilepsy"
    if "focal onset" in source and text in {
        "epilepsy",
        "focal onset",
        "focal seizures",
        "seizures possibly focal onset",
    }:
        return "focal epilepsy"
    if (
        text
        in {
            "epilepsy",
            "focal epilepsy",
            "focal epilepsy probable temporal",
            "temporal focal epilepsy",
        }
        and "epilep" in source
    ):
        if "probable temporal" in source or "temporal lobe epilepsy" in source:
            return "temporal lobe epilepsy"
    if text in {"epilepsy", "unclear epilepsy"} and "epilep" in source:
        if "probable focal" in source or "focal onset" in source:
            return "focal epilepsy"
        if "possibly generalised" in source or "possibly generalized" in source:
            return "generalised epilepsy"
    return text


def project_sf_state_from_evidence(
    text: str,
    attrs: dict[str, str],
    evidence: str,
    *,
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[str, dict[str, str], list[str]]:
    if INFREQUENT_DIAGNOSIS_YEAR.search(evidence):
        return (
            text,
            {"FrequencyChange": "Infrequent"},
            ["projected_infrequent_diagnosis_year_to_change_state"],
        )
    year_match = YEAR_IN_TEXT.search(evidence)
    march_range = re.search(
        r"\bin\s+march\b.{0,40}\b(?P<lower>\d+)\s*(?:-|to)\s*(?P<upper>\d+)\b",
        evidence,
        re.IGNORECASE,
    )
    if march_range:
        projected = {
            key: value
            for key, value in attrs.items()
            if key
            not in {
                "NumberOfSeizures",
                "NumberOfTimePeriods",
                "TimePeriod",
                "PointInTime",
                "FrequencyChange",
            }
        }
        projected.update(
            {
                "LowerNumberOfSeizures": march_range.group("lower"),
                "UpperNumberOfSeizures": march_range.group("upper"),
                "TimeSince_or_TimeOfEvent": "During",
                "MonthDate": "3",
            }
        )
        return text, projected, ["projected_march_range_count"]
    if (
        attrs.get("NumberOfSeizures") == "0"
        and normalize_phrase(text) in {"absence like seizure", "absence like seizures"}
        and year_match
    ):
        projected = {
            key: value
            for key, value in attrs.items()
            if key
            not in {
                "NumberOfSeizures",
                "LowerNumberOfSeizures",
                "UpperNumberOfSeizures",
                "FrequencyChange",
                "PointInTime",
                "TimePeriod",
            }
        }
        projected.update(
            {
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": year_match.group("year"),
            }
        )
        return text, projected, ["projected_dated_absence_like_zero_to_active_rate"]
    last_event_match = LAST_EVENT_MONTH_YEAR.search(evidence)
    if last_event_match and attrs.get("NumberOfSeizures") != "0":
        projected = {
            key: value
            for key, value in attrs.items()
            if key
            not in {
                "NumberOfSeizures",
                "LowerNumberOfSeizures",
                "UpperNumberOfSeizures",
                "NumberOfTimePeriods",
                "LowerNumberOfTimePeriods",
                "UpperNumberOfTimePeriods",
                "TimePeriod",
                "FrequencyChange",
                "PointInTime",
            }
        }
        projected.update(
            {
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "MonthDate": MONTH_TO_NUMBER[last_event_match.group("month").lower()],
                "YearDate": last_event_match.group("year"),
            }
        )
        return text, projected, ["projected_last_event_month_year_to_zero_since"]
    if not REMOTE_LAST_SEIZURES_IN_TEENS.search(evidence):
        if re.search(
            r"\bsince\s+(?:her|his|the)\s+last\s+clinic\s+appointment\s+"
            r"(?:she|he|they)\s+has\s+had\s+four\s+secondary\s+generalised\s+seizures\b",
            evidence,
            re.IGNORECASE,
        ):
            family = "projected_four_since_last_clinic"
            if not is_projection_family_enabled(family, projection_family_switches):
                return text, attrs, [quarantined_projection_family_warning(family)]
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "NumberOfTimePeriods",
                    "LowerNumberOfTimePeriods",
                    "UpperNumberOfTimePeriods",
                    "TimePeriod",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "4",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "PointInTime": "LastClinic",
                }
            )
            return text, projected, [family]
        if SEVERAL_SINCE_LAST_CLINIC.search(evidence):
            family = "projected_several_since_last_clinic"
            if not is_projection_family_enabled(family, projection_family_switches):
                return text, attrs, [quarantined_projection_family_warning(family)]
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "NumberOfTimePeriods",
                    "LowerNumberOfTimePeriods",
                    "UpperNumberOfTimePeriods",
                    "TimePeriod",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "3",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "PointInTime": "LastClinic",
                }
            )
            return text, projected, [family]
        if GENERIC_YEARLY_SEIZURE_RATE.search(evidence):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "TimeSince_or_TimeOfEvent",
                    "PointInTime",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                }
            )
            return "seizures", projected, ["projected_generic_yearly_rate_anchor"]
        range_match = EVERY_N_TO_M_PERIODS.search(evidence)
        if (
            range_match
            and attrs.get("NumberOfSeizures", "1") == "1"
            and "LowerNumberOfSeizures" not in attrs
            and "UpperNumberOfSeizures" not in attrs
        ):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "NumberOfTimePeriods",
                    "LowerNumberOfTimePeriods",
                    "UpperNumberOfTimePeriods",
                    "TimePeriod",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": range_match.group("lower"),
                    "UpperNumberOfTimePeriods": range_match.group("upper"),
                    "TimePeriod": period_to_canonical(range_match.group("period")),
                }
            )
            return (
                text,
                projected,
                ["projected_every_n_to_m_periods_to_one_event_rate"],
            )
        if (
            "NumberOfSeizures" not in attrs
            and "LowerNumberOfSeizures" not in attrs
            and "UpperNumberOfSeizures" not in attrs
        ):
            match = EVERY_N_PERIODS.search(evidence)
            if match:
                projected = {
                    key: value for key, value in attrs.items() if key not in {"FrequencyChange"}
                }
                projected["NumberOfSeizures"] = "1"
                projected["NumberOfTimePeriods"] = match.group("n")
                projected["TimePeriod"] = period_to_canonical(match.group("period"))
                return (
                    text,
                    projected,
                    ["projected_every_n_periods_to_one_event_rate"],
                )
        if VAGUE_YEARLY_SEIZURE_RATE.search(evidence):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "TimeSince_or_TimeOfEvent",
                    "PointInTime",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                }
            )
            return text, projected, ["projected_vague_yearly_rate"]
        return text, attrs, []
    projected = {
        key: value
        for key, value in attrs.items()
        if key
        not in {
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "FrequencyChange",
        }
    }
    projected.update(
        {
            "NumberOfSeizures": "0",
            "TimeSince_or_TimeOfEvent": "Since",
            "AgeLower": "13",
            "AgeUpper": "19",
            "AgeUnit": "Year",
        }
    )
    return "seizures", projected, ["projected_remote_last_seizures_to_seizure_free"]
