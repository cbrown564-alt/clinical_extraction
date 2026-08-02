"""Canonical ExECTv2 one-call producer and its two selected projections."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import dspy

from clinical_extraction.core.local_structured_output import (
    FormatOnlyJsonRetry,
    assess_structured_output,
    build_format_only_retry_input,
    validate_format_retry,
)
from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    is_terminal_provider_error,
    raw_output_from_adapter_parse_error,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

from ..llm.pipelines.key_entities_structured.constants import (
    PIPELINE_FAMILY,
    PromptProfile,
    prompt_version_for,
)
from ..llm.pipelines.key_entities_structured.parsing import (
    flatten_events,
    parse_structured_events_json,
)
from ..llm.pipelines.key_entities_structured.projection import (
    to_predicted_letter,
)
from ..llm.pipelines.key_entities_structured.prompt_builders import (
    build_prompt_input,
)
from ..llm.pipelines.key_entities_structured.records import (
    StructuredExtractionRecord,
)
from ..llm.pipelines.key_entities_structured.signatures import (
    DspyKeyEntitiesStructuredExtractor,
)
from .contracts import (
    ExectRecordResult,
    ExectStageEvent,
    StructuredMethodConfig,
    StructuredProducerResult,
)
from .letter_assembly import assemble_structured_rows


def produce_structured_letter(
    letter: ExectLetter,
    *,
    model: str = "",
    temperature: float = 0.0,
    max_tokens: int = 900,
    mode: Literal["live", "prompt-only", "replay"] = "prompt-only",
    dspy_cache: bool = True,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
    split: str | None = None,
    raw_output: str | None = None,
    program: Any | None = None,
    format_retry_program: Any | None = None,
    config: StructuredMethodConfig | None = None,
) -> StructuredProducerResult:
    """Own prompt construction, one model/replay read, parsing, retry, and flattening."""

    config = config or StructuredMethodConfig.selected()
    prompt_version = prompt_version_for(config.prompt_profile)
    prompt_input_json = build_prompt_input(letter, prompt_profile=config.prompt_profile)
    if mode == "replay" and raw_output is None:
        raise ValueError("replay mode requires a saved raw_output")
    raw_text = raw_output if raw_output is not None else ""
    reused = raw_output is not None
    call_error: str | None = None
    if mode == "live" and not reused:
        if program is None:
            dspy.configure(
                lm=build_dspy_lm(
                    model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    cache=dspy_cache,
                    api_base=api_base,
                    api_key=api_key,
                    timeout=timeout,
                )
            )
            program = DspyKeyEntitiesStructuredExtractor()
        try:
            prediction = program(prompt_input_json=prompt_input_json)
            raw_text = str(prediction.extraction_json)
        except Exception as exc:  # pragma: no cover - live provider behavior.
            call_error = f"{type(exc).__name__}: {exc}"
            if is_terminal_provider_error(call_error):
                raise RuntimeError(
                    "Terminal model-provider error; stopping before recording "
                    "placeholder rows: " + call_error
                ) from exc
            recovered = raw_output_from_adapter_parse_error(call_error)
            if recovered:
                raw_text = recovered
                call_error = None

    record, parse_errors = (
        parse_structured_events_json(raw_text) if raw_text else (None, ["not_run"])
    )
    initial_parse_errors = list(parse_errors)
    assessment = assess_structured_output(raw_text, initial_parse_errors, call_error=call_error)
    format_retry_output = ""
    format_retry_notes: list[str] = []
    if mode == "live" and model.startswith("ollama_chat/") and assessment.retry_eligible:
        try:
            format_retry_program = format_retry_program or FormatOnlyJsonRetry()
            retry_prediction = format_retry_program(
                retry_input_json=build_format_only_retry_input(
                    malformed_output=raw_text,
                    schema=StructuredExtractionRecord.model_json_schema(),
                )
            )
            format_retry_output = str(retry_prediction.repaired_json)
            retry_validation = validate_format_retry(
                raw_text, initial_parse_errors, format_retry_output
            )
            retry_record, retry_parse_errors = parse_structured_events_json(format_retry_output)
            format_retry_notes = list(retry_validation.notes)
            if retry_validation.accepted and retry_record is not None:
                record = retry_record
                parse_errors = [*retry_parse_errors, *format_retry_notes]
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

    mentions = flatten_events(record) if record else []
    projected, gate_warnings = to_predicted_letter(
        letter.letter_id,
        mentions,
        note_text=letter.note_text,
        prompt_version=prompt_version,
    )
    row = {
        "letter_id": letter.letter_id,
        "split": split or ("replay" if mode == "prompt-only" else "live"),
        "prompt_version": prompt_version,
        "prompt_profile": config.prompt_profile,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "mode": mode,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_text,
        "call_error": call_error,
        "initial_parse_errors": initial_parse_errors,
        "parse_errors": parse_errors,
        "structured_output_failure_codes": list(assessment.failure_codes),
        "format_retry_output": format_retry_output,
        "format_retry_notes": format_retry_notes,
        "gate_warnings": gate_warnings,
        "n_events_raw": len(record.clinical_events) if record else 0,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(projected.mentions),
        "n_evidence_invalid": len(mentions) - len(projected.mentions),
        "structured_events": [
            event.model_dump() for event in (record.clinical_events if record else [])
        ],
        "predicted_mentions": [_mention_to_row(mention) for mention in projected.mentions],
        "gold_mentions": [],
    }
    _producer_stages = (
        ExectStageEvent(
            stage_id="exect.hybrid.build_prompt",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=letter.letter_id,
            output_value=prompt_input_json,
            changed=True,
            action="build_four_family_prompt",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.model_call",
            owner="model",
            effect_class="clinical_meaning",
            input_value=prompt_input_json,
            output_value=raw_text,
            changed=bool(raw_text),
            action="one_model_or_replay_call",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.parse_and_retry",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=raw_text,
            output_value=row["structured_events"],
            changed=bool(parse_errors or format_retry_output),
            action="parse_schema_and_optional_format_retry",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.flatten_events",
            owner="deterministic",
            effect_class="representation",
            input_value=row["structured_events"],
            output_value=[_mention_to_row(mention) for mention in mentions],
            changed=True,
            action="flatten_model_events",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.project_and_gate",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=[_mention_to_row(mention) for mention in mentions],
            output_value=[_mention_to_row(mention) for mention in projected.mentions],
            changed=len(mentions) != len(projected.mentions),
            action="repair_attributes_and_enforce_evidence",
            rule_category="clinical_epilepsy",
        ),
    )
    producer = StructuredProducerResult(
        letter_id=letter.letter_id,
        prompt_input_json=prompt_input_json,
        raw_output=raw_text,
        parsed_record=record,
        flattened_mentions=tuple(mentions),
        projected_letter=projected,
        gate_warnings=tuple(gate_warnings),
        initial_parse_errors=tuple(initial_parse_errors),
        parse_errors=tuple(parse_errors),
        format_retry_output=format_retry_output,
        format_retry_notes=tuple(format_retry_notes),
        call_error=call_error,
        model=model,
        mode=mode,
        row=row,
    )
    return producer


def run_llm_only_letter(
    letter: ExectLetter,
    producer: StructuredProducerResult,
) -> ExectRecordResult:
    """Project the shared producer to the selected decision-0046 raw lane."""

    _require_matching_letter(letter, producer)
    row = dict(producer.row)
    row["source_method_id"] = "exectv2_llm_only"
    row["source_pipeline_family"] = row.get("pipeline_family", PIPELINE_FAMILY)
    row["method_id"] = "llm"
    row["pipeline_family"] = "llm"
    row["run_id"] = "llm"
    row["scored_view"] = "raw_candidate"
    row["route"] = row.get("route", "")
    stages = _llm_only_producer_stages(producer)
    stages += (
        ExectStageEvent(
            stage_id="exect.llm.raw_candidate",
            owner="deterministic",
            effect_class="benchmark_projection",
            input_value=len(producer.flattened_mentions),
            output_value=len(producer.projected_letter.mentions),
            changed=False,
            action="materialize_raw_candidate_view",
            rule_category="benchmark_format",
        ),
        ExectStageEvent(
            stage_id="exect.llm.score",
            owner="scorer",
            effect_class="benchmark_projection",
            input_value=len(producer.projected_letter.mentions),
            output_value={},
            changed=False,
            action="defer_gold_comparison_to_scorer",
        ),
    )
    return ExectRecordResult(
        prediction=producer.projected_letter,
        row=row,
        stage_events=stages,
        producer=producer,
        scorer_projection={
            "view": "raw_candidate",
            "n_mentions": len(producer.projected_letter.mentions),
        },
        first_prediction_changing_owner="model" if producer.raw_output else None,
        first_failure=producer.call_error or next(iter(producer.parse_errors), None),
    )


def run_llm_with_rules_letter(
    letter: ExectLetter,
    producer: StructuredProducerResult,
    *,
    config: StructuredMethodConfig | None = None,
) -> ExectRecordResult:
    """Apply selected deterministic projections and default/default family lenses."""

    config = config or StructuredMethodConfig.selected()
    config.require_selected()
    return _run_llm_with_rules_letter(letter, producer, config=config)


def run_archived_llm_with_rules_letter(
    letter: ExectLetter,
    producer: StructuredProducerResult,
    *,
    config: StructuredMethodConfig,
) -> ExectRecordResult:
    """Replay an explicitly archived or ablated hybrid policy."""

    if not config.archived_replay:
        raise ValueError("archived replay entry point requires archived_replay=True")
    return _run_llm_with_rules_letter(letter, producer, config=config)


def _run_llm_with_rules_letter(
    letter: ExectLetter,
    producer: StructuredProducerResult,
    *,
    config: StructuredMethodConfig,
) -> ExectRecordResult:
    _require_matching_letter(letter, producer)
    assembled = assemble_structured_rows([letter], [producer.row], config=config)[letter.letter_id]
    stages = list(producer_stages_for(producer))
    stages.extend(
        [
            ExectStageEvent(
                stage_id="exect.hybrid.sf_state_projection",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=producer.row.get("predicted_mentions", []),
                output_value=assembled["lanes"][SEIZURE_FREQUENCY.name]["predicted_mentions"],
                changed=True,
                action="project_seizure_frequency_state",
                rule_category="seizure_frequency",
            ),
            ExectStageEvent(
                stage_id="exect.hybrid.sf_unknown_suppression",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=producer.row.get("predicted_mentions", []),
                output_value=assembled["lanes"][SEIZURE_FREQUENCY.name]["predicted_mentions"],
                changed=False,
                action="suppress_unsupported_unknown_state",
                rule_category="seizure_frequency",
            ),
            ExectStageEvent(
                stage_id="exect.hybrid.register_findings",
                owner="deterministic",
                effect_class="representation",
                input_value=len(producer.projected_letter.mentions),
                output_value=len(assembled["predicted_mentions"]),
                changed=True,
                action="register_raw_and_scored_findings",
                rule_category="general",
            ),
        ]
    )
    lens_stage_names = {
        DIAGNOSIS.name: "diagnosis",
        SEIZURE_FREQUENCY.name: "seizure_frequency",
        PRESCRIPTION.name: "prescription",
        INVESTIGATIONS.name: "investigations",
    }
    for entity in (
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        PRESCRIPTION.name,
        INVESTIGATIONS.name,
    ):
        lane = assembled["lanes"][entity]
        stages.append(
            ExectStageEvent(
                stage_id=f"exect.hybrid.lens.{lens_stage_names[entity]}",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=lane["raw_lane_mentions"],
                output_value=lane["predicted_mentions"],
                changed=lane["raw_lane_mentions"] != lane["predicted_mentions"],
                action="apply_named_family_lens",
                rule_category="clinical_epilepsy",
            )
        )
    stages.extend(
        [
            ExectStageEvent(
                stage_id="exect.hybrid.evidence_requirement",
                owner="deterministic",
                effect_class="validation_gate",
                input_value=len(assembled["predicted_mentions"]),
                output_value=True,
                changed=False,
                action="require_exact_source_evidence",
                rule_category="general",
            ),
            ExectStageEvent(
                stage_id="exect.hybrid.materialize_views",
                owner="deterministic",
                effect_class="benchmark_projection",
                input_value=len(assembled["predicted_mentions"]),
                output_value={
                    surface: len(rows)
                    for surface, rows in assembled["prediction_surfaces"].items()
                },
                changed=True,
                action="materialize_scoring_views",
                rule_category="benchmark_format",
            ),
            ExectStageEvent(
                stage_id="exect.hybrid.score",
                owner="scorer",
                effect_class="benchmark_projection",
                input_value=len(assembled["predicted_mentions"]),
                output_value={},
                changed=False,
                action="defer_gold_comparison_to_scorer",
            ),
        ]
    )
    prediction = _prediction_from_assembly(letter, assembled)
    row = dict(assembled)
    row["method_id"] = "exectv2_llm_with_rules"
    row["scored_view"] = "clinical_headline"
    return ExectRecordResult(
        prediction=prediction,
        row=row,
        stage_events=tuple(stages),
        producer=producer,
        scorer_projection={"view": "clinical_headline", "n_mentions": len(prediction.mentions)},
        first_prediction_changing_owner="model" if producer.raw_output else None,
        first_failure=producer.call_error or next(iter(producer.parse_errors), None),
    )


def run_primary_pair(
    letter: ExectLetter,
    *,
    producer: StructuredProducerResult | None = None,
    config: StructuredMethodConfig | None = None,
    **producer_kwargs: Any,
) -> tuple[ExectRecordResult, ExectRecordResult]:
    """Produce once, then pass the same immutable producer to both paper rows."""

    producer = producer or produce_structured_letter(letter, config=config, **producer_kwargs)
    llm_only = run_llm_only_letter(letter, producer)
    hybrid = run_llm_with_rules_letter(
        letter,
        producer,
        config=config or StructuredMethodConfig.selected(),
    )
    return llm_only, hybrid


def _require_matching_letter(
    letter: ExectLetter, producer: StructuredProducerResult
) -> None:
    if producer.letter_id != letter.letter_id:
        raise ValueError(
            f"producer letter_id {producer.letter_id!r} does not match "
            f"input letter_id {letter.letter_id!r}"
        )


def producer_stages_for(producer: StructuredProducerResult) -> tuple[ExectStageEvent, ...]:
    return (
        ExectStageEvent(
            stage_id="exect.hybrid.build_prompt",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=producer.letter_id,
            output_value=producer.prompt_input_json,
            changed=True,
            action="build_four_family_prompt",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.model_call",
            owner="model",
            effect_class="clinical_meaning",
            input_value=producer.prompt_input_json,
            output_value=producer.raw_output,
            changed=bool(producer.raw_output),
            action="one_model_or_replay_call",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.parse_and_retry",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=producer.raw_output,
            output_value=producer.row.get("structured_events", []),
            changed=bool(producer.parse_errors or producer.format_retry_output),
            action="parse_schema_and_optional_format_retry",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.flatten_events",
            owner="deterministic",
            effect_class="representation",
            input_value=producer.row.get("structured_events", []),
            output_value=[_mention_to_row(m) for m in producer.flattened_mentions],
            changed=True,
            action="flatten_model_events",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.hybrid.project_and_gate",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=[_mention_to_row(m) for m in producer.flattened_mentions],
            output_value=[_mention_to_row(m) for m in producer.projected_letter.mentions],
            changed=len(producer.flattened_mentions) != len(producer.projected_letter.mentions),
            action="repair_attributes_and_enforce_evidence",
            rule_category="clinical_epilepsy",
        ),
    )


def _llm_only_producer_stages(
    producer: StructuredProducerResult,
) -> tuple[ExectStageEvent, ...]:
    """Rename shared producer stages for the distinct raw-candidate method."""

    stages = producer_stages_for(producer)
    return tuple(
        ExectStageEvent(
            stage_id=event.stage_id.replace("exect.hybrid.", "exect.llm."),
            owner=event.owner,
            effect_class=event.effect_class,
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            action=event.action,
            rule_category=event.rule_category,
        )
        for event in stages
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only", "replay"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    config: StructuredMethodConfig | None = None,
    model_builder: Callable[..., Any] | None = None,
    program_factory: Callable[[], Any] | None = None,
    format_retry_factory: Callable[[], Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility batch adapter around the shared producer."""

    config = config or StructuredMethodConfig.selected()
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)
    program = None
    retry_program = None
    if mode == "live":
        model_builder = model_builder or build_dspy_lm
        dspy.configure(
            lm=model_builder(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
                api_key=api_key,
                timeout=timeout,
            )
        )
        program = (
            program_factory()
            if program_factory is not None
            else DspyKeyEntitiesStructuredExtractor()
        )
        retry_program = (
            format_retry_factory()
            if format_retry_factory is not None
            else FormatOnlyJsonRetry()
        )
    prompt_version = prompt_version_for(config.prompt_profile)
    for letter in todo:
        producer = produce_structured_letter(
            letter,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            api_key=api_key,
            timeout=timeout,
            split=split,
            program=program,
            format_retry_program=retry_program,
            config=config,
        )
        row = dict(producer.row)
        if progress_every and (len(rows) - n_resumed + 1) % progress_every == 0:
            rows.append(row)
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
                prompt_version=prompt_version,
                prompt_profile=config.prompt_profile,
            )
            continue
        rows.append(row)
    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": prompt_version,
        "prompt_profile": config.prompt_profile,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
        "diagnosis_policy_variant": config.diagnosis_policy_variant,
        "prescription_policy_variant": config.prescription_policy_variant,
    }
    metadata["summary"] = _summarize_rows(rows)
    return rows, metadata


def _prediction_from_assembly(letter: ExectLetter, row: Mapping[str, Any]) -> PredictedLetter:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
        _predicted_mention,
    )

    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(
            _predicted_mention(mention)
            for mention in row.get("predicted_mentions", [])
        ),
        diagnostics={"view": "clinical_headline", "policy": row.get("policy", {})},
    )


def _mention_to_row(mention: Any) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": getattr(mention, "component_owner", ""),
    }


def _summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    from ..llm.pipelines.key_entities_structured.runner import summarize_rows

    return summarize_rows([dict(row) for row in rows])


def _emit_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
    prompt_version: str,
    prompt_profile: str,
) -> None:
    from ..llm.pipelines.key_entities_structured.runner import (
        _emit_checkpoint as legacy_emit_checkpoint,
    )

    legacy_emit_checkpoint(
        [dict(row) for row in rows],
        total=total,
        jsonl_path=jsonl_path,
        report_path=report_path,
        split=split,
        model=model,
        mode=mode,
        prompt_version=prompt_version,
        prompt_profile=cast(PromptProfile, prompt_profile),
    )
