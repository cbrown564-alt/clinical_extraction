"""General CLI harness for Gan 2026 LLM-backed pipelines.

This module is the single CLI surface for routine Gan 2026 LLM-backed
experiments. Pipeline modules own extraction and report formatting; this module
owns split loading, model/cache flags, progress cadence, checkpoint paths, and
the pipeline registry.
"""

from __future__ import annotations

import argparse
import json
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


def pipeline_specs() -> dict[str, GanLlmPipelineCliSpec]:
    """Return routine LLM experiment pipelines exposed by the single CLI."""


    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_candidate_set_clinical_assessment_probe,
        llm_candidate_set_selector_schema_probe,
        llm_extracted_candidate_schema_probe,
        llm_heavy_clinical_frequency_reasoner,
        llm_heavy_evidence_selection_with_deterministic_adapters,
        llm_only_direct_labeler,
        llm_only_structured_events,
    )



    return {
        "llm_only_direct_labeler": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only direct-labeler experiment.",
            default_jsonl_path=llm_only_direct_labeler.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_direct_labeler.DEFAULT_REPORT_PATH,
            run_split=llm_only_direct_labeler.run_split,
            write_jsonl=llm_only_direct_labeler.write_jsonl,
            write_report=llm_only_direct_labeler.write_report,
            summarize_rows=llm_only_direct_labeler.summarize_records,
        ),
        "llm_extracted_candidate_schema_probe": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 ExtractedCandidate kind-specific schema probe."
            ),
            default_jsonl_path=llm_extracted_candidate_schema_probe.DEFAULT_JSONL_PATH,
            default_report_path=llm_extracted_candidate_schema_probe.DEFAULT_REPORT_PATH,
            run_split=llm_extracted_candidate_schema_probe.run_split,
            write_jsonl=llm_extracted_candidate_schema_probe.write_jsonl,
            write_report=llm_extracted_candidate_schema_probe.write_report,
            summarize_rows=llm_extracted_candidate_schema_probe.summarize_records,
            default_max_tokens=5000,
        ),
        "llm_candidate_set_selector_schema_probe": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 CandidateSet selector-decision schema probe."
            ),
            default_jsonl_path=llm_candidate_set_selector_schema_probe.DEFAULT_JSONL_PATH,
            default_report_path=llm_candidate_set_selector_schema_probe.DEFAULT_REPORT_PATH,
            run_split=llm_candidate_set_selector_schema_probe.run_split,
            write_jsonl=llm_candidate_set_selector_schema_probe.write_jsonl,
            write_report=llm_candidate_set_selector_schema_probe.write_report,
            summarize_rows=llm_candidate_set_selector_schema_probe.summarize_records,
            default_max_tokens=1800,
        ),
        "llm_candidate_set_clinical_assessment_probe": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 CandidateSet merged clinical-assessment schema probe."
            ),
            default_jsonl_path=llm_candidate_set_clinical_assessment_probe.DEFAULT_JSONL_PATH,
            default_report_path=llm_candidate_set_clinical_assessment_probe.DEFAULT_REPORT_PATH,
            run_split=llm_candidate_set_clinical_assessment_probe.run_split,
            write_jsonl=llm_candidate_set_clinical_assessment_probe.write_jsonl,
            write_report=llm_candidate_set_clinical_assessment_probe.write_report,
            summarize_rows=llm_candidate_set_clinical_assessment_probe.summarize_records,
            default_max_tokens=2400,
            default_candidate_set_jsonl_path=(
                llm_candidate_set_clinical_assessment_probe.DEFAULT_CANDIDATE_SET_JSONL_PATH
            ),
        ),
        "llm_only_structured_events": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only structured-events experiment.",
            default_jsonl_path=llm_only_structured_events.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_structured_events.DEFAULT_REPORT_PATH,
            run_split=llm_only_structured_events.run_split,
            write_jsonl=llm_only_structured_events.write_jsonl,
            write_report=llm_only_structured_events.write_report,
            summarize_rows=llm_only_structured_events.summarize_records,
            default_max_tokens=5000,
        ),



        "llm_heavy_clinical_frequency_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 LLM-heavy clinical frequency reasoner schema smoke."
            ),
            default_jsonl_path=llm_heavy_clinical_frequency_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=llm_heavy_clinical_frequency_reasoner.DEFAULT_REPORT_PATH,
            run_split=llm_heavy_clinical_frequency_reasoner.run_split,
            write_jsonl=llm_heavy_clinical_frequency_reasoner.write_jsonl,
            write_report=llm_heavy_clinical_frequency_reasoner.write_report,
            summarize_rows=llm_heavy_clinical_frequency_reasoner.summarize_records,
            default_max_tokens=1800,
        ),
        "llm_heavy_evidence_selection_with_deterministic_adapters": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 Decision 0007 LLM-heavy selected-evidence and "
                "mechanical-adapter smoke."
            ),
            default_jsonl_path=(
                llm_heavy_evidence_selection_with_deterministic_adapters.DEFAULT_JSONL_PATH
            ),
            default_report_path=(
                llm_heavy_evidence_selection_with_deterministic_adapters.DEFAULT_REPORT_PATH
            ),
            run_split=llm_heavy_evidence_selection_with_deterministic_adapters.run_split,
            write_jsonl=llm_heavy_evidence_selection_with_deterministic_adapters.write_jsonl,
            write_report=llm_heavy_evidence_selection_with_deterministic_adapters.write_report,
            summarize_rows=(
                llm_heavy_evidence_selection_with_deterministic_adapters.summarize_records
            ),
            default_max_tokens=1800,
        ),

    }


def run_cli(argv: Sequence[str] | None = None) -> None:
    specs = pipeline_specs()
    pipeline_parser = argparse.ArgumentParser(add_help=False)
    pipeline_parser.add_argument("--pipeline", choices=sorted(specs), required=True)
    pipeline_args, _ = pipeline_parser.parse_known_args(argv)
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
    args = parser.parse_args(argv)
    spec = specs[args.pipeline]
    _validate_validation_ladder(args, parser)
    _validate_output_overwrite_policy(args, parser)

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]

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
            metadata["summary"] = spec.summarize_rows(rows)
    _attach_run_timing(
        metadata,
        started_at=run_started_at,
        elapsed_seconds=time.perf_counter() - run_started_monotonic,
        row_count=len(rows),
    )
    spec.write_jsonl(rows, args.jsonl)
    spec.write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


def _validate_validation_ladder(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> None:
    if args.split != "validation" or args.escalation_reason:
        return
    if args.limit is None or args.limit > 250:
        parser.error(
            "validation runs above 250 rows require --escalation-reason; "
            "use --limit 25, --limit 50, or --limit 250 for routine ladder runs"
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
