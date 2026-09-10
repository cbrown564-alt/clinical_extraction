"""Living paper roster."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root, resolve_letter_benchmarks_root

ROOT = discover_repo_root(start=Path(__file__))
BENCHMARKS_ROOT = resolve_letter_benchmarks_root(root=ROOT)
ROSTER_PATH = BENCHMARKS_ROOT / "roster.json"
LOCAL_LADDER_PATH = BENCHMARKS_ROOT / "local_size_ladder.json"


def living_models() -> list[dict[str, Any]]:
    """Return the six living paper models, Gemini first."""

    payload = json.loads(ROSTER_PATH.read_text(encoding="utf-8"))
    living = list(payload["living"])
    slugs = [item["slug"] for item in living]
    if slugs != [
        "gemini37flash",
        "grok46",
        "gpt56luna",
        "deepseek_v4_flash",
        "qwen38_27b",
        "gemma4_26b",
    ]:
        raise RuntimeError(f"paper roster drifted: {slugs}")
    return living


def extra_models() -> list[dict[str, Any]]:
    """Return runnable models that are not living paper cells."""

    payload = json.loads(ROSTER_PATH.read_text(encoding="utf-8"))
    extra = list(payload.get("runnable") or [])
    slugs = [item["slug"] for item in extra]
    if slugs != ["deepseek_v41_flash"]:
        raise RuntimeError(f"runnable roster drifted: {slugs}")
    return extra


def model_by_slug(slug: str) -> dict[str, Any]:
    """Return one living or extra runnable roster row."""

    for item in [*living_models(), *extra_models()]:
        if item["slug"] == slug:
            return item
    raise KeyError(f"unknown living model {slug}")


def local_ladder_models() -> list[dict[str, Any]]:
    """Return the non-living local size-and-era ladder."""

    payload = json.loads(LOCAL_LADDER_PATH.read_text(encoding="utf-8"))
    if payload.get("living") is not False:
        raise RuntimeError("local size ladder must stay off the living roster")
    models = list(payload["models"])
    slugs = [item["slug"] for item in models]
    if slugs != [
        "qwen25_14b",
        "llama31_8b",
        "qwen35_9b",
        "qwen36_35b",
    ]:
        raise RuntimeError(f"local size ladder drifted: {slugs}")
    living = {item["slug"] for item in living_models()}
    overlap = living.intersection(slugs)
    if overlap:
        raise RuntimeError(f"local size ladder overlaps living roster: {sorted(overlap)}")
    return models


def runnable_model_row(slug: str) -> dict[str, Any]:
    """Return a living, extra-runnable, or local-ladder roster row."""

    try:
        return model_by_slug(slug)
    except KeyError:
        for item in local_ladder_models():
            if item["slug"] == slug:
                return item
    raise KeyError(f"unknown runnable model {slug}")
