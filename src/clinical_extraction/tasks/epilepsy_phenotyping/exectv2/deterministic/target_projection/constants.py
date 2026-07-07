"""Regex constants for target-indicator projection and evidence repair.

``EVERY_N_TO_M_PERIODS`` is re-exported from ``sf_surface_registry.patterns``
(canonical owner since P1-1 Phase 1). Quarantine metadata lives in
``sf_surface_registry/catalog/projection_sf.yaml``; ``policy.py`` reads the catalog.
"""
# ruff: noqa: F401 — re-exports ``EVERY_N_TO_M_PERIODS`` imported by other modules.

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    EVERY_N_TO_M_PERIODS,
)

from .policy import (
    QUARANTINED_TARGET_PROJECTION_FAMILIES,
    TARGET_PROJECTION_AUDIT_REPLAY_SWITCHES,
)

DIAGNOSIS_ALLOWED_CORE = re.compile(
    r"\b(epilep\w*|seizures?|jme|absence|absences|myoclonic|tonic|clonic|"
    r"convulsive|partial|focal|generalised|generalized|status|grand mal)\b",
    re.IGNORECASE,
)
DIAGNOSIS_PROHIBITED_CORES = frozenset(
    {
        "seizure",
        "seizures",
        "febrile seizure",
        "febrile seizures",
        "dissociative seizure",
        "dissociative seizures",
        "non epileptic seizure",
        "non epileptic seizures",
        "psychogenic seizure",
        "psychogenic seizures",
        "myoclonic jerk",
        "myoclonic jerks",
        "absence like seizure",
        "absence like seizures",
    }
)
PLANNED_PRESCRIPTION_CONTEXT = re.compile(
    r"\b(?:to start|starts?|suggest(?:ed|s|ing)? adding|would suggest|"
    r"plan(?:ned)? to start|if attacks recur|target dose)\b",
    re.IGNORECASE,
)
PLANNED_INVESTIGATION_CONTEXT = re.compile(
    r"\b(?:will arrange|will request|i will request|to arrange|to request|"
    r"arranging|requesting|further tests including|await(?:ing)?|planned|useful to get)\b",
    re.IGNORECASE,
)
ASYMMETRIC_DOSING = re.compile(
    r"(?P<first>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b(?:mane|morning|am)\b"
    r".{0,80}?(?P<second>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b"
    r"(?:nocte|night|pm|afternoon|evening)\b",
    re.IGNORECASE | re.DOTALL,
)
SEIZURE_FREQUENCY_ANCHOR = re.compile(
    r"\b(seizures?|attacks?|episodes?|convulsions?|absences?|jerks?|myoclon(?:ic|us)|"
    r"tonic|clonic|focal|generalised|generalized|partial)\b",
    re.IGNORECASE,
)
SEIZURE_FREQUENCY_PROHIBITED_ANCHOR = re.compile(
    r"\b(?:febrile|dissociative|non.?epileptic|psychogenic)\s+"
    r"(?:seizures?|convulsions?|events?)\b",
    re.IGNORECASE,
)
REMOTE_LAST_SEIZURES_IN_TEENS = re.compile(
    r"\blast\s+seizures?\s+were\s+in\s+(?:(?:his|her|their)\s+)?teenage\s+years\b",
    re.IGNORECASE,
)
VAGUE_YEARLY_SEIZURE_RATE = re.compile(
    r"\b(?:a\s+)?(?:few|couple|several)\s+\w*seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
GENERIC_YEARLY_SEIZURE_RATE = re.compile(
    r"\b(?:roughly|about|around|approximately)\s+two\s+seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
YEAR_IN_TEXT = re.compile(r"\b(?P<year>19\d{2}|20\d{2})\b")
LAST_EVENT_MONTH_YEAR = re.compile(
    r"\blast\s+(?:event|seizure)\s+"
    r"(?P<month>january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\s+(?P<year>19\d{2}|20\d{2})\b",
    re.IGNORECASE,
)
SEVERAL_SINCE_LAST_CLINIC = re.compile(
    r"\bseveral\s+seizures?\s+since\s+(?:the\s+)?last\s+clinic(?:\s+appointment)?\b",
    re.IGNORECASE,
)
EVERY_N_PERIODS = re.compile(
    r"\bevery\s+(?P<n>\d+)\s+(?P<period>days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)
CONTROLLED_ON_DOSE = re.compile(
    r"\b(?:completely\s+)?under\s+control\s+on\s+the\s+dose\b",
    re.IGNORECASE,
)
CLUSTER_OF_SEIZURES = re.compile(r"\bcluster\s+of\s+seizures\b", re.IGNORECASE)
INFREQUENT_DIAGNOSIS_YEAR = re.compile(
    r"\binfrequent\b.+\byear\s+of\s+(?:his|her|the)\s+diagnosis\b",
    re.IGNORECASE | re.DOTALL,
)
GENERALIZED_EPILEPSY_GTCS_ALONE = re.compile(
    r"\bepilepsy\s+with\s+general(?:ised|ized)\s+tonic\s+(?:clonic|chronic)\s+"
    r"seizures?\s+alone\b",
    re.IGNORECASE,
)
SPECIFIC_SEIZURE_EVIDENCE = re.compile(
    r"\b(seizures?|convulsions?|absences?|focal|tonic|clonic|partial|myoclonic)\b",
    re.IGNORECASE,
)
UNKNOWN_LIKE_NUMBER = frozenset({"unknown", "unclear"})
SF_STATE_ATTRIBUTES = frozenset(
    {
        "AgeLower",
        "AgeUnit",
        "AgeUpper",
        "DayDate",
        "FrequencyChange",
        "LowerNumberOfSeizures",
        "LowerNumberOfTimePeriods",
        "MonthDate",
        "NumberOfSeizures",
        "NumberOfTimePeriods",
        "PointInTime",
        "TimePeriod",
        "TimeSince_or_TimeOfEvent",
        "UpperNumberOfSeizures",
        "UpperNumberOfTimePeriods",
        "YearDate",
    }
)
SF_TEXT_ALIASES = {
    "absence like seizure": "absence like seizures",
    "absence like seizures": "absence like seizures",
    "focal seizures without change in awareness": "focal seizures",
}
MONTH_TO_NUMBER = {
    "january": "1",
    "february": "2",
    "march": "3",
    "april": "4",
    "may": "5",
    "june": "6",
    "july": "7",
    "august": "8",
    "september": "9",
    "october": "10",
    "november": "11",
    "december": "12",
}
