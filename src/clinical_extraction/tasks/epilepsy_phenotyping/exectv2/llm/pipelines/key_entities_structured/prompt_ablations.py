"""Retained cheap-stack drop from the frozen v0.9.24 structured prompt.

Only ``v0.9.40_drop_encoding_non_sf_all_examples`` remains live. Intermediate
leave-one-out prune arms are lineage in git history, not parallel live IDs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.40_drop_encoding_non_sf_all_examples"
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
        "rule-33",
        "rule-37",
        "rule-38",
        "rule-48",
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


ABLATION_SPECS: dict[str, AblationSpec] = {
    PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES: AblationSpec(
        version=PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
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
    return ablated
