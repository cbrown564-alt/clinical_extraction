"""Deterministic birth-history extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    birth_history_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import BIRTH_HISTORY
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner

_BIRTH_HISTORY_RULES: tuple[tuple[re.Pattern[str], str, str, dict[str, str]], ...] = (
    (re.compile(r"\bborn\s+normally\b", re.IGNORECASE), "born-normally", "born normally", {}),
    (
        re.compile(r"\bbirth\s+was\s+normal\b", re.IGNORECASE),
        "birth-was-normal",
        "birth was normal",
        {},
    ),
    (re.compile(r"\bnormal\s+birth\b", re.IGNORECASE), "normal-birth", "normal birth", {}),
    (re.compile(r"\bnormal\s+delivery\b", re.IGNORECASE), "normal-delivery", "normal delivery", {}),
    (
        re.compile(r"\bno\s+problems\s+when\s+\w+\s+was\s+born\b", re.IGNORECASE),
        "no-problems-when-he-was-born",
        "born normally",
        {},
    ),
    (re.compile(r"\bfull[-\s]term\b", re.IGNORECASE), "full-term", "full term", {}),
    (
        re.compile(r"\bborn\s+prematurely\s+at\s+32\s+weeks\b", re.IGNORECASE),
        "born-prematurely-at-32-weeks",
        "born prematurely at 32 weeks",
        {"PrematureBirth": "32to<37_ModerateToLatePreterm"},
    ),
    (
        re.compile(r"\bborn\s+slightly\s+premature(?:ly)?\b", re.IGNORECASE),
        "born-slightly-premature",
        "born slightly premature",
        {"PrematureBirth": "34to<37_LatePretermBirth"},
    ),
    (
        re.compile(r"\bborn\s+prematurely\b", re.IGNORECASE),
        "born-prematurely",
        "born prematurely",
        {"PrematureBirth": "34to<37_LatePretermBirth"},
    ),
    (
        re.compile(r"\bperinatal\s+insult\b", re.IGNORECASE),
        "perinatal-insult",
        "perinatal insult",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+trauma\b", re.IGNORECASE),
        "perinatal-trauma",
        "perinatal trauma",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+injury\b", re.IGNORECASE),
        "perinatal-injury",
        "perinatal injury",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+hypoxia\b", re.IGNORECASE),
        "perinatal-hypoxia",
        "perinatal hypoxia",
        {},
    ),
    (
        re.compile(r"\bhypoxia\s+during\s+a\s+difficult\s+birth\b", re.IGNORECASE),
        "hypoxia-during-a-difficult-birth.",
        "hypoxia during a difficult birth",
        {},
    ),
    (
        re.compile(r"\bspecial\s+care\s+baby\s+unit\b", re.IGNORECASE),
        "Special-care-baby-Unit",
        "special care baby unit",
        {},
    ),
)


def _extract_birth_history(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase, extra_attrs in _BIRTH_HISTORY_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            concept = birth_history_concept(concept_phrase)
            if concept is None:
                continue
            attrs = {"Certainty": "5", "Negation": "Affirmed", **extra_attrs}
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=BIRTH_HISTORY.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "birth_history",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)
