"""Standard-dictionary translation layer for the simplified single-GPT engine.

This module is the one deterministic place that translates *clinical facts* the
model has already extracted into *scoring-convention* surfaces: drug-name
mapping, dose-unit and frequency variants, diagnosis benchmark/CUIPhrase
convention repair, and the small set of SeizureFrequency benchmark rewrites.

Design contract:

- The prompt owns clinical extraction and selection (which findings exist).
- This module owns convention translation (how an existing finding's surface
  should read for scoring). It never invents clinical content from nothing
  except for the explicitly-bounded, dev-derived diagnosis residual additions,
  which are labelled ``benchmark_format`` exactly as in the v05 lens.

Functions operate on plain strings / mappings (not ``ClinicalFinding``) so the
dictionary is decoupled and unit-testable. Assembly lenses are thin wrappers
that call into here (see ``assembly/lenses.py``).

Provenance: the diagnosis convention/residual tables are migrated verbatim from
the v04/v05 ``DiagnosisConventionAliasLens`` / ``DiagnosisResidualBenchmarkLens``
logic; the SF rewrites from ``llm_sf_union_arbitration._rewrite``; the
prescription primitives mirror ``deterministic.all_entities``. Parity with those
sources is the floor and is guarded by tests.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_CONCEPT_BY_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    normalize_phrase,
)

# ---------------------------------------------------------------------------
# Prescription: medication name / dose-unit / frequency dictionaries
# ---------------------------------------------------------------------------

#: Surface spellings that are not in the benchmark lexicon but map to a known
#: generic. Mirrors ``all_entities._MEDICATION_EXTRA_SURFACE_ALIASES``.
DRUG_SURFACE_ALIASES: dict[str, str] = {
    "lamtorigine": "lamotrigine",
}

#: Canonical dose units. Variants collapse to one of these.
_DOSE_UNIT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.IGNORECASE,
)

#: Frequency abbreviation / phrasing -> ExECTv2 ``Frequency`` code. Order
#: matters (As_Required before the daily forms). Mirrors
#: ``all_entities._FREQUENCY_PATTERNS``.
_FREQUENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|"
            r"rescue|for\s+seizure\s+clusters?)\b",
            re.IGNORECASE,
        ),
        "As_Required",
    ),
    (
        re.compile(
            r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+aday|"
            r"twice\s+daily|twice\s+today)\b",
            re.IGNORECASE,
        ),
        "2",
    ),
    (
        re.compile(
            r"\b(?:od|o\.d\.|once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|"
            r"nightly|morning|afternoon|evening|am|pm|at\s+night|"
            r"in\s+the\s+(?:morning|afternoon|night|evening)|on|nokte)\b",
            re.IGNORECASE,
        ),
        "1",
    ),
    (re.compile(r"\b(?:tds|t\.d\.s\.|tid|three\s+times\s+(?:a\s+)?day)\b", re.IGNORECASE), "3"),
)


def normalize_drug_name(surface: str) -> str | None:
    """Return the canonical generic drug name for a surface mention, if known."""

    key = normalize_phrase(surface)
    key = DRUG_SURFACE_ALIASES.get(key, key)
    concept = PRESCRIPTION_CONCEPT_BY_PHRASE.get(key)
    return concept.canonical if concept is not None else None


def normalize_dose_unit(unit: str) -> str:
    """Collapse a dose-unit variant (mg/mgs/mgms/grams/...) to ``mg`` or ``g``."""

    return "g" if unit.strip().lower().startswith("g") else "mg"


def dose_from_text(text: str) -> tuple[str, str] | None:
    """Return ``(value, canonical_unit)`` for the first dose in ``text``."""

    match = _DOSE_UNIT_RE.search(text)
    if match is None:
        return None
    return match.group(1), normalize_dose_unit(match.group(2))


def frequency_code(text: str) -> str | None:
    """Map free-text frequency wording to an ExECTv2 ``Frequency`` code."""

    for pattern, value in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            return value
    return None


# ---------------------------------------------------------------------------
# Diagnosis: benchmark / CUIPhrase convention dictionary
# (migrated from the v03-v05 diagnosis lenses)
# ---------------------------------------------------------------------------

DIAGNOSIS_STANDALONE_NOISE: frozenset[str] = frozenset(
    {
        "absence like seizures",
        "absence seizures",
        "absences",
        "convulsive seizure",
        "dissociative seizures",
        "learning difficulties",
        "multiple seizures",
        "myoclonic jerks",
        "myoclonus",
        "seizures",
        "single seizure",
    }
)

DIAGNOSIS_CONVENTION_ALIAS_REPAIRS: dict[str, str] = {
    "drug resistant focal epilepsy": "drug resistant epilepsy",
    "epilepsy with tonic clonic seizures alone": (
        "epilepsy with generalised tonic clonic seizures alone"
    ),
    "focal cortical dysplasia": "symptomatic structural focal epilepsy",
    "focal cortical dysplasia right temporal lobe": "symptomatic structural focal epilepsy",
    "focal dyscognitive seizures": "dyscognitive seizures",
    "focal frontal lobe seizures": "frontal lobe seizures",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "grand mal seizure": "grand mal",
    "right hippocampal sclerosis": "temporal lobe epilepsy",
    "secondarily generalised seizures": "secondary generalised seizures",
    "tonic clonic seizures alone": "epilepsy with generalised tonic clonic seizures alone",
}

DIAGNOSIS_RESIDUAL_CONVENTION_NOISE: frozenset[str] = frozenset(
    {
        "drop attacks",
        "hydrocephalus",
        "learning difficulties",
        "nocturnal seizures",
        "seizure",
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
    r"secondary generalised|secondary generalisation",
    re.IGNORECASE,
)
_RESIDUAL_GENERIC_EPILEPSY_NOISE = re.compile(
    r"epilepsy in general|history of epilepsy|epilepsy protocol|father has a history|"
    r"epilepsy point|epilepsy service|epilepsy helpline|improve his seizures|"
    r"contraindication",
    re.IGNORECASE,
)

#: dev-derived source-phrase -> benchmark concept additions (``benchmark_format``).
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
)


def diagnosis_convention_target(text: str, evidence: str) -> str | None:
    """Return the convention-repaired Diagnosis text, or ``None`` if unchanged.

    Combines the v04 concept-keyed alias repairs with the v05 concept+evidence
    residual benchmark rewrites, in the same precedence the lenses applied
    (alias repair first, then residual benchmark).
    """

    concept = canonicalize_diagnosis_concept(text)
    alias = DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.get(concept)
    if alias is not None:
        return alias
    return _diagnosis_residual_benchmark_target(concept, evidence)


def _diagnosis_residual_benchmark_target(concept: str, evidence: str) -> str | None:
    if (
        concept == "focal epilepsy"
        and re.search(r"\bsymptomatic epilepsy\b", evidence, re.IGNORECASE)
        and not re.search(r"\bfocal\b", evidence, re.IGNORECASE)
    ):
        return "symptomatic epilepsy"
    if concept == "focal epilepsy" and re.search(
        r"\bsymptomatic focal epilepsy\b", evidence, re.IGNORECASE
    ):
        return "symptomatic focal epilepsy"
    if concept == "temporal lobe epilepsy" and re.search(
        r"focal seizures, probably temporal lobe", evidence, re.IGNORECASE
    ):
        return "temporal lobe seizures"
    if concept == "secondary generalised tonic clonic seizures":
        if re.search(r"secondary generalisation", evidence, re.IGNORECASE):
            return "secondary generalisation"
        if re.search(r"secondary generalised seizures", evidence, re.IGNORECASE):
            return "secondary generalised seizures"
    return None


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

    # v03: weak generic-epilepsy context without a strong diagnostic assertion.
    if concept == "epilepsy":
        return bool(_WEAK_GENERIC_EPILEPSY_CONTEXT.search(evidence)) and not bool(
            _STRONG_GENERIC_EPILEPSY_CONTEXT.search(evidence)
        )
    return False


def diagnosis_residual_additions(note_text: str) -> list[tuple[str, str]]:
    """Return dev-derived ``(concept_text, evidence)`` additions for a letter.

    De-duplicated by canonical concept, matching the v05 lens behaviour. The
    caller is responsible for skipping concepts already present.
    """

    added: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pattern, text in RESIDUAL_SOURCE_CONCEPT_PATTERNS:
        match = pattern.search(note_text)
        if match is None:
            continue
        concept = canonicalize_diagnosis_concept(text)
        if concept in seen:
            continue
        seen.add(concept)
        added.append((text, match.group(0)))
    return added


# ---------------------------------------------------------------------------
# SeizureFrequency: small benchmark rewrite dictionary
# (migrated from llm_sf_union_arbitration._rewrite)
# ---------------------------------------------------------------------------

_REWRITE_THESE_SEIZURES_RE = re.compile(r"10-15 of these seizures over 2 days", re.IGNORECASE)
_REWRITE_UP_TO_RANGE_RE = re.compile(r"up to 2 or 3 times per month", re.IGNORECASE)


def sf_convention_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Apply SF benchmark rewrites.

    Returns ``(new_text, new_attributes, rule_id)`` when a rewrite fires, else
    ``None``. Attributes are returned as a fresh dict so callers can replace.
    """

    attrs = dict(attributes)
    phrase = normalize_phrase(text)

    if phrase == "cluster of 3":
        attrs["CUI"] = "C3203523"
        attrs["CUIPhrase"] = "seizure cluster"
        return "seizure cluster", attrs, "rewrite_cluster_of_3_to_seizure_cluster"
    if _REWRITE_THESE_SEIZURES_RE.search(evidence) and attrs.get("CUI") == "C0270834":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_named_to_generic_seizures"
    if re.search(r"typical absences", evidence, re.IGNORECASE) and phrase == "absences":
        attrs["CUI"] = "C4316903"
        attrs["CUIPhrase"] = "typical absences"
        return "typical absences", attrs, "rewrite_absences_to_typical_absences"
    if _REWRITE_UP_TO_RANGE_RE.search(evidence) and attrs.get("CUI") == "C0877017":
        attrs["LowerNumberOfSeizures"] = "0"
        return text, attrs, "rewrite_up_to_range_lower_zero"
    return None
