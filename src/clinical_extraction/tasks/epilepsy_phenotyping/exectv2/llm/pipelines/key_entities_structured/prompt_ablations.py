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
PROMPT_VERSION_V0_9_30_DROP_SCAFFOLD_EXAMPLES = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.30_drop_scaffold_examples"
)
PROMPT_VERSION_V0_9_31_DROP_SCAFFOLD_EXAMPLES_ENCODING = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.31_drop_scaffold_examples_encoding"
)
PROMPT_VERSION_V0_9_32_DROP_SCOPE_SF_REFUSE = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.32_drop_scope_sf_refuse"
)
PROMPT_VERSION_V0_9_33_DROP_SCOPE_SF_KEEP = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.33_drop_scope_sf_keep"
)
PROMPT_VERSION_V0_9_34_DROP_SCOPE_DIAGNOSIS = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.34_drop_scope_diagnosis"
)
PROMPT_VERSION_V0_9_35_DROP_SCOPE_RX_IX = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.35_drop_scope_rx_ix"
)
PROMPT_VERSION_V0_9_36_DROP_ENCODING_NON_SF = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.36_drop_encoding_non_sf"
)
PROMPT_VERSION_V0_9_37_DROP_EXAMPLES_NON_SF = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.37_drop_examples_non_sf"
)
PROMPT_VERSION_V0_9_38_DROP_EXAMPLES_SF_ENCODING = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.38_drop_examples_sf_encoding"
)
PROMPT_VERSION_V0_9_39_DROP_EXAMPLES_SF_SCOPE = (
    "exectv2_hybrid_key_family_event_ledger_v0.9.39_drop_examples_sf_scope"
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
_SCOPE_SF_REFUSE = frozenset(
    {
        "rule-41",
        "rule-42",
        "rule-43",
        "rule-44",
        "rule-45",
        "rule-46",
        "rule-59",
    }
)
_SCOPE_SF_KEEP = frozenset({"rule-47", "rule-57", "rule-60", "rule-61"})
_SCOPE_DIAGNOSIS = frozenset(
    {
        "rule-15",
        "rule-17",
        "rule-18",
        "rule-24",
        "rule-25",
        "rule-26",
        "rule-30",
    }
)
_SCOPE_RX_IX = frozenset(
    {
        "rule-66",
        "rule-72",
        "rule-73",
        "rule-74",
        "rule-75",
        "rule-76",
        "rule-77",
    }
)
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
_EXAMPLES_NON_SF = frozenset(
    {
        "example-01",
        "example-03",
        "example-04",
        "example-05",
        "example-13",
        "example-21",
        "example-22",
        "example-23",
        "example-24",
        "example-25",
        "example-26",
        "example-27",
        "example-28",
        "example-29",
        "example-30",
        "example-31",
        "example-32",
        "example-33",
        "example-34",
        "example-35",
        "example-36",
        "example-37",
        "example-38",
        "example-39",
        "example-40",
        "example-41",
    }
)
_EXAMPLES_SF_ENCODING = frozenset(
    {
        "example-02",
        "example-06",
        "example-07",
        "example-08",
        "example-09",
        "example-10",
        "example-11",
        "example-12",
        "example-14",
        "example-15",
        "example-16",
        "example-17",
        "example-20",
    }
)
_EXAMPLES_SF_SCOPE = frozenset(
    {
        "example-18",
        "example-19",
        "example-42",
        "example-43",
        "example-44",
        "example-45",
        "example-46",
        "example-47",
        "example-48",
        "example-49",
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
    PROMPT_VERSION_V0_9_30_DROP_SCAFFOLD_EXAMPLES: AblationSpec(
        version=PROMPT_VERSION_V0_9_30_DROP_SCAFFOLD_EXAMPLES,
        drop_payload_keys=_SCAFFOLD_KEYS,
        drop_examples=True,
        drop_rule_ids=_JUNK_LEDGER_RULES,
        task=_SCAFFOLD_TASK,
    ),
    PROMPT_VERSION_V0_9_31_DROP_SCAFFOLD_EXAMPLES_ENCODING: AblationSpec(
        version=PROMPT_VERSION_V0_9_31_DROP_SCAFFOLD_EXAMPLES_ENCODING,
        drop_payload_keys=_SCAFFOLD_KEYS,
        drop_examples=True,
        drop_rule_ids=_JUNK_LEDGER_RULES | _ENCODING_RULES,
        task=_SCAFFOLD_TASK,
    ),
    PROMPT_VERSION_V0_9_32_DROP_SCOPE_SF_REFUSE: AblationSpec(
        version=PROMPT_VERSION_V0_9_32_DROP_SCOPE_SF_REFUSE,
        drop_rule_ids=_SCOPE_SF_REFUSE,
    ),
    PROMPT_VERSION_V0_9_33_DROP_SCOPE_SF_KEEP: AblationSpec(
        version=PROMPT_VERSION_V0_9_33_DROP_SCOPE_SF_KEEP,
        drop_rule_ids=_SCOPE_SF_KEEP,
    ),
    PROMPT_VERSION_V0_9_34_DROP_SCOPE_DIAGNOSIS: AblationSpec(
        version=PROMPT_VERSION_V0_9_34_DROP_SCOPE_DIAGNOSIS,
        drop_rule_ids=_SCOPE_DIAGNOSIS,
    ),
    PROMPT_VERSION_V0_9_35_DROP_SCOPE_RX_IX: AblationSpec(
        version=PROMPT_VERSION_V0_9_35_DROP_SCOPE_RX_IX,
        drop_rule_ids=_SCOPE_RX_IX,
    ),
    PROMPT_VERSION_V0_9_36_DROP_ENCODING_NON_SF: AblationSpec(
        version=PROMPT_VERSION_V0_9_36_DROP_ENCODING_NON_SF,
        drop_rule_ids=_ENCODING_NON_SF,
    ),
    PROMPT_VERSION_V0_9_37_DROP_EXAMPLES_NON_SF: AblationSpec(
        version=PROMPT_VERSION_V0_9_37_DROP_EXAMPLES_NON_SF,
        drop_example_ids=_EXAMPLES_NON_SF,
    ),
    PROMPT_VERSION_V0_9_38_DROP_EXAMPLES_SF_ENCODING: AblationSpec(
        version=PROMPT_VERSION_V0_9_38_DROP_EXAMPLES_SF_ENCODING,
        drop_example_ids=_EXAMPLES_SF_ENCODING,
    ),
    PROMPT_VERSION_V0_9_39_DROP_EXAMPLES_SF_SCOPE: AblationSpec(
        version=PROMPT_VERSION_V0_9_39_DROP_EXAMPLES_SF_SCOPE,
        drop_example_ids=_EXAMPLES_SF_SCOPE,
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
