"""FrequencyChange extraction rules for ExECTv2.

Gold closed vocab: {Decreased, Frequent, Increased, Infrequent, Same}.
These rules extract mentions where the dominant clinical information is a
direction-of-change rather than a count — e.g. "frequency has decreased".
"""

from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import SEIZURE_TERMS

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleGroup,
)

_SEIZURE_NOUN = rf"(?:seizure|{SEIZURE_TERMS})\s+(?:frequency|rate|burden|control)"


def _change_candidate(
    match: re.Match[str],
    change_value: str,
    rule_id: str,
) -> AttributeExtraction:
    evidence = clean_span(match.group(0))
    return AttributeExtraction(
        evidence=evidence,
        span=(match.start(), match.end()),
        attributes={"FrequencyChange": change_value},
        kind=AttributeKind.FREQUENCY_CHANGE,
        rule_id=rule_id,
        rule_group=RuleGroup.FREQUENCY_CHANGE,
        portability=Portability.CLINICAL_EPILEPSY,
    )


# ---------------------------------------------------------------------------
# Decreased
# ---------------------------------------------------------------------------


def _build_decreased(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Decreased", "change.decreased")


# ---------------------------------------------------------------------------
# Increased
# ---------------------------------------------------------------------------


def _build_increased(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Increased", "change.increased")


# ---------------------------------------------------------------------------
# Same / Unchanged
# ---------------------------------------------------------------------------


def _build_same(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Same", "change.same")


# ---------------------------------------------------------------------------
# Infrequent
# ---------------------------------------------------------------------------


def _build_infrequent(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Infrequent", "change.infrequent")


# ---------------------------------------------------------------------------
# Frequent
# ---------------------------------------------------------------------------


def _build_frequent(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _change_candidate(match, "Frequent", "change.frequent")


# RuleSpec metadata: sf_surface_registry/catalog/extract.yaml
# Assembled via sf_surface_registry/adapters/extraction.py

from .extract_impl_types import ExtractRuleImpl

CHANGE_EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
    "change.decreased": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?|episodes?|events?)\\s+(?:(?:has|have)\\s+)?(?:decreased|reduced|improved|declined|lessened)|(?:decreased|reduced|improvement\\s+in)\\s+(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizure\\s+(?:frequency|burden)|seizures?)|(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?)\\s+(?:are|is)\\s+(?:decreased|reduced|better\\s+controlled|less\\s+frequent))\\b",
            re.IGNORECASE,
        ),
        _build_decreased,
    ),
    "change.increased": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?|episodes?|events?)\\s+(?:(?:has|have)\\s+)?(?:increased|worsened|escalated|risen)|(?:increased|increase\\s+in|worsening\\s+of)\\s+(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?)|(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?)\\s+(?:are|is)\\s+(?:increased|more\\s+frequent|worse))\\b",
            re.IGNORECASE,
        ),
        _build_increased,
    ),
    "change.same": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizures?)\\s+(?:(?:remain(?:s)?|are|is)\\s+)?(?:unchanged|stable|the\\s+same)|no\\s+change\\s+in\\s+(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizure\\s+(?:frequency|pattern))|(?:unchanged|stable)\\s+(?:(?:seizure|seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+(?:frequency|rate|burden|control)|seizure\\s+(?:frequency|pattern)))\\b",
            re.IGNORECASE,
        ),
        _build_same,
    ),
    "change.infrequent": ExtractRuleImpl(
        re.compile(
            "\\b(?:infrequent|infrequently|rare)\\s+(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|seizures?|episodes?)\\b|\\b(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|seizures?|episodes?)\\s+(?:are\\s+)?(?:infrequent|rare)\\b",
            re.IGNORECASE,
        ),
        _build_infrequent,
    ),
    "change.frequent": ExtractRuleImpl(
        re.compile(
            "\\b(?:frequent|frequently|high.?frequency)\\s+(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|seizures?|episodes?)\\b|\\b(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|seizures?|episodes?)\\s+(?:are\\s+)?(?:frequent|occurring\\s+frequently)\\b",
            re.IGNORECASE,
        ),
        _build_frequent,
    ),
}
