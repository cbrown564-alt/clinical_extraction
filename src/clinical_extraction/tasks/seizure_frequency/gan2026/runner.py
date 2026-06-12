"""Unified parameterized runner framework for Gan 2026 pipelines.

This module unifies the execution sequence of the deterministic, hybrid,
and fully-LLM architectures, providing consistent intermediate schemas and
unified artifact generation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    deterministic_canonical_stages as canonical_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_score as projection_score,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_decision as verification_decision,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_route as verification_route,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    deterministic_candidate_set_from_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    GanRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    _candidate_event,
    _extract_candidates,
    _fallback_evidence,
    _normalize_candidate,
    _select_final_event,
)

PipelineArchitecture = Literal[
    "deterministic",
    "deterministic_canonical_pipeline",
    "hybrid",
    "llm_only_direct_labeler",
    "hybrid_structured_events",
    "llm_only_canonical_pipeline",
]

# Architecture family groupings (for reporting and taxonomy).
# Two hybrid configs share deterministic downstream stages (normalize/project/render/score)
# but differ in their LLM task. Contrast with "fully_llm" configs (direct_labeler,
# canonical_pipeline) that
# own the full extraction-to-label pass in one LLM call with no deterministic
# normalization stage. The two hybrids differ in their LLM task:
#   - hybrid_structured_events: LLM extracts structured events (open-text → schema)
#   - hybrid: LLM assesses a pre-extracted deterministic candidate set
ARCHITECTURE_FAMILY: dict[str, str] = {
    "deterministic": "deterministic",
    "deterministic_canonical_pipeline": "deterministic",
    "hybrid": "hybrid",
    "llm_only_direct_labeler": "fully_llm",
    "hybrid_structured_events": "hybrid",
    "llm_only_canonical_pipeline": "fully_llm",
}


class PipelineConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    architecture: PipelineArchitecture
    ablation_config: AblationConfig = AblationConfig()
    dspy_cache: bool = True
    model: str = "openai/gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 900


@dataclass(frozen=True)
class PipelineOutputArtifact:
    projection_render_rows: list[dict[str, Any]]
    score_rows: list[dict[str, Any]]
    route_rows: list[dict[str, Any]]
    decision_rows: list[dict[str, Any]]
    metadata: dict[str, Any]


class Gan2026PipelineRunner:
    """Unified runner capable of executing all Gan 2026 pipeline configurations."""

    def __init__(self, config: PipelineConfiguration) -> None:
        self.config = config

    def _configure_lm(self) -> None:
        import dspy

        from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
            build_dspy_lm,
        )

        lm = build_dspy_lm(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            cache=self.config.dspy_cache,
        )
        dspy.configure(lm=lm)

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        """Run a single record through the unified schema flow based on architecture."""
        if self.config.architecture == "deterministic":
            # 1. Extraction
            raw_candidates = _extract_candidates(item.note_text, self.config.ablation_config)
            if not raw_candidates:
                raw_candidates = [
                    RawCandidate(
                        kind=CandidateKind.NO_REFERENCE,
                        label="no seizure frequency reference",
                        evidence=_fallback_evidence(item.note_text),
                    )
                ]

            candidate_set = deterministic_candidate_set_from_raw(
                raw_candidates,
                note_text=item.note_text,
                source_row_index=item.source_row_index or 1,
            )

            # 2. Selection
            candidate_events = [
                _candidate_event(index=index, candidate=candidate, note_text=item.note_text)
                for index, candidate in enumerate(raw_candidates, start=1)
            ]
            normalized_events = [
                _normalize_candidate(event, raw_candidate, self.config.ablation_config)
                for event, raw_candidate in zip(candidate_events, raw_candidates, strict=True)
            ]
            final_selection = _select_final_event(
                candidate_events,
                normalized_events,
                self.config.ablation_config,
            )

            # Translate event_id (e.g. "event_1") to candidate_id (e.g. "det:1:1")
            # Zipped index matches
            selected_index = int(final_selection.selected_event_ids[0].split("_")[1]) - 1
            selected_candidate = candidate_set.candidates[selected_index]

            # 3. Direct final label selection for deterministic run
            output = FinalExtraction(
                final_value=final_selection.final_label,
                rationale=final_selection.rationale,
                evidence=final_selection.evidence,
            )

            # 4. Optional intermediate ClinicalAssessment diagnostics for visibility
            disabled_switches = {
                group.value
                for group in RuleGroup
                if group not in self.config.ablation_config.enabled_groups
            } | set(self.config.ablation_config.disabled_rule_ids)

            draft = assessment_probe.AssessmentDraft(
                assessment_kind=selected_candidate.candidate_kind,
                primary_candidate_ids=[selected_candidate.candidate_id],
                supporting_candidate_ids=[
                    c.candidate_id
                    for idx, c in enumerate(candidate_set.candidates)
                    if idx != selected_index
                ],
                normalized_burden=assessment_probe.AssessmentDraftBurden(
                    source_normalized_phrase=final_selection.evidence
                ),
                assessment_summary=final_selection.rationale,
            )
            try:
                clinical_assessment, _ = assessment_probe.assemble_clinical_assessment(
                    draft,
                    candidate_set=candidate_set,
                    disabled_ablation_switches=disabled_switches,
                )
            except Exception:
                clinical_assessment = None

            from clinical_extraction.core.evidence import evidence_is_substring
            diagnostics = {
                "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
                "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
                "final_selection": final_selection.model_dump(mode="json"),
                "evidence_valid": evidence_is_substring(item.note_text, final_selection.evidence),
                "clinical_assessment": (
                    clinical_assessment.model_dump() if clinical_assessment else None
                ),
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        elif self.config.architecture == "deterministic_canonical_pipeline":
            # Same logic as "deterministic", restructured into named, stage-owned,
            # ablatable Extract/Normalize/Select & Render/Evidence Trace Check form
            # (a pure staging pass; see decision 0013).
            # Diagnostics are kept key-identical to "deterministic" so "rules
            # unchanged" is a directly assertable equivalence.
            raw_candidates, candidate_set, candidate_events = canonical_stages.extract_stage(
                item.note_text,
                source_row_index=item.source_row_index or 1,
                ablation_config=self.config.ablation_config,
            )

            normalized_events = canonical_stages.normalize_stage(
                candidate_events,
                raw_candidates,
                ablation_config=self.config.ablation_config,
            )

            final_selection = canonical_stages.select_and_render_stage(
                candidate_events,
                normalized_events,
                ablation_config=self.config.ablation_config,
            )

            # Translate event_id (e.g. "event_1") to candidate_id (e.g. "det:1:1")
            # Zipped index matches
            selected_index = int(final_selection.selected_event_ids[0].split("_")[1]) - 1

            output = FinalExtraction(
                final_value=final_selection.final_label,
                rationale=final_selection.rationale,
                evidence=final_selection.evidence,
            )

            disabled_switches = {
                group.value
                for group in RuleGroup
                if group not in self.config.ablation_config.enabled_groups
            } | set(self.config.ablation_config.disabled_rule_ids)

            evidence_valid, clinical_assessment = canonical_stages.evidence_trace_check_stage(
                item.note_text,
                final_selection=final_selection,
                candidate_set=candidate_set,
                selected_index=selected_index,
                disabled_ablation_switches=disabled_switches,
            )

            diagnostics = {
                "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
                "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
                "final_selection": final_selection.model_dump(mode="json"),
                "evidence_valid": evidence_valid,
                "clinical_assessment": (
                    clinical_assessment.model_dump() if clinical_assessment else None
                ),
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        elif self.config.architecture == "hybrid":
            # 1. Extraction (same as deterministic)
            raw_candidates = _extract_candidates(item.note_text, self.config.ablation_config)
            if not raw_candidates:
                raw_candidates = [
                    RawCandidate(
                        kind=CandidateKind.NO_REFERENCE,
                        label="no seizure frequency reference",
                        evidence=_fallback_evidence(item.note_text),
                    )
                ]

            candidate_set = deterministic_candidate_set_from_raw(
                raw_candidates,
                note_text=item.note_text,
                source_row_index=item.source_row_index or 1,
            )

            self._configure_lm()

            inputs = assessment_probe.build_assessment_inputs(item, candidate_set)
            program = assessment_probe.DspyCandidateSetClinicalAssessment()
            prediction = program(
                note_text=inputs["note_text"],
                source_row_index=inputs["source_row_index"],
                task_instructions=inputs["task_instructions"],
                policy_examples=inputs["policy_examples"],
                candidate_set=inputs["candidate_set"],
                output_contract=inputs["output_contract"],
            )

            draft = prediction.assessment_draft

            disabled_switches = {
                group.value
                for group in RuleGroup
                if group not in self.config.ablation_config.enabled_groups
            } | set(self.config.ablation_config.disabled_rule_ids)

            clinical_assessment, errors = assessment_probe.assemble_clinical_assessment(
                draft,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_switches,
            )

            if clinical_assessment is None:
                raise ValueError(f"ClinicalAssessment assembly failed: {errors}")

            # 3. Project & Render
            proj_decision, final_rendered_label = projection_render.project_and_render(
                clinical_assessment,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_switches,
            )
            final_value = final_rendered_label.rendered_label or "unknown"
            rationale = clinical_assessment.assessment_summary or ""
            evidence = final_rendered_label.evidence or ""

            output = FinalExtraction(
                final_value=final_value,
                rationale=rationale,
                evidence=evidence,
            )

            diagnostics = {
                "candidate_set": candidate_set.model_dump(),
                "assessment_draft": draft.model_dump() if draft else None,
                "clinical_assessment": (
                    clinical_assessment.model_dump() if clinical_assessment else None
                ),
                "projection_decision": proj_decision.model_dump() if proj_decision else None,
                "final_rendered_label": (
                    final_rendered_label.model_dump() if final_rendered_label else None
                ),
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        elif self.config.architecture == "llm_only_direct_labeler":
            from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
                llm_only_direct_labeler,
            )

            self._configure_lm()

            prompt_input_json = llm_only_direct_labeler.build_prompt_input(item)
            program = llm_only_direct_labeler.DspyLlmOnlyDirectLabelerExtractor()
            prediction = program(prompt_input_json=prompt_input_json)
            raw_output = str(prediction.decision_json)

            decision, parse_errors = llm_only_direct_labeler.parse_decision_json(raw_output)

            output = FinalExtraction(
                final_value=decision.final_label if decision else "unknown",
                rationale=decision.rationale if decision else "extraction failed",
                evidence=decision.evidence if decision else "",
            )
            diagnostics = {
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        elif self.config.architecture == "hybrid_structured_events":
            from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
                hybrid_structured_events,
            )

            self._configure_lm()

            prompt_input_json = hybrid_structured_events.build_prompt_input(item)
            program = hybrid_structured_events.DspyStructuredExtractor()
            prediction = program(prompt_input_json=prompt_input_json)
            raw_output = str(prediction.structured_json)

            extraction, normalized_events, parse_errors = (
                hybrid_structured_events.parse_structured_json(
                    raw_output,
                    note_text=item.note_text,
                    repair_config=hybrid_structured_events.StructuredRepairConfig(),
                )
            )

            final_label = extraction.selection.final_label if extraction else "unknown"
            output = FinalExtraction(
                final_value=final_label,
                rationale=extraction.selection.rationale if extraction else "extraction failed",
                evidence=extraction.selection.evidence if extraction else "",
            )
            diagnostics = {
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "parse_errors": parse_errors,
                "structured_record": extraction.model_dump() if extraction else None,
                "normalized_events": [event.model_dump() for event in normalized_events],
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        elif self.config.architecture == "llm_only_canonical_pipeline":
            from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
                llm_only_canonical_pipeline,
            )

            self._configure_lm()

            prompt_input_json = llm_only_canonical_pipeline.build_prompt_input(item)
            program = llm_only_canonical_pipeline.DspyCanonicalLlmExtractor()
            prediction = program(prompt_input_json=prompt_input_json)
            raw_output = str(prediction.decision_json)

            decision, parse_errors = llm_only_canonical_pipeline.parse_decision_json(raw_output)

            from clinical_extraction.core.evidence import evidence_is_substring

            output = FinalExtraction(
                final_value=decision.final_label if decision else "unknown",
                rationale=decision.rationale if decision else "extraction failed",
                evidence=decision.evidence if decision else "",
            )
            diagnostics = {
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "evidence_text_contained": (
                    evidence_is_substring(item.note_text, decision.evidence)
                    if decision and decision.evidence
                    else False
                ),
            }
            return PipelineResult(output=output, diagnostics=diagnostics)

        else:
            raise ValueError(
                "Unsupported architecture for single-item run: "
                f"{self.config.architecture}"
            )

    def run_split(
        self,
        records: Sequence[GanFrequencyRecord],
        *,
        split: str,
        split_manifest: str,
        mode: Literal["live", "prompt-only"],
        escalation_reason: str | None = None,
        progress_every: int | None = None,
        checkpoint_jsonl_path: Path | None = None,
        checkpoint_report_path: Path | None = None,
        candidate_set_jsonl_path: Path | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return run_split(
            records,
            architecture=self.config.architecture,
            split=split,
            split_manifest=split_manifest,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            mode=mode,
            dspy_cache=self.config.dspy_cache,
            api_base=None,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
            candidate_set_jsonl_path=candidate_set_jsonl_path,
        )


def build_unified_pipeline_artifact(
    *,
    architecture: PipelineArchitecture,
    assessment_rows: Sequence[Mapping[str, Any]],
    candidate_sets: Mapping[int, CandidateSet],
    gold_records: Mapping[int, GanFrequencyRecord],
    assessment_artifact_path: str = "in_memory",
    candidate_set_artifact_path: str = "in_memory",
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
    project_render_artifact_path: str | None = None,
    score_artifact_path: str | None = None,
    route_artifact_path: str | None = None,
) -> PipelineOutputArtifact:
    """Build unified pipeline artifacts using deterministic downstream stages."""
    projection_render_rows, projection_render_metadata = (
        projection_render.build_projection_render_artifact(
            assessment_rows,
            candidate_sets=candidate_sets,
            assessment_artifact_path=assessment_artifact_path,
            candidate_set_artifact_path=candidate_set_artifact_path,
            disabled_ablation_switches=disabled_ablation_switches,
        )
    )
    score_rows, score_metadata = projection_score.build_scoring_artifact(
        projection_render_rows,
        gold_records=gold_records,
        project_render_artifact_path=project_render_artifact_path or "in_memory",
    )
    route_rows, route_metadata = verification_route.build_verification_route_artifact(
        score_rows,
        score_artifact_path=score_artifact_path or "in_memory",
    )
    decision_rows, decision_metadata = (
        verification_decision.build_verification_decision_artifact(
            route_rows,
            route_artifact_path=route_artifact_path or "in_memory",
        )
    )

    projection_summary = dict(projection_render_metadata.get("summary") or {})
    score_summary = dict(score_metadata.get("summary") or {})
    route_summary = dict(route_metadata.get("summary") or {})
    decision_summary = dict(decision_metadata.get("summary") or {})

    metadata = {
        "artifact_kind": f"gan2026_{architecture}_pipeline",
        "pipeline_family": f"{architecture}_pipeline",
        "pipeline_version": f"gan2026_{architecture}_pipeline_v0",
        "claim_boundary": (
            "validation-development unified composition; no model calls, no "
            "locked-test inspection, and score context remains audit-only"
        ),
        "source_artifacts": {
            "assessment_artifact_path": assessment_artifact_path,
            "candidate_set_artifact_path": candidate_set_artifact_path,
        },
        "disabled_ablation_switches": sorted(disabled_ablation_switches or []),
        "stage_metadata": {
            "projection_render": dict(projection_render_metadata),
            "score": dict(score_metadata),
            "route": dict(route_metadata),
            "verification_decision": dict(decision_metadata),
        },
        "summary": {
            "input_assessment_rows": len(assessment_rows),
            "projection_rows": int(projection_summary.get("projection_rows", 0)),
            "rendered_label_rows": int(projection_summary.get("rendered_label_rows", 0)),
            "null_rendered_label_rows": int(
                projection_summary.get("null_rendered_label_rows", 0)
            ),
            "scored_rows": int(score_summary.get("scored_rows", 0)),
            "purist_correct": int(score_summary.get("purist_correct", 0)),
            "routed_rows": int(route_summary.get("routed_rows", 0)),
            "decision_rows": int(decision_summary.get("decision_rows", 0)),
            "action_counts": dict(decision_summary.get("action_counts") or {}),
        },
    }

    return PipelineOutputArtifact(
        projection_render_rows=list(projection_render_rows),
        score_rows=list(score_rows),
        route_rows=list(route_rows),
        decision_rows=list(decision_rows),
        metadata=metadata,
    )


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    architecture: PipelineArchitecture,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Execute a run split using the specified unified runner architecture."""
    if architecture in ("deterministic", "deterministic_canonical_pipeline"):
        from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
            label_to_frequency_record,
        )
        from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
            build_run_metadata,
        )
        from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
            map_pragmatic,
            map_purist,
        )

        config = PipelineConfiguration(
            architecture=architecture,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            dspy_cache=dspy_cache,
        )
        runner = Gan2026PipelineRunner(config)
        rows = []
        for record in records:
            result = runner.run(record)
            final_label = result.output.final_value
            predicted_frequency = label_to_frequency_record(final_label).monthly_frequency
            comparison = {
                "predicted_monthly_frequency": predicted_frequency,
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "purist_correct": map_purist(predicted_frequency)
                == map_purist(record.gold_monthly_frequency),
                "pragmatic_correct": map_pragmatic(predicted_frequency)
                == map_pragmatic(record.gold_monthly_frequency),
            }
            rows.append(
                {
                    "source_row_index": record.source_row_index,
                    "split": split,
                    "split_manifest": split_manifest,
                    "final_label": final_label,
                    "evidence_valid": bool(result.diagnostics.get("evidence_valid")),
                    "diagnostics": result.diagnostics,
                    "comparison": comparison,
                    "reference": {
                        "gold_label": record.gold_label,
                        "gold_monthly_frequency": record.gold_monthly_frequency,
                        "row_ok": record.row_ok,
                    },
                }
            )

        metadata = build_run_metadata(
            mode=mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_version=f"{architecture}_v1",
            dspy_version="none",
            split=split,
            split_manifest=split_manifest,
            api_base=api_base,
            row_count=len(records),
        )
        purist_correct = sum(1 for r in rows if r["comparison"]["purist_correct"])
        pragmatic_correct = sum(1 for r in rows if r["comparison"]["pragmatic_correct"])
        metadata["summary"] = {
            "examples": len(rows),
            "purist_correct": purist_correct,
            "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
            "pragmatic_correct": pragmatic_correct,
            "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        }
        return rows, metadata

    elif architecture == "hybrid":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            llm_candidate_set_clinical_assessment_probe,
        )
        return llm_candidate_set_clinical_assessment_probe.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
            candidate_set_jsonl_path=candidate_set_jsonl_path,
        )

    elif architecture == "llm_only_direct_labeler":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_only_direct_labeler
        return llm_only_direct_labeler.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )

    elif architecture == "hybrid_structured_events":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            hybrid_structured_events,
        )
        return hybrid_structured_events.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )

    elif architecture == "llm_only_canonical_pipeline":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            llm_only_canonical_pipeline,
        )
        return llm_only_canonical_pipeline.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )
    else:
        raise ValueError(f"Unknown architecture: {architecture}")


def write_deterministic_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
        write_markdown_report,
    )
    summary = metadata.get("summary", {})
    lines = [
        "# Gan 2026 Deterministic Pipeline Validation Run",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation run of the deterministic baseline pipeline.",
        "",
        "## Summary",
        "",
        f"- Examples: {summary.get('examples', 0)}",
        f"- Purist-correct: {summary.get('purist_correct', 0)}",
        f"- Purist-accuracy: {summary.get('purist_accuracy', 0.0):.4f}",
        f"- Pragmatic-correct: {summary.get('pragmatic_correct', 0)}",
        f"- Pragmatic-accuracy: {summary.get('pragmatic_accuracy', 0.0):.4f}",
        "",
        "## Rows",
        "",
        "| Row | Predicted | Gold | Purist Correct | Pragmatic Correct |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        comp = row.get("comparison", {})
        lines.append(
            f"| {row['source_row_index']} | {row['final_label']} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comp.get('purist_correct') else 'no'} | "
            f"{'yes' if comp.get('pragmatic_correct') else 'no'} |"
        )
    write_markdown_report(path, lines)


def get_cli_specs() -> dict[str, Any]:
    from pathlib import Path

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

    def write_jsonl(rows, path):
        write_jsonl_rows(rows, path)

    return {
        "agentic_matched_budget": GanLlmPipelineCliSpec(
            description=(
                "Run the Gan 2026 agentic matched-budget prompt-only/no-call "
                "trace surface."
            ),
            default_jsonl_path=agentic_runner.DEFAULT_JSONL_PATH,
            default_report_path=agentic_runner.DEFAULT_REPORT_PATH,
            run_split=agentic_runner.run_split,
            write_jsonl=write_jsonl,
            write_report=agentic_runner.write_report,
            summarize_rows=agentic_runner.summarize_rows,
            default_max_tokens=900,
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
            # None -> run_split builds CandidateSets live (deterministic + LLM
            # union) per row instead of looking them up in the static 250-row
            # artifact, so the CLI covers the full split surface by default.
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
