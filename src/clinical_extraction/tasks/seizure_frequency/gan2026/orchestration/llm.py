"""Canonical per-record orchestrator for Gan 2026 LLM-only extraction."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.contracts import (
    GanModelOutput,
    GanRecordResult,
    GanStageEvent,
    ModelOutputSource,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.scaffolding import (
    attach_row_scoring,
    common_split_metadata_updates,
    configure_live_lm,
    configure_split_lm,
    envelope_model_call_error,
    finalize_split_metadata,
    first_prediction_changing_owner,
    maybe_emit_progress_checkpoint,
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
    model_output_source: ModelOutputSource | None = None,
    prompt_input_json: str | None = None,
    program: Any | None = None,
) -> GanRecordResult:
    """Run one record through the explicit LLM-only stage order.

    ``raw_output`` and ``model_output_source`` are replay seams. Once a value
    crosses this boundary, downstream code sees only repository-owned strings
    and parsed records, never a provider SDK response.
    """

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm as legacy,
    )

    prompt_input_json = prompt_input_json or legacy.build_prompt_input(record)
    model_output = GanModelOutput(raw_output=raw_output or "")
    reused_raw_output = raw_output is not None and raw_output != ""
    call_error: str | None = None
    if model_output_source is not None and not reused_raw_output:
        model_output = model_output_source.read(
            record,
            prompt_input_json=prompt_input_json,
            config=config,
        )
        reused_raw_output = model_output.reused
    elif mode == "live" and not reused_raw_output:
        if program is None:
            configure_live_lm(config)
            program = legacy.DspyCanonicalLlmExtractor()
        try:
            prediction = program(prompt_input_json=prompt_input_json)
            model_output = GanModelOutput(raw_output=str(prediction.decision_json))
        except Exception as exc:  # pragma: no cover - live provider behavior.
            call_error = envelope_model_call_error(exc)
            model_output = GanModelOutput(raw_output="", call_error=call_error)

    raw_text = model_output.raw_output
    call_error = call_error or model_output.call_error
    if raw_text:
        decision, parse_errors, row_trace = legacy.parse_decision_json_with_trace(raw_text)
    else:
        decision, parse_errors, row_trace = (
            None,
            ["not_run"],
            legacy._llm_only_row_trace(
                model_decision=None,
                schema_payload_changed=False,
                format_events=["not_run"],
                adapter_events=[],
            ),
        )

    evidence_text_contained = bool(
        decision
        and decision.evidence
        and legacy.evidence_is_substring(record.note_text, decision.evidence)
    )
    row_trace["evidence_validation"] = {
        "evidence": decision.evidence if decision else "",
        "exact_substring": evidence_text_contained,
    }
    row_trace["scoring"] = None
    diagnostics: dict[str, Any] = {
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_text,
        "reused_raw_output": reused_raw_output,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "evidence_text_contained": evidence_text_contained,
        "row_trace": row_trace,
    }
    output = FinalExtraction(
        final_value=decision.final_label if decision else "unknown",
        rationale=decision.rationale if decision else "extraction failed",
        evidence=decision.evidence if decision else "",
    )

    adapter_events = row_trace.get("deterministic_adapter", {}).get("events", [])
    schema_events = row_trace.get("format_repair", {}).get("events", [])
    stage_events = (
        GanStageEvent(
            stage_id="gan.llm.build_prompt",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=record.source_row_index,
            output_value=prompt_input_json,
            changed=True,
            action="build_prompt_input",
            rule_category="general",
        ),
        GanStageEvent(
            stage_id="gan.llm.model_call",
            owner="model",
            effect_class="clinical_meaning",
            input_value=prompt_input_json,
            output_value=raw_text,
            changed=bool(raw_text),
            action="model_or_replay_output",
        ),
        GanStageEvent(
            stage_id="gan.llm.json_schema_repair",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=raw_text,
            output_value=decision.model_dump() if decision else None,
            changed=bool(schema_events),
            action="parse_json_and_repair_dialect",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.llm.schema_validation",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=raw_text,
            output_value=decision.model_dump() if decision else None,
            changed=any(
                str(error).startswith("schema_validation_error:")
                for error in parse_errors
            ),
            action="validate_decision_schema",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.llm.selected_evidence_repair",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=row_trace.get("deterministic_adapter", {}).get("before_label"),
            output_value=row_trace.get("deterministic_adapter", {}).get("after_label"),
            changed=bool(adapter_events),
            action="repair_label_from_selected_evidence",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.llm.scorable_label_check",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=output.final_value,
            output_value={
                "scorable": not any(
                    "unscorable_final_label:" in str(error) for error in parse_errors
                )
            },
            changed=any(
                "unscorable_final_label:" in str(error) for error in parse_errors
            ),
            action="validate_scorable_label",
            rule_category="benchmark_format",
        ),
        GanStageEvent(
            stage_id="gan.llm.evidence_containment",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=output.evidence,
            output_value={"exact_substring": evidence_text_contained},
            changed=not evidence_text_contained,
            action="validate_exact_evidence_substring",
            rule_category="general",
        ),
        GanStageEvent(
            stage_id="gan.llm.score",
            owner="scorer",
            effect_class="benchmark_projection",
            input_value=output.model_dump(),
            output_value={},
            changed=False,
            action="defer_gold_comparison_to_scorer",
        ),
    )
    first_owner = first_prediction_changing_owner(stage_events)
    first_failure = call_error or next(
        (str(error) for error in parse_errors if str(error) != "json_dialect_repaired"),
        None,
    )
    return GanRecordResult(
        output=output,
        diagnostics=diagnostics,
        stage_events=stage_events,
        raw_model_output=raw_text,
        parsed_model_output=decision,
        deterministic_output=decision,
        first_prediction_changing_owner=first_owner,
        first_failure=first_failure,
        scorer_projection={
            "final_label": output.final_value,
            "evidence_text_contained": evidence_text_contained,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Batch adapter: loading and checkpoint policy remain outside ``run_record``."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm as legacy,
    )

    reuse_raw_outputs = reuse_raw_outputs or {}
    config = PipelineConfiguration(
        architecture="llm",
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        dspy_cache=dspy_cache,
        api_base=api_base,
    )
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
        common_split_metadata_updates(
            dspy_cache=dspy_cache,
            reuse_source=reuse_source,
            escalation_reason=escalation_reason,
        )
    )
    program = None
    if mode == "live":
        configure_split_lm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            dspy_cache=dspy_cache,
            api_base=api_base,
        )
        program = legacy.DspyCanonicalLlmExtractor()

    rows: list[dict[str, Any]] = []
    for record in records:
        result = run_record(
            record,
            config,
            mode=mode,
            raw_output=reuse_raw_outputs.get(record.source_row_index),
            program=program,
        )
        decision = result.parsed_model_output
        row_trace = attach_row_scoring(
            result,
            record=record,
            compare_fn=legacy._compare_to_gold,
            parsed=decision,
        )
        row = {
            "source_row_index": record.source_row_index,
            "split": split,
            "split_manifest": split_manifest,
            "prompt_version": legacy.PROMPT_VERSION,
            "prompt_input_json": result.diagnostics["prompt_input_json"],
            "raw_output": result.raw_model_output or "",
            "reused_raw_output": result.diagnostics["reused_raw_output"],
            "call_error": result.diagnostics["call_error"],
            "parse_errors": result.diagnostics["parse_errors"],
            "decision_record": decision.model_dump() if decision else None,
            "evidence_text_contained": result.scorer_projection["evidence_text_contained"],
            "row_trace": row_trace,
            "reference": {
                "gold_label": record.gold_label,
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "row_ok": record.row_ok,
            },
            "comparison": row_trace["scoring"],
        }
        rows.append(row)
        maybe_emit_progress_checkpoint(
            rows,
            metadata,
            total=len(records),
            progress_every=progress_every,
            jsonl_path=checkpoint_jsonl_path,
            report_path=checkpoint_report_path,
            emit_fn=legacy._emit_progress_checkpoint,
        )
    return finalize_split_metadata(rows, metadata, legacy.summarize_records)
