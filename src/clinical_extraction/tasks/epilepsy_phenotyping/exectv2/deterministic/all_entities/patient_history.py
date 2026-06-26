"""Deterministic patient-history extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    attach_benchmark_concept,
    patient_history_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import PATIENT_HISTORY
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import PredictedMention

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner, _sentence_start, _sentence_window
from .text import _temporal_unit

_PATIENT_HISTORY_RULES: tuple[
    tuple[re.Pattern[str], str, str],
    ...
] = (
    (
        re.compile(r"\bfebrile\s+convulsions?\b", re.IGNORECASE),
        "febrile-convulsions",
        "febrile convulsions",
    ),
    (re.compile(r"\bfebrile\s+seizures?\b", re.IGNORECASE), "febrile-seizures", "febrile seizures"),
    (re.compile(r"\bmyoclonic\s+jerks?\b", re.IGNORECASE), "myoclonic-jerks", "myoclonic jerks"),
    (re.compile(r"\babsences?\b", re.IGNORECASE), "absences", "absences"),
    (re.compile(r"\banxiety\b", re.IGNORECASE), "anxiety", "anxiety"),
    (re.compile(r"\bdepression\b", re.IGNORECASE), "depression", "depression"),
    (re.compile(r"\bmigraines?\b", re.IGNORECASE), "migraine", "migraine"),
    (
        re.compile(r"\bdissociative\s+seizures?\b", re.IGNORECASE),
        "dissociative-seizures",
        "dissociative seizures",
    ),
    (
        re.compile(r"\bnon[-\s]epileptic\s+psychogenic\s+seizures?\b", re.IGNORECASE),
        "non-epileptic-psychogenic-seizures",
        "non epileptic psychogenic seizures",
    ),
    (
        re.compile(r"\bnon[-\s]epileptic\s+attacks?\b", re.IGNORECASE),
        "non-epileptic-attacks",
        "non epileptic attacks",
    ),
    (
        re.compile(r"\btransient\s+loss\s+of\s+consciousness\b", re.IGNORECASE),
        "transient-loss-of-consciousness",
        "transient loss of consciousness",
    ),
    (
        re.compile(r"\bloss\s+of\s+consciousness\b", re.IGNORECASE),
        "loss-of-consciousness",
        "loss of consciousness",
    ),
    (re.compile(r"\bdiabetes\b", re.IGNORECASE), "diabetes", "diabetes"),
    (re.compile(r"\bgliosis\b", re.IGNORECASE), "gliosis", "gliosis"),
    (
        re.compile(r"\bcortical\s+dysplasia\b", re.IGNORECASE),
        "cortical-dysplasia",
        "cortical dysplasia",
    ),
    (
        re.compile(
            r"\b(?:severe\s+|minor\s+)?head\s+injury"
            r"(?:\s+due\s+to\s+an?\s+RTA)?(?:\s+in\s+\d{4})?\b",
            re.IGNORECASE,
        ),
        "head-injury",
        "head injury",
    ),
    (
        re.compile(r"\btraumatic\s+brain\s+injury(?:\s+in\s+\d{4})?\b", re.IGNORECASE),
        "traumatic-brain-injury",
        "traumatic brain injury",
    ),
    (re.compile(r"\bviral\s+meningitis\b", re.IGNORECASE), "meningitis", "viral meningitis"),
    (re.compile(r"\bmeningitis\b", re.IGNORECASE), "meningitis", "meningitis"),
    (
        re.compile(r"\bviral\s+encephalitis\b", re.IGNORECASE),
        "viral-encephalitis",
        "viral encephalitis",
    ),
    (re.compile(r"\bencephalitis\b", re.IGNORECASE), "encephalitis", "encephalitis"),
    (re.compile(r"\bbrain\s+surgery\b", re.IGNORECASE), "brain-surgery", "brain surgery"),
    (
        re.compile(r"\bcerebral\s+ab(?:s|c)cess\b", re.IGNORECASE),
        "cerebral-abcess",
        "cerebral abcess",
    ),
    (re.compile(r"\bhypertension\b", re.IGNORECASE), "hypertension", "hypertension"),
    (
        re.compile(r"\blearning\s+disabilit(?:y|ies)\b", re.IGNORECASE),
        "learning-disabilities",
        "learning disabilities",
    ),
    (
        re.compile(r"\blearning\s+difficult(?:y|ies)\b", re.IGNORECASE),
        "learning-difficulties",
        "learning difficulties",
    ),
    (re.compile(r"\b(?:stroke|CVA)\b", re.IGNORECASE), "stroke", "stroke"),
    (re.compile(r"\bsyncope\b", re.IGNORECASE), "syncope", "syncope"),
    (re.compile(r"\bphotosensitivity\b", re.IGNORECASE), "photosensitivity", "photosensitivity"),
    (
        re.compile(r"\btuberous\s+sclerosis\b", re.IGNORECASE),
        "tuberous-sclerosis",
        "tuberous sclerosis",
    ),
    (re.compile(r"\bmeasles\b", re.IGNORECASE), "measles", "measles"),
    (
        re.compile(r"\bneurocysticercosis\b", re.IGNORECASE),
        "neurocysticercosis",
        "neurocysticercosis",
    ),
    (re.compile(r"\bmeningioma\b", re.IGNORECASE), "meningioma", "meningioma"),
    (
        re.compile(r"\bclusters?\s+of\s+seizures?\b", re.IGNORECASE),
        "cluster-of-seizures",
        "cluster of seizures",
    ),
    (re.compile(r"\bmyoclonus\b", re.IGNORECASE), "myoclonus", "myoclonus"),
)
_NEGATED_PATIENT_HISTORY = re.compile(
    r"\b(?:no|without|denies|denied)\s+(?:prior\s+|past\s+)?(?:history\s+of\s+)?"
    r"[^.:\n;]{0,90}$",
    re.IGNORECASE,
)
_HISTORY_CONTEXT = re.compile(
    r"\b(?:past\s+medical\s+history|past\s+history|history\s+of|comorbidit(?:y|ies)|"
    r"background|diagnos(?:e|i)s|summary|known\s+to\s+suffer|suffered|had|"
    r"with|includes?)\b",
    re.IGNORECASE,
)
def _extract_patient_history(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase in _PATIENT_HISTORY_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            if not _is_patient_history_context(text, match):
                continue
            concept = patient_history_concept(concept_phrase)
            if concept is None:
                continue
            evidence = _patient_history_evidence(text, match)
            attrs = _patient_history_attrs(text, match, evidence)
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=PATIENT_HISTORY.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=evidence,
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "patient_history",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)
def _patient_history_attrs(
    text: str,
    match: re.Match[str],
    evidence: str,
) -> dict[str, str]:
    attrs = _patient_history_temporal_attrs(evidence)
    if _is_patient_history_negated(text, match):
        return {**attrs, "Certainty": "1", "Negation": "Negated"}
    return {**attrs, "Certainty": "5", "Negation": "Affirmed"}


def _patient_history_temporal_attrs(evidence: str) -> dict[str, str]:
    age_range = re.search(
        r"\b(?:ages?|age\s+of)\s+(?P<low>\d{1,2})\s+(?:and|to|-)\s+(?P<high>\d{1,2})"
        r"\s*(?P<unit>months?|years?)?\b",
        evidence,
        re.IGNORECASE,
    )
    if age_range:
        return {
            "AgeLower": age_range.group("low"),
            "AgeUpper": age_range.group("high"),
            "AgeUnit": _temporal_unit(age_range.group("unit")),
        }
    age = re.search(
        r"\b(?:at\s+)?(?:the\s+)?age\s+of\s+(?P<age>\d{1,2})\s*"
        r"(?P<unit>months?|years?)?\b",
        evidence,
        re.IGNORECASE,
    )
    if age:
        return {
            "Age": age.group("age"),
            "AgeUnit": _temporal_unit(age.group("unit")),
        }
    duration = re.search(
        r"\b(?:for|last|past)\s+(?P<count>\d{1,2})\s+(?P<unit>months?|years?)\b",
        evidence,
        re.IGNORECASE,
    )
    if duration:
        return {
            "NumberOfTimePeriods": duration.group("count"),
            "TimePeriod": _temporal_unit(duration.group("unit")),
        }
    year = re.search(r"\b(?P<year>20\d{2}|19\d{2})\b", evidence)
    if year:
        return {"YearDate": year.group("year")}
    if re.search(r"\bsurgery\b", evidence, re.IGNORECASE):
        return {"PointInTime": "Surgery"}
    return {}


def _is_patient_history_context(text: str, match: re.Match[str]) -> bool:
    window = _sentence_window(text, match.start(), match.end())
    right = text[match.end() : match.end() + 80]
    if _is_patient_history_negated(text, match):
        return True
    if _HISTORY_CONTEXT.search(window):
        return True
    if re.search(r"\b(?:at\s+the\s+age|age\s+of|in\s+\d{4})\b", right, re.IGNORECASE):
        return True
    return False


def _is_patient_history_negated(text: str, match: re.Match[str]) -> bool:
    left = text[max(0, match.start() - 110) : match.start()]
    return bool(_NEGATED_PATIENT_HISTORY.search(left))


def _patient_history_evidence(text: str, match: re.Match[str]) -> str:
    sentence = _sentence_window(text, match.start(), match.end())
    relative_start = match.start() - _sentence_start(text, match.start())
    local_right = sentence[relative_start:]
    temporal_tail = re.match(
        r"[^.;\n]{0,80}?\b(?:in\s+\d{4}|at\s+the\s+age\s+of\s+\d{1,2}"
        r"(?:\s+(?:and|to|-)\s+\d{1,2})?|for\s+\d{1,2}\s+(?:months?|years?))\b",
        local_right,
        re.IGNORECASE,
    )
    if temporal_tail:
        return temporal_tail.group(0).strip(" ,;")
    return match.group(0)
