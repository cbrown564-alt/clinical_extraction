"""CLI binding for the Gan 2026 section-claim-table LLM pipeline."""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_pipeline_cli import (
    GanLlmPipelineCliSpec,
    run_cli,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.section_claim_table import (
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
                "Run the Gan 2026 section-and-claim-table LLM extraction experiment."
            ),
            default_jsonl_path=DEFAULT_JSONL_PATH,
            default_report_path=DEFAULT_REPORT_PATH,
            run_split=run_split,
            write_jsonl=write_jsonl,
            write_report=write_report,
            load_reusable_raw_outputs=load_reusable_raw_outputs,
            default_max_tokens=1400,
        ),
        argv,
    )


if __name__ == "__main__":
    main()
