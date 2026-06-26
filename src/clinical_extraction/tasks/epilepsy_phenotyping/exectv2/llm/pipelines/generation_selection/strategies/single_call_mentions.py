"""Single-call mention-selection strategies (flat and per-entity)."""

from __future__ import annotations

import json
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


def run_single_call_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
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

    mention_prompt_input_json = mono.build_single_call_mentions_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_mention_output = ""
    mention_call_error: str | None = None
    if mode == "live":
        try:
            mention_prediction = program(mention_prompt_input_json)
            raw_mention_output = str(mention_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            mention_call_error = f"{type(exc).__name__}: {exc}"

    mention_record, mention_parse_errors = (
        mono.parse_generation_selection_mentions_json(raw_mention_output)
        if raw_mention_output
        else (None, ["not_run"])
    )
    mention_record = mention_record or mono.StructuredMentionSelectionRecord()
    final_mentions = mono.final_mentions_from_generation_selection(mention_record)
    return (
        mention_prompt_input_json,
        "",
        raw_mention_output,
        raw_mention_output,
        mention_call_error,
        mention_call_error,
        mention_parse_errors,
        mention_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": mention_prompt_input_json,
            "raw_inventory_output": raw_mention_output,
            "inventory_call_error": mention_call_error,
            "inventory_parse_errors": mention_parse_errors,
            "inventory_selection_summary": mention_record.selection_summary,
            "structured_mentions_generation": [
                mention.model_dump() for mention in mention_record.generated_mentions
            ],
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "n_mentions_generation": len(mention_record.generated_mentions),
        },
    )


def run_single_call_per_entity_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
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

    prompt_inputs_by_entity: dict[str, dict[str, Any]] = {}
    raw_outputs_by_entity: dict[str, str] = {}
    parse_errors: list[str] = []
    call_errors: list[str] = []
    generated_mentions: list[dict[str, Any]] = []
    final_mentions: list[dict[str, Any]] = []
    selection_summary_by_entity: dict[str, list[dict[str, Any]]] = {}

    for target_entity in structured.KEY_ENTITY_NAMES:
        prompt_input_json = mono.build_single_call_per_entity_mentions_prompt_input(
            letter,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        )
        prompt_inputs_by_entity[target_entity] = json.loads(prompt_input_json)
        raw_entity_output = ""
        if mode == "live":
            try:
                entity_prediction = program(prompt_input_json)
                raw_entity_output = str(entity_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_errors.append(f"{target_entity}:{type(exc).__name__}: {exc}")
        raw_outputs_by_entity[target_entity] = raw_entity_output

        mention_record, entity_parse_errors = (
            mono.parse_generation_selection_mentions_json(raw_entity_output)
            if raw_entity_output
            else (None, [])
        )
        mention_record = mention_record or mono.StructuredMentionSelectionRecord()
        generated_mentions.extend(
            mention.model_dump() for mention in mention_record.generated_mentions
        )
        final_mentions.extend(
            mention.model_dump() for mention in mention_record.final_mentions
        )
        selection_summary_by_entity[target_entity] = list(
            mention_record.selection_summary
        )
        parse_errors.extend(f"{target_entity}:{error}" for error in entity_parse_errors)

    prompt_bundle = {
        "stage": "single_call_per_entity_mention_selection",
        "entity_prompt_inputs": prompt_inputs_by_entity,
    }
    raw_output_bundle = {
        "stage": "single_call_per_entity_mention_selection",
        "entity_raw_outputs": raw_outputs_by_entity,
    }
    call_error = "; ".join(call_errors) or None
    return (
        json.dumps(prompt_bundle, sort_keys=True),
        "",
        json.dumps(raw_output_bundle, sort_keys=True),
        json.dumps(raw_output_bundle, sort_keys=True),
        call_error,
        call_error,
        parse_errors,
        parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": json.dumps(prompt_bundle, sort_keys=True),
            "raw_inventory_output": json.dumps(raw_output_bundle, sort_keys=True),
            "inventory_call_error": call_error,
            "inventory_parse_errors": parse_errors,
            "inventory_selection_summary": selection_summary_by_entity,
            "structured_mentions_generation": generated_mentions,
            "structured_mentions_final": final_mentions,
            "n_mentions_generation": len(generated_mentions),
            "n_entity_calls": len(structured.KEY_ENTITY_NAMES),
        },
    )


def run_single_call_typed_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: Any,
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

    typed_prompt_input_json = mono.build_single_call_typed_mentions_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_typed_output = ""
    typed_call_error: str | None = None
    if mode == "live":
        try:
            typed_prediction = program(typed_prompt_input_json)
            raw_typed_output = str(typed_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            typed_call_error = f"{type(exc).__name__}: {exc}"

    typed_record, typed_parse_errors = (
        mono.parse_generation_selection_typed_mentions_json(raw_typed_output)
        if raw_typed_output
        else (None, ["not_run"])
    )
    typed_record = typed_record or mono.StructuredMentionSelectionRecord()
    return (
        typed_prompt_input_json,
        "",
        raw_typed_output,
        raw_typed_output,
        typed_call_error,
        typed_call_error,
        typed_parse_errors,
        typed_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": typed_prompt_input_json,
            "raw_inventory_output": raw_typed_output,
            "inventory_call_error": typed_call_error,
            "inventory_parse_errors": typed_parse_errors,
            "inventory_selection_summary": typed_record.selection_summary,
            "structured_mentions_generation": [
                mention.model_dump() for mention in typed_record.generated_mentions
            ],
            "structured_mentions_final": [
                mention.model_dump() for mention in typed_record.final_mentions
            ],
            "n_mentions_generation": len(typed_record.generated_mentions),
        },
    )


def _outcome_from_mention_run(
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
        program=ctx.programs.mention,
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


def run_single_call_mentions(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_mention_run(ctx, run_letter=run_single_call_mentions_letter)


def run_single_call_per_entity_mentions(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_mention_run(
        ctx,
        run_letter=run_single_call_per_entity_mentions_letter,
    )


def run_single_call_typed_mentions(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_mention_run(
        ctx,
        run_letter=run_single_call_typed_mentions_letter,
    )
