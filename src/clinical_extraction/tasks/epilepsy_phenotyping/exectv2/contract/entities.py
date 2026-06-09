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

_NEGATION_VOCAB: frozenset[str] = frozenset({"Affirmed", "Negated"})
_CERTAINTY_VOCAB: frozenset[str] = frozenset({"1", "2", "3", "4", "5"})

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
        "Negation": frozenset({"Affirmed"}),
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
        "Negation": frozenset({"Affirmed"}),
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
        "Negation": frozenset({"Affirmed"}),
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
        "MRI_Performed": frozenset({"Yes"}),
        "MRI_Results": frozenset({"Normal", "Abnormal"}),
        "CT_Performed": frozenset({"Yes"}),
        "CT_Results": frozenset({"Normal", "Abnormal", "Unknown"}),
        "EEG_Performed": frozenset({"Yes"}),
        "EEG_Results": frozenset({"Normal", "Abnormal", "Unknown"}),
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
        "AgeUnit": frozenset({"Year", "Month"}),
        "TimePeriod": frozenset({"Year", "Month", "Week", "Day"}),
        "PointInTime": frozenset({"From_Birth"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": frozenset({"Affirmed"}),
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
        "AgeUnit": frozenset({"Year", "Month"}),
        "TimePeriod": frozenset({"Year", "Month", "Week", "Day"}),
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
        # "days" appears once (annotation noise for "Day"); accept both to avoid
        # spurious validation errors on gold itself.
        "TimePeriod": frozenset({"Day", "Week", "Month", "Year", "days"}),
        "PointInTime": frozenset({
            "Birthday", "DrugChange", "LastClinic",
            "Last_Month", "Last_Week", "Last_Year", "Surgery",
        }),
        "AgeUnit": frozenset({"Year", "Month"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": frozenset({"Affirmed"}),
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
        "AgeUnit": frozenset({"Year", "Month"}),
        "TimePeriod": frozenset({"Year", "Month"}),
        "Certainty": _CERTAINTY_VOCAB,
        "Negation": frozenset({"Affirmed"}),
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
