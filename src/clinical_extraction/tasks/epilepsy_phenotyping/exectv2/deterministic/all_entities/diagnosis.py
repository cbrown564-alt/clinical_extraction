"""Deterministic diagnosis extraction rules."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    DIAGNOSIS_SURFACE_FORMS,
    attach_benchmark_concept,
    diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner, _sentence_window


def _surface_pattern(name: str) -> str:
    return r"[ \t-]+".join(re.escape(part) for part in name.split())


_RECALL_FIRST_SURFACES: tuple[str, ...] = (
    "symptomatic structural focal epilepsy",
    "symptomatic structural epilepsy",
    "localisation related epilepsy",
    "localization related epilepsy",
    "focal onset epilepsy",
    "epilepsy probable focal onset",
    "epilepsy probable focal",
)
_RECOGNISE_SURFACES: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *sorted(_RECALL_FIRST_SURFACES, key=len, reverse=True),
            *sorted(DIAGNOSIS_SURFACE_FORMS, key=len, reverse=True),
        )
    )
)
_PROBABLE_FOCAL_PATTERN = re.compile(
    r"\b(epilepsy\s*[-–,]\s*probable\s+focal(?:\s+onset)?)\b",
    re.IGNORECASE,
)
_BASELINE_DIAGNOSIS_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(name) for name in _RECOGNISE_SURFACES)
    + r")\b",
    re.IGNORECASE,
)
_RESOLUTION_DIAGNOSIS_PATTERN = re.compile(
    r"\b("
    + "|".join(
        _surface_pattern(name)
        for name in sorted(DIAGNOSIS_SURFACE_FORMS, key=len, reverse=True)
    )
    + r")\b",
    re.IGNORECASE,
)

_NEGATED_DIAGNOSIS_CONTEXT = re.compile(
    r"\b(?:no|without)\s+(?:clear\s+|convincing\s+|obvious\s+|significant\s+|real\s+)?"
    r"(?:history\s+of\s+|evidence\s+(?:of|to suggest)\s+|episodes?\s+(?:of|which)\s+|"
    r"events?\s+(?:of|which)\s+|features?\s+of\s+|diagnosis\s+of\s+|"
    r"(?:focal|absence|myoclonic|tonic|generalised|generalized|epileptic|seizure)\b)"
    r"[^.;\n]{0,120}$|"
    r"\b(?:has|have|had)\s+not\s+had\b[^.;\n]{0,120}$|"
    r"\bdo\s+not\s+think\b[^.;\n]{0,120}$",
    re.IGNORECASE,
)
_NONPATIENT_DIAGNOSIS_CONTEXT = re.compile(
    r"\b(?:family history|mother|father|maternal|paternal|brother|sister|aunt|uncle|"
    r"cousin|grandmother|grandfather)\b[^.;\n]{0,140}$",
    re.IGNORECASE,
)
_FAMILY_WITNESS_CONTEXT = re.compile(
    r"\b(?:mother|father|brother|sister|aunt|uncle|grandmother|grandfather)\b"
    r"[^.;\n]{0,32}\b(?:said|reported|confirmed|described|recalled)\b",
    re.IGNORECASE,
)
_ADMINISTRATIVE_DIAGNOSIS_CONTEXT = re.compile(
    r"\bepilepsy\s+(?:service|nurse|helpline|specialist)|"
    r"\bdiscussion about epilepsy\b|\bepilepsy in general\b|"
    r"\bsudden (?:unexpected )?death in epilepsy\b",
    re.IGNORECASE,
)
_UNCERTAIN_NONDIAGNOSIS_CONTEXT = re.compile(
    r"\b(?:may|might)\s+be\b[^.;\n]{0,100}\b(?:difficult|unclear|uncertain)\b",
    re.IGNORECASE,
)


def _extract_diagnoses(
    text: str,
    *,
    include_resolution_candidate: bool = False,
    include_benchmark_residuals: bool = False,
) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    pattern = (
        _RESOLUTION_DIAGNOSIS_PATTERN
        if include_resolution_candidate
        else _BASELINE_DIAGNOSIS_PATTERN
    )
    matches = sorted(
        (*pattern.finditer(text), *_PROBABLE_FOCAL_PATTERN.finditer(text)),
        key=lambda m: m.end() - m.start(),
        reverse=True,
    )
    for match in matches:
        if any(_overlaps(match.span(), span) for span in occupied):
            continue
        if include_resolution_candidate and _is_excluded_diagnosis_context(text, match):
            continue
        if not include_resolution_candidate and (
            _is_diagnosis_phrase_inside_onset_statement(text, match)
            or _is_diagnosis_phrase_inside_cause_statement(text, match)
        ):
            continue
        phrase = match.group(1)
        format_target = sd.diagnosis_format_target(phrase, phrase)
        concept = (
            diagnosis_concept(phrase)
            or diagnosis_concept(canonicalize_diagnosis_concept(phrase))
            or (diagnosis_concept(format_target) if format_target else None)
        )
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
                evidence=_sentence_window(text, match.start(), match.end()),
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
    if include_benchmark_residuals:
        _add_benchmark_residuals(
            text,
            mentions,
            include_resolution_candidate=include_resolution_candidate,
        )
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


def _add_benchmark_residuals(
    text: str,
    mentions: list[PredictedMention],
    *,
    include_resolution_candidate: bool,
) -> None:
    existing = {canonicalize_diagnosis_concept(mention.text) for mention in mentions}
    for residual_text, evidence in sd.diagnosis_residual_additions(
        text,
        include_resolution_candidate=include_resolution_candidate,
    ):
        normalized = canonicalize_diagnosis_concept(residual_text)
        if normalized in existing:
            continue
        if sd.is_redundant_diagnosis_residual_addition(
            residual_text,
            evidence=evidence,
            selected_texts=[mention.text for mention in mentions],
            include_resolution_candidate=include_resolution_candidate,
        ):
            continue
        evidence_match = re.search(re.escape(evidence), text, re.IGNORECASE)
        if evidence_match is None:
            continue
        context_match = _residual_context_match(
            text,
            residual_text=residual_text,
            evidence_match=evidence_match,
        )
        if _is_excluded_diagnosis_context(text, context_match):
            continue
        attrs = {
            "DiagCategory": diagnosis_category_for_concept(residual_text),
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        concept = diagnosis_concept(residual_text)
        if concept is not None:
            attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=residual_text,
                attributes=attrs,
                evidence=evidence,
                evidence_span=match_span(evidence_match),
                component_owner=_owner(
                    "deterministic_diagnosis_residual",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.BENCHMARK_FORMAT,
                    Portability.CLINICAL_EPILEPSY,
                ),
            )
        )
        existing.add(normalized)


def _residual_context_match(
    text: str,
    *,
    residual_text: str,
    evidence_match: re.Match[str],
) -> re.Match[str]:
    candidates = (residual_text, re.sub(r"\s+(?:seizures?|epilepsy)$", "", residual_text))
    for candidate in candidates:
        if not candidate:
            continue
        pattern = re.compile(
            r"[ \t-]+".join(re.escape(part) for part in candidate.split()),
            re.IGNORECASE,
        )
        match = pattern.search(text, evidence_match.start(), evidence_match.end())
        if match is not None:
            return match
    return evidence_match


def _is_excluded_diagnosis_context(text: str, match: re.Match[str]) -> bool:
    context = _sentence_window(text, match.start(), match.end())
    offset = context.lower().find(match.group(0).lower())
    left = context[:offset] if offset >= 0 else context
    if _NEGATED_DIAGNOSIS_CONTEXT.search(left):
        return True
    if _NONPATIENT_DIAGNOSIS_CONTEXT.search(left) and not _FAMILY_WITNESS_CONTEXT.search(left):
        return True
    if (
        match.group(0).strip().lower() == "epilepsy"
        and _ADMINISTRATIVE_DIAGNOSIS_CONTEXT.search(context)
    ):
        return True
    return bool(_UNCERTAIN_NONDIAGNOSIS_CONTEXT.search(context))
