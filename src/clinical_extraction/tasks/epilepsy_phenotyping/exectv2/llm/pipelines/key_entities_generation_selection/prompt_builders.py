"""Prompt payload/input builders for every generation-selection call strategy."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_dedup import (
    build_single_call_dedup_facts_prompt_input,
    build_single_call_dedup_facts_prompt_payload,
    build_single_call_per_entity_clean_render_ids_prompt_input,
    build_single_call_per_entity_clean_render_ids_prompt_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_generation import (
    build_generation_prompt_input,
    build_generation_prompt_payload,
    build_selection_prompt_input,
    build_selection_prompt_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_qwen_pool import (
    build_qwen_pool_adjudication_prompt_input,
    build_qwen_pool_adjudication_prompt_payload,
    build_qwen_pool_entity_adjudication_prompt_input,
    build_qwen_pool_entity_adjudication_prompt_payload,
    build_qwen_pool_group_adjudication_prompt_input,
    build_qwen_pool_group_adjudication_prompt_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_single_call_ids import (
    build_single_call_clean_render_ids_prompt_input,
    build_single_call_clean_render_ids_prompt_payload,
    build_single_call_mention_ids_prompt_input,
    build_single_call_mention_ids_prompt_payload,
    build_single_call_render_ids_prompt_input,
    build_single_call_render_ids_prompt_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_single_call_mentions import (
    build_single_call_inventory_prompt_input,
    build_single_call_inventory_prompt_payload,
    build_single_call_mentions_prompt_input,
    build_single_call_mentions_prompt_payload,
    build_single_call_per_entity_mentions_prompt_input,
    build_single_call_per_entity_mentions_prompt_payload,
    build_single_call_typed_mentions_prompt_input,
    build_single_call_typed_mentions_prompt_payload,
)

__all__ = [
    "build_generation_prompt_input",
    "build_generation_prompt_payload",
    "build_qwen_pool_adjudication_prompt_input",
    "build_qwen_pool_adjudication_prompt_payload",
    "build_qwen_pool_entity_adjudication_prompt_input",
    "build_qwen_pool_entity_adjudication_prompt_payload",
    "build_qwen_pool_group_adjudication_prompt_input",
    "build_qwen_pool_group_adjudication_prompt_payload",
    "build_selection_prompt_input",
    "build_selection_prompt_payload",
    "build_single_call_clean_render_ids_prompt_input",
    "build_single_call_clean_render_ids_prompt_payload",
    "build_single_call_dedup_facts_prompt_input",
    "build_single_call_dedup_facts_prompt_payload",
    "build_single_call_inventory_prompt_input",
    "build_single_call_inventory_prompt_payload",
    "build_single_call_mention_ids_prompt_input",
    "build_single_call_mention_ids_prompt_payload",
    "build_single_call_mentions_prompt_input",
    "build_single_call_mentions_prompt_payload",
    "build_single_call_per_entity_clean_render_ids_prompt_input",
    "build_single_call_per_entity_clean_render_ids_prompt_payload",
    "build_single_call_per_entity_mentions_prompt_input",
    "build_single_call_per_entity_mentions_prompt_payload",
    "build_single_call_render_ids_prompt_input",
    "build_single_call_render_ids_prompt_payload",
    "build_single_call_typed_mentions_prompt_input",
    "build_single_call_typed_mentions_prompt_payload",
]
