"""Qwen pool adjudication call strategies."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.context import (
    StrategyContext,
    StrategyOutcome,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    PromptProfile,
)


def run_qwen_pool_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    pool_mentions, pool_notes = mono.coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    pool_prompt_input_json = mono.build_qwen_pool_adjudication_prompt_input(
        letter,
        pool_mentions,
        prompt_profile=prompt_profile,
    )
    raw_selection_output = ""
    selection_call_error: str | None = None
    if mode == "live":
        try:
            selection_prediction = program(pool_prompt_input_json)
            raw_selection_output = str(selection_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            selection_call_error = f"{type(exc).__name__}: {exc}"

    selection_record, selection_parse_errors = (
        mono.parse_qwen_pool_adjudication_json(raw_selection_output)
        if raw_selection_output
        else (None, ["not_run"])
    )
    selection_record = selection_record or mono.StructuredPoolAdjudicationRecord()
    final_mentions, selection_notes = mono.final_mentions_from_mention_id_selection(
        mono.StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=selection_record.final_mention_ids,
            selection_summary=selection_record.selection_summary,
        )
    )
    all_selection_notes = [*pool_notes, *selection_parse_errors, *selection_notes]
    return (
        "",
        pool_prompt_input_json,
        "",
        raw_selection_output,
        None,
        selection_call_error,
        [],
        all_selection_notes,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": pool_prompt_input_json,
            "raw_inventory_output": raw_selection_output,
            "inventory_call_error": selection_call_error,
            "inventory_parse_errors": all_selection_notes,
            "inventory_selection_summary": selection_record.selection_summary,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [mention.model_dump() for mention in final_mentions],
            "final_mention_ids": list(selection_record.final_mention_ids),
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def run_qwen_pool_entity_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    pool_mentions, pool_notes = mono.coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    prompts_by_entity: dict[str, dict[str, Any]] = {}
    raw_outputs_by_entity: dict[str, str] = {}
    final_ids_by_entity: dict[str, list[str]] = {}
    selection_summary_by_entity: dict[str, list[dict[str, Any]]] = {}
    entity_pool_sizes: dict[str, int] = {}
    selection_call_errors: list[str] = []
    selection_parse_errors: list[str] = list(pool_notes)

    for target_entity in structured.KEY_ENTITY_NAMES:
        entity_mentions = [
            mention
            for mention in pool_mentions
            if str(mention.get("entity") or "") == target_entity
        ]
        entity_pool_sizes[target_entity] = len(entity_mentions)
        if not entity_mentions:
            prompts_by_entity[target_entity] = {}
            raw_outputs_by_entity[target_entity] = ""
            final_ids_by_entity[target_entity] = []
            selection_summary_by_entity[target_entity] = []
            continue

        prompt_input_json = mono.build_qwen_pool_entity_adjudication_prompt_input(
            letter,
            entity_mentions,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        )
        prompts_by_entity[target_entity] = json.loads(prompt_input_json)
        raw_entity_output = ""
        if mode == "live":
            try:
                entity_prediction = program(prompt_input_json)
                raw_entity_output = str(entity_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                selection_call_errors.append(f"{target_entity}:{type(exc).__name__}: {exc}")
        raw_outputs_by_entity[target_entity] = raw_entity_output

        entity_record, entity_errors = (
            mono.parse_qwen_pool_adjudication_json(raw_entity_output)
            if raw_entity_output
            else (None, [])
        )
        entity_record = entity_record or mono.StructuredPoolAdjudicationRecord()
        final_ids_by_entity[target_entity] = list(entity_record.final_mention_ids)
        selection_summary_by_entity[target_entity] = list(entity_record.selection_summary)
        selection_parse_errors.extend(f"{target_entity}:{error}" for error in entity_errors)

    final_ids = [
        mention_id
        for target_entity in structured.KEY_ENTITY_NAMES
        for mention_id in final_ids_by_entity.get(target_entity, [])
    ]
    final_mentions, selection_notes = mono.final_mentions_from_mention_id_selection(
        mono.StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=final_ids,
            selection_summary=[
                summary
                for target_entity in structured.KEY_ENTITY_NAMES
                for summary in selection_summary_by_entity.get(target_entity, [])
            ],
        )
    )
    all_selection_notes = [*selection_parse_errors, *selection_notes]
    prompt_bundle = {
        "stage": "qwen_pool_entity_adjudication",
        "entity_prompt_inputs": prompts_by_entity,
    }
    raw_output_bundle = {
        "stage": "qwen_pool_entity_adjudication",
        "entity_raw_outputs": raw_outputs_by_entity,
    }
    selection_call_error = "; ".join(selection_call_errors) or None
    return (
        "",
        json.dumps(prompt_bundle, sort_keys=True),
        "",
        json.dumps(raw_output_bundle, sort_keys=True),
        None,
        selection_call_error,
        [],
        all_selection_notes,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": json.dumps(prompt_bundle, sort_keys=True),
            "raw_inventory_output": json.dumps(raw_output_bundle, sort_keys=True),
            "inventory_call_error": selection_call_error,
            "inventory_parse_errors": all_selection_notes,
            "inventory_selection_summary": selection_summary_by_entity,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [mention.model_dump() for mention in final_mentions],
            "final_mention_ids": final_ids,
            "final_mention_ids_by_entity": final_ids_by_entity,
            "entity_pool_sizes": entity_pool_sizes,
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def run_qwen_pool_group_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    pool_mentions, pool_notes = mono.coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    group_prompt_input_json = mono.build_qwen_pool_group_adjudication_prompt_input(
        letter,
        pool_mentions,
        prompt_profile=prompt_profile,
    )
    raw_group_output = ""
    group_call_error: str | None = None
    if mode == "live":
        try:
            group_prediction = program(group_prompt_input_json)
            raw_group_output = str(group_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            group_call_error = f"{type(exc).__name__}: {exc}"

    group_record, group_parse_errors = (
        mono.parse_qwen_pool_group_adjudication_json(raw_group_output)
        if raw_group_output
        else (None, ["not_run"])
    )
    group_record = group_record or mono.StructuredPoolGroupAdjudicationRecord()
    final_mentions, selection_notes = mono.final_mentions_from_mention_id_selection(
        mono.StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=group_record.final_mention_ids,
            selection_summary=group_record.selection_summary,
        )
    )
    all_parse_errors = [*pool_notes, *group_parse_errors, *selection_notes]
    return (
        "",
        group_prompt_input_json,
        "",
        raw_group_output,
        None,
        group_call_error,
        [],
        all_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": group_prompt_input_json,
            "raw_inventory_output": raw_group_output,
            "inventory_call_error": group_call_error,
            "inventory_parse_errors": all_parse_errors,
            "inventory_selection_summary": group_record.selection_summary,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [mention.model_dump() for mention in final_mentions],
            "final_mention_ids": list(group_record.final_mention_ids),
            "fact_groups": list(group_record.fact_groups),
            "n_fact_groups": len(group_record.fact_groups),
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def _pool_mentions_for_letter(ctx: StrategyContext) -> list[dict[str, Any]]:
    return list((ctx.pool_mentions_by_letter or {}).get(ctx.letter.letter_id, []))


def _outcome_from_pool_run(
    ctx: StrategyContext,
    *,
    run_letter,
) -> StrategyOutcome:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    (
        generation_prompt_input_json,
        selection_prompt_input_json,
        raw_generation_output,
        raw_selection_output,
        generation_call_error,
        selection_call_error,
        generation_parse_errors,
        selection_parse_errors,
        first_pass_record,
        final_record,
        inventory_details,
    ) = run_letter(
        ctx.letter,
        mode=ctx.mode,
        prompt_profile=ctx.prompt_profile,
        program=ctx.programs.pool,
        model_generated_mentions=_pool_mentions_for_letter(ctx),
    )
    row = mono.row_from_final_mentions(
        ctx.letter,
        inventory_details["structured_mentions_final"],
        split=ctx.split,
        model=ctx.model,
        mode=ctx.mode,
        raw_generation_output=raw_generation_output,
        raw_selection_output=raw_selection_output,
        generation_parse_errors=generation_parse_errors,
        selection_parse_errors=selection_parse_errors,
    )
    return StrategyOutcome(
        generation_prompt_input_json=generation_prompt_input_json,
        selection_prompt_input_json=selection_prompt_input_json,
        raw_generation_output=raw_generation_output,
        raw_selection_output=raw_selection_output,
        generation_call_error=generation_call_error,
        selection_call_error=selection_call_error,
        generation_parse_errors=generation_parse_errors,
        selection_parse_errors=selection_parse_errors,
        first_pass_record=first_pass_record,
        final_record=final_record,
        inventory_details=inventory_details,
        row=row,
    )


def run_qwen_pool_group_adjudication(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_pool_run(
        ctx,
        run_letter=run_qwen_pool_group_adjudication_letter,
    )


def run_qwen_pool_entity_adjudication(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_pool_run(
        ctx,
        run_letter=run_qwen_pool_entity_adjudication_letter,
    )


def run_qwen_pool_adjudication(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_pool_run(
        ctx,
        run_letter=run_qwen_pool_adjudication_letter,
    )
