"""Gold-defined within-family categories for ExECT development analysis.

These categories describe the clinical fact a mention asks the extractor to
recover. They do not change the ExECT contract or clinical-headline scorers.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")

PRIMARY_SUBTYPE_ORDER: dict[str, tuple[str, ...]] = {
    "Diagnosis": ("epilepsy", "multiple_seizures", "single_seizure"),
    "SeizureFrequency": (
        "seizure_free",
        "numeric_cadence_rate",
        "count_in_named_window",
        "qualitative_frequency_change",
        "numeric_plus_frequency_change",
        "count_without_cadence_or_anchor",
        "temporal_anchor_without_count",
        "sparse_or_other",
    ),
    "Prescription": (
        "complete_regimen",
        "rescue_as_required",
        "incomplete_or_partial",
    ),
    "Investigations": (
        "eeg_normal",
        "eeg_abnormal",
        "eeg_unknown_or_unstated",
        "mri_normal",
        "mri_abnormal",
        "mri_unknown_or_unstated",
        "ct_normal",
        "ct_abnormal",
        "ct_unknown_or_unstated",
    ),
}

_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(value: Any) -> str:
    text = _CAMEL_BOUNDARY.sub("_", str(value or "").strip())
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "missing_or_other"


def _attributes(mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in (mention.get("attributes") or {}).items()
        if value is not None
    }


def _sf_subtype(attributes: Mapping[str, str]) -> str:
    count_values = [
        attributes.get(key)
        for key in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
        if key in attributes
    ]
    has_count = bool(count_values)
    has_cadence = "TimePeriod" in attributes or any(
        "TimePeriod" in key for key in attributes
    )
    has_change = "FrequencyChange" in attributes
    has_anchor = any(
        key in attributes
        for key in (
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
            "YearDate",
            "MonthDate",
            "DayDate",
        )
    )
    if has_count and all(value in {"", "0"} for value in count_values):
        return "seizure_free"
    if has_count and has_cadence:
        return "numeric_cadence_rate"
    if has_count and has_anchor:
        return "count_in_named_window"
    if has_count and has_change:
        return "numeric_plus_frequency_change"
    if has_change:
        return "qualitative_frequency_change"
    if has_count:
        return "count_without_cadence_or_anchor"
    if has_anchor:
        return "temporal_anchor_without_count"
    return "sparse_or_other"


def family_subtypes(mention: Mapping[str, Any]) -> tuple[str, ...]:
    """Return deterministic subtype labels for one saved ExECT mention."""

    family = str(mention.get("entity") or "")
    attributes = _attributes(mention)
    if family == "Diagnosis":
        return (_snake(attributes.get("DiagCategory")),)
    if family == "SeizureFrequency":
        return (_sf_subtype(attributes),)
    if family == "Prescription":
        frequency = _snake(attributes.get("Frequency"))
        if frequency == "as_required":
            return ("rescue_as_required",)
        has_drug = bool(attributes.get("DrugName") or mention.get("text"))
        if all(
            (
                has_drug,
                attributes.get("DrugDose"),
                attributes.get("DoseUnit"),
                attributes.get("Frequency"),
            )
        ):
            return ("complete_regimen",)
        return ("incomplete_or_partial",)
    if family == "Investigations":
        subtypes: list[str] = []
        for modality in ("EEG", "MRI", "CT"):
            performed = attributes.get(f"{modality}_Performed")
            result = attributes.get(f"{modality}_Results")
            eeg_type = attributes.get("EEG_Type") if modality == "EEG" else None
            if not any((performed, result, eeg_type)):
                continue
            state = _snake(result) if result else "unknown_or_unstated"
            if state == "unknown":
                state = "unknown_or_unstated"
            subtypes.append(f"{modality.lower()}_{state}")
        return tuple(subtypes) or ("missing_or_other",)
    raise ValueError(f"Unsupported ExECT family: {family!r}")


def _project_investigation(
    mention: Mapping[str, Any], subtype: str
) -> dict[str, Any]:
    modality = subtype.split("_", 1)[0].upper()
    keep = {f"{modality}_Performed", f"{modality}_Results"}
    if modality == "EEG":
        keep.add("EEG_Type")
    projected = dict(mention)
    projected["attributes"] = {
        key: value
        for key, value in _attributes(mention).items()
        if key in keep
    }
    return projected


def mentions_for_subtype(
    mentions: Iterable[Mapping[str, Any]], family: str, subtype: str
) -> list[dict[str, Any]]:
    """Filter mentions to one family subtype without leaking sibling units."""

    selected: list[dict[str, Any]] = []
    for mention in mentions:
        if str(mention.get("entity") or "") != family:
            continue
        if subtype not in family_subtypes(mention):
            continue
        if family == "Investigations":
            selected.append(_project_investigation(mention, subtype))
        else:
            selected.append(dict(mention))
    return selected


def observed_gold_subtypes(
    rows: Iterable[Mapping[str, Any]], family: str
) -> tuple[str, ...]:
    """Return observed gold subtypes in stable, clinically readable order."""

    observed = {
        subtype
        for row in rows
        for mention in row.get("gold_mentions", [])
        if str(mention.get("entity") or "") == family
        for subtype in family_subtypes(mention)
    }
    preferred = PRIMARY_SUBTYPE_ORDER[family]
    return tuple(
        [subtype for subtype in preferred if subtype in observed]
        + sorted(observed - set(preferred))
    )
