"""General CLI harness for Gan 2026 LLM-backed pipelines.

This module is the single CLI surface for routine Gan 2026 LLM-backed
experiments. Pipeline modules own extraction and report formatting; this module
owns split loading, model/cache flags, progress cadence, checkpoint paths, and
the pipeline registry.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)


class PipelineRunFn(Protocol):
    def __call__(
        self,
        records: Sequence[GanFrequencyRecord],
        *,
        split: str,
        split_manifest: str,
        model: str,
        temperature: float,
        max_tokens: int,
        mode: Literal["live", "prompt-only"],
        dspy_cache: bool,
        escalation_reason: str | None,
        progress_every: int | None,
        checkpoint_jsonl_path: Path | None,
        checkpoint_report_path: Path | None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]: ...


class PipelineReportWriter(Protocol):
    def __call__(
        self,
        rows: Sequence[Mapping[str, Any]],
        metadata: Mapping[str, Any],
        path: Path,
        *,
        jsonl_path: Path,
    ) -> None: ...


@dataclass(frozen=True)
class GanLlmPipelineCliSpec:
    """Callbacks and defaults needed to expose a Gan LLM pipeline on the CLI."""

    description: str
    default_jsonl_path: Path
    default_report_path: Path
    run_split: PipelineRunFn
    write_jsonl: Callable[[Sequence[Mapping[str, Any]], Path], None]
    write_report: PipelineReportWriter
    default_model: str = "openai/gpt-4.1-mini"
    default_max_tokens: int = 900


def pipeline_specs() -> dict[str, GanLlmPipelineCliSpec]:
    """Return routine LLM experiment pipelines exposed by the single CLI."""

    from clinical_extraction.tasks.seizure_frequency.gan2026 import (
        dspy_modules,
        llm_first,
        llm_structured,
        section_claim_table,
    )

    return {
        "llm-first": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-first seizure-frequency extraction experiment.",
            default_jsonl_path=llm_first.DEFAULT_JSONL_PATH,
            default_report_path=llm_first.DEFAULT_REPORT_PATH,
            run_split=llm_first.run_split,
            write_jsonl=llm_first.write_jsonl,
            write_report=llm_first.write_report,
        ),
        "structured": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 structured LLM seizure-frequency extraction experiment.",
            default_jsonl_path=llm_structured.DEFAULT_JSONL_PATH,
            default_report_path=llm_structured.DEFAULT_REPORT_PATH,
            run_split=llm_structured.run_split,
            write_jsonl=llm_structured.write_jsonl,
            write_report=llm_structured.write_report,
        ),
        "section-claim-table": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 section-and-claim-table LLM extraction experiment.",
            default_jsonl_path=section_claim_table.DEFAULT_JSONL_PATH,
            default_report_path=section_claim_table.DEFAULT_REPORT_PATH,
            run_split=section_claim_table.run_split,
            write_jsonl=section_claim_table.write_jsonl,
            write_report=section_claim_table.write_report,
            default_max_tokens=1400,
        ),
        "architecture2": GanLlmPipelineCliSpec(
            description=(
                "Run Gan 2026 Architecture 2: deterministic candidate generator "
                "plus LLM adjudicator."
            ),
            default_jsonl_path=dspy_modules.DEFAULT_ARCH2_JSONL_PATH,
            default_report_path=dspy_modules.DEFAULT_ARCH2_REPORT_PATH,
            run_split=dspy_modules.run_architecture2_split,
            write_jsonl=dspy_modules.write_architecture2_jsonl,
            write_report=dspy_modules.write_architecture2_report,
            default_max_tokens=1100,
        ),
    }


def run_cli(argv: Sequence[str] | None = None) -> None:
    specs = pipeline_specs()
    pipeline_parser = argparse.ArgumentParser(add_help=False)
    pipeline_parser.add_argument("--pipeline", choices=sorted(specs), required=True)
    pipeline_args, _ = pipeline_parser.parse_known_args(argv)
    spec = specs[pipeline_args.pipeline]

    parser = argparse.ArgumentParser(description=spec.description, parents=[pipeline_parser])
    parser.add_argument("--split", choices=("train", "validation"), default="validation")
    parser.add_argument("--jsonl", type=Path, default=spec.default_jsonl_path)
    parser.add_argument("--markdown", type=Path, default=spec.default_report_path)
    parser.add_argument("--model", default=spec.default_model)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=spec.default_max_tokens)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--disable-dspy-cache",
        action="store_true",
        help="Disable DSPy/LiteLLM cache for new model calls.",
    )
    parser.add_argument(
        "--escalation-reason",
        default=None,
        help="Reason for a rare broader validation run; recorded in the report.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Emit progress and checkpoint artifacts every N processed rows. Use 0 to disable.",
    )
    args = parser.parse_args(argv)
    spec = specs[args.pipeline]

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    progress_every = args.progress_every if args.progress_every > 0 else None

    rows, metadata = spec.run_split(
        records,
        split=args.split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.disable_dspy_cache,
        escalation_reason=args.escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
    )
    spec.write_jsonl(rows, args.jsonl)
    spec.write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


def main(argv: Sequence[str] | None = None) -> None:
    run_cli(argv)


if __name__ == "__main__":
    main()
