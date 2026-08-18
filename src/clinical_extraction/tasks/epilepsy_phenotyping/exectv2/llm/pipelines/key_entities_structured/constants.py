"""Constants, regexes, and prompt-version helpers for the structured pipeline.

Pure relocation of the module-level constants from
``llm_only_key_entities_structured``. No logic changes.

Paper names ``exect_llm_with_rules`` and ``exect_full_ledger`` are
aliases of Compact and Full. The older ``exectv2_*`` strings remain
the live default and replay aliases until paper cells are rewritten.
Dump, further-prune, and naming-graft identities are gone. Mention
encoder lives in ``mention_unit.py``, not this registry.
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

EXECT_LLM_WITH_RULES = "exect_llm_with_rules"
EXECT_LLM_ONLY = "exect_llm_only"
EXECT_FULL_LEDGER = "exect_full_ledger"
FULL_LEDGER = "exectv2_full_ledger"
COMPACT_LEDGER = "exectv2_compact_ledger"
FULL_VERSIONS = frozenset({FULL_LEDGER, EXECT_FULL_LEDGER})
COMPACT_VERSIONS = frozenset({COMPACT_LEDGER, EXECT_LLM_WITH_RULES})
LLM_ONLY_VERSIONS = frozenset({EXECT_LLM_ONLY})
FLAT_SCHEMA_VERSIONS = COMPACT_VERSIONS | LLM_ONLY_VERSIONS
# Live default is Compact hybrid. Full stays as the cited comparator.
PROMPT_VERSION = COMPACT_LEDGER
_SUPPORTED_PROMPT_VERSIONS = FULL_VERSIONS | FLAT_SCHEMA_VERSIONS
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
    "medication", "diagnosis", "seizure_frequency", "investigation", "history"
]
ALLOWED_EVENT_FAMILIES = {
    "medication",
    "diagnosis",
    "seizure_frequency",
    "investigation",
    "history",
}
FAMILY_TO_ENTITY = {
    "medication": PRESCRIPTION.name,
    "diagnosis": DIAGNOSIS.name,
    "seizure_frequency": SEIZURE_FREQUENCY.name,
    "investigation": INVESTIGATIONS.name,
    "history": "History",
}
PromptProfile = Literal["full"]

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


def set_active_prompt_version(version: str) -> None:
    """Select the full-profile prompt version emitted by build_prompt_input."""

    global PROMPT_VERSION
    if version not in _SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {version!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)}"
        )
    PROMPT_VERSION = version


def prompt_version_for(
    profile: PromptProfile = "full",
    *,
    prompt_version: str | None = None,
) -> str:
    """Resolve the prompt identity for a profile and optional override."""

    if profile != "full":
        raise ValueError(f"unsupported prompt profile {profile!r}; expected 'full'")
    selected = prompt_version or PROMPT_VERSION
    if selected not in _SUPPORTED_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {selected!r}; "
            f"expected one of {sorted(_SUPPORTED_PROMPT_VERSIONS)}"
        )
    return selected
