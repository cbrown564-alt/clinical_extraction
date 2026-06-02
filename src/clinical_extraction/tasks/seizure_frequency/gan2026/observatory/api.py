"""Thin FastAPI wrapper for Gan 2026 Observatory data and pipelines."""

from __future__ import annotations

import importlib
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

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

PipelineFamily = Literal[
    "rules_only",
    "deterministic_v1",
    "llm_only_claim_table_selector",
    "llm_only_direct_labeler",
    "llm_only_structured_events",
    "hybrid_rules_candidates_llm_adjudicator",
]
TEMPORAL_SELECTION_RULES = temporal_selection.TEMPORAL_SELECTION_RULES

PROMPT_MODULES = (
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_claim_table_selector",
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler",
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_structured_events",
    "clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.hybrid_rules_candidates_llm_adjudicator",
)

# Families that can actually be executed via /run/note and /run/ablation
EXECUTABLE_PIPELINES: set[str] = {"rules_only", "deterministic_v1"}


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
        summary="Thin backend over Gan 2026 clinical-extraction pipelines and artifacts.",
    )
    app.state.observatory_settings = settings

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

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
        selected_path = _select_artifact_path(
            entry.to_json_record()["artifact_paths"],
            artifact_path,
        )
        resolved = _safe_repo_path(settings.repo_root, selected_path)
        if not resolved.exists():
            raise HTTPException(status_code=404, detail=f"Artifact not found: {selected_path}")
        content = _load_artifact_content(resolved, limit=limit)
        return {
            "run_id": run_id,
            "artifact_path": selected_path,
            "artifact_type": resolved.suffix.lstrip(".") or "text",
            "content": content,
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
        families: list[dict[str, Any]] = [
            {
                "value": "rules_only",
                "label": "Deterministic V1",
                "executable": True,
                "kind": "rules_only",
            },
            {
                "value": "deterministic_v1",
                "label": "Deterministic V1 (alias)",
                "executable": True,
                "kind": "rules_only",
            },
        ]
        for module_name in PROMPT_MODULES:
            families.append(_llm_family_payload(module_name))
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

    return app


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


def _select_artifact_path(paths: Sequence[str], requested: str | None) -> str:
    if requested is not None:
        if requested not in paths:
            raise HTTPException(
                status_code=404,
                detail=f"Run does not reference artifact: {requested}",
            )
        return requested
    for path in paths:
        if Path(path).suffix in {".jsonl", ".json"}:
            return path
    return paths[0]


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


def _jsonable_mapping_sequence(items: Iterable[Any]) -> list[dict[str, Any]]:
    payload = []
    for item in items:
        if isinstance(item, Mapping):
            payload.append({str(key): value for key, value in item.items()})
    return payload


app = create_app()
