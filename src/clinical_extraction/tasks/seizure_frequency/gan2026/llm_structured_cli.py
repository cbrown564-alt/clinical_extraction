"""CLI binding for the Gan 2026 structured LLM extraction pipeline."""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_pipeline_cli import (
    GanLlmPipelineCliSpec,
    run_cli,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_structured import (
    DEFAULT_JSONL_PATH,
    DEFAULT_REPORT_PATH,
    load_reusable_raw_outputs,
    run_split,
    write_jsonl,
    write_report,
)


def main(argv: Sequence[str] | None = None) -> None:
    run_cli(
        GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 structured LLM seizure-frequency extraction experiment."
            ),
            default_jsonl_path=DEFAULT_JSONL_PATH,
            default_report_path=DEFAULT_REPORT_PATH,
            run_split=run_split,
            write_jsonl=write_jsonl,
            write_report=write_report,
            load_reusable_raw_outputs=load_reusable_raw_outputs,
        ),
        argv,
    )


if __name__ == "__main__":
    main()
