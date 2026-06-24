"""Thin FastAPI wrapper for the clinical-extraction Observatory.

Shared cross-task backend the frontend consumes: Gan 2026 (registry, records,
rules, live pipeline/ablation execution) and ExECTv2 (the live ``/exectv2/runs``
frontend dataset). Lives at the package top level rather than under the gan2026
task because it now serves both datasets.
"""

from __future__ import annotations

import csv
import importlib
import inspect
import json
import os
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import (
    cached_exectv2_runs_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (  # noqa: E501
    cached_component_ablation_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_transition_examples import (  # noqa: E501
    cached_component_transitions_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    cached_gan_reliability_scorecard_json,
    cached_reliability_scorecard_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.component_stage_ladder import (  # noqa: E501
    cached_component_stage_ladder_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.component_transition_examples import (  # noqa: E501
    cached_component_transitions_json as cached_gan_component_transitions_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.gold_audit_active_sampler import (  # noqa: E501
    enrich_rows_for_active_sampling,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    temporal_selection,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.cluster import (
    CLUSTER_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.diary import (
    DIARY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.gan_shorthand import (
    GAN_SHORTHAND_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.rate import (
    PORTABLE_RATE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import evaluate_predictions
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    load_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1

# Hard-slice atlas imports (may fail if dependencies missing; guarded below)
try:
    from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
        hidden_family_atlas,
    )

    ATLAS_HARD_SLICE_DEFINITIONS = hidden_family_atlas.ATLAS_HARD_SLICE_DEFINITIONS
    classify_hidden_families = hidden_family_atlas.classify_hidden_families
except Exception:  # pragma: no cover
    ATLAS_HARD_SLICE_DEFINITIONS = ()
    classify_hidden_families = None  # type: ignore[assignment, misc]

PipelineFamily = Literal[
    "rules_only",
    "hybrid_structured_events",
    "llm_only_canonical_pipeline",
]
TEMPORAL_SELECTION_RULES = temporal_selection.TEMPORAL_SELECTION_RULES

PROMPT_MODULES = (
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler",
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events",
)

# Families that can actually be executed via /run/note and /run/ablation
EXECUTABLE_PIPELINES: set[str] = {"rules_only"}

# Historical registry rows are preserved, but deleted runner families should not
# re-enter the active Observatory pipeline-family surface.
RETIRED_PIPELINE_FAMILIES: set[str] = {
    "hybrid_parallel_state_candidate_reasoner",
    "hybrid_rules_candidates_llm_adjudicator",
    "llm_only_claim_table_selector",
    "llm_only_minimal_evidence_selector",
    "llm_only_simplified_selected_state_reasoner",
    "llm_only_sparse_operands_selected_state_reasoner",
    "llm_only_typed_adapter_reasoner",
    "llm_only_typed_operations_reasoner",
}

# The Explorer pipeline dropdown is trimmed to the three canonical Gan
# architectures that the Component Impact stage-ladder compares — one best
# performer per family (deterministic / hybrid / LLM-only). Historical
# comparator families stay in the registry but are no longer surfaced here.
# Re-introducing qwen/deepseek comparators (and unifying the labels with
# Component Impact) is tracked in
# docs/plans/architecture_comparison_expansion_qwen_deepseek_2026-06-24.md.
CANONICAL_PIPELINE_FAMILIES: dict[str, tuple[str, str]] = {
    "rules_only": ("Deterministic V1", "rules_only"),
    "hybrid_structured_events": ("Hybrid Structured Events", "hybrid"),
    "llm_only_canonical_pipeline": ("LLM-only Canonical", "llm_only"),
}


class ObservatorySettings(BaseModel):
    """Filesystem settings for Observatory endpoints."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    repo_root: Path
    data_path: Path
    split_manifest_path: Path
    registry_path: Path
    experiments_dir: Path


class AblationConfigPayload(BaseModel):
    """JSON-serialisable form of the deterministic rule ablation config."""

    enabled_groups: list[RuleGroup] | None = None
    enabled_portability: list[Portability] | None = None
    disabled_rule_ids: list[str] = Field(default_factory=list)

    def to_domain(self) -> AblationConfig:
        return AblationConfig(
            enabled_groups=frozenset(self.enabled_groups or list(RuleGroup)),
            enabled_portability=frozenset(self.enabled_portability or list(Portability)),
            disabled_rule_ids=frozenset(self.disabled_rule_ids),
        )


class RunNoteRequest(BaseModel):
    """Single-note execution request."""

    note_text: str = Field(min_length=1)
    pipeline: PipelineFamily = "rules_only"
    source_row_index: int = 0
    gold_label: str = "unknown"
    gold_reference: str = ""
    ablation_config: AblationConfigPayload = Field(default_factory=AblationConfigPayload)


class RunAblationRequest(BaseModel):
    """Batch deterministic ablation request against a named Gan split."""

    split: str = "validation"
    pipeline: PipelineFamily = "rules_only"
    limit: int | None = Field(default=None, ge=1)
    ablation_config: AblationConfigPayload = Field(default_factory=AblationConfigPayload)


class GoldAuditDecision(BaseModel):
    """Single human audit decision for a gold label row."""

    source_row_index: int
    split: str
    simple_class: Literal["correct", "ambiguous", "wrong"] = "ambiguous"
    rq10_class: Literal[
        "true_extraction_failure",
        "benchmark_convention_dominated",
        "underdetermined_note",
        "clinically_defensible_alternative",
        "possible_gold_weakness",
        "instrumentation_gap",
    ] | None = None
    notes: str = ""
    corrected_gold_label: str | None = None
    benchmark_convention_flag: bool = False
    all_system_fail: bool = False
    exact_evidence_but_scorer_wrong: bool = False
    clinically_defensible_alternative: bool = False
    likely_gold_defect: bool = False
    timestamp: str | None = None
    auditor: str | None = None


class TagErrorRequest(BaseModel):
    """Request to classify a single prediction into the frontend error taxonomy."""

    gold_category: str
    predicted_category: str
    purist_correct: bool = False
    pragmatic_correct: bool = False


class HardSliceMembershipRequest(BaseModel):
    """Request to compute hard-slice membership for a set of artifact rows."""

    rows: list[dict[str, Any]]
    primary_layer: str | None = None


class PromptTemplateResponse(BaseModel):
    """Structured prompt metadata for a single module."""

    module: str
    prompt_version: str
    system_hint: str | None = None
    user_hint: str | None = None
    output_schema_hint: str | None = None
    build_prompt_signature: str | None = None
    policy_taxonomy: list[dict[str, Any]]


def create_app(
    *,
    repo_root: Path | None = None,
    data_path: Path | None = None,
    split_manifest_path: Path | None = None,
    registry_path: Path | None = None,
    experiments_dir: Path | None = None,
) -> FastAPI:
    """Create the Observatory FastAPI app."""

    root = (repo_root or _discover_repo_root()).resolve()
    settings = ObservatorySettings(
        repo_root=root,
        data_path=_resolve_under_root(root, data_path or DEFAULT_DATA_PATH),
        split_manifest_path=_resolve_under_root(
            root,
            split_manifest_path or DEFAULT_SPLIT_MANIFEST_PATH,
        ),
        registry_path=_resolve_under_root(
            root,
            registry_path or Path("experiments/registry.jsonl"),
        ),
        experiments_dir=_resolve_under_root(root, experiments_dir or Path("experiments")),
    )

    app = FastAPI(
        title="Clinical Extraction Observatory API",
        version="0.1.0",
        summary=(
            "Thin backend over the clinical-extraction pipelines, artifacts, "
            "and frontend datasets (Gan 2026 and ExECTv2)."
        ),
    )
    app.state.observatory_settings = settings

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/exectv2/runs")
    def get_exectv2_runs() -> Response:
        """Live ExECTv2 frontend dataset — parity with Gan's live registry/artifacts.

        Rendered from the canonical artifact index by the shared
        ``exectv2.frontend_review`` module (the same source the committed dev
        fallback is generated from). The serialized body is process-cached.
        """
        try:
            return Response(content=cached_exectv2_runs_json(), media_type="application/json")
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build ExECTv2 runs: {exc}",
            ) from exc

    @app.get("/exectv2/reliability-scorecard")
    def get_exectv2_reliability_scorecard() -> Response:
        """Structured ExECTv2 reliability scorecard for the frontend view."""
        try:
            return Response(
                content=cached_reliability_scorecard_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build ExECTv2 reliability scorecard: {exc}",
            ) from exc

    @app.get("/exectv2/component-ablation")
    def get_exectv2_component_ablation() -> Response:
        """Structured ExECTv2 layered component-impact replay for the frontend."""
        try:
            return Response(
                content=cached_component_ablation_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build ExECTv2 component ablation payload: {exc}",
            ) from exc

    @app.get("/exectv2/component-transitions")
    def get_exectv2_component_transitions() -> Response:
        """Illustrative per-letter stage-transition examples for the Component Impact sidebar."""
        try:
            return Response(
                content=cached_component_transitions_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build ExECTv2 component transition examples: {exc}",
            ) from exc

    @app.get("/gan2026/reliability-scorecard")
    def get_gan2026_reliability_scorecard() -> Response:
        """Structured Gan reliability scorecard for the frontend view."""
        try:
            return Response(
                content=cached_gan_reliability_scorecard_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build Gan reliability scorecard: {exc}",
            ) from exc

    @app.get("/gan2026/component-ablation")
    def get_gan2026_component_ablation() -> Response:
        """Replay-only Gan component stage-ladder for the frontend view."""
        try:
            return Response(
                content=cached_component_stage_ladder_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build Gan component ablation payload: {exc}",
            ) from exc

    @app.get("/gan2026/component-transitions")
    def get_gan2026_component_transitions() -> Response:
        """Illustrative per-note stage label trajectories for the Component Impact sidebar."""
        try:
            return Response(
                content=cached_gan_component_transitions_json(),
                media_type="application/json",
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build Gan component transition examples: {exc}",
            ) from exc

    @app.post("/run/note")
    def run_note(request: RunNoteRequest) -> dict[str, Any]:
        _require_supported_pipeline(request.pipeline)
        record = _request_record(request)
        result = Gan2026PipelineV1(request.ablation_config.to_domain()).run(record)
        return {
            "pipeline": request.pipeline,
            "source_row_index": record.source_row_index,
            "gold_label": record.gold_label,
            "result": result.model_dump(mode="json"),
        }

    @app.post("/run/ablation")
    def run_ablation(request: RunAblationRequest) -> dict[str, Any]:
        _require_supported_pipeline(request.pipeline)
        records = _load_split_records(settings, request.split)
        if request.limit is not None:
            records = records[: request.limit]
        pipeline = Gan2026PipelineV1(request.ablation_config.to_domain())
        rows = []
        predictions = []
        references = []
        for record in records:
            result = pipeline.run(record)
            final_selection = result.diagnostics["final_selection"]
            predicted_label = str(final_selection["final_label"])
            predicted_frequency = label_to_frequency_record(predicted_label).monthly_frequency
            rows.append(
                {
                    "source_row_index": record.source_row_index,
                    "prediction_label": predicted_label,
                    "prediction_monthly_frequency": predicted_frequency,
                    "gold_label": record.gold_label,
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "evidence_valid": bool(result.diagnostics.get("evidence_valid")),
                    "diagnostics": result.diagnostics,
                    "purist_predicted_category": map_purist(predicted_frequency),
                    "purist_gold_category": map_purist(record.gold_monthly_frequency),
                    "pragmatic_predicted_category": map_pragmatic(predicted_frequency),
                    "pragmatic_gold_category": map_pragmatic(record.gold_monthly_frequency),
                }
            )
            predictions.append(predicted_frequency)
            references.append(record.gold_monthly_frequency)
        return {
            "split": request.split,
            "pipeline": request.pipeline,
            "row_count": len(rows),
            "ablation_config": request.ablation_config.model_dump(mode="json"),
            "summary": {
                "total": len(rows),
                "purist": evaluate_predictions(references, predictions, method="purist"),
                "pragmatic": evaluate_predictions(references, predictions, method="pragmatic"),
            },
            "rows": rows,
        }

    @app.get("/artifacts/{run_id}")
    def get_artifact(
        run_id: str,
        artifact_path: str | None = Query(default=None),
        limit: int | None = Query(default=None, ge=1),
    ) -> dict[str, Any]:
        entry = _registry_entry(settings, run_id)
        record = entry.to_json_record()
        selected_paths = _select_artifact_paths(
            settings.repo_root,
            record["artifact_paths"],
            record.get("split"),
            artifact_path,
        )
        if not selected_paths:
            return {
                "run_id": run_id,
                "artifact_paths": [],
                "artifact_type": "none",
                "content": [],
                "note": "No JSONL artifacts available for this run",
            }
        all_content: list[Any] = []
        for selected_path in selected_paths:
            resolved = _safe_repo_path(settings.repo_root, selected_path)
            if not resolved.exists():
                continue
            content = _load_artifact_content(resolved, limit=limit)
            if isinstance(content, list):
                all_content.extend(content)
            else:
                all_content.append(content)
        # Re-apply limit after merging
        if limit is not None:
            all_content = all_content[:limit]
        return {
            "run_id": run_id,
            "artifact_paths": selected_paths,
            "artifact_type": "jsonl",
            "content": all_content,
        }

    @app.get("/registry")
    def registry() -> dict[str, Any]:
        entries = [entry.to_json_record() for entry in load_run_registry(settings.registry_path)]
        return {
            "registry_path": _relative_to_root(settings, settings.registry_path),
            "runs": entries,
        }

    @app.get("/splits/{split_name}")
    def split(split_name: str) -> dict[str, Any]:
        manifest = load_split_manifest(settings.split_manifest_path)
        splits = manifest.get("splits", {})
        if split_name not in splits:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown split {split_name!r}; expected one of {sorted(splits)}",
            )
        payload = dict(splits[split_name])
        payload["split_name"] = split_name
        payload["manifest_path"] = _relative_to_root(settings, settings.split_manifest_path)
        payload["split_manifest"] = manifest.get("split_manifest", "gan2026_split_v1")
        return payload

    @app.get("/rules")
    def rules() -> dict[str, Any]:
        specs = _all_rule_specs()
        return {
            "groups": [group.value for group in RuleGroup],
            "portability": [portability.value for portability in Portability],
            "rules": [_rule_payload(spec) for spec in specs],
        }

    @app.get("/pipeline-families")
    def pipeline_families() -> dict[str, Any]:
        families = _build_pipeline_families(settings)
        return {"families": families}

    @app.get("/prompts")
    def prompts() -> dict[str, Any]:
        return {"prompts": [_prompt_payload(module_name) for module_name in PROMPT_MODULES]}

    @app.get("/records/{split_name}")
    def records(split_name: str) -> dict[str, Any]:
        records = _load_split_records(settings, split_name)
        return {
            "split": split_name,
            "count": len(records),
            "records": [
                {
                    "source_row_index": r.source_row_index,
                    "gold_label": r.gold_label,
                    "gold_reference": r.gold_reference,
                    "row_ok": r.row_ok,
                    "note_preview": r.note_text[:200].replace("\n", " "),
                }
                for r in records
            ],
        }

    @app.get("/records/{split_name}/{source_row_index}")
    def record(split_name: str, source_row_index: int) -> dict[str, Any]:
        records = _load_split_records(settings, split_name)
        for r in records:
            if r.source_row_index == source_row_index:
                return {
                    "split": split_name,
                    "source_row_index": r.source_row_index,
                    "gold_label": r.gold_label,
                    "gold_reference": r.gold_reference,
                    "row_ok": r.row_ok,
                    "note_text": r.note_text,
                    "labels_match_all_categories": r.labels_match_all_categories,
                    "quotes_ok_all_categories": r.quotes_ok_all_categories,
                }
        raise HTTPException(
            status_code=404,
            detail=f"Record {source_row_index} not found in split {split_name}",
        )

    # ── Gold Audit endpoints ──

    @app.get("/gold-audit/rows")
    def gold_audit_rows(split: str = Query(default="validation")) -> dict[str, Any]:
        rows = _load_gold_audit_rows(settings, split=split)
        decisions = _load_gold_audit_decisions(settings)
        class_counts: dict[str, int] = {c: 0 for c in RQ10_CLASS_ORDER}
        for d in decisions:
            c = str(d.get("rq10_class", ""))
            if c in class_counts:
                class_counts[c] += 1
        enriched, model_summary = enrich_rows_for_active_sampling(rows, decisions)
        for row in enriched:
            row["priority_score"] = row["active_learning_score"]
        return {
            "split": split,
            "total": len(rows),
            "decided": sum(1 for row in enriched if row["has_decision"]),
            "class_counts": class_counts,
            "sampling_model": model_summary,
            "rows": enriched,
        }

    @app.get("/gold-audit/decisions")
    def gold_audit_decisions(split: str | None = Query(default=None)) -> dict[str, Any]:
        all_decisions = _load_gold_audit_decisions(settings)
        if split is not None:
            all_decisions = [d for d in all_decisions if d.get("split") == split]
        return {"decisions": all_decisions, "count": len(all_decisions)}

    @app.post("/gold-audit/decide")
    def gold_audit_decide(decision: GoldAuditDecision) -> dict[str, Any]:
        payload = decision.model_dump(mode="json")
        if not payload.get("timestamp"):
            payload["timestamp"] = datetime.now(UTC).isoformat()
        _save_gold_audit_decision(settings, payload)
        return {"status": "saved", "decision": payload}

    @app.get("/gold-audit/next")
    def gold_audit_next(split: str = Query(default="validation")) -> dict[str, Any]:
        rows = _load_gold_audit_rows(settings, split=split)
        decisions = _load_gold_audit_decisions(settings)
        next_row = _compute_next_row(rows, decisions)
        if next_row is None:
            return {"split": split, "row": None, "message": "All rows have been audited."}
        return {"split": split, "row": next_row}

    # ── Error taxonomy endpoints ──

    @app.get("/error-taxonomy/schema")
    def error_taxonomy_schema() -> dict[str, Any]:
        return {
            "error_types": [
                {"id": "correct", "description": "Prediction exactly matches gold standard."},
                {
                    "id": "false_negative",
                    "description": (
                        "Predicted no-seizure/unknown when note describes a frequency."
                    ),
                },
                {
                    "id": "false_positive",
                    "description": (
                        "Predicted a frequency when gold is no-seizure/unknown."
                    ),
                },
                {"id": "over_estimate", "description": "Predicted higher frequency than gold."},
                {"id": "under_estimate", "description": "Predicted lower frequency than gold."},
                {"id": "near_miss", "description": "Off by exactly one category bucket."},
            ],
            "severity": {
                "description": "Absolute magnitude delta between gold and predicted category.",
                "levels": ["none", "near", "moderate", "significant", "severe"],
            },
        }

    @app.post("/tag-error")
    def tag_error(request: TagErrorRequest) -> dict[str, Any]:
        return _classify_error(
            request.gold_category,
            request.predicted_category,
            request.purist_correct,
        )

    # ── Hard-slice endpoints ──

    @app.get("/hard-slices/definitions")
    def hard_slice_definitions() -> dict[str, Any]:
        return {
            "slices": [
                dict(definition) for definition in ATLAS_HARD_SLICE_DEFINITIONS
            ],
        }

    @app.post("/hard-slices/membership")
    def hard_slice_membership(request: HardSliceMembershipRequest) -> dict[str, Any]:
        if classify_hidden_families is None:
            raise HTTPException(
                status_code=503,
                detail="Hard-slice classification dependencies are not available.",
            )
        results = []
        for row in request.rows:
            note_text = str(row.get("note_text", ""))
            gold_label = str(row.get("gold_label", ""))
            predicted_label = str(row.get("predicted_label", ""))
            families = classify_hidden_families(
                note_text=note_text,
                gold_label=gold_label,
                predicted_label=predicted_label,
            )
            results.append(
                {
                    "source_row_index": row.get("source_row_index"),
                    "hidden_families": list(families),
                }
            )
        return {"rows": results}

    # ── Prompt template registry ──

    @app.get("/prompts/{module_name}/template")
    def prompt_template(module_name: str) -> dict[str, Any]:
        if module_name not in PROMPT_MODULES:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Unknown prompt module: {module_name!r}. "
                    f"Expected one of {list(PROMPT_MODULES)}."
                ),
            )
        return _prompt_template_payload(module_name)

    # ── Git / repository metadata ──

    @app.get("/meta")
    def meta() -> dict[str, Any]:
        return {
            "git": _git_metadata(settings.repo_root),
            "observatory_version": "0.1.0",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    return app


# ── Gold audit helpers ──

DEFAULT_GOLD_AUDIT_CSV = Path(
    "experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv"
)
DEFAULT_GOLD_AUDIT_DECISIONS = Path("experiments/gold_audit_decisions.jsonl")


RQ10_CLASS_ORDER = [
    "true_extraction_failure",
    "benchmark_convention_dominated",
    "underdetermined_note",
    "clinically_defensible_alternative",
    "possible_gold_weakness",
    "instrumentation_gap",
]


def _load_gold_audit_rows(
    settings: ObservatorySettings, split: str = "validation"
) -> list[dict[str, Any]]:
    """Load ambiguity review CSV rows for the given split."""
    csv_path = _resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_CSV)
    if not csv_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("split") == split:
                rows.append(dict(row))
    return rows


def _load_gold_audit_decisions(settings: ObservatorySettings) -> list[dict[str, Any]]:
    """Load previously saved audit decisions from JSONL."""
    path = _resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_DECISIONS)
    if not path.exists():
        return []
    decisions: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                decisions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return decisions


def _save_gold_audit_decision(settings: ObservatorySettings, decision: dict[str, Any]) -> None:
    """Append a single decision to the JSONL store."""
    path = _resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_DECISIONS)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(decision, ensure_ascii=False, sort_keys=True) + "\n")


def _decision_key(d: Mapping[str, Any]) -> tuple[str, int]:
    return (str(d.get("split", "")), int(d.get("source_row_index", 0)))


def _compute_next_row(
    rows: Sequence[Mapping[str, Any]], decisions: Sequence[Mapping[str, Any]]
) -> dict[str, Any] | None:
    """Return the highest-priority un-audited row, or None if all audited."""
    enriched, _model_summary = enrich_rows_for_active_sampling(rows, decisions)
    candidates = [
        (float(row["active_learning_score"]), row) for row in enriched if not row["has_decision"]
    ]

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return dict(candidates[0][1])


def _discover_repo_root() -> Path:
    for candidate in (Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parents[6:7]):
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    return Path.cwd()


def _resolve_under_root(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid repository-relative path: {relative_path}",
        )
    resolved = (repo_root / path).resolve()
    if repo_root not in (resolved, *resolved.parents):
        raise HTTPException(status_code=400, detail=f"Path escapes repository: {relative_path}")
    return resolved


def _relative_to_root(settings: ObservatorySettings, path: Path) -> str:
    try:
        return str(path.relative_to(settings.repo_root))
    except ValueError:
        return str(path)


def _request_record(request: RunNoteRequest) -> GanRecord:
    gold_label = request.gold_label.strip() or "unknown"
    try:
        gold_record = label_to_frequency_record(gold_label)
    except ValueError:
        gold_record = label_to_frequency_record("unknown")
    return GanRecord(
        source_row_index=request.source_row_index,
        note_text=request.note_text,
        gold_label=gold_record.normalized_label,
        gold_reference=request.gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={"source": "observatory_run_note"},
    )


def _require_supported_pipeline(pipeline: str) -> None:
    if pipeline not in EXECUTABLE_PIPELINES:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline {pipeline!r} is not yet executable via the Observatory API. "
            f"Supported: {sorted(EXECUTABLE_PIPELINES)}.",
        )


def _load_split_records(settings: ObservatorySettings, split: str) -> Sequence[Any]:
    try:
        return load_records_for_split(
            split,
            data_path=settings.data_path,
            manifest_path=settings.split_manifest_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _registry_entry(settings: ObservatorySettings, run_id: str) -> Any:
    for entry in load_run_registry(settings.registry_path):
        if entry.run_id == run_id:
            return entry
    raise HTTPException(status_code=404, detail=f"Unknown run_id: {run_id}")


def _select_artifact_paths(
    repo_root: Path,
    paths: Sequence[str],
    split: str | None,
    requested: str | None,
) -> list[str]:
    if requested is not None:
        if requested not in paths:
            raise HTTPException(
                status_code=404,
                detail=f"Run does not reference artifact: {requested}",
            )
        return [requested]

    jsonl_paths = [p for p in paths if Path(p).suffix == ".jsonl"]
    if not jsonl_paths:
        return []

    # For validation+test splits, load all JSONL artifacts (they cover different splits)
    if split and "+" in split and "test" in split:
        return jsonl_paths

    # Otherwise pick the largest JSONL by file size (handles multiple sizes of same split)
    def _file_size(path: str) -> int:
        try:
            return os.path.getsize(_safe_repo_path(repo_root, path))
        except Exception:
            return 0

    largest = max(jsonl_paths, key=_file_size)
    return [largest]


def _load_artifact_content(path: Path, *, limit: int | None) -> Any:
    if path.suffix == ".jsonl":
        rows = load_jsonl_rows(path)
        return rows[:limit] if limit is not None else rows
    if path.suffix == ".json":
        content = json.loads(path.read_text(encoding="utf-8"))
        if limit is not None and isinstance(content, list):
            return content[:limit]
        return content
    return {"text": path.read_text(encoding="utf-8")}


def _all_rule_specs() -> tuple[RuleSpec, ...]:
    return (
        *PORTABLE_RATE_RULES,
        *CLUSTER_RULES,
        *DIARY_RULES,
        *SEIZURE_FREE_RULES,
        *GAN_SHORTHAND_RULES,
        *TEMPORAL_SELECTION_RULES,
        *BENCHMARK_REPAIR_RULES,
    )


def _rule_payload(spec: RuleSpec) -> dict[str, Any]:
    return {
        "rule_id": spec.rule_id,
        "group": spec.group.value,
        "portability": spec.portability.value,
        "description": spec.description,
        "regex_preview": spec.pattern.pattern,
        "provenance": spec.provenance,
        "examples": [_rule_example_payload(example) for example in spec.examples],
        "has_exclusions": bool(spec.exclude),
    }


def _rule_example_payload(example: Any) -> dict[str, Any]:
    return {
        "text": example.text,
        "expected_label": example.expected_label,
        "expected_evidence": example.expected_evidence,
        "anti_example": example.anti_example,
        "note": example.note,
    }


def _prompt_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])
    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "policy_taxonomy": _jsonable_mapping_sequence(taxonomy),
        "policy_ids": [
            str(policy["policy_id"])
            for policy in taxonomy
            if isinstance(policy, Mapping) and "policy_id" in policy
        ],
    }


def _llm_family_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    # Derive family value from module name (last segment)
    family_value = module_name.rsplit(".", maxsplit=1)[-1]
    kind = "llm_only" if "llm_only" in module_name else "hybrid"
    return {
        "value": family_value,
        "label": prompt_version,
        "executable": False,
        "kind": kind,
    }


def _build_pipeline_families(settings: ObservatorySettings) -> list[dict[str, Any]]:
    """Build the Explorer pipeline-family dropdown.

    Surfaces exactly the canonical Gan architectures declared in
    ``CANONICAL_PIPELINE_FAMILIES`` (deterministic / hybrid / LLM-only), in that
    order, so the Explorer dropdown matches the Component Impact comparison.
    Registry runs only supply each family's replay availability and run count;
    the label and kind are the canonical declarations, not registry prose.
    """
    entries = load_run_registry(settings.registry_path)

    # Group registry runs for each canonical family (ignore everything else).
    by_family: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        record = entry.to_json_record()
        family = record.get("pipeline_family")
        if not family or family in RETIRED_PIPELINE_FAMILIES:
            continue
        if family not in CANONICAL_PIPELINE_FAMILIES:
            continue
        by_family.setdefault(family, []).append(record)

    families: list[dict[str, Any]] = []
    for family, (label, kind) in CANONICAL_PIPELINE_FAMILIES.items():
        runs = by_family.get(family, [])
        has_jsonl = any(
            any(p.endswith(".jsonl") for p in r.get("artifact_paths", []))
            for r in runs
        )
        families.append(
            {
                "value": family,
                "label": label,
                "executable": family in EXECUTABLE_PIPELINES,
                "kind": kind,
                "has_replay_artifact": has_jsonl,
                "run_count": len(runs),
            }
        )

    return families


def _jsonable_mapping_sequence(items: Iterable[Any]) -> list[dict[str, Any]]:
    payload = []
    for item in items:
        if isinstance(item, Mapping):
            payload.append({str(key): value for key, value in item.items()})
    return payload


# ── Error taxonomy helpers ──

# 0 = no frequency information, 1 = very low, 8 = very high
_CATEGORY_MAGNITUDE: dict[str, int] = {
    "currently_no_seizure": 0,
    "seizure_freq_unknown": 0,
    "seizure_freq_1_per_yr": 1,
    "seizure_freq_1_per_6mon": 2,
    "seizure_freq_more1per6mon_less1mon": 3,
    "seizure_freq_1_per_mon": 4,
    "seizure_freq_more1mon_less1week": 5,
    "seizure_freq_1_per_week": 6,
    "seizure_freq_more1week_less1day": 7,
    "seizure_freq_1ormore_daily": 8,
    "seizure_infrequent": 1,
    "seizure_frequent": 8,
}


def _category_magnitude(cat: str) -> int:
    return _CATEGORY_MAGNITUDE.get(cat, 0)


def _classify_error(
    gold_category: str,
    predicted_category: str,
    purist_correct: bool,
) -> dict[str, Any]:
    if purist_correct:
        return {"error_type": "correct", "severity": 0, "severity_level": "none"}

    gold_mag = _category_magnitude(gold_category)
    pred_mag = _category_magnitude(predicted_category)
    severity = abs(pred_mag - gold_mag)

    if gold_mag > 0 and pred_mag == 0:
        error_type = "false_negative"
    elif gold_mag == 0 and pred_mag > 0:
        error_type = "false_positive"
    elif pred_mag > gold_mag:
        error_type = "near_miss" if pred_mag - gold_mag == 1 else "over_estimate"
    elif pred_mag < gold_mag:
        error_type = "near_miss" if gold_mag - pred_mag == 1 else "under_estimate"
    else:
        error_type = "near_miss"

    if severity == 0:
        severity_level = "none"
    elif severity == 1:
        severity_level = "near"
    elif severity <= 3:
        severity_level = "moderate"
    elif severity <= 5:
        severity_level = "significant"
    else:
        severity_level = "severe"

    return {"error_type": error_type, "severity": severity, "severity_level": severity_level}


# ── Prompt template helpers ──

def _prompt_template_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])

    # Try to extract DSPy signature docstring as system hint
    system_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and hasattr(attr, "__mro__"):
            # Heuristic: DSPy Signature subclasses have InputField/OutputField
            if any(hasattr(base, "fields") for base in attr.__mro__ if base is not object):
                doc = inspect.getdoc(attr)
                if doc and len(doc) > 20:
                    system_hint = doc
                    break

    # Try to extract build_prompt_input docstring as user hint
    user_hint: str | None = None
    build_fn = getattr(module, "build_prompt_input", None)
    if build_fn is not None:
        user_hint = inspect.getdoc(build_fn)

    # Try to find output schema class docstring
    output_schema_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, BaseModel) and "Record" in attr_name:
            doc = inspect.getdoc(attr)
            if doc and len(doc) > 10:
                output_schema_hint = doc
                break

    build_sig: str | None = None
    if build_fn is not None:
        try:
            build_sig = str(inspect.signature(build_fn))
        except Exception:
            build_sig = None

    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "system_hint": system_hint,
        "user_hint": user_hint,
        "output_schema_hint": output_schema_hint,
        "build_prompt_signature": build_sig,
        "policy_taxonomy": _jsonable_mapping_sequence(taxonomy),
    }


# ── Git metadata helpers ──

def _git_metadata(repo_root: Path) -> dict[str, Any]:
    def _run(cmd: list[str]) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit = _run(["git", "rev-parse", "HEAD"])
    dirty = _run(["git", "status", "--porcelain"]) != ""
    remote = _run(["git", "remote", "get-url", "origin"])

    return {
        "branch": branch or None,
        "commit": commit or None,
        "dirty": dirty,
        "remote_url": remote or None,
    }


app = create_app()
