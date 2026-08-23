"""Constants, regexes, and prompt-version helpers for the structured pipeline.

Pure relocation of the module-level constants from
``llm_only_key_entities_structured``. No logic changes.

Paper names ``exect_llm_pre_post`` and ``exect_llm_extract`` are the
living methods. ``exect_llm_extract_filtered`` is the Compact extract
ablation. Legacy prompt strings are accepted on read only via
``LEGACY_PROMPT_VERSION_ALIASES``.
"""

from __future__ import annotations

import re
from typing import Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)

EXECT_LLM_PRE_POST = "exect_llm_pre_post"
EXECT_LLM_WITH_RULES = "exect_llm_with_rules"
EXECT_LLM_EXTRACT = "exect_llm_extract"
EXECT_LLM_EXTRACT_FILTERED = "exect_llm_extract_filtered"
EXECT_LLM_ONLY = "exect_llm_only"
EXECT_LLM_INVENTORY = "exect_llm_inventory"
COMPACT_LEDGER = "exectv2_compact_ledger"

LEGACY_PROMPT_VERSION_ALIASES: dict[str, str] = {
    EXECT_LLM_WITH_RULES: EXECT_LLM_PRE_POST,
    EXECT_LLM_ONLY: EXECT_LLM_EXTRACT_FILTERED,
    EXECT_LLM_INVENTORY: EXECT_LLM_EXTRACT,
}

COMPACT_VERSIONS = frozenset({COMPACT_LEDGER})
BOTH_EXTRACT_VERSIONS = frozenset({EXECT_LLM_PRE_POST})
LLM_ONLY_VERSIONS = frozenset({EXECT_LLM_EXTRACT_FILTERED})
INVENTORY_VERSIONS = frozenset({EXECT_LLM_EXTRACT})
PROMPT_VERSION = EXECT_LLM_PRE_POST
_SUPPORTED_PROMPT_VERSIONS = (
    COMPACT_VERSIONS | BOTH_EXTRACT_VERSIONS | LLM_ONLY_VERSIONS | INVENTORY_VERSIONS
)
PIPELINE_FAMILY = "exectv2_hybrid_key_family_event_ledger"
COMPONENT_OWNER = "hybrid_key_family_event_ledger"

KEY_ENTITY_NAMES: tuple[str, ...] = (
    PRESCRIPTION.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    INVESTIGATIONS.name,
)

KEY_ENTITY_ITEM_F1_TARGET = 0.80
PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "Prescription": 0.87,
    "Diagnosis": 0.85,
    "SeizureFrequency": 0.66,
    "Investigations": 0.95,
}

EventFamily = Literal[
    "medication", "diagnosis", "seizure_frequency", "investigation"
]
ALLOWED_EVENT_FAMILIES = {
    "medication",
    "diagnosis",
    "seizure_frequency",
    "investigation",
}
FAMILY_TO_ENTITY = {
    "medication": PRESCRIPTION.name,
    "diagnosis": DIAGNOSIS.name,
    "seizure_frequency": SEIZURE_FREQUENCY.name,
    "investigation": INVESTIGATIONS.name,
}
_MEDICATION_RE = re.compile(
    r"\b("
    r"lamotrigine|lamictal|levetiracetam|keppra|brivaracetam|sodium valproate|"
    r"valproate|eplim|carbamazepine|tegretol|topiramate|clobazam|clonazepam|"
    r"midazolam|lacosamide|vimpat|zonisamide|phenobarbital|phenytoin|"
    r"oxcarbazepine|gabapentin|pregabalin|perampanel|eslicarbazepine"
    r")\b",
    re.IGNORECASE,
)
_INVESTIGATION_RE = re.compile(
    r"\b(MRI|CT|EEG|VEEG|video\s+EEG|video[- ]telemetry|telemetry)\b",
    re.IGNORECASE,
)
_DIAGNOSIS_RE = re.compile(
    r"\b("
    r"epilepsy|seizure disorder|focal epilepsy|temporal lobe epilepsy|"
    r"generalised epilepsy|generalized epilepsy|JME|juvenile myoclonic epilepsy|"
    r"tonic[- ]clonic seizures?|tonic[- ]chronic seizures?|"
    r"generalised tonic[- ]clonic seizures?|generalized tonic[- ]clonic seizures?|"
    r"focal seizures?|focal to bilateral(?: convulsive)? seizures?|"
    r"absence(?:-like)? seizures?|complex partial seizures?|dyscognitive seizures?|"
    r"myoclonic seizures?"
    r")\b",
    re.IGNORECASE,
)
_SEIZURE_STATE_RE = re.compile(
    r"\b("
    r"seizures?|seizure[- ]free|last event|last seizure|no further|no more|"
    r"not had|per|every|daily|weekly|monthly|yearly|few|several|cluster|"
    r"returned|frequent|infrequent|controlled|under control|increased|decreased"
    r")\b",
    re.IGNORECASE,
)


def canonicalize_prompt_version(version: str) -> str:
    """Map legacy Compact prompt strings to the living paper name."""

    return LEGACY_PROMPT_VERSION_ALIASES.get(version, version)


def set_active_prompt_version(version: str) -> None:
    """Select the full-profile prompt version emitted by build_prompt_input."""

    global PROMPT_VERSION
    selected = canonicalize_prompt_version(version)
    if selected not in _SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {version!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)} "
            f"or legacy aliases {sorted(LEGACY_PROMPT_VERSION_ALIASES)}"
        )
    PROMPT_VERSION = selected


def prompt_version_for(*, prompt_version: str | None = None) -> str:
    """Resolve the living Compact prompt identity."""

    selected = canonicalize_prompt_version(prompt_version or PROMPT_VERSION)
    if selected not in _SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {selected!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)}"
        )
    return selected
