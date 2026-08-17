"""Canonical ExECTv2 one-call producer and its two selected projections."""

from __future__ import annotations

import hashlib
import json
import threading
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
    format_retry_schema_for,
)
from ..llm.pipelines.key_entities_structured.signatures import (
    DspyKeyEntitiesStructuredExtractor,
)
from .contracts import (
    ExectRecordResult,
    ExectStageEvent,
    StructuredMethodConfig,
    StructuredProducerResult,
    deep_thaw,
)
from .letter_assembly import assemble_structured_rows

SOURCE_PIPELINE_FAMILY = "exectv2_hybrid_key_family_event_ledger"
CHECKPOINT_SCHEMA_VERSION = "exectv2.checkpoint.v1"


def _predict_with_deadline(
    program: Any,
    *,
    prompt_input_json: str,
    timeout: int | None,
) -> tuple[Any | None, str | None]:
    """Run one DSPy predict call, but do not let post-response regex hang the letter."""

    box: dict[str, Any] = {}

    def _run() -> None:
        try:
            box["prediction"] = program(prompt_input_json=prompt_input_json)
        except Exception as exc:
            box["exc"] = exc

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(float(timeout or 300))
    if thread.is_alive():
        return None, "invalid_json: produce_deadline_exceeded"
    if "exc" in box:
        raise box["exc"]
    return box.get("prediction"), None


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
    if mode == "live" and raw_output is not None:
        raise ValueError("live mode does not accept raw_outputs")
    if mode == "replay" and raw_output is None:
        raise ValueError("replay mode requires a saved raw_output")
    raw_text = raw_output if raw_output is not None else ""
    reused = raw_output is not None
    call_error: str | None = None
    parse_deadline_notes: list[str] = []
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
            prediction, deadline_note = _predict_with_deadline(
                program,
                prompt_input_json=prompt_input_json,
                timeout=timeout,
            )
            if deadline_note:
                raw_text = ""
                parse_deadline_notes = [deadline_note]
            elif prediction is not None:
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
    if parse_deadline_notes:
        parse_errors = [*parse_deadline_notes, *parse_errors]
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
                    schema=format_retry_schema_for(prompt_version),
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
        "patient_history": [
            item.model_dump() for item in (record.patient_history if record else [])
        ],
        "medication_history": [
            item.model_dump() for item in (record.medication_history if record else [])
        ],
        "predicted_mentions": [_mention_to_row(mention) for mention in projected.mentions],
        "gold_mentions": [],
    }
    _producer_stages = (
        ExectStageEvent(
            stage_id="exect.llm_with_rules.build_prompt",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=letter.letter_id,
            output_value=prompt_input_json,
            changed=True,
            action="build_four_family_prompt",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.llm_with_rules.model_call",
            owner="model",
            effect_class="clinical_meaning",
            input_value=prompt_input_json,
            output_value=raw_text,
            changed=bool(raw_text),
            action="one_model_or_replay_call",
        ),
        ExectStageEvent(
            stage_id="exect.llm_with_rules.parse_and_retry",
            owner="deterministic",
            effect_class="transport_or_schema",
            input_value=raw_text,
            output_value=row["structured_events"],
            changed=bool(parse_errors or format_retry_output),
            action="parse_schema_and_optional_format_retry",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.llm_with_rules.flatten_events",
            owner="deterministic",
            effect_class="representation",
            input_value=row["structured_events"],
            output_value=[_mention_to_row(mention) for mention in mentions],
            changed=True,
            action="flatten_model_events",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.llm_with_rules.project_and_gate",
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
        route=api_base or "",
        dspy_cache=dspy_cache,
        row=row,
        stage_events=_producer_stages,
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
    row["active_method"] = "llm"
    row["method_id"] = "llm"
    row["pipeline_family"] = "llm"
    row["run_id"] = "llm"
    row["scored_view"] = "raw_candidate"
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
    row["route"] = producer.route
    row["dspy_cache"] = producer.dspy_cache
    row["producer_row"] = dict(producer.row)
    row["prediction"] = producer.projected_letter.model_dump(mode="json")
    row["stage_events"] = [event.to_dict() for event in stages]
    row["scorer_projection"] = {
        "view": "raw_candidate",
        "n_mentions": len(producer.projected_letter.mentions),
    }
    row["first_prediction_changing_owner"] = (
        "model" if producer.raw_output else None
    )
    row["first_failure"] = producer.call_error or next(iter(producer.parse_errors), None)
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
    failure = _blocking_producer_failure(producer)
    if failure is not None:
        return _fail_closed_hybrid_result(letter, producer, config=config, failure=failure)

    producer_row = deep_thaw(producer.row)
    assembled = assemble_structured_rows([letter], [producer_row], config=config)[
        letter.letter_id
    ]
    stages = list(_hybrid_producer_stages(producer))
    stages.extend(
        [
            ExectStageEvent(
                stage_id="exect.llm_with_rules.sf_state_projection",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=producer_row.get("predicted_mentions", []),
                output_value=assembled["lanes"][SEIZURE_FREQUENCY.name]["predicted_mentions"],
                changed=True,
                action="project_seizure_frequency_state",
                rule_category="seizure_frequency",
            ),
            ExectStageEvent(
                stage_id="exect.llm_with_rules.sf_unknown_suppression",
                owner="deterministic",
                effect_class="clinical_meaning",
                input_value=producer_row.get("predicted_mentions", []),
                output_value=assembled["lanes"][SEIZURE_FREQUENCY.name]["predicted_mentions"],
                changed=False,
                action="suppress_unsupported_unknown_state",
                rule_category="seizure_frequency",
            ),
            ExectStageEvent(
                stage_id="exect.llm_with_rules.register_findings",
                owner="deterministic",
                effect_class="transport_or_schema",
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
                stage_id=f"exect.llm_with_rules.lens.{lens_stage_names[entity]}",
                owner="deterministic",
                effect_class=(
                    "representation"
                    if entity in {SEIZURE_FREQUENCY.name, INVESTIGATIONS.name}
                    else "clinical_meaning"
                ),
                input_value=lane["raw_lane_mentions"],
                output_value=lane["predicted_mentions"],
                changed=lane["raw_lane_mentions"] != lane["predicted_mentions"],
                action="apply_named_family_lens",
                rule_category=(
                    "seizure_frequency"
                    if entity == SEIZURE_FREQUENCY.name
                    else "clinical_epilepsy"
                ),
            )
        )
    stages.extend(
        [
            ExectStageEvent(
                stage_id="exect.llm_with_rules.evidence_requirement",
                owner="deterministic",
                effect_class="validation_gate",
                input_value=len(assembled["predicted_mentions"]),
                output_value=True,
                changed=False,
                action="require_exact_source_evidence",
                rule_category="general",
            ),
            ExectStageEvent(
                stage_id="exect.llm_with_rules.materialize_views",
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
                stage_id="exect.llm_with_rules.score",
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
    row = producer_row
    row.update(assembled)
    row["source_method_id"] = "exectv2_llm_with_rules"
    row["source_pipeline_family"] = SOURCE_PIPELINE_FAMILY
    row["active_method"] = "llm_with_rules"
    row["method_id"] = "llm_with_rules"
    row["pipeline_family"] = "llm_with_rules"
    row["run_id"] = "llm_with_rules"
    row["split"] = producer.row.get("split", row.get("split"))
    row["route"] = producer.route
    row["dspy_cache"] = producer.dspy_cache
    row["producer_row"] = deep_thaw(producer.row)
    row["prediction"] = prediction.model_dump(mode="json")
    row["scored_view"] = "clinical_headline"
    row["stage_events"] = [event.to_dict() for event in stages]
    row["scorer_projection"] = {
        "view": "clinical_headline",
        "n_mentions": len(prediction.mentions),
    }
    row["first_prediction_changing_owner"] = (
        "model" if producer.raw_output else None
    )
    row["first_failure"] = _producer_first_failure(producer)
    return ExectRecordResult(
        prediction=prediction,
        row=row,
        stage_events=tuple(stages),
        producer=producer,
        scorer_projection={"view": "clinical_headline", "n_mentions": len(prediction.mentions)},
        first_prediction_changing_owner="model" if producer.raw_output else None,
        first_failure=_producer_first_failure(producer),
    )


def _blocking_producer_failure(producer: StructuredProducerResult) -> str | None:
    """Return a terminal producer failure before any deterministic assembly runs."""

    if producer.call_error:
        return producer.call_error
    for error in producer.parse_errors:
        if str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run")):
            return str(error)
    if producer.initial_parse_errors and not producer.format_retry_output:
        for error in producer.initial_parse_errors:
            if str(error).startswith(
                ("invalid_json:", "schema_validation_error:", "not_run")
            ):
                return str(error)
    if producer.parsed_record is None:
        failure_codes = producer.row.get("structured_output_failure_codes", [])
        return "; ".join(str(code) for code in failure_codes) or "schema_blocking_output"
    return None


def _producer_first_failure(producer: StructuredProducerResult) -> str | None:
    return (
        producer.call_error
        or next(iter(producer.parse_errors), None)
        or next(iter(producer.initial_parse_errors), None)
    )


def _fail_closed_hybrid_result(
    letter: ExectLetter,
    producer: StructuredProducerResult,
    *,
    config: StructuredMethodConfig,
    failure: str,
) -> ExectRecordResult:
    """Return an explicit empty clinical result when model output is unusable."""

    stages = list(_hybrid_producer_stages(producer))
    stages.append(
        ExectStageEvent(
            stage_id="exect.llm_with_rules.fail_closed",
            owner="deterministic",
            effect_class="validation_gate",
            input_value={
                "call_error": producer.call_error,
                "initial_parse_errors": list(producer.initial_parse_errors),
                "parse_errors": list(producer.parse_errors),
                "structured_output_failure_codes": producer.row.get(
                    "structured_output_failure_codes", []
                ),
            },
            output_value={"predicted_mentions": [], "failure": failure},
            changed=True,
            action="fail_closed_on_producer_error",
            rule_category="general",
        )
    )
    prediction = PredictedLetter(
        letter_id=letter.letter_id,
        mentions=(),
        diagnostics={
            "view": "clinical_headline",
            "policy": {
                "diagnosis_policy_variant": config.diagnosis_policy_variant,
                "prescription_policy_variant": config.prescription_policy_variant,
                "sf_projection_ablation": config.sf_projection_ablation,
            },
            "status": "blocked",
            "failure": failure,
        },
    )
    row = deep_thaw(producer.row)
    row.update(
        {
            "source_method_id": "exectv2_llm_with_rules",
            "source_pipeline_family": SOURCE_PIPELINE_FAMILY,
            "active_method": "llm_with_rules",
            "method_id": "llm_with_rules",
            "pipeline_family": "llm_with_rules",
            "run_id": "llm_with_rules",
            "split": producer.row.get("split", "operational"),
            "route": producer.route,
            "dspy_cache": producer.dspy_cache,
            "producer_row": deep_thaw(producer.row),
            "predicted_mentions": [],
            "prediction": prediction.model_dump(mode="json"),
            "scored_view": "clinical_headline",
            "stage_events": [event.to_dict() for event in stages],
            "scorer_projection": {
                "view": "clinical_headline",
                "n_mentions": 0,
                "status": "blocked",
            },
            "first_prediction_changing_owner": "model" if producer.raw_output else None,
            "first_failure": failure,
            "status": "blocked",
        }
    )
    scorer_projection = {
        "view": "clinical_headline",
        "n_mentions": 0,
        "status": "blocked",
    }
    return ExectRecordResult(
        prediction=prediction,
        row=row,
        stage_events=tuple(stages),
        producer=producer,
        scorer_projection=scorer_projection,
        first_prediction_changing_owner="model" if producer.raw_output else None,
        first_failure=failure,
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
    return producer.stage_events


def _hybrid_producer_stages(
    producer: StructuredProducerResult,
) -> tuple[ExectStageEvent, ...]:
    return tuple(
        ExectStageEvent(
            stage_id=event.stage_id,
            owner=event.owner,
            effect_class=(
                "clinical_meaning"
                if event.stage_id == "exect.llm_with_rules.project_and_gate"
                else event.effect_class
            ),
            input_value=event.input_value,
            output_value=event.output_value,
            changed=event.changed,
            action=event.action,
            rule_category=event.rule_category,
        )
        for event in producer_stages_for(producer)
    )


def _llm_only_producer_stages(
    producer: StructuredProducerResult,
) -> tuple[ExectStageEvent, ...]:
    """Rename shared producer stages for the distinct raw-candidate method."""

    stages = producer_stages_for(producer)
    return tuple(
        ExectStageEvent(
            stage_id=event.stage_id.replace("exect.llm_with_rules.", "exect.llm."),
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
    program: Any | None = None,
    format_retry_program: Any | None = None,
    raw_outputs: Mapping[str, str] | None = None,
    projection: Literal["producer", "llm", "llm_with_rules"] = "producer",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility batch adapter around the shared producer."""

    if mode not in {"live", "prompt-only", "replay"}:
        raise ValueError("ExECT split mode must be live, prompt-only, or replay")
    if mode == "live" and raw_outputs is not None:
        raise ValueError("live mode does not accept raw_outputs")
    if mode == "prompt-only" and raw_outputs is not None:
        raise ValueError("prompt-only mode does not accept raw_outputs")
    config = config or StructuredMethodConfig.selected()
    if projection not in {"producer", "llm", "llm_with_rules"}:
        raise ValueError(f"unsupported ExECT split projection: {projection}")
    if projection == "llm_with_rules":
        config.require_selected()
    order = [letter.letter_id for letter in letters]
    if len(order) != len(set(order)):
        raise ValueError("ExECT split letters must have unique letter_id values")
    if mode == "replay":
        if raw_outputs is None or set(raw_outputs) != set(order):
            raise ValueError("replay mode requires complete raw_outputs for the requested letters")
    run_contract = _run_contract(
        projection=projection,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        config=config,
        replay_content_sha256=(
            _replay_content_fingerprint(raw_outputs) if mode == "replay" else None
        ),
    )
    run_fingerprint = _run_fingerprint(run_contract)
    requested = set(order)
    try:
        existing_rows, completed = read_completed(
            checkpoint_jsonl_path if resume else None, key="letter_id"
        )
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("checkpoint is malformed") from exc
    if resume and checkpoint_jsonl_path is not None and checkpoint_jsonl_path.exists():
        _validate_checkpoint(
            existing_rows,
            requested=requested,
            run_contract=run_contract,
            run_fingerprint=run_fingerprint,
            report_path=checkpoint_report_path,
        )
    rows: list[dict[str, Any]] = list(existing_rows)
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)
    retry_program = format_retry_program
    if mode == "live" and todo:
        model_builder = model_builder or build_dspy_lm
        if program is None:
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
        if retry_program is None:
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
            raw_output=(raw_outputs or {}).get(letter.letter_id),
            config=config,
        )
        if projection == "llm":
            result = run_llm_only_letter(letter, producer)
            row = dict(result.row)
        elif projection == "llm_with_rules":
            result = run_llm_with_rules_letter(letter, producer, config=config)
            row = dict(result.row)
        else:
            row = dict(producer.row)
        if checkpoint_jsonl_path is not None or resume:
            row["run_contract"] = dict(run_contract)
            row["run_fingerprint"] = run_fingerprint
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
                run_contract=run_contract,
                run_fingerprint=run_fingerprint,
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
        "run_contract": run_contract,
        "run_fingerprint": run_fingerprint,
    }
    if projection in {"llm", "llm_with_rules"}:
        active_method = "llm" if projection == "llm" else "llm_with_rules"
        method_id = active_method
        scored_view = "raw_candidate" if projection == "llm" else "clinical_headline"
        metadata.update(
            {
                "active_method": active_method,
                "method_id": method_id,
                "pipeline_family": active_method,
                "run_id": active_method,
                "scored_view": scored_view,
            }
        )
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
    run_contract: Mapping[str, Any],
    run_fingerprint: str,
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
    if report_path is not None and jsonl_path is not None:
        _checkpoint_metadata_path(report_path).write_text(
            json.dumps(
                {
                    "schema_version": CHECKPOINT_SCHEMA_VERSION,
                    "run_contract": dict(run_contract),
                    "run_fingerprint": run_fingerprint,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


def _run_contract(
    *,
    projection: str,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    dspy_cache: bool,
    api_base: str | None,
    config: StructuredMethodConfig,
    replay_content_sha256: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "active_method": projection,
        "method_id": projection,
        "pipeline_family": projection if projection != "producer" else PIPELINE_FAMILY,
        "split": split,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "dspy_cache": dspy_cache,
        "route": api_base or "",
        "prompt_profile": config.prompt_profile,
        "prompt_version": prompt_version_for(config.prompt_profile),
        "diagnosis_policy_variant": config.diagnosis_policy_variant,
        "prescription_policy_variant": config.prescription_policy_variant,
        "sf_projection_ablation": config.sf_projection_ablation,
        "replay_content_sha256": replay_content_sha256,
    }


def _replay_content_fingerprint(raw_outputs: Mapping[str, str] | None) -> str:
    if raw_outputs is None:
        raise ValueError("replay mode requires raw outputs")
    payload = json.dumps(dict(raw_outputs), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _run_fingerprint(contract: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(contract), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    *,
    requested: set[str],
    run_contract: Mapping[str, Any],
    run_fingerprint: str,
    report_path: Path | None,
) -> None:
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"checkpoint row {index} is malformed")
        letter_id = row.get("letter_id")
        if not isinstance(letter_id, str) or not letter_id:
            raise ValueError(f"checkpoint row {index} is missing letter_id")
        if letter_id not in requested:
            raise ValueError(f"checkpoint row {letter_id} is foreign to the requested split")
        if letter_id in seen:
            raise ValueError(f"checkpoint contains duplicate letter_id {letter_id}")
        seen.add(letter_id)
        if row.get("run_fingerprint") != run_fingerprint:
            raise ValueError(f"checkpoint row {letter_id} has mismatched run_fingerprint")
        if row.get("run_contract") != dict(run_contract):
            raise ValueError(f"checkpoint row {letter_id} has mismatched run provenance")

    if report_path is None:
        return
    metadata_file = _checkpoint_metadata_path(report_path)
    if not metadata_file.exists():
        raise ValueError("checkpoint provenance metadata is missing for resume")
    try:
        report = json.loads(metadata_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("checkpoint report is malformed") from exc
    if not isinstance(report, Mapping):
        raise ValueError("checkpoint report is malformed")
    if report.get("run_fingerprint") != run_fingerprint:
        raise ValueError("checkpoint report has mismatched run_fingerprint")
    if report.get("run_contract") != dict(run_contract):
        raise ValueError("checkpoint report has mismatched run provenance")


def _checkpoint_metadata_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}_checkpoint.meta.json")
