"""Five-cell writer assembles the paper table from living cells."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.paper.five_cell import (
    _exect_rules_stage,
    _gan_rules_stage,
    write_five_cell_grid,
)

ROOT = Path(__file__).resolve().parents[1]


def test_gan_rules_stage_stops_read_promoted_owner() -> None:
    assert _gan_rules_stage("test450", "find") == 190
    assert _gan_rules_stage("test450", "encode") == 284
    assert _gan_rules_stage("test450", "select") == 325
    assert _gan_rules_stage("dev750", "select") == 691


def test_exect_rules_find_stop_reads_frozen_recognise_key() -> None:
    assert _exect_rules_stage("dev140", "find") == 0.9012
    assert _exect_rules_stage("dev140", "encode") == 0.915


def test_write_five_cell_keeps_curated_exect_grid() -> None:
    payload = write_five_cell_grid(
        "exect_llm_extract",
        slug="gemini37flash",
        split="test60",
    )
    generated = json.loads((ROOT / payload["artifact"]).read_text(encoding="utf-8"))
    curated = json.loads(
        (
            ROOT
            / "paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json"
        ).read_text(encoding="utf-8")
    )
    assert generated["headline"] == "select"
    assert generated["scorer"] == "4-family micro F1"
    assert set(generated["cells"]) == set(curated["cells"])
    assert generated["cells"]["llm_extract_then_rules"]["select"] == curated["cells"][
        "llm_extract_then_rules"
    ]["select"]
    assert generated["cells"]["rules"]["select"] == curated["cells"]["rules"]["select"]
    assert generated["cells"]["llm"]["select"] == curated["cells"]["llm"]["select"]
    assert (
        generated["cells"]["llm_extract_encode_then_select_rules"]["select"]
        == curated["cells"]["llm_extract_encode_then_select_rules"]["select"]
    )
    assert payload["curated"]
    curated_path = (
        ROOT
        / "paper_experiments/exect/five_cell_grid/gemini37flash/test60/comparison.json"
    )
    assert curated_path.is_file()
