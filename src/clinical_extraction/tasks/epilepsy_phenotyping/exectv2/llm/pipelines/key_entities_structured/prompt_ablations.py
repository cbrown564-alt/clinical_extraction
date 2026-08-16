"""Retained cheap-stack drop from the frozen v0.9.24 structured prompt.

``v0.9.40_drop_encoding_non_sf_all_examples`` is the live cheap slot.
The v0.9.41–v0.9.44 identities are study-only further prunes of that
slot. Intermediate leave-one-out prune arms are lineage in git history.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prompt_further_prune import (
    IX_PENDING,
    REFUSE_CHORUS,
    SCAFFOLD_REPRINT,
    STACKED_PRUNES,
    apply_further_prune,
)
from .prompt_plain_language import apply_plain_language

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

# Non-SF encoding rules from the 2026-08-15 convention catalog (16 rules).
_ENCODING_NON_SF = frozenset(
    {
        "rule-11",
        "rule-12",
        "rule-14",
        "rule-16",
        "rule-19",
        "rule-20",
        "rule-21",
        "rule-22",
        "rule-28",
        "rule-29",
        "rule-31",
        "rule-32",
        "rule-68",
        "rule-78",
        "rule-79",
        "rule-80",
    }
)


@dataclass(frozen=True)
class AblationSpec:
    version: str
    drop_payload_keys: frozenset[str] = frozenset()
    drop_examples: bool = False
    drop_example_ids: frozenset[str] = frozenset()
    drop_rule_ids: frozenset[str] = frozenset()
    task: str | None = None
    plain_language: bool = False
    further_prunes: tuple[str, ...] = ()


ABLATION_SPECS: dict[str, AblationSpec] = {
    PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES: AblationSpec(
        version=PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
    ),
    PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT: AblationSpec(
        version=PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        further_prunes=(IX_PENDING,),
    ),
    PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT: AblationSpec(
        version=PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        further_prunes=(SCAFFOLD_REPRINT,),
    ),
    PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE: AblationSpec(
        version=PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        further_prunes=(REFUSE_CHORUS,),
    ),
    PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES: AblationSpec(
        version=PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        further_prunes=STACKED_PRUNES,
    ),
}


def rule_id_for_index(index: int) -> str:
    return f"rule-{index + 1:02d}"


def example_id_for_index(index: int) -> str:
    return f"example-{index + 1:02d}"


def apply_v0924_ablation(payload: dict[str, Any], spec: AblationSpec) -> dict[str, Any]:
    """Return a copy of the v0.9.24 payload with one named slice removed."""

    ablated = dict(payload)
    ablated["prompt_version"] = spec.version
    if spec.task is not None:
        ablated["task"] = spec.task
    for key in spec.drop_payload_keys:
        ablated.pop(key, None)
    if spec.drop_examples:
        ablated.pop("worked_examples", None)
    elif spec.drop_example_ids:
        examples = list(ablated.get("worked_examples") or [])
        ablated["worked_examples"] = [
            example
            for index, example in enumerate(examples)
            if example_id_for_index(index) not in spec.drop_example_ids
        ]
    if spec.drop_rule_ids:
        rules = list(ablated["clinical_rules"])
        ablated["clinical_rules"] = [
            rule
            for index, rule in enumerate(rules)
            if rule_id_for_index(index) not in spec.drop_rule_ids
        ]
    if spec.plain_language:
        ablated = apply_plain_language(ablated)
    for kind in spec.further_prunes:
        ablated = apply_further_prune(ablated, kind)
    return ablated
