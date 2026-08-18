"""Promote living ExECT Compact dev140 cells into the tracked paper tree."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import compact_metrics_from_structured
from clinical_extraction.paper.methods import (
    exect_row_count,
    holdout_is_aggregate_only,
    method_spec,
    split_for,
)
from clinical_extraction.paper.roster import living_models, model_by_slug
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
WORK_ROOT = ROOT / "experiments/paper/exect_llm_with_rules"
HOLDOUT_ROOT = ROOT / "scratch/holdout/paper/exect_llm_with_rules"
PAPER_EXECT = ROOT / "paper_experiments/exect"
PANEL_PATH = PAPER_EXECT / "dev140_panel.json"
INVENTORY_PATH = ROOT / "paper_experiments/inventory.json"
REPLAY_FIELDS = ("letter_id", "prompt_version", "raw_output")
METHOD = "exect_llm_with_rules"
PROMOTE_SPLIT = "dev140"
HOLDOUT_FORBIDDEN = ("letter_ids", "changed_rows")


def living_work_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the living (non-remasure) Compact sidecar."""

    root = HOLDOUT_ROOT if holdout_is_aggregate_only(split) else WORK_ROOT
    return root / slug / split


def paper_cell_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the tracked paper directory for a Compact cell."""

    return PAPER_EXECT / METHOD / slug / split


def promote_exect_dev140(slug: str) -> dict[str, Any]:
    """Copy a finished living-effort Compact dev140 cell into paper_experiments."""

    return promote_exect(slug, PROMOTE_SPLIT)


def promote_exect(slug: str, split: str) -> dict[str, Any]:
    """Copy a finished living-effort Compact cell into paper_experiments."""

    spec = method_spec(METHOD)
    if spec["task"] != "exectv2":
        raise RuntimeError("promote-exect is ExECT only")
    split_for(METHOD, split)
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    source = living_work_root(slug, split)
    structured_path = _sidecar_structured_path(source)
    comparison_path = source / "comparison.json"
    if structured_path is None or not comparison_path.is_file():
        raise RuntimeError(f"missing living {METHOD} {slug} {split} sidecar")
    rows = load_jsonl_rows(structured_path)
    expected = exect_row_count(split)
    if len(rows) != expected:
        raise RuntimeError(f"{structured_path} has {len(rows)} rows, expected {expected}")
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if comparison.get("split") != split:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    if comparison.get("reasoning_effort") not in {None, "low"}:
        raise RuntimeError("promote only the living low-effort cell, not a remasure")
    if holdout:
        _assert_aggregate_only(comparison)
    dest = paper_cell_root(slug, split)
    dest.mkdir(parents=True, exist_ok=True)
    replay, empty = _public_replay(rows)
    write_jsonl_rows(replay, dest / "structured.jsonl")
    (dest / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    arm = _compact_arm(comparison)
    cell = {
        "model_slug": slug,
        "model": model["model"],
        "method": METHOD,
        "program": "exectv2_compact_ledger",
        "split": split,
        "split_machine": "test" if holdout else "dev",
        "n": expected,
        "row_count": expected,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "id_field": "letter_id",
        "replay_fields": list(REPLAY_FIELDS),
        "empty_raw_count": empty,
        "source": source.relative_to(ROOT).as_posix(),
        "living_effort": _living_effort(slug),
        "rows": "structured.jsonl",
        "comparison": "comparison.json",
        "raw_headline_f1": arm.get("raw_headline_f1"),
        "hybrid_headline_f1": arm.get("hybrid_headline_f1"),
    }
    if not holdout:
        metrics_path = _sidecar_metrics_path(source)
        if metrics_path is not None:
            metrics = load_jsonl_rows(metrics_path)
        else:
            metrics = compact_metrics_from_structured(slug, dest / "structured.jsonl")
        scored = _public_scored(metrics)
        if len(scored) != expected:
            raise RuntimeError(f"{slug} scored {len(scored)} letters, expected {expected}")
        write_jsonl_rows(scored, dest / "scored.jsonl")
        cell["scored"] = "scored.jsonl"
    (dest / "cell.json").write_text(
        json.dumps(cell, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if holdout:
        _upsert_present(
            {
                "model_slug": slug,
                "model": model["model"],
                "method": METHOD,
                "replay_alias": "exectv2_compact_ledger",
                "split": split,
                "n": expected,
                "row_policy": "aggregate_only",
                "path": (dest / "structured.jsonl").relative_to(ROOT).as_posix(),
                "status": "present",
                "empty_raw_count": empty,
            }
        )
        return {"cell": cell}
    panel = rebuild_dev140_panel()
    return {
        "cell": cell,
        "panel": PANEL_PATH.relative_to(ROOT).as_posix(),
        "cells": panel["cells"],
    }


def ensure_exect_dev140_scored(slug: str) -> Path:
    """Write frontend-joinable scored rows for an already-tracked Compact cell."""

    dest = paper_cell_root(slug)
    scored_path = dest / "scored.jsonl"
    if scored_path.is_file():
        return scored_path
    structured_path = dest / "structured.jsonl"
    if not structured_path.is_file():
        raise RuntimeError(f"missing tracked {METHOD} {slug} {PROMOTE_SPLIT} structured")
    metrics = compact_metrics_from_structured(slug, structured_path)
    write_jsonl_rows(_public_scored(metrics), scored_path)
    if not (dest / "cell.json").is_file():
        comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
        arm = _compact_arm(comparison)
        model = model_by_slug(slug)
        empty = sum(
            1
            for row in load_jsonl_rows(structured_path)
            if not str(row.get("raw_output") or "").strip()
        )
        cell = {
            "model_slug": slug,
            "model": model["model"],
            "method": METHOD,
            "program": "exectv2_compact_ledger",
            "split": PROMOTE_SPLIT,
            "n": exect_row_count(PROMOTE_SPLIT),
            "row_policy": "development_review_permitted",
            "empty_raw_count": empty,
            "living_effort": _living_effort(slug),
            "raw_headline_f1": arm.get("raw_headline_f1"),
            "hybrid_headline_f1": arm.get("hybrid_headline_f1"),
        }
        (dest / "cell.json").write_text(
            json.dumps(cell, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return scored_path


def rebuild_dev140_panel() -> dict[str, Any]:
    """Write the rectangular living ExECT Compact dev140 index."""

    cells: list[dict[str, Any]] = []
    for model in living_models():
        slug = str(model["slug"])
        dest = paper_cell_root(slug)
        structured_path = dest / "structured.jsonl"
        comparison_path = dest / "comparison.json"
        cell_path = dest / "cell.json"
        scored_path = dest / "scored.jsonl"
        if structured_path.is_file() and comparison_path.is_file():
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            arm = _compact_arm(comparison)
            extra = (
                json.loads(cell_path.read_text(encoding="utf-8"))
                if cell_path.is_file()
                else {}
            )
            cells.append(
                {
                    "model_slug": slug,
                    "model": model["model"],
                    "label": model["label"],
                    "method": METHOD,
                    "status": "present",
                    "path": dest.relative_to(ROOT).as_posix() + "/",
                    "rows": structured_path.relative_to(ROOT).as_posix(),
                    "scored": scored_path.relative_to(ROOT).as_posix()
                    if scored_path.is_file()
                    else None,
                    "comparison": comparison_path.relative_to(ROOT).as_posix(),
                    "n": exect_row_count(PROMOTE_SPLIT),
                    "raw_headline_f1": arm.get("raw_headline_f1"),
                    "hybrid_headline_f1": arm.get("hybrid_headline_f1"),
                    "living_effort": extra.get("living_effort") or _living_effort(slug),
                }
            )
        else:
            cells.append(
                {
                    "model_slug": slug,
                    "model": model["model"],
                    "label": model["label"],
                    "method": METHOD,
                    "status": "pending",
                    "path": dest.relative_to(ROOT).as_posix() + "/",
                    "n": exect_row_count(PROMOTE_SPLIT),
                }
            )
    panel = {
        "schema_version": "paper_experiments.exect.dev140_panel.v1",
        "split": PROMOTE_SPLIT,
        "split_machine": "dev",
        "row_policy": "development_review_permitted",
        "method_identity": "grok46",
        "living_effort": {
            "hosted_reasoning": "low",
            "deepseek": "thinking_on_provider_default",
            "local": "none",
        },
        "notes_source": {
            "split_machine": "dev",
            "frontend": "/datasets/exectv2/letters",
        },
        "methods": [METHOD],
        "models": [item["slug"] for item in living_models()],
        "cells": cells,
        "claim_boundary": (
            "Living six-model ExECT Compact development panel. One Compact "
            "call is both raw and hybrid. Remasures stay under "
            "experiments/paper/.../reasoning_* or thinking_disabled/. Not holdout. "
            "The July explorer runs.json roster is historical."
        ),
    }
    PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    PANEL_PATH.write_text(
        json.dumps(panel, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _sync_inventory(panel)
    return panel


def load_dev140_panel() -> dict[str, Any]:
    """Return the living ExECT Compact dev140 panel, rebuilding it if needed."""

    if not PANEL_PATH.is_file():
        return rebuild_dev140_panel()
    return json.loads(PANEL_PATH.read_text(encoding="utf-8"))


def paper_exect_run_id(slug: str, lane: Literal["llm", "llm_with_rules"]) -> str:
    """Workbench run id for a living Compact cell."""

    suffix = "llm_plus_rules" if lane == "llm_with_rules" else "llm_only"
    return f"exectv2_dev140_{slug}_{suffix}"


def paper_exect_identity(run_id: str) -> tuple[str, Literal["llm", "llm_with_rules"]] | None:
    """Return (model slug, lane) for a living Compact workbench run id."""

    prefix = "exectv2_dev140_"
    if not run_id.startswith(prefix):
        return None
    rest = run_id[len(prefix) :]
    if rest.endswith("_llm_plus_rules"):
        return rest[: -len("_llm_plus_rules")], "llm_with_rules"
    if rest.endswith("_llm_only"):
        return rest[: -len("_llm_only")], "llm"
    return None


def paper_exect_catalog_runs() -> list[dict[str, Any]]:
    """Present living Compact cells as workbench raw and hybrid runs."""

    panel = load_dev140_panel()
    runs: list[dict[str, Any]] = []
    for cell in panel.get("cells", []):
        if not isinstance(cell, dict) or cell.get("status") != "present":
            continue
        rows_path = ROOT / str(cell["rows"])
        if not rows_path.is_file():
            continue
        slug = str(cell["model_slug"])
        label = str(cell.get("label") or slug)
        model = str(cell["model"])
        for lane, score, kind, view in (
            (
                "llm_with_rules",
                cell.get("hybrid_headline_f1"),
                "llm_with_rules",
                "headline_target",
            ),
            ("llm", cell.get("raw_headline_f1"), "llm", "raw_lane_score"),
        ):
            runs.append(
                {
                    "run_id": paper_exect_run_id(slug, lane),
                    "task": "exectv2",
                    "label": (
                        f"{label} · LLM + rules"
                        if lane == "llm_with_rules"
                        else f"{label} · LLM only"
                    ),
                    "model": model,
                    "kind": kind,
                    "active_method": lane,
                    "method_id": lane,
                    "architecture_family": "exect_llm_with_rules",
                    "pipeline_family": (
                        "exect_llm_with_rules" if lane == "llm_with_rules" else "llm"
                    ),
                    "split": "dev140",
                    "row_count": int(cell.get("n") or 140),
                    "date": "2026-08-18",
                    "decision": "development_comparison",
                    "promotion_decision": "living Compact panel",
                    "claim_boundary": panel.get("claim_boundary"),
                    "scorer_view": view,
                    "artifact_paths": [rows_path.relative_to(ROOT).as_posix()],
                    "source_paths": [rows_path.relative_to(ROOT).as_posix()],
                    "metrics": {
                        "overall_f1": score,
                        "precision": None,
                        "recall": None,
                        "families": {},
                    },
                    "operational": {
                        "call_failures": 0,
                        "parse_schema_failures": 0,
                        "evidence_invalid_dropped": 0,
                        "exact_evidence_rate": None,
                        "by_family": {},
                    },
                    "letters": [],
                }
            )
    return runs


def load_scored_rows(slug: str) -> list[dict[str, Any]]:
    """Return frontend-joinable scored rows for one present Compact cell."""

    model_by_slug(slug)
    path = paper_cell_root(slug) / "scored.jsonl"
    if not path.is_file():
        raise FileNotFoundError(path)
    return load_jsonl_rows(path)


def _assert_aggregate_only(comparison: Mapping[str, Any]) -> None:
    if comparison.get("row_policy") != "aggregate_only":
        raise RuntimeError("holdout comparison is not aggregate-only")
    if any(comparison.get(field) for field in HOLDOUT_FORBIDDEN):
        raise RuntimeError("holdout comparison is not aggregate-only")


def _upsert_present(entry: Mapping[str, Any]) -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    key = (entry["model_slug"], entry["method"], entry["split"])
    inventory["present"] = [
        row
        for row in inventory["present"]
        if (row["model_slug"], row["method"], row["split"]) != key
    ]
    inventory["missing"] = [
        row
        for row in inventory["missing"]
        if (row.get("model_slug"), row["method"], row.get("split")) != key
    ]
    inventory["present"].append(dict(entry))
    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sidecar_structured_path(source: Path) -> Path | None:
    nested = source / METHOD / "structured.jsonl"
    flat = source / "structured.jsonl"
    if nested.is_file():
        return nested
    if flat.is_file():
        return flat
    return None


def _sidecar_metrics_path(source: Path) -> Path | None:
    nested = source / METHOD / "letter_metrics.jsonl"
    flat = source / "letter_metrics.jsonl"
    if nested.is_file():
        return nested
    if flat.is_file():
        return flat
    return None


def _compact_arm(comparison: Mapping[str, Any]) -> dict[str, Any]:
    arms = comparison.get("arms") or {}
    if not isinstance(arms, Mapping):
        return {}
    arm = arms.get(METHOD) or arms.get("compact_ledger") or {}
    return dict(arm) if isinstance(arm, Mapping) else {}


def _living_effort(slug: str) -> str:
    if slug in {"grok46", "gpt56luna", "gemini37flash"}:
        return "low"
    if slug == "deepseek_v4_flash":
        return "thinking_on_provider_default"
    return "none"


def _public_replay(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    replay: list[dict[str, Any]] = []
    empty = 0
    for row in rows:
        raw = str(row.get("raw_output") or "")
        if not raw.strip():
            empty += 1
        replay.append(
            {
                "letter_id": str(row["letter_id"]),
                "prompt_version": str(row["prompt_version"]),
                "raw_output": raw,
            }
        )
    return replay, empty


def _public_scored(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in metrics:
        quality = row.get("quality") or {}
        raw_prf = row.get("raw_headline_prf") or {}
        hybrid_prf = row.get("hybrid_headline_prf") or {}
        scored.append(
            {
                "letter_id": str(row["letter_id"]),
                "method": METHOD,
                "raw_headline_f1": raw_prf.get("f1"),
                "hybrid_headline_f1": hybrid_prf.get("f1"),
                "raw_four_family_letter_exact": row.get("raw_four_family_letter_exact"),
                "hybrid_four_family_letter_exact": row.get(
                    "hybrid_four_family_letter_exact"
                ),
                "family_letter_exact": row.get("family_letter_exact"),
                "parse_ok": int(quality.get("parse") or 0) == 0
                and int(quality.get("schema") or 0) == 0,
            }
        )
    return scored


def _sync_inventory(panel: Mapping[str, Any]) -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    living_slugs = {item["slug"] for item in living_models()}
    existing_present = {
        (row["model_slug"], row["method"], row["split"]): row
        for row in inventory["present"]
    }

    def living_dev140(row: Mapping[str, Any]) -> bool:
        return (
            row.get("method") == METHOD
            and row.get("split") == PROMOTE_SPLIT
            and row.get("model_slug") in living_slugs
        )

    present = [row for row in inventory["present"] if not living_dev140(row)]
    missing = [row for row in inventory["missing"] if not living_dev140(row)]
    by_slug = {item["slug"]: item for item in living_models()}
    for cell in panel["cells"]:
        slug = str(cell["model_slug"])
        key = (slug, METHOD, PROMOTE_SPLIT)
        dest = paper_cell_root(slug)
        if cell["status"] == "present":
            cell_path = dest / "cell.json"
            if cell_path.is_file():
                cell_meta = json.loads(cell_path.read_text(encoding="utf-8"))
                present.append(
                    {
                        "model_slug": slug,
                        "model": by_slug[slug]["model"],
                        "method": METHOD,
                        "replay_alias": cell_meta["program"],
                        "split": PROMOTE_SPLIT,
                        "n": exect_row_count(PROMOTE_SPLIT),
                        "row_policy": "development_review_permitted",
                        "path": (dest / "structured.jsonl").relative_to(ROOT).as_posix(),
                        "status": "present",
                        "empty_raw_count": cell_meta["empty_raw_count"],
                    }
                )
            elif key in existing_present:
                present.append(existing_present[key])
            continue
        historical = existing_present.get(key)
        if historical is not None:
            present.append(historical)
            continue
        missing.append(
            {
                "model_slug": slug,
                "model": by_slug[slug]["model"],
                "method": METHOD,
                "split": PROMOTE_SPLIT,
                "n": exect_row_count(PROMOTE_SPLIT),
                "status": "missing",
                "note": (
                    "Living-effort ExECT Compact development cell. "
                    "Promote when the sidecar finishes."
                ),
            }
        )
    inventory["present"] = present
    inventory["missing"] = missing
    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
