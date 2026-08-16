"""Leave-one-out drops from the frozen v0.9.24 structured prompt.

Each candidate keeps the v0.9.24 schema, family guidance, vocabulary,
and hybrid stack. One named slice is removed. Rule-class membership
is the 2026-08-15 convention catalog. Do not load that JSON at
runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.26_drop_scaffold"
)
PROMPT_VERSION_V0_9_27_DROP_EXAMPLES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.27_drop_examples"
)
PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.28_drop_encoding_rules"
)
PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.29_drop_scope_rules"
)

_SCAFFOLD_TASK = (
    "Read the clinical letter once. Build a compact list of source-near "
    "clinical events for medication, diagnosis, seizure frequency, and "
    "investigations. Each event may render one or more entity mentions when "
    "the same clinical fact validly belongs to more than one requested family."
)

_SCAFFOLD_KEYS = frozenset(
    {
        "architecture",
        "decision_procedure",
        "candidate_evidence_ledger",
        "event_lane_guide",
    }
)
_JUNK_LEDGER_RULES = frozenset({"rule-01", "rule-02", "rule-03", "rule-04"})
_ENCODING_RULES = frozenset(
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
        "rule-49",
        "rule-50",
        "rule-51",
        "rule-52",
        "rule-53",
        "rule-54",
        "rule-55",
        "rule-56",
        "rule-58",
        "rule-68",
        "rule-78",
        "rule-79",
        "rule-80",
    }
)
_SCOPE_RULES = frozenset(
    {
        "rule-15",
        "rule-17",
        "rule-18",
        "rule-24",
        "rule-25",
        "rule-26",
        "rule-30",
        "rule-41",
        "rule-42",
        "rule-43",
        "rule-44",
        "rule-45",
        "rule-46",
        "rule-47",
        "rule-57",
        "rule-59",
        "rule-60",
        "rule-61",
        "rule-66",
        "rule-72",
        "rule-73",
        "rule-74",
        "rule-75",
        "rule-76",
        "rule-77",
    }
)


@dataclass(frozen=True)
class AblationSpec:
    version: str
    drop_payload_keys: frozenset[str] = frozenset()
    drop_examples: bool = False
    drop_rule_ids: frozenset[str] = frozenset()
    task: str | None = None


ABLATION_SPECS: dict[str, AblationSpec] = {
    PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD: AblationSpec(
        version=PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD,
        drop_payload_keys=_SCAFFOLD_KEYS,
        drop_rule_ids=_JUNK_LEDGER_RULES,
        task=_SCAFFOLD_TASK,
    ),
    PROMPT_VERSION_V0_9_27_DROP_EXAMPLES: AblationSpec(
        version=PROMPT_VERSION_V0_9_27_DROP_EXAMPLES,
        drop_examples=True,
    ),
    PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES: AblationSpec(
        version=PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES,
        drop_rule_ids=_ENCODING_RULES,
    ),
    PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES: AblationSpec(
        version=PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES,
        drop_rule_ids=_SCOPE_RULES,
    ),
}


def rule_id_for_index(index: int) -> str:
    return f"rule-{index + 1:02d}"


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
    if spec.drop_rule_ids:
        rules = list(ablated["clinical_rules"])
        ablated["clinical_rules"] = [
            rule
            for index, rule in enumerate(rules)
            if rule_id_for_index(index) not in spec.drop_rule_ids
        ]
    return ablated
