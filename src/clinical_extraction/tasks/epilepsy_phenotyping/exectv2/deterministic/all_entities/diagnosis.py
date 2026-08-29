"""Deterministic diagnosis extraction rules."""

from __future__ import annotations

import re
from collections.abc import Callable
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
    DIAGNOSIS_PARENT,
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
    is_diagnosis_descendant,
)

from ..mention_identity import match_span
from ..rule_metadata import Portability, RuleGroup
from .common import _overlaps, _owner, _sentence_window

if TYPE_CHECKING:
    from ..find_ledger import FindCandidate


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
# Recall-first lexicon expansion: surfaces the direct benchmark lexicon
# misses. Matched only by the unrestricted-surface producer, so a Select
# keep rule must accept them before they can reach the select stop.
_RECALL_EXPANSION_SURFACES: tuple[str, ...] = (
    "epilepsy with generalised tonic clonic seizures alone",
    "epilepsy with generalized tonic clonic seizures alone",
    "temporal lobe onset seizures",
    "temporal lobe onset seizure",
    "frontal lobe onset seizures",
    "frontal lobe onset seizure",
    "drug resistant epilepsy",
    "drug refractory epilepsies",
    "drug refractory epilepsy",
    "refractory epilepsies",
    "refractory epilepsy",
    "temporal lobe seizures",
    "temporal lobe seizure",
    "epileptic attacks",
    "epileptic attack",
    "nocturnal seizures",
    "nocturnal seizure",
)
_EXPANDED_RECOGNISE_SURFACES: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *sorted(_RECALL_EXPANSION_SURFACES, key=len, reverse=True),
            *_RECOGNISE_SURFACES,
        )
    )
)
# Adjectival tokens annotators sometimes split out of compound diagnosis
# phrases as standalone gold units. Emitted only inside a matched surface.
_COMPONENT_TOKENS: frozenset[str] = frozenset(
    {
        "focal",
        "generalised",
        "generalized",
        "temporal",
        "frontal",
        "occipital",
        "parietal",
        "symptomatic",
        "secondary",
        "drug",
        "epileptic",
        "refractory",
        "nocturnal",
    }
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
) -> tuple[FindCandidate, ...]:
    from ..find_ledger import DIAGNOSIS_NONDIAGNOSTIC_CONTEXT, FindCandidate

    candidates: list[FindCandidate] = []
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
            FindCandidate(
                mention=mention,
                candidate_class=DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
                rule_id="recognise.diagnosis_nondiagnostic_context",
            )
        )
    return tuple(candidates)


def _nested_diagnosis_candidates(
    note_text: str,
    *,
    require_hierarchy: bool,
    candidate_class: str,
    rule_id: str,
) -> tuple[FindCandidate, ...]:
    from ..find_ledger import FindCandidate

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
    candidates: list[FindCandidate] = []
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
            if require_hierarchy:
                continue
            candidate_mention = _conceptless_diagnosis_from_match(note_text, match)
        candidate_concept = canonicalize_diagnosis_concept(candidate_mention.text)
        if not candidate_concept or candidate_concept in direct_concepts:
            continue
        if require_hierarchy and not any(
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
            FindCandidate(
                mention=candidate_mention,
                candidate_class=candidate_class,
                rule_id=rule_id,
            )
        )
    return tuple(candidates)


def nested_ancestor_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    from ..find_ledger import DIAGNOSIS_NESTED_ANCESTOR

    return _nested_diagnosis_candidates(
        note_text,
        require_hierarchy=True,
        candidate_class=DIAGNOSIS_NESTED_ANCESTOR,
        rule_id="recognise.diagnosis_nested_ancestor",
    )


def nested_surface_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: every distinct shorter surface overlapping an accepted
    span, with no hierarchy requirement. Select owns dedupe/specificity."""

    from ..find_ledger import DIAGNOSIS_NESTED_SURFACE

    return _nested_diagnosis_candidates(
        note_text,
        require_hierarchy=False,
        candidate_class=DIAGNOSIS_NESTED_SURFACE,
        rule_id="recognise.diagnosis_nested_surface",
    )


def _conceptless_diagnosis_from_match(
    text: str, match: re.Match[str]
) -> PredictedMention:
    """Candidate mention for a surface with no benchmark concept mapping.

    Inventory unit keys derive from canonicalized text, so a recall-first
    candidate is scoreable without a CUI. Only used on candidate paths;
    the direct path still requires a resolvable concept.
    """

    phrase = match.group(1) if match.groups() else match.group(0)
    return PredictedMention(
        entity=DIAGNOSIS.name,
        text=phrase,
        attributes={
            "DiagCategory": canonicalize_diagnosis_concept(phrase),
            "Certainty": "5",
            "Negation": "Affirmed",
        },
        evidence=_sentence_window(text, match.start(), match.end()),
        evidence_span=match_span(match),
        component_owner=_owner(
            "deterministic_diagnosis_phrase",
            RuleGroup.ANCHOR_PHRASE,
            Portability.CLINICAL_EPILEPSY,
        ),
    )


_HEADING_QUALIFIER_CONCEPTS: dict[str, str] = {
    "focal": "focal epilepsy",
    "generalised": "generalised epilepsy",
    "generalized": "generalised epilepsy",
    "temporal": "temporal lobe epilepsy",
    "frontal": "frontal lobe epilepsy",
    "occipital": "occipital lobe epilepsy",
    "parietal": "parietal lobe epilepsy",
}
_HEADING_QUALIFIER_RE = re.compile(
    r"\bepilepsy\s*(?:[–\-,]|\()\s*(?:probable\s+|possibly\s+|likely\s+)?"
    r"(focal|generalised|generalized|temporal|frontal|occipital|parietal)"
    r"(?:\s+(?:lobe|onset))?\s*\)?",
    re.IGNORECASE,
)
# Wider qualifier grammar: allows intervening tokens ("epilepsy –
# unclassified, possibly generalised") and adverb forms ("probably").
_HEADING_QUALIFIER_LOOSE_RE = re.compile(
    r"\bepilepsy\b[^.\n]{0,40}?\b(?:probable|probably|possibly|likely)\s+"
    r"(focal|generalised|generalized|temporal|frontal|occipital|parietal)\b",
    re.IGNORECASE,
)


def heading_decomposition_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: decompose qualified epilepsy headings into both concepts.

    ``epilepsy – probable focal`` names both ``epilepsy`` and
    ``focal epilepsy``; ``focal epilepsy (occipital)`` also names
    ``occipital lobe epilepsy``. The direct path emits one mention per
    span, so the second concept is otherwise unreachable.
    """

    from ..find_ledger import DIAGNOSIS_HEADING_DECOMPOSITION, FindCandidate

    candidates: list[FindCandidate] = []
    seen: set[str] = set()
    heading_matches = (
        *_HEADING_QUALIFIER_RE.finditer(note_text),
        *_HEADING_QUALIFIER_LOOSE_RE.finditer(note_text),
    )
    for match in heading_matches:
        qualifier = match.group(1).lower()
        evidence = _sentence_window(note_text, match.start(), match.end())
        for concept_text in (_HEADING_QUALIFIER_CONCEPTS[qualifier], "epilepsy"):
            concept_key = canonicalize_diagnosis_concept(concept_text)
            if concept_key in seen:
                continue
            seen.add(concept_key)
            concept = diagnosis_concept(concept_text)
            attrs = {
                "DiagCategory": concept.canonical if concept else concept_key,
                "Certainty": "5",
                "Negation": "Affirmed",
            }
            if concept is not None:
                attrs = attach_benchmark_concept(attrs, concept)
            candidates.append(
                FindCandidate(
                    mention=PredictedMention(
                        entity=DIAGNOSIS.name,
                        text=concept_text,
                        attributes=attrs,
                        evidence=evidence,
                        evidence_span=match_span(match),
                        component_owner=_owner(
                            "deterministic_diagnosis_heading_decomposition",
                            RuleGroup.ANCHOR_PHRASE,
                            Portability.CLINICAL_EPILEPSY,
                        ),
                    ),
                    candidate_class=DIAGNOSIS_HEADING_DECOMPOSITION,
                    rule_id="recognise.diagnosis_heading_decomposition",
                )
            )
    return tuple(candidates)


def _recall_surface_pattern(name: str) -> str:
    """Like ``_surface_pattern`` but crossing line breaks (recall-first only)."""

    return r"[\s-]+".join(re.escape(part) for part in name.split())


def _expanded_surface_matches(text: str) -> tuple[re.Match[str], ...]:
    matches: list[re.Match[str]] = []
    for name in _EXPANDED_RECOGNISE_SURFACES:
        pattern = re.compile(rf"\b({_recall_surface_pattern(name)})\b", re.IGNORECASE)
        matches.extend(pattern.finditer(text))
    return tuple(matches)


def _expansion_only_surface_matches(text: str) -> tuple[re.Match[str], ...]:
    matches: list[re.Match[str]] = []
    for name in _RECALL_EXPANSION_SURFACES:
        pattern = re.compile(rf"\b({_recall_surface_pattern(name)})\b", re.IGNORECASE)
        matches.extend(pattern.finditer(text))
    return tuple(matches)


# Alias decompositions: a matched span asserts concepts whose canonical
# surface differs from the span (annotators normalize these forms).
# Templates may use backreferences into the pattern.
_ALIAS_DECOMPOSITIONS: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (re.compile(r"\bfocal\s+onset\b", re.IGNORECASE), ("focal seizures",)),
    (
        re.compile(r"\b(temporal|frontal|occipital|parietal)\s+lobe\s+onset\b", re.IGNORECASE),
        (r"\1 lobe onset seizure",),
    ),
    (
        re.compile(r"\bfocal\s+to\s+bilateral\s+seizures?\b", re.IGNORECASE),
        ("focal to bilateral convulsive seizures",),
    ),
    (
        re.compile(r"\bsecondarily\s+generalised\s+seizures?\b", re.IGNORECASE),
        ("secondary generalised seizures",),
    ),
    (
        re.compile(r"\bnocturnal\s+(?:[a-z]+\s+){0,3}seizures?\b", re.IGNORECASE),
        ("nocturnal seizures",),
    ),
    (
        re.compile(
            r"\bcomplex\s+partial\s+and\b[^.\n]{0,60}?\bseizures?\b", re.IGNORECASE
        ),
        ("complex partial seizures",),
    ),
    (
        re.compile(r"\bepileptic\s+and\s+(?:[a-z]+\s+){0,2}attacks?\b", re.IGNORECASE),
        ("epileptic attack",),
    ),
    (
        re.compile(
            r"\bepilepsy\s*\??\s*(?:left|right)?\s*"
            r"(temporal|frontal|occipital|parietal)\s+lobe\b",
            re.IGNORECASE,
        ),
        (r"\1 lobe epilepsy",),
    ),
    (
        re.compile(
            r"\b(drug\s+(?:resistant|refractory)|refractory)\s+"
            r"(?:focal|generalised|generalized)\s+(epilepsy|epilepsies)\b",
            re.IGNORECASE,
        ),
        (r"\1 \2", "focal epilepsy"),
    ),
)

# Seizure-type -> syndrome inference: annotators fold seizure semiology
# into the syndrome concept (e.g. "symptomatic structural epilepsy" with
# focal motor seizures is annotated symptomatic structural *focal*
# epilepsy, whose inventory split includes "focal epilepsy").
_FOCAL_TYPE_EVIDENCE_RE = re.compile(
    r"\bfocal(?:\s+[a-z]+){0,3}\s+seizures?\b|\bcomplex\s+partial\s+seizures?\b|"
    r"\b(?:temporal|frontal|occipital|parietal)\s+lobe\b",
    re.IGNORECASE,
)
_GENERALISED_TYPE_EVIDENCE_RE = re.compile(
    r"\bgeneralised?\s+tonic[\s-]+clonic\s+seizures?\b|"
    r"\b(?:myoclonic|absence)\s+seizures?\b",
    re.IGNORECASE,
)
_EPILEPSY_EVIDENCE_RE = re.compile(r"\bepilep", re.IGNORECASE)


def _distinct_concept_emitter(
    note_text: str, candidate_class: str
) -> tuple[list[FindCandidate], Callable[[PredictedMention, str], None]]:
    """Shared dedupe-by-concept emitter seeded with the direct-path concepts."""

    from ..find_ledger import FindCandidate

    seen: set[str] = {
        canonicalize_diagnosis_concept(mention.text)
        for mention in _extract_diagnoses(note_text)
    }
    candidates: list[FindCandidate] = []

    def _emit(mention: PredictedMention, rule_id: str) -> None:
        concept_key = canonicalize_diagnosis_concept(mention.text)
        if not concept_key or concept_key in seen:
            return
        seen.add(concept_key)
        candidates.append(
            FindCandidate(
                mention=mention,
                candidate_class=candidate_class,
                rule_id=rule_id,
            )
        )

    return candidates, _emit


def expansion_surface_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: expansion-lexicon surfaces and alias decompositions.

    Covers direct-path misses that are purely lexical: surfaces absent
    from the benchmark lexicon and spans whose canonical concept differs
    from the matched surface. Split from the unrestricted class because
    these emissions are precision-safe enough to keep at Select.
    """

    from ..find_ledger import DIAGNOSIS_EXPANSION_SURFACE

    candidates, _emit = _distinct_concept_emitter(
        note_text, DIAGNOSIS_EXPANSION_SURFACE
    )

    for match in _expansion_only_surface_matches(note_text):
        _emit(
            _predicted_diagnosis_from_match(note_text, match)
            or _conceptless_diagnosis_from_match(note_text, match),
            "recognise.diagnosis_expansion_surface",
        )

    for pattern, templates in _ALIAS_DECOMPOSITIONS:
        for match in pattern.finditer(note_text):
            for template in templates:
                _emit(
                    _aliased_diagnosis_mention(
                        note_text, match, match.expand(template)
                    ),
                    "recognise.diagnosis_alias_decomposition",
                )

    return tuple(candidates)


def unrestricted_surface_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: benchmark surfaces with no context gates, plus inference.

    Covers direct-path misses from context exclusions (negation, onset,
    service, narrative) and seizure-type -> syndrome inference. One
    candidate per distinct concept key not already produced by the direct
    path. FP-heavy by design; recall lives at the find stop.
    """

    from ..find_ledger import DIAGNOSIS_UNRESTRICTED_SURFACE

    candidates, _emit = _distinct_concept_emitter(
        note_text, DIAGNOSIS_UNRESTRICTED_SURFACE
    )

    for match in _expanded_surface_matches(note_text):
        _emit(
            _predicted_diagnosis_from_match(note_text, match)
            or _conceptless_diagnosis_from_match(note_text, match),
            "recognise.diagnosis_unrestricted_surface",
        )

    if _EPILEPSY_EVIDENCE_RE.search(note_text):
        for evidence_re, syndrome in (
            (_FOCAL_TYPE_EVIDENCE_RE, "focal epilepsy"),
            (_GENERALISED_TYPE_EVIDENCE_RE, "generalised epilepsy"),
        ):
            evidence_match = evidence_re.search(note_text)
            if evidence_match is not None:
                _emit(
                    _aliased_diagnosis_mention(note_text, evidence_match, syndrome),
                    "recognise.diagnosis_syndrome_inference",
                )

    return tuple(candidates)


def _aliased_diagnosis_mention(
    text: str, match: re.Match[str], concept_text: str
) -> PredictedMention:
    """Mention asserting *concept_text* on the evidence of *match*."""

    concept = _diagnosis_concept_from_phrase(concept_text)
    attrs = {
        "DiagCategory": (
            concept.canonical
            if concept
            else canonicalize_diagnosis_concept(concept_text)
        ),
        "Certainty": "5",
        "Negation": "Affirmed",
    }
    if concept is not None:
        attrs = attach_benchmark_concept(attrs, concept)
    return PredictedMention(
        entity=DIAGNOSIS.name,
        text=concept_text,
        attributes=attrs,
        evidence=_sentence_window(text, match.start(), match.end()),
        evidence_span=match_span(match),
        component_owner=_owner(
            "deterministic_diagnosis_alias",
            RuleGroup.ANCHOR_PHRASE,
            Portability.CLINICAL_EPILEPSY,
        ),
    )


def hierarchy_ancestor_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: hierarchy ancestors of directly recognized concepts.

    A frontal lobe epilepsy mention also asserts focal epilepsy (and
    epilepsy); annotators score those parents as separate inventory units.
    No surface for the ancestor is required.
    """

    from ..find_ledger import DIAGNOSIS_HIERARCHY_ANCESTOR, FindCandidate

    direct_mentions = _extract_diagnoses(note_text)
    direct_concepts = {
        canonicalize_diagnosis_concept(mention.text) for mention in direct_mentions
    }
    seen: set[str] = set(direct_concepts)
    candidates: list[FindCandidate] = []
    for mention in direct_mentions:
        ancestor = DIAGNOSIS_PARENT.get(canonicalize_diagnosis_concept(mention.text))
        while ancestor is not None:
            if ancestor in seen:
                ancestor = DIAGNOSIS_PARENT.get(ancestor)
                continue
            seen.add(ancestor)
            concept = diagnosis_concept(ancestor)
            attrs = {
                "DiagCategory": concept.canonical if concept else ancestor,
                "Certainty": "5",
                "Negation": "Affirmed",
            }
            if concept is not None:
                attrs = attach_benchmark_concept(attrs, concept)
            candidates.append(
                FindCandidate(
                    mention=PredictedMention(
                        entity=DIAGNOSIS.name,
                        text=ancestor,
                        attributes=attrs,
                        evidence=mention.evidence,
                        evidence_span=mention.evidence_span,
                        component_owner=_owner(
                            "deterministic_diagnosis_hierarchy_ancestor",
                            RuleGroup.ANCHOR_PHRASE,
                            Portability.CLINICAL_EPILEPSY,
                        ),
                    ),
                    candidate_class=DIAGNOSIS_HIERARCHY_ANCESTOR,
                    rule_id="recognise.diagnosis_hierarchy_ancestor",
                )
            )
            ancestor = DIAGNOSIS_PARENT.get(ancestor)
    return tuple(candidates)


def component_token_diagnosis_candidates(
    note_text: str,
) -> tuple[FindCandidate, ...]:
    """Recall-first: standalone adjectival tokens inside matched surfaces.

    Annotators sometimes split a compound heading into standalone units
    (``generalised``, ``Focal``, ``Occipital``). Tokens are emitted only
    when they occur inside an expanded-lexicon surface match, one
    candidate per distinct token.
    """

    from ..find_ledger import DIAGNOSIS_COMPONENT_TOKEN, FindCandidate

    direct_concepts = {
        canonicalize_diagnosis_concept(mention.text)
        for mention in _extract_diagnoses(note_text)
    }
    seen: set[str] = set(direct_concepts)
    candidates: list[FindCandidate] = []
    for match in _expanded_surface_matches(note_text):
        for token_match in re.finditer(r"[A-Za-z]+", match.group(1)):
            token = token_match.group(0)
            if token.lower() not in _COMPONENT_TOKENS:
                continue
            concept_key = canonicalize_diagnosis_concept(token)
            if not concept_key or concept_key in seen:
                continue
            seen.add(concept_key)
            start = match.start(1) + token_match.start()
            end = match.start(1) + token_match.end()
            token_span_match = re.compile(
                rf"({re.escape(token)})", re.IGNORECASE
            ).match(note_text, start, end)
            if token_span_match is None:
                continue
            candidates.append(
                FindCandidate(
                    mention=_conceptless_diagnosis_from_match(
                        note_text, token_span_match
                    ),
                    candidate_class=DIAGNOSIS_COMPONENT_TOKEN,
                    rule_id="recognise.diagnosis_component_token",
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
