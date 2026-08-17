"""Living paper roster."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root

ROOT = discover_repo_root(start=Path(__file__))
ROSTER_PATH = ROOT / "paper_experiments/roster.json"


def living_models() -> list[dict[str, Any]]:
    """Return the six living paper models, Sol first."""

    payload = json.loads(ROSTER_PATH.read_text(encoding="utf-8"))
    living = list(payload["living"])
    slugs = [item["slug"] for item in living]
    if slugs != [
        "gpt56sol",
        "gpt56luna",
        "gemini37flash",
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
