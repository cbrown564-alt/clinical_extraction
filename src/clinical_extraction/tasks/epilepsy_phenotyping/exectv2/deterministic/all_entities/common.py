"""Shared helpers for deterministic all-entity extraction."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
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

from ..overlap import _overlaps as _overlaps
from ..rule_metadata import Portability, RuleGroup

_OWNER_PREFIX = "deterministic"


def _sentence_start(text: str, start: int) -> int:
    return max(text.rfind(".", 0, start), text.rfind("\n", 0, start)) + 1


def _canonical_modality(surface: str) -> str:
    upper = re.sub(r"[\s-]+", " ", surface).upper()
    if upper.startswith("EEG") or upper.startswith("VEEG") or upper.startswith("VIDEO EEG"):
        return "EEG"
    if upper.startswith("MR"):
        return "MRI"
    return "CT"


def _right_context_until_separator(text: str, start: int) -> str:
    tail = text[start:]
    stop = len(tail)
    for separator in (" and ", ";", "\n", "."):
        idx = tail.find(separator)
        if idx != -1:
            stop = min(stop, idx)
    return tail[:stop].strip(" ,;")


def _sentence_window(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_candidates = [idx for idx in (text.find(".", end), text.find("\n", end)) if idx != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1 : right].strip(" ,;")


def _owner(
    rule_id: str,
    group: RuleGroup,
    portability: Portability,
    *extra_portability: Portability,
) -> str:
    parts = [_OWNER_PREFIX, rule_id, group.value, portability.value]
    parts.extend(item.value for item in extra_portability)
    return ":".join(parts)


def _rule_family_summary() -> dict[str, dict[str, str]]:
    return {
        "prescription_medication": {
            "entity": PRESCRIPTION.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "phrase_scope_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "investigation_result": {
            "entity": INVESTIGATIONS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "diagnosis_phrase": {
            "entity": DIAGNOSIS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "onset_epilepsy_age": {
            "entity": ONSET.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "onset_epilepsy_duration": {
            "entity": ONSET.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "when_diagnosed": {
            "entity": WHEN_DIAGNOSED.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "phrase_scope_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "birth_history": {
            "entity": BIRTH_HISTORY.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "epilepsy_cause": {
            "entity": EPILEPSY_CAUSE.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "patient_history": {
            "entity": PATIENT_HISTORY.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "temporal_attributes": Portability.CLINICAL_EPILEPSY.value,
        },
        "seizure_frequency": {
            "entity": SEIZURE_FREQUENCY.name,
            "group": "see deterministic.pipeline diagnostics",
            "portability": Portability.SEIZURE_FREQUENCY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
    }
