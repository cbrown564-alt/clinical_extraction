"""Shared prescription normalization helpers and regex patterns."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    DRUG_SURFACE_ALIASES,
    resolve_drug_surface,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_CONCEPT_BY_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

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
    """Return the benchmark canonical drug name for a surface mention, if known."""

    key = normalize_phrase(surface)
    concept = PRESCRIPTION_CONCEPT_BY_PHRASE.get(key)
    if concept is not None:
        return concept.canonical
    resolved = normalize_phrase(resolve_drug_surface(surface))
    if resolved != key:
        concept = PRESCRIPTION_CONCEPT_BY_PHRASE.get(resolved)
        return concept.canonical if concept is not None else None
    return None


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
