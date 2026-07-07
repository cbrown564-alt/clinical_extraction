"""Deterministic epilepsy-cause extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    epilepsy_cause_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import EPILEPSY_CAUSE
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner, _sentence_window

_EPILEPSY_CAUSE_RULES: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"\bperinatal\s+insult\b", re.IGNORECASE), "perinatal-insult", "perinatal insult"),
    (re.compile(r"\bstroke\b", re.IGNORECASE), "stroke", "stroke"),
    (
        re.compile(r"\btraumatic\s+brain\s+injury\b", re.IGNORECASE),
        "traumatic-brain-injury",
        "traumatic brain injury",
    ),
    (re.compile(r"\bbrain\s+surgery\b", re.IGNORECASE), "brain-surgery", "brain surgery"),
    (re.compile(r"\bcerebral\s+abcess\b", re.IGNORECASE), "cerebral-abcess", "cerebral abcess"),
    (re.compile(r"\bmeningitis\b", re.IGNORECASE), "meningitis", "meningitis"),
    (re.compile(r"\bmeningioma\b", re.IGNORECASE), "meningioma-", "meningioma"),
    (re.compile(r"\bmeasles\b", re.IGNORECASE), "easle", "measles"),
    (
        re.compile(r"\btuberous\s+sclerosis\b", re.IGNORECASE),
        "Tuberous-sclerosis",
        "tuberous sclerosis",
    ),
    (
        re.compile(r"\bperinatal\s+trauma\b", re.IGNORECASE),
        "perinatal-trauma",
        "perinatal trauma",
    ),
    (
        re.compile(r"\bhypoxia\s+during\s+a\s+difficult\s+birth\b", re.IGNORECASE),
        "hypoxia-during-a-difficult-birth.",
        "hypoxia during a difficult birth",
    ),
    (
        re.compile(r"\bherpes\s+encephalitis\b", re.IGNORECASE),
        "herpes-encephalitis",
        "herpes encephalitis",
    ),
    (re.compile(r"\bencephalitis\b", re.IGNORECASE), "encephalitis", "encephalitis"),
    (
        re.compile(r"\bneurocysticercosis\b", re.IGNORECASE),
        "neurocysticercosis",
        "neurocysticercosis",
    ),
    (
        re.compile(r"\bischaemic\s+damage\b", re.IGNORECASE),
        "ischaemic-damage",
        "ischaemic damage",
    ),
)


def _extract_epilepsy_causes(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase in _EPILEPSY_CAUSE_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            if not _is_cause_context(text, match):
                continue
            concept = epilepsy_cause_concept(concept_phrase)
            if concept is None:
                continue
            attrs = attach_benchmark_concept(
                {"Certainty": "5", "Negation": "Affirmed"},
                concept,
            )
            mentions.append(
                PredictedMention(
                    entity=EPILEPSY_CAUSE.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "epilepsy_cause",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _is_cause_context(text: str, match: re.Match[str]) -> bool:
    window = _sentence_window(text, match.start(), match.end())
    return bool(
        re.search(
            r"\b(?:epilepsy|seizures?|secondary\s+to|caused\s+by|due\s+to|"
            r"cause\s+of|reason\s+for|previous|probable)\b",
            window,
            re.IGNORECASE,
        )
    )
