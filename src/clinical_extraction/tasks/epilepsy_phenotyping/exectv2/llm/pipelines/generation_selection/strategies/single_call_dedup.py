"""Single-call de-duplicated clinical-facts strategies."""

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
    DECISION_TABLE_FAMILIES,
    DEDUP_FACT_FAMILIES,
    DedupFactFamily,
    PromptProfile,
)


def _dedup_fact_prompt_profile_for_family(
    prompt_profile: PromptProfile,
    family: DedupFactFamily,
) -> PromptProfile:
    if prompt_profile == "decision_table_sf_inv":
        return "decision_table" if family in DECISION_TABLE_FAMILIES else "compact"
    return prompt_profile


def run_single_call_dedup_facts_letter(
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

    prompt_input_json = mono.build_single_call_dedup_facts_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_output = ""
    call_error: str | None = None
    if mode == "live":
        try:
            prediction = program(prompt_input_json)
            raw_output = str(prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            call_error = f"{type(exc).__name__}: {exc}"

    fact_record, parse_errors = (
        mono.parse_dedup_clinical_facts_json(raw_output) if raw_output else (None, ["not_run"])
    )
    fact_record = fact_record or mono.DedupClinicalFactsRecord()
    mentions, provenance, adapter_notes = mono.clinical_facts_to_mentions(
        fact_record.clinical_facts
    )
    all_errors = [*parse_errors, *adapter_notes]
    return (
        prompt_input_json,
        "",
        raw_output,
        raw_output,
        call_error,
        call_error,
        all_errors,
        all_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": prompt_input_json,
            "raw_inventory_output": raw_output,
            "inventory_call_error": call_error,
            "inventory_parse_errors": all_errors,
            "inventory_selection_summary": [],
            "clinical_facts_final": [fact.model_dump() for fact in fact_record.clinical_facts],
            "adapter_provenance": provenance,
            "structured_mentions_generation": [mention.model_dump() for mention in mentions],
            "structured_mentions_final": [mention.model_dump() for mention in mentions],
            "n_mentions_generation": len(mentions),
            "n_clinical_facts_final": len(fact_record.clinical_facts),
            "dedup_adapter_added_facts": 0,
            "dedup_adapter_deduplicated_facts": 0,
        },
    )


def run_single_call_dedup_facts_per_family_letter(
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

    prompt_by_family: dict[str, str] = {}
    raw_by_family: dict[str, str] = {}
    call_error_by_family: dict[str, str] = {}
    parse_errors: list[str] = []
    facts: list[dict[str, Any]] = []

    for family in DEDUP_FACT_FAMILIES:
        family_prompt_profile = _dedup_fact_prompt_profile_for_family(
            prompt_profile,
            family,
        )
        prompt_input_json = mono.build_single_call_dedup_facts_prompt_input(
            letter,
            prompt_profile=family_prompt_profile,
            target_family=family,
        )
        prompt_by_family[family] = prompt_input_json
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        raw_by_family[family] = raw_output
        if call_error:
            call_error_by_family[family] = call_error

        fact_record, family_parse_errors = (
            mono.parse_dedup_clinical_facts_json(raw_output) if raw_output else (None, ["not_run"])
        )
        parse_errors.extend(f"{family}:{error}" for error in family_parse_errors)
        for fact in (fact_record or mono.DedupClinicalFactsRecord()).clinical_facts:
            facts.append(fact.model_dump())

    combined_record = mono.DedupClinicalFactsRecord.model_validate({"clinical_facts": facts})
    mentions, provenance, adapter_notes = mono.clinical_facts_to_mentions(
        combined_record.clinical_facts
    )
    all_errors = [*parse_errors, *adapter_notes]
    prompt_bundle = json.dumps(prompt_by_family, sort_keys=True)
    raw_bundle = json.dumps(raw_by_family, sort_keys=True)
    combined_call_error = (
        json.dumps(call_error_by_family, sort_keys=True) if call_error_by_family else None
    )
    return (
        prompt_bundle,
        "",
        raw_bundle,
        raw_bundle,
        combined_call_error,
        combined_call_error,
        all_errors,
        all_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": prompt_bundle,
            "raw_inventory_output": raw_bundle,
            "inventory_call_error": combined_call_error,
            "inventory_parse_errors": all_errors,
            "inventory_selection_summary": [],
            "clinical_facts_final": [fact.model_dump() for fact in combined_record.clinical_facts],
            "adapter_provenance": provenance,
            "structured_mentions_generation": [mention.model_dump() for mention in mentions],
            "structured_mentions_final": [mention.model_dump() for mention in mentions],
            "dedup_fact_prompt_inputs_by_family": prompt_by_family,
            "dedup_fact_raw_outputs_by_family": raw_by_family,
            "dedup_fact_call_errors_by_family": call_error_by_family,
            "n_mentions_generation": len(mentions),
            "n_clinical_facts_final": len(combined_record.clinical_facts),
            "dedup_adapter_added_facts": 0,
            "dedup_adapter_deduplicated_facts": 0,
        },
    )


def _outcome_from_dedup_run(
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
        program=ctx.programs.dedup_facts,
    )
    row = mono.row_from_final_dedup_facts(
        ctx.letter,
        mono.DedupClinicalFactsRecord.model_validate(
            {"clinical_facts": inventory_details["clinical_facts_final"]}
        ),
        split=ctx.split,
        model=ctx.model,
        mode=ctx.mode,
        raw_generation_output=raw_generation_output,
        generation_parse_errors=generation_parse_errors,
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


def run_single_call_dedup_facts(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_dedup_run(ctx, run_letter=run_single_call_dedup_facts_letter)


def run_single_call_dedup_facts_per_family(ctx: StrategyContext) -> StrategyOutcome:
    return _outcome_from_dedup_run(
        ctx,
        run_letter=run_single_call_dedup_facts_per_family_letter,
    )
