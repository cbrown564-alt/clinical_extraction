"""CallStrategy -> handler registry for generation-selection dispatch."""

from __future__ import annotations

from collections.abc import Callable

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.context import (
    StrategyContext,
    StrategyOutcome,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.qwen_pool import (
    run_qwen_pool_adjudication,
    run_qwen_pool_entity_adjudication,
    run_qwen_pool_group_adjudication,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.single_call_dedup import (
    run_single_call_dedup_facts,
    run_single_call_dedup_facts_per_family,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.single_call_inventory import (
    run_single_call_inventory,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.single_call_mention_ids import (
    run_single_call_clean_render_ids,
    run_single_call_mention_ids,
    run_single_call_per_entity_clean_render_ids,
    run_single_call_render_ids,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.single_call_mentions import (
    run_single_call_mentions,
    run_single_call_per_entity_mentions,
    run_single_call_typed_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.strategies.two_stage import (
    run_two_stage,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    CALL_STRATEGIES,
    CallStrategy,
)

StrategyHandler = Callable[[StrategyContext], StrategyOutcome]

STRATEGY_REGISTRY: dict[CallStrategy, StrategyHandler] = {
    "two_stage": run_two_stage,
    "single_call_dedup_facts": run_single_call_dedup_facts,
    "single_call_dedup_facts_per_family": run_single_call_dedup_facts_per_family,
    "single_call_inventory": run_single_call_inventory,
    "single_call_mentions": run_single_call_mentions,
    "single_call_per_entity_mentions": run_single_call_per_entity_mentions,
    "single_call_typed_mentions": run_single_call_typed_mentions,
    "single_call_mention_ids": run_single_call_mention_ids,
    "single_call_render_ids": run_single_call_render_ids,
    "single_call_clean_render_ids": run_single_call_clean_render_ids,
    "single_call_per_entity_clean_render_ids": run_single_call_per_entity_clean_render_ids,
    "qwen_pool_adjudication": run_qwen_pool_adjudication,
    "qwen_pool_entity_adjudication": run_qwen_pool_entity_adjudication,
    "qwen_pool_group_adjudication": run_qwen_pool_group_adjudication,
}


def _validate_registry() -> None:
    registered = frozenset(STRATEGY_REGISTRY)
    expected = frozenset(CALL_STRATEGIES)
    if registered != expected:  # pragma: no cover - protected by registry tests
        missing = sorted(expected - registered)
        extra = sorted(registered - expected)
        raise RuntimeError(
            "generation_selection STRATEGY_REGISTRY mismatch: "
            f"missing={missing!r} extra={extra!r}"
        )


_validate_registry()
