"""Deterministic onset extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    onset_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import ONSET
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import PredictedMention

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner
from .text import _canonical_onset_phrase, _number_value

_ONSET_AGE_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:first\s+)?(?:started|began|commenced|presented)\s+"
    r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+|when\s+\w+\s+was\s+)?"
    r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
    re.IGNORECASE,
)
_ONSET_SINCE_AGE_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:since|from)\s+(?:the\s+)?(?:age\s+of\s+|age\s+)?"
    r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
    re.IGNORECASE,
)
_ONSET_DURATION_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:first\s+)?(?:started|began|commenced|presented)\s+"
    r"(?:around|approximately|about)?\s*"
    r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b\s+"
    r"(?P<unit>years?|months?)\s+ago\b",
    re.IGNORECASE,
)
def _extract_onsets(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, attr_builder, rule_id in (
        (_ONSET_AGE_PATTERN, _onset_age_attrs, "onset_epilepsy_age"),
        (_ONSET_SINCE_AGE_PATTERN, _onset_age_attrs, "onset_epilepsy_age"),
        (_ONSET_DURATION_PATTERN, _onset_duration_attrs, "onset_epilepsy_duration"),
    ):
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            phrase = _canonical_onset_phrase(match.group("phrase"))
            concept = onset_concept(phrase)
            if concept is None:
                continue
            attrs = attr_builder(match)
            attrs.update({"Certainty": "5", "Negation": "Affirmed"})
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=ONSET.name,
                    text=phrase,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        rule_id,
                        RuleGroup.TEMPORAL_ANCHOR,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)
def _onset_age_attrs(match: re.Match[str]) -> dict[str, str]:
    return {"Age": _number_value(match.group("age")), "AgeUnit": "Year"}


def _onset_duration_attrs(match: re.Match[str]) -> dict[str, str]:
    return {
        "NumberOfTimePeriods": _number_value(match.group("count")),
        "TimePeriod": "Month" if match.group("unit").lower().startswith("month") else "Year",
    }
