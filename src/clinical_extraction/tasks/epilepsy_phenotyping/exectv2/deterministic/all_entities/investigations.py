"""Deterministic investigations extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    investigation_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import INVESTIGATIONS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _canonical_modality, _owner, _sentence_window

_INVESTIGATION_PATTERN = re.compile(r"\b(EEGs?|MRI|CT)(?:\s+(?:brain|scan|head))?\b", re.IGNORECASE)
_RESULT_NORMAL = re.compile(r"\b(?:normal|negative|unremarkable)\b", re.IGNORECASE)
_RESULT_ABNORMAL = re.compile(
    r"\b(?:abnormal|abnormalities|lesion|infarct|sclerosis|dysplasia|"
    r"spike\s+and\s+wave|polyspikes?|epileptiform)\b",
    re.IGNORECASE,
)
_RESULT_UNKNOWN = re.compile(
    r"\b(?:do\s+not\s+have|don't\s+have|not\s+have|not\s+seen|"
    r"await(?:ing)?|pending|unknown|unavailable)\b.{0,80}\b(?:results?|reports?)\b|"
    r"\b(?:results?|reports?)\b.{0,80}\b(?:do\s+not\s+have|don't\s+have|"
    r"not\s+available|unavailable|unknown|pending)\b",
    re.IGNORECASE,
)
_EEG_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsleep\s*deprived\b", re.IGNORECASE), "SleepDeprived"),
    (re.compile(r"\bvideo\s*telemetry\b", re.IGNORECASE), "VideoTelemetry"),
)


def _extract_investigations(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    for match in _INVESTIGATION_PATTERN.finditer(text):
        modality = _canonical_modality(match.group(1))
        evidence = _sentence_window(text, match.start(), match.end())
        result = _investigation_result(evidence)
        attrs = {f"{modality}_Performed": "Yes"}
        if result:
            attrs[f"{modality}_Results"] = result
        if modality == "EEG":
            eeg_type = _eeg_type(evidence)
            if eeg_type:
                attrs["EEG_Type"] = eeg_type
        concept = investigation_concept(modality, result)
        if concept:
            attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=INVESTIGATIONS.name,
                text=modality,
                attributes=attrs,
                evidence=evidence,
                evidence_span=match_span(match),
                component_owner=_owner(
                    "investigation_result",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return tuple(mentions)


def _investigation_result(text: str) -> str | None:
    if _RESULT_UNKNOWN.search(text):
        return "Unknown"
    if _RESULT_ABNORMAL.search(text):
        return "Abnormal"
    if _RESULT_NORMAL.search(text):
        return "Normal"
    return None


def _eeg_type(text: str) -> str | None:
    for pattern, value in _EEG_TYPE_PATTERNS:
        if pattern.search(text):
            return value
    if re.search(
        r"\b(?:standard|routine)\s+EEG\b|\bsingle\s+burst\s+of\s+"
        r"(?:generalised|generalized)?\s*spike\s+and\s+wave\b",
        text,
        re.IGNORECASE,
    ):
        return "Standard"
    return None
