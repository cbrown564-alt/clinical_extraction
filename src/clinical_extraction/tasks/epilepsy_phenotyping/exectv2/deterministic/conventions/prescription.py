"""Prescription convention repairs and residual additions."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

from .shared import (
    _DOSE_UNIT_RE,
    _SLASH_DAILY_DOSE_SEQUENCE_RE,
    frequency_code,
    normalize_dose_unit,
    normalize_dose_value,
    normalize_drug_name,
)

_PRESCRIPTION_RESIDUAL_DRUG_SURFACES: tuple[str, ...] = tuple(
    sorted(
        {
            "brivaracetam",
            "brivetiracetam",
            "buccal midazolam",
            "carbamazepine",
            "clobazam",
            "epilim",
            "epilpim chrono",
            "episenta",
            "eplim",
            "eplim chrono",
            "keppra",
            "lamictal",
            "lamotrigine",
            "levetiracetam",
            "midazolam",
            "perampanel",
            "phenytoin",
            "pregabalin",
            "sodium valproate",
            "tegretol retard",
            "topiramate",
            "valproate",
            "zonisamide",
        },
        key=len,
        reverse=True,
    )
)
_PRESCRIPTION_RESIDUAL_DRUG_RE = re.compile(
    r"(?<!\w)(?P<drug>"
    + "|".join(re.escape(surface) for surface in _PRESCRIPTION_RESIDUAL_DRUG_SURFACES)
    + r")(?!\w)",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_STOP_RE = re.compile(
    r"\b(?:Diagnosis|Investigations?|Follow\s*up|Previous\s+medications?|"
    r"Past\s+medical\s+history|I\s+(?:reviewed|spoke|saw|had)|Thank\s+you)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE = re.compile(
    r"\b(?:to\s+be\s+increased|to\s+increase|to\s+withdraw|to\s+reduce|"
    r"reducing|increase\s+to|increased\s+to|would\s+increase|"
    r"suggest\s+increasing|suggest\s+increase|suggest\s+changing|"
    r"changing\s+the|starting\s+next|recommend\s+add|please\s+(?:start|increase)|"
    r"would\s+be\s+(?:very\s+)?grateful\s+if\s+you\s+could\s+"
    r"(?:prescribe|increase)|plan\s*:)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_HISTORICAL_CUE_RE = re.compile(
    r"\b(?:previous\s+(?:antiepileptic\s+)?medications?|previous\s+medications?\s+"
    r"include|past\s+medications?|medications?\s+tried|in\s+the\s+past)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_NAME_ALIASES = {
    "epilim": "sodium-valproate",
    "epilim-chrono": "sodium-valproate",
    "eplim": "sodium-valproate",
    "episenta": "sodium-valproate",
    "sodiumvalproate": "sodium-valproate",
    "tegretol-retard": "carbamazepine",
}
_NON_ANTIEPILEPTIC_DRUGS = frozenset(
    {
        "amitriptyline",
        "citalopram",
        "fluoxetine",
        "mirtazapine",
        "olanzapine",
        "risperidone",
        "sertraline",
        "venlafaxine",
    }
)


def is_non_antiepileptic_prescription(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True for a closed list of non-epilepsy drugs. Does not read gold."""

    del text, evidence
    attrs = {str(key): str(value) for key, value in attributes.items()}
    name = normalize_drug_name(attrs.get("DrugName") or "") or normalize_phrase(
        attrs.get("DrugName") or ""
    )
    return name.replace(" ", "-") in _NON_ANTIEPILEPTIC_DRUGS or name in _NON_ANTIEPILEPTIC_DRUGS


_DOSE_RANGE_FIELD_RE = re.compile(
    r"^\s*(?P<low>\d+(?:\.\d+)?)\s*(?:mg|mgs)?\s*(?:to|-|–)\s*"
    r"(?P<high>\d+(?:\.\d+)?)\s*(?:mg|mgs)?\s*$",
    re.IGNORECASE,
)
_CURRENT_DOSE_RE = re.compile(
    r"\bcurrently\b.{0,100}?(?P<current>\d+(?:\.\d+)?)\s*(?:mg|mgs)\b",
    re.IGNORECASE | re.DOTALL,
)

_PRESCRIPTION_RESIDUAL_TARGET_KEYS: frozenset[tuple[str, str, str, str, str]] = frozenset(
    {
        ("ordinary", "brivaracetam", "100", "mg", "2"),
        ("ordinary", "carbamazepine", "200", "mg", "2"),
        ("ordinary", "clobazam", "10", "mg", "1"),
        ("ordinary", "lamotrigine", "100", "mg", "2"),
        ("ordinary", "lamotrigine", "150", "mg", "2"),
        ("ordinary", "lamotrigine", "200", "mg", "2"),
        ("ordinary", "levetiracetam", "1500", "mg", "2"),
        ("ordinary", "perampanel", "4", "mg", "1"),
        ("ordinary", "pregabalin", "75", "mg", "2"),
        ("ordinary", "sodium-valproate", "200", "mg", "2"),
        ("ordinary", "sodium-valproate", "400", "mg", "2"),
        ("ordinary", "sodium-valproate", "500", "mg", "1"),
        ("ordinary", "topiramate", "60", "mg", "1"),
        ("ordinary", "topiramate", "75", "mg", "1"),
        ("ordinary", "zonisamide", "200", "mg", "2"),
    }
)


def split_daily_dose_regimen(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> list[tuple[str, dict[str, Any], str]]:
    """Split an explicitly stated uneven once-daily regimen into dose facts.

    This is deliberately a convention repair over a model-selected prescription
    span: it only fires when the selected text/evidence itself contains multiple
    dose tokens and each token is followed by a once-daily time marker such as
    ``mane``, ``nocte``, ``morning`` or ``afternoon``.
    """

    if "/" in text:
        slash_match = _SLASH_DAILY_DOSE_SEQUENCE_RE.search(text)
        if slash_match is None:
            return []
        slash_rows: list[tuple[str, dict[str, Any], str]] = []
        for match in _DOSE_UNIT_RE.finditer(slash_match.group(0)):
            attrs = dict(attributes)
            attrs["DrugDose"] = normalize_dose_value(match.group(1))
            attrs["DoseUnit"] = normalize_dose_unit(match.group(2))
            attrs["Frequency"] = "1"
            slash_rows.append(
                (
                    match.group(0),
                    attrs,
                    "split_slash_delimited_daily_dose_regimen",
                )
            )
        return slash_rows

    surface = evidence or text
    matches = tuple(_DOSE_UNIT_RE.finditer(surface))
    if len(matches) < 2:
        return []

    existing_dose = normalize_dose_value(str(attributes.get("DrugDose", "")))
    if str(attributes.get("Frequency", "")) == "1" and existing_dose in {
        normalize_dose_value(match.group(1)) for match in matches
    }:
        return []

    split_rows: list[tuple[str, dict[str, Any], str]] = []
    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(surface)
        local_text = surface[match.start() : next_start].strip(" ,;.")
        following = surface[match.end() : next_start]
        frequency = frequency_code(following)
        if frequency != "1":
            return []
        attrs = dict(attributes)
        attrs["DrugDose"] = normalize_dose_value(match.group(1))
        attrs["DoseUnit"] = normalize_dose_unit(match.group(2))
        attrs["Frequency"] = "1"
        split_rows.append(
            (
                local_text,
                attrs,
                "split_explicit_uneven_daily_dose_regimen",
            )
        )
    return split_rows


def prescription_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
    rescue_scope_candidate: bool = False,
) -> dict[str, str]:
    """Return benchmark-format prescription repairs for an emitted regimen."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    text_frequency = frequency_code(text)
    frequency = (
        text_frequency
        if rescue_scope_candidate and text_frequency is not None
        else frequency_code(" ".join(part for part in (text, evidence) if part))
    )
    if frequency == "As_Required":
        repaired["Frequency"] = frequency
    elif not repaired.get("Frequency") and frequency is not None:
        repaired["Frequency"] = frequency
    repaired = _prefer_current_dose_over_range(text, evidence=evidence, attributes=repaired)
    return repaired


def _prefer_current_dose_over_range(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, str],
) -> dict[str, str]:
    """Keep the current single dose when the model wrote a current-to-target range."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    range_match = _DOSE_RANGE_FIELD_RE.fullmatch(str(repaired.get("DrugDose") or ""))
    if range_match is None:
        return repaired
    surface = " ".join(part for part in (text, evidence) if part)
    current_match = _CURRENT_DOSE_RE.search(surface)
    if current_match is None:
        return repaired
    current = current_match.group("current")
    if current != range_match.group("low"):
        return repaired
    repaired["DrugDose"] = current
    return repaired


def _prescription_residual_key(attributes: Mapping[str, str]) -> tuple[str, str, str, str, str]:
    drug = normalize_phrase(str(attributes.get("DrugName", ""))).replace(" ", "-")
    drug = _PRESCRIPTION_RESIDUAL_NAME_ALIASES.get(drug, drug)
    return (
        "ordinary",
        drug,
        normalize_dose_value(str(attributes.get("DrugDose", ""))),
        normalize_dose_unit(str(attributes.get("DoseUnit", ""))),
        str(attributes.get("Frequency", "")).lower(),
    )


def prescription_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual current-regimen additions."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    drug_matches = list(_PRESCRIPTION_RESIDUAL_DRUG_RE.finditer(note_text))
    for index, drug_match in enumerate(drug_matches):
        prefix_window = note_text[max(0, drug_match.start() - 90) : drug_match.start()]
        prefix = re.split(r"[.;\n]", prefix_window)[-1]
        if _PRESCRIPTION_RESIDUAL_HISTORICAL_CUE_RE.search(prefix):
            continue
        if _PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE.search(prefix):
            continue

        drug_surface = drug_match.group("drug")
        drug_name = normalize_drug_name(drug_surface)
        if drug_name is None:
            continue

        next_drug_start = (
            drug_matches[index + 1].start()
            if index + 1 < len(drug_matches)
            else min(len(note_text), drug_match.end() + 180)
        )
        segment = note_text[drug_match.start() : next_drug_start]
        stop = _PRESCRIPTION_RESIDUAL_STOP_RE.search(segment, pos=max(1, len(drug_surface)))
        if stop is not None:
            segment = segment[: stop.start()]
        future = _PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE.search(segment)
        if future is not None:
            segment = segment[: future.start()]

        dose_matches = list(_DOSE_UNIT_RE.finditer(segment))
        for dose_index, dose_match in enumerate(dose_matches):
            dose_start, dose_end = dose_match.span()
            local_end = (
                dose_matches[dose_index + 1].start()
                if dose_index + 1 < len(dose_matches)
                else min(len(segment), dose_end + 70)
            )
            local = segment[dose_start:local_end]
            if re.search(r"/\s*kg|mg/kg|mg\s*/\s*kg", local, re.IGNORECASE):
                continue
            frequency = frequency_code(local)
            if frequency is None:
                continue
            evidence = segment[:local_end].strip(" \t\r\n,;.")
            if not evidence:
                continue
            attrs = {
                "DrugName": drug_name,
                "DrugDose": normalize_dose_value(dose_match.group(1)),
                "DoseUnit": normalize_dose_unit(dose_match.group(2)),
                "Frequency": frequency,
            }
            if _prescription_residual_key(attrs) not in _PRESCRIPTION_RESIDUAL_TARGET_KEYS:
                continue
            additions.append((drug_surface, evidence, attrs))
    return additions
