"""Diagnosis benchmark / CUIPhrase convention dictionary."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, TypeVar

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
    is_diagnosis_descendant,
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

# Same-fact name aliases permitted at the encode stop. The broader convention
# table above also contains clinical concept remaps (for example focal cortical
# dysplasia -> an epilepsy syndrome); those remain selection/revision rules.
DIAGNOSIS_FORMAT_ALIAS_REPAIRS: dict[str, str] = {
    key: value
    for key, value in DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.items()
    if key
    not in {
        "focal cortical dysplasia",
        "focal cortical dysplasia right temporal lobe",
        "right hippocampal sclerosis",
    }
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

DIAGNOSIS_FORMAT_SURFACE_REPAIRS: dict[str, str] = {
    "absence": "absence seizures",
    "complex partial": "complex partial seizures",
    "focal dyscognitive seizure": "dyscognitive seizures",
    "focal epileptic seizure": "focal seizures",
    "focal (occipital lobe) epilepsy": "occipital lobe epilepsy",
    "gtcs": "generalised tonic clonic seizures",
    "nocturnal generalised tonic clonic seizure": ("generalised tonic clonic seizures"),
    "secondarily generalised seizure": "secondary generalised seizures",
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
            r"\bsymptomatic structural(?:\s+focal)?\s+epilepsy\b",
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

_CERTAINTY_POSSIBLE = 1
_CERTAINTY_PROBABLE = 2
_LOBE_SYNDROMES: dict[str, str] = {
    "temporal": "temporal lobe epilepsy",
    "frontal": "frontal lobe epilepsy",
    "parietal": "parietal lobe epilepsy",
    "occipital": "occipital lobe epilepsy",
}
_ETIOLOGY_FOCAL_FORMS: frozenset[str] = frozenset(
    {
        "localisation related epilepsy",
        "localization related epilepsy",
        "symptomatic focal epilepsy",
        "symptomatic structural focal epilepsy",
    }
)
_NAMED_LOBE_SYNDROME = re.compile(
    r"\b(?:left|right|bilateral)?\s*"
    r"(temporal|frontal|parietal|occipital)\s+lobe\s+epilepsy\b"
    r"|\btle\b",
    re.IGNORECASE,
)
_LOBE_ANY = re.compile(
    r"\b(?:left|right|bilateral)?\s*"
    r"(temporal|frontal|parietal|occipital)"
    r"(?:\s+lobe)?(?P<onset>\s+onset)?\b",
    re.IGNORECASE,
)
_PROBABLE_CUE = re.compile(
    r"\b(?:probable|probably|likely|most\s+likely)\b",
    re.IGNORECASE,
)
_POSSIBLE_CUE = re.compile(r"\b(?:possible|possibly)\b|\?", re.IGNORECASE)
_ELABORATION_TAIL = re.compile(
    r"[,;:]?\s*\b(?:namely|i\.e\.|ie|that is(?:\s+to\s+say)?)\b.*$",
    re.IGNORECASE,
)
_LATERAL_FOCAL = re.compile(
    r"(?<!structural\s)\bfocal(?:\s+onset)?\s+epilepsy\b|"
    r"\b(?:possible|possibly|probable|probably|likely|most\s+likely)\s+"
    r"focal(?:\s+onset)?\b(?!\s+seizure)",
    re.IGNORECASE,
)
_LATERAL_GENERALISED = re.compile(
    r"\bgenerali[sz]ed\s+epilepsy\b|"
    r"\b(?:possible|possibly|probable|probably|likely|most\s+likely)\s+"
    r"generali[sz]ed\b(?!\s+(?:tonic|clonic|seizure|convuls))",
    re.IGNORECASE,
)
_FOCAL_DIAGNOSIS_CLASS = re.compile(
    r"\bfocal(?:\s+onset)?\s+epilepsy\b|"
    r"\b(?:probable|probably|possible|possibly)\s+focal(?:\s+onset)?\b",
    re.IGNORECASE,
)
_INVESTIGATION_CUE = re.compile(r"\b(?:mri|eeg|ct|imaging|scan)\b", re.IGNORECASE)
_DIAGNOSIS_CONTEXT_CUE = re.compile(
    r"\b(?:diagnos|epilepsy|syndrome|impression|seizure)\b",
    re.IGNORECASE,
)


def _local_specificity_blob(text: str, evidence: str) -> str:
    evidence_core = _ELABORATION_TAIL.sub("", evidence)
    return " ".join(part for part in (text, evidence_core) if part)


def _certainty_rank(blob: str) -> int:
    if _PROBABLE_CUE.search(blob):
        return _CERTAINTY_PROBABLE
    if _POSSIBLE_CUE.search(blob):
        return _CERTAINTY_POSSIBLE
    return 3


def _laterality_from_blob(blob: str) -> str | None:
    has_focal = _LATERAL_FOCAL.search(blob) is not None
    has_generalised = _LATERAL_GENERALISED.search(blob) is not None
    if has_focal and has_generalised:
        return None
    if has_focal:
        return "focal epilepsy"
    if has_generalised:
        return "generalised epilepsy"
    return None


def _lobe_from_blob(blob: str, *, certainty: int) -> str | None:
    named = _NAMED_LOBE_SYNDROME.search(blob)
    if named is not None:
        if named.group(0).lower() == "tle":
            return "temporal lobe epilepsy"
        return _LOBE_SYNDROMES[named.group(1).lower()]
    modifiers: list[str] = []
    onsets: list[str] = []
    for match in _LOBE_ANY.finditer(blob):
        lobe = match.group(1).lower()
        if match.group("onset"):
            onsets.append(lobe)
        else:
            modifiers.append(lobe)
    if modifiers:
        return _LOBE_SYNDROMES[modifiers[0]]
    if onsets and certainty >= _CERTAINTY_PROBABLE:
        return _LOBE_SYNDROMES[onsets[0]]
    return None


def _may_overwrite_diagnosis(mention: str, target: str) -> bool:
    mention_concept = canonicalize_diagnosis_concept(mention)
    target_concept = canonicalize_diagnosis_concept(target)
    if mention_concept == target_concept:
        return False
    if is_diagnosis_descendant(mention_concept, target_concept):
        return False
    if is_diagnosis_descendant(target_concept, mention_concept):
        return True
    if mention_concept in _ETIOLOGY_FOCAL_FORMS and is_diagnosis_descendant(
        target_concept, "focal epilepsy"
    ):
        return True
    named_lobe = _lobe_from_blob(mention, certainty=_CERTAINTY_PROBABLE)
    return named_lobe is not None and named_lobe == target_concept


def diagnosis_select_specificity_target(text: str, evidence: str) -> str | None:
    """Rewrite a kept Diagnosis to a more specific closed name.

    Catalogue rule ``selection.diagnosis_specificity_hierarchy`` (select
    authority, ``llm_select`` rewrite): a probable anatomical modifier, or a
    possible laterality class, may overwrite a less specific epilepsy mention
    on the same branch. Laterality classifies the epilepsy, not a seizure-type
    adjective. Elaborating ``namely`` / ``i.e.`` clauses do not overwrite.
    Possible or queried onset does not create a lobe syndrome. A generalised
    mention is not overwritten by a temporal sibling. A named lobe wins over a
    same-branch etiology form.
    """

    blob = _local_specificity_blob(text, evidence)
    if _INVESTIGATION_CUE.search(blob) and not _DIAGNOSIS_CONTEXT_CUE.search(blob):
        return None
    certainty = _certainty_rank(blob)
    target = None
    lobe = _lobe_from_blob(blob, certainty=certainty)
    if lobe is not None and certainty >= _CERTAINTY_PROBABLE:
        target = lobe
    if target is None:
        laterality = _laterality_from_blob(blob)
        if laterality is not None and certainty >= _CERTAINTY_POSSIBLE:
            target = laterality
    if target is None or not _may_overwrite_diagnosis(text, target):
        return None
    return target


def diagnosis_convention_surface_alias_target(text: str, evidence: str) -> str | None:
    """Return a live surface/alias convention repair, or ``None`` if unchanged.

    Catalogue rules ``diagnosis_surface_spelling_alias`` (dialect or rewrite,
    ``llm_select``) and ``diagnosis_concept_remap_from_evidence`` (rewrite,
    ``llm_select``): spelling, alias, and closed-name rewrites toward benchmark
    wording, including evidence-bound concept remaps such as intractable
    epilepsy and focal-onset normalisation. Excludes select-authority
    specificity hierarchy overwrites; :func:`diagnosis_format_target` replays
    the same-fact encode subset at encode-replay.
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


def diagnosis_convention_target(text: str, evidence: str) -> str | None:
    """Return the convention-repaired Diagnosis text, or ``None`` if unchanged.

    Composes :func:`diagnosis_select_specificity_target` then
    :func:`diagnosis_convention_surface_alias_target` in that order.
    """

    specific = diagnosis_select_specificity_target(text, evidence)
    if specific is not None:
        return specific
    return diagnosis_convention_surface_alias_target(text, evidence)


def diagnosis_format_target(
    text: str,
    evidence: str,
    *,
    diag_category: str | None = None,
) -> str | None:
    """Return a closed standard name for the same extracted Diagnosis fact.

    This is the encode-only subset of :func:`diagnosis_convention_target`.
    It may repair spelling, abbreviations, word order, and benchmark name
    altitude already stated on the mention's own row. It deliberately excludes
    cause/finding-to-syndrome remaps, which remain semantic revision.
    """

    surface = normalize_phrase(text.replace("–", " ").replace("—", " ").replace("-", " "))
    if surface == "secondarily generalised seizure" and (
        diag_category == "SingleSeizure"
        or re.search(r"\bonly\b[^.\n]{0,30}\bone\b", evidence, re.IGNORECASE)
    ):
        return None
    structural_lobe = re.search(
        r"\bsymptomatic structural (temporal|frontal|parietal|occipital) lobe epilepsy\b",
        surface,
        re.IGNORECASE,
    )
    if structural_lobe is not None:
        return f"{structural_lobe.group(1).lower()} lobe epilepsy"
    if " with occasional secondary generalisation" in surface:
        return re.sub(
            r"\bwith\s+occasional\s+secondary\s+generalisation\b",
            "with secondary generalisation",
            text,
            flags=re.IGNORECASE,
        )
    if surface == "focal" and _FOCAL_DIAGNOSIS_CLASS.search(evidence):
        return "focal epilepsy"
    surface_target = DIAGNOSIS_FORMAT_SURFACE_REPAIRS.get(
        surface
    ) or DIAGNOSIS_SURFACE_CONVENTION_REPAIRS.get(surface)
    if surface_target is not None:
        return surface_target
    for pattern, target in _PREFIX_DIAGNOSIS_CONVENTION_REPAIRS:
        if pattern.search(text):
            return target
    concept = canonicalize_diagnosis_concept(text)
    return DIAGNOSIS_FORMAT_ALIAS_REPAIRS.get(concept)


def diagnosis_convention_category(text: str) -> str:
    """Gold-scheme DiagCategory for a kept or rewritten diagnosis phrase."""

    surface = " ".join(text.replace("-", " ").replace("—", " ").replace("–", " ").lower().split())
    surface = surface.replace("generalized", "generalised")
    if surface in DIAGNOSIS_SINGLE_SEIZURE_SURFACES:
        return "SingleSeizure"
    return diagnosis_category_for_concept(text)


def diagnosis_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> dict[str, str]:
    """Return benchmark-format assertion repairs for a convention-rewritten diagnosis."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    current = repaired.get("DiagCategory")
    if current not in {"MultipleSeizures", "SingleSeizure"}:
        repaired["DiagCategory"] = diagnosis_convention_category(text)
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
SYNDROME_OWNED_PHENOTYPES: dict[str, frozenset[str]] = {
    _JME_SYNDROME: frozenset(
        {
            "absence",
            "absence like seizures",
            "absence seizure",
            "absence seizures",
            "absences",
            "typical absence",
            "typical absences",
            "myoclonic jerk",
            "myoclonic jerks",
            "myoclonus",
        }
    )
}


def owned_heading_phenotypes(concepts: set[str]) -> set[str]:
    """Return phenotypes already owned by a selected named syndrome."""

    owned: set[str] = set()
    for concept in concepts:
        owned.update(SYNDROME_OWNED_PHENOTYPES.get(concept, ()))
    return owned


def _finding_text(item: Any) -> str:
    if isinstance(item, Mapping):
        return str(item.get("text") or "")
    return str(getattr(item, "text", "") or "")


def drop_syndrome_covered_phenotypes(findings: Sequence[_Finding]) -> list[_Finding]:
    """Drop phenotypes already owned by a selected named syndrome."""

    concepts = {canonicalize_diagnosis_concept(_finding_text(item)) for item in findings}
    owned = owned_heading_phenotypes(concepts)
    if not owned:
        return list(findings)
    return [
        item
        for item in findings
        if canonicalize_diagnosis_concept(_finding_text(item)) not in owned
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
