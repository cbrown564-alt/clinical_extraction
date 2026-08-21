"""Diagnosis benchmark / CUIPhrase convention dictionary."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, TypeVar

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
)

DIAGNOSIS_STANDALONE_NOISE: frozenset[str] = frozenset(
    {
        "absence",
        "absence like seizures",
        "absence seizure",
        "absence seizures",
        "absences",
        "convulsive seizures",
        "convulsive seizure",
        "dissociative seizures",
        "jerk",
        "jerks",
        "learning difficulties",
        "multiple seizures",
        "myoclonic jerk",
        "myoclonic jerks",
        "myoclonus",
        "nonepileptic events",
        "seizures",
        "single seizure",
    }
)

DIAGNOSIS_CONVENTION_ALIAS_REPAIRS: dict[str, str] = {
    "drug refractory focal epilepsy": "drug refractory epilepsy",
    "drug resistant focal epilepsy": "drug resistant epilepsy",
    "epilepsy with tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "focal cortical dysplasia": "symptomatic structural focal epilepsy",
    "focal cortical dysplasia right temporal lobe": "symptomatic structural focal epilepsy",
    "focal dyscognitive seizures": "dyscognitive seizures",
    "focal frontal lobe seizure": "frontal lobe seizures",
    "focal frontal lobe seizures": "frontal lobe seizures",
    "focal to bilateral seizure": "focal to bilateral convulsive seizures",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "grand mal seizure": "grand mal",
    "right hippocampal sclerosis": "temporal lobe epilepsy",
    "secondarily generalised seizures": "secondary generalised seizures",
    "tonic clonic seizures alone": "epilepsy with generalised tonic clonic seizures alone",
}

DIAGNOSIS_SURFACE_CONVENTION_REPAIRS: dict[str, str] = {
    "epilepsy due to perinatal insult": "epilepsy",
    "epilepsy probable focal": "focal epilepsy",
    "epilepsy probable focal onset": "focal epilepsy",
    "focal epilepsy probable temporal": "focal epilepsy",
    "epilepsy with generalised tonic chronic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "focal onset": "focal epilepsy",
    "focal seizures left arm movement": "focal seizures",
    "generalised epilepsy with tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "generalised tonic chronic seizure": "generalised tonic clonic seizure",
    "generalised tonic chronic seizures": "generalised tonic clonic seizures",
    "generalised tonic clonic seizures alone": "generalised tonic clonic seizures",
    "epilepsy with generalised tonic clonic seizure alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "left temporal lobe epilepsy": "temporal lobe epilepsy",
    "possibly generalised epilepsy": "generalised epilepsy",
    "refractory focal epilepsy": "refractory epilepsies",
    "temporal lobe": "temporal lobe epilepsy",
    "tle": "temporal lobe epilepsy",
    "unclassified epilepsy": "epilepsy",
}

DIAGNOSIS_RESIDUAL_CONVENTION_NOISE: frozenset[str] = frozenset(
    {
        "anxiety",
        "anxiety and depression",
        "absence events",
        "complex partial",
        "chronic migraine",
        "depression",
        "dissociative seizure",
        "dissociative seizures",
        "drop attacks",
        "drops",
        "focal",
        "focal onset",
        "frontal lobe brain tumour",
        "general seizures",
        "generalised",
        "gtcs",
        "hydrocephalus",
        "learning difficulties",
        "left frontal cortical dysplasia",
        "left frontal lobe focal cortical dysplasia",
        "longstanding epilepsy",
        "migraine",
        "episodic migraine",
        "minor seizures",
        "neurocysticercosis",
        "nocturnal generalised tonic clonic seizures",
        "nocturnal seizures",
        "occasional secondary generalisation",
        "parietal onset",
        "right temporal lobe onset",
        "right mca infarct",
        "seizure",
        "single epileptic seizure",
        "staring episodes",
        "syncope",
        "temporal",
        "temporal lobe",
        "tle",
        "tuberous sclerosis",
        "unwitnessed blackouts",
    }
)

DIAGNOSIS_SINGLE_SEIZURE_SURFACES: frozenset[str] = frozenset(
    {
        "convulsive seizure",
        "focal seizure",
        "generalised tonic clonic seizure",
        "tonic clonic seizure",
    }
)

_WEAK_GENERIC_EPILEPSY_CONTEXT = re.compile(
    r"epilepsy (?:service|specialist|nurse|clinic|medication)|"
    r"driving with epilepsy|improved (?:his|her) epilepsy|"
    r"epilepsy history|history of epilepsy|anti epileptic",
    re.IGNORECASE,
)
_STRONG_GENERIC_EPILEPSY_CONTEXT = re.compile(
    r"\b(?:diagnosis|impression|has|diagnosed|known)\b.{0,80}\bepilep",
    re.IGNORECASE,
)
_SECONDARY_GENERALISED_EVIDENCE = re.compile(
    r"secondar(?:y|ily) generali[sz]|secondary generalisation|focal to bilateral",
    re.IGNORECASE,
)
_GENERAL_AND_COMPLEX_PARTIAL_EVIDENCE = re.compile(
    r"\bgeneral and complex partial seizures\b",
    re.IGNORECASE,
)
_DIAGNOSIS_FAMILY_CONTEXT = re.compile(
    r"\b(?:family history|paternal|maternal|father|mother|brother|sister|aunt|"
    r"uncle|cousin)\b",
    re.IGNORECASE,
)
_PREFIX_DIAGNOSIS_CONVENTION_REPAIRS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\bsymptomatic structural (?:frontal lobe |temporal lobe )?epilepsy\b",
            re.IGNORECASE,
        ),
        "symptomatic structural focal epilepsy",
    ),
    (
        re.compile(r"\blocali[sz]ation related epilepsy\b", re.IGNORECASE),
        "localisation related epilepsy",
    ),
    (re.compile(r"\bfocal onset epilepsy\b", re.IGNORECASE), "focal epilepsy"),
    (re.compile(r"\bepilepsy\s*[-–]\s*focal onset\b", re.IGNORECASE), "focal epilepsy"),
    (re.compile(r"\bepilepsy,\s*probable focal onset\b", re.IGNORECASE), "focal epilepsy"),
    (re.compile(r"\bepilepsy unclassified\b", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bchildhood onset epilepsy\b", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bgenetic epilepsy\b", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bsevere epilepsy\b", re.IGNORECASE), "epilepsy"),
)
_MINOR_SEIZURES_CONTEXTUAL_NOISE = re.compile(
    r"\bminor seizures\b",
    re.IGNORECASE,
)
_RESIDUAL_GENERIC_EPILEPSY_NOISE = re.compile(
    r"epilepsy in general|history of epilepsy|epilepsy protocol|father has a history|"
    r"epilepsy point|epilepsy service|epilepsy helpline|improve his seizures|"
    r"contraindication",
    re.IGNORECASE,
)

#: dev-derived source-phrase -> benchmark concept additions (``benchmark_format``).
_PATIENT_ABSENCE_SEIZURES = re.compile(
    r"\b(?:the patient|patient|she|he|[A-Z][a-z]+)\s+"
    r"(?:started having|continues to have)\s+absence seizures\b",
    re.IGNORECASE,
)

RESIDUAL_SOURCE_CONCEPT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"Diagnosis:\s*focal onset epilepsy \(occipital\)", re.IGNORECASE),
        "occipital lobe epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*focal epilepsy, probable parietal onset", re.IGNORECASE),
        "parietal lobe epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*symptomatic structural frontal lobe epilepsy", re.IGNORECASE),
        "frontal lobe epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*Epilepsy,\s*probable focal onset", re.IGNORECASE),
        "focal epilepsy",
    ),
    (
        re.compile(r"Diagnosis:\s*epilepsy\s*[-–]\s*probable\s+focal\b", re.IGNORECASE),
        "focal epilepsy",
    ),
    (
        re.compile(
            r"Diagnosis:\s*focal epilepsy\s*[-–]\s*Probable\s+temporal\b",
            re.IGNORECASE,
        ),
        "temporal lobe epilepsy",
    ),
    (
        re.compile(r"seizures every 3 to 4 weeks,\s*possibly focal onset", re.IGNORECASE),
        "focal epilepsy",
    ),
    (
        re.compile(r"Focal epilepsy \? right temporal lobe onset", re.IGNORECASE),
        "temporal lobe onset seizure",
    ),
    (re.compile(r"Drug refractory focal epilepsy", re.IGNORECASE), "drug refractory epilepsy"),
    (
        re.compile(r"nocturnal generalised tonic clonic seizures", re.IGNORECASE),
        "nocturnal seizures",
    ),
    (
        re.compile(r"Symptomatic epilepsy presenting with\s*focal motor seizures", re.IGNORECASE),
        "focal motor seizures",
    ),
    (re.compile(r"tonic clonic convulsion", re.IGNORECASE), "tonic clonic convulsion"),
    (re.compile(r"focal, frontal lobe onset", re.IGNORECASE), "frontal lobe onset seizure"),
    (
        re.compile(r"generalised tonic clonic seizures probably with a focal onset", re.IGNORECASE),
        "focal seizures",
    ),
    (
        re.compile(
            r"New diagnosis of epilepsy with generalised tonic clonic seizures from sleep",
            re.IGNORECASE,
        ),
        "focal seizures",
    ),
    (re.compile(r"Focal frontal lobe seizures consist", re.IGNORECASE), "focal seizures"),
    (
        re.compile(r"diagnosis of epilepsy[^.]{0,80}causes seizures", re.IGNORECASE),
        "focal seizures",
    ),
    (
        re.compile(
            r"Diagnosis:\s*longstanding epilepsy with generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Diagnosis:\s*Longstanding epilepsy, myoclonic jerks and "
            r"generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Complex partial seizures with secondary generalised tonic clonic seizures",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Symptomatic epilepsy with generalised tonic clonic seizures "
            r"with right temporal meningioma",
            re.IGNORECASE,
        ),
        "generalised",
    ),
    (
        re.compile(
            r"Symptomatic epilepsy with generalised tonic clonic seizures "
            r"with right temporal meningioma",
            re.IGNORECASE,
        ),
        "symptomatic",
    ),
    (
        re.compile(
            r"complex partial seizures.*secondary generalised seizures", re.IGNORECASE | re.DOTALL
        ),
        "secondary",
    ),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "secondary"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "focal"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "drug"),
    (re.compile(r"drug refractory focal \(occipital lobe\) epilepsy", re.IGNORECASE), "occipital"),
    (re.compile(r"diagnosed with epilepsy at the age of 22", re.IGNORECASE), "focal"),
    (
        re.compile(
            r"Seizure type and frequency:\s*focal seizures with altered awareness", re.IGNORECASE
        ),
        "focal",
    ),
    (re.compile(r"Probable Complex Partial Seizures - \?TLE", re.IGNORECASE), "temporal"),
    (re.compile(r"typical absences", re.IGNORECASE), "typical absences"),
    (re.compile(r"Previous episode of status epilepticus", re.IGNORECASE), "status epilepticus"),
    (
        re.compile(r"Her generalised seizures come without any warning", re.IGNORECASE),
        "generalised seizures",
    ),
    (re.compile(r"Drug refactory focal epilepsy", re.IGNORECASE), "drug refractory epilepsies"),
    (re.compile(r"Diagnosis:\s*epilepsy\s*[-–]\s*unclassified", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bepilepsy unclassified\b", re.IGNORECASE), "epilepsy"),
    (
        re.compile(
            r"\b(?:Diagnosis:\s*(?:Genetic|Severe)\s+epilepsy|"
            r"Problem\s+Epilepsy|most\s+likely\s+diagnosis\s+is\s+epilepsy|"
            r"(?:His|Her)\s+epilepsy\s+(?:was\s+well\s+controlled|started))\b",
            re.IGNORECASE,
        ),
        "epilepsy",
    ),
    (re.compile(r"\bdiagnosed with epilepsy\b", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bdiagnosis of epilepsy\b", re.IGNORECASE), "epilepsy"),
    (re.compile(r"\bprimary generalised epilepsy\b", re.IGNORECASE), "generalised epilepsy"),
    (re.compile(r"\btemporal lobe epilepsy\b", re.IGNORECASE), "temporal lobe epilepsy"),
    (re.compile(r"\bjuvenile myoclonic epilepsy\b", re.IGNORECASE), "juvenile myoclonic epilepsy"),
    (
        re.compile(
            r"\bpossible JME\b|\bpossible juvenile myoclonic epilepsy\b",
            re.IGNORECASE,
        ),
        "juvenile myoclonic epilepsy",
    ),
    (
        re.compile(
            r"\bgeneralised tonic clonic seizures with myoclonic jerks,\s*possible JME\b",
            re.IGNORECASE,
        ),
        "juvenile myoclonic epilepsy",
    ),
    (
        re.compile(r"\bsymptomatic structural focal epilepsy\b", re.IGNORECASE),
        "symptomatic structural focal epilepsy",
    ),
    (re.compile(r"\bfocal epilepsy\b", re.IGNORECASE), "focal epilepsy"),
    (
        re.compile(r"\bfocal seizures with altered awareness\b", re.IGNORECASE),
        "focal seizures with altered awareness",
    ),
    (re.compile(r"\bfocal motor seizures?\b", re.IGNORECASE), "focal motor seizures"),
    (
        re.compile(r"\bsecondary generalised seizures?\b", re.IGNORECASE),
        "secondary generalised seizures",
    ),
    (
        re.compile(r"\bsecondarily generalised seizures?\b", re.IGNORECASE),
        "secondary generalised seizures",
    ),
    (
        re.compile(r"\bfocal to bilateral convulsive seizures?\b", re.IGNORECASE),
        "focal to bilateral convulsive seizures",
    ),
    (
        re.compile(r"\bbilateral convulsive seizures?\b", re.IGNORECASE),
        "focal to bilateral convulsive seizures",
    ),
    (
        re.compile(
            r"(?:Diagnosis|Seizure type(?: and frequency)?):[^\n]{0,180}"
            r"\bgenerali[sz]ed tonic clonic seizures?\b",
            re.IGNORECASE,
        ),
        "generalised tonic clonic seizures",
    ),
    (
        re.compile(
            r"\bHistory is consistent with generalised tonic clonic seizures\b",
            re.IGNORECASE,
        ),
        "generalised tonic clonic seizures",
    ),
    (re.compile(r"\bcomplex partial seizures\b", re.IGNORECASE), "complex partial seizures"),
)
_RESOLUTION_CANDIDATE_SOURCE_CONCEPT_PATTERNS: tuple[
    tuple[re.Pattern[str], str], ...
] = ((_PATIENT_ABSENCE_SEIZURES, "absence seizures"),)


def diagnosis_convention_target(text: str, evidence: str) -> str | None:
    """Return the convention-repaired Diagnosis text, or ``None`` if unchanged.

    Combines the v04 concept-keyed alias repairs with the v05 concept+evidence
    residual benchmark rewrites, in the same precedence the lenses applied
    (alias repair first, then residual benchmark).
    """

    surface = normalize_phrase(text.replace("–", " ").replace("—", " ").replace("-", " "))
    if surface == "epilepsy" and re.search(r"\bintractable epilepsy\b", evidence, re.IGNORECASE):
        return "intractable epilepsy"
    surface_target = DIAGNOSIS_SURFACE_CONVENTION_REPAIRS.get(surface)
    if surface_target is not None:
        return surface_target
    for pattern, target in _PREFIX_DIAGNOSIS_CONVENTION_REPAIRS:
        if pattern.search(" ".join(part for part in (text, evidence) if part)):
            return target

    concept = canonicalize_diagnosis_concept(text)
    return DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.get(concept)


def diagnosis_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> dict[str, str]:
    """Return benchmark-format assertion repairs for a convention-rewritten diagnosis."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    repaired["DiagCategory"] = (
        "SingleSeizure"
        if normalize_phrase(text) in DIAGNOSIS_SINGLE_SEIZURE_SURFACES
        else diagnosis_category_for_concept(text)
    )
    concept = canonicalize_diagnosis_concept(text)
    if concept == "epilepsy" and re.search(
        r"Diagnosis:\s*Epilepsy\s*[-–]\s*unclassified", evidence, re.IGNORECASE
    ):
        repaired["Certainty"] = "5"
        repaired["Negation"] = "Affirmed"
    if concept == "epilepsy" and re.search(
        r"\b(?:epilepsy due to perinatal insult|symptomatic structural focal epilepsy)\b",
        evidence,
        re.IGNORECASE,
    ):
        repaired["Certainty"] = "5"
        repaired["Negation"] = "Affirmed"
    if concept == "generalised epilepsy" and re.search(
        r"\bpossibly generalised\b|\bpossible generalised\b", evidence, re.IGNORECASE
    ):
        repaired["Certainty"] = "3"
        repaired["Negation"] = "Affirmed"
    if concept == "tonic clonic seizures" and re.search(
        r"\bdiagnosis\s*:\s*generalised tonic clonic seizures\b", evidence, re.IGNORECASE
    ):
        repaired["Certainty"] = "5"
        repaired["Negation"] = "Affirmed"
    return repaired


_Finding = TypeVar("_Finding")

_JME_SYNDROME = "juvenile myoclonic epilepsy"
_JME_COVERED_PHENOTYPES = frozenset(
    {
        "absence",
        "absence like seizures",
        "absence seizure",
        "absence seizures",
        "absences",
        "myoclonic jerk",
        "myoclonic jerks",
        "myoclonus",
    }
)


def _finding_text(item: Any) -> str:
    if isinstance(item, Mapping):
        return str(item.get("text") or "")
    return str(getattr(item, "text", "") or "")


def drop_syndrome_covered_phenotypes(findings: Sequence[_Finding]) -> list[_Finding]:
    """Drop jerk/absence Diagnosis siblings when JME is already emitted."""

    concepts = {canonicalize_diagnosis_concept(_finding_text(item)) for item in findings}
    if _JME_SYNDROME not in concepts:
        return list(findings)
    return [
        item
        for item in findings
        if canonicalize_diagnosis_concept(_finding_text(item)) not in _JME_COVERED_PHENOTYPES
    ]


def is_diagnosis_convention_noise(
    text: str,
    *,
    evidence: str,
    diag_category: str | None,
) -> bool:
    """True if this Diagnosis should be dropped as convention/benchmark noise.

    Unifies the v03 standalone/weak-generic cleanup, the v04 residual convention
    noise, and the v05 residual benchmark noise drops. Evaluate *after*
    ``diagnosis_convention_target`` has been applied (the lenses dropped on the
    rewritten finding).
    """

    concept = canonicalize_diagnosis_concept(text)
    normalized_text = normalize_phrase(text)

    # v03: standalone symptom / non-diagnostic terms unless tagged Epilepsy.
    if (
        concept in DIAGNOSIS_STANDALONE_NOISE or normalized_text in DIAGNOSIS_STANDALONE_NOISE
    ) and diag_category != "Epilepsy":
        return True

    # v04: residual convention noise concepts.
    if concept in DIAGNOSIS_RESIDUAL_CONVENTION_NOISE:
        return True

    # v05: secondary-generalised tonic clonic noise + residual generic epilepsy.
    if concept == "tonic clonic seizures" and _SECONDARY_GENERALISED_EVIDENCE.search(evidence):
        return True
    if concept == "epilepsy" and _RESIDUAL_GENERIC_EPILEPSY_NOISE.search(evidence):
        return True
    if concept == "general seizures" and _GENERAL_AND_COMPLEX_PARTIAL_EVIDENCE.search(evidence):
        return True
    if concept == "minor seizures" and _MINOR_SEIZURES_CONTEXTUAL_NOISE.search(evidence):
        return True
    if re.search(
        r"\b(?:non[- ]?epileptic psychogenic seizures?|febrile seizures?)\b",
        concept,
        re.IGNORECASE,
    ):
        return True
    if (
        diagnosis_category_for_concept(text) == "Epilepsy"
        and _DIAGNOSIS_FAMILY_CONTEXT.search(evidence)
        and not re.search(
            r"\bpatient\b|\bthis (?:man|woman|lady|gentleman)\b",
            evidence,
            re.IGNORECASE,
        )
    ):
        return True

    # v03: weak generic-epilepsy context without a strong diagnostic assertion.
    if concept == "epilepsy":
        return bool(_WEAK_GENERIC_EPILEPSY_CONTEXT.search(evidence)) and not bool(
            _STRONG_GENERIC_EPILEPSY_CONTEXT.search(evidence)
        )
    return False


def diagnosis_residual_additions(
    note_text: str, *, include_resolution_candidate: bool = False
) -> list[tuple[str, str]]:
    """Return dev-derived ``(concept_text, evidence)`` additions for a letter.

    De-duplicated by canonical concept, matching the v05 lens behaviour. The
    caller is responsible for skipping concepts already present.
    """

    added: list[tuple[str, str]] = []
    seen: set[str] = set()
    patterns = RESIDUAL_SOURCE_CONCEPT_PATTERNS
    if include_resolution_candidate:
        patterns = (*_RESOLUTION_CANDIDATE_SOURCE_CONCEPT_PATTERNS, *patterns)
    for pattern, text in patterns:
        match = pattern.search(note_text)
        if match is None:
            continue
        concept = canonicalize_diagnosis_concept(text)
        if concept in seen:
            continue
        seen.add(concept)
        added.append((text, match.group(0)))
    return added


def diagnosis_residual_addition_category(text: str, evidence: str) -> str:
    """Return the declared rule category for one source-bound addition."""

    if (
        canonicalize_diagnosis_concept(text) == "absence seizures"
        and _PATIENT_ABSENCE_SEIZURES.search(evidence)
    ):
        return "clinical_epilepsy"
    return "benchmark_format"


def is_redundant_diagnosis_residual_addition(
    text: str,
    *,
    evidence: str,
    selected_texts: Sequence[str],
    include_resolution_candidate: bool = False,
) -> bool:
    """True when a dev residual fragment is already covered by a specific concept."""

    concept = canonicalize_diagnosis_concept(text)
    if concept == "tonic clonic seizures" and _SECONDARY_GENERALISED_EVIDENCE.search(evidence):
        return True
    selected = {canonicalize_diagnosis_concept(item) for item in selected_texts}
    if include_resolution_candidate and concept == "generalised epilepsy":
        return any(
            item != concept and item.endswith("generalised epilepsy") for item in selected
        )
    if concept == "focal":
        return concept in selected
    if concept == "generalised":
        return concept in selected
    if concept == "secondary":
        return concept in selected
    if concept == "focal seizures with altered awareness" and "dyscognitive seizures" in selected:
        return True
    return False
