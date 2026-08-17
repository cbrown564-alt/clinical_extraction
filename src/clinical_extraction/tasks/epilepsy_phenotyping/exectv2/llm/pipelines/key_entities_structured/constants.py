"""Constants, regexes, and prompt-version helpers for the structured pipeline.

Pure relocation of the module-level constants from
``llm_only_key_entities_structured``. No logic changes.

After Decision 0056, the public names and machine identities are Full
ledger and Compact ledger. The older ``v0.9.24`` / ``v0.9.40`` strings
remain replay aliases. Study-only further-prune identities, including
``v0.9.44``, sit beside them; they are not Compact ledger. Mention
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

FULL_LEDGER = "exectv2_full_ledger"
COMPACT_LEDGER = "exectv2_compact_ledger"
PROMPT_VERSION_V0_9_24 = "exectv2_hybrid_key_family_event_ledger_v0.9.24"
PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.40_drop_encoding_non_sf_all_examples"
)
PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.41_cheap_drop_ix_pending_repeat"
)
PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.42_cheap_drop_scaffold_reprint"
)
PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.43_cheap_collapse_refuse"
)
PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.44_cheap_stack_further_prunes"
)
PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.40_combo_clinical_name"
)
FULL_LEDGER_DROP_EXAMPLES = "exectv2_full_ledger_drop_examples"
FULL_LEDGER_DROP_ENCODING_NON_SF = "exectv2_full_ledger_drop_encoding_non_sf"
COMPACT_LEDGER_FURTHER_PRUNE = "exectv2_compact_ledger_further_prune"
# Primary prompt version for the frozen six-model panel and current stack.
PROMPT_VERSION = FULL_LEDGER
_SUPPORTED_FULL_PROMPT_VERSIONS = frozenset(
    {
        FULL_LEDGER,
        COMPACT_LEDGER,
        PROMPT_VERSION_V0_9_24,
        PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT,
        PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT,
        PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE,
        PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES,
        PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME,
        FULL_LEDGER_DROP_EXAMPLES,
        FULL_LEDGER_DROP_ENCODING_NON_SF,
        COMPACT_LEDGER_FURTHER_PRUNE,
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

    if profile != "full":
        raise ValueError(f"unsupported prompt profile {profile!r}; expected 'full'")
    selected = prompt_version or PROMPT_VERSION
    if selected not in _SUPPORTED_FULL_PROMPT_VERSIONS:
        raise ValueError(
            f"unsupported prompt version {selected!r}; "
            f"expected one of {sorted(_SUPPORTED_FULL_PROMPT_VERSIONS)}"
        )
    return selected
