"""Named development slices for gan_llm_pre_post. Holdout is not allowed."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.core.paths import discover_repo_root

ROOT = discover_repo_root(start=Path(__file__))
LUNA_HYBRID_MISSES = "luna_hybrid_misses"
LUNA_HYBRID_COMPARISON = (
    ROOT / "paper_experiments/gan/gan_llm_with_rules/gpt56luna/dev750/comparison.json"
)
KNOWN_SLICES = (LUNA_HYBRID_MISSES,)


def source_rows_for_slice(name: str) -> list[int]:
    """Return locked development source_row_index values for a named slice."""

    if name != LUNA_HYBRID_MISSES:
        raise ValueError(
            f"unknown gan_llm_pre_post slice {name!r}; expected one of {KNOWN_SLICES}"
        )
    payload = json.loads(LUNA_HYBRID_COMPARISON.read_text(encoding="utf-8"))
    if payload.get("split") != "dev750":
        raise RuntimeError("luna hybrid miss slice is locked to the living dev750 cell")
    rows = [int(item) for item in payload["incorrect_source_row_indices"]]
    if len(rows) != len(set(rows)):
        raise RuntimeError("luna hybrid miss list has duplicate source_row_index values")
    return rows
