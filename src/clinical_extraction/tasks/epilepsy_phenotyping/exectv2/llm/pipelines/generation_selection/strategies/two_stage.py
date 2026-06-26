"""Two-stage generation-then-selection call strategy."""

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


def run_two_stage_letter(
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

    generation_prompt_input_json = mono.build_generation_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_generation_output = ""
    generation_call_error: str | None = None
    if mode == "live":
        try:
            generation_prediction = program(generation_prompt_input_json)
            raw_generation_output = str(generation_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            generation_call_error = f"{type(exc).__name__}: {exc}"

    generation_record, generation_parse_errors = (
        mono.parse_events_json(raw_generation_output)
        if raw_generation_output
        else (None, ["not_run"])
    )
    first_pass_record = generation_record or structured.StructuredExtractionRecord()

    selection_prompt_input_json = mono.build_selection_prompt_input(
        letter,
        first_pass_record,
        prompt_profile=prompt_profile,
    )
    raw_selection_output = ""
    selection_call_error: str | None = None
    if mode == "live":
        try:
            selection_prediction = program(selection_prompt_input_json)
            raw_selection_output = str(selection_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            selection_call_error = f"{type(exc).__name__}: {exc}"

    final_record, selection_parse_errors = (
        mono.parse_events_json(raw_selection_output)
        if raw_selection_output
        else (None, ["not_run"])
    )
    return (
        generation_prompt_input_json,
        selection_prompt_input_json,
        raw_generation_output,
        raw_selection_output,
        generation_call_error,
        selection_call_error,
        generation_parse_errors,
        selection_parse_errors,
        first_pass_record,
        final_record or structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": "",
            "raw_inventory_output": "",
            "inventory_call_error": None,
            "inventory_parse_errors": [],
            "inventory_selection_summary": [],
        },
    )


def run_two_stage(ctx: StrategyContext) -> StrategyOutcome:
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
    ) = run_two_stage_letter(
        ctx.letter,
        mode=ctx.mode,
        prompt_profile=ctx.prompt_profile,
        program=ctx.programs.two_stage,
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
