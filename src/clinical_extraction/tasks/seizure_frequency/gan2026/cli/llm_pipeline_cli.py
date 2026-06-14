"""General CLI harness for Gan 2026 LLM-backed pipelines.

This module is the single CLI surface for routine Gan 2026 LLM-backed
experiments. Pipeline modules own extraction and report formatting; this module
owns split loading, model/cache flags, progress cadence, checkpoint paths, and
the pipeline registry.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Protocol

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
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
        api_base: str | None,
        escalation_reason: str | None,
        progress_every: int | None,
        checkpoint_jsonl_path: Path | None,
        checkpoint_report_path: Path | None,
        candidate_set_jsonl_path: Path | None = None,
        structured_event_jsonl_path: Path | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]: ...


class PipelineReportWriter(Protocol):
    def __call__(
        self,
        rows: Sequence[Mapping[str, Any]],
        metadata: Mapping[str, Any],
        path: Path,
        /,
        *,
        jsonl_path: Path,
    ) -> None: ...


class PipelineSummarizer(Protocol):
    def __call__(self, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class GanLlmPipelineCliSpec:
    """Callbacks and defaults needed to expose a Gan LLM pipeline on the CLI."""

    description: str
    default_jsonl_path: Path
    default_report_path: Path
    run_split: PipelineRunFn
    write_jsonl: Callable[[Sequence[Mapping[str, Any]], Path], None]
    write_report: PipelineReportWriter
    summarize_rows: PipelineSummarizer | None = None
    default_model: str = "openai/gpt-4.1-mini"
    default_max_tokens: int = 900
    default_candidate_set_jsonl_path: Path | None = None
    default_structured_event_jsonl_path: Path | None = None


@dataclass(frozen=True)
class FrozenTestLaunchSpec:
    """Exact launch tuple for a frozen locked-test audit."""

    model: str
    max_tokens: int
    jsonl_path: Path
    report_path: Path


FROZEN_TEST_PIPELINE_LAUNCH_SPECS: Mapping[str, FrozenTestLaunchSpec] = {
    "fresh_evidence_reasoner": FrozenTestLaunchSpec(
        model="openai/gpt-4.1",
        max_tokens=2800,
        jsonl_path=Path(
            "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl"
        ),
        report_path=Path(
            "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md"
        ),
    ),
}


def pipeline_specs() -> dict[str, GanLlmPipelineCliSpec]:
    """Return routine LLM experiment pipelines exposed by the single CLI."""
    from clinical_extraction.tasks.seizure_frequency.gan2026 import runner

    return runner.get_cli_specs()


def run_cli(argv: Sequence[str] | None = None) -> None:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    specs = pipeline_specs()
    pipeline_parser = argparse.ArgumentParser(add_help=False)
    pipeline_parser.add_argument("--pipeline", choices=sorted(specs), required=True)
    pipeline_args, _ = pipeline_parser.parse_known_args(raw_argv)
    spec = specs[pipeline_args.pipeline]

    parser = argparse.ArgumentParser(description=spec.description, parents=[pipeline_parser])
    parser.add_argument("--split", choices=("train", "validation", "test"), default="validation")
    parser.add_argument("--jsonl", type=Path, default=spec.default_jsonl_path)
    parser.add_argument("--markdown", type=Path, default=spec.default_report_path)
    parser.add_argument("--model", default=spec.default_model)
    parser.add_argument(
        "--api-base",
        default=None,
        help=(
            "Optional OpenAI-compatible API base URL for local providers such as Ollama; "
            "recorded in run metadata."
        ),
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=spec.default_max_tokens)
    if spec.default_candidate_set_jsonl_path is not None:
        parser.add_argument(
            "--candidate-set-jsonl",
            type=Path,
            default=spec.default_candidate_set_jsonl_path,
            help="CandidateSet JSONL artifact to use for CandidateSet-backed probes.",
        )
    if spec.default_structured_event_jsonl_path is not None:
        parser.add_argument(
            "--structured-event-jsonl",
            type=Path,
            default=spec.default_structured_event_jsonl_path,
            help="Saved structured-event JSONL artifact to use as the V0 input substrate.",
        )
    if pipeline_args.pipeline == "agentic_matched_budget":
        parser.add_argument(
            "--conditions",
            default=None,
            help=(
                "Comma-separated agentic conditions to run. Defaults to all "
                "predeclared matched-budget conditions."
            ),
        )
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--source-row-indices",
        default=None,
        help=(
            "Comma-separated source_row_index values to run, in the requested order. "
            "Use for fixed validation hard slices."
        ),
    )
    parser.add_argument(
        "--source-row-index-file",
        type=Path,
        default=None,
        help=(
            "Text file containing source_row_index values, one per line or comma-separated. "
            "Lines starting with # are ignored."
        ),
    )
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
        "--confirm-test-audit",
        action="store_true",
        help=(
            "Required with --split test to confirm this is an explicitly authorized "
            "frozen aggregate holdout audit. Test runs must cover the full split."
        ),
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Emit progress and checkpoint artifacts every N processed rows. Use 0 to disable.",
    )
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help=(
            "Resume from the target JSONL by skipping existing source_row_index rows. "
            "Progress checkpoints are written to .resume-part files so the existing "
            "artifact is not overwritten until the combined run succeeds."
        ),
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help=(
            "Allow replacing existing JSONL/Markdown output artifacts. Without this "
            "or --resume-existing, the CLI refuses to write over existing outputs."
        ),
    )
    args = parser.parse_args(raw_argv)
    spec = specs[args.pipeline]
    requested_source_indices = _parse_requested_source_indices(args, parser)

    records = load_records_for_split(args.split)
    if requested_source_indices is not None:
        records = _filter_records_by_source_indices(
            records,
            requested_source_indices=requested_source_indices,
            parser=parser,
        )
    if args.limit is not None:
        records = records[: args.limit]
    # Frozen-path / audit / ladder policy violations are reported before the
    # generic output-overwrite guard: using the wrong artifact path is a more
    # fundamental error than the correct path already existing.
    _validate_test_audit_policy(
        args,
        parser,
        row_count=len(records),
        explicit_source_override_options=_explicit_source_override_options(raw_argv),
    )
    _validate_validation_ladder(args, parser, row_count=len(records))
    _validate_output_overwrite_policy(args, parser)

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    progress_every = args.progress_every if args.progress_every > 0 else None

    run_started_at = datetime.now(UTC)
    run_started_monotonic = time.perf_counter()
    existing_rows: list[dict[str, Any]] = []
    records_to_run = records
    resume_checkpoint_jsonl_path = args.jsonl
    resume_checkpoint_report_path = args.markdown
    if args.resume_existing:
        if args.jsonl.exists():
            existing_rows = load_jsonl_rows(args.jsonl)
        completed_indices = _source_indices_from_rows(existing_rows)
        records_to_run = [
            record
            for record in records
            if _source_index_from_record(record, parser) not in completed_indices
        ]
        resume_checkpoint_jsonl_path = _resume_part_path(args.jsonl)
        resume_checkpoint_report_path = _resume_part_path(args.markdown)

    run_kwargs: dict[str, Any] = {
        "split": args.split,
        "split_manifest": split_manifest,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "mode": args.mode,
        "dspy_cache": not args.disable_dspy_cache,
        "api_base": args.api_base,
        "escalation_reason": args.escalation_reason,
        "progress_every": progress_every,
        "checkpoint_jsonl_path": resume_checkpoint_jsonl_path,
        "checkpoint_report_path": resume_checkpoint_report_path,
    }
    if spec.default_candidate_set_jsonl_path is not None:
        run_kwargs["candidate_set_jsonl_path"] = args.candidate_set_jsonl
    if spec.default_structured_event_jsonl_path is not None:
        run_kwargs["structured_event_jsonl_path"] = args.structured_event_jsonl
    if pipeline_args.pipeline == "agentic_matched_budget" and args.conditions:
        run_kwargs["conditions"] = _parse_agentic_conditions(args.conditions, parser)
    rows, metadata = (
        spec.run_split(records_to_run, **run_kwargs)
        if records_to_run
        else ([], {"summary": {}})
    )
    if args.resume_existing:
        rows = _combine_resume_rows(
            existing_rows,
            rows,
            requested_records=records,
            parser=parser,
        )
        metadata["resume"] = {
            "enabled": True,
            "existing_rows": len(existing_rows),
            "completed_rows_skipped": len(existing_rows),
            "rows_run": len(records_to_run),
            "combined_rows": len(rows),
            "resume_checkpoint_jsonl_path": str(resume_checkpoint_jsonl_path),
            "resume_checkpoint_report_path": str(resume_checkpoint_report_path),
        }
        if spec.summarize_rows is not None:
            metadata["summary"] = _summarize_rows_for_split(
                spec.summarize_rows,
                rows,
                split=args.split,
            )
    _attach_run_timing(
        metadata,
        started_at=run_started_at,
        elapsed_seconds=time.perf_counter() - run_started_monotonic,
        row_count=len(rows),
    )
    spec.write_jsonl(rows, args.jsonl)
    spec.write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


def _parse_agentic_conditions(
    value: str,
    parser: argparse.ArgumentParser,
) -> list[str]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
        DEFAULT_CONDITIONS,
    )

    conditions = [condition.strip() for condition in value.split(",") if condition.strip()]
    invalid = [condition for condition in conditions if condition not in DEFAULT_CONDITIONS]
    if invalid:
        parser.error(
            "unknown --conditions value(s): "
            + ", ".join(invalid)
            + "; valid values are: "
            + ", ".join(DEFAULT_CONDITIONS)
        )
    if not conditions:
        parser.error("--conditions must include at least one condition")
    return conditions


def _parse_requested_source_indices(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> list[int] | None:
    values: list[str] = []
    if args.source_row_indices:
        values.extend(_split_source_index_text(str(args.source_row_indices)))
    if args.source_row_index_file:
        if not args.source_row_index_file.exists():
            parser.error(f"--source-row-index-file does not exist: {args.source_row_index_file}")
        lines = args.source_row_index_file.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            values.extend(_split_source_index_text(stripped))
    if not values:
        return None
    indices: list[int] = []
    invalid: list[str] = []
    for value in values:
        try:
            indices.append(int(value))
        except ValueError:
            invalid.append(value)
    if invalid:
        parser.error("invalid source_row_index value(s): " + ", ".join(invalid[:10]))
    duplicates = _duplicates(indices)
    if duplicates:
        parser.error(
            "duplicate source_row_index value(s): "
            + ", ".join(str(index) for index in duplicates[:10])
        )
    return indices


def _split_source_index_text(value: str) -> list[str]:
    return [part.strip() for part in value.replace(",", "\n").splitlines() if part.strip()]


def _filter_records_by_source_indices(
    records: Sequence[GanFrequencyRecord],
    *,
    requested_source_indices: Sequence[int],
    parser: argparse.ArgumentParser,
) -> list[GanFrequencyRecord]:
    records_by_index = {
        _source_index_from_record(record, parser): record for record in records
    }
    missing = [index for index in requested_source_indices if index not in records_by_index]
    if missing:
        parser.error(
            "requested source_row_index value(s) are not present in the selected split: "
            + ", ".join(str(index) for index in missing[:10])
        )
    return [records_by_index[index] for index in requested_source_indices]


def _duplicates(values: Sequence[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _validate_validation_ladder(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    *,
    row_count: int,
) -> None:
    if args.split != "validation" or args.escalation_reason:
        return
    if row_count > 250:
        parser.error(
            "validation runs above 250 rows require --escalation-reason; "
            "use --limit 25, --limit 50, or --limit 250 for routine ladder runs"
        )


def _summarize_rows_for_split(
    summarize_rows: PipelineSummarizer,
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
) -> dict[str, Any]:
    signature = inspect.signature(summarize_rows)
    parameters = signature.parameters
    accepts_split = "split" in parameters or any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    if accepts_split:
        return summarize_rows(rows, split=split)  # type: ignore[call-arg]
    return summarize_rows(rows)


def _validate_test_audit_policy(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    *,
    row_count: int,
    explicit_source_override_options: Sequence[str] = (),
) -> None:
    if args.split != "test":
        if args.confirm_test_audit:
            parser.error("--confirm-test-audit may only be used with --split test")
        return
    if not args.confirm_test_audit:
        parser.error(
            "test split runs require --confirm-test-audit after explicit "
            "frozen-protocol authorization"
        )
    if not args.escalation_reason:
        parser.error("test split runs require --escalation-reason naming the frozen audit")
    if args.limit is not None:
        parser.error("test split runs must cover the full locked split; do not use --limit")
    if args.source_row_indices or args.source_row_index_file:
        parser.error(
            "test split runs must not use --source-row-indices or --source-row-index-file"
        )
    if explicit_source_override_options:
        parser.error(
            "test split runs must not use source-artifact override option(s): "
            + ", ".join(explicit_source_override_options)
            + "; use the frozen pipeline defaults"
        )
    if args.overwrite_existing:
        parser.error(
            "test split runs must not use --overwrite-existing; use --resume-existing "
            "only for documented technical recovery"
        )
    if args.resume_existing:
        if not args.jsonl.exists():
            parser.error(
                "test split --resume-existing requires an existing JSONL artifact "
                "for documented technical recovery"
            )
        if "technical recovery" not in args.escalation_reason.lower():
            parser.error(
                "test split --resume-existing requires --escalation-reason to "
                "describe technical recovery"
            )
    if args.progress_every != 0:
        parser.error("test split runs must use --progress-every 0")
    if args.mode != "live":
        parser.error("test split runs must use --mode live")
    if args.temperature != 0.0:
        parser.error("test split runs must use --temperature 0.0")
    if args.api_base is not None:
        parser.error("test split runs must not use --api-base")
    if args.disable_dspy_cache:
        parser.error("test split runs must not use --disable-dspy-cache")
    frozen_launch_spec = FROZEN_TEST_PIPELINE_LAUNCH_SPECS.get(args.pipeline)
    if frozen_launch_spec is not None:
        if args.model != frozen_launch_spec.model:
            parser.error(
                f"{args.pipeline} test split runs must use --model "
                f"{frozen_launch_spec.model}"
            )
        if args.max_tokens != frozen_launch_spec.max_tokens:
            parser.error(
                f"{args.pipeline} test split runs must use --max-tokens "
                f"{frozen_launch_spec.max_tokens}"
            )
        if not _same_cli_path(args.jsonl, frozen_launch_spec.jsonl_path):
            parser.error(
                f"{args.pipeline} test split runs must use --jsonl "
                f"{frozen_launch_spec.jsonl_path}"
            )
        if not _same_cli_path(args.markdown, frozen_launch_spec.report_path):
            parser.error(
                f"{args.pipeline} test split runs must use --markdown "
                f"{frozen_launch_spec.report_path}"
            )
    if row_count == 0:
        parser.error("test split run selected zero rows")


def _same_cli_path(path: Path, expected_path: Path) -> bool:
    return path.resolve(strict=False) == expected_path.resolve(strict=False)


def _explicit_source_override_options(argv: Sequence[str]) -> tuple[str, ...]:
    source_options = ("--candidate-set-jsonl", "--structured-event-jsonl")
    return tuple(
        option
        for option in source_options
        if any(arg == option or arg.startswith(f"{option}=") for arg in argv)
    )


def _validate_output_overwrite_policy(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> None:
    if args.resume_existing and args.overwrite_existing:
        parser.error("use either --resume-existing or --overwrite-existing, not both")
    if args.resume_existing or args.overwrite_existing:
        return
    existing_paths = [
        path for path in (args.jsonl, args.markdown) if Path(path).exists()
    ]
    if existing_paths:
        parser.error(
            "output artifact already exists; use --resume-existing to continue "
            "or --overwrite-existing to replace: "
            + ", ".join(str(path) for path in existing_paths)
        )


def _attach_run_timing(
    metadata: dict[str, Any],
    *,
    started_at: datetime,
    elapsed_seconds: float,
    row_count: int,
) -> None:
    """Attach wall-clock timing captured by the shared CLI harness."""

    finished_at = datetime.now(UTC)
    elapsed = round(elapsed_seconds, 3)
    metadata["run_started_at_utc"] = started_at.isoformat()
    metadata["run_finished_at_utc"] = finished_at.isoformat()
    metadata["elapsed_seconds"] = elapsed
    metadata["elapsed_minutes"] = round(elapsed / 60, 3)
    metadata["rows_per_second"] = round(row_count / elapsed_seconds, 6) if elapsed_seconds else None
    metadata["seconds_per_row"] = round(elapsed_seconds / row_count, 3) if row_count else None


def _source_index_from_record(record: GanFrequencyRecord, parser: argparse.ArgumentParser) -> int:
    source_row_index = getattr(record, "source_row_index", None)
    if source_row_index is None:
        parser.error("--resume-existing requires records with source_row_index")
    return int(source_row_index)


def _source_indices_from_rows(rows: Sequence[Mapping[str, Any]]) -> set[int]:
    indices: set[int] = set()
    for row in rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is not None:
            indices.add(int(source_row_index))
    return indices


def _resume_part_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.resume-part{path.suffix}")


def _combine_resume_rows(
    existing_rows: Sequence[Mapping[str, Any]],
    new_rows: Sequence[Mapping[str, Any]],
    *,
    requested_records: Sequence[GanFrequencyRecord],
    parser: argparse.ArgumentParser,
) -> list[dict[str, Any]]:
    rows_by_index: dict[int, dict[str, Any]] = {}
    duplicate_indices: list[int] = []
    for row in [*existing_rows, *new_rows]:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        index = int(source_row_index)
        if index in rows_by_index:
            duplicate_indices.append(index)
        rows_by_index[index] = dict(row)
    if duplicate_indices:
        parser.error(
            "--resume-existing found duplicate source_row_index rows: "
            + ", ".join(str(index) for index in duplicate_indices[:10])
        )
    requested_indices = [
        _source_index_from_record(record, parser) for record in requested_records
    ]
    missing_indices = [index for index in requested_indices if index not in rows_by_index]
    if missing_indices:
        parser.error(
            "--resume-existing did not produce all requested rows; missing: "
            + ", ".join(str(index) for index in missing_indices[:10])
        )
    return [rows_by_index[index] for index in requested_indices]


def main(argv: Sequence[str] | None = None) -> None:
    run_cli(argv)


if __name__ == "__main__":
    main()
