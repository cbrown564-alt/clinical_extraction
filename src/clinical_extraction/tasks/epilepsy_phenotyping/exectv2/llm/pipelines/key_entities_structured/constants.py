"""Constants, regexes, and prompt-version helpers for the structured pipeline.

Pure relocation of the module-level constants from
``llm_only_key_entities_structured``. No logic changes.
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

PROMPT_VERSION_V0_9_24 = "exectv2_hybrid_key_family_event_ledger_v0.9.24"
PROMPT_VERSION_V10 = "exectv2_hybrid_key_family_event_ledger_v10"
PROMPT_VERSION_V11 = "exectv2_hybrid_key_family_event_ledger_v11"
PROMPT_VERSION_V12 = "exectv2_hybrid_key_family_event_ledger_v12"
PROMPT_VERSION_V13 = "exectv2_hybrid_key_family_event_ledger_v13"
PROMPT_VERSION_V14 = "exectv2_hybrid_key_family_event_ledger_v14"
PROMPT_VERSION_V15 = "exectv2_hybrid_key_family_event_ledger_v15"
PROMPT_VERSION_V16 = "exectv2_hybrid_key_family_event_ledger_v16"
PROMPT_VERSION_V17 = "exectv2_hybrid_key_family_event_ledger_v17"
PROMPT_VERSION_V18 = "exectv2_hybrid_key_family_event_ledger_v18"
PROMPT_VERSION_V19 = "exectv2_hybrid_key_family_event_ledger_v19"
PROMPT_VERSION_V20 = "exectv2_hybrid_key_family_event_ledger_v20"
PROMPT_VERSION_V21 = "exectv2_hybrid_key_family_event_ledger_v21"
PROMPT_VERSION_V22 = "exectv2_hybrid_key_family_event_ledger_v22"
PROMPT_VERSION_V23 = "exectv2_hybrid_key_family_event_ledger_v23"
PROMPT_VERSION_V24 = "exectv2_hybrid_key_family_event_ledger_v24"
PROMPT_VERSION_V25 = "exectv2_hybrid_key_family_event_ledger_v25"
PROMPT_VERSION_V26 = "exectv2_hybrid_key_family_event_ledger_v26"
PROMPT_VERSION_V0_9_25_LUNA_SF_STATE = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.25_luna_sf_state"
)
PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.25_luna_sf_boundary_dx"
)
# Primary prompt version for the frozen six-model panel. Luna v0.9.25 variants,
# the v10 contract study, and v11–v26 are development candidates
# only; they must not replace v0.9.24 in place.
PROMPT_VERSION = PROMPT_VERSION_V0_9_24
QWEN_COMPACT_PROMPT_VERSION = "exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact"
_SUPPORTED_FULL_PROMPT_VERSIONS = frozenset(
    {
        PROMPT_VERSION_V0_9_24,
        PROMPT_VERSION_V10,
        PROMPT_VERSION_V11,
        PROMPT_VERSION_V12,
        PROMPT_VERSION_V13,
        PROMPT_VERSION_V14,
        PROMPT_VERSION_V15,
        PROMPT_VERSION_V16,
        PROMPT_VERSION_V17,
        PROMPT_VERSION_V18,
        PROMPT_VERSION_V19,
        PROMPT_VERSION_V20,
        PROMPT_VERSION_V21,
        PROMPT_VERSION_V22,
        PROMPT_VERSION_V23,
        PROMPT_VERSION_V24,
        PROMPT_VERSION_V25,
        PROMPT_VERSION_V26,
        PROMPT_VERSION_V0_9_25_LUNA_SF_STATE,
        PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX,
    }
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
PromptProfile = Literal["full", "qwen_compact"]

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
    if version not in _SUPPORTED_FULL_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {version!r}; "
            f"expected one of {sorted(_SUPPORTED_FULL_PROMPT_VERSIONS)}"
        )
    PROMPT_VERSION = version


def prompt_version_for(
    profile: PromptProfile = "full",
    *,
    prompt_version: str | None = None,
) -> str:
    """Resolve the prompt identity for a profile and optional override."""

    if profile == "qwen_compact":
        if prompt_version is not None and prompt_version != QWEN_COMPACT_PROMPT_VERSION:
            raise ValueError(
                "qwen_compact profile only supports "
                f"{QWEN_COMPACT_PROMPT_VERSION!r}, got {prompt_version!r}"
            )
        return QWEN_COMPACT_PROMPT_VERSION
    selected = prompt_version or PROMPT_VERSION
    if selected not in _SUPPORTED_FULL_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {selected!r}; "
            f"expected one of {sorted(_SUPPORTED_FULL_PROMPT_VERSIONS)}"
        )
    return selected
