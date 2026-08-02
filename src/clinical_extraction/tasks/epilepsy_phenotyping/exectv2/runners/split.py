"""No-call split runner for the ExECT rules method."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
    Exectv2PipelineConfiguration,
    Exectv2PipelineRunner,
)

from .naming import active_method_name


def run_split(
    letters: Sequence[ExectLetter],
    *,
    method: str = "rules",
    split: str,
    model: str = "(model-independent)",
    temperature: float = 0.0,
    max_tokens: int = 0,
    mode: str = "no-call",
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    **_: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run deterministic ExECT rules over supplied letters without model I/O.

    The extra run/checkpoint arguments keep the split boundary compatible with
    the model-led runners. They are intentionally inert for this no-call path.
    """

    del temperature, max_tokens, checkpoint_jsonl_path, checkpoint_report_path, resume
    if active_method_name(method) != "rules":
        raise ValueError("the ExECT rules split runner accepts only the rules method")

    runner = Exectv2PipelineRunner(Exectv2PipelineConfiguration(method=method))
    rows: list[dict[str, Any]] = []
    for letter in letters:
        result = runner.run(letter).result
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": "rules",
                "method_id": "rules",
                "saved_run_id": "exectv2_deterministic_all9_dev140",
                "retained_evidence_id": "exectv2_deterministic_all9_dev_20260714",
                "model": "(model-independent)",
                "mode": "no-call",
                "prompt_version": "n/a (deterministic rules)",
                "raw_output": "",
                "call_error": None,
                "parse_errors": [],
                "predicted_mentions": [
                    mention.model_dump(mode="json") for mention in result.prediction.mentions
                ],
                "comparison_projection": [
                    mention.model_dump(mode="json")
                    for mention in result.comparison_projection.mentions
                ],
                "diagnostics": dict(result.prediction.diagnostics),
                "stage_events": [event.to_dict() for event in result.stage_events],
            }
        )

    metadata = {
        "method_id": "rules",
        "pipeline_family": "rules",
        "retained_method_id": "exectv2_rules_only",
        "saved_run_id": "exectv2_deterministic_all9_dev140",
        "retained_evidence_id": "exectv2_deterministic_all9_dev_20260714",
        "split": split,
        "model": "(model-independent)",
        "mode": "no-call",
        "prompt_version": "n/a (deterministic rules)",
        "row_count": len(rows),
        "call_failures": 0,
        "parse_failures": 0,
    }
    return rows, metadata
