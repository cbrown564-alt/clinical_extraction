"""Shared constants for the LLM-first essential clinical evaluation package."""

from __future__ import annotations

import re
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)

CERTAINTY = "Certainty"
NEGATION = "Negation"
CUI = "CUI"
CUI_PHRASE = "CUIPhrase"
CERTAINTY_ATTRS = frozenset({CERTAINTY, NEGATION})

GUIDELINE_CERTAINTY_ENTITIES = frozenset(
    {
        "BirthHistory",
        DIAGNOSIS.name,
        EPILEPSY_CAUSE.name,
        "Onset",
        "PatientHistory",
        "WhenDiagnosed",
    }
)
GUIDELINE_NEGATION_ENTITIES = GUIDELINE_CERTAINTY_ENTITIES
GUIDELINE_CERTAINTY_TRIGGERS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "guideline_certainty_triggers.yaml"
)

FEBRILE_HISTORY = re.compile(r"\bfebrile\s+(?:seizures?|convulsions?)\b", re.IGNORECASE)
NEGATED_FEBRILE_HISTORY = re.compile(
    r"\b(?:no|not|never|denies?|denied|without)\b.{0,60}\bfebrile\s+"
    r"(?:seizures?|convulsions?)\b|\bfebrile\s+(?:seizures?|convulsions?)\b"
    r".{0,60}\b(?:absent|denied|negated)\b",
    re.IGNORECASE | re.DOTALL,
)

ESSENTIAL_CLINICAL_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    SEIZURE_FREQUENCY.name,
    DIAGNOSIS.name,
    EPILEPSY_CAUSE.name,
    INVESTIGATIONS.name,
)
ESSENTIAL_ATOMIC_CONCEPT_ONLY = frozenset({DIAGNOSIS.name, EPILEPSY_CAUSE.name})

OWNERSHIP_RULES_ONLY = "rules_only"
OWNERSHIP_LLM_FIRST = "llm_first"
OWNERSHIP_HYBRID = "hybrid"

ERROR_TYPES: tuple[str, ...] = (
    "candidate_miss",
    "wrong_detail_selection",
    "projection_gap",
    "evidence_failure",
)
