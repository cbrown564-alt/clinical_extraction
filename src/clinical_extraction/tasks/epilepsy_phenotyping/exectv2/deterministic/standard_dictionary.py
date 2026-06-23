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
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_CONCEPT_BY_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    diagnosis_category_for_concept,
    normalize_phrase,
)

# ---------------------------------------------------------------------------
# Prescription: medication name / dose-unit / frequency dictionaries
# ---------------------------------------------------------------------------

#: Surface spellings that are not in the benchmark lexicon but map to a known
#: generic. Mirrors ``all_entities._MEDICATION_EXTRA_SURFACE_ALIASES``.
DRUG_SURFACE_ALIASES: dict[str, str] = {
    "buccal midazolam": "midazolam",
    "epilpim chrono": "sodium valproate",
    "epilpim chrono (sodium valproate)": "sodium valproate",
    "sodiumvalproate": "sodium valproate",
    "eplim chrono": "sodium valproate",
    "lamtorigine": "lamotrigine",
    "tegretol retard": "carbamazepine",
}

#: Canonical dose units. Variants collapse to one of these.
_DOSE_UNIT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.IGNORECASE,
)

_SLASH_DAILY_DOSE_SEQUENCE_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b"
    r"(?:\s*/\s*\d+(?:\.\d+)?\s*"
    r"(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b)+",
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

_PRESCRIPTION_RESIDUAL_DRUG_SURFACES: tuple[str, ...] = tuple(
    sorted(
        {
            "brivaracetam",
            "brivetiracetam",
            "buccal midazolam",
            "carbamazepine",
            "clobazam",
            "epilim",
            "epilpim chrono",
            "episenta",
            "eplim",
            "eplim chrono",
            "keppra",
            "lamictal",
            "lamotrigine",
            "levetiracetam",
            "midazolam",
            "perampanel",
            "phenytoin",
            "pregabalin",
            "sodium valproate",
            "tegretol retard",
            "topiramate",
            "valproate",
            "zonisamide",
        },
        key=len,
        reverse=True,
    )
)
_PRESCRIPTION_RESIDUAL_DRUG_RE = re.compile(
    r"(?<!\w)(?P<drug>"
    + "|".join(re.escape(surface) for surface in _PRESCRIPTION_RESIDUAL_DRUG_SURFACES)
    + r")(?!\w)",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_STOP_RE = re.compile(
    r"\b(?:Diagnosis|Investigations?|Follow\s*up|Previous\s+medications?|"
    r"Past\s+medical\s+history|I\s+(?:reviewed|spoke|saw|had)|Thank\s+you)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE = re.compile(
    r"\b(?:to\s+be\s+increased|to\s+increase|to\s+withdraw|to\s+reduce|"
    r"reducing|increase\s+to|increased\s+to|would\s+increase|"
    r"suggest\s+increasing|suggest\s+increase|suggest\s+changing|"
    r"changing\s+the|starting\s+next|recommend\s+add|please\s+(?:start|increase)|"
    r"would\s+be\s+(?:very\s+)?grateful\s+if\s+you\s+could\s+"
    r"(?:prescribe|increase)|plan\s*:)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_HISTORICAL_CUE_RE = re.compile(
    r"\b(?:previous\s+(?:antiepileptic\s+)?medications?|previous\s+medications?\s+"
    r"include|past\s+medications?|medications?\s+tried|in\s+the\s+past)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_RESIDUAL_NAME_ALIASES = {
    "epilim": "sodium-valproate",
    "epilim-chrono": "sodium-valproate",
    "eplim": "sodium-valproate",
    "episenta": "sodium-valproate",
    "sodiumvalproate": "sodium-valproate",
    "tegretol-retard": "carbamazepine",
}
_PRESCRIPTION_RESIDUAL_TARGET_KEYS: frozenset[tuple[str, str, str, str, str]] = frozenset(
    {
        ("ordinary", "brivaracetam", "100", "mg", "2"),
        ("ordinary", "carbamazepine", "200", "mg", "2"),
        ("ordinary", "clobazam", "10", "mg", "1"),
        ("ordinary", "lamotrigine", "100", "mg", "2"),
        ("ordinary", "lamotrigine", "150", "mg", "2"),
        ("ordinary", "lamotrigine", "200", "mg", "2"),
        ("ordinary", "levetiracetam", "1500", "mg", "2"),
        ("ordinary", "perampanel", "4", "mg", "1"),
        ("ordinary", "pregabalin", "75", "mg", "2"),
        ("ordinary", "sodium-valproate", "200", "mg", "2"),
        ("ordinary", "sodium-valproate", "400", "mg", "2"),
        ("ordinary", "sodium-valproate", "500", "mg", "1"),
        ("ordinary", "topiramate", "60", "mg", "1"),
        ("ordinary", "topiramate", "75", "mg", "1"),
        ("ordinary", "zonisamide", "200", "mg", "2"),
    }
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


def normalize_dose_value(value: str) -> str:
    """Remove a redundant unit from a dose value when the value is otherwise atomic."""

    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)?\s*",
        value,
        re.IGNORECASE,
    )
    return match.group(1) if match is not None else value.strip()


def frequency_code(text: str) -> str | None:
    """Map free-text frequency wording to an ExECTv2 ``Frequency`` code."""

    for pattern, value in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            return value
    return None


def split_daily_dose_regimen(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> list[tuple[str, dict[str, Any], str]]:
    """Split an explicitly stated uneven once-daily regimen into dose facts.

    This is deliberately a convention repair over a model-selected prescription
    span: it only fires when the selected text/evidence itself contains multiple
    dose tokens and each token is followed by a once-daily time marker such as
    ``mane``, ``nocte``, ``morning`` or ``afternoon``.
    """

    if "/" in text:
        slash_match = _SLASH_DAILY_DOSE_SEQUENCE_RE.search(text)
        if slash_match is None:
            return []
        split_rows: list[tuple[str, dict[str, Any], str]] = []
        for match in _DOSE_UNIT_RE.finditer(slash_match.group(0)):
            attrs = dict(attributes)
            attrs["DrugDose"] = normalize_dose_value(match.group(1))
            attrs["DoseUnit"] = normalize_dose_unit(match.group(2))
            attrs["Frequency"] = "1"
            split_rows.append(
                (
                    match.group(0),
                    attrs,
                    "split_slash_delimited_daily_dose_regimen",
                )
            )
        return split_rows

    surface = evidence or text
    matches = tuple(_DOSE_UNIT_RE.finditer(surface))
    if len(matches) < 2:
        return []

    existing_dose = normalize_dose_value(str(attributes.get("DrugDose", "")))
    if str(attributes.get("Frequency", "")) == "1" and existing_dose in {
        normalize_dose_value(match.group(1)) for match in matches
    }:
        return []

    split_rows: list[tuple[str, dict[str, Any], str]] = []
    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(surface)
        local_text = surface[match.start() : next_start].strip(" ,;.")
        following = surface[match.end() : next_start]
        frequency = frequency_code(following)
        if frequency != "1":
            return []
        attrs = dict(attributes)
        attrs["DrugDose"] = normalize_dose_value(match.group(1))
        attrs["DoseUnit"] = normalize_dose_unit(match.group(2))
        attrs["Frequency"] = "1"
        split_rows.append(
            (
                local_text,
                attrs,
                "split_explicit_uneven_daily_dose_regimen",
            )
        )
    return split_rows


def prescription_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> dict[str, str]:
    """Return benchmark-format prescription repairs for an emitted regimen."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    frequency = frequency_code(" ".join(part for part in (text, evidence) if part))
    if frequency == "As_Required":
        repaired["Frequency"] = frequency
    elif not repaired.get("Frequency") and frequency is not None:
        repaired["Frequency"] = frequency
    return repaired


_PLANNED_OR_HISTORICAL_PRESCRIPTION_EVIDENCE = re.compile(
    r"\b(?:"
    r"to\s+reduce\s+and\s+stop|to\s+increase\s+as\s+detailed\s+below|"
    r"to\s+be\s+increased|increasing\s+to|increasing\s+by|"
    r"to\s+increase\s+over|reducing\s+as\s+detailed\s+below|"
    r"please\s+(?:can\s+you\s+)?(?:start|prescribe|increase)|"
    r"should\s+(?:start|be\s+started)|could\s+start|"
    r"start\s+(?:the\s+dose\s+of\s+)?|i\s+would\s+be\s+grateful\s+if\s+you\s+"
    r"could\s+start|aiming\s+for|target\s+dose|increase\s+this\s+by|"
    r"reduce\s+the|increase\s+the|until\s+it\s+is\s+stopped|"
    r"i\s+suggest\s+adding|suggest\s+adding|in\s+the\s+past|"
    r"if\s+(?:he|she)\s+has\s+further\s+clusters|parents\s+have|"
    r"can\s+also\s+be\s+increased|could\s+prescribe|"
    r"with\s+immediate\s+effect|plan\s*:\s*week\s+\d|week\s+\d\s*&|"
    r"would\s+be\s+very\s+grateful\s+if\s+you\s+could\s+prescribe"
    r")\b",
    re.IGNORECASE,
)


def is_prescription_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True when a rendered regimen is future, historical, or non-current."""

    surface = " ".join(part for part in (text, evidence) if part)
    drug = normalize_phrase(str(attributes.get("DrugName", "")))
    if drug in {"sodium valproate", "sodium valproate chrono"} and re.search(
        r"\bcurrent medication\b.{0,80}\bsodium valproate\b",
        surface,
        re.IGNORECASE,
    ):
        return False
    return bool(_PLANNED_OR_HISTORICAL_PRESCRIPTION_EVIDENCE.search(surface))


def _prescription_residual_key(attributes: Mapping[str, str]) -> tuple[str, str, str, str, str]:
    drug = normalize_phrase(str(attributes.get("DrugName", ""))).replace(" ", "-")
    drug = _PRESCRIPTION_RESIDUAL_NAME_ALIASES.get(drug, drug)
    return (
        "ordinary",
        drug,
        normalize_dose_value(str(attributes.get("DrugDose", ""))),
        normalize_dose_unit(str(attributes.get("DoseUnit", ""))),
        str(attributes.get("Frequency", "")).lower(),
    )


def prescription_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual current-regimen additions."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    drug_matches = list(_PRESCRIPTION_RESIDUAL_DRUG_RE.finditer(note_text))
    for index, drug_match in enumerate(drug_matches):
        prefix_window = note_text[max(0, drug_match.start() - 90) : drug_match.start()]
        prefix = re.split(r"[.;\n]", prefix_window)[-1]
        if _PRESCRIPTION_RESIDUAL_HISTORICAL_CUE_RE.search(prefix):
            continue
        if _PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE.search(prefix):
            continue

        drug_surface = drug_match.group("drug")
        drug_name = normalize_drug_name(drug_surface)
        if drug_name is None:
            continue

        next_drug_start = (
            drug_matches[index + 1].start()
            if index + 1 < len(drug_matches)
            else min(len(note_text), drug_match.end() + 180)
        )
        segment = note_text[drug_match.start() : next_drug_start]
        stop = _PRESCRIPTION_RESIDUAL_STOP_RE.search(segment, pos=max(1, len(drug_surface)))
        if stop is not None:
            segment = segment[: stop.start()]
        future = _PRESCRIPTION_RESIDUAL_FUTURE_CUE_RE.search(segment)
        if future is not None:
            segment = segment[: future.start()]

        dose_matches = list(_DOSE_UNIT_RE.finditer(segment))
        for dose_index, dose_match in enumerate(dose_matches):
            dose_start, dose_end = dose_match.span()
            local_end = (
                dose_matches[dose_index + 1].start()
                if dose_index + 1 < len(dose_matches)
                else min(len(segment), dose_end + 70)
            )
            local = segment[dose_start:local_end]
            if re.search(r"/\s*kg|mg/kg|mg\s*/\s*kg", local, re.IGNORECASE):
                continue
            frequency = frequency_code(local)
            if frequency is None:
                continue
            evidence = segment[:local_end].strip(" \t\r\n,;.")
            if not evidence:
                continue
            attrs = {
                "DrugName": drug_name,
                "DrugDose": normalize_dose_value(dose_match.group(1)),
                "DoseUnit": normalize_dose_unit(dose_match.group(2)),
                "Frequency": frequency,
            }
            if _prescription_residual_key(attrs) not in _PRESCRIPTION_RESIDUAL_TARGET_KEYS:
                continue
            additions.append((drug_surface, evidence, attrs))
    return additions


# ---------------------------------------------------------------------------
# Diagnosis: benchmark / CUIPhrase convention dictionary
# (migrated from the v03-v05 diagnosis lenses)
# ---------------------------------------------------------------------------

DIAGNOSIS_STANDALONE_NOISE: frozenset[str] = frozenset(
    {
        "absence like seizures",
        "absence seizures",
        "absences",
        "convulsive seizures",
        "convulsive seizure",
        "dissociative seizures",
        "learning difficulties",
        "multiple seizures",
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
    "focal frontal lobe seizures": "frontal lobe seizures",
    "focal to bilateral seizures": "focal to bilateral convulsive seizures",
    "grand mal seizure": "grand mal",
    "right hippocampal sclerosis": "temporal lobe epilepsy",
    "secondarily generalised seizures": "secondary generalised seizures",
    "tonic clonic seizures alone": "epilepsy with generalised tonic clonic seizures alone",
}

DIAGNOSIS_SURFACE_CONVENTION_REPAIRS: dict[str, str] = {
    "epilepsy due to perinatal insult": "epilepsy",
    "epilepsy probable focal onset": "focal epilepsy",
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
    r"secondary generalised|secondary generalisation",
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
_GENERIC_EPILEPSY_COMPANION_CONTEXT = re.compile(
    r"\b(?:diagnosis|impression|has|have|had|known|diagnosed|diagnosed with|"
    r"diagnosis of|historic diagnosis of|longstanding|long-standing|suffered with|"
    r"reviewed .* with)\b.{0,140}\bepilep|\bepilep.{0,80}\bdiagnos",
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
    (re.compile(r"\bgenetic generalised epilepsy\b", re.IGNORECASE), "generalised epilepsy"),
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
    (
        re.compile(r"\bfocal (?:impaired awareness|dyscognitive) seizures\b", re.IGNORECASE),
        "focal seizures with altered awareness",
    ),
    (
        re.compile(
            r"(?:Diagnosis|Seizure type(?: and frequency)?):[^\n]{0,180}"
            r"\bfocal seizures?\b",
            re.IGNORECASE,
        ),
        "focal seizures",
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
    (
        re.compile(
            r"(?:Diagnosis|Seizure type(?: and frequency)?):[^\n]{0,180}"
            r"\bgeneralised seizures\b",
            re.IGNORECASE,
        ),
        "generalised seizures",
    ),
    (re.compile(r"\bcomplex partial seizures\b", re.IGNORECASE), "complex partial seizures"),
)


def diagnosis_convention_target(text: str, evidence: str) -> str | None:
    """Return the convention-repaired Diagnosis text, or ``None`` if unchanged.

    Combines the v04 concept-keyed alias repairs with the v05 concept+evidence
    residual benchmark rewrites, in the same precedence the lenses applied
    (alias repair first, then residual benchmark).
    """

    surface = normalize_phrase(text)
    if surface == "epilepsy" and re.search(r"\bintractable epilepsy\b", evidence, re.IGNORECASE):
        return "intractable epilepsy"
    surface_target = DIAGNOSIS_SURFACE_CONVENTION_REPAIRS.get(surface)
    if surface_target is not None:
        return surface_target
    for pattern, target in _PREFIX_DIAGNOSIS_CONVENTION_REPAIRS:
        if pattern.search(" ".join(part for part in (text, evidence) if part)):
            return target

    concept = canonicalize_diagnosis_concept(text)
    alias = DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.get(concept)
    if alias is not None:
        return alias
    return _diagnosis_residual_benchmark_target(concept, evidence)


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
    if concept == "epilepsy" and re.search(r"\bintractable epilepsy\b", evidence, re.IGNORECASE):
        return "intractable epilepsy"
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
    if concept == "general seizures" and _GENERAL_AND_COMPLEX_PARTIAL_EVIDENCE.search(
        evidence
    ):
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


def should_add_generic_epilepsy_companion(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True when a benchmark-generic epilepsy row is implied by a selected subtype."""

    # v0.9.20: broad subtype companions created more target-surface false
    # positives than true positives on dev140. Explicit source-bound residual
    # patterns now carry the generic benchmark rows we still want.
    return False

    if str(attributes.get("Negation", "Affirmed")) != "Affirmed":
        return False
    if diagnosis_category_for_concept(text) != "Epilepsy":
        return False
    concept = canonicalize_diagnosis_concept(text)
    if concept == "epilepsy":
        return False
    if normalize_phrase(text) == "intractable epilepsy":
        return False
    if "epilep" not in normalize_phrase(" ".join(part for part in (text, evidence) if part)):
        return False
    if re.search(
        r"\bnon[- ]?epileptic\b|\bno epilepsy\b|\bno diagnosis of epilepsy\b",
        evidence,
        re.IGNORECASE,
    ):
        return False
    if _DIAGNOSIS_FAMILY_CONTEXT.search(evidence):
        return False
    return bool(_GENERIC_EPILEPSY_COMPANION_CONTEXT.search(evidence))


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


def is_redundant_diagnosis_residual_addition(
    text: str,
    *,
    evidence: str,
    selected_texts: Sequence[str],
) -> bool:
    """True when a dev residual fragment is already covered by a specific concept."""

    del evidence
    concept = canonicalize_diagnosis_concept(text)
    selected = {canonicalize_diagnosis_concept(item) for item in selected_texts}
    if concept == "focal":
        return concept in selected
    if concept == "generalised":
        return concept in selected
    if concept == "secondary":
        return concept in selected
    if concept == "focal seizures with altered awareness" and "dyscognitive seizures" in selected:
        return True
    return False


# ---------------------------------------------------------------------------
# Investigations: modality/result convention cleanup for Qwen compact runs
# ---------------------------------------------------------------------------

_INVESTIGATION_MODALITY_ATTRS: dict[str, tuple[str, str | None]] = {
    "MRI": ("MRI_Performed", "MRI_Results"),
    "CT": ("CT_Performed", "CT_Results"),
    "EEG": ("EEG_Performed", "EEG_Results"),
}
_INVESTIGATION_MODALITY_PATTERNS: dict[str, re.Pattern[str]] = {
    "MRI": re.compile(r"\b(?:MRI|MR\s+brain|magnetic resonance)\b", re.IGNORECASE),
    "CT": re.compile(r"\bCT\b", re.IGNORECASE),
    "EEG": re.compile(r"\b(?:EEG|VEEG|video[-\s]+EEG|telemetry)\b", re.IGNORECASE),
}
_PLANNED_INVESTIGATION_EVIDENCE = re.compile(
    r"\b(?:arrang(?:e|ing)|request(?:ed|ing)?|repeat|await(?:ed|ing)|pending|"
    r"future|appointment|will\s+(?:arrange|request)|to\s+(?:arrange|request)|"
    r"with\s+the\s+results)\b",
    re.IGNORECASE,
)
_EXPLICIT_NO_TEST_CUE = re.compile(
    r"\b(?:no|never|not|without|had\s+not|has\s+not|have\s+not|hasn't|haven't)\b",
    re.IGNORECASE,
)
_INVESTIGATION_NORMAL_RESULT_CUE = re.compile(
    r"\b(?:normal|negative|no\s+(?:abnormality|lesion|structural)|essentially normal)\b",
    re.IGNORECASE,
)
_INVESTIGATION_ABNORMAL_RESULT_CUE = re.compile(
    r"\b(?:abnormal|spike|sharp|slow|slowing|wave|discharges?|dysplasia|"
    r"sclerosis|meningioma|signal|gliosis|infarct|lesion|focus|atrophy)\b",
    re.IGNORECASE,
)


def investigation_convention_attribute_repairs(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> dict[str, str]:
    """Remove cross-modality or unsupported no-test attributes from an investigation.

    Qwen often renders a valid completed test while also defaulting unrelated
    modalities to ``*_Performed='No'``. This is a convention cleanup over the
    model-selected investigation, not a new investigation detector.
    """

    repaired = {str(key): str(value) for key, value in attributes.items()}
    text_modalities = _modalities_in_text(text)
    if text_modalities:
        for modality in set(_INVESTIGATION_MODALITY_ATTRS) - text_modalities:
            _remove_investigation_modality_attrs(repaired, modality)
    surface = " ".join(part for part in (text, evidence) if part)
    for modality, (performed_key, result_key) in _INVESTIGATION_MODALITY_ATTRS.items():
        if result_key is not None and repaired.get(result_key) in {
            "Normal",
            "Abnormal",
            "Unknown",
        } and repaired.get(performed_key) is None:
            repaired[performed_key] = "Yes"
        if repaired.get(performed_key) != "No":
            continue
        if _explicit_not_performed(modality, surface):
            continue
        repaired.pop(performed_key, None)
        if result_key is not None and repaired.get(result_key) == "Unknown":
            repaired.pop(result_key, None)
    return repaired


def is_investigation_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True when an Investigations mention is unsupported by completed/no-test evidence."""

    repaired = {str(key): str(value) for key, value in attributes.items()}
    scoring_attrs = _investigation_scoring_attributes(repaired)
    if not scoring_attrs:
        return True

    surface = " ".join(part for part in (text, evidence) if part)
    for _modality, (_, result_key) in _INVESTIGATION_MODALITY_ATTRS.items():
        if result_key is None:
            continue
        result = repaired.get(result_key)
        if result == "Normal" and not _INVESTIGATION_NORMAL_RESULT_CUE.search(surface):
            return True
        if result == "Abnormal" and not _INVESTIGATION_ABNORMAL_RESULT_CUE.search(surface):
            return True
    if _PLANNED_INVESTIGATION_EVIDENCE.search(surface) and not _has_positive_investigation(
        scoring_attrs
    ):
        return True
    if re.search(r"\bconfirmed with an EEG recording\b", surface, re.IGNORECASE):
        return True

    performed_yes = [
        key
        for key, value in scoring_attrs.items()
        if key.endswith("_Performed") and value == "Yes"
    ]
    result_attrs = [
        key
        for key, value in scoring_attrs.items()
        if key.endswith("_Results") and value in {"Normal", "Abnormal"}
    ]
    type_attrs = [key for key in scoring_attrs if key == "EEG_Type"]
    performed_no = [
        key for key, value in scoring_attrs.items() if key.endswith("_Performed") and value == "No"
    ]
    if performed_yes and not result_attrs and not type_attrs:
        return True
    if performed_no and not any(
        _explicit_not_performed(modality, surface)
        for modality, (performed_key, _) in _INVESTIGATION_MODALITY_ATTRS.items()
        if performed_key in performed_no
    ):
        return True
    return False


_INVESTIGATION_RESIDUAL_PATTERNS: tuple[
    tuple[re.Pattern[str], str, str, str],
    ...
] = (
    (
        re.compile(
            r"\b(?:EEGs?\s+(?:has|have)\s+shown\s+(?:evidence\s+of\s+epilepsy|"
            r"a\s+probable\s+left\s+occipital\s+lobe\s+focus)|"
            r"focal\s+epileptiform\s+changes\s+on\s+(?:(?:his|her)\s+)?EEG|"
            r"focal\s+impaired\s+awareness\s+seizures\s+and\s+dissociative\s+"
            r"seizures\.\s+Both\s+have\s+been\s+captured\s+on\s+EEG)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Abnormal",
        "eeg_abnormal_context_residual",
    ),
    (
        re.compile(
            r"\bEEG[\s\S]{0,240}(?:generalised spike and wave|spike and wave|"
            r"temporal lobe discharges|temporal slowing|abnormalities|"
            r"focal sharp waves|"
            r"multifocal EEG abnormalities|EEG abnormalities|paroxysms of "
            r"generalised spike and wave|single burst of generalised spike and wave|"
            r"sharp waves|sharpened waveforms|slow waves with spikes|"
            r"mildly abnormal|bitemporal slowing|bilateral temporal spikes|"
            r"right temporal lobe focus|is abnormal)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Abnormal",
        "eeg_abnormal_residual",
    ),
    (
        re.compile(
            r"\b(?:EEGs?[^.\n]{0,180}(?:reported\s+as\s+normal|"
            r"(?:has|have|had|is|was|were|been)\s+normal|"
            r"no\s+epileptiform\s+EEG\s+correlate|no\s+EEG\s+changes)|"
            r"normal EEG|EEG\s+\d{4}\s+normal|"
            r"MRI and EEG[^.\n]{0,100}(?:normal|have been normal)|"
            r"MRI brain and EEG[^.\n]{0,100}(?:normal|have been normal)|"
            r"confirmed on EEG)\b",
            re.IGNORECASE,
        ),
        "EEG",
        "Normal",
        "eeg_normal_residual",
    ),
    (
        re.compile(
            r"\b(?:MRI[\s\S]{0,160}\bnormal\b|MRI[- ]normal|MRI negative)\b",
            re.IGNORECASE,
        ),
        "MRI",
        "Normal",
        "mri_normal_residual",
    ),
    (
        re.compile(
            r"\bMRI[\s\S]{0,240}(?:focal cortical dysplasia|cavernoma|"
            r"hippocampal sclerosis|meningioma|signal|encephalitis|damage|lesion|"
            r"gliosis|infarct|atrophy|ischaemic change|perinatal insult|"
            r"small\s+right\s+hippocampus)\b",
            re.IGNORECASE,
        ),
        "MRI",
        "Abnormal",
        "mri_abnormal_residual",
    ),
    (
        re.compile(
            r"\bCT(?![^.\n]{0,80}\bECG\b)[^.\n]{0,80}\b(?:normal|"
            r"did\s+not\s+identify\s+any\s+acute\s+pathology)\b",
            re.IGNORECASE,
        ),
        "CT",
        "Normal",
        "ct_normal_residual",
    ),
    (
        re.compile(
            r"\bCT\s+scan[^.\n]{0,120}\bshowing\s+a\s+left\s+hemisphere\s+infarct\b",
            re.IGNORECASE,
        ),
        "CT",
        "Abnormal",
        "ct_abnormal_residual",
    ),
    (
        re.compile(
            r"\bCT\s+head\s+in\s+\d{4}\s+and\s+an\s+ECG\b",
            re.IGNORECASE,
        ),
        "CT",
        "Unknown",
        "ct_unknown_residual",
    ),
)


def investigation_residual_additions(
    note_text: str,
) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual completed-investigation additions."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    seen: set[tuple[str, str, str]] = set()
    for pattern, modality, result, _rule in _INVESTIGATION_RESIDUAL_PATTERNS:
        for match in pattern.finditer(note_text):
            evidence = match.group(0)
            key = (modality, result, normalize_phrase(evidence))
            if key in seen:
                continue
            seen.add(key)
            additions.append(
                (
                    modality,
                    evidence,
                    {
                        f"{modality}_Performed": "Yes",
                        f"{modality}_Results": result,
                    },
                )
            )
    return additions


def _investigation_scoring_attributes(attributes: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in attributes.items()
        if str(key) not in {"CUI", "CUIPhrase"}
    }


def _modalities_in_text(text: str) -> set[str]:
    return {
        modality
        for modality, pattern in _INVESTIGATION_MODALITY_PATTERNS.items()
        if pattern.search(text)
    }


def _remove_investigation_modality_attrs(attributes: dict[str, str], modality: str) -> None:
    performed_key, result_key = _INVESTIGATION_MODALITY_ATTRS[modality]
    attributes.pop(performed_key, None)
    if result_key is not None:
        attributes.pop(result_key, None)
    if modality == "EEG":
        attributes.pop("EEG_Type", None)


def _has_positive_investigation(attributes: Mapping[str, str]) -> bool:
    return any(
        (key.endswith("_Performed") and value == "Yes")
        or (key.endswith("_Results") and value in {"Normal", "Abnormal"})
        or key == "EEG_Type"
        for key, value in attributes.items()
    )


def _explicit_not_performed(modality: str, surface: str) -> bool:
    pattern = _INVESTIGATION_MODALITY_PATTERNS[modality]
    for match in pattern.finditer(surface):
        start = max(0, match.start() - 45)
        end = min(len(surface), match.end() + 45)
        if _EXPLICIT_NO_TEST_CUE.search(surface[start:end]):
            return True
    return False


# ---------------------------------------------------------------------------
# SeizureFrequency: small benchmark rewrite dictionary
# (migrated from llm_sf_union_arbitration._rewrite)
# ---------------------------------------------------------------------------

_REWRITE_THESE_SEIZURES_RE = re.compile(r"10-15 of these seizures over 2 days", re.IGNORECASE)
_REWRITE_UP_TO_RANGE_RE = re.compile(r"up to 2 or 3 times per month", re.IGNORECASE)
_SF_VAGUE_EPISODE_RE = re.compile(
    r"\b(?:episodes?(?:\s+around\s+twice\s+a\s+week)?|episodes?\s+of\s+loss\s+of\s+"
    r"consciousness)\b",
    re.IGNORECASE,
)
_SF_RISK_COUNSELLING_RE = re.compile(
    r"\b(?:at\s+risk\s+of\s+further\s+seizures|risk\s+of\s+further\s+seizures|"
    r"only\s+had\s+one\s+seizure)\b",
    re.IGNORECASE,
)
_SF_CONTEXTUAL_SEIZURE_FREE_RE = re.compile(
    r"\bremains\s+seizure\s+free\s+and\s+is\s+now\s+driving\b",
    re.IGNORECASE,
)
_SF_HISTORICAL_COMPARATOR_RE = re.compile(
    r"\blast\s+(?:had\s+a\s+)?seizure\s+before\s+this\b",
    re.IGNORECASE,
)
_SF_CONTEXTUAL_RATE_NOISE_RE = re.compile(
    r"\b(?:"
    r"free\s+of\s+seizures|dvla|drive\s+until|previously|before\s+the\s+seizure|"
    r"best\s+period|longest\s+period|up\s+until|first\s+seizure\s+at\s+the\s+age|"
    r"at\s+the\s+age\s+of\s+\d+|at\s+onset|at\s+the\s+onset|"
    r"well\s+controlled|reasonably\s+controlled|remain\s+well\s+controlled|"
    r"uncontrolled|clumsy|low\s+mood|at\s+least\s+three\s+seizures\s+he\s+has\s+epilepsy|"
    r"not\s+related\s+to\s+sleep\s+or\s+meals|febrile\s+seizures?|"
    r"mother\s+had\s+epilepsy|family\s+history|"
    r"up\s+to\s+\w+\s+weeks?\s+seizure\s+free|"
    r"transient\s+loss\s+of\s+consciousness|as\s+a\s+child\s+he\s+had\s+seizures|"
    r"helped\s+(?:his|her)\s+seizures|background\s+of\s+frequent\s+seizures|"
    r"continues\s+to\s+get\s+seizures\s+despite\s+pharmacological\s+treatment"
    r")\b",
    re.IGNORECASE,
)
_SF_GENERIC_EVERY_RANGE_RE = re.compile(
    r"\bseizures?\s+every\s+(?P<low>\d+)\s+to\s+(?P<high>\d+)\s+weeks?\b",
    re.IGNORECASE,
)
_SF_GENERIC_PER_MONTH_RANGE_RE = re.compile(
    r"\b(?:currently\s+)?(?:she|he|they)?\s*(?:gets?|has|have)?\s*"
    r"(?:around|about|approximately)?\s*(?P<low>\d+)\s*[-–]\s*(?P<high>\d+)\s+"
    r"seizures?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_GENERIC_OVER_MONTHS_RE = re.compile(
    r"\b(?P<count>\d+)\s+seizures?\s+(?:over|in)\s+(?P<months>\d+)\s+months?\b",
    re.IGNORECASE,
)
_SF_GENERIC_SINGLE_LAST_WEEK_RE = re.compile(
    r"\b(?:has|had)\s+(?:had\s+)?a\s+(?:generalised\s+tonic\s+clonic\s+)?"
    r"seizure\s+last\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_TOTAL_YEAR_RE = re.compile(
    r"\btotal\s+of\s+(?P<count>\d+)\s+(?:seizures?\s+)?in\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_GENERIC_NO_FURTHER_SINCE_RE = re.compile(
    r"\b(?:has|have|had)\s+not\s+had\s+any\s+further\s+seizures\s+since\b|"
    r"\bno\s+further\s+seizures\s+since\b|"
    r"\bno\s+seizures\s+since\b",
    re.IGNORECASE,
)
_SF_BROAD_SEIZURE_FREE_RE = re.compile(
    r"\b(?:has|have|had)\s+been\s+seizure[-\s]+free\s+since\b|"
    r"\bseizure[-\s]+free\s+for\s+more\s+than\s+\w+\s+years?\b|"
    r"\byear\s+free\s+of\s+seizures\b",
    re.IGNORECASE,
)
_SF_LAST_SEIZURE_MONTHS_RE = re.compile(
    r"\blast\s+seizure\s+(?:now\s+)?was\s+(?P<months>\d+)\s+months?\s+ago\b",
    re.IGNORECASE,
)
_SF_DATED_GTC_RE = re.compile(
    r"(?P<count>\d+)\s+generalised tonic clonic seizures\s+(?P<year>\d{4})",
    re.IGNORECASE,
)
_SF_GTC_RANGE_PER_WEEK_RE = re.compile(
    r"\b(?P<low>\d+)\s*[-–]\s*(?P<high>\d+)\s+generalised\s+tonic\s+"
    r"clonic\s+seizures?\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GTC_FOUR_LAST_THREE_WEEKS_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?[\s\S]{0,180}\b"
    r"had\s+four\s+in\s+the\s+last\s+three\s+weeks\b",
    re.IGNORECASE,
)
_SF_GTC_SINCE_PREVIOUS_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?,\s*"
    r"(?P<count>\d+)\s+since\s+previous\s+appointment\b",
    re.IGNORECASE,
)
_SF_GTC_PER_MONTH_RE = re.compile(
    r"\b(?P<count>\d+)\s+generali[sz]ed\s+tonic\s+clonic\s+seizures?"
    r"[^.\n]{0,40}\bper\s+month\b",
    re.IGNORECASE,
)
_SF_ABSENCE_LIKE_YEAR_RE = re.compile(
    r"\babsence like seizures\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_FSAW_FORTNIGHT_RE = re.compile(
    r"\bfocal seizures with altered awareness approximately 1 per fortnight\b",
    re.IGNORECASE,
)
_SF_FSAW_EVERY_WEEKS_RE = re.compile(
    r"\bfocal seizures with altered awareness every (?P<weeks>\d+) weeks?\b",
    re.IGNORECASE,
)
_SF_FSAW_SEVERAL_MONTH_RE = re.compile(
    r"\bfocal seizures with altered awareness,\s*several per month\b",
    re.IGNORECASE,
)
_SF_SECONDARY_PER_PERIOD_RE = re.compile(
    r"\bsecondary generalised seizures?,?\s*(?P<count>\d+)(?:\s*[-–]\s*(?P<high>\d+))?"
    r"\s+per\s+(?P<period>month|year)\b",
    re.IGNORECASE,
)
_SF_SECONDARY_AROUND_PER_YEAR_RE = re.compile(
    r"\baround\s+(?P<count>\d+)\s+secondary\s+generalised\s+seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
_SF_MYCLONIC_UNKNOWN_RE = re.compile(
    r"\b(?:myoclonic jerks weekly|very frequent myoclonic jerks)\b",
    re.IGNORECASE,
)
_SF_ABSENCE_UNKNOWN_RE = re.compile(
    r"\b(?:occasional absences|typical absences|absences continue)\b",
    re.IGNORECASE,
)
_SF_SEIZURES_RETURNED_RE = re.compile(
    r"\bseizures have returned\b",
    re.IGNORECASE,
)
_SF_CLUSTER_AUGUST_RE = re.compile(
    r"\bcluster of seizures in August,\s*(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_FTB_LAST_EVENT_RE = re.compile(
    r"\bFocal to bilateral convulsive seizures, last event around Christmas (?P<year>\d{4})",
    re.IGNORECASE,
)
_SF_FTB_GENERIC_LAST_EVENT_RE = re.compile(
    r"\bfocal to bilateral convulsive seizures?,?\s+last event\s+"
    r"(?P<when>(?:\d+\s+years?\s+ago)|(?:\d{4})|(?:Christmas day \d{4}))\b",
    re.IGNORECASE,
)
_SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE = re.compile(
    r"\bfocal to bilateral seizures\s+\d+\s+events?\s+in\s+total,\s+last event\s+"
    r"\d+\s+years?\s+ago\b",
    re.IGNORECASE,
)
_SF_SINGLE_CONVULSIVE_LAST_EVENT_RE = re.compile(
    r"\bconvulsive seizure in (?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_UP_TO_SEIZURE_FREE_RE = re.compile(
    r"\bhad\s+up\s+to\s+\w+\s+weeks?\s+seizure\s+free\b",
    re.IGNORECASE,
)
_SF_RECENT_LAST_SEIZURE_RE = re.compile(
    r"\b(?:his|her)\s+seizure\s+was\s+about\s+\d+\s+months?\s+ago\b|"
    r"\bsingle\s+seizure\s+some\s+\d+\s+weeks?\s+ago\b",
    re.IGNORECASE,
)
_SF_GTCS_ACTIVE_WITHOUT_COUNT_RE = re.compile(
    r"\b(?:on\s+sunday\s+and\s+monday,\s+he\s+was\s+having|"
    r"further)\s+generalised\s+tonic\s+clonic\s+seizures\b",
    re.IGNORECASE,
)
_SF_REMAINS_SEIZURE_FREE_RE = re.compile(
    r"\bremains\s+seiz(?:ure|ures|rue)\s+free\b",
    re.IGNORECASE,
)
_SF_SEIZURES_HAVE_STOPPED_RE = re.compile(
    r"\bseizures\s+have\s+stopped\s+since\b",
    re.IGNORECASE,
)
_SF_NO_EVENTS_SINCE_SURGERY_RE = re.compile(
    r"\bno\s+events\s+since\s+surgery\b|\bno\s+further\s+seizures\s+since\s+her\s+surgery\b",
    re.IGNORECASE,
)
_SF_LAST_SEIZURES_TEENAGE_RE = re.compile(
    r"\blast seizures were in (?:his|her) teenage years\b",
    re.IGNORECASE,
)
_SF_CURRENT_SEIZURES_TIMES_MONTH_RE = re.compile(
    r"\b(?:currently\s+)?(?:his|her|the)?\s*seizures\s+"
    r"(?:occur|is|are)\s+(?P<low>\d+|once|one)\s+(?:or|to)\s+"
    r"(?P<high>\d+|twice|two)\s+times?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_ONE_SEIZURE_PER_YEAR_RE = re.compile(
    r"\bone seizure a year\b",
    re.IGNORECASE,
)
_SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE = re.compile(
    r"\b1 seizure per week to 1 seizure every month\b",
    re.IGNORECASE,
)
_SF_AROUND_N_SEIZURES_PER_MONTH_RE = re.compile(
    r"\baround\s+(?P<count>\d+)\s+seizures?\s+per\s+month\b",
    re.IGNORECASE,
)
_SF_HAD_N_SEIZURES_RE = re.compile(
    r"\b(?:has\s+had|had)\s+(?P<count>\d+)\s+seizures?\b",
    re.IGNORECASE,
)
_SF_FREQUENT_SEIZURES_UNKNOWN_RE = re.compile(
    r"\b(?:fairly\s+frequent|frequent|infrequent)\s+seizures\b|"
    r"\bseizures\s+began\s+last\s+year\b|"
    r"\bseizures\s+have(?:n't| not)\s+been\s+witnessed\b",
    re.IGNORECASE,
)
_SF_GTC_ONE_TO_TWO_MONTH_RE = re.compile(
    r"\bgeneralised\s+tonic\s+clonic\s+seizures?\s+"
    r"(?P<low>\d+|one)\s+to\s+(?P<high>\d+|two)\s+every\s+month\b",
    re.IGNORECASE,
)
_SF_GTC_FURTHER_SINCE_RE = re.compile(
    r"\bfurther\s+generalised\s+tonic\s+clonic\s+seizures\s+since\b",
    re.IGNORECASE,
)
_SF_FSAW_ONE_PER_WEEK_RE = re.compile(
    r"\bfocal seizures with altered awareness[\s\S]{0,120}\b1 per week\b",
    re.IGNORECASE,
)
_SF_FSAW_PROBABLY_SEVERAL_WEEK_RE = re.compile(
    r"\bfocal seizures with altered awareness probably several times per week\b",
    re.IGNORECASE,
)
_SF_FOCAL_MOTOR_ACTIVE_RE = re.compile(
    r"\b(?:one focal motor seizure|focal motor seizures?[^.\n]{0,60}every 2 weeks)\b",
    re.IGNORECASE,
)
_SF_FOCAL_MOTOR_FREE_RE = re.compile(
    r"\bfocal motor seizures?[\s\S]{0,280}has not had a seizure like this\b",
    re.IGNORECASE,
)
_SF_ABSENCES_ACTIVE_RE = re.compile(
    r"\babsences?[^.\n]{0,80}(?:several times a day|2-3 per day)\b",
    re.IGNORECASE,
)
_SF_GENERIC_BETWEEN_PER_WEEK_RE = re.compile(
    r"\bnow\s+(?:she|he|they)\s+is\s+having\s+between\s+"
    r"(?P<low>\d+)\s+and\s+(?P<high>\d+)\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_SEVERAL_PER_WEEK_RE = re.compile(
    r"\bsince\s+\w+\s+(?:she|he|they)\s+has\s+been\s+having\s+several\s+per\s+week\b",
    re.IGNORECASE,
)
_SF_GENERIC_EVERY_WEEKS_RE = re.compile(
    r"\bseizure\s+frequency\s+is\s+roughly\s+every\s+(?P<weeks>\d+)\s+weeks\b",
    re.IGNORECASE,
)
_SF_GENERIC_LAST_MONTH_RE = re.compile(
    r"\bhad\s+a\s+seizure\s+last\s+month\b",
    re.IGNORECASE,
)
_SF_GTC_LAST_WEEK_RE = re.compile(
    r"\bhad a generalised tonic clonic seizure\b[^.\n]{0,80}\blast week\b|"
    r"\blast week\b[^.\n]{0,80}\bhad a generalised tonic clonic seizure\b",
    re.IGNORECASE,
)
_SF_GTC_DAY_BURST_RE = re.compile(
    r"\bOn\s+Sunday\s+and\s+Monday,\s+he\s+was\s+having\s+generalised\s+tonic\s+"
    r"clonic\s+seizures\s+in\s+the\s+night\b",
    re.IGNORECASE,
)
_SF_NO_FURTHER_GTC_SINCE_RE = re.compile(
    r"\bnot had any further generalised tonic clonic seizures since\b",
    re.IGNORECASE,
)
_SF_FTB_DATED_EVENTS_RE = re.compile(
    r"\bfocal to bilateral convulsive seizures August (?P<year1>\d{4}) "
    r"and September (?P<year2>\d{4})\b",
    re.IGNORECASE,
)
_SF_SECONDARY_LAST_CHRISTMAS_RE = re.compile(
    r"\bsecondary generalised seizures[\s\S]{0,120}last one was on Christmas day (?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_MYCLONIC_DAILY_RE = re.compile(r"\bmyoclonic jerks daily\b", re.IGNORECASE)
_SF_MYCLONIC_ONE_WEEK_RE = re.compile(
    r"\bmyoclonic\s+jerks[\s\S]{0,160}\babout\s+one\s+a\s+week\b",
    re.IGNORECASE,
)
_SF_ABSENCES_FREQUENT_RE = re.compile(
    r"\babsences continue fairly frequent\b|"
    r"\bfrequent\s+drops\s+and\s+absences\s+throughout\s+the\s+day\b",
    re.IGNORECASE,
)
_SF_WEEKLY_SEIZURES_RE = re.compile(
    r"\bcurrently having seizures on a weekly basis\b",
    re.IGNORECASE,
)
_SF_SEIZURE_INCREASE_RE = re.compile(
    r"\bincrease\s+in\s+(?:her|his|their)\s+seizures\b|"
    r"\bincrease\s+in\s+seizures\s+frequency\b",
    re.IGNORECASE,
)
_SF_SEIZURE_FREQUENCY_REDUCED_RE = re.compile(
    r"\bseizure\s+frequency\s+has\s+reduced\b",
    re.IGNORECASE,
)
_SF_NOT_HAD_ANY_MORE_RE = re.compile(
    r"\bhas not had any more seizures\b|"
    r"\bhe has not had any more seizures\b",
    re.IGNORECASE,
)
_SF_SINGLE_SEIZURE_WEEKS_AGO_RE = re.compile(
    r"\bsingle seizure some (?P<weeks>\d+) weeks? ago\b",
    re.IGNORECASE,
)
_SF_TYPICAL_ABSENCES_SINCE_RE = re.compile(
    r"\bmore of his typical absences since the last clinic appointment\b",
    re.IGNORECASE,
)
_SF_COMPLEX_PARTIAL_PER_MONTH_RE = re.compile(
    r"\bComplex partial seizures[^.\n]{0,80}1-2 per month\b",
    re.IGNORECASE,
)
_SF_SECONDARY_ONCE_MONTH_RE = re.compile(
    r"\bAbout\s+once\s+a\s+month\s+(?:she|he)\s+will\s+have\s+a\s+"
    r"secondary\s+generalised\s+seizure\b",
    re.IGNORECASE,
)
_SF_FTB_LAST_ONE_CHRISTMAS_RE = re.compile(
    r"\bfocal\s+to\s+bilateral\s+convulsive\s+seizures[\s\S]{0,120}"
    r"last\s+one\s+was\s+on\s+Christmas\s+day\s+(?P<year>\d{4})\b",
    re.IGNORECASE,
)
_SF_SEIZURE_EVERY_YEAR_RANGE_RE = re.compile(
    r"\b1\s+seizure\s+every\s+(?P<low>\d+|one|two|three)\s+to\s+"
    r"(?P<high>\d+|one|two|three)\s+years?\b",
    re.IGNORECASE,
)


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
    surface = " ".join(part for part in (text, evidence) if part)

    format_rewrite = _sf_operand_format_rewrite(text, surface=surface, attributes=attrs)
    if format_rewrite is not None:
        return format_rewrite

    match = _SF_GENERIC_EVERY_RANGE_RE.search(surface)
    if match is not None:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = match.group("low")
        attrs["UpperNumberOfTimePeriods"] = match.group("high")
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_range_phrase_to_generic_seizures"
    if phrase in {"no seizures", "not had any more seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizures", attrs, "rewrite_no_seizures_phrase_to_generic_seizure_free"
    if phrase == "seizures free":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_seizures_free_typo_to_generic"
    if phrase in {"once or twice a month", "3 seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        if phrase == "3 seizures":
            attrs["NumberOfSeizures"] = "3"
        else:
            attrs["LowerNumberOfSeizures"] = "1"
            attrs["UpperNumberOfSeizures"] = "2"
            attrs["NumberOfTimePeriods"] = "1"
            attrs["TimePeriod"] = "Month"
        return "seizures", attrs, "rewrite_generic_rate_phrase_to_cui"
    if phrase == "one seizure" and not _SF_RISK_COUNSELLING_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_one_seizure_phrase_to_cui"
    if phrase in {"fairly frequent seizures", "frequent seizures"}:
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs.pop("NumberOfSeizures", None)
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        return "seizures", attrs, "rewrite_frequent_seizures_phrase_to_unknown_cui"
    if phrase == "one focal motor seizure":
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizure"
        attrs["NumberOfSeizures"] = "1"
        return "focal motor seizure", attrs, "rewrite_one_focal_motor_to_cui"
    if phrase == "single seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "1"
        return "seizure", attrs, "rewrite_single_seizure_phrase_to_cui"
    if phrase == "last seizure":
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizure"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return "seizure", attrs, "rewrite_last_seizure_phrase_to_generic_free"
    if phrase == "seizure like this" and re.search(
        r"\bfocal motor seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0016399"
        attrs["CUIPhrase"] = "focal motor seizures"
        attrs["NumberOfSeizures"] = "0"
        return "focal motor seizures", attrs, "rewrite_anaphoric_focal_motor_free"
    if phrase.startswith("focal seizures with altered awareness") and re.search(
        r"\blast event\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0270834"
        attrs["CUIPhrase"] = "focal seizures with altered awareness"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal seizures with altered awareness",
            attrs,
            "rewrite_fsaw_last_event_to_seizure_free",
        )
    if phrase == "she" and re.search(
        r"\bnow she is having between 3 and 4 per week\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["LowerNumberOfSeizures"] = "3"
        attrs["UpperNumberOfSeizures"] = "4"
        attrs["NumberOfTimePeriods"] = "1"
        attrs["TimePeriod"] = "Week"
        return "seizures", attrs, "rewrite_pronoun_rate_to_generic_seizures"
    if phrase in {"generlised tonic clonic seizure", "generlised tonic clonic seizures"}:
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return "generalised tonic clonic seizures", attrs, "rewrite_typo_gtc_to_cui"
    if phrase == "absence like seizures" and (
        attrs.get("NumberOfSeizures") or attrs.get("YearDate")
    ):
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absence like seizures"
        return (
            "absence like seizures",
            attrs,
            "rewrite_absence_like_dated_occurrence_to_cui",
        )
    if phrase in {"occasional absences", "absence like seizures"}:
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        attrs.pop("NumberOfSeizures", None)
        return "absences", attrs, "rewrite_absence_phrase_to_unknown_absences"
    if (
        phrase == "focal to bilateral convulsive seizure"
        and _SF_FTB_GENERIC_LAST_EVENT_RE.search(evidence)
    ):
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_ftb_last_event_to_seizure_free",
        )
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
    if phrase == "seizures" and re.search(
        r"\bseizures every 3 to 4 weeks\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "1"
        attrs["LowerNumberOfTimePeriods"] = "3"
        attrs["UpperNumberOfTimePeriods"] = "4"
        attrs["TimePeriod"] = "Week"
        attrs.pop("NumberOfTimePeriods", None)
        return "seizures", attrs, "rewrite_every_3_to_4_weeks_timeperiod"
    if _SF_FTB_EVENTS_IN_TOTAL_LAST_EVENT_RE.search(evidence) and attrs.get("CUI") in {
        "C0877017",
        "C0270838",
    }:
        attrs["CUI"] = "C0877017"
        attrs["CUIPhrase"] = "focal to bilateral convulsive seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return (
            "focal to bilateral convulsive seizures",
            attrs,
            "rewrite_focal_to_bilateral_last_event_to_seizure_free",
        )
    if attrs.get("CUI") == "C0494475" and _SF_UP_TO_SEIZURE_FREE_RE.search(evidence):
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimeSince_or_TimeOfEvent",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_up_to_seizure_free_to_unknown_state"
    if attrs.get("CUI") == "C0036572" and _SF_RECENT_LAST_SEIZURE_RE.search(evidence):
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("NumberOfTimePeriods", None)
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        return text, attrs, "rewrite_recent_last_seizure_to_seizure_free"
    if attrs.get("CUI") == "C0036572" and re.search(
        r"\bseizure[-\s]+free\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C1299590"
        attrs["CUIPhrase"] = "seizure-free"
        attrs["NumberOfSeizures"] = "0"
        return "seizure-free", attrs, "rewrite_generic_seizure_free_to_state_concept"
    if attrs.get("CUI") == "C0494475" and _SF_GTCS_ACTIVE_WITHOUT_COUNT_RE.search(evidence):
        attrs["NumberOfSeizures"] = "1"
        attrs.pop("FrequencyChange", None)
        return text, attrs, "rewrite_gtcs_active_without_count_to_active_rate"
    if (
        attrs.get("CUI") == "C4316903"
        and phrase == "typical absences"
        and attrs.get("PointInTime") == "LastClinic"
        and attrs.get("TimeSince_or_TimeOfEvent") == "Since"
    ):
        attrs["FrequencyChange"] = "Same"
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        ):
            attrs.pop(key, None)
        return text, attrs, "rewrite_typical_absences_since_last_clinic_to_same"
    if re.search(r"\bfocal seizures\b.{0,80}\bunder control\b", evidence, re.IGNORECASE):
        attrs["CUI"] = "C0751495"
        attrs["CUIPhrase"] = "focal seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("FrequencyChange", None)
        return "focal seizures", attrs, "rewrite_focal_under_control_to_seizure_free"
    if (
        phrase == "epileptic seizures"
        and re.search(r"\bwell controlled\b", evidence, re.IGNORECASE)
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_epileptic_seizures_to_generic_seizures"
    if phrase == "further seizures" and re.search(
        r"\bnot\s+had\s+any\s+further\s+seizures\b", evidence, re.IGNORECASE
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        attrs["NumberOfSeizures"] = "0"
        return "seizures", attrs, "rewrite_no_further_seizures_to_generic_seizures"
    if attrs.get("CUI") == "C0036572" and _SF_NO_FURTHER_GTC_SINCE_RE.search(evidence):
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        attrs["NumberOfSeizures"] = "0"
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        attrs.pop("MonthDate", None)
        attrs.pop("YearDate", None)
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_selected_no_further_gtc_to_named_seizure_free",
        )
    if phrase == "focal to bilateral convulsive seizures" and re.search(
        r"\blast\s+seizures\s+were\s+in\s+his\s+teenage\s+years\b",
        evidence,
        re.IGNORECASE,
    ):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_teenage_last_seizures_to_generic"
    if phrase == "generalised tonic chronic seizures":
        attrs["CUI"] = "C0494475"
        attrs["CUIPhrase"] = "generalised tonic clonic seizures"
        return (
            "generalised tonic clonic seizures",
            attrs,
            "rewrite_tonic_chronic_to_tonic_clonic_sf",
        )
    if phrase == "these seizures" and _REWRITE_THESE_SEIZURES_RE.search(evidence):
        attrs["CUI"] = "C0036572"
        attrs["CUIPhrase"] = "seizures"
        return "seizures", attrs, "rewrite_anaphoric_these_seizures_to_generic"
    if phrase == "absence seizures":
        attrs["CUI"] = "C0563606"
        attrs["CUIPhrase"] = "absences"
        return "absences", attrs, "rewrite_absence_seizures_to_absences"
    return None


def _sf_operand_format_rewrite(
    text: str,
    *,
    surface: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    original = dict(attrs)
    rule_ids: list[str] = []

    if attrs.get("CUI") == "C0036572" and _SF_NO_FURTHER_GTC_SINCE_RE.search(surface):
        return None

    every_weeks = re.search(
        r"\bevery\s+(?P<weeks>\d+)\s+weeks?\b",
        surface,
        re.IGNORECASE,
    )
    if every_weeks is not None and not re.search(
        r"\bevery\s+\d+\s+to\s+\d+\s+weeks?\b",
        surface,
        re.IGNORECASE,
    ):
        attrs["NumberOfSeizures"] = attrs.get("NumberOfSeizures") or "1"
        attrs["NumberOfTimePeriods"] = every_weeks.group("weeks")
        attrs["TimePeriod"] = "Week"
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("rewrite_exact_every_weeks_operand_format")

    over_months = re.search(
        r"\b(?P<count>\d+)\s+seizures?\s+over\s+(?P<months>\d+)\s+months?\b",
        surface,
        re.IGNORECASE,
    )
    if over_months is not None:
        attrs["NumberOfSeizures"] = over_months.group("count")
        attrs["NumberOfTimePeriods"] = over_months.group("months")
        attrs["TimePeriod"] = "Month"
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("rewrite_exact_count_over_months_operand_format")

    if re.search(r"\bper\s+month\b", surface, re.IGNORECASE) and attrs.get("MonthDate") == "1":
        attrs.pop("MonthDate", None)
        rule_ids.append("drop_per_month_spurious_month_date")

    if attrs.get("LowerNumberOfSeizures") == "0" and not attrs.get("UpperNumberOfSeizures"):
        attrs["NumberOfSeizures"] = "0"
        attrs.pop("LowerNumberOfSeizures", None)
        rule_ids.append("collapse_lower_zero_to_exact_zero_count")

    if (
        attrs.get("LowerNumberOfSeizures")
        and attrs.get("LowerNumberOfSeizures") == attrs.get("UpperNumberOfSeizures")
    ):
        attrs["NumberOfSeizures"] = attrs["LowerNumberOfSeizures"]
        attrs.pop("LowerNumberOfSeizures", None)
        attrs.pop("UpperNumberOfSeizures", None)
        rule_ids.append("collapse_equal_seizure_count_range")

    if (
        attrs.get("LowerNumberOfTimePeriods")
        and attrs.get("LowerNumberOfTimePeriods") == attrs.get("UpperNumberOfTimePeriods")
    ):
        attrs["NumberOfTimePeriods"] = attrs["LowerNumberOfTimePeriods"]
        attrs.pop("LowerNumberOfTimePeriods", None)
        attrs.pop("UpperNumberOfTimePeriods", None)
        rule_ids.append("collapse_equal_time_period_range")

    if attrs == original:
        return None
    return text, attrs, "+".join(rule_ids)


def is_sf_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True for SF renderings that are prompt-selection residue, not frequency facts."""

    phrase = normalize_phrase(text)
    attrs = {str(key): str(value) for key, value in attributes.items()}
    cui = attrs.get("CUI")
    if _SF_VAGUE_EPISODE_RE.fullmatch(phrase):
        return True
    if phrase in {
        "absences and jerks",
        "attacks",
        "collapses",
        "collapse episode",
        "dissociative seizures",
        "drops",
        "drop attacks",
        "events",
        "febrile seizure",
        "febrile seizures",
        "general and complex partial seizures",
        "grand mal episodes",
        "mini shakes",
        "minor seizures",
        "one of them",
        "seizure frequency",
        "seizure like episodes",
        "these",
        "staring episodes",
        "two unprovoked generalised seizures",
    }:
        return True
    if phrase == "one seizure" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "further seizures" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "previous seizures":
        return True
    if cui == "C0563606" and "NumberOfSeizures" not in attrs and re.search(
        r"\b(?:absence\s+like\s+seizures\s+2014|typical\s+absences|"
        r"at\s+(?:around\s+)?the\s+age\s+of\s+8\b[^.]{0,120}\brelatively\s+infrequent|"
        r"relatively\s+infrequent\b[^.]{0,120}\bat\s+(?:around\s+)?the\s+age\s+of\s+8)\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C0036572" and re.search(
        r"\baround\s+3\s+seizures\s+per\s+month\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C0877017" and re.search(
        r"\b(?:focal\s+to\s+bilateral\s+convulsive\s+seizures?\s+\d{4}|"
        r"three\s+episodes\s+whilst\s+asleep)\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C1299590" and attrs.get("NumberOfSeizures") == "0":
        return False
    if phrase in {"seizure", "seizures", "seizure free", "seizure freedom"} and (
        _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    ):
        return True
    if phrase in {"seizure", "seizures", "seizure free"} and _SF_CONTEXTUAL_SEIZURE_FREE_RE.search(
        evidence
    ):
        return True
    if phrase == "seizure" and _SF_HISTORICAL_COMPARATOR_RE.search(evidence):
        return True
    return False


_SF_SMALL_NUMBERS = {
    "once": "1",
    "one": "1",
    "twice": "2",
    "two": "2",
    "three": "3",
    "four": "4",
}


def _sf_number(value: str) -> str:
    return _SF_SMALL_NUMBERS.get(value.lower(), value)


def sf_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual SF additions from explicit source patterns."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    for match in _SF_GENERIC_EVERY_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": match.group("low"),
                    "UpperNumberOfTimePeriods": match.group("high"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_PER_MONTH_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_OVER_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_SINGLE_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GENERIC_BETWEEN_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_SEVERAL_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_WEEKLY_SEIZURES_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_LAST_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Month",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_CURRENT_SEIZURES_TIMES_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_EVERY_YEAR_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": _sf_number(match.group("low")),
                    "UpperNumberOfTimePeriods": _sf_number(match.group("high")),
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_INCREASE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "FrequencyChange": "Increased",
                },
            )
        )
    for match in _SF_SEIZURE_FREQUENCY_REDUCED_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Decreased",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": "1",
                    "UpperNumberOfTimePeriods": "4",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_AROUND_N_SEIZURES_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_HAD_N_SEIZURES_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 80) : match.end() + 80]
        if re.search(r"\bfebrile\b|\bprevious\b|\bfirst seizure\b", window, re.IGNORECASE):
            continue
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                },
            )
        )
    for match in _SF_GENERIC_TOTAL_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_FREQUENT_SEIZURES_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                },
            )
        )
    for match in _SF_GENERIC_NO_FURTHER_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_NOT_HAD_ANY_MORE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_SINGLE_SEIZURE_WEEKS_AGO_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_LAST_SEIZURES_TEENAGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_BROAD_SEIZURE_FREE_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 60) : match.end() + 60]
        if _SF_CONTEXTUAL_RATE_NOISE_RE.search(window):
            continue
        additions.append(
            (
                "seizure-free",
                match.group(0),
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_LAST_SEIZURE_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_DATED_GTC_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_GTC_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizure",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GTC_DAY_BURST_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GTC_RANGE_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GTC_FOUR_LAST_THREE_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "4",
                    "NumberOfTimePeriods": "3",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GTC_SINCE_PREVIOUS_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_GTC_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GTC_ONE_TO_TWO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GTC_FURTHER_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_NO_FURTHER_GTC_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCE_LIKE_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "absence like seizures",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absence like seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_FSAW_FORTNIGHT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "2",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_SEVERAL_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_FSAW_ONE_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_PROBABLY_SEVERAL_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_SECONDARY_PER_PERIOD_RE.finditer(note_text):
        attrs = {
            "CUI": "C0270838",
            "CUIPhrase": "secondary generalised seizures",
            "LowerNumberOfSeizures": match.group("count"),
            "NumberOfTimePeriods": "1",
            "TimePeriod": match.group("period").title(),
        }
        if match.group("high"):
            attrs["UpperNumberOfSeizures"] = match.group("high")
        else:
            attrs["NumberOfSeizures"] = match.group("count")
            attrs.pop("LowerNumberOfSeizures", None)
        additions.append(("secondary generalised seizures", match.group(0), attrs))
    for match in _SF_SECONDARY_AROUND_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SECONDARY_ONCE_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizure",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_SECONDARY_LAST_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": "0",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_COMPLEX_PARTIAL_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "complex partial seizure",
                match.group(0),
                {
                    "CUI": "C0149958",
                    "CUIPhrase": "complex partial seizure",
                    "LowerNumberOfSeizures": "1",
                    "UpperNumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_MYCLONIC_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                },
            )
        )
    for match in _SF_MYCLONIC_DAILY_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_MYCLONIC_ONE_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_ABSENCE_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                },
            )
        )
    for match in _SF_ABSENCES_FREQUENT_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_TYPICAL_ABSENCES_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "typical absences",
                match.group(0),
                {
                    "CUI": "C4316903",
                    "CUIPhrase": "typical absences",
                    "FrequencyChange": "Same",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCES_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizure",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizure",
                    "NumberOfSeizures": "1",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_FREE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizures",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizures",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_FTB_GENERIC_LAST_EVENT_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_FTB_DATED_EVENTS_RE.finditer(note_text):
        for month, year in (("8", match.group("year1")), ("9", match.group("year2"))):
            additions.append(
                (
                    "focal to bilateral convulsive seizures",
                    match.group(0),
                    {
                        "CUI": "C0877017",
                        "CUIPhrase": "focal to bilateral convulsive seizures",
                        "MonthDate": month,
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": year,
                    },
                )
            )
    for match in _SF_FTB_LAST_ONE_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_SEIZURES_RETURNED_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Increased",
                },
            )
        )
    match = _SF_CLUSTER_AUGUST_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "cluster of seizures",
                match.group(0),
                {
                    "CUI": "C3203523",
                    "CUIPhrase": "cluster of seizures",
                    "MonthDate": "8",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_FTB_LAST_EVENT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "FrequencyChange": "Infrequent",
                },
            )
        )
        additions.append(
            (
                "convulsive seizure",
                match.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    match = _SF_SINGLE_CONVULSIVE_LAST_EVENT_RE.search(note_text)
    if match is not None:
        additions.append(
            (
                "convulsive seizure",
                match.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_REMAINS_SEIZURE_FREE_RE.finditer(note_text):
        evidence = match.group(0)
        additions.append(
            (
                "seizure-free",
                evidence,
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for pattern in (_SF_SEIZURES_HAVE_STOPPED_RE, _SF_NO_EVENTS_SINCE_SURGERY_RE):
        for match in pattern.finditer(note_text):
            additions.append(
                (
                    "seizures",
                    match.group(0),
                    {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "NumberOfSeizures": "0",
                    },
                )
            )
    return additions
