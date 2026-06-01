"""General CLI harness for Gan 2026 LLM-backed pipelines.

This module is intentionally pipeline-agnostic: direct extractors, structured
extractors, DSPy programs, and future hybrid LLM pipelines should bind into this
runner by providing a small callback spec. Pipeline modules own extraction and
report formatting; this module owns shared CLI concerns such as split loading,
raw-output reuse, DSPy cache control, progress cadence, and checkpoint paths.
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
        reuse_raw_outputs: Mapping[int, str],
        reuse_source: str | None,
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
    load_reusable_raw_outputs: Callable[[Path], dict[int, str]]
    default_model: str = "openai/gpt-4.1-mini"
    default_max_tokens: int = 900


def run_cli(spec: GanLlmPipelineCliSpec, argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=spec.description)
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
        "--reuse-jsonl",
        type=Path,
        action="append",
        default=[],
        help="Reuse raw model outputs from an existing JSONL artifact by source_row_index.",
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

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    reuse_raw_outputs: dict[int, str] = {}
    for reuse_jsonl in args.reuse_jsonl:
        reuse_raw_outputs.update(spec.load_reusable_raw_outputs(reuse_jsonl))
    reuse_source = ", ".join(str(path) for path in args.reuse_jsonl) or None
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
        reuse_raw_outputs=reuse_raw_outputs,
        reuse_source=reuse_source,
        escalation_reason=args.escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
    )
    spec.write_jsonl(rows, args.jsonl)
    spec.write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


# Backward-compatible alias for the first pipeline bindings that imported the
# old name while the shared runner was being split out.
LlmPipelineCliSpec = GanLlmPipelineCliSpec
