"""run_split orchestration, reporting, checkpointing, and dedup-fact replay."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection import (
    STRATEGY_REGISTRY,
    StrategyContext,
    StrategyPrograms,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    CallStrategy,
    PromptProfile,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.constants import (
    COMPONENT_OWNER,
    FACT_ORIGIN,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    component_owner_for_model,
    report_model_label,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.facts import (
    clinical_facts_from_mentions,
    clinical_facts_to_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    row_from_final_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.records import (
    DedupClinicalFactsRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.signatures import (
    QwenGenerationSelectionExtractor,
    QwenPoolAdjudicationExtractor,
    QwenSingleCallDedupFactsExtractor,
    QwenSingleCallInventoryExtractor,
    QwenSingleCallMentionExtractor,
    QwenSingleCallMentionIdExtractor,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    prompt_profile: PromptProfile = "compact",
    call_strategy: CallStrategy = "two_stage",
    pool_mentions_by_letter: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    programs = StrategyPrograms(
        two_stage=QwenGenerationSelectionExtractor(),
        inventory=QwenSingleCallInventoryExtractor(),
        mention=QwenSingleCallMentionExtractor(),
        mention_id=QwenSingleCallMentionIdExtractor(),
        dedup_facts=QwenSingleCallDedupFactsExtractor(),
        pool=QwenPoolAdjudicationExtractor(),
    )
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    strategy_handler = STRATEGY_REGISTRY[call_strategy]

    for letter in todo:
        outcome = strategy_handler(
            StrategyContext(
                letter=letter,
                mode=mode,
                prompt_profile=prompt_profile,
                programs=programs,
                split=split,
                model=model,
                pool_mentions_by_letter=pool_mentions_by_letter,
            )
        )
        row = outcome.row
        generation_prompt_input_json = outcome.generation_prompt_input_json
        selection_prompt_input_json = outcome.selection_prompt_input_json
        generation_call_error = outcome.generation_call_error
        selection_call_error = outcome.selection_call_error
        generation_parse_errors = outcome.generation_parse_errors
        selection_parse_errors = outcome.selection_parse_errors
        first_pass_record = outcome.first_pass_record
        final_record = outcome.final_record
        inventory_details = outcome.inventory_details
        row.update(
            {
                "prompt_profile": prompt_profile,
                "call_strategy": call_strategy,
                "generation_prompt_input_json": generation_prompt_input_json,
                "selection_prompt_input_json": selection_prompt_input_json,
                "generation_call_error": generation_call_error,
                "selection_call_error": selection_call_error,
                "call_error": generation_call_error or selection_call_error,
                "parse_errors": [f"generation:{error}" for error in generation_parse_errors]
                + [f"selection:{error}" for error in selection_parse_errors],
                "n_events_generation": len(first_pass_record.clinical_events),
                "n_events_raw": len(final_record.clinical_events),
                "structured_events_generation": [
                    event.model_dump() for event in first_pass_record.clinical_events
                ],
                **inventory_details,
            }
        )
        rows.append(row)

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
                prompt_profile=prompt_profile,
                call_strategy=call_strategy,
            )

    rows = merge_rows(rows, order, key="letter_id")
    component_owner = component_owner_for_model(model)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "call_strategy": call_strategy,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    if pool_mentions_by_letter is not None:
        metadata["pool_letters"] = len(pool_mentions_by_letter)
        metadata["pool_mentions_total"] = sum(
            len(mentions) for mentions in pool_mentions_by_letter.values()
        )
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summary = structured.summarize_rows(rows)
    summary["generation_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("generation_parse_errors")) for r in rows
    )
    summary["selection_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("selection_parse_errors")) for r in rows
    )
    summary["generation_call_failures"] = sum(bool(r.get("generation_call_error")) for r in rows)
    summary["selection_call_failures"] = sum(bool(r.get("selection_call_error")) for r in rows)
    summary["inventory_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("inventory_parse_errors")) for r in rows
    )
    summary["inventory_call_failures"] = sum(bool(r.get("inventory_call_error")) for r in rows)
    summary["fact_origin"] = {FACT_ORIGIN: sum(int(r.get("n_mentions_scored", 0)) for r in rows)}
    summary["protocol_surfaces"] = {
        "model_preserving_canonical": summary.get("scores", {})
        .get("benchmark", {})
        .get("per_item", {}),
        "hybrid_full_stack": None,
    }
    return summary


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    is_checkpoint = bool(metadata.get("is_checkpoint"))
    total_letters = int(metadata.get("total_letters") or metadata.get("n_letters") or 0)
    lines = [
        f"# ExECTv2 {report_model_label(str(metadata.get('model') or ''))} "
        "LLM-Only Generation-Selection",
        "",
    ]
    if is_checkpoint:
        processed = summary.get("examples", len(rows))
        total = total_letters or processed
        lines.extend([f"CHECKPOINT ONLY: processed {processed} / {total} letters", ""])
    n_generation_events = sum(int(r.get("n_events_generation", 0)) for r in rows)
    lines.extend(
        [
            f"- JSONL: `{jsonl_path}`",
            f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
            f"- Prompt profile: `{metadata.get('prompt_profile', 'compact')}`",
            f"- Call strategy: `{metadata.get('call_strategy', 'two_stage')}`",
            f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
            f"- Component owner: `{metadata.get('component_owner', COMPONENT_OWNER)}`",
            f"- Fact origin: `{metadata.get('fact_origin', FACT_ORIGIN)}`",
            f"- Split: `{metadata.get('split')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Letters: {summary.get('examples', 0)}",
            f"- Pool letters: {metadata.get('pool_letters', 'not-used')}",
            f"- Pool mentions total: {metadata.get('pool_mentions_total', 'not-used')}",
            "",
            "## Model-Call And Gate Summary",
            "",
            f"- Generation call failures: {summary.get('generation_call_failures', 0)}",
            f"- Selection call failures: {summary.get('selection_call_failures', 0)}",
            f"- Inventory call failures: {summary.get('inventory_call_failures', 0)}",
            f"- Generation parse/schema failures: {summary.get('generation_parse_failures', 0)}",
            f"- Selection parse/schema failures: {summary.get('selection_parse_failures', 0)}",
            f"- Inventory parse/schema failures: {summary.get('inventory_parse_failures', 0)}",
            f"- Clinical events generation: {n_generation_events}",
            f"- Clinical events final: {summary.get('n_events_raw', 0)}",
            f"- Mentions raw final: {summary.get('n_mentions_raw', 0)}",
            f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
            f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
            f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
            "",
            "## Protocol Surfaces",
            "",
            "| Surface | P | R | F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    canonical = summary.get("protocol_surfaces", {}).get("model_preserving_canonical", {})
    lines.append(
        "| model_preserving_canonical | "
        f"{canonical.get('precision', 0):.3f} | "
        f"{canonical.get('recall', 0):.3f} | "
        f"{canonical.get('f1', 0):.3f} | "
        f"{canonical.get('tp', 0)} | "
        f"{canonical.get('fp', 0)} | "
        f"{canonical.get('fn', 0)} |"
    )
    lines.append("| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |")
    lines.extend(["", "## Overall Scores", ""])
    for config_name in ("benchmark", "semantic", "phrase_only"):
        lines.extend(
            structured._score_lines(
                config_name,
                summary.get("scores", {}).get(config_name, {}),
            )
        )
    lines.extend(structured._clinical_recovery_lines(summary.get("clinical_recovery", {})))
    lines.extend(structured._diagnostic_ladder_lines(summary.get("diagnostic_ladder", {})))
    path.write_text("\n".join(lines), encoding="utf-8")


def replay_dedup_facts_from_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_key: str = "predicted_mentions",
    split: str = "dev",
    model: str = "no-call-replay",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay saved model mention rows through the simplified fact adapter."""

    component_owner = component_owner_for_model(model)
    replay_rows: list[dict[str, Any]] = []
    for row in rows:
        facts, fact_notes = clinical_facts_from_mentions(row.get(source_key) or [])
        mentions, provenance, adapter_notes = clinical_facts_to_mentions(facts)
        letter = ExectLetter(
            letter_id=str(row.get("letter_id") or ""),
            note_text=" ".join(
                str(mention.get("evidence") or "")
                for mention in row.get(source_key) or []
                if isinstance(mention, Mapping)
            ),
            annotations=tuple(),
        )
        replay_row = row_from_final_dedup_facts(
            letter,
            DedupClinicalFactsRecord.model_validate({"clinical_facts": facts}),
            split=split,
            model=model,
            mode="replay",
            raw_generation_output="",
            generation_parse_errors=[],
        )
        replay_row["gold_mentions"] = list(row.get("gold_mentions") or [])
        replay_row["adapter_provenance"] = provenance
        replay_row["adapter_parse_errors"] = [*fact_notes, *adapter_notes]
        replay_row["structured_mentions_final"] = [mention.model_dump() for mention in mentions]
        replay_rows.append(replay_row)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": "replay",
        "call_strategy": "single_call_dedup_facts",
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": "replay",
        "split": split,
        "n_letters": len(replay_rows),
        "summary": summarize_rows(replay_rows),
    }
    return replay_rows, metadata


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
    prompt_profile: PromptProfile,
    call_strategy: CallStrategy,
) -> None:
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    if report_path:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "prompt_profile": prompt_profile,
                "call_strategy": call_strategy,
                "pipeline_family": PIPELINE_FAMILY,
                "component_owner": component_owner_for_model(model),
                "fact_origin": FACT_ORIGIN,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summarize_rows(rows),
                "is_checkpoint": True,
                "total_letters": total,
            },
            _checkpoint_report_path(report_path),
            jsonl_path=jsonl_path or Path(""),
        )


def _checkpoint_report_path(path: Path) -> Path:
    if path.stem.endswith("_checkpoint"):
        return path
    return path.with_name(f"{path.stem}_checkpoint{path.suffix}")


def _has_parse_or_schema_error(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:"))
        for error in (errors or [])
    )
