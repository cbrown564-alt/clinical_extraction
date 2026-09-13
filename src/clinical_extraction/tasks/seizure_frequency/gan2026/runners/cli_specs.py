"""Command-line choices for the three retained Gan pipelines."""

from __future__ import annotations

from typing import Any


def get_cli_specs() -> dict[str, Any]:
    from clinical_extraction.core.jsonl import (
        write_jsonl_rows,
    )
    from clinical_extraction.operational.gan_benchmark import (
        GanLlmPipelineCliSpec,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm as llm_pipeline,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
        write_deterministic_report,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

    def write_jsonl(rows, path):
        write_jsonl_rows(rows, path)

    return {
        "rules": GanLlmPipelineCliSpec(
            description="Run the Gan rules-only pipeline.",
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="rules",
                **kwargs,
            ),
            write_jsonl=write_jsonl,
            write_report=write_deterministic_report,
            default_max_tokens=900,
        ),
        "llm": GanLlmPipelineCliSpec(
            description="Run the Gan LLM-only pipeline (one model call per letter).",
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="llm",
                **kwargs,
            ),
            write_jsonl=llm_pipeline.write_jsonl,
            write_report=llm_pipeline.write_report,
            summarize_rows=llm_pipeline.summarize_records,
            default_max_tokens=1200,
        ),
        "llm_with_rules": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan pipeline that extracts events with one model call, then "
                "normalizes and scores them with deterministic code."
            ),
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="llm_with_rules",
                **kwargs,
            ),
            write_jsonl=hybrid_structured_events.write_jsonl,
            write_report=hybrid_structured_events.write_report,
            summarize_rows=hybrid_structured_events.summarize_records,
            default_max_tokens=5000,
        ),
    }
