"""Clinical concept normalization for ExECTv2 scorers and projection helpers."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    ONSET,
    PATIENT_HISTORY,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")
_SEIZURE_TYPE = re.compile(
    r"\b(focal|generalised|generalized|tonic|clonic|myoclonic|absence|partial|"
    r"convulsive|secondary)\b"
)
_NON_EPILEPSY_SEIZURE = re.compile(r"\b(febrile|dissociative|non.?epileptic|psychogenic)\b")
_COMPOUND_SPLIT = re.compile(r"\s+with\s+|\s+and\s+|\s*,\s*")
_PARENTHETICAL = re.compile(r"\([^)]*\)")
_DIAGNOSIS_QUALIFIER_PREFIX = re.compile(
    r"^(?:diagnosis(?:\s+of)?|known|established|confirmed|probable|possibly|"
    r"possible|likely|suspected|query|questionable|\?+)\s+"
)

# SeizureFrequency is kept unsplit for the benchmark-altitude projection because
# the gold anchor can intentionally be a compound phrase carrying one rate.
COMPOUND_ENTITIES: frozenset[str] = frozenset({"Diagnosis", "PatientHistory"})
AFFIRMED_DEFAULT_ENTITIES: frozenset[str] = frozenset(
    {"Diagnosis", "PatientHistory", "EpilepsyCause", "BirthHistory", "Onset", "WhenDiagnosed"}
)
CONCEPT_IDENTITY_ENTITIES: frozenset[str] = frozenset(
    {
        BIRTH_HISTORY.name,
        DIAGNOSIS.name,
        EPILEPSY_CAUSE.name,
        ONSET.name,
        WHEN_DIAGNOSED.name,
    }
)
ASSERTION_ATTRIBUTES: frozenset[str] = frozenset({"Negation", "Certainty"})

_CONCEPT_ALIASES: dict[str, str] = {
    "birth normal": "born normally",
    "born normally": "born normally",
    "born normal": "born normally",
    "jme": "juvenile myoclonic epilepsy",
    "generalized epilepsy": "generalised epilepsy",
    "generalised tonic clonic seizures": "tonic clonic seizures",
    "generalized tonic clonic seizures": "tonic clonic seizures",
}
_DIAGNOSIS_CONCEPT_ALIASES: dict[str, str] = {
    "focal onset epilepsy": "focal epilepsy",
    "genetic generalised epilepsy": "genetic generalised epilepsy",
    "genetic generalized epilepsy": "genetic generalised epilepsy",
    "single focal seizure": "focal seizure",
    "focal seizures without change in awareness": "focal seizures",
    "focal onset seizures": "focal seizures",
    "generalized epilepsy": "generalised epilepsy",
    "epilepsy unclassified": "epilepsy",
    "unclassified epilepsy": "epilepsy",
    "generalized seizures": "generalised seizures",
    "generalised tonic clonic seizure": "tonic clonic seizures",
    "generalised tonic clonic seizures": "tonic clonic seizures",
    "generalized tonic clonic seizure": "tonic clonic seizures",
    "generalized tonic clonic seizures": "tonic clonic seizures",
    "tonic clonic seizure": "tonic clonic seizures",
    "tonic chronic seizures": "tonic clonic seizures",
    "generalised tonic chronic seizures": "tonic clonic seizures",
    "generalized tonic chronic seizures": "tonic clonic seizures",
    "symptomatic structural focal epilepsy": "focal epilepsy",
    "localisation related epilepsy": "focal epilepsy",
    "localization related epilepsy": "focal epilepsy",
    "epilepsy with generalised tonic clonic seizure alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "epilepsy with generalised tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "epilepsy with generalized tonic clonic seizure alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "epilepsy with generalized tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "bilateral convulsive seizure": "focal to bilateral convulsive seizures",
    "bilateral convulsive seizures": "focal to bilateral convulsive seizures",
    "temporal lobe onset focal seizures": "temporal lobe seizure",
    "temporal lobe onset focal seizure": "temporal lobe seizure",
    "temporal focal epilepsy": "temporal lobe epilepsy",
    "general and complex partial seizures": "complex partial seizures",
    "general and complex partial seizure": "complex partial seizures",
    "temporal epilepsy": "temporal lobe epilepsy",
    "epileptic events": "epileptic attack",
    "epileptic event": "epileptic attack",
    "jme": "juvenile myoclonic epilepsy",
}
_PROTECTED_DIAGNOSIS_COMPOUNDS: frozenset[str] = frozenset(
    {
        "focal seizures with altered awareness",
        "focal seizures with impaired awareness",
        "focal impaired awareness seizures",
        "epilepsy with generalised tonic clonic seizures alone",
        "epilepsy with generalised tonic clonic seizure alone",
        "epilepsy with generalised tonic clonic seizures on awakening",
        "general and complex partial seizures",
        "general and complex partial seizure",
    }
)

DIAGNOSIS_PARENT: dict[str, str] = {
    "focal epilepsy": "epilepsy",
    "focal onset epilepsy": "focal epilepsy",
    "temporal lobe epilepsy": "focal epilepsy",
    "symptomatic structural focal epilepsy": "focal epilepsy",
    "generalised epilepsy": "epilepsy",
    "juvenile myoclonic epilepsy": "generalised epilepsy",
}


@dataclass(frozen=True)
class ClinicalConcept:
    """A normalized atomic clinical concept used by recovery scorers."""

    entity: str
    concept: str
    assertion: tuple[tuple[str, str], ...] = ()

    @property
    def concept_key(self) -> Hashable:
        return (self.entity, self.concept)

    @property
    def assertion_key(self) -> Hashable:
        return (self.entity, self.concept, self.assertion)


def canonicalize_concept(text: str) -> str:
    normalized = normalize_phrase(text)
    return _CONCEPT_ALIASES.get(normalized, normalized)


def canonicalize_diagnosis_concept(text: str) -> str:
    """Project a diagnosis phrase to the core clinical fact used for scoring."""

    normalized = normalize_phrase(
        _PARENTHETICAL.sub(" ", str(text)).replace("–", " ").replace("—", " ")
    )
    previous = None
    while normalized and normalized != previous:
        previous = normalized
        normalized = _DIAGNOSIS_QUALIFIER_PREFIX.sub("", normalized).strip()
    normalized = canonicalize_concept(normalized)
    if normalized in _DIAGNOSIS_CONCEPT_ALIASES:
        return _DIAGNOSIS_CONCEPT_ALIASES[normalized]
    if "epilep" in normalized and "generalised" in normalized:
        return "generalised epilepsy"
    if "epilep" in normalized and "generalized" in normalized:
        return "generalised epilepsy"
    return normalized


def split_compound_phrase(text: str, *, entity: str | None = None) -> list[str]:
    """Split a coordinated same-kind phrase into atomic concept phrases."""

    normalized = normalize_phrase(text)
    if entity == DIAGNOSIS.name and normalized in _PROTECTED_DIAGNOSIS_COMPOUNDS:
        return [canonicalize_diagnosis_concept(normalized)]
    if " with " not in normalized and " and " not in normalized and "," not in normalized:
        return [
            canonicalize_diagnosis_concept(normalized)
            if entity == DIAGNOSIS.name
            else canonicalize_concept(normalized)
        ]
    parts = [
        canonicalize_diagnosis_concept(p.strip())
        if entity == DIAGNOSIS.name
        else canonicalize_concept(p.strip())
        for p in _COMPOUND_SPLIT.split(normalized)
        if p.strip()
    ]
    if parts:
        return parts
    return [
        canonicalize_diagnosis_concept(normalized)
        if entity == DIAGNOSIS.name
        else canonicalize_concept(normalized)
    ]


def is_epilepsy_seizure_type(phrase: str) -> bool:
    normalized = normalize_phrase(phrase)
    return (
        bool(_SEIZURE_TYPE.search(normalized))
        and "seizure" in normalized
        and not _NON_EPILEPSY_SEIZURE.search(normalized)
    )


def diagnosis_category_for_concept(concept: str) -> str:
    normalized = canonicalize_concept(concept)
    if is_epilepsy_seizure_type(normalized):
        return "MultipleSeizures"
    if "single seizure" in normalized:
        return "SingleSeizure"
    return "Epilepsy"


def with_text(mention: PredictedMention, text: str) -> PredictedMention:
    return mention.model_copy(update={"text": text})


def diagnosis_copy(mention: PredictedMention, text: str) -> PredictedMention:
    attributes = {k: v for k, v in mention.attributes.items() if k not in {"CUI", "CUIPhrase"}}
    attributes.setdefault("DiagCategory", diagnosis_category_for_concept(text))
    attributes.setdefault("Certainty", "5")
    attributes.setdefault("Negation", "Affirmed")
    return mention.model_copy(
        update={
            "entity": "Diagnosis",
            "text": text,
            "attributes": attributes,
            "component_owner": "benchmark_altitude_entity_norm",
        }
    )


def apply_affirmed_defaults(mention: PredictedMention) -> PredictedMention:
    if mention.entity not in AFFIRMED_DEFAULT_ENTITIES:
        return mention
    attributes = dict(mention.attributes)
    changed = False
    if "Certainty" not in attributes:
        attributes["Certainty"] = "5"
        changed = True
    if "Negation" not in attributes:
        attributes["Negation"] = "Affirmed"
        changed = True
    return mention.model_copy(update={"attributes": attributes}) if changed else mention


def annotation_clinical_concepts(
    entity: str,
    text: str,
    attributes: Mapping[str, str],
) -> tuple[ClinicalConcept, ...]:
    """Emit atomic concept units implied by one annotation or prediction."""

    parts = (
        split_compound_phrase(text, entity=entity)
        if entity in COMPOUND_ENTITIES
        else [canonicalize_concept(text)]
    )
    concepts: list[ClinicalConcept] = []
    for part in parts:
        normalized_attrs = _assertion_attributes(entity, part, attributes)
        if entity in CONCEPT_IDENTITY_ENTITIES:
            concepts.append(ClinicalConcept(entity, part, normalized_attrs))
        if entity in {PATIENT_HISTORY.name, SEIZURE_FREQUENCY.name} and is_epilepsy_seizure_type(
            part
        ):
            concepts.append(
                ClinicalConcept(
                    DIAGNOSIS.name,
                    canonicalize_diagnosis_concept(part),
                    normalized_attrs,
                )
            )
    return tuple(concepts)


def collapse_diagnoses_to_most_specific(
    concepts: Iterable[ClinicalConcept],
) -> tuple[ClinicalConcept, ...]:
    """Drop generic Diagnosis concepts when a descendant is present."""

    by_assertion = Counter((concept.concept, concept.assertion) for concept in concepts)
    present = {concept for concept, _assertion in by_assertion}
    collapsed = Counter({key: 1 for key in by_assertion})
    for concept, assertion in by_assertion:
        if _has_specific_descendant(concept, present):
            collapsed[(concept, assertion)] = 0
    out: list[ClinicalConcept] = []
    for (concept, assertion), count in collapsed.items():
        out.extend(ClinicalConcept(DIAGNOSIS.name, concept, assertion) for _ in range(count))
    return tuple(out)


def collapse_concepts_to_most_specific(
    concepts: Iterable[ClinicalConcept],
) -> tuple[ClinicalConcept, ...]:
    by_entity: dict[str, list[ClinicalConcept]] = {}
    for concept in concepts:
        by_entity.setdefault(concept.entity, []).append(concept)

    collapsed: list[ClinicalConcept] = []
    for entity, entity_concepts in by_entity.items():
        if entity == DIAGNOSIS.name:
            collapsed.extend(collapse_diagnoses_to_most_specific(entity_concepts))
        else:
            collapsed.extend(entity_concepts)
    return tuple(collapsed)


def _assertion_attributes(
    entity: str,
    concept: str,
    attributes: Mapping[str, str],
) -> tuple[tuple[str, str], ...]:
    normalized = {
        key: _normalize_attribute_value(key, value)
        for key, value in attributes.items()
        if key in ASSERTION_ATTRIBUTES
    }
    if entity in AFFIRMED_DEFAULT_ENTITIES or (
        entity == PATIENT_HISTORY.name and is_epilepsy_seizure_type(concept)
    ):
        normalized.setdefault("Certainty", "5")
        normalized.setdefault("Negation", "Affirmed")
    return tuple(sorted(normalized.items()))


def _normalize_attribute_value(key: str, value: str) -> str:
    value = _WHITESPACE.sub(" ", str(value).translate(_QUOTES)).strip()
    if key == "Negation" and value.lower() == "affirmed":
        return "Affirmed"
    if key == "Negation" and value.lower() == "negated":
        return "Negated"
    return value


def concepts_hierarchically_related(first: str, second: str) -> bool:
    """True when two Diagnosis concepts denote the same clinical fact at
    different altitudes -- one is an ancestor/descendant of the other in
    ``DIAGNOSIS_PARENT`` (or they are identical).

    Reuses ``_has_specific_descendant`` so the scoring path's hierarchy-aware
    match and the per-side specificity collapse share one relation definition:
    ``collapse_diagnoses_to_most_specific`` drops a parent when a descendant is
    present on the *same* side, and this predicate lets the match reconcile the
    parent/descendant split that independent per-side collapse leaves across the
    gold and prediction sides.
    """

    if first == second:
        return True
    return _has_specific_descendant(first, {second}) or _has_specific_descendant(second, {first})


def _has_specific_descendant(concept: str, present: set[str]) -> bool:
    return any(_is_descendant(candidate, concept) for candidate in present if candidate != concept)


def _is_descendant(candidate: str, ancestor: str) -> bool:
    current = DIAGNOSIS_PARENT.get(candidate)
    while current is not None:
        if current == ancestor:
            return True
        current = DIAGNOSIS_PARENT.get(current)
    return False
