"""Structured key-entity prompt corpora."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_dedup_fact_decision_tables,
    load_dedup_fact_worked_examples,
    load_qwen_compact_worked_examples,
    load_v16_shape_examples,
    load_worked_examples,
)

__all__ = [
    "load_dedup_fact_decision_tables",
    "load_dedup_fact_worked_examples",
    "load_qwen_compact_worked_examples",
    "load_v16_shape_examples",
    "load_worked_examples",
]
