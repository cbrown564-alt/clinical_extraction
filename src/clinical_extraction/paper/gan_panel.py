"""Promote living Gan dev750 cells into the tracked paper tree."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.cells import normalize_rungs_payload
from clinical_extraction.paper.comparison_contract import (
    adapt_legacy_comparison,
    stage_metric,
)
from clinical_extraction.paper.gan_later_stage import EXTRACT_METHOD
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
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
WORK_ROOT = ROOT / "experiments/paper"
HOLDOUT_ROOT = ROOT / "scratch/holdout/paper"
PAPER_GAN = ROOT / "paper_experiments/gan"
PANEL_PATH = PAPER_GAN / "dev750_panel.json"
INVENTORY_PATH = ROOT / "paper_experiments/inventory.json"
REPLAY_FIELDS = ("source_row_index", "prompt_version", "raw_output")
GAN_METHODS = ("gan_llm_only", "gan_llm_extract_raw")
PANEL_METHODS = ("rules_only", "llm_extract", "llm_encode", "llm_select")
PROMOTE_SPLIT = "dev750"
HOLDOUT_FORBIDDEN = ("incorrect_source_row_indices", "letter_ids", "changed_rows")


def living_work_root(method: str, slug: str, split: str) -> Path:
    """Return the living-effort Gan work directory."""

    root = HOLDOUT_ROOT if holdout_is_aggregate_only(split) else WORK_ROOT
    flat = root / method / slug / split
    if method in {"gan_llm_encode", "gan_llm_select", "gan_llm_select_from_extract"}:
        nested = root / method / slug / EXTRACT_METHOD / split
        if (nested / "rows.jsonl").is_file():
            return nested
        if (flat / "rows.jsonl").is_file():
            return flat
        return nested
    return flat


def paper_cell_root(method: str, slug: str, split: str) -> Path:
    """Return the tracked paper directory for a Gan cell."""

    return PAPER_GAN / method / slug / split


def _living_extract_stages(slug: str) -> dict[str, float] | None:
    dest = paper_cell_root("gan_llm_extract", slug, PROMOTE_SPLIT)
    comparison_path = dest / "comparison.json"
    if not comparison_path.is_file():
        return None
    living = adapt_legacy_comparison(
        json.loads(comparison_path.read_text(encoding="utf-8"))
    )
    if living is None:
        return None
    extract = stage_metric(living, "extract")
    encode = stage_metric(living, "encode")
    select = stage_metric(living, "select")
    if extract is None or select is None:
        return None
    return {
        "llm_extract": extract,
        "llm_encode": encode if encode is not None else extract,
        "llm_select": select,
    }


def promote_gan_dev750(method: str, slug: str) -> dict[str, Any]:
    """Copy a finished living-effort Gan dev750 cell into paper_experiments."""

    return promote_gan(method, slug, PROMOTE_SPLIT)


def promote_gan(method: str, slug: str, split: str) -> dict[str, Any]:
    """Copy a finished living-effort Gan cell into paper_experiments."""

    spec = method_spec(method)
    if spec["task"] != "gan2026":
        raise RuntimeError("promote-gan is Gan only")
    split_for(method, split)
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    source = living_work_root(method, slug, split)
    rows_path = source / "rows.jsonl"
    comparison_path = source / "comparison.json"
    if not rows_path.is_file() or not comparison_path.is_file():
        raise RuntimeError(f"missing finished living-effort {method} {slug} {split} run")
    rows = load_jsonl_rows(rows_path)
    expected = gan_row_count(split)
    if len(rows) != expected:
        raise RuntimeError(f"{rows_path} has {len(rows)} rows, expected {expected}")
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if comparison.get("split") != split or comparison.get("method") != method:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    if comparison.get("reasoning_effort") not in {None, "low"}:
        raise RuntimeError(
            "promote only the living low-effort cell, not a non-living-effort repeat"
        )
    if holdout:
        _assert_aggregate_only(comparison)
    dest = paper_cell_root(method, slug, split)
    dest.mkdir(parents=True, exist_ok=True)
    replay, scored, empty = _public_rows(method, rows)
    write_jsonl_rows(replay, dest / "rows.jsonl")
    if not holdout:
        write_jsonl_rows(scored, dest / "scored.jsonl")
    (dest / "comparison.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    prompt = str(comparison.get("prompt_version") or replay[0]["prompt_version"])
    summary = comparison.get("summary") or {}
    cell = {
        "model_slug": slug,
        "model": model["model"],
        "method": method,
        "program": prompt,
        "split": split,
        "split_machine": gan_machine_split(split),
        "n": expected,
        "row_count": expected,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "id_field": "source_row_index",
        "replay_fields": list(REPLAY_FIELDS),
        "empty_raw_count": empty,
        "source": source.relative_to(ROOT).as_posix(),
        "call_mode": "live_2026-08-17",
        "living_effort": (
            "low"
            if slug in {"grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash"}
            else "none"
        ),
        "rows": "rows.jsonl",
        "comparison": "comparison.json",
        "purist_correct": summary.get("purist_correct"),
        "purist_accuracy": summary.get("purist_accuracy"),
        "micro_f1": summary.get("micro_f1", summary.get("purist_accuracy")),
    }
    if not holdout:
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
            "replay_alias": prompt,
            "split": split,
            "n": expected,
            "row_policy": "aggregate_only" if holdout else "development_review_permitted",
            "path": (dest / "rows.jsonl").relative_to(ROOT).as_posix(),
            "status": "present",
            "empty_raw_count": empty,
        }
    )
    if holdout or method not in GAN_METHODS:
        return {"cell": cell}
    panel = rebuild_dev750_panel()
    return {"cell": cell, "panel": PANEL_PATH.relative_to(ROOT).as_posix(), "cells": panel["cells"]}


def rebuild_dev750_panel() -> dict[str, Any]:
    """Write the rectangular Gan cell-3 development index for the frontend."""

    cells: list[dict[str, Any]] = []
    for model in living_models():
        slug = str(model["slug"])
        extract_stages = _living_extract_stages(slug)
        rung_dir = PAPER_GAN / "rungs" / slug / PROMOTE_SPLIT
        comparison_path = rung_dir / "comparison.json"
        scored_path = rung_dir / "scored.jsonl"
        payload = (
            json.loads(comparison_path.read_text(encoding="utf-8"))
            if comparison_path.is_file()
            else {}
        )
        raw_rungs = payload.get("rungs") or {}
        rungs = (
            normalize_rungs_payload(raw_rungs) if isinstance(raw_rungs, dict) else {}
        )
        extract_dest = paper_cell_root("gan_llm_extract", slug, PROMOTE_SPLIT)
        extract_comparison = extract_dest / "comparison.json"
        extract_scored = extract_dest / "scored.jsonl"
        for method in PANEL_METHODS:
            extract_metric = (
                extract_stages.get(method) if extract_stages is not None else None
            )
            rung = rungs.get(method)
            if extract_metric is not None and method != "rules_only":
                cells.append(
                    {
                        "model_slug": slug,
                        "model": model["model"],
                        "label": model["label"],
                        "method": method,
                        "status": "present",
                        "path": extract_dest.relative_to(ROOT).as_posix() + "/",
                        "scored": extract_scored.relative_to(ROOT).as_posix()
                        if extract_scored.is_file()
                        else (
                            scored_path.relative_to(ROOT).as_posix()
                            if scored_path.is_file()
                            else None
                        ),
                        "comparison": extract_comparison.relative_to(ROOT).as_posix()
                        if extract_comparison.is_file()
                        else None,
                        "n": gan_row_count(PROMOTE_SPLIT),
                        "purist_accuracy": extract_metric,
                        "micro_f1": extract_metric,
                        "shared_raw_output": "gan_llm_extract",
                    }
                )
                continue
            if isinstance(rung, Mapping) and rung.get("purist_accuracy") is not None:
                cells.append(
                    {
                        "model_slug": slug,
                        "model": model["model"],
                        "label": model["label"],
                        "method": method,
                        "status": "present",
                        "path": rung_dir.relative_to(ROOT).as_posix() + "/",
                        "scored": scored_path.relative_to(ROOT).as_posix()
                        if scored_path.is_file()
                        else None,
                        "comparison": comparison_path.relative_to(ROOT).as_posix(),
                        "n": gan_row_count(PROMOTE_SPLIT),
                        "purist_correct": rung.get("purist_correct"),
                        "purist_accuracy": rung.get("purist_accuracy"),
                        "micro_f1": rung.get("micro_f1", rung.get("purist_accuracy")),
                        "shared_raw_output": payload.get("shared_raw_output"),
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
                        "n": gan_row_count(PROMOTE_SPLIT),
                    }
                )
    panel = {
        "schema_version": "paper_experiments.gan.dev750_panel.v3",
        "split": PROMOTE_SPLIT,
        "split_machine": "validation",
        "row_policy": "development_review_permitted",
        "method_identity": "gemini37flash",
        "living_effort": {
            "hosted_reasoning": "low",
            "deepseek": "low",
            "local": "none",
        },
        "notes_source": {
            "split_machine": "validation",
            "frontend": "/datasets/gan2026/letters",
        },
        "methods": list(PANEL_METHODS),
        "models": [item["slug"] for item in living_models()],
        "cells": cells,
        "claim_boundary": (
            "Gan cell-3 development panel: rules, then extract / encode / "
            "select on living gan_llm_extract with gan_rules_encode and "
            "llm_select_after_codebook. Not holdout. gan_llm_only is not "
            "a panel column. Source-near rungs remain a fallback until a "
            "model has a living extract envelope."
        ),
    }
    PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    PANEL_PATH.write_text(json.dumps(panel, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _sync_inventory()
    return panel


def load_dev750_panel() -> dict[str, Any]:
    """Return the living Gan dev750 panel, rebuilding it if needed."""

    if not PANEL_PATH.is_file():
        return rebuild_dev750_panel()
    return json.loads(PANEL_PATH.read_text(encoding="utf-8"))


def load_scored_rows(method: str, slug: str) -> list[dict[str, Any]]:
    """Return frontend-joinable scored rows for one present cell."""

    model_by_slug(slug)
    if method in PANEL_METHODS:
        path = PAPER_GAN / "rungs" / slug / PROMOTE_SPLIT / "scored.jsonl"
        if not path.is_file():
            raise FileNotFoundError(path)
        rows: list[dict[str, Any]] = []
        for row in load_jsonl_rows(path):
            rungs = row.get("rungs") or {}
            rung = rungs.get(method) if isinstance(rungs, Mapping) else None
            if not isinstance(rung, Mapping):
                continue
            source_row_index = int(row["source_row_index"])
            rows.append(
                {
                    "source_row_index": source_row_index,
                    "letter_id": str(source_row_index),
                    "method": method,
                    "predicted_label": rung.get("predicted_label"),
                    "purist_correct": rung.get("purist_correct"),
                    "pragmatic_correct": rung.get("pragmatic_correct"),
                }
            )
        return rows
    method_spec(method)
    path = paper_cell_root(method, slug, PROMOTE_SPLIT) / "scored.jsonl"
    if not path.is_file():
        raise FileNotFoundError(path)
    return load_jsonl_rows(path)


def _public_rows(
    method: str,
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    replay: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []
    empty = 0
    for row in rows:
        raw = str(row.get("raw_output") or "")
        if not raw.strip():
            empty += 1
        replay.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "prompt_version": str(row["prompt_version"]),
                "raw_output": raw,
            }
        )
        comparison = row.get("comparison") or {}
        source_row_index = int(row["source_row_index"])
        scored.append(
            {
                "source_row_index": source_row_index,
                "letter_id": str(source_row_index),
                "method": method,
                "predicted_label": _predicted_label(row),
                "purist_correct": comparison.get("purist_correct"),
                "pragmatic_correct": comparison.get("pragmatic_correct"),
                "parse_ok": not bool(row.get("call_error"))
                and (
                    row.get("decision_record") is not None
                    or row.get("structured_record") is not None
                ),
            }
        )
    return replay, scored, empty


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


def _predicted_label(row: Mapping[str, Any]) -> str | None:
    decision = row.get("decision_record")
    if isinstance(decision, Mapping) and decision.get("final_label"):
        return str(decision["final_label"])
    structured = row.get("structured_record")
    if isinstance(structured, Mapping):
        selection = structured.get("selection") or {}
        if isinstance(selection, Mapping) and selection.get("final_label"):
            return str(selection["final_label"])
    return None


def _sync_inventory() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    living_slugs = {item["slug"] for item in living_models()}
    existing_present = {
        (row["model_slug"], row["method"], row["split"]): row
        for row in inventory["present"]
    }

    def living_dev750(row: Mapping[str, Any]) -> bool:
        return (
            row.get("method") in GAN_METHODS
            and row.get("split") == PROMOTE_SPLIT
            and row.get("model_slug") in living_slugs
        )

    def generic_gan_blank(row: Mapping[str, Any]) -> bool:
        return (
            row.get("method") in GAN_METHODS
            and row.get("split") in {PROMOTE_SPLIT, None}
            and "model_slug" not in row
        )

    present = [row for row in inventory["present"] if not living_dev750(row)]
    missing = [
        row
        for row in inventory["missing"]
        if not living_dev750(row) and not generic_gan_blank(row)
    ]
    by_slug = {item["slug"]: item for item in living_models()}
    for model in living_models():
        slug = str(model["slug"])
        for method in GAN_METHODS:
            key = (slug, method, PROMOTE_SPLIT)
            dest = paper_cell_root(method, slug, PROMOTE_SPLIT)
            rows_path = dest / "rows.jsonl"
            cell_path = dest / "cell.json"
            if rows_path.is_file() and cell_path.is_file():
                historical = existing_present.get(key)
                if historical is not None:
                    present.append(historical)
                    continue
                cell_meta = json.loads(cell_path.read_text(encoding="utf-8"))
                present.append(
                    {
                        "model_slug": slug,
                        "model": by_slug[slug]["model"],
                        "method": method,
                        "replay_alias": cell_meta["program"],
                        "split": PROMOTE_SPLIT,
                        "n": gan_row_count(PROMOTE_SPLIT),
                        "row_policy": "development_review_permitted",
                        "path": rows_path.relative_to(ROOT).as_posix(),
                        "status": "present",
                        "empty_raw_count": cell_meta["empty_raw_count"],
                    }
                )
                continue
            historical = existing_present.get(key)
            if historical is not None:
                present.append(historical)
                continue
    inventory["present"] = present
    inventory["missing"] = missing
    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
