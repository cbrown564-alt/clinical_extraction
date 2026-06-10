"""Entity and attribute registry for the ExECTv2 extraction contract.

Derived from a one-shot profile of the 200-letter gold corpus (2026-06-09).
See docs/research/exectv2_gold_schema_profile_2026-06-09.md for the full
observed distribution.  Noise attributes are documented here rather than
silently inherited into validation.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntitySpec:
    """Schema for one of the nine ExECTv2 entities."""

    name: str
    legal_attributes: frozenset[str]
    closed_vocab: Mapping[str, frozenset[str]] = field(default_factory=dict)
    noise_attributes: frozenset[str] = field(default_factory=frozenset)


_SHARED_CUI_ATTRS: frozenset[str] = frozenset({"CUI", "CUIPhrase"})
_SHARED_CERTAINTY: frozenset[str] = frozenset({"Certainty"})
_SHARED_NEGATION: frozenset[str] = frozenset({"Negation"})

# Closed-vocabulary domains.
#
# Physical-unit, binary, and scale attributes are validated against their full
# legal domain — NOT merely the values that happen to occur in the 200-letter
# gold corpus.  The gate validates *predictions*, and a prediction may carry a
# correct-but-unseen value (e.g. MRI_Results="Unknown", Negation="Negated",
# Certainty="2" on an entity gold only ever showed at 4/5).  Restricting these
# to observed-gold values would mark such correct predictions invalid and turn
# the validity-rate metric into a measure of the gold's incidental value
# distribution.  Semantic categoricals (DiagCategory, FrequencyChange,
# DrugName, EEG_Type, PrematureBirth, PointInTime, ...) stay observed-only
# because their domains are genuinely enumerated by the annotation scheme.
_CERTAINTY_VOCAB: frozenset[str] = frozenset({"1", "2", "3", "4", "5"})
_NEGATION_VOCAB: frozenset[str] = frozenset({"Affirmed", "Negated"})
_PERFORMED_VOCAB: frozenset[str] = frozenset({"Yes", "No"})
_RESULTS_VOCAB: frozenset[str] = frozenset({"Normal", "Abnormal", "Unknown"})
_AGE_UNIT_VOCAB: frozenset[str] = frozenset({"Year", "Month"})
_TIME_PERIOD_VOCAB: frozenset[str] = frozenset({"Day", "Week", "Month", "Year"})

BIRTH_HISTORY = EntitySpec(
    name="BirthHistory",
    legal_attributes=frozenset({
        "PrematureBirth",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "PrematureBirth": frozenset({
            "32to<37_ModerateToLatePreterm",
            "34to<37_LatePreterm",
            "34to<37_LatePretermBirth",
            "37+_TermBirth",
        }),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
)

DIAGNOSIS = EntitySpec(
    name="Diagnosis",
    legal_attributes=frozenset({
        "DiagCategory",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        # EA0138 uses lowercase 'epilepsy' — annotation inconsistency, both accepted.
        "DiagCategory": frozenset({"Epilepsy", "epilepsy", "MultipleSeizures", "SingleSeizure"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
)

EPILEPSY_CAUSE = EntitySpec(
    name="EpilepsyCause",
    legal_attributes=frozenset({
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
)

INVESTIGATIONS = EntitySpec(
    name="Investigations",
    legal_attributes=frozenset({
        "MRI_Performed", "MRI_Results",
        "CT_Performed", "CT_Results",
        "EEG_Performed", "EEG_Results", "EEG_Type",
        *_SHARED_CUI_ATTRS,
    }),
    closed_vocab={
        "MRI_Performed": _PERFORMED_VOCAB,
        "MRI_Results": _RESULTS_VOCAB,
        "CT_Performed": _PERFORMED_VOCAB,
        "CT_Results": _RESULTS_VOCAB,
        "EEG_Performed": _PERFORMED_VOCAB,
        "EEG_Results": _RESULTS_VOCAB,
        "EEG_Type": frozenset({"Standard", "SleepDeprived", "VideoTelemetry"}),
    },
)

ONSET = EntitySpec(
    name="Onset",
    legal_attributes=frozenset({
        "Age", "AgeLower", "AgeUpper", "AgeUnit",
        "NumberOfTimePeriods", "TimePeriod",
        "PointInTime",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "AgeUnit": _AGE_UNIT_VOCAB,
        "TimePeriod": _TIME_PERIOD_VOCAB,
        "PointInTime": frozenset({"From_Birth"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
)

PATIENT_HISTORY = EntitySpec(
    name="PatientHistory",
    legal_attributes=frozenset({
        "Age", "AgeLower", "AgeUpper", "AgeUnit",
        "DayDate", "MonthDate", "YearDate",
        "NumberOfTimePeriods", "TimePeriod",
        "PointInTime",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "AgeUnit": _AGE_UNIT_VOCAB,
        "TimePeriod": _TIME_PERIOD_VOCAB,
        "PointInTime": frozenset({"Last_Year", "Surgery"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
    # C0151744 appears on one mention — likely a CUI key mistakenly used as an
    # attribute name; treat as noise.
    noise_attributes=frozenset({"C0151744"}),
)

PRESCRIPTION = EntitySpec(
    name="Prescription",
    legal_attributes=frozenset({
        "DrugName", "DrugDose", "DoseUnit", "Frequency",
        *_SHARED_CUI_ATTRS,
    }),
    closed_vocab={
        "DoseUnit": frozenset({"mg", "g"}),
        "Frequency": frozenset({"1", "2", "3", "As_Required"}),
    },
)

SEIZURE_FREQUENCY = EntitySpec(
    name="SeizureFrequency",
    legal_attributes=frozenset({
        "NumberOfSeizures",
        "LowerNumberOfSeizures", "UpperNumberOfSeizures",
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods", "UpperNumberOfTimePeriods",
        "TimePeriod",
        "TimeSince_or_TimeOfEvent",
        "FrequencyChange",
        "PointInTime",
        "DayDate", "MonthDate", "YearDate",
        "AgeLower", "AgeUpper", "AgeUnit",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "TimeSince_or_TimeOfEvent": frozenset({"During", "Since"}),
        "FrequencyChange": frozenset({"Decreased", "Frequent", "Increased", "Infrequent", "Same"}),
        # "days" appears once — annotation noise (plural form of "Day"); kept as a
        # legal value so gold validates clean (see noise summary in the profile).
        "TimePeriod": _TIME_PERIOD_VOCAB | frozenset({"days"}),
        "PointInTime": frozenset({
            "Birthday", "DrugChange", "LastClinic",
            "Last_Month", "Last_Week", "Last_Year", "Surgery",
        }),
        "AgeUnit": _AGE_UNIT_VOCAB,
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
    # DiagCategory appears on two SF mentions — annotation noise from the Diagnosis
    # entity schema.  Documented here, not validated.
    noise_attributes=frozenset({"DiagCategory"}),
)

WHEN_DIAGNOSED = EntitySpec(
    name="WhenDiagnosed",
    legal_attributes=frozenset({
        "Age", "AgeUnit",
        "MonthDate", "YearDate",
        "NumberOfTimePeriods", "TimePeriod",
        *_SHARED_CUI_ATTRS,
        *_SHARED_CERTAINTY,
        *_SHARED_NEGATION,
    }),
    closed_vocab={
        "AgeUnit": _AGE_UNIT_VOCAB,
        "TimePeriod": _TIME_PERIOD_VOCAB,
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": _NEGATION_VOCAB,
    },
)

ALL_ENTITIES: tuple[EntitySpec, ...] = (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)

ENTITY_REGISTRY: dict[str, EntitySpec] = {spec.name: spec for spec in ALL_ENTITIES}
