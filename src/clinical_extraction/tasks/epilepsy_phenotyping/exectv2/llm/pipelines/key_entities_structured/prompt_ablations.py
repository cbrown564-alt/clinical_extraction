"""Compact-ledger cut from the Full-ledger structured prompt.

``exectv2_compact_ledger`` and ``exect_llm_with_rules`` are the same
payload: authored order, no ``letter_id`` or ``prompt_version``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .constants import (
    COMPACT_LEDGER,
    EXECT_LLM_WITH_RULES,
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
COMPACT_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "categories",
    "clinical_rules",
    "suggested_evidence",
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
    authored_order: bool = False


def _compact_spec(version: str) -> AblationSpec:
    return AblationSpec(
        version=version,
        drop_examples=True,
        drop_rule_ids=_ENCODING_NON_SF,
        plain_language=True,
        authored_order=True,
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
    EXECT_LLM_WITH_RULES: _compact_spec(EXECT_LLM_WITH_RULES),
    COMPACT_LEDGER: _compact_spec(COMPACT_LEDGER),
}


def rule_id_for_index(index: int) -> str:
    return f"rule-{index + 1:02d}"


def example_id_for_index(index: int) -> str:
    return f"example-{index + 1:02d}"


def apply_v0924_ablation(payload: dict[str, Any], spec: AblationSpec) -> dict[str, Any]:
    """Return a copy of the Full-ledger payload with the Compact cut applied."""

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
    return ablated
