"""Always-on contract for the Holgate-like 250-letter development sample."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.paper.gan_holgate_dev250 import (
    SAMPLE_ID,
    SAMPLE_SIZE,
    draw_holgate_dev250_indices,
    holgate_dev250_sample_payload,
    validation_source_row_indices,
)

FROZEN = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "research"
    / "gan2026"
    / "gan_holgate_like_dev250_v1.json"
)


def test_holgate_dev250_is_a_frozen_validation_subset() -> None:
    pool = validation_source_row_indices()
    drawn = draw_holgate_dev250_indices()
    payload = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert len(pool) == 750
    assert len(drawn) == SAMPLE_SIZE
    assert drawn == sorted(drawn)
    assert set(drawn) <= set(pool)
    assert payload == holgate_dev250_sample_payload()
    assert payload["sample_id"] == SAMPLE_ID
    assert payload["source_row_indices"] == drawn
