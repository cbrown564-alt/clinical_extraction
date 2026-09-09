"""Living paper roster."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root

ROOT = discover_repo_root(start=Path(__file__))
ROSTER_PATH = ROOT / "paper_experiments/roster.json"
LOCAL_LADDER_PATH = ROOT / "paper_experiments/local_size_ladder.json"


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


def model_by_slug(slug: str) -> dict[str, Any]:
    """Return one living roster row."""

    for item in living_models():
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
    """Return a living roster row or a local-ladder row."""

    try:
        return model_by_slug(slug)
    except KeyError:
        for item in local_ladder_models():
            if item["slug"] == slug:
                return item
    raise KeyError(f"unknown runnable model {slug}")
