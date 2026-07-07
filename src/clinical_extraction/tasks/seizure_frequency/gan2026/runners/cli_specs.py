"""CLI pipeline spec registry for Gan 2026 unified runner surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def get_cli_specs() -> dict[str, Any]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
        cross_model_challenge_adjudicator,
        cross_model_structured_event_adjudicator,
        event_completion_reasoner,
        fresh_evidence_reasoner,
        llm_event_reasoner,
        represented_event_normalizer,
        structured_event_verifier,
        targeted_boundary_router,
        temporal_sentinel_specialist,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
        runner as agentic_runner,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
        GanLlmPipelineCliSpec,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        write_jsonl_rows,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events,
        llm_candidate_set_clinical_assessment_probe,
        llm_only_canonical_pipeline,
        llm_only_direct_labeler,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
        write_deterministic_report,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

    def write_jsonl(rows, path):
        write_jsonl_rows(rows, path)

    return {
        "agentic_matched_budget": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 agentic matched-budget prompt-only/no-call trace surface."
            ),
            default_jsonl_path=agentic_runner.DEFAULT_JSONL_PATH,
            default_report_path=agentic_runner.DEFAULT_REPORT_PATH,
            run_split=agentic_runner.run_split,
            write_jsonl=write_jsonl,
            write_report=agentic_runner.write_report,
            summarize_rows=agentic_runner.summarize_rows,
            default_max_tokens=900,
        ),
        "llm_event_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V1 LLM-owned structured-event reasoner over "
                "a saved pure structured-event V0 artifact."
            ),
            default_jsonl_path=llm_event_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=llm_event_reasoner.DEFAULT_REPORT_PATH,
            run_split=llm_event_reasoner.run_split,
            write_jsonl=llm_event_reasoner.write_jsonl,
            write_report=llm_event_reasoner.write_report,
            summarize_rows=llm_event_reasoner.summarize_rows,
            default_max_tokens=1600,
            default_structured_event_jsonl_path=(
                llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "structured_event_verifier": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V4 verifier-first structured-event correction "
                "pipeline over a saved pure structured-event V0 artifact."
            ),
            default_jsonl_path=structured_event_verifier.DEFAULT_JSONL_PATH,
            default_report_path=structured_event_verifier.DEFAULT_REPORT_PATH,
            run_split=structured_event_verifier.run_split,
            write_jsonl=structured_event_verifier.write_jsonl,
            write_report=structured_event_verifier.write_report,
            summarize_rows=structured_event_verifier.summarize_rows,
            default_max_tokens=1800,
            default_structured_event_jsonl_path=(
                structured_event_verifier.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "targeted_boundary_router": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V3 targeted boundary router over a saved pure "
                "structured-event V0 artifact."
            ),
            default_jsonl_path=targeted_boundary_router.DEFAULT_JSONL_PATH,
            default_report_path=targeted_boundary_router.DEFAULT_REPORT_PATH,
            run_split=targeted_boundary_router.run_split,
            write_jsonl=targeted_boundary_router.write_jsonl,
            write_report=targeted_boundary_router.write_report,
            summarize_rows=targeted_boundary_router.summarize_rows,
            default_max_tokens=2000,
            default_structured_event_jsonl_path=(
                targeted_boundary_router.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "event_completion_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V7 event-completion reasoner over a saved pure "
                "structured-event V0 artifact."
            ),
            default_jsonl_path=event_completion_reasoner.DEFAULT_JSONL_PATH,
            default_report_path=event_completion_reasoner.DEFAULT_REPORT_PATH,
            run_split=event_completion_reasoner.run_split,
            write_jsonl=event_completion_reasoner.write_jsonl,
            write_report=event_completion_reasoner.write_report,
            summarize_rows=event_completion_reasoner.summarize_rows,
            default_max_tokens=2200,
            default_structured_event_jsonl_path=(
                event_completion_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "represented_event_normalizer": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V8 represented-event normalizer over a saved "
                "pure structured-event V0 artifact."
            ),
            default_jsonl_path=represented_event_normalizer.DEFAULT_JSONL_PATH,
            default_report_path=represented_event_normalizer.DEFAULT_REPORT_PATH,
            run_split=represented_event_normalizer.run_split,
            write_jsonl=represented_event_normalizer.write_jsonl,
            write_report=represented_event_normalizer.write_report,
            summarize_rows=represented_event_normalizer.summarize_rows,
            default_max_tokens=2200,
            default_structured_event_jsonl_path=(
                represented_event_normalizer.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "temporal_sentinel_specialist": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V9 temporal/sentinel specialist over a saved "
                "pure structured-event V0 artifact."
            ),
            default_jsonl_path=temporal_sentinel_specialist.DEFAULT_JSONL_PATH,
            default_report_path=temporal_sentinel_specialist.DEFAULT_REPORT_PATH,
            run_split=temporal_sentinel_specialist.run_split,
            write_jsonl=temporal_sentinel_specialist.write_jsonl,
            write_report=temporal_sentinel_specialist.write_report,
            summarize_rows=temporal_sentinel_specialist.summarize_rows,
            default_max_tokens=2400,
            default_structured_event_jsonl_path=(
                temporal_sentinel_specialist.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "cross_model_structured_event_adjudicator": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V10 cross-model structured-event adjudicator "
                "over saved GPT, Qwen, and DeepSeek structured-event artifacts."
            ),
            default_jsonl_path=(cross_model_structured_event_adjudicator.DEFAULT_JSONL_PATH),
            default_report_path=(cross_model_structured_event_adjudicator.DEFAULT_REPORT_PATH),
            run_split=cross_model_structured_event_adjudicator.run_split,
            write_jsonl=cross_model_structured_event_adjudicator.write_jsonl,
            write_report=cross_model_structured_event_adjudicator.write_report,
            summarize_rows=cross_model_structured_event_adjudicator.summarize_rows,
            default_max_tokens=1800,
            default_structured_event_jsonl_path=(
                cross_model_structured_event_adjudicator.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "cross_model_challenge_adjudicator": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V11 open cross-model challenge adjudicator "
                "over saved GPT, Qwen, and DeepSeek structured-event artifacts."
            ),
            default_jsonl_path=cross_model_challenge_adjudicator.DEFAULT_JSONL_PATH,
            default_report_path=cross_model_challenge_adjudicator.DEFAULT_REPORT_PATH,
            run_split=cross_model_challenge_adjudicator.run_split,
            write_jsonl=cross_model_challenge_adjudicator.write_jsonl,
            write_report=cross_model_challenge_adjudicator.write_report,
            summarize_rows=cross_model_challenge_adjudicator.summarize_rows,
            default_max_tokens=2000,
            default_structured_event_jsonl_path=(
                cross_model_challenge_adjudicator.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "cross_model_challenge_gated_adjudicator": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V11 cross-model challenge adjudicator with "
                "the high-precision peer-selection gate."
            ),
            default_jsonl_path=cross_model_challenge_adjudicator.DEFAULT_GATED_JSONL_PATH,
            default_report_path=cross_model_challenge_adjudicator.DEFAULT_GATED_REPORT_PATH,
            run_split=lambda records, **kwargs: cross_model_challenge_adjudicator.run_split(
                records,
                safety_policy="high_precision",
                **kwargs,
            ),
            write_jsonl=cross_model_challenge_adjudicator.write_jsonl,
            write_report=cross_model_challenge_adjudicator.write_report,
            summarize_rows=cross_model_challenge_adjudicator.summarize_rows,
            default_max_tokens=2000,
            default_structured_event_jsonl_path=(
                cross_model_challenge_adjudicator.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
        ),
        "fresh_evidence_reasoner": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 V12 fresh-evidence reasoner over saved GPT, "
                "Qwen, and DeepSeek structured-event traces."
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
        "deterministic": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 deterministic rules-only pipeline.",
            default_jsonl_path=Path("experiments/gan2026_deterministic_pipeline_validation.jsonl"),
            default_report_path=Path("experiments/gan2026_deterministic_pipeline_validation.md"),
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="deterministic",
                **kwargs,
            ),
            write_jsonl=write_jsonl,
            write_report=write_deterministic_report,
            default_max_tokens=900,
        ),
        "deterministic_canonical_pipeline": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 staged deterministic_canonical_pipeline "
                "architecture (proven byte-identical to 'deterministic')."
            ),
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
        "hybrid": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 CandidateSet hybrid (assessment + projection) pipeline.",
            default_jsonl_path=Path("experiments/gan2026_hybrid_pipeline_validation.jsonl"),
            default_report_path=Path("experiments/gan2026_hybrid_pipeline_validation.md"),
            run_split=lambda records, **kwargs: run_split(records, architecture="hybrid", **kwargs),
            write_jsonl=llm_candidate_set_clinical_assessment_probe.write_jsonl,
            write_report=llm_candidate_set_clinical_assessment_probe.write_report,
            summarize_rows=llm_candidate_set_clinical_assessment_probe.summarize_records,
            default_max_tokens=2400,
            default_candidate_set_jsonl_path=None,
        ),
        "llm_only_direct_labeler": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only direct-labeler experiment.",
            default_jsonl_path=llm_only_direct_labeler.DEFAULT_JSONL_PATH,
            default_report_path=llm_only_direct_labeler.DEFAULT_REPORT_PATH,
            run_split=lambda records, **kwargs: run_split(
                records,
                architecture="llm_only_direct_labeler",
                **kwargs,
            ),
            write_jsonl=llm_only_direct_labeler.write_jsonl,
            write_report=llm_only_direct_labeler.write_report,
            summarize_rows=llm_only_direct_labeler.summarize_records,
            default_max_tokens=900,
        ),
        "hybrid_structured_events": GanLlmPipelineCliSpec(
            description="Run the Gan 2026 LLM-only structured-events experiment.",
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
        "llm_only_canonical_pipeline": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 LLM-only canonical-pipeline (purest-form, "
                "single-shot extract/select/normalize/project/render) experiment."
            ),
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
    }
