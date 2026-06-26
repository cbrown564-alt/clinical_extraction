"""Deterministic when-diagnosed extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    when_diagnosed_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import WHEN_DIAGNOSED
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import PredictedMention

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner
from .text import _MONTHS, _MONTH_PATTERN, _number_value

_WHEN_DIAGNOSED_TEXT = "epileps"
_WHEN_DIAGNOSED_AGE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\bdiagnosed\s+with\s+epilepsy\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bepilepsy\s+was\s+(?:first\s+)?diagnosed\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdiagnosis\s+of\s+epilepsy\b.{0,80}?\bwas\s+diagnosed\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
)
_WHEN_DIAGNOSED_DURATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\bdiagnosed\s+with\s+epilepsy\s+(?:around|approximately|about)?\s*"
        r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\s+"
        r"(?P<unit>years?|months?)\s+ago\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdiagnosis\s+of\s+epilepsy\s+was\s+made\s+"
        r"(?:around|approximately|about)?\s*"
        r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\s+"
        r"(?P<unit>years?|months?)\s+ago\b",
        re.IGNORECASE,
    ),
)
_WHEN_DIAGNOSED_DATE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        rf"\b(?:diagnosed\s+with\s+epilepsy|epilepsy\s+was\s+diagnosed|"
        rf"diagnosis\s+of\s+(?:his\s+|her\s+)?epilepsy)\s+"
        rf"(?:in\s+|was\s+made\s+in\s+|at\s+the\s+time\s+of\s+)?"
        rf"(?:(?P<month>{_MONTH_PATTERN})\s+)?(?P<year>20\d{{2}}|19\d{{2}})\b",
        re.IGNORECASE,
    ),
)
def _extract_when_diagnosed(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for patterns, attr_builder, rule_id in (
        (_WHEN_DIAGNOSED_AGE_PATTERNS, _when_diagnosed_age_attrs, "when_diagnosed_age"),
        (
            _WHEN_DIAGNOSED_DURATION_PATTERNS,
            _when_diagnosed_duration_attrs,
            "when_diagnosed_duration",
        ),
        (_WHEN_DIAGNOSED_DATE_PATTERNS, _when_diagnosed_date_attrs, "when_diagnosed_date"),
    ):
        for pattern in patterns:
            for match in pattern.finditer(text):
                if any(_overlaps(match.span(), span) for span in occupied):
                    continue
                attrs = attr_builder(match)
                attrs.update({"Certainty": "5", "Negation": "Affirmed"})
                attrs = attach_benchmark_concept(attrs, when_diagnosed_concept())
                mentions.append(
                    PredictedMention(
                        entity=WHEN_DIAGNOSED.name,
                        text=_WHEN_DIAGNOSED_TEXT,
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
def _when_diagnosed_age_attrs(match: re.Match[str]) -> dict[str, str]:
    return {"Age": _number_value(match.group("age")), "AgeUnit": "Year"}


def _when_diagnosed_duration_attrs(match: re.Match[str]) -> dict[str, str]:
    return {
        "NumberOfTimePeriods": _number_value(match.group("count")),
        "TimePeriod": "Month" if match.group("unit").lower().startswith("month") else "Year",
    }


def _when_diagnosed_date_attrs(match: re.Match[str]) -> dict[str, str]:
    attrs = {"YearDate": match.group("year")}
    month = match.groupdict().get("month")
    if month:
        attrs["MonthDate"] = _MONTHS[month.lower()]
    return attrs
