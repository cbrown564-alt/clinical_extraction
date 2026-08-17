"""Always-on presence check for tracked paper fills."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPACT_ROOT = ROOT / "paper_experiments/exectv2_compact_ledger"
LIVING_SLUGS = (
    "gpt56sol",
    "gpt56luna",
    "gemini37flash",
    "deepseek_v4_flash",
    "qwen38_27b",
    "gemma4_26b",
)
COMPACT_PRESENT = {
    ("gpt56sol", "dev140", 140, "openai/gpt-5.6-sol"),
    ("gpt56sol", "test60", 59, "openai/gpt-5.6-sol"),
    ("gpt56luna", "dev140", 140, "openai/gpt-5.6-luna"),
    ("gemini37flash", "dev140", 140, "gemini/gemini-3.7-flash"),
    ("gemini37flash", "test60", 59, "gemini/gemini-3.7-flash"),
    ("deepseek_v4_flash", "dev140", 140, "deepseek/deepseek-v4-flash"),
    ("deepseek_v4_flash", "test60", 59, "deepseek/deepseek-v4-flash"),
    ("gemma4_26b", "dev140", 140, "ollama_chat/gemma4:26b"),
    ("gemma4_26b", "test60", 59, "ollama_chat/gemma4:26b"),
}


def test_paper_hybrid_fills_are_present() -> None:
    fills = json.loads(
        (ROOT / "paper_experiments/current_stack/latest/fills.json").read_text(
            encoding="utf-8"
        )
    )
    assert "hybrid" in fills
    assert "gan_test450" in fills["hybrid"]
    assert "exect_dev140" in fills["hybrid"]
    assert "exect_test60" in fills["hybrid"]
    e5 = json.loads(
        (
            ROOT
            / "paper_experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json"
        ).read_text(encoding="utf-8")
    )
    assert "dev140" in e5
    assert "test60" in e5


def test_roster_locks_the_living_six() -> None:
    roster = json.loads((ROOT / "paper_experiments/roster.json").read_text(encoding="utf-8"))
    assert roster["schema_version"] == "paper_experiments.roster.v1"
    living = tuple(row["slug"] for row in roster["living"])
    assert living == LIVING_SLUGS
    assert roster["living"][0]["method_identity"] is True
    historical = {row.get("slug") or row.get("identity") for row in roster["historical"]}
    assert "gpt41mini" in historical
    assert "qwen36_35b" in historical
    assert "deepseek_v4_flash_pre0731" in historical


def test_local_raws_inventory_covers_present_and_missing_cells() -> None:
    inventory = json.loads(
        (ROOT / "paper_experiments/local_raws.json").read_text(encoding="utf-8")
    )
    assert inventory["schema_version"] == "paper_experiments.local_raws.v1"
    present = {(row["model_slug"], row["program"], row["split"]) for row in inventory["present"]}
    missing = {(row["model_slug"], row["program"], row["split"]) for row in inventory["missing"]}
    assert present == {
        ("gpt56sol", "exectv2_compact_ledger", "dev140"),
        ("gpt56sol", "exectv2_compact_ledger", "test60"),
        ("gpt56luna", "exectv2_compact_ledger", "dev140"),
        ("gemini37flash", "exectv2_compact_ledger", "dev140"),
        ("gemini37flash", "exectv2_compact_ledger", "test60"),
        ("deepseek_v4_flash", "exectv2_compact_ledger", "dev140"),
        ("deepseek_v4_flash", "exectv2_compact_ledger", "test60"),
        ("gemma4_26b", "gan2026_hybrid_structured_events_v0.5", "dev750"),
        ("gemma4_26b", "gan2026_hybrid_structured_events_v0.5", "test450"),
        ("qwen38_27b", "gan2026_hybrid_structured_events_v0.5", "dev750"),
        ("qwen38_27b", "gan2026_hybrid_structured_events_v0.5", "test450"),
        ("gemma4_26b", "gan2026_llm_only_canonical_pipeline_v0.8", "dev750"),
        ("gemma4_26b", "gan2026_llm_only_canonical_pipeline_v0.8", "test450"),
        ("gemma4_26b", "exectv2_compact_ledger", "dev140"),
        ("gemma4_26b", "exectv2_compact_ledger", "test60"),
    }
    assert missing == {
        ("qwen38_27b", "exectv2_compact_ledger", "dev140"),
        ("qwen38_27b", "exectv2_compact_ledger", "test60"),
        ("gpt56luna", "exectv2_compact_ledger", "test60"),
        ("qwen38_27b", "gan2026_llm_only_canonical_pipeline_v0.8", "dev750"),
        ("qwen38_27b", "gan2026_llm_only_canonical_pipeline_v0.8", "test450"),
    }
    gan_fields = set(inventory["strip"]["gan2026"])
    exect_fields = set(inventory["strip"]["exectv2"])
    for row in inventory["present"]:
        path = ROOT / row["path"]
        assert path.is_file()
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) == row["n"]
        empty = 0
        ids: set[object] = set()
        expected_fields = exect_fields if row["program"].startswith("exectv2") else gan_fields
        id_field = "letter_id" if "letter_id" in expected_fields else "source_row_index"
        for line in lines:
            payload = json.loads(line)
            assert set(payload) == expected_fields
            assert payload["prompt_version"] == row["program"]
            raw = payload["raw_output"]
            assert isinstance(raw, str)
            if not raw.strip():
                empty += 1
            ids.add(payload[id_field])
        assert len(ids) == row["n"]
        assert empty == row["empty_raw_count"]
        if row["split"] in {"test450", "test60"}:
            assert row["row_policy"] == "aggregate_only"


def test_compact_paper_cells_have_raw_and_hybrid() -> None:
    for slug, split, rows, model in COMPACT_PRESENT:
        comparison = json.loads(
            (COMPACT_ROOT / slug / split / "comparison.json").read_text(encoding="utf-8")
        )
        assert comparison["split"] == split
        assert comparison["row_count"] == rows
        assert comparison["model"] == model
        if split == "test60":
            assert comparison["row_policy"] == "aggregate_only"
            assert "letter_ids" not in comparison
            assert "changed_rows" not in comparison
        for arm, prompt in (
            ("compact_ledger", "exectv2_compact_ledger"),
            ("full_ledger", "exectv2_full_ledger"),
        ):
            summary = comparison["arms"][arm]
            assert "raw_headline_f1" in summary
            assert "hybrid_headline_f1" in summary
            sidecar = COMPACT_ROOT / slug / split / arm / "structured.jsonl"
            text = sidecar.read_text(encoding="utf-8")
            lines = [line for line in text.splitlines() if line.strip()]
            assert len(lines) == rows
            row = json.loads(lines[0])
            assert set(row) == {"letter_id", "prompt_version", "raw_output"}
            assert row["prompt_version"] == prompt
