"""Module-level constants for the ExECTv2 target-indicators single-call path.

Pure relocation of the constant/regex/frozenset definitions from
``llm_target_indicators_single_call``. No logic, regex, or value changes.
"""

from __future__ import annotations

import re
from typing import Literal

PROMPT_VERSION = "exectv2_target_indicators_single_call_v0.42"
PIPELINE_FAMILY = "exectv2_target_indicators_single_call"
COMPONENT_OWNER = "llm_single_call_target_indicators"
_DIAGNOSIS_ALLOWED_CORE = re.compile(
    r"\b(epilep\w*|seizures?|jme|absence|absences|myoclonic|tonic|clonic|"
    r"convulsive|partial|focal|generalised|generalized|status|grand mal)\b",
    re.IGNORECASE,
)
_DIAGNOSIS_PROHIBITED_CORES = frozenset(
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
_PLANNED_PRESCRIPTION_CONTEXT = re.compile(
    r"\b(?:to start|starts?|suggest(?:ed|s|ing)? adding|would suggest|"
    r"plan(?:ned)? to start|if attacks recur|target dose)\b",
    re.IGNORECASE,
)
_PLANNED_INVESTIGATION_CONTEXT = re.compile(
    r"\b(?:will arrange|will request|i will request|to arrange|to request|"
    r"arranging|requesting|further tests including|await(?:ing)?|planned|useful to get)\b",
    re.IGNORECASE,
)
_SEIZURE_FREQUENCY_ANCHOR = re.compile(
    r"\b(seizures?|attacks?|episodes?|convulsions?|absences?|jerks?|myoclon(?:ic|us)|"
    r"tonic|clonic|focal|generalised|generalized|partial)\b",
    re.IGNORECASE,
)
_SEIZURE_FREQUENCY_PROHIBITED_ANCHOR = re.compile(
    r"\b(?:febrile|dissociative|non.?epileptic|psychogenic)\s+"
    r"(?:seizures?|convulsions?|events?)\b",
    re.IGNORECASE,
)
_CLUSTER_OF_SEIZURES = re.compile(r"\bcluster\s+of\s+seizures\b", re.IGNORECASE)
_GENERALIZED_EPILEPSY_GTCS_ALONE = re.compile(
    r"\bepilepsy\s+with\s+general(?:ised|ized)\s+tonic\s+(?:clonic|chronic)\s+"
    r"seizures?\s+alone\b",
    re.IGNORECASE,
)
_SPECIFIC_SEIZURE_EVIDENCE = re.compile(
    r"\b(seizures?|convulsions?|absences?|focal|tonic|clonic|partial|myoclonic)\b",
    re.IGNORECASE,
)
_UNKNOWN_LIKE_NUMBER = frozenset({"unknown", "unclear"})
_SF_STATE_ATTRIBUTES = frozenset(
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
_SF_TEXT_ALIASES = {
    "absence like seizure": "absence like seizures",
    "absence like seizures": "absence like seizures",
    "focal seizures without change in awareness": "focal seizures",
}

Mode = Literal["live", "prompt-only"]
