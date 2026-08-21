"""Always-on presence check for tracked paper fills."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECT_HYBRID_ROOT = ROOT / "paper_experiments/exect/exect_llm_pre_post"
LIVING_SLUGS = (
    "grok46",
    "gpt56luna",
    "gemini37flash",
    "deepseek_v4_flash",
    "qwen38_27b",
    "gemma4_26b",
)
EXECT_HYBRID_PRESENT = {
    ("gpt56luna", "dev140", 140, "openai/gpt-5.6-luna"),
    ("gpt56luna", "test60", 59, "openai/gpt-5.6-luna"),
    ("gemini37flash", "dev140", 140, "gemini/gemini-3.7-flash"),
    ("gemini37flash", "test60", 59, "gemini/gemini-3.7-flash"),
    ("deepseek_v4_flash", "dev140", 140, "deepseek/deepseek-v4-flash"),
    ("deepseek_v4_flash", "test60", 59, "deepseek/deepseek-v4-flash"),
    ("gemma4_26b", "dev140", 140, "ollama_chat/gemma4:26b"),
    ("gemma4_26b", "test60", 59, "ollama_chat/gemma4:26b"),
}


def test_paper_hybrid_fills_are_present() -> None:
    e5 = json.loads(
        (ROOT / "paper_experiments/exect/exect_rules/dev140.json").read_text(
            encoding="utf-8"
        )
    )
    assert e5["dev140"]["four_family_headline_f1"] == 0.9042
    assert e5["test60"]["four_family_headline_f1"] == 0.7937
    test60 = json.loads(
        (ROOT / "paper_experiments/exect/exect_rules/test60.json").read_text(
            encoding="utf-8"
        )
    )
    assert test60["split"] == "test60"
    assert test60["row_policy"] == "aggregate_only"


def test_roster_locks_the_living_six() -> None:
    roster = json.loads((ROOT / "paper_experiments/roster.json").read_text(encoding="utf-8"))
    assert roster["schema_version"] == "paper_experiments.roster.v1"
    living = tuple(row["slug"] for row in roster["living"])
    assert living == LIVING_SLUGS
    assert roster["living"][0]["method_identity"] is True
    historical_slugs = {row.get("slug") for row in roster["historical"]}
    assert "gpt56sol" in historical_slugs
    assert "grok46" not in historical_slugs


def test_inventory_covers_present_and_missing_cells() -> None:
    inventory = json.loads(
        (ROOT / "paper_experiments/inventory.json").read_text(encoding="utf-8")
    )
    assert inventory["schema_version"] == "paper_experiments.inventory.v1"
    present = {(row["model_slug"], row["method"], row["split"]) for row in inventory["present"]}
    missing_methods = {row["method"] for row in inventory["missing"]}
    assert present == {
        ("grok46", "exect_llm_pre_post", "dev140"),
        ("grok46", "exect_llm_pre_post", "test60"),
        ("grok46", "exect_llm_only", "dev140"),
        ("grok46", "exect_llm_only", "test60"),
        ("gpt56luna", "exect_llm_pre_post", "dev140"),
        ("gpt56luna", "exect_llm_pre_post", "test60"),
        ("gpt56luna", "exect_llm_only", "dev140"),
        ("gpt56luna", "exect_llm_only", "test60"),
        ("gemini37flash", "exect_llm_pre_post", "dev140"),
        ("gemini37flash", "exect_llm_pre_post", "test60"),
        ("gemini37flash", "exect_llm_only", "dev140"),
        ("gemini37flash", "exect_llm_only", "test60"),
        ("deepseek_v4_flash", "exect_llm_pre_post", "dev140"),
        ("deepseek_v4_flash", "exect_llm_pre_post", "test60"),
        ("deepseek_v4_flash", "exect_llm_only", "dev140"),
        ("deepseek_v4_flash", "exect_llm_only", "test60"),
        ("gemma4_26b", "exect_llm_pre_post", "dev140"),
        ("gemma4_26b", "exect_llm_pre_post", "test60"),
        ("gemma4_26b", "gan_llm_only", "dev750"),
        ("gemma4_26b", "gan_llm_only", "test450"),
        ("grok46", "gan_llm_only", "dev750"),
        ("grok46", "gan_llm_only", "test450"),
        ("grok46", "gan_llm_with_rules", "dev750"),
        ("grok46", "gan_llm_with_rules", "test450"),
        ("gpt56luna", "gan_llm_only", "dev750"),
        ("gpt56luna", "gan_llm_with_rules", "dev750"),
        ("gpt56luna", "gan_llm_with_rules", "test450"),
        ("gpt56luna", "gan_llm_pre_post", "dev750"),
        ("gpt56luna", "gan_llm_pre_post", "test450"),
        ("gemini37flash", "gan_llm_only", "dev750"),
        ("gemini37flash", "gan_llm_only", "test450"),
        ("gemini37flash", "gan_llm_with_rules", "dev750"),
        ("gemini37flash", "gan_llm_with_rules", "test450"),
    }
    assert "gan_llm_with_rules" in missing_methods
    missing_cells = {
        (row.get("model_slug"), row["method"], row.get("split")) for row in inventory["missing"]
    }
    assert ("qwen38_27b", "exect_llm_pre_post", "dev140") in missing_cells
    assert ("grok46", "exect_llm_only", "dev140") not in missing_cells
    assert ("gemini37flash", "exect_llm_only", "dev140") not in missing_cells
    assert ("gpt56luna", "exect_llm_only", "dev140") not in missing_cells
    assert ("grok46", "exect_llm_pre_post", "dev140") not in missing_cells
    assert ("grok46", "exect_llm_pre_post", "test60") not in missing_cells
    assert ("grok46", "gan_llm_only", "test450") not in missing_cells
    assert ("grok46", "gan_llm_with_rules", "test450") not in missing_cells
    assert ("deepseek_v4_flash", "gan_llm_only", "dev750") in missing_cells
    assert ("deepseek_v4_flash", "gan_llm_with_rules", "dev750") in missing_cells
    assert ("qwen38_27b", "gan_llm_only", "dev750") in missing_cells
    assert ("qwen38_27b", "gan_llm_with_rules", "dev750") in missing_cells
    assert ("gemma4_26b", "gan_llm_with_rules", "dev750") in missing_cells
    assert ("grok46", "gan_llm_with_rules", "dev750") not in missing_cells
    gan_fields = set(inventory["strip"]["gan"])
    exect_fields = set(inventory["strip"]["exect"])
    for row in inventory["present"]:
        path = ROOT / row["path"]
        assert path.is_file()
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) == row["n"]
        empty = 0
        ids: set[object] = set()
        expected_fields = exect_fields if row["method"].startswith("exect") else gan_fields
        id_field = "letter_id" if "letter_id" in expected_fields else "source_row_index"
        for line in lines:
            payload = json.loads(line)
            assert set(payload) == expected_fields
            assert payload["prompt_version"] == row["replay_alias"]
            raw = payload["raw_output"]
            assert isinstance(raw, str)
            if not raw.strip():
                empty += 1
            ids.add(payload[id_field])
        assert len(ids) == row["n"]
        assert empty == row["empty_raw_count"]
        if row["split"] in {"test450", "test60"}:
            assert row["row_policy"] == "aggregate_only"


def test_gan_dev750_panel_is_rectangular() -> None:
    panel = json.loads(
        (ROOT / "paper_experiments/gan/dev750_panel.json").read_text(encoding="utf-8")
    )
    assert panel["schema_version"] == "paper_experiments.gan.dev750_panel.v1"
    assert panel["split"] == "dev750"
    assert panel["method_identity"] == "grok46"
    assert panel["living_effort"]["hosted_reasoning"] == "low"
    assert panel["models"] == list(LIVING_SLUGS)
    assert panel["methods"] == ["gan_llm_only", "gan_llm_with_rules"]
    assert len(panel["cells"]) == 12
    present = {
        (cell["model_slug"], cell["method"])
        for cell in panel["cells"]
        if cell["status"] == "present"
    }
    pending = {
        (cell["model_slug"], cell["method"])
        for cell in panel["cells"]
        if cell["status"] == "pending"
    }
    assert present == {
        ("grok46", "gan_llm_only"),
        ("grok46", "gan_llm_with_rules"),
        ("gpt56luna", "gan_llm_only"),
        ("gpt56luna", "gan_llm_with_rules"),
        ("gemini37flash", "gan_llm_only"),
        ("gemini37flash", "gan_llm_with_rules"),
    }
    assert pending == {
        ("deepseek_v4_flash", "gan_llm_only"),
        ("deepseek_v4_flash", "gan_llm_with_rules"),
        ("qwen38_27b", "gan_llm_only"),
        ("qwen38_27b", "gan_llm_with_rules"),
        ("gemma4_26b", "gan_llm_only"),
        ("gemma4_26b", "gan_llm_with_rules"),
    }
    for cell in panel["cells"]:
        if cell["status"] != "present":
            continue
        scored_path = ROOT / cell["scored"]
        rows = [
            json.loads(line)
            for line in scored_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 750
        first = rows[0]
        assert first["letter_id"] == str(first["source_row_index"])
        assert {"source_row_index", "letter_id", "predicted_label", "purist_correct"} <= set(first)


def test_exect_dev140_panel_is_rectangular() -> None:
    panel = json.loads(
        (ROOT / "paper_experiments/exect/dev140_panel.json").read_text(encoding="utf-8")
    )
    assert panel["schema_version"] == "paper_experiments.exect.dev140_panel.v2"
    assert panel["split"] == "dev140"
    assert panel["method_identity"] == "grok46"
    assert panel["living_effort"]["hosted_reasoning"] == "low"
    assert panel["models"] == list(LIVING_SLUGS)
    assert panel["methods"] == [
        "rules_only",
        "llm_schema",
        "llm_encode",
        "llm_revise",
        "llm_pre_post",
    ]
    assert panel["request_methods"] == ["exect_llm_only", "exect_llm_pre_post"]
    assert len(panel["cells"]) == 30
    present = {
        (cell["model_slug"], cell["method"])
        for cell in panel["cells"]
        if cell["status"] == "present"
    }
    pending = {
        (cell["model_slug"], cell["method"])
        for cell in panel["cells"]
        if cell["status"] == "pending"
    }
    assert {("grok46", "rules_only"), ("grok46", "llm_pre_post")} <= present
    assert ("qwen38_27b", "llm_pre_post") in pending
    for cell in panel["cells"]:
        if cell["status"] != "present" or not cell.get("scored"):
            continue
        scored_path = ROOT / cell["scored"]
        rows = [
            json.loads(line)
            for line in scored_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 140
        first = rows[0]
        assert first["letter_id"].startswith("EA")
        if cell["method"] == "llm_pre_post":
            assert first["method"] == "exect_llm_pre_post"
            assert {
                "hybrid_headline_f1",
                "hybrid_four_family_letter_exact",
            } <= set(first)


def test_exect_hybrid_cells_have_raw_and_hybrid() -> None:
    for slug, split, rows, model in EXECT_HYBRID_PRESENT:
        comparison = json.loads(
            (EXECT_HYBRID_ROOT / slug / split / "comparison.json").read_text(
                encoding="utf-8"
            )
        )
        assert comparison["split"] == split
        assert comparison["row_count"] == rows
        assert comparison["model"] == model
        if split == "test60":
            assert comparison["row_policy"] == "aggregate_only"
            assert "letter_ids" not in comparison
            assert "changed_rows" not in comparison
        compact = (
            comparison["arms"].get("exect_llm_pre_post")
            or comparison["arms"].get("exect_llm_with_rules")
            or comparison["arms"]["compact_ledger"]
        )
        assert "raw_headline_f1" in compact
        assert "hybrid_headline_f1" in compact
        hybrid_row = json.loads(
            (EXECT_HYBRID_ROOT / slug / split / "structured.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[0]
        )
        assert set(hybrid_row) == {"letter_id", "prompt_version", "raw_output"}
        assert hybrid_row["prompt_version"] == "exect_llm_pre_post"
        lines = [
            line
            for line in (EXECT_HYBRID_ROOT / slug / split / "structured.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        assert len(lines) == rows
