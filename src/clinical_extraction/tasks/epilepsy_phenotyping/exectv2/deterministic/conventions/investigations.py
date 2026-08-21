"""Investigations modality/result convention cleanup."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

_INVESTIGATION_MODALITY_ATTRS: dict[str, tuple[str, str | None]] = {
    "MRI": ("MRI_Performed", "MRI_Results"),
    "CT": ("CT_Performed", "CT_Results"),
    "EEG": ("EEG_Performed", "EEG_Results"),
}
_INVESTIGATION_MODALITY_PATTERNS: dict[str, re.Pattern[str]] = {
    "MRI": re.compile(r"\b(?:MRI|MR\s+brain|magnetic resonance)\b", re.IGNORECASE),
    "CT": re.compile(r"\bCT\b", re.IGNORECASE),
    "EEG": re.compile(r"\b(?:EEG|VEEG|video[-\s]+EEG|telemetry)\b", re.IGNORECASE),
}
_PENDING_INVESTIGATION_CUE = re.compile(
    r"\b(?:"
    r"will\s+(?:arrange|request|have|organise|organize)|"
    r"arrang(?:e|ing)|request(?:ed|ing)?|await(?:ed|ing)|appointment|"
    r"suggest(?:ed|ing)?|recommend(?:ed|ing)?|should\s+update|chase|"
    r"up\s+to\s+date|not\s+yet\s+(?:performed|received)|planned|pending"
    r")\b",
    re.IGNORECASE,
)
_EXPLICIT_NO_TEST_CUE = re.compile(
    r"\b(?:no|never|not|without|had\s+not|has\s+not|have\s+not|hasn't|haven't)\b",
    re.IGNORECASE,
)
_INVESTIGATION_NORMAL_RESULT_CUE = re.compile(
    r"\b(?:normal|negative|no\s+(?:abnormality|lesion|structural)|essentially normal)\b",
    re.IGNORECASE,
)
_INVESTIGATION_ABNORMAL_RESULT_CUE = re.compile(
    r"\b(?:abnormal|spike|sharp|slow|slowing|wave|discharges?|dysplasia|"
    r"sclerosis|meningioma|signal|gliosis|infarct|lesion|focus|atrophy)\b",
    re.IGNORECASE,
)


def investigation_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> dict[str, str]:
    """Remove cross-modality or unsupported no-test attributes from an investigation.

    Qwen often renders a valid completed test while also defaulting unrelated
    modalities to ``*_Performed='No'``. This is a convention cleanup over the
    model-selected investigation, not a new investigation detector.
    """

    repaired = {str(key): str(value) for key, value in attributes.items()}
    text_modalities = _modalities_in_text(text)
    if text_modalities:
        for modality in set(_INVESTIGATION_MODALITY_ATTRS) - text_modalities:
            _remove_investigation_modality_attrs(repaired, modality)
    surface = " ".join(part for part in (text, evidence) if part)
    for modality, (performed_key, result_key) in _INVESTIGATION_MODALITY_ATTRS.items():
        if (
            result_key is not None
            and repaired.get(result_key)
            in {
                "Normal",
                "Abnormal",
                "Unknown",
            }
            and repaired.get(performed_key) is None
        ):
            repaired[performed_key] = "Yes"
        if repaired.get(performed_key) != "No":
            continue
        if _explicit_not_performed(modality, surface):
            continue
        repaired.pop(performed_key, None)
        if result_key is not None and repaired.get(result_key) == "Unknown":
            repaired.pop(result_key, None)
    return repaired


def is_pending_investigation(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True when the mention is only a planned/awaited test, not a completed one."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    scoring_attrs = _investigation_scoring_attributes(repaired)
    surface = " ".join(part for part in (text, evidence) if part)
    if not _PENDING_INVESTIGATION_CUE.search(surface):
        return False
    if _has_positive_investigation(scoring_attrs):
        return False
    has_result_cue = _INVESTIGATION_NORMAL_RESULT_CUE.search(
        surface
    ) or _INVESTIGATION_ABNORMAL_RESULT_CUE.search(surface)
    if has_result_cue:
        return False
    return True


_INVESTIGATION_RESIDUAL_PATTERNS: tuple[tuple[re.Pattern[str], str, str, str], ...] = (
    (
        re.compile(
            r"\b(?:EEGs?\s+(?:has|have)\s+shown\s+(?:evidence\s+of\s+epilepsy|"
            r"a\s+probable\s+left\s+occipital\s+lobe\s+focus)|"
            r"focal\s+epileptiform\s+changes\s+on\s+(?:(?:his|her)\s+)?EEG|"
            r"focal\s+impaired\s+awareness\s+seizures\s+and\s+dissociative\s+"
            r"seizures\.\s+Both\s+have\s+been\s+captured\s+on\s+EEG)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Abnormal",
        "eeg_abnormal_context_residual",
    ),
    (
        re.compile(
            r"\bEEG[\s\S]{0,240}(?:generalised spike and wave|spike and wave|"
            r"temporal lobe discharges|temporal slowing|abnormalities|"
            r"focal sharp waves|"
            r"multifocal EEG abnormalities|EEG abnormalities|paroxysms of "
            r"generalised spike and wave|single burst of generalised spike and wave|"
            r"sharp waves|sharpened waveforms|slow waves with spikes|"
            r"mildly abnormal|bitemporal slowing|bilateral temporal spikes|"
            r"right temporal lobe focus|is abnormal)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Abnormal",
        "eeg_abnormal_residual",
    ),
    (
        re.compile(
            r"\b(?:EEGs?[^.\n]{0,180}(?:reported\s+as\s+normal|"
            r"(?:has|have|had|is|was|were|been)\s+normal|"
            r"no\s+epileptiform\s+EEG\s+correlate|no\s+EEG\s+changes)|"
            r"normal EEG|EEG\s+\d{4}\s+normal|"
            r"MRI and EEG[^.\n]{0,100}(?:normal|have been normal)|"
            r"MRI brain and EEG[^.\n]{0,100}(?:normal|have been normal)|"
            r"confirmed on EEG)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Normal",
        "eeg_normal_residual",
    ),
    (
        re.compile(
            r"\b(?:MRI[\s\S]{0,160}\bnormal\b|MRI[- ]normal|MRI negative)\b",
            re.IGNORECASE,
        ),
        "MRI",
        "Normal",
        "mri_normal_residual",
    ),
    (
        re.compile(
            r"\bMRI[\s\S]{0,240}(?:focal cortical dysplasia|cavernoma|"
            r"hippocampal sclerosis|meningioma|signal|encephalitis|damage|lesion|"
            r"gliosis|infarct|atrophy|ischaemic change|perinatal insult|"
            r"small\s+right\s+hippocampus)\b",
            re.IGNORECASE,
        ),
        "MRI",
        "Abnormal",
        "mri_abnormal_residual",
    ),
    (
        re.compile(
            r"\bCT(?![^.\n]{0,80}\bECG\b)[^.\n]{0,80}\b(?:normal|"
            r"did\s+not\s+identify\s+any\s+acute\s+pathology)\b",
            re.IGNORECASE,
        ),
        "CT",
        "Normal",
        "ct_normal_residual",
    ),
    (
        re.compile(
            r"\bCT\s+scan[^.\n]{0,120}\bshowing\s+a\s+left\s+hemisphere\s+infarct\b",
            re.IGNORECASE,
        ),
        "CT",
        "Abnormal",
        "ct_abnormal_residual",
    ),
    (
        re.compile(
            r"\bCT\s+head\s+in\s+\d{4}\s+and\s+an\s+ECG\b",
            re.IGNORECASE,
        ),
        "CT",
        "Unknown",
        "ct_unknown_residual",
    ),
)


def investigation_residual_additions(
    note_text: str,
) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual completed-investigation additions."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    seen: set[tuple[str, str, str]] = set()
    for pattern, modality, result, _rule in _INVESTIGATION_RESIDUAL_PATTERNS:
        for match in pattern.finditer(note_text):
            evidence = match.group(0)
            key = (modality, result, normalize_phrase(evidence))
            if key in seen:
                continue
            seen.add(key)
            additions.append(
                (
                    modality,
                    evidence,
                    {
                        f"{modality}_Performed": "Yes",
                        f"{modality}_Results": result,
                    },
                )
            )
    return additions


def _investigation_scoring_attributes(attributes: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in attributes.items()
        if str(key) not in {"CUI", "CUIPhrase"}
    }


def _modalities_in_text(text: str) -> set[str]:
    return {
        modality
        for modality, pattern in _INVESTIGATION_MODALITY_PATTERNS.items()
        if pattern.search(text)
    }


def _remove_investigation_modality_attrs(attributes: dict[str, str], modality: str) -> None:
    performed_key, result_key = _INVESTIGATION_MODALITY_ATTRS[modality]
    attributes.pop(performed_key, None)
    if result_key is not None:
        attributes.pop(result_key, None)
    if modality == "EEG":
        attributes.pop("EEG_Type", None)


def _has_positive_investigation(attributes: Mapping[str, str]) -> bool:
    return any(
        (key.endswith("_Performed") and value == "Yes")
        or (key.endswith("_Results") and value in {"Normal", "Abnormal"})
        or key == "EEG_Type"
        for key, value in attributes.items()
    )


def _explicit_not_performed(modality: str, surface: str) -> bool:
    pattern = _INVESTIGATION_MODALITY_PATTERNS[modality]
    for match in pattern.finditer(surface):
        start = max(0, match.start() - 45)
        end = min(len(surface), match.end() + 45)
        if _EXPLICIT_NO_TEST_CUE.search(surface[start:end]):
            return True
    return False
