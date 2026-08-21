"""Standard names and closed detail values for later-stage ExECT encode and select.

Lives off the same phrase tables as projection. No letter text. No research metadata.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    _DIAGNOSIS_ENTRIES,
    _PRESCRIPTION_ENTRIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    DRUG_SURFACE_ALIASES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    SF_CUI_LEXICON,
)

STANDARD_NAME_RULES = [
    "Write one standard name from the list for that clinical family.",
    "If the clinical name is already a listed also-word, write that row's standard name.",
    "Do not copy a count, dose, or date into the standard name.",
    (
        "When a detail field has a listed set of values, write one of those "
        "values. Leave other detail fields as the words already on the row."
    ),
]


def _name_item(head: str, also: list[str]) -> dict[str, Any]:
    row: dict[str, Any] = {"standard_name": head}
    if also:
        row["also"] = also
    return row


def _name_rows(entries: tuple[tuple[Any, tuple[str, ...]], ...]) -> list[dict[str, Any]]:
    rows = []
    for _concept, variants in entries:
        head, *also = variants
        rows.append(_name_item(head.replace("-", " "), list(also)))
    return rows


def _medicine_rows() -> list[dict[str, Any]]:
    also_by_head: dict[str, set[str]] = defaultdict(set)
    for alias, generic in DRUG_SURFACE_ALIASES.items():
        if alias != generic:
            also_by_head[generic].add(alias)
    for _concept, variants in _PRESCRIPTION_ENTRIES:
        for variant in variants:
            generic = DRUG_SURFACE_ALIASES.get(
                normalize_phrase(variant),
                variant.replace("-", " "),
            )
            also_by_head.setdefault(generic, set())
            if normalize_phrase(variant) != normalize_phrase(generic):
                also_by_head[generic].add(variant)
    heads = sorted(also_by_head)
    return [_name_item(head, sorted(also_by_head[head])) for head in heads]


# CUI lookup keeps truncation and state strings. The prompt only lists type names.
_PROMPT_DROP_ALSO = frozenset(
    {
        "no further seizures",
        "generalised",
        "focal",
        "complex",
        "dyscognitive",
        "generalised tonic chronic seizures",
        "generalized tonic chronic seizures",
    }
)


def _seizure_type_rows() -> list[dict[str, Any]]:
    specific: list[dict[str, Any]] = []
    generic: dict[str, Any] | None = None
    for phrases in SF_CUI_LEXICON.values():
        head, *also = phrases
        row = _name_item(
            head,
            [item for item in also if item not in _PROMPT_DROP_ALSO],
        )
        if head == "seizures":
            generic = row
        else:
            specific.append(row)
    if generic is not None:
        specific.append(generic)
    return specific


def standard_names_payload() -> dict[str, Any]:
    """Model-facing name and detail-value block shared by encode and select."""

    return {
        "rules": list(STANDARD_NAME_RULES),
        "diagnosis": _name_rows(_DIAGNOSIS_ENTRIES),
        "seizure_types": _seizure_type_rows(),
        "medicines": _medicine_rows(),
        "tests": [
            _name_item("MRI", ["mri"]),
            _name_item("CT", ["ct"]),
            _name_item("EEG", ["eeg"]),
        ],
        "details": {
            "Diagnosis": {
                "category": ["Epilepsy", "MultipleSeizures", "SingleSeizure"],
            },
            "SeizureFrequency": {
                "period": ["Day", "Week", "Month", "Year"],
                "since_or_during": ["During", "Since"],
                "change": [
                    "Decreased",
                    "Frequent",
                    "Increased",
                    "Infrequent",
                    "Same",
                ],
                "point_in_time": [
                    "Birthday",
                    "DrugChange",
                    "LastClinic",
                    "Last_Month",
                    "Last_Week",
                    "Last_Year",
                    "Surgery",
                ],
                "age_unit": ["Year", "Month"],
            },
            "Prescription": {
                "dose": "number already on the row",
                "unit": ["mg", "g"],
                "schedule": ["1", "2", "3", "As_Required"],
            },
            "Investigations": {
                "performed": ["Yes", "No"],
                "result": ["Normal", "Abnormal", "Unknown"],
                "eeg_type": ["Standard", "SleepDeprived", "VideoTelemetry"],
            },
        },
    }
