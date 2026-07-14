"""CLI specs for the retained Gan architecture matrix and efficiency ceiling."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def get_cli_specs() -> dict[str, Any]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
        fresh_evidence_reasoner,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
        GanLlmPipelineCliSpec,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        write_jsonl_rows,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events,
        llm_only_canonical_pipeline,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
        write_deterministic_report,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

    def write_jsonl(rows, path):
        write_jsonl_rows(rows, path)

    return {
        "deterministic_canonical_pipeline": GanLlmPipelineCliSpec(
            description="Run the retained Gan deterministic rules pipeline.",
            default_jsonl_path=Path(
                "experiments/gan2026_deterministic_canonical_pipeline_validation.jsonl"
            ),
            default_report_path=Path(
                "experiments/gan2026_deterministic_canonical_pipeline_validation.md"
            ),
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="deterministic_canonical_pipeline",
                **kwargs,
            ),
            write_jsonl=write_jsonl,
            write_report=write_deterministic_report,
            default_max_tokens=900,
        ),
        "llm_only_canonical_pipeline": GanLlmPipelineCliSpec(
            description="Run the retained single-call LLM-only pipeline.",
            default_jsonl_path=llm_only_canonical_pipeline.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_canonical_pipeline.DEFAULT_REPORT_PATH,
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="llm_only_canonical_pipeline",
                **kwargs,
            ),
            write_jsonl=llm_only_canonical_pipeline.write_jsonl,
            write_report=llm_only_canonical_pipeline.write_report,
            summarize_rows=llm_only_canonical_pipeline.summarize_records,
            default_max_tokens=1200,
        ),
        "hybrid_structured_events": GanLlmPipelineCliSpec(
            description="Run the retained single-call structured-event hybrid.",
            default_jsonl_path=hybrid_structured_events.DEFAULT_JSONL_PATH,
            default_report_path=hybrid_structured_events.DEFAULT_REPORT_PATH,
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="hybrid_structured_events",
                **kwargs,
            ),
            write_jsonl=hybrid_structured_events.write_jsonl,
            write_report=hybrid_structured_events.write_report,
            summarize_rows=hybrid_structured_events.summarize_records,
            default_max_tokens=5000,
        ),
        "fresh_evidence_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the retained V12 fresh-evidence efficiency ceiling over saved GPT, Qwen, "
                "and DeepSeek structured-event traces."
            ),
            default_jsonl_path=fresh_evidence_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=fresh_evidence_reasoner.DEFAULT_REPORT_PATH,
            run_split=fresh_evidence_reasoner.run_split,
            write_jsonl=fresh_evidence_reasoner.write_jsonl,
            write_report=fresh_evidence_reasoner.write_report,
            summarize_rows=fresh_evidence_reasoner.summarize_rows,
            default_max_tokens=2800,
            default_structured_event_jsonl_path=(
                fresh_evidence_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
    }
