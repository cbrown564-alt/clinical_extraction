"""Named gan_llm_pre_post development slices."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.gan_pre_post_slices import (
    LUNA_HYBRID_MISSES,
    source_rows_for_slice,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)

ROOT = Path(__file__).resolve().parents[1]


def test_luna_hybrid_misses_are_the_living_dev750_errors() -> None:
    living = json.loads(
        (
            ROOT
            / "paper_experiments/gan/gan_llm_with_rules/gpt56luna/dev750/comparison.json"
        ).read_text(encoding="utf-8")
    )
    expected = [int(item) for item in living["incorrect_source_row_indices"]]
    got = source_rows_for_slice(LUNA_HYBRID_MISSES)
    assert got == expected
    assert len(got) == 87
    assert {79, 694, 1165} <= set(got)
    validation = {record.source_row_index for record in load_records_for_split("validation")}
    assert set(got) <= validation


def test_unknown_slice_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown gan_llm_pre_post slice"):
        source_rows_for_slice("easy_prefix")
