"""Canonical per-record orchestrator for Gan 2026 LLM-with-rules extraction."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal, cast

import dspy

from clinical_extraction.core.local_structured_output import (
    FormatOnlyJsonRetry,
    assess_structured_output,
    build_format_only_retry_input,
    raw_output_from_adapter_error,
    validate_format_retry,
)
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.contracts import (
    GanRecordResult,
    GanStageEvent,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_record(
    record: GanFrequencyRecord,
    config: PipelineConfiguration,
    *,
    mode: Literal["live", "prompt-only"] = "live",
    raw_output: str | None = None,
    program: Any | None = None,
    format_retry_program: Any | None = None,
    repair_config: Any | None = None,
) -> GanRecordResult:
    """Run one structured-events record through the frozen hybrid stage order."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as legacy,
    )

    prompt_version = config.prompt_version or legacy.PROMPT_VERSION
    prompt_input_json = legacy.build_prompt_input(record, prompt_version=prompt_version)
    repair_config = repair_config or (
        legacy.StructuredRepairConfig.for_mode(
            cast(legacy.StructuredRepairMode, config.repair_mode)
        )
        if config.repair_mode
        else legacy.StructuredRepairConfig()
    )
    raw_text = raw_output or ""
    reused_raw_output = raw_output is not None and raw_output != ""
    call_error: str | None = None
    adapter_repair_notes: list[str] = []

    if mode == "live" and not reused_raw_output:
        if program is None:
            dspy.configure(
                lm=build_dspy_lm(
                    config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    cache=config.dspy_cache,
                    api_base=config.api_base,
                    api_key=config.api_key,
                    timeout=config.timeout,
                )
            )
            program = legacy.DspyStructuredExtractor()
        try:
            prediction = program(prompt_input_json=prompt_input_json)
            raw_text = str(prediction.structured_json)
        except Exception as exc:  # pragma: no cover - live provider behavior.
            call_error = f"{type(exc).__name__}: {exc}"
            recovered = raw_output_from_adapter_error(call_error)
            if recovered:
                raw_text = recovered
                call_error = None
                adapter_repair_notes.append(
                    "adapter_output_field_repaired: structured_json_missing"
                )

    if raw_text:
        extraction, normalized_events, parse_errors, row_trace = (
            legacy.parse_structured_json_with_trace(
                raw_text,
                note_text=record.note_text,
                repair_config=repair_config,
            )
        )
    else:
        extraction, normalized_events, parse_errors, row_trace = (
            None,
            [],
            ["not_run"],
            legacy._hybrid_row_trace(
                model_extraction=None,
                schema_payload_changed=False,
                format_events=["not_run"],
                resolved_label=None,
                final_label=None,
                semantic_events=[],
            ),
        )

    initial_parse_errors = list(parse_errors)
    assessment = assess_structured_output(raw_text, initial_parse_errors, call_error=call_error)
    format_retry_output = ""
    format_retry_notes: list[str] = []
    if (
        mode == "live"
        and config.model.startswith("ollama_chat/")
        and assessment.retry_eligible
    ):
        try:
            format_retry_program = format_retry_program or FormatOnlyJsonRetry()
            retry_prediction = format_retry_program(
                retry_input_json=build_format_only_retry_input(
                    malformed_output=raw_text,
                    schema=legacy.StructuredExtractionRecord.model_json_schema(),
                )
            )
            format_retry_output = str(retry_prediction.repaired_json)
            retry_validation = validate_format_retry(
                raw_text, initial_parse_errors, format_retry_output
            )
            retry_extraction, retry_events, retry_errors, retry_row_trace = (
                legacy.parse_structured_json_with_trace(
                    format_retry_output,
                    note_text=record.note_text,
                    repair_config=repair_config,
                )
            )
            format_retry_notes = list(retry_validation.notes)
            if retry_validation.accepted and retry_extraction is not None:
                extraction = retry_extraction
                normalized_events = retry_events
                row_trace = retry_row_trace
                row_trace["model_prediction"]["raw_output_field"] = "format_retry_output"
                parse_errors = [*retry_errors, *format_retry_notes]
            elif retry_validation.accepted:
                format_retry_notes = ["format_retry_rejected: schema_validation"]
                parse_errors = [*initial_parse_errors, *format_retry_notes]
            else:
                parse_errors = [*initial_parse_errors, *format_retry_notes]
        except Exception as exc:  # pragma: no cover - live provider behavior.
            format_retry_notes = [
                f"format_retry_rejected: provider_error:{type(exc).__name__}"
            ]
            parse_errors = [*initial_parse_errors, *format_retry_notes]

    parse_errors = [*adapter_repair_notes, *parse_errors]
    evidence_valid = bool(
        extraction
        and extraction.selection.evidence
        and legacy.evidence_is_substring(record.note_text, extraction.selection.evidence)
    )
    final_label = extraction.selection.final_label if extraction else None
    output = FinalExtraction(
        final_value=final_label or "unknown",
        rationale=extraction.selection.rationale if extraction else "extraction failed",
        evidence=extraction.selection.evidence if extraction else "",
    )
    row_trace["format_repair"]["events"] = [
        *adapter_repair_notes,
        *row_trace["format_repair"]["events"],
        *format_retry_notes,
    ]
    row_trace["evidence_validation"] = {
        "evidence": output.evidence,
        "exact_substring": evidence_valid,
    }
    row_trace["scoring"] = None
    diagnostics: dict[str, Any] = {
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_text,
        "reused_raw_output": reused_raw_output,
        "call_error": call_error,
        "initial_parse_errors": initial_parse_errors,
        "parse_errors": parse_errors,
        "structured_output_failure_codes": list(assessment.failure_codes),
        "format_retry_output": format_retry_output,
        "format_retry_notes": format_retry_notes,
        "structured_record": extraction.model_dump() if extraction else None,
        "normalized_events": [event.model_dump() for event in normalized_events],
        "evidence_valid": evidence_valid,
        "row_trace": row_trace,
        "repair_config": asdict(repair_config),
    }

    semantic = row_trace.get("deterministic_semantic", {})
    repair_events = semantic.get("events", []) if isinstance(semantic, Mapping) else []
    stage_events: list[GanStageEvent] = [
        GanStageEvent(
            stage_id="gan.hybrid.build_prompt",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=record.source_row_index,
            output_value=prompt_input_json,
            changed=True,
            action="build_prompt_input",
            rule_category="general",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.model_call",
            owner="model",
            effect_class="clinical_meaning",
            input_value=prompt_input_json,
            output_value=raw_text,
            changed=bool(raw_text),
            action="model_or_replay_output",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.json_schema_repair",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=raw_text,
            output_value=extraction.model_dump() if extraction else None,
            changed=bool(row_trace.get("format_repair", {}).get("events")),
            action="repair_json_dialect_and_payload_shape",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.format_only_retry",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=initial_parse_errors,
            output_value=format_retry_output,
            changed=bool(format_retry_output),
            action="optional_format_only_retry",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.schema_validation",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=raw_text,
            output_value=extraction.model_dump() if extraction else None,
            changed=any(
                str(error).startswith("schema_validation_error:")
                for error in parse_errors
            ),
            action="validate_structured_extraction_schema",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.normalize_events",
            owner="deterministic",
            effect_class="representation",
            input_value=extraction.model_dump() if extraction else None,
            output_value=[event.model_dump() for event in normalized_events],
            changed=bool(normalized_events),
            action="normalize_model_events",
            rule_category="seizure_frequency",
        ),
        GanStageEvent(
            stage_id="gan.hybrid.resolve_label",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=(
                row_trace.get("model_prediction", {}).get("record", {}).get("selection")
                if extraction
                else None
            ),
            output_value=final_label,
            changed=True,
            action="resolve_model_selected_event",
            rule_category="gan2026_specific",
        ),
    ]
    repair_stage_ids = (
        "selected_evidence",
        "monthly_diary",
        "usual_interval",
        "typical_over_ytd",
        "breakthrough",
        "non_epileptic",
        "residual_jerk",
        "post_change_burst",
        "dated_sequence",
        "elapsed_anchor",
    )
    for family in repair_stage_ids:
        family_event = next(
            (
                event
                for event in repair_events
                if isinstance(event, Mapping) and str(event.get("family")) == family
            ),
            None,
        )
        stage_events.append(
            GanStageEvent(
                stage_id=f"gan.hybrid.repair.{family}",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=(family_event or {}).get("before_label"),
                output_value=(family_event or {}).get("after_label"),
                changed=bool(family_event and family_event.get("changed")),
                action="apply_named_repair_family",
                rule_category="seizure_frequency",
            )
        )
    stage_events.extend(
        [
            GanStageEvent(
                stage_id="gan.hybrid.scorable_label_check",
                owner="deterministic",
                effect_class="validation_gate",
                input_value=output.final_value,
                output_value={"scorable": not any("unscorable" in str(e) for e in parse_errors)},
                changed=any("unscorable" in str(e) for e in parse_errors),
                action="validate_scorable_label",
                rule_category="benchmark_format",
            ),
            GanStageEvent(
                stage_id="gan.hybrid.evidence_containment",
                owner="deterministic",
                effect_class="validation_gate",
                input_value=output.evidence,
                output_value={"exact_substring": evidence_valid},
                changed=not evidence_valid,
                action="validate_exact_evidence_substring",
                rule_category="general",
            ),
            GanStageEvent(
                stage_id="gan.hybrid.score",
                owner="scorer",
                effect_class="benchmark_projection",
                input_value=output.model_dump(),
                output_value={},
                changed=False,
                action="defer_gold_comparison_to_scorer",
            ),
        ]
    )
    first_owner = next(
        (
            event.owner
            for event in stage_events
            if event.changed and event.effect_class == "clinical_meaning"
        ),
        None,
    )
    first_failure = call_error or next(
        (
            str(error)
            for error in parse_errors
            if not str(error).startswith("json_dialect_repaired")
        ),
        None,
    )
    return GanRecordResult(
        output=output,
        diagnostics=diagnostics,
        stage_events=tuple(stage_events),
        raw_model_output=raw_text,
        parsed_model_output=extraction,
        deterministic_output=normalized_events,
        first_prediction_changing_owner=first_owner,
        first_failure=first_failure,
        scorer_projection={
            "final_label": output.final_value,
            "evidence_valid": evidence_valid,
        },
    )


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    repair_config: Any | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Batch adapter with checkpoint/report concerns outside the record core."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
        repair_mode_metadata,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as legacy,
    )

    reuse_raw_outputs = reuse_raw_outputs or {}
    config = PipelineConfiguration(
        architecture="llm_with_rules",
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        dspy_cache=dspy_cache,
        api_base=api_base,
    )
    repair_config = repair_config or legacy.StructuredRepairConfig()
    metadata = legacy._run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata.update(
        {
            "pipeline_family": "llm_with_rules",
            "dspy_cache": dspy_cache,
            "reuse_source": reuse_source,
            "escalation_reason": escalation_reason,
            "repair_mode": repair_config.resolved_repair_mode,
            "repair_mode_metadata": repair_mode_metadata(repair_config.resolved_repair_mode),
            "repair_config": asdict(repair_config),
        }
    )
    program = None
    retry_program = None
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
        program = legacy.DspyStructuredExtractor()
        retry_program = FormatOnlyJsonRetry()

    rows: list[dict[str, Any]] = []
    for record in records:
        result = run_record(
            record,
            config,
            mode=mode,
            raw_output=reuse_raw_outputs.get(record.source_row_index),
            program=program,
            format_retry_program=retry_program,
            repair_config=repair_config,
        )
        row_trace = dict(result.diagnostics["row_trace"])
        extraction = result.parsed_model_output
        comparison = legacy._compare_to_gold(record, extraction) if extraction else None
        row_trace["scoring"] = comparison
        row = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "pipeline_family": "llm_with_rules",
            "prompt_version": legacy.PROMPT_VERSION,
            "prompt_input_json": result.diagnostics["prompt_input_json"],
            "raw_output": result.raw_model_output or "",
            "reused_raw_output": result.diagnostics["reused_raw_output"],
            "call_error": result.diagnostics["call_error"],
            "initial_parse_errors": result.diagnostics["initial_parse_errors"],
            "parse_errors": result.diagnostics["parse_errors"],
            "structured_output_failure_codes": result.diagnostics[
                "structured_output_failure_codes"
            ],
            "format_retry_output": result.diagnostics["format_retry_output"],
            "format_retry_notes": result.diagnostics["format_retry_notes"],
            "structured_record": extraction.model_dump() if extraction else None,
            "normalized_events": result.diagnostics["normalized_events"],
            "evidence_valid": result.diagnostics["evidence_valid"],
            "row_trace": row_trace,
            "reference": {
                "gold_label": record.gold_label,
                "gold_normalized_label": record.gold_normalized_label,
                "gold_label_kind": str(record.gold_label_kind),
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "row_ok": record.row_ok,
            },
            "comparison": comparison,
        }
        rows.append(row)
        if progress_every and len(rows) % progress_every == 0:
            legacy._emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )
    metadata["summary"] = legacy.summarize_records(rows)
    return rows, metadata
