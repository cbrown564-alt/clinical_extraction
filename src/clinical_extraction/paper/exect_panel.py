"""Promote living ExECT Compact dev140 cells into the tracked paper tree."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import compact_metrics_from_structured
from clinical_extraction.paper.exect_later_stage import (
    CITED_SLUG as LATER_STAGE_SLUG,
)
from clinical_extraction.paper.exect_later_stage import (
    later_stage_work_root,
    rescore_later_stage,
)
from clinical_extraction.paper.exect_rung_replay import exect_rung_out_dir
from clinical_extraction.paper.methods import (
    exect_row_count,
    holdout_is_aggregate_only,
    method_spec,
    split_for,
)
from clinical_extraction.paper.roster import living_models, model_by_slug
from clinical_extraction.paper.rungs import RUNG_IDS, normalize_cell_id
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
WORK_ROOT = ROOT / "experiments/paper/exect_llm_pre_post"
HOLDOUT_ROOT = ROOT / "scratch/holdout/paper/exect_llm_pre_post"
LEGACY_WORK_ROOT = ROOT / "experiments/paper/exect_llm_with_rules"
LEGACY_HOLDOUT_ROOT = ROOT / "scratch/holdout/paper/exect_llm_with_rules"
LLM_ONLY_WORK_ROOT = ROOT / "experiments/paper/exect_llm_only"
LLM_ONLY_HOLDOUT_ROOT = ROOT / "scratch/holdout/paper/exect_llm_only"
PAPER_EXECT = ROOT / "paper_experiments/exect"
PANEL_PATH = PAPER_EXECT / "dev140_panel.json"
INVENTORY_PATH = ROOT / "paper_experiments/inventory.json"
REPLAY_FIELDS = ("letter_id", "prompt_version", "raw_output")
METHOD = "exect_llm_pre_post"
LEGACY_METHOD = "exect_llm_with_rules"
LLM_ONLY_METHOD = "exect_llm_only"
REQUEST_METHODS = (LLM_ONLY_METHOD, METHOD)
EXECT_METHODS = REQUEST_METHODS
LATER_STAGE_METHODS = ("exect_llm_encode", "exect_llm_select")
PANEL_METHODS = RUNG_IDS
PROMOTE_SPLIT = "dev140"
HOLDOUT_FORBIDDEN = ("letter_ids", "changed_rows")


def living_work_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the living-effort Compact work directory."""

    holdout = holdout_is_aggregate_only(split)
    candidates = (
        (HOLDOUT_ROOT / slug / split, LEGACY_HOLDOUT_ROOT / slug / split)
        if holdout
        else (WORK_ROOT / slug / split, LEGACY_WORK_ROOT / slug / split)
    )
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def paper_cell_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the tracked paper directory for an ExECT LLM with rules cell."""

    return paper_method_cell_root(METHOD, slug, split)


def paper_llm_only_cell_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the tracked paper directory for an ExECT LLM only cell."""

    return paper_method_cell_root(LLM_ONLY_METHOD, slug, split)


def paper_method_cell_root(method: str, slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the tracked paper directory for one ExECT paper method cell."""

    if method not in EXECT_METHODS and method not in LATER_STAGE_METHODS:
        raise ValueError(f"unsupported ExECT paper method {method}")
    return PAPER_EXECT / method / slug / split


def living_llm_only_work_root(slug: str, split: str = PROMOTE_SPLIT) -> Path:
    """Return the living-effort ExECT LLM only work directory."""

    root = LLM_ONLY_HOLDOUT_ROOT if holdout_is_aggregate_only(split) else LLM_ONLY_WORK_ROOT
    return root / slug / split


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
    structured_path = _work_structured_path(source, METHOD)
    comparison_path = source / "comparison.json"
    if structured_path is None or not comparison_path.is_file():
        raise RuntimeError(f"missing finished living-effort {METHOD} {slug} {split} run")
    rows = load_jsonl_rows(structured_path)
    expected = exect_row_count(split)
    if len(rows) != expected:
        raise RuntimeError(f"{structured_path} has {len(rows)} rows, expected {expected}")
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if comparison.get("split") != split:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    if comparison.get("reasoning_effort") not in {None, "low"}:
        raise RuntimeError(
            "promote only the living low-effort cell, not a non-living-effort repeat"
        )
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
        "program": "exect_llm_pre_post",
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
        metrics_path = _work_metrics_path(source, METHOD)
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
                "replay_alias": "exect_llm_pre_post",
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


def promote_exect_llm_only(slug: str, split: str) -> dict[str, Any]:
    """Copy a finished Compact LLM-only cell. Cite raw F1 only."""

    spec = method_spec(LLM_ONLY_METHOD)
    if spec["task"] != "exectv2":
        raise RuntimeError("promote-exect LLM-only is ExECT only")
    split_for(LLM_ONLY_METHOD, split)
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    source = living_llm_only_work_root(slug, split)
    structured_path = _work_structured_path(source, LLM_ONLY_METHOD)
    comparison_path = source / "comparison.json"
    if structured_path is None or not comparison_path.is_file():
        raise RuntimeError(
            f"missing finished living-effort {LLM_ONLY_METHOD} {slug} {split} run"
        )
    rows = load_jsonl_rows(structured_path)
    expected = exect_row_count(split)
    if len(rows) != expected:
        raise RuntimeError(f"{structured_path} has {len(rows)} rows, expected {expected}")
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if comparison.get("split") != split:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    if comparison.get("reasoning_effort") not in {None, "low"}:
        raise RuntimeError(
            "promote only the living low-effort cell, not a non-living-effort repeat"
        )
    if holdout:
        _assert_aggregate_only(comparison)
    dest = paper_llm_only_cell_root(slug, split)
    dest.mkdir(parents=True, exist_ok=True)
    replay, empty = _public_replay(rows)
    write_jsonl_rows(replay, dest / "structured.jsonl")
    (dest / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    arm = _llm_only_arm(comparison)
    cell = {
        "model_slug": slug,
        "model": model["model"],
        "method": LLM_ONLY_METHOD,
        "program": "exect_llm_only",
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
    }
    if not holdout:
        metrics_path = _work_metrics_path(source, LLM_ONLY_METHOD)
        if metrics_path is not None:
            metrics = load_jsonl_rows(metrics_path)
        else:
            metrics = compact_metrics_from_structured(slug, dest / "structured.jsonl")
        scored = _public_scored_llm_only(metrics)
        if len(scored) != expected:
            raise RuntimeError(f"{slug} scored {len(scored)} letters, expected {expected}")
        write_jsonl_rows(scored, dest / "scored.jsonl")
        cell["scored"] = "scored.jsonl"
    (dest / "cell.json").write_text(
        json.dumps(cell, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _upsert_present(
        {
            "model_slug": slug,
            "model": model["model"],
            "method": LLM_ONLY_METHOD,
            "replay_alias": "exect_llm_only",
            "split": split,
            "n": expected,
            "row_policy": "aggregate_only" if holdout else "development_review_permitted",
            "path": (dest / "structured.jsonl").relative_to(ROOT).as_posix(),
            "status": "present",
            "empty_raw_count": empty,
        }
    )
    _ensure_missing_standalone_llm_only()
    return {"cell": cell}


def promote_exect_later_stage(method: str, slug: str, split: str) -> dict[str, Any]:
    """Copy a rescored Gemini later-stage encode or select cell."""

    spec = method_spec(method)
    if spec["task"] != "exectv2" or method not in LATER_STAGE_METHODS:
        raise RuntimeError("promote-exect later-stage is exect_llm_encode or exect_llm_select")
    if slug != LATER_STAGE_SLUG:
        raise RuntimeError("later-stage ExECT encode and select run on Gemini only")
    split_for(method, split)
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    rescore_later_stage(method, slug, split)
    source = later_stage_work_root(method, slug, split)
    rows_path = source / "rows.jsonl"
    comparison_path = source / "comparison.json"
    if not rows_path.is_file() or not comparison_path.is_file():
        raise RuntimeError(f"missing finished later-stage {method} {slug} {split} run")
    rows = load_jsonl_rows(rows_path)
    expected = exect_row_count(split)
    if len(rows) != expected:
        raise RuntimeError(f"{rows_path} has {len(rows)} rows, expected {expected}")
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if comparison.get("split") != split or comparison.get("method") != method:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    if comparison.get("scorer") != "clinical_headline_unit_keys":
        raise RuntimeError("later-stage comparison must use the exact clinical-fact scorer")
    if comparison.get("reasoning_effort") not in {None, "low"}:
        raise RuntimeError(
            "promote only the living low-effort cell, not a non-living-effort repeat"
        )
    if holdout:
        _assert_aggregate_only(comparison)
    dest = paper_method_cell_root(method, slug, split)
    dest.mkdir(parents=True, exist_ok=True)
    replay, empty = _public_replay(rows)
    write_jsonl_rows(replay, dest / "rows.jsonl")
    (dest / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    cell = {
        "model_slug": slug,
        "model": model["model"],
        "method": method,
        "program": method,
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
        "rows": "rows.jsonl",
        "comparison": "comparison.json",
        "four_family_headline_f1": comparison.get("four_family_headline_f1"),
        "scorer": comparison.get("scorer"),
    }
    if not holdout:
        scored = _public_later_stage_scored(method, rows)
        if len(scored) != expected:
            raise RuntimeError(f"{slug} scored {len(scored)} letters, expected {expected}")
        write_jsonl_rows(scored, dest / "scored.jsonl")
        cell["scored"] = "scored.jsonl"
    (dest / "cell.json").write_text(
        json.dumps(cell, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _upsert_present(
        {
            "model_slug": slug,
            "model": model["model"],
            "method": method,
            "replay_alias": method,
            "split": split,
            "n": expected,
            "row_policy": "aggregate_only" if holdout else "development_review_permitted",
            "path": (dest / "rows.jsonl").relative_to(ROOT).as_posix(),
            "status": "present",
            "empty_raw_count": empty,
        }
    )
    return {"cell": cell}


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
            "program": "exect_llm_pre_post",
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
    """Write the rectangular living ExECT five-rung development index."""

    cells: list[dict[str, Any]] = []
    rules_path = PAPER_EXECT / "exect_rules" / "dev140.json"
    rules_f1 = None
    if rules_path.is_file():
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        rules_f1 = rules.get("dev140", {}).get("four_family_headline_f1")
    for model in living_models():
        slug = str(model["slug"])
        rung_dir = PAPER_EXECT / "rungs" / slug / PROMOTE_SPLIT
        rung_comparison_path = rung_dir / "comparison.json"
        rung_scored = rung_dir / "scored.jsonl"
        rung_payload = (
            json.loads(rung_comparison_path.read_text(encoding="utf-8"))
            if rung_comparison_path.is_file()
            else {}
        )
        rung_scores = rung_payload.get("rungs") or {}
        pre_post_dest = paper_method_cell_root(METHOD, slug)
        for method in PANEL_METHODS:
            if method == "rules_only":
                dest = PAPER_EXECT / "exect_rules"
                if rules_f1 is not None:
                    cells.append(
                        {
                            "model_slug": slug,
                            "model": model["model"],
                            "label": model["label"],
                            "method": method,
                            "status": "present",
                            "path": dest.relative_to(ROOT).as_posix() + "/",
                            "comparison": (
                                dest / "dev140.json"
                            ).relative_to(ROOT).as_posix(),
                            "n": exect_row_count(PROMOTE_SPLIT),
                            "clinical_fact_f1": rules_f1,
                        }
                    )
                else:
                    cells.append(
                        {
                            "model_slug": slug,
                            "model": model["model"],
                            "label": model["label"],
                            "method": method,
                            "status": "pending",
                            "path": dest.relative_to(ROOT).as_posix() + "/",
                            "n": exect_row_count(PROMOTE_SPLIT),
                        }
                    )
                continue
            if method == "llm_pre_post":
                dest = pre_post_dest
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
                            "method": method,
                            "status": "present",
                            "path": dest.relative_to(ROOT).as_posix() + "/",
                            "rows": structured_path.relative_to(ROOT).as_posix(),
                            "scored": scored_path.relative_to(ROOT).as_posix()
                            if scored_path.is_file()
                            else None,
                            "comparison": comparison_path.relative_to(ROOT).as_posix(),
                            "n": exect_row_count(PROMOTE_SPLIT),
                            "clinical_fact_f1": arm.get("hybrid_headline_f1"),
                            "raw_headline_f1": arm.get("raw_headline_f1"),
                            "hybrid_headline_f1": arm.get("hybrid_headline_f1"),
                            "living_effort": extra.get("living_effort")
                            or _living_effort(slug),
                        }
                    )
                else:
                    cells.append(
                        {
                            "model_slug": slug,
                            "model": model["model"],
                            "label": model["label"],
                            "method": method,
                            "status": "pending",
                            "path": dest.relative_to(ROOT).as_posix() + "/",
                            "n": exect_row_count(PROMOTE_SPLIT),
                        }
                    )
                continue
            rung = rung_scores.get(method)
            if isinstance(rung, Mapping) and rung.get("clinical_fact_f1") is not None:
                cells.append(
                    {
                        "model_slug": slug,
                        "model": model["model"],
                        "label": model["label"],
                        "method": method,
                        "status": "present",
                        "path": rung_dir.relative_to(ROOT).as_posix() + "/",
                        "scored": rung_scored.relative_to(ROOT).as_posix()
                        if rung_scored.is_file()
                        else None,
                        "comparison": rung_comparison_path.relative_to(ROOT).as_posix(),
                        "n": exect_row_count(PROMOTE_SPLIT),
                        "clinical_fact_f1": rung.get("clinical_fact_f1"),
                    }
                )
            else:
                cells.append(
                    {
                        "model_slug": slug,
                        "model": model["model"],
                        "label": model["label"],
                        "method": method,
                        "status": "pending",
                        "path": rung_dir.relative_to(ROOT).as_posix() + "/",
                        "n": exect_row_count(PROMOTE_SPLIT),
                    }
                )
    panel = {
        "schema_version": "paper_experiments.exect.dev140_panel.v2",
        "split": PROMOTE_SPLIT,
        "split_machine": "dev",
        "row_policy": "development_review_permitted",
        "method_identity": "gemini37flash",
        "living_effort": {
            "hosted_reasoning": "low",
            "deepseek": "thinking_on_provider_default",
            "local": "none",
        },
        "notes_source": {
            "split_machine": "dev",
            "frontend": "/datasets/exectv2/letters",
        },
        "methods": list(PANEL_METHODS),
        "request_methods": list(REQUEST_METHODS),
        "models": [item["slug"] for item in living_models()],
        "cells": cells,
        "claim_boundary": (
            "Living six-model ExECT development panel. Headline columns are "
            "the five rungs. Rungs 2-4 replay exect_llm_only. Rung 5 is "
            "living exect_llm_pre_post. Not holdout. The July explorer "
            "runs.json roster is historical."
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
    by_slug = {item["slug"]: item for item in living_models()}
    for model_row in living_models():
        slug = str(model_row["slug"])
        label = str(by_slug[slug]["label"])
        model = str(by_slug[slug]["model"])
        for method in REQUEST_METHODS:
            rows_path = paper_method_cell_root(method, slug) / "structured.jsonl"
            if not rows_path.is_file():
                continue
            extra = {}
            cell_path = rows_path.parent / "cell.json"
            if cell_path.is_file():
                extra = json.loads(cell_path.read_text(encoding="utf-8"))
            if method == LLM_ONLY_METHOD:
                runs.append(
                    {
                        "run_id": paper_exect_run_id(slug, "llm"),
                        "task": "exectv2",
                        "label": f"{label} · LLM only",
                        "model": model,
                        "kind": "llm",
                        "active_method": "llm",
                        "method_id": "llm",
                        "architecture_family": LLM_ONLY_METHOD,
                        "pipeline_family": "llm",
                        "split": "dev140",
                        "row_count": 140,
                        "date": "2026-08-18",
                        "decision": "development_comparison",
                        "promotion_decision": "living ExECT LLM only",
                        "claim_boundary": panel.get("claim_boundary"),
                        "scorer_view": "raw_lane_score",
                        "artifact_paths": [rows_path.relative_to(ROOT).as_posix()],
                        "source_paths": [rows_path.relative_to(ROOT).as_posix()],
                        "metrics": {
                            "overall_f1": extra.get("raw_headline_f1"),
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
                continue
            runs.append(
                {
                    "run_id": paper_exect_run_id(slug, "llm_with_rules"),
                    "task": "exectv2",
                    "label": f"{label} · LLM + rules",
                    "model": model,
                    "kind": "llm_with_rules",
                    "active_method": "llm_with_rules",
                    "method_id": "llm_with_rules",
                    "architecture_family": METHOD,
                    "pipeline_family": METHOD,
                    "split": "dev140",
                    "row_count": 140,
                    "date": "2026-08-18",
                    "decision": "development_comparison",
                    "promotion_decision": "living ExECT panel",
                    "claim_boundary": panel.get("claim_boundary"),
                    "scorer_view": "headline_target",
                    "artifact_paths": [rows_path.relative_to(ROOT).as_posix()],
                    "source_paths": [rows_path.relative_to(ROOT).as_posix()],
                    "metrics": {
                        "overall_f1": extra.get("hybrid_headline_f1"),
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


def load_scored_rows(method: str, slug: str) -> list[dict[str, Any]]:
    """Return frontend-joinable scored rows for one present ExECT cell."""

    model_by_slug(slug)
    if method == LEGACY_METHOD:
        method = METHOD
    if method == "llm_pre_post":
        method = METHOD
    try:
        cell = normalize_cell_id(method)
    except ValueError:
        cell = None
    if cell in {"llm_extract", "llm_encode", "llm_select"}:
        path = exect_rung_out_dir(slug, PROMOTE_SPLIT) / "scored.jsonl"
        if not path.is_file():
            raise FileNotFoundError(path)
        rows = []
        for row in load_jsonl_rows(path):
            payload = dict(row)
            payload["method"] = cell
            rows.append(payload)
        return rows
    path = paper_method_cell_root(method, slug) / "scored.jsonl"
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


def _work_structured_path(source: Path, method: str = METHOD) -> Path | None:
    for name in (method, METHOD, LEGACY_METHOD):
        nested = source / name / "structured.jsonl"
        if nested.is_file():
            return nested
    flat = source / "structured.jsonl"
    if flat.is_file():
        return flat
    return None


def _work_metrics_path(source: Path, method: str = METHOD) -> Path | None:
    for name in (method, METHOD, LEGACY_METHOD):
        nested = source / name / "letter_metrics.jsonl"
        if nested.is_file():
            return nested
    flat = source / "letter_metrics.jsonl"
    if flat.is_file():
        return flat
    return None


def _llm_only_arm(comparison: Mapping[str, Any]) -> dict[str, Any]:
    arms = comparison.get("arms") or {}
    if not isinstance(arms, Mapping):
        return {}
    arm = arms.get(LLM_ONLY_METHOD) or {}
    return dict(arm) if isinstance(arm, Mapping) else {}


def _public_scored_llm_only(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in metrics:
        quality = row.get("quality") or {}
        raw_prf = row.get("raw_headline_prf") or {}
        scored.append(
            {
                "letter_id": str(row["letter_id"]),
                "method": LLM_ONLY_METHOD,
                "raw_headline_f1": raw_prf.get("f1"),
                "raw_four_family_letter_exact": row.get("raw_four_family_letter_exact"),
                "parse_ok": int(quality.get("parse") or 0) == 0
                and int(quality.get("schema") or 0) == 0,
            }
        )
    return scored


def _ensure_missing_standalone_llm_only() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    present = {
        (row["model_slug"], row["method"], row["split"]) for row in inventory["present"]
    }
    missing = {
        (row.get("model_slug"), row["method"], row.get("split"))
        for row in inventory["missing"]
    }
    extra: list[dict[str, Any]] = []
    for model in living_models():
        slug = str(model["slug"])
        for split, n, policy in (
            ("dev140", 140, "development_review_permitted"),
            ("test60", 59, "aggregate_only"),
        ):
            key = (slug, LLM_ONLY_METHOD, split)
            if key in present or key in missing:
                continue
            extra.append(
                {
                    "model_slug": slug,
                    "model": model["model"],
                    "method": LLM_ONLY_METHOD,
                    "n": n,
                    "note": (
                        "ExECT LLM only. The unrepaired output of "
                        "ExECT pre-post is not this method."
                    ),
                    "row_policy": policy,
                    "split": split,
                    "status": "missing",
                }
            )
    if extra:
        inventory["missing"].extend(extra)
        INVENTORY_PATH.write_text(
            json.dumps(inventory, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _compact_arm(comparison: Mapping[str, Any]) -> dict[str, Any]:
    arms = comparison.get("arms") or {}
    if not isinstance(arms, Mapping):
        return {}
    arm = (
        arms.get(METHOD)
        or arms.get(LEGACY_METHOD)
        or arms.get("compact_ledger")
        or {}
    )
    return dict(arm) if isinstance(arm, Mapping) else {}


def _living_effort(slug: str) -> str:
    if slug in {"grok46", "gpt56luna", "gemini37flash"}:
        return "low"
    if slug == "deepseek_v4_flash":
        return "thinking_on_provider_default"
    return "none"


def _public_later_stage_scored(
    method: str, rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        scored.append(
            {
                "letter_id": str(row["letter_id"]),
                "method": method,
                "parse_ok": not bool(row.get("call_error"))
                and bool(str(row.get("raw_output") or "").strip()),
            }
        )
    return scored


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
                "prompt_version": structured.canonicalize_prompt_version(
                    str(row["prompt_version"])
                ),
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
            row.get("method") in REQUEST_METHODS
            and row.get("split") == PROMOTE_SPLIT
            and row.get("model_slug") in living_slugs
        )

    present = [row for row in inventory["present"] if not living_dev140(row)]
    missing = [row for row in inventory["missing"] if not living_dev140(row)]
    by_slug = {item["slug"]: item for item in living_models()}
    for model in living_models():
        slug = str(model["slug"])
        for method in REQUEST_METHODS:
            key = (slug, method, PROMOTE_SPLIT)
            dest = paper_method_cell_root(method, slug)
            structured_path = dest / "structured.jsonl"
            cell_path = dest / "cell.json"
            if structured_path.is_file() and cell_path.is_file():
                cell_meta = json.loads(cell_path.read_text(encoding="utf-8"))
                present.append(
                    {
                        "model_slug": slug,
                        "model": by_slug[slug]["model"],
                        "method": method,
                        "replay_alias": cell_meta["program"],
                        "split": PROMOTE_SPLIT,
                        "n": exect_row_count(PROMOTE_SPLIT),
                        "row_policy": "development_review_permitted",
                        "path": structured_path.relative_to(ROOT).as_posix(),
                        "status": "present",
                        "empty_raw_count": cell_meta["empty_raw_count"],
                    }
                )
                continue
            if structured_path.is_file() and key in existing_present:
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
                    "method": method,
                    "split": PROMOTE_SPLIT,
                    "n": exect_row_count(PROMOTE_SPLIT),
                    "status": "missing",
                    "note": (
                        "Living-effort ExECT development cell. "
                        "Promote when the run finishes."
                    ),
                }
            )
    inventory["present"] = present
    inventory["missing"] = missing
    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
