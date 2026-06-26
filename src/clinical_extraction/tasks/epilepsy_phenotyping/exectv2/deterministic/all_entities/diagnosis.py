"""Deterministic diagnosis extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    DIAGNOSIS_SURFACE_FORMS,
    attach_benchmark_concept,
    diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import PredictedMention

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner

_DIAGNOSIS_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(name) for name in sorted(DIAGNOSIS_SURFACE_FORMS, key=len, reverse=True))
    + r")\b",
    re.IGNORECASE,
)
def _extract_diagnoses(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    matches = sorted(
        _DIAGNOSIS_PATTERN.finditer(text),
        key=lambda m: m.end() - m.start(),
        reverse=True,
    )
    for match in matches:
        if any(_overlaps(match.span(), span) for span in occupied):
            continue
        if _is_diagnosis_phrase_inside_onset_statement(text, match):
            continue
        if _is_diagnosis_phrase_inside_cause_statement(text, match):
            continue
        phrase = match.group(1)
        concept = diagnosis_concept(phrase)
        if concept is None:
            continue
        attrs = {
            "DiagCategory": concept.canonical,
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=phrase,
                attributes=attrs,
                evidence=phrase,
                evidence_span=match_span(match),
                component_owner=_owner(
                    "deterministic_diagnosis_phrase",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
        occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)
def _is_diagnosis_phrase_inside_onset_statement(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : match.end() + 48]
    return bool(
        re.match(
            r"\s+(?:first\s+)?(?:started|began|commenced|presented|since|from)\b",
            right,
            re.IGNORECASE,
        )
    )


def _is_diagnosis_phrase_inside_cause_statement(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : match.end() + 64]
    return bool(
        re.match(
            r"\s+(?:is\s+)?(?:secondary\s+to|caused\s+by|due\s+to)\b",
            right,
            re.IGNORECASE,
        )
    )
