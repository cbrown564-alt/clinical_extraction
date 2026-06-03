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

    from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
        hybrid_parallel_state_candidate_reasoner,
        hybrid_rules_candidates_llm_adjudicator,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_heavy_clinical_frequency_reasoner,
        llm_heavy_evidence_selection_with_deterministic_adapters,
        llm_only_claim_table_selector,
        llm_only_direct_labeler,
        llm_only_minimal_evidence_selector,
        llm_only_structured_events,
        llm_only_typed_adapter_reasoner,
        llm_only_typed_operations_reasoner,
    )

    llm_only_claim_table_selector_spec = GanLlmPipelineCliSpec(
        description="Run the Gan 2026 LLM-only claim-table selector experiment.",
        default_jsonl_path=llm_only_claim_table_selector.DEFAULT_JSONL_PATH,
        default_report_path=llm_only_claim_table_selector.DEFAULT_REPORT_PATH,
        run_split=llm_only_claim_table_selector.run_split,
        write_jsonl=llm_only_claim_table_selector.write_jsonl,
        write_report=llm_only_claim_table_selector.write_report,
        default_max_tokens=1400,
    )
    hybrid_rules_candidates_llm_adjudicator_spec = GanLlmPipelineCliSpec(
        description=("Run the Gan 2026 hybrid rules-candidates LLM-adjudicator experiment."),
        default_jsonl_path=(
            hybrid_rules_candidates_llm_adjudicator.DEFAULT_HYBRID_RULES_CANDIDATES_LLM_ADJUDICATOR_JSONL_PATH
        ),
        default_report_path=(
            hybrid_rules_candidates_llm_adjudicator.DEFAULT_HYBRID_RULES_CANDIDATES_LLM_ADJUDICATOR_REPORT_PATH
        ),
        run_split=(
            hybrid_rules_candidates_llm_adjudicator.run_hybrid_rules_candidates_llm_adjudicator_split
        ),
        write_jsonl=(
            hybrid_rules_candidates_llm_adjudicator.write_hybrid_rules_candidates_llm_adjudicator_jsonl
        ),
        write_report=(
            hybrid_rules_candidates_llm_adjudicator.write_hybrid_rules_candidates_llm_adjudicator_report
        ),
        default_max_tokens=1100,
    )

    return {
        "llm_only_direct_labeler": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only direct-labeler experiment.",
            default_jsonl_path=llm_only_direct_labeler.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_direct_labeler.DEFAULT_REPORT_PATH,
            run_split=llm_only_direct_labeler.run_split,
            write_jsonl=llm_only_direct_labeler.write_jsonl,
            write_report=llm_only_direct_labeler.write_report,
        ),
        "llm_only_structured_events": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only structured-events experiment.",
            default_jsonl_path=llm_only_structured_events.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_structured_events.DEFAULT_REPORT_PATH,
            run_split=llm_only_structured_events.run_split,
            write_jsonl=llm_only_structured_events.write_jsonl,
            write_report=llm_only_structured_events.write_report,
        ),
        "llm_only_claim_table_selector": llm_only_claim_table_selector_spec,
        "llm_only_minimal_evidence_selector": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only minimal evidence-selector experiment.",
            default_jsonl_path=llm_only_minimal_evidence_selector.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_minimal_evidence_selector.DEFAULT_REPORT_PATH,
            run_split=llm_only_minimal_evidence_selector.run_split,
            write_jsonl=llm_only_minimal_evidence_selector.write_jsonl,
            write_report=llm_only_minimal_evidence_selector.write_report,
            default_max_tokens=900,
        ),
        "hybrid_rules_candidates_llm_adjudicator": (hybrid_rules_candidates_llm_adjudicator_spec),
        "hybrid_parallel_state_candidate_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 hybrid parallel state/candidate reasoner smoke."
            ),
            default_jsonl_path=hybrid_parallel_state_candidate_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=hybrid_parallel_state_candidate_reasoner.DEFAULT_REPORT_PATH,
            run_split=hybrid_parallel_state_candidate_reasoner.run_split,
            write_jsonl=hybrid_parallel_state_candidate_reasoner.write_jsonl,
            write_report=hybrid_parallel_state_candidate_reasoner.write_report,
            default_max_tokens=1800,
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
            default_max_tokens=1800,
        ),
        "llm_only_typed_adapter_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 LLM-only typed DSPy JSONAdapter reasoner smoke."
            ),
            default_jsonl_path=llm_only_typed_adapter_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_typed_adapter_reasoner.DEFAULT_REPORT_PATH,
            run_split=llm_only_typed_adapter_reasoner.run_split,
            write_jsonl=llm_only_typed_adapter_reasoner.write_jsonl,
            write_report=llm_only_typed_adapter_reasoner.write_report,
            default_max_tokens=1800,
        ),
        "llm_only_typed_operations_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 LLM-only typed operations and graph overlay smoke."
            ),
            default_jsonl_path=llm_only_typed_operations_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_typed_operations_reasoner.DEFAULT_REPORT_PATH,
            run_split=llm_only_typed_operations_reasoner.run_split,
            write_jsonl=llm_only_typed_operations_reasoner.write_jsonl,
            write_report=llm_only_typed_operations_reasoner.write_report,
            default_max_tokens=2400,
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
    _validate_validation_ladder(args, parser)

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    progress_every = args.progress_every if args.progress_every > 0 else None

    run_started_at = datetime.now(UTC)
    run_started_monotonic = time.perf_counter()
    rows, metadata = spec.run_split(
        records,
        split=args.split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.disable_dspy_cache,
        api_base=args.api_base,
        escalation_reason=args.escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
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


def main(argv: Sequence[str] | None = None) -> None:
    run_cli(argv)


if __name__ == "__main__":
    main()
