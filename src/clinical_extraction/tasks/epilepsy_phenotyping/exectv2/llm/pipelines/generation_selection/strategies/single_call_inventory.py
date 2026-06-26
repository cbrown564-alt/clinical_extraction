"""Single-call inventory selection strategy."""

from __future__ import annotations

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


def run_single_call_inventory_letter(
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

    inventory_prompt_input_json = mono.build_single_call_inventory_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_inventory_output = ""
    inventory_call_error: str | None = None
    if mode == "live":
        try:
            inventory_prediction = program(inventory_prompt_input_json)
            raw_inventory_output = str(inventory_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            inventory_call_error = f"{type(exc).__name__}: {exc}"

    inventory_record, inventory_parse_errors = (
        mono.parse_generation_selection_json(raw_inventory_output)
        if raw_inventory_output
        else (None, ["not_run"])
    )
    inventory_record = inventory_record or mono.StructuredGenerationSelectionRecord()
    first_pass_record = structured.StructuredExtractionRecord(
        clinical_events=inventory_record.generated_events
    )
    final_record = mono.final_record_from_generation_selection(inventory_record)
    return (
        inventory_prompt_input_json,
        "",
        raw_inventory_output,
        raw_inventory_output,
        inventory_call_error,
        inventory_call_error,
        inventory_parse_errors,
        inventory_parse_errors,
        first_pass_record,
        final_record,
        {
            "inventory_prompt_input_json": inventory_prompt_input_json,
            "raw_inventory_output": raw_inventory_output,
            "inventory_call_error": inventory_call_error,
            "inventory_parse_errors": inventory_parse_errors,
            "inventory_selection_summary": inventory_record.selection_summary,
        },
    )


def run_single_call_inventory(ctx: StrategyContext) -> StrategyOutcome:
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
    ) = run_single_call_inventory_letter(
        ctx.letter,
        mode=ctx.mode,
        prompt_profile=ctx.prompt_profile,
        program=ctx.programs.inventory,
    )
    row = mono.row_from_final_record(
        ctx.letter,
        final_record,
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
