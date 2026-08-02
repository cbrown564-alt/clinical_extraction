"""Operational wrapper for the selected one-call ExECT LLM-with-rules pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter


def run_exect_notes(
    notes: Sequence[InputNote], runtime: RuntimeConfig, *, method: str = "llm_with_rules"
) -> list[dict[str, Any]]:
    """Run the selected ExECT method while preserving the live default."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
        active_method_name,
    )

    active_method = active_method_name(method)
    if active_method == "rules":
        runner = Exectv2PipelineRunner(Exectv2PipelineConfiguration(method=method))
        rules_output: list[dict[str, Any]] = []
        for note in notes:
            result = runner.run(ExectLetter(note.note_id, note.text)).result
            rules_output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "ok",
                    "model": "(model-independent)",
                    "pipeline": "rules",
                    "method": "rules",
                    "run_id": "rules",
                    "prediction": {
                        "mentions": [
                            mention.model_dump(mode="json")
                            for mention in result.prediction.mentions
                        ]
                    },
                    "comparison_projection": result.comparison_projection.model_dump(mode="json"),
                    "diagnostics": dict(result.prediction.diagnostics),
                    "trace": [event.to_dict() for event in result.stage_events],
                }
            )
        return rules_output
    if active_method == "llm":
        import dspy

        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
            structured_one_call,
        )

        dspy.configure(
            lm=structured_one_call.build_dspy_lm(
                runtime.model,
                temperature=runtime.temperature,
                max_tokens=runtime.max_tokens,
                cache=False,
                api_base=runtime.base_url,
                api_key=runtime.api_key,
                timeout=int(runtime.timeout_seconds),
            )
        )
        program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
        format_retry_program = (
            structured_one_call.FormatOnlyJsonRetry()
            if runtime.model.startswith("ollama_chat/")
            else None
        )
        runner = Exectv2PipelineRunner(
            Exectv2PipelineConfiguration(
                method=method,
                model=runtime.model,
                temperature=runtime.temperature,
                max_tokens=runtime.max_tokens,
                mode="live",
                api_base=runtime.base_url,
                api_key=runtime.api_key,
                timeout=int(runtime.timeout_seconds),
                route=runtime.base_url,
                dspy_cache=False,
                program=program,
                format_retry_program=format_retry_program,
                split="operational",
            )
        )
        llm_output: list[dict[str, Any]] = []
        for note in notes:
            result = runner.run(ExectLetter(note.note_id, note.text)).result
            row = dict(result.row)
            llm_failed = _llm_row_has_blocking_failure(row)
            llm_output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "error" if llm_failed else "ok",
                    "model": runtime.model,
                    "pipeline": "llm",
                    "method": "llm",
                    "run_id": "llm",
                    "prediction": {
                        "mentions": [
                            mention.model_dump(mode="json")
                            for mention in result.prediction.mentions
                        ]
                    },
                    "scored_view": "raw_candidate",
                    "prompt_version": row.get("prompt_version", ""),
                    "prompt_profile": row.get("prompt_profile", ""),
                    "route": row.get("route", runtime.base_url),
                    "raw_output": row.get("raw_output", ""),
                    "initial_parse_errors": row.get("initial_parse_errors", []),
                    "parse_errors": row.get("parse_errors", []),
                    "format_retry_output": row.get("format_retry_output", ""),
                    "format_retry_notes": row.get("format_retry_notes", []),
                    **(
                        {
                            "error": {
                                "type": "model_or_parse_failure",
                                "message": row.get("call_error")
                                or "; ".join(
                                    str(error) for error in row.get("parse_errors", [])
                                )
                                or "; ".join(
                                    str(error)
                                    for error in row.get("initial_parse_errors", [])
                                ),
                            }
                        }
                        if llm_failed
                        else {}
                    ),
                    "trace": [event.to_dict() for event in result.stage_events],
                }
            )
        return llm_output

    import dspy

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    dspy.configure(
        lm=structured_one_call.build_dspy_lm(
            runtime.model,
            temperature=runtime.temperature,
            max_tokens=runtime.max_tokens,
            cache=False,
            api_base=runtime.base_url,
            api_key=runtime.api_key,
            timeout=int(runtime.timeout_seconds),
        )
    )
    program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
    format_retry_program = (
        structured_one_call.FormatOnlyJsonRetry()
        if runtime.model.startswith("ollama_chat/")
        else None
    )
    runner = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(
            method=method,
            model=runtime.model,
            temperature=runtime.temperature,
            max_tokens=runtime.max_tokens,
            mode="live",
            api_base=runtime.base_url,
            api_key=runtime.api_key,
            timeout=int(runtime.timeout_seconds),
            route=runtime.base_url,
            dspy_cache=False,
            program=program,
            format_retry_program=format_retry_program,
            split="operational",
        )
    )
    output: list[dict[str, Any]] = []
    for note in notes:
        letter = ExectLetter(note.note_id, note.text)
        try:
            result = runner.run(letter).result
        except Exception as exc:
            output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "error",
                    "model": runtime.api_model,
                    "pipeline": "llm_with_rules",
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                }
            )
            continue
        row = dict(result.row)
        if _llm_row_has_blocking_failure(row):
            output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "error",
                    "model": runtime.api_model,
                    "pipeline": "llm_with_rules",
                    "method": "llm_with_rules",
                    "run_id": "llm_with_rules",
                    "error": {
                        "type": "model_or_parse_failure",
                        "message": row.get("call_error")
                        or "; ".join(str(error) for error in row.get("parse_errors", [])),
                    },
                    "trace": [event.to_dict() for event in result.stage_events],
                }
            )
            continue
        output.append(
            {
                "id": note.note_id,
                "task": "exect",
                "status": "ok",
                "model": runtime.api_model,
                "pipeline": "llm_with_rules",
                "method": "llm_with_rules",
                "run_id": "llm_with_rules",
                "scored_view": "clinical_headline",
                "prompt_version": row.get("prompt_version", ""),
                "prompt_profile": row.get("prompt_profile", ""),
                "route": row.get("route", runtime.base_url),
                "raw_output": row.get("raw_output", ""),
                "prediction": {"mentions": row.get("predicted_mentions", [])},
                "lanes": row.get("lanes", {}),
                "trace": [event.to_dict() for event in result.stage_events],
            }
        )
    return output


def _assemble(
    letters: Sequence[ExectLetter], structured_rows: Sequence[Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Compatibility name for the shared selected assembly function."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        letter_assembly,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    return letter_assembly.assemble_structured_rows(
        letters,
        structured_rows,
        config=StructuredMethodConfig.selected(),
    )


def _blocking_parse_error(errors: Sequence[Any]) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in errors
    )


def _llm_row_has_blocking_failure(row: Mapping[str, Any]) -> bool:
    """Apply the final-output parse policy while allowing an accepted retry."""

    if row.get("call_error") or _blocking_parse_error(row.get("parse_errors", [])):
        return True
    return bool(
        row.get("initial_parse_errors")
        and not row.get("format_retry_output")
        and _blocking_parse_error(row.get("initial_parse_errors", []))
    )
