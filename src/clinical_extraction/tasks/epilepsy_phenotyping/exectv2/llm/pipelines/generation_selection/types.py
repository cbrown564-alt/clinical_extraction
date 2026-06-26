"""Shared literals for generation-selection call strategies."""

from __future__ import annotations

from typing import Literal

PromptProfile = Literal[
    "compact",
    "full_examples",
    "decision_table",
    "decision_table_sf_inv",
]

CallStrategy = Literal[
    "two_stage",
    "single_call_dedup_facts",
    "single_call_dedup_facts_per_family",
    "single_call_inventory",
    "single_call_mentions",
    "single_call_per_entity_mentions",
    "single_call_typed_mentions",
    "single_call_mention_ids",
    "single_call_render_ids",
    "single_call_clean_render_ids",
    "single_call_per_entity_clean_render_ids",
    "qwen_pool_adjudication",
    "qwen_pool_entity_adjudication",
    "qwen_pool_group_adjudication",
]

DedupFactFamily = Literal[
    "diagnosis",
    "seizure_frequency",
    "prescription",
    "investigation",
]

CALL_STRATEGIES: tuple[CallStrategy, ...] = (
    "two_stage",
    "single_call_dedup_facts",
    "single_call_dedup_facts_per_family",
    "single_call_inventory",
    "single_call_mentions",
    "single_call_per_entity_mentions",
    "single_call_typed_mentions",
    "single_call_mention_ids",
    "single_call_render_ids",
    "single_call_clean_render_ids",
    "single_call_per_entity_clean_render_ids",
    "qwen_pool_adjudication",
    "qwen_pool_entity_adjudication",
    "qwen_pool_group_adjudication",
)

DEDUP_FACT_FAMILIES: tuple[DedupFactFamily, ...] = (
    "diagnosis",
    "seizure_frequency",
    "prescription",
    "investigation",
)

DECISION_TABLE_FAMILIES: frozenset[DedupFactFamily] = frozenset(
    {"seizure_frequency", "investigation"}
)
