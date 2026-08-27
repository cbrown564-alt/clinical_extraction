"""Deterministic diagnosis extraction rules."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

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
    is_diagnosis_descendant,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner, _sentence_window

if TYPE_CHECKING:
    from ..recognise_ledger import RecogniseCandidate


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
_FOCAL_ONSET_HEADING_PATTERN = re.compile(
    r"\b(epilepsy\s*[-–,]\s*focal\s+onset)\b",
    re.IGNORECASE,
)
_POSSIBLY_FOCAL_ONSET_PATTERN = re.compile(
    r"\b(possibly\s+focal\s+onset)\b",
    re.IGNORECASE,
)
_SERVICE_CONTEXT_FOLLOWING = re.compile(
    r"\s+(?:nurse|nurses|specialist\s+nurses?|service|serivce|helpline|clinic|team|colleagues)\b",
    re.IGNORECASE,
)
_FAMILY_HISTORY_OF_PREFIX = re.compile(
    r"\b(?:no\s+)?family\s+history\s+of\s*$",
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


def _is_nondiagnostic_service_context(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : match.end() + 64]
    if _SERVICE_CONTEXT_FOLLOWING.match(right):
        return True
    prefix = text[max(0, match.start() - 120) : match.start()]
    return bool(_FAMILY_HISTORY_OF_PREFIX.search(prefix))


def _focal_onset_alias_matches(text: str) -> tuple[re.Match[str], ...]:
    return (
        *_FOCAL_ONSET_HEADING_PATTERN.finditer(text),
        *_POSSIBLY_FOCAL_ONSET_PATTERN.finditer(text),
    )


def _focal_onset_alias_concept_phrase(phrase: str, evidence: str) -> str:
    if _POSSIBLY_FOCAL_ONSET_PATTERN.fullmatch(phrase.strip()):
        return "focal epilepsy"
    format_target = sd.diagnosis_format_target(phrase, evidence)
    return format_target or phrase


def _extract_diagnoses(
    text: str,
    *,
    include_resolution_candidate: bool = False,
    include_benchmark_residuals: bool = False,
    service_context_exclusion: bool = False,
    secondary_to_retention: bool = False,
    focal_onset_alias: bool = False,
) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    pattern = (
        _RESOLUTION_DIAGNOSIS_PATTERN
        if include_resolution_candidate
        else _BASELINE_DIAGNOSIS_PATTERN
    )
    alias_matches = _focal_onset_alias_matches(text) if focal_onset_alias else ()
    matches = sorted(
        (*pattern.finditer(text), *_PROBABLE_FOCAL_PATTERN.finditer(text), *alias_matches),
        key=lambda m: m.end() - m.start(),
        reverse=True,
    )
    for match in matches:
        if any(_overlaps(match.span(), span) for span in occupied):
            continue
        if include_resolution_candidate and _is_excluded_diagnosis_context(text, match):
            continue
        if service_context_exclusion and _is_nondiagnostic_service_context(text, match):
            continue
        if not include_resolution_candidate and (
            (
                not (
                    service_context_exclusion
                    and _has_possessive_diagnosis_prefix(text, match)
                )
                and _is_diagnosis_phrase_inside_onset_statement(text, match)
            )
            or (
                not secondary_to_retention
                and _is_diagnosis_phrase_inside_cause_statement(text, match)
            )
        ):
            continue
        phrase = match.group(1)
        evidence = _sentence_window(text, match.start(), match.end())
        if focal_onset_alias and (
            _FOCAL_ONSET_HEADING_PATTERN.fullmatch(phrase.strip())
            or _POSSIBLY_FOCAL_ONSET_PATTERN.fullmatch(phrase.strip())
        ):
            concept_phrase = _focal_onset_alias_concept_phrase(phrase, evidence)
            phrase = concept_phrase
        else:
            concept_phrase = phrase
        format_target = sd.diagnosis_format_target(concept_phrase, evidence)
        concept = (
            diagnosis_concept(concept_phrase)
            or diagnosis_concept(canonicalize_diagnosis_concept(concept_phrase))
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
                evidence=evidence,
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


_POSSESSIVE_DIAGNOSIS_PREFIX = re.compile(
    r"(?:\b(?:his|her|their)|['\u2019]s)\s*$",
    re.IGNORECASE,
)


def _has_possessive_diagnosis_prefix(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 12) : match.start()]
    return bool(_POSSESSIVE_DIAGNOSIS_PREFIX.search(prefix))


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


def _mention_span(mention: PredictedMention) -> tuple[int, int] | None:
    span = mention.evidence_span
    if span is None or span.start_char is None or span.end_char is None:
        return None
    return (span.start_char, span.end_char)


def _diagnosis_concept_from_phrase(phrase: str):
    format_target = sd.diagnosis_format_target(phrase, phrase)
    return (
        diagnosis_concept(phrase)
        or diagnosis_concept(canonicalize_diagnosis_concept(phrase))
        or (diagnosis_concept(format_target) if format_target else None)
    )


def _baseline_diagnosis_matches(text: str) -> tuple[re.Match[str], ...]:
    matches: list[re.Match[str]] = []
    for name in _RECOGNISE_SURFACES:
        pattern = re.compile(rf"\b({re.escape(name)})\b", re.IGNORECASE)
        matches.extend(pattern.finditer(text))
    matches.extend(_PROBABLE_FOCAL_PATTERN.finditer(text))
    return tuple(
        sorted(
            matches,
            key=lambda match: match.end() - match.start(),
            reverse=True,
        )
    )


def _predicted_diagnosis_from_match(text: str, match: re.Match[str]) -> PredictedMention | None:
    phrase = match.group(1)
    concept = _diagnosis_concept_from_phrase(phrase)
    if concept is None:
        return None
    attrs = {
        "DiagCategory": concept.canonical,
        "Certainty": "5",
        "Negation": "Affirmed",
    }
    attrs = attach_benchmark_concept(attrs, concept)
    return PredictedMention(
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


def nondiagnostic_context_diagnosis_candidates(
    note_text: str,
) -> tuple[RecogniseCandidate, ...]:
    from ..recognise_ledger import DIAGNOSIS_NONDIAGNOSTIC_CONTEXT, RecogniseCandidate

    candidates: list[RecogniseCandidate] = []
    seen_spans: set[tuple[int, int]] = set()
    for match in _baseline_diagnosis_matches(note_text):
        if not _is_nondiagnostic_service_context(note_text, match):
            continue
        span = match.span()
        if span in seen_spans:
            continue
        mention = _predicted_diagnosis_from_match(note_text, match)
        if mention is None:
            continue
        seen_spans.add(span)
        candidates.append(
            RecogniseCandidate(
                mention=mention,
                candidate_class=DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
                rule_id="recognise.diagnosis_nondiagnostic_context",
            )
        )
    return tuple(candidates)


def nested_ancestor_diagnosis_candidates(
    note_text: str,
) -> tuple[RecogniseCandidate, ...]:
    from ..recognise_ledger import DIAGNOSIS_NESTED_ANCESTOR, RecogniseCandidate

    direct_mentions = _extract_diagnoses(note_text)
    direct_concepts = {
        canonicalize_diagnosis_concept(mention.text) for mention in direct_mentions
    }
    accepted_spans: list[tuple[tuple[int, int], str]] = []
    for mention in direct_mentions:
        span = _mention_span(mention)
        concept = canonicalize_diagnosis_concept(mention.text)
        if span is None or not concept:
            continue
        accepted_spans.append((span, concept))

    seen_concepts: set[str] = set()
    candidates: list[RecogniseCandidate] = []
    for match in _baseline_diagnosis_matches(note_text):
        span = match.span()
        if not any(_overlaps(span, accepted_span) for accepted_span, _ in accepted_spans):
            continue
        if _is_diagnosis_phrase_inside_onset_statement(note_text, match) or (
            _is_diagnosis_phrase_inside_cause_statement(note_text, match)
        ):
            continue
        candidate_mention = _predicted_diagnosis_from_match(note_text, match)
        if candidate_mention is None:
            continue
        candidate_concept = canonicalize_diagnosis_concept(candidate_mention.text)
        if not candidate_concept or candidate_concept in direct_concepts:
            continue
        if not any(
            accepted_concept != candidate_concept
            and is_diagnosis_descendant(accepted_concept, candidate_concept)
            for accepted_span, accepted_concept in accepted_spans
            if _overlaps(span, accepted_span)
        ):
            continue
        if candidate_concept in seen_concepts:
            continue
        seen_concepts.add(candidate_concept)
        candidates.append(
            RecogniseCandidate(
                mention=candidate_mention,
                candidate_class=DIAGNOSIS_NESTED_ANCESTOR,
                rule_id="recognise.diagnosis_nested_ancestor",
            )
        )
    return tuple(candidates)


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
