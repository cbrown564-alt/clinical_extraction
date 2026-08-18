"""Discover governed Gan validation750 artifacts for the trace explorer.

Hybrid (`llm_with_rules`) cells prefer a current-stack no-call replay tree
when `hybrid_artifact_root` is set. Those `dev750` forests were retired in
the 16 Aug living-stack freeze, so workbench cells stay visible as
`not_retained`. Nested leftover scratch paths are still accepted if a
config points there. Partial conditions remain visible as progress
metadata but their rows are never served.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.paper.gan_panel import load_dev750_panel
from clinical_extraction.paper.roster import living_models

TRACE_SCHEMA_VERSION = "gan2026.row_trace.v1"


@dataclass(frozen=True)
class ModelCondition:
    slug: str
    route: str
    label: str


MODEL_CONDITIONS = (
    ModelCondition("gpt56luna", "openai/gpt-5.6-luna", "GPT-5.6 Luna"),
    ModelCondition("gemini37flash", "gemini/gemini-3.7-flash", "Gemini 3.7 Flash"),
    ModelCondition("gpt56sol", "openai/gpt-5.6-sol", "GPT-5.6 Sol"),
    ModelCondition(
        "deepseek_v4_flash",
        "deepseek/deepseek-v4-flash",
        "DeepSeek V4 Flash",
    ),
    ModelCondition("qwen36_35b", "ollama_chat/qwen3.6:35b", "Qwen 3.6:35B"),
    ModelCondition("gemma4_26b", "ollama_chat/gemma4:26b", "Gemma 4 26B"),
)


@dataclass(frozen=True)
class GanValidationDiscovery:
    catalog: dict[str, Any]
    registry_entries: tuple[dict[str, Any], ...]
    replay_artifacts: dict[str, Path]


def discover_gan2026_validation_runs(
    config_path: Path,
    *,
    expected_indices: set[int],
) -> GanValidationDiscovery:
    """Build the selector and replay allowlist from exact validation750 outputs."""

    config = _object(config_path)
    repo_root = config_path.parent.parent.parent
    artifact_root = repo_root / str(config["artifact_root"])
    hybrid_root = (
        repo_root / str(config["hybrid_artifact_root"])
        if config.get("hybrid_artifact_root")
        else None
    )
    configured = {str(item["slug"]): item for item in config["conditions"]}
    methods = {str(item["method"]): item for item in config["methods"]}
    families: list[dict[str, Any]] = []
    registry: list[dict[str, Any]] = []
    artifacts: dict[str, Path] = {}

    for method_name in ("llm_with_rules", "llm_only"):
        method = methods[method_name]
        for condition in MODEL_CONDITIONS:
            configured_condition = configured[condition.slug]
            if configured_condition["model"] != condition.route:
                raise ValueError(f"configured model mismatch for {condition.slug}")
            path = _condition_rows_path(
                artifact_root,
                condition.slug,
                method_name,
                hybrid_root=hybrid_root,
            )
            inspection = _inspect_rows(
                path,
                expected_indices=expected_indices,
                method=method_name,
            )
            family = _model_family(
                condition,
                method_name=method_name,
                prompt_version=str(method["prompt_version"]),
                repair_mode=str(method["repair_mode"]),
                inspection=inspection,
            )
            families.append(family)
            if not inspection["complete"]:
                continue
            run_id = str(family["run_id"])
            artifacts[run_id] = path.resolve()
            registry.append(
                {
                    "run_id": run_id,
                    "artifact_paths": [
                        path.relative_to(config_path.parent.parent.parent).as_posix()
                    ],
                    "date": (
                        "2026-08-13" if method_name == "llm_with_rules" else "2026-07-19"
                    ),
                    "decision": "development_comparison",
                    "mode": "replay",
                    "model": condition.route,
                    "model_role": family["display_label"],
                    "pipeline_family": family["pipeline_family"],
                    "primary_metrics": family["metrics"],
                    "repair_mode": method["repair_mode"],
                    "replay_status": "native_validation_run",
                    "row_count": 750,
                    "split": "validation",
                    "registry_roles": ["six_model_validation_comparison"],
                    "evidence_validity": (
                        "Row-level Gan validation development evidence; not holdout evidence."
                    ),
                }
            )

    families.append(_rules_only_family())
    _overlay_paper_dev750(repo_root, families, registry, artifacts)
    return GanValidationDiscovery(
        catalog={
            "generated_on": "2026-08-13",
            "source_artifact": config["protocol"],
            "claim_boundary": (
                "Gan validation750 is inspectable development evidence. Hybrid cells "
                "are the 13 Aug current-stack no-call replay; LLM-only cells are the "
                "July 18 comparison tree. Only exact, trace-valid 750-row conditions "
                "are replayable; test450 is excluded."
            ),
            "families": families,
        },
        registry_entries=tuple(registry),
        replay_artifacts=artifacts,
    )


def paper_run_id(method: str, slug: str) -> str:
    """Workbench run id for a living paper Gan cell."""

    suffix = "llm_with_rules" if method == "gan_llm_with_rules" else "llm_only"
    return f"gan2026_validation750_{slug}_{suffix}"


def paper_identity_from_run_id(run_id: str) -> tuple[str, str] | None:
    """Return (paper method, model slug) for a workbench Gan run id."""

    prefix = "gan2026_validation750_"
    if not run_id.startswith(prefix):
        return None
    rest = run_id[len(prefix) :]
    if rest.endswith("_llm_with_rules"):
        return "gan_llm_with_rules", rest[: -len("_llm_with_rules")]
    if rest.endswith("_llm_only"):
        return "gan_llm_only", rest[: -len("_llm_only")]
    return None


def _overlay_paper_dev750(
    repo_root: Path,
    families: list[dict[str, Any]],
    registry: list[dict[str, Any]],
    artifacts: dict[str, Path],
) -> None:
    """Prefer tracked paper_experiments rows for living development cells."""

    panel = load_dev750_panel()
    by_run = {str(family["run_id"]): family for family in families}
    models = {item["slug"]: item for item in living_models()}
    for cell in panel.get("cells", []):
        if not isinstance(cell, dict) or cell.get("status") != "present":
            continue
        method = str(cell["method"])
        slug = str(cell["model_slug"])
        rows_path = repo_root / str(cell["rows"])
        if not rows_path.is_file():
            continue
        row_count = int(cell.get("n") or 750)
        purist_correct = int(cell.get("purist_correct") or 0)
        purist_accuracy = float(cell.get("purist_accuracy") or 0.0)
        inspection = {
            "complete": True,
            "row_count": row_count,
            "metrics": {
                "row_count": row_count,
                "purist_correct": purist_correct,
                "purist_accuracy": purist_accuracy,
                "pragmatic_correct": 0,
                "pragmatic_accuracy": 0.0,
            },
        }
        run_id = paper_run_id(method, slug)
        artifacts[run_id] = rows_path.resolve()
        model = models.get(slug, {})
        family = _paper_family(cell, model, inspection)
        existing = by_run.get(run_id)
        if existing is None:
            families.insert(-1, family)
        else:
            families[families.index(existing)] = family
        by_run[run_id] = family
        registry[:] = [item for item in registry if item["run_id"] != run_id]
        registry.append(
            {
                "run_id": run_id,
                "artifact_paths": [rows_path.relative_to(repo_root).as_posix()],
                "date": "2026-08-18",
                "decision": "development_comparison",
                "mode": "replay",
                "model": cell.get("model") or model.get("model"),
                "model_role": family["display_label"],
                "pipeline_family": family["pipeline_family"],
                "primary_metrics": family["metrics"],
                "repair_mode": family["repair_mode"],
                "replay_status": "paper_dev750_raw_replay",
                "row_count": 750,
                "split": "validation",
                "registry_roles": ["paper_dev750_panel"],
                "evidence_validity": (
                    "Row-level Gan validation development evidence; not holdout evidence."
                ),
            }
        )


def _paper_family(
    cell: dict[str, Any],
    model: dict[str, Any],
    inspection: dict[str, Any],
) -> dict[str, Any]:
    method = str(cell["method"])
    slug = str(cell["model_slug"])
    method_name = "llm_with_rules" if method == "gan_llm_with_rules" else "llm_only"
    condition = ModelCondition(
        slug,
        str(cell.get("model") or model.get("model") or ""),
        str(cell.get("label") or model.get("label") or slug),
    )
    return _model_family(
        condition,
        method_name=method_name,
        prompt_version=(
            "gan2026_hybrid_structured_events_v0.7"
            if method_name == "llm_with_rules"
            else "gan2026_llm_only_canonical_pipeline_v0.8"
        ),
        repair_mode=(
            "hybrid_full_stack"
            if method_name == "llm_with_rules"
            else "model_selected_evidence_benchmark_adapter"
        ),
        inspection=inspection,
    )


def _condition_rows_path(
    artifact_root: Path,
    slug: str,
    method_name: str,
    *,
    hybrid_root: Path | None = None,
) -> Path:
    """Resolve a cell under the current-stack hybrid tree or the July 18 tree."""

    roots: list[Path] = []
    if method_name == "llm_with_rules" and hybrid_root is not None:
        roots.append(hybrid_root)
    roots.append(artifact_root)
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(
            (
                root / slug / "validation750.rows.jsonl",
                root / slug / method_name / "validation750.rows.jsonl",
                root / f"{slug}--{method_name}.jsonl",
            )
        )
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]


def _inspect_rows(
    path: Path,
    *,
    expected_indices: set[int],
    method: str,
) -> dict[str, Any]:
    if not path.is_file():
        return {"complete": False, "row_count": 0}
    row_count = 0
    indices: list[int] = []
    trace_count = 0
    purist_correct = 0
    pragmatic_correct = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                return {"complete": False, "row_count": row_count}
            if not isinstance(value, dict):
                return {"complete": False, "row_count": row_count}
            row_count += 1
            try:
                indices.append(int(value["source_row_index"]))
            except (KeyError, TypeError, ValueError):
                return {"complete": False, "row_count": row_count}
            trace = value.get("row_trace") or {}
            trace_count += int(
                trace.get("schema_version") == TRACE_SCHEMA_VERSION
                and trace.get("method") == method
                and value.get("split") == "validation"
                and value.get("split_manifest") == "gan2026_split_v1"
            )
            comparison = value.get("comparison") or {}
            purist_correct += int(bool(comparison.get("purist_correct")))
            pragmatic_correct += int(bool(comparison.get("pragmatic_correct")))
    unique_indices = set(indices)
    complete = (
        row_count == len(expected_indices)
        and len(unique_indices) == len(expected_indices)
        and unique_indices == expected_indices
        and trace_count == row_count
    )
    result: dict[str, Any] = {"complete": complete, "row_count": row_count}
    if complete:
        result["metrics"] = {
            "row_count": row_count,
            "purist_correct": purist_correct,
            "purist_accuracy": round(purist_correct / row_count, 4),
            "pragmatic_correct": pragmatic_correct,
            "pragmatic_accuracy": round(pragmatic_correct / row_count, 4),
        }
    return result


def _model_family(
    condition: ModelCondition,
    *,
    method_name: Literal["llm_with_rules", "llm_only"],
    prompt_version: str,
    repair_mode: str,
    inspection: dict[str, Any],
) -> dict[str, Any]:
    active_method = "llm_with_rules" if method_name == "llm_with_rules" else "llm"
    kind = active_method
    run_id = f"gan2026_validation750_{condition.slug}_{method_name}"
    complete = bool(inspection["complete"])
    mode_label = "LLM + rules" if method_name == "llm_with_rules" else "LLM only"
    status_label = mode_label if complete else "in progress"
    result: dict[str, Any] = {
        "value": run_id,
        "run_id": run_id,
        "label": condition.label,
        "display_label": f"{condition.label} · {status_label}",
        "model_label": condition.label,
        "executable": False,
        "kind": kind,
        "active_method": active_method,
        "architecture_family": active_method,
        "pipeline_family": active_method,
        "model": condition.route,
        "comparison_role": "winner" if method_name == "llm_with_rules" else "diagnostic",
        "availability": "replay" if complete else "not_retained",
        "evidence_scope": "validation750_row_level" if complete else "incomplete_not_served",
        "has_replay_artifact": complete,
        "split": "validation750",
        "prompt_version": prompt_version,
        "repair_mode": repair_mode,
        "run_count": 1 if complete else 0,
        "progress": {"completed_rows": inspection["row_count"], "expected_rows": 750},
    }
    if complete:
        result["metrics"] = inspection["metrics"]
    else:
        result["unavailable_reason"] = (
            "This condition is incomplete; partial validation rows are not served."
        )
    return result


def _rules_only_family() -> dict[str, Any]:
    return {
        "value": "rules",
        "run_id": "rules",
        "saved_run_id": "rules_only",
        "label": "Deterministic canonical",
        "display_label": "Deterministic canonical",
        "model_label": "No model",
        "executable": True,
        "kind": "rules",
        "architecture_family": "rules",
        "pipeline_family": "rules",
        "model": "(model-independent)",
        "comparison_role": "control",
        "availability": "live",
        "evidence_scope": "validation_rows",
        "has_replay_artifact": False,
        "split": "validation",
        "prompt_version": "deterministic",
        "repair_mode": "deterministic_v1",
        "run_count": 1,
    }


def _object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value
