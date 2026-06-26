"""Single-call mention-id / render-id selection strategies."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.context import (
    StrategyContext,
    StrategyOutcome,
)


def _outcome_from_mention_id_run(
    ctx: StrategyContext,
    *,
    run_letter: Callable[..., tuple[Any, ...]],
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
        program=ctx.programs.mention_id,
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


def run_single_call_mention_ids(ctx: StrategyContext) -> StrategyOutcome:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    return _outcome_from_mention_id_run(
        ctx,
        run_letter=mono._run_single_call_mention_ids_letter,
    )


def run_single_call_render_ids(ctx: StrategyContext) -> StrategyOutcome:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    return _outcome_from_mention_id_run(
        ctx,
        run_letter=mono._run_single_call_render_ids_letter,
    )


def run_single_call_clean_render_ids(ctx: StrategyContext) -> StrategyOutcome:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    return _outcome_from_mention_id_run(
        ctx,
        run_letter=mono._run_single_call_clean_render_ids_letter,
    )


def run_single_call_per_entity_clean_render_ids(ctx: StrategyContext) -> StrategyOutcome:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_generation_selection as mono,
    )

    return _outcome_from_mention_id_run(
        ctx,
        run_letter=mono._run_single_call_per_entity_clean_render_ids_letter,
    )
