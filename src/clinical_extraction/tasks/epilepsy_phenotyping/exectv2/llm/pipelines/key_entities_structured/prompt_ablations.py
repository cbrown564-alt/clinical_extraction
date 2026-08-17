"""Retained Compact-ledger drop from the Full-ledger structured prompt.

``exectv2_compact_ledger`` is the living Compact identity: authored
order, no ``letter_id`` or ``prompt_version``. The older ``v0.9.40``
string keeps the current-run dump so saved raws still replay. The
v0.9.41–v0.9.44 identities are historical further prunes of that
current-run dump. Intermediate leave-one-out prune arms are lineage
in git history.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .constants import (
    COMPACT_LEDGER,
    COMPACT_LEDGER_FURTHER_PRUNE,
    FULL_LEDGER_DROP_ENCODING_NON_SF,
    FULL_LEDGER_DROP_EXAMPLES,
    PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME,
    PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
    PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT,
    PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT,
    PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE,
    PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES,
)
from .prompt_further_prune import (
    COMBO_CLINICAL_NAME,
    IX_PENDING,
    REFUSE_CHORUS,
    SCAFFOLD_REPRINT,
    STACKED_PRUNES,
    apply_further_prune,
)
from .prompt_plain_language import apply_plain_language

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


AUTHORED_KEY_ORDER = (
    "task",
    "architecture",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "categories",
    "event_lane_guide",
    "clinical_rules",
    "suggested_evidence",
    "candidate_evidence_ledger",
    "worked_examples",
    "letter_text",
)
RESEARCH_METADATA_KEYS = frozenset({"letter_id", "prompt_version"})


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
    authored_order: bool = False


def _compact_spec(
    version: str,
    *,
    further_prunes: tuple[str, ...] = (),
    authored_order: bool = False,
) -> AblationSpec:
    return AblationSpec(
        version=version,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        further_prunes=further_prunes,
        authored_order=authored_order,
    )


def dump_model_facing_payload(
    payload: dict[str, Any], *, authored_order: bool
) -> str:
    """Serialize a structured prompt. Authored order omits research metadata."""

    if not authored_order:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
    visible = {
        key: value
        for key, value in payload.items()
        if key not in RESEARCH_METADATA_KEYS
    }
    ordered: dict[str, Any] = {}
    for key in AUTHORED_KEY_ORDER:
        if key in visible:
            ordered[key] = visible.pop(key)
    for key in sorted(visible):
        ordered[key] = visible[key]
    return json.dumps(ordered, ensure_ascii=False)


ABLATION_SPECS: dict[str, AblationSpec] = {
    COMPACT_LEDGER: _compact_spec(COMPACT_LEDGER, authored_order=True),
    FULL_LEDGER_DROP_EXAMPLES: AblationSpec(
        version=FULL_LEDGER_DROP_EXAMPLES,
        drop_examples=True,
        authored_order=True,
    ),
    FULL_LEDGER_DROP_ENCODING_NON_SF: AblationSpec(
        version=FULL_LEDGER_DROP_ENCODING_NON_SF,
        drop_rule_ids=_ENCODING_NON_SF,
        authored_order=True,
    ),
    COMPACT_LEDGER_FURTHER_PRUNE: _compact_spec(
        COMPACT_LEDGER_FURTHER_PRUNE,
        further_prunes=STACKED_PRUNES,
        authored_order=True,
    ),
    PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES: _compact_spec(
        PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
    ),
    PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT: _compact_spec(
        PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT,
        further_prunes=(IX_PENDING,),
    ),
    PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT: _compact_spec(
        PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT,
        further_prunes=(SCAFFOLD_REPRINT,),
    ),
    PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE: _compact_spec(
        PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE,
        further_prunes=(REFUSE_CHORUS,),
    ),
    PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES: _compact_spec(
        PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES,
        further_prunes=STACKED_PRUNES,
    ),
    PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME: _compact_spec(
        PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME,
        further_prunes=(COMBO_CLINICAL_NAME,),
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
