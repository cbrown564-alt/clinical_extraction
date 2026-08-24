"""Discover governed Gan validation750 artifacts for the trace explorer.

The workbench catalog is the living six-model roster. Present cells prefer
tracked ``paper_experiments`` rows. July 18 and 13 Aug leftover trees are
used only when a living slug still has a matching config path and no paper
cell. Historical Sol and Qwen 3.6 are not catalog rows. Partial living
conditions stay visible as ``not_retained``; their rows are never served.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.paper.roster import living_models

TRACE_SCHEMA_VERSION = "gan2026.row_trace.v1"


@dataclass(frozen=True)
class ModelCondition:
    slug: str
    route: str
    label: str


def living_model_conditions() -> tuple[ModelCondition, ...]:
    """Return the living paper roster as workbench model conditions."""

    return tuple(
        ModelCondition(str(item["slug"]), str(item["model"]), str(item["label"]))
        for item in living_models()
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

    for config_method in ("llm_with_rules", "llm_only"):
        pipeline_method: Literal["llm_with_rules", "llm"] = (
            "llm_with_rules" if config_method == "llm_with_rules" else "llm"
        )
        method = methods[config_method]
        for condition in living_model_conditions():
            configured_condition = configured.get(condition.slug)
            if (
                configured_condition is not None
                and configured_condition["model"] != condition.route
            ):
                raise ValueError(f"configured model mismatch for {condition.slug}")
            path = (
                _condition_rows_path(
                    artifact_root,
                    condition.slug,
                    pipeline_method,
                    hybrid_root=hybrid_root,
                )
                if configured_condition is not None
                else artifact_root / "_missing" / f"{condition.slug}--{pipeline_method}.jsonl"
            )
            inspection = _inspect_rows(
                path,
                expected_indices=expected_indices,
                method=pipeline_method,
            )
            family = _model_family(
                condition,
                run_suffix=config_method,
                pipeline_method=pipeline_method,
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
                        "2026-08-13" if config_method == "llm_with_rules" else "2026-07-19"
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
    _overlay_paper_five_cell(repo_root, families, registry, artifacts)
    return GanValidationDiscovery(
        catalog={
            "generated_on": "2026-08-19",
            "source_artifact": config["protocol"],
            "claim_boundary": (
                "Living six-model Gan development panel. Present cells prefer "
                "paper_experiments; pending living models stay visible as "
                "not_retained. Historical Sol and Qwen 3.6 are not catalog rows. "
                "Only exact, trace-valid 750-row conditions are replayable; "
                "test450 is excluded."
            ),
            "families": families,
        },
        registry_entries=tuple(registry),
        replay_artifacts=artifacts,
    )


_RUN_ID_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("_llm_with_rules", "gan_llm_extract_raw"),
    ("_llm_select", "gan_llm_select_from_extract"),
    ("_llm_extract", "gan_llm_extract"),
    ("_llm_encode", "gan_llm_encode"),
    ("_llm_only", "gan_llm_only"),
    ("_rules", "gan_rules"),
)

_RUN_ID_METHOD_SUFFIX: dict[str, str] = {
    "gan_llm_extract_raw": "llm_with_rules",
    "gan_llm_only": "llm_only",
    "gan_llm_extract": "llm_extract",
    "llm_extract": "llm_extract",
    "gan_llm_encode": "llm_encode",
    "llm_encode": "llm_encode",
    "gan_llm_select_from_extract": "llm_select",
    "llm_select": "llm_select",
    "gan_rules": "rules",
    "rules_only": "rules",
}


def paper_run_id(method: str, slug: str) -> str:
    """Workbench run id for a living paper Gan cell."""

    suffix = _RUN_ID_METHOD_SUFFIX.get(method)
    if suffix is None:
        suffix = "llm_with_rules" if method == "gan_llm_extract_raw" else "llm_only"
    return f"gan2026_validation750_{slug}_{suffix}"


def paper_identity_from_run_id(run_id: str) -> tuple[str, str] | None:
    """Return (paper method, model slug) for a workbench Gan run id."""

    prefix = "gan2026_validation750_"
    if not run_id.startswith(prefix):
        return None
    rest = run_id[len(prefix) :]
    for suffix, method in _RUN_ID_SUFFIXES:
        if rest.endswith(suffix):
            return method, rest[: -len(suffix)]
    return None


def _overlay_paper_dev750(
    repo_root: Path,
    families: list[dict[str, Any]],
    registry: list[dict[str, Any]],
    artifacts: dict[str, Path],
) -> None:
    """Prefer tracked paper_experiments rows for living development cells."""

    by_run = {str(family["run_id"]): family for family in families}
    models = {item["slug"]: item for item in living_models()}
    paper_gan = repo_root / "paper_experiments" / "gan"
    for model in living_models():
        slug = str(model["slug"])
        for method in ("gan_llm_only", "gan_llm_extract_raw"):
            dest = paper_gan / method / slug / "dev750"
            rows_path = dest / "rows.jsonl"
            comparison_path = dest / "comparison.json"
            if not rows_path.is_file() or not comparison_path.is_file():
                continue
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            summary = comparison.get("summary") or {}
            cell = {
                "method": method,
                "model_slug": slug,
                "model": model["model"],
                "label": model["label"],
                "n": 750,
                "purist_correct": summary.get("purist_correct"),
                "purist_accuracy": summary.get("purist_accuracy"),
            }
            row_count = 750
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
            roster_model = models.get(slug, {})
            family = _paper_family(cell, roster_model, inspection)
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
                    "model": cell.get("model") or roster_model.get("model"),
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


_PANEL_CELL_METHODS = frozenset(
    {"llm_extract", "llm_encode", "llm_select", "llm_pre_post"}
)
_PANEL_REPAIR_MODE = {
    "llm_extract": "raw_model",
    "llm_encode": "llm_encode",
    "llm_select": "llm_select",
    "llm_pre_post": "llm_select",
}


def _overlay_paper_five_cell(
    repo_root: Path,
    families: list[dict[str, Any]],
    registry: list[dict[str, Any]],
    artifacts: dict[str, Path],
) -> None:
    """Serve living five-cell rows from the shared extract raw."""

    panel_path = repo_root / "paper_experiments" / "gan" / "dev750_panel.json"
    if not panel_path.is_file():
        return
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    cells = panel.get("cells")
    if not isinstance(cells, list):
        return
    models = {item["slug"]: item for item in living_models()}
    by_run = {str(family["run_id"]): family for family in families}
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        method = str(cell.get("method") or "")
        if method not in _PANEL_CELL_METHODS:
            continue
        slug = str(cell.get("model_slug") or "")
        roster = models.get(slug, {})
        raw_name = str(cell.get("shared_raw_output") or "gan_llm_extract_raw")
        rows_path = (
            repo_root / "paper_experiments" / "gan" / raw_name / slug / "dev750" / "rows.jsonl"
        )
        present = cell.get("status") == "present" and rows_path.is_file()
        run_id = paper_run_id(method, slug)
        row_count = int(cell.get("n") or 0)
        purist_correct = int(cell.get("purist_correct") or 0)
        purist_accuracy = float(cell.get("purist_accuracy") or 0.0)
        inspection = {
            "complete": present,
            "row_count": row_count if present else 0,
            "metrics": {
                "row_count": row_count,
                "purist_correct": purist_correct,
                "purist_accuracy": purist_accuracy,
                "pragmatic_correct": 0,
                "pragmatic_accuracy": 0.0,
            },
        }
        condition = ModelCondition(
            slug,
            str(cell.get("model") or roster.get("model") or ""),
            str(cell.get("label") or roster.get("label") or slug),
        )
        family = _model_family(
            condition,
            run_suffix=_RUN_ID_METHOD_SUFFIX[method],
            pipeline_method="llm_with_rules",
            prompt_version=raw_name,
            repair_mode=_PANEL_REPAIR_MODE[method],
            inspection=inspection,
            paper_cell=method,
        )
        existing = by_run.get(run_id)
        if existing is None:
            families.insert(-1, family)
        else:
            families[families.index(existing)] = family
        by_run[run_id] = family
        if not present:
            continue
        artifacts[run_id] = rows_path.resolve()
        registry[:] = [item for item in registry if item["run_id"] != run_id]
        registry.append(
            {
                "run_id": run_id,
                "artifact_paths": [rows_path.relative_to(repo_root).as_posix()],
                "date": "2026-08-23",
                "decision": "development_comparison",
                "mode": "replay",
                "model": condition.route,
                "model_role": family["display_label"],
                "pipeline_family": family["pipeline_family"],
                "primary_metrics": family["metrics"],
                "repair_mode": family["repair_mode"],
                "replay_status": "paper_dev750_five_cell_replay",
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
    method_name: Literal["llm_with_rules", "llm"] = (
        "llm_with_rules" if method == "gan_llm_extract_raw" else "llm"
    )
    condition = ModelCondition(
        slug,
        str(cell.get("model") or model.get("model") or ""),
        str(cell.get("label") or model.get("label") or slug),
    )
    return _model_family(
        condition,
        run_suffix="llm_with_rules" if method_name == "llm_with_rules" else "llm_only",
        pipeline_method=method_name,
        prompt_version=(
            "gan_llm_extract_raw"
            if method_name == "llm_with_rules"
            else "gan_llm_only"
        ),
        repair_mode=(
            "llm_select"
            if method_name == "llm_with_rules"
            else "model_selected_evidence_benchmark_adapter"
        ),
        inspection=inspection,
    )


def _condition_rows_path(
    artifact_root: Path,
    slug: str,
    method_name: Literal["llm_with_rules", "llm"],
    *,
    hybrid_root: Path | None = None,
) -> Path:
    """Resolve a cell under the current-stack hybrid tree or the July 18 tree."""

    roots: list[Path] = []
    if method_name == "llm_with_rules" and hybrid_root is not None:
        roots.append(hybrid_root)
    roots.append(artifact_root)
    method_suffixes: list[str] = [method_name]
    if method_name == "llm":
        method_suffixes.append("llm_only")
    candidates: list[Path] = []
    for root in roots:
        for suffix in method_suffixes:
            candidates.extend(
                (
                    root / slug / "validation750.rows.jsonl",
                    root / slug / suffix / "validation750.rows.jsonl",
                    root / f"{slug}--{suffix}.jsonl",
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
    method: Literal["llm_with_rules", "llm"],
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
    run_suffix: str,
    pipeline_method: Literal["llm_with_rules", "llm"],
    prompt_version: str,
    repair_mode: str,
    inspection: dict[str, Any],
    paper_cell: str | None = None,
) -> dict[str, Any]:
    active_method = "llm_with_rules" if pipeline_method == "llm_with_rules" else "llm"
    kind = active_method
    run_id = f"gan2026_validation750_{condition.slug}_{run_suffix}"
    complete = bool(inspection["complete"])
    mode_label = "LLM + rules" if pipeline_method == "llm_with_rules" else "LLM only"
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
        "comparison_role": "winner" if pipeline_method == "llm_with_rules" else "diagnostic",
        "availability": "replay" if complete else "not_retained",
        "evidence_scope": "validation750_row_level" if complete else "incomplete_not_served",
        "has_replay_artifact": complete,
        "split": "validation750",
        "prompt_version": prompt_version,
        "repair_mode": repair_mode,
        "run_count": 1 if complete else 0,
        "progress": {"completed_rows": inspection["row_count"], "expected_rows": 750},
    }
    if paper_cell is not None:
        result["paper_cell"] = paper_cell
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
        "saved_run_id": "rules",
        "label": "Deterministic canonical",
        "display_label": "Deterministic canonical",
        "model_label": "No model",
        "executable": True,
        "kind": "rules",
        "paper_cell": "rules_only",
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
