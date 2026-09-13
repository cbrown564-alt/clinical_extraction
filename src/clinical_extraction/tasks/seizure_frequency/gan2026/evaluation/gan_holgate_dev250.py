"""Prespecified 250-letter Holgate-like development sample."""

from __future__ import annotations

import json
import random
from pathlib import Path

from clinical_extraction.core.paths import discover_repo_root

SAMPLE_ID = "gan_holgate_like_dev250_v1"
SAMPLE_SEED = 20260830
SAMPLE_SIZE = 250
SPLIT_MANIFEST = "gan2026_split_v1"


def validation_source_row_indices(root: Path | None = None) -> list[int]:
    """Return sorted validation indices from the locked Gan split."""

    repo = root or discover_repo_root(start=Path(__file__))
    path = repo / "data" / "Gan (2026)" / "splits" / "gan2026_split_v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return sorted(int(index) for index in payload["splits"]["validation"]["source_row_indices"])


def draw_holgate_dev250_indices(root: Path | None = None) -> list[int]:
    """Draw the frozen Holgate-like 250-letter development sample."""

    pool = validation_source_row_indices(root)
    drawn = random.Random(SAMPLE_SEED).sample(pool, SAMPLE_SIZE)
    return sorted(drawn)


def holgate_dev250_sample_payload(root: Path | None = None) -> dict[str, object]:
    """Machine-readable sample identity."""

    indices = draw_holgate_dev250_indices(root)
    return {
        "sample_id": SAMPLE_ID,
        "seed": SAMPLE_SEED,
        "size": SAMPLE_SIZE,
        "split": "dev750",
        "split_machine": "validation",
        "split_manifest": SPLIT_MANIFEST,
        "source_row_indices": indices,
    }
