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
                    "saved_run_id": "exectv2_deterministic_all9_dev140",
                    "retained_evidence_id": "exectv2_deterministic_all9_dev_20260714",
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
        raise ValueError("ExECT llm-only migration is not part of the rules vertical slice")

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured import (  # noqa: E501
        runner as structured_runner,
    )

    letters = [ExectLetter(note.note_id, note.text) for note in notes]
    rows, _ = structured_runner.run_split(
        letters,
        split="operational",
        model=runtime.model,
        temperature=runtime.temperature,
        max_tokens=runtime.max_tokens,
        mode="live",
        dspy_cache=False,
        api_base=runtime.base_url,
        api_key=runtime.api_key,
        timeout=int(runtime.timeout_seconds),
        prompt_profile="full",
    )
    failed = {
        str(row["letter_id"]): row
        for row in rows
        if row.get("call_error") or _blocking_parse_error(row.get("parse_errors", []))
    }
    usable_letters = [letter for letter in letters if letter.letter_id not in failed]
    usable_rows = [row for row in rows if str(row["letter_id"]) not in failed]
    assembled_by_id: dict[str, dict[str, Any]] = {}
    if usable_rows:
        assembled_by_id = _assemble(usable_letters, usable_rows)

    output: list[dict[str, Any]] = []
    for note in notes:
        if note.note_id in failed:
            row = failed[note.note_id]
            output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "error",
                    "model": runtime.api_model,
                    "pipeline": "llm_with_rules_one_call",
                    "error": {
                        "type": "model_or_parse_failure",
                        "message": row.get("call_error")
                        or "; ".join(row.get("parse_errors", [])),
                    },
                }
            )
            continue
        assembled = assembled_by_id[note.note_id]
        output.append(
            {
                "id": note.note_id,
                "task": "exect",
                "status": "ok",
                "model": runtime.api_model,
                "pipeline": "llm_with_rules_one_call",
                "prompt_version": usable_rows[0].get("prompt_version", ""),
                "prediction": {"mentions": assembled["predicted_mentions"]},
                "lanes": assembled["lanes"],
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
