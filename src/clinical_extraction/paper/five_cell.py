"""Assemble the paper five-cell grid from living cell comparisons."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.comparison_contract import (
    adapt_legacy_comparison,
    stage_metric,
)
from clinical_extraction.paper.methods import (
    holdout_is_aggregate_only,
    method_spec,
)
from clinical_extraction.paper.roster import model_by_slug

ROOT = discover_repo_root(start=Path(__file__))
EXECT_CELL_ORDER = (
    "rules",
    "both_extract_then_rules",
    "llm_extract_then_rules",
    "llm_extract_encode_then_select_rules",
    "llm",
)
def write_five_cell_grid(
    method: str,
    *,
    slug: str = "gemini37flash",
    split: str,
) -> dict[str, Any]:
    """Write generated.json beside the curated five-cell grid."""

    spec = method_spec(method)
    task = str(spec["task"])
    if task == "gan2026":
        if split not in {"dev750", "test450"}:
            raise ValueError("Gan five-cell grid accepts split dev750 or test450")
        grid = _gan_grid(slug, split)
        out_dir = ROOT / "paper_experiments/gan/five_cell_grid" / slug / split
    elif task == "exectv2":
        if split not in {"dev140", "test60"}:
            raise ValueError("ExECT five-cell grid accepts split dev140 or test60")
        grid = _exect_grid(slug, split)
        out_dir = ROOT / "paper_experiments/exect/five_cell_grid" / slug / split
    else:
        raise ValueError(f"unsupported five-cell task {task}")
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_path = out_dir / "generated.json"
    generated_path.write_text(
        json.dumps(grid, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    curated_path = out_dir / "comparison.json"
    curated = (
        json.loads(curated_path.read_text(encoding="utf-8"))
        if curated_path.is_file()
        else None
    )
    return {
        "artifact": generated_path.relative_to(ROOT).as_posix(),
        "curated": (
            curated_path.relative_to(ROOT).as_posix() if curated_path.is_file() else None
        ),
        "matches_curated": _selects_match(grid, curated) if curated else None,
        "grid": grid,
    }


def _exect_grid(slug: str, split: str) -> dict[str, Any]:
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    extract = _load_comparison("exect", "exect_llm_extract", slug, split)
    both = _load_comparison("exect", "exect_llm_pre_post", slug, split)
    encode = _load_comparison("exect", "exect_llm_encode", slug, split)
    rule_select = _load_comparison(
        "exect", "exect_rule_select_after_llm_encode", slug, split
    )
    llm_select = _load_comparison("exect", "exect_llm_select", slug, split)
    rules = _exect_rules_score(split)
    extract_f1 = _stage(extract, "extract")
    extract_select = _stage(extract, "select")
    both_extract = _stage(both, "extract")
    both_encode = _stage(both, "encode")
    both_select = _stage(both, "select")
    encode_f1 = _later_stage_f1(encode)
    cell4_encode = _nested_f1(rule_select, "encode_stop") or encode_f1
    cell4_select = _nested_f1(rule_select, "select_stop")
    llm_f1 = _later_stage_f1(llm_select)
    n = 59 if split == "test60" else 140
    return {
        "claim_boundary": (
            "ExECT aggregate-only test60 five-cell grid. Headline is the "
            "select stop. All five rows use 4-family micro F1. Do not "
            "inspect holdout rows."
            if holdout
            else (
                "ExECT development five-cell grid. Headline is the select "
                "stop. All five rows use 4-family micro F1. Not holdout."
            )
        ),
        "split": split,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "model": model["model"],
        "scorer": "4-family micro F1",
        "n": n,
        "headline": "select",
        "role_values": ["rules", "LLM", "both"],
        "generated_from": "living_cells",
        "cells": {
            "rules": {
                "extract_role": "rules",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "exect_rules",
                "select": rules,
                "ablation": {
                    "extract": _exect_rules_stage(split, "find") or rules,
                    "encode": _exect_rules_stage(split, "encode") or rules,
                },
            },
            "both_extract_then_rules": {
                "extract_role": "both",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "exect_llm_pre_post",
                "prompt": "exect_llm_extract plus suggested candidates",
                "select": both_select,
                "ablation": {"extract": both_extract, "encode": both_encode},
            },
            "llm_extract_then_rules": {
                "extract_role": "LLM",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "exect_llm_extract",
                "select": extract_select,
                "ablation": {"extract": extract_f1},
            },
            "llm_extract_encode_then_select_rules": {
                "extract_role": "LLM",
                "encode_role": "LLM",
                "select_role": "rules",
                "extract_source": "exect_llm_extract",
                "encode_source": "exect_llm_encode",
                "select_source": "exect_rule_select_after_llm_encode",
                "select": cell4_select,
                "ablation": {"extract": extract_f1, "encode": cell4_encode},
            },
            "llm": {
                "extract_role": "LLM",
                "encode_role": "LLM",
                "select_role": "LLM",
                "extract_source": "exect_llm_extract",
                "encode_source": "exect_llm_encode",
                "select_source": "exect_llm_select",
                "select": llm_f1,
                "ablation": {"extract": extract_f1, "encode": encode_f1},
            },
        },
    }


def _gan_grid(slug: str, split: str) -> dict[str, Any]:
    holdout = holdout_is_aggregate_only(split)
    model = model_by_slug(slug)
    extract = _load_comparison("gan", "gan_llm_extract", slug, split)
    both = _load_comparison("gan", "gan_llm_and_rules_extract", slug, split)
    encode = _load_comparison("gan", "gan_llm_encode", slug, split)
    llm_select = _load_comparison("gan", "gan_llm_select_from_extract", slug, split)
    if llm_select is None:
        llm_select = _load_comparison("gan", "gan_llm_select", slug, split)
    rules = _gan_rules_count(split)
    return {
        "claim_boundary": (
            "Gan aggregate-only test450 five-cell grid. Headline is the "
            "select stop. Extract and encode counts are prior-stage "
            "ablations. Do not inspect holdout rows."
            if holdout
            else (
                "Gan development five-cell grid. Headline is the select "
                "stop. Extract and encode counts are prior-stage ablations. "
                "Not holdout."
            )
        ),
        "split": split,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "model": model["model"],
        "scorer": "purist",
        "n": 450 if split == "test450" else 750,
        "headline": "select",
        "role_values": ["rules", "LLM", "both"],
        "generated_from": "living_cells",
        "cells": {
            "rules": {
                "extract_role": "rules",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "gan_rules",
                "select": rules,
                "ablation": {"extract": rules, "encode": rules},
            },
            "both_extract_then_rules": {
                "extract_role": "both",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "gan_llm_and_rules_extract",
                "select": _gan_count(both, "select"),
                "ablation": {
                    "extract": _gan_count(both, "extract"),
                    "encode": _gan_count(both, "encode"),
                },
            },
            "llm_extract_then_rules": {
                "extract_role": "LLM",
                "encode_role": "rules",
                "select_role": "rules",
                "extract_source": "gan_llm_extract",
                "select": _gan_count(extract, "select"),
                "ablation": {
                    "extract": _gan_count(extract, "extract"),
                    "encode": _gan_count(extract, "encode"),
                },
            },
            "llm_extract_encode_then_select_rules": {
                "extract_role": "LLM",
                "encode_role": "LLM",
                "select_role": "rules",
                "extract_source": "gan_llm_extract",
                "select": _gan_count(encode, "select"),
                "ablation": {
                    "extract": _gan_count(extract, "extract"),
                    "encode": _gan_count(encode, "encode"),
                },
            },
            "llm": {
                "extract_role": "LLM",
                "encode_role": "LLM",
                "select_role": "LLM",
                "extract_source": "gan_llm_extract",
                "select_method": "gan_llm_select_from_extract",
                "select": _gan_count(llm_select, "select"),
                "ablation": {
                    "extract": _gan_count(extract, "extract"),
                    "encode": _gan_count(extract, "encode"),
                },
            },
        },
    }


def _load_comparison(
    task: str,
    method: str,
    slug: str,
    split: str,
) -> dict[str, Any] | None:
    path = ROOT / "paper_experiments" / task / method / slug / split / "comparison.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage(payload: Mapping[str, Any] | None, stage: str) -> float | None:
    if payload is None:
        return None
    return stage_metric(payload, stage)


def _later_stage_f1(payload: Mapping[str, Any] | None) -> float | None:
    if payload is None:
        return None
    living = adapt_legacy_comparison(payload)
    if living is not None:
        return stage_metric(living, "select")
    value = payload.get("four_family_headline_f1")
    return None if value is None else float(value)


def _nested_f1(payload: Mapping[str, Any] | None, key: str) -> float | None:
    if payload is None:
        return None
    block = payload.get(key)
    if not isinstance(block, Mapping):
        return None
    value = block.get("four_family_headline_f1") or block.get("four_family_micro_f1")
    if value is None:
        summary = block.get("summary")
        if isinstance(summary, Mapping) and summary.get("f1") is not None:
            value = summary["f1"]
    return None if value is None else float(value)


def _exect_rules_score(split: str) -> float | None:
    block = _exect_rules_block(split)
    if block is None:
        return None
    value = block.get("four_family_micro_f1")
    return None if value is None else float(value)


def _exect_rules_stage(split: str, stop: str) -> float | None:
    """Measured find/encode stop for the standalone-rules row."""

    block = _exect_rules_block(split)
    if block is None:
        return None
    rungs = block.get("stage_rungs")
    if not isinstance(rungs, Mapping):
        return None
    entry = rungs.get(stop)
    # Frozen ExECT stage_rungs still record the first stop as "recognise".
    if not isinstance(entry, Mapping) and stop == "find":
        entry = rungs.get("recognise")
    if not isinstance(entry, Mapping) or entry.get("f1") is None:
        return None
    return float(entry["f1"])


def _exect_rules_block(split: str) -> Mapping[str, Any] | None:
    path = ROOT / "paper_experiments/exect/exect_rules/dev140.json"
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    block = payload.get(split)
    return block if isinstance(block, Mapping) else None


def _gan_count(payload: Mapping[str, Any] | None, stage: str) -> int | None:
    if payload is None:
        return None
    living = (
        payload
        if payload.get("living_schema_version")
        else adapt_legacy_comparison(payload)
    )
    if living is None:
        return None
    block = (living.get("stages") or {}).get(stage)
    if not isinstance(block, Mapping):
        return None
    correct = block.get("purist_correct")
    return None if correct is None else int(correct)


def _gan_rules_count(split: str) -> int | None:
    path = (
        ROOT
        / "paper_experiments/gan/five_cell_grid/gemini37flash"
        / split
        / "comparison.json"
    )
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    cells = payload.get("cells")
    if not isinstance(cells, Mapping):
        return None
    rules = cells.get("rules")
    if not isinstance(rules, Mapping) or rules.get("select") is None:
        return None
    return int(rules["select"])


def _selects_match(
    generated: Mapping[str, Any],
    curated: Mapping[str, Any],
) -> bool:
    generated_cells = generated.get("cells")
    curated_cells = curated.get("cells")
    if not isinstance(generated_cells, Mapping) or not isinstance(curated_cells, Mapping):
        return False
    for name in EXECT_CELL_ORDER:
        left = generated_cells.get(name)
        right = curated_cells.get(name)
        if not isinstance(left, Mapping) or not isinstance(right, Mapping):
            return False
        if left.get("select") != right.get("select"):
            return False
    return True
