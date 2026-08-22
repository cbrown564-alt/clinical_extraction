"""Promote living Gan dev750 cells into the rectangular frontend panel."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.gan_panel import (
    promote_gan,
    promote_gan_dev750,
    rebuild_dev750_panel,
)
from clinical_extraction.paper.roster import living_models


def _patch_panel_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paper = tmp_path / "paper_experiments"
    gan = paper / "gan"
    monkeypatch.setattr("clinical_extraction.paper.gan_panel.ROOT", tmp_path)
    monkeypatch.setattr(
        "clinical_extraction.paper.gan_panel.WORK_ROOT",
        tmp_path / "experiments/paper",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.gan_panel.HOLDOUT_ROOT",
        tmp_path / "scratch/holdout/paper",
    )
    monkeypatch.setattr("clinical_extraction.paper.gan_panel.PAPER_GAN", gan)
    monkeypatch.setattr(
        "clinical_extraction.paper.gan_panel.PANEL_PATH",
        gan / "dev750_panel.json",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.gan_panel.INVENTORY_PATH",
        paper / "inventory.json",
    )


def _write_work_cell(root: Path, method: str, slug: str, *, label: str) -> None:
    cell = root / "experiments/paper" / method / slug / "dev750"
    cell.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(750):
        source = 10 + index
        rows.append(
            {
                "source_row_index": source,
                "prompt_version": method,
                "raw_output": f'{{"final_label": "{label}"}}',
                "call_error": None,
                "decision_record": {"final_label": label} if method == "gan_llm_only" else None,
                "structured_record": (
                    None
                    if method == "gan_llm_only"
                    else {"selection": {"final_label": label}}
                ),
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
            }
        )
    (cell / "rows.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    (cell / "comparison.json").write_text(
        json.dumps(
            {
                "method": method,
                "split": "dev750",
                "prompt_version": method,
                "reasoning_effort": "low",
                "summary": {
                    "purist_correct": 750,
                    "purist_accuracy": 1.0,
                    "examples": 750,
                },
            }
        ),
        encoding="utf-8",
    )


def test_promote_writes_replay_scored_and_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "gan_llm_only", "grok46", label="1 per month")
    inventory = {
        "schema_version": "paper_experiments.inventory.v1",
        "strip": {"gan": ["source_row_index", "prompt_version", "raw_output"]},
        "present": [],
        "missing": [
            {
                "method": "gan_llm_with_rules",
                "status": "missing",
                "note": "old blob",
            }
        ],
    }
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps(inventory),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)

    payload = promote_gan_dev750("gan_llm_only", "grok46")
    dest = tmp_path / "paper_experiments/gan/gan_llm_only/grok46/dev750"
    replay = json.loads((dest / "rows.jsonl").read_text(encoding="utf-8").splitlines()[0])
    scored = json.loads((dest / "scored.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(replay) == {"source_row_index", "prompt_version", "raw_output"}
    assert scored["predicted_label"] == "1 per month"
    assert scored["letter_id"] == str(scored["source_row_index"])
    assert scored["purist_correct"] is True
    panel = rebuild_dev750_panel()
    assert panel["method_identity"] == "gemini37flash"
    assert panel["living_effort"]["hosted_reasoning"] == "low"
    assert panel["methods"] == ["rules_only", "llm_extract", "llm_encode", "llm_select"]
    assert len(panel["cells"]) == 24
    assert all(cell["status"] == "pending" for cell in panel["cells"])
    assert not any(cell["method"] in {"gan_llm_only", "gan_llm_with_rules"} for cell in panel["cells"])
    assert payload["cell"]["n"] == 750
    slugs = [item["slug"] for item in living_models()]
    assert panel["models"] == slugs
    synced = json.loads((tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8"))
    assert any(
        row["model_slug"] == "grok46"
        and row["method"] == "gan_llm_only"
        and row["split"] == "dev750"
        for row in synced["present"]
    )
    assert not any(row.get("note") == "old blob" for row in synced["missing"])
    assert {
        (row["model_slug"], row["method"])
        for row in synced["missing"]
        if row.get("split") == "dev750"
    } == {
        (slug, method)
        for slug in slugs
        for method in ("gan_llm_only", "gan_llm_with_rules")
        if (slug, method) != ("grok46", "gan_llm_only")
    }


def test_rebuild_keeps_historical_present_when_panel_slot_is_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    historical = {
        "model_slug": "gemma4_26b",
        "model": "ollama_chat/gemma4:26b",
        "method": "gan_llm_only",
        "replay_alias": "gan_llm_only",
        "split": "dev750",
        "n": 750,
        "row_policy": "development_review_permitted",
        "path": "paper_experiments/gan/gan_llm_only/gemma4_26b/dev750/rows.jsonl",
        "status": "present",
        "empty_raw_count": 8,
    }
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps(
            {
                "schema_version": "paper_experiments.inventory.v1",
                "strip": {"gan": ["source_row_index", "prompt_version", "raw_output"]},
                "present": [historical],
                "missing": [],
            }
        ),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)
    panel = rebuild_dev750_panel()
    assert not any(cell["method"] == "gan_llm_only" for cell in panel["cells"])
    synced = json.loads((tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8"))
    assert historical in synced["present"]


def test_promote_rejects_non_living_effort_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "gan_llm_only", "grok46", label="1 per month")
    comparison_path = tmp_path / "experiments/paper/gan_llm_only/grok46/dev750/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison["reasoning_effort"] = "high"
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps({"present": [], "missing": []}),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="living low-effort"):
        promote_gan_dev750("gan_llm_only", "grok46")


def _write_holdout_work_cell(root: Path, method: str, slug: str) -> None:
    cell = root / "scratch/holdout/paper" / method / slug / "test450"
    cell.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(450):
        rows.append(
            {
                "source_row_index": 10 + index,
                "prompt_version": method,
                "raw_output": '{"final_label": "1 per month"}',
                "call_error": None,
                "decision_record": {"final_label": "1 per month"},
                "comparison": {"purist_correct": True},
                "note_text": "do-not-promote",
            }
        )
    (cell / "rows.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    (cell / "comparison.json").write_text(
        json.dumps(
            {
                "method": method,
                "split": "test450",
                "prompt_version": method,
                "reasoning_effort": "low",
                "row_policy": "aggregate_only",
                "summary": {
                    "purist_correct": 327,
                    "purist_accuracy": 0.7267,
                    "examples": 450,
                },
            }
        ),
        encoding="utf-8",
    )


def test_promote_gan_test450_strips_replay_and_updates_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_holdout_work_cell(tmp_path, "gan_llm_only", "grok46")
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps(
            {
                "schema_version": "paper_experiments.inventory.v1",
                "strip": {"gan": ["source_row_index", "prompt_version", "raw_output"]},
                "present": [],
                "missing": [
                    {
                        "model_slug": "grok46",
                        "method": "gan_llm_only",
                        "split": "test450",
                        "status": "missing",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)

    payload = promote_gan("gan_llm_only", "grok46", "test450")
    dest = tmp_path / "paper_experiments/gan/gan_llm_only/grok46/test450"
    replay = json.loads((dest / "rows.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(replay) == {"source_row_index", "prompt_version", "raw_output"}
    assert not (dest / "scored.jsonl").is_file()
    comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["row_policy"] == "aggregate_only"
    assert "incorrect_source_row_indices" not in comparison
    assert payload["cell"]["n"] == 450
    assert payload["cell"]["row_policy"] == "aggregate_only"
    synced = json.loads((tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8"))
    assert any(
        row["model_slug"] == "grok46"
        and row["method"] == "gan_llm_only"
        and row["split"] == "test450"
        and row["row_policy"] == "aggregate_only"
        for row in synced["present"]
    )
    assert not any(
        row.get("model_slug") == "grok46" and row.get("split") == "test450"
        for row in synced["missing"]
    )


def test_promote_gan_llm_pre_post_writes_inventory_without_changing_the_two_method_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "gan_llm_pre_post", "gpt56luna", label="1 per month")
    _write_holdout_work_cell(tmp_path, "gan_llm_pre_post", "gpt56luna")
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps(
            {
                "schema_version": "paper_experiments.inventory.v1",
                "strip": {"gan": ["source_row_index", "prompt_version", "raw_output"]},
                "present": [],
                "missing": [],
            }
        ),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)

    development = promote_gan("gan_llm_pre_post", "gpt56luna", "dev750")
    holdout = promote_gan("gan_llm_pre_post", "gpt56luna", "test450")

    dev_dest = tmp_path / "paper_experiments/gan/gan_llm_pre_post/gpt56luna/dev750"
    holdout_dest = tmp_path / "paper_experiments/gan/gan_llm_pre_post/gpt56luna/test450"
    assert (dev_dest / "rows.jsonl").is_file()
    assert (dev_dest / "scored.jsonl").is_file()
    assert (holdout_dest / "rows.jsonl").is_file()
    assert not (holdout_dest / "scored.jsonl").is_file()
    assert development["cell"]["method"] == "gan_llm_pre_post"
    assert holdout["cell"]["row_policy"] == "aggregate_only"
    assert "panel" not in development
    panel = rebuild_dev750_panel()
    assert panel["methods"] == ["rules_only", "llm_extract", "llm_encode", "llm_select"]
    assert len(panel["cells"]) == 24
    synced = json.loads((tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8"))
    present = {(row["model_slug"], row["method"], row["split"]) for row in synced["present"]}
    assert ("gpt56luna", "gan_llm_pre_post", "dev750") in present
    assert ("gpt56luna", "gan_llm_pre_post", "test450") in present


def test_promote_gan_later_stage_writes_inventory_without_changing_the_two_method_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "gan_llm_encode", "gemini37flash", label="1 per day")
    _write_holdout_work_cell(tmp_path, "gan_llm_encode", "gemini37flash")
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps(
            {
                "schema_version": "paper_experiments.inventory.v1",
                "strip": {"gan": ["source_row_index", "prompt_version", "raw_output"]},
                "present": [],
                "missing": [],
            }
        ),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)

    development = promote_gan("gan_llm_encode", "gemini37flash", "dev750")
    holdout = promote_gan("gan_llm_encode", "gemini37flash", "test450")

    assert development["cell"]["method"] == "gan_llm_encode"
    assert holdout["cell"]["row_policy"] == "aggregate_only"
    assert "panel" not in development
    panel = rebuild_dev750_panel()
    assert panel["methods"] == ["rules_only", "llm_extract", "llm_encode", "llm_select"]
    synced = json.loads((tmp_path / "paper_experiments/inventory.json").read_text())
    present = {(row["model_slug"], row["method"], row["split"]) for row in synced["present"]}
    assert ("gemini37flash", "gan_llm_encode", "dev750") in present
    assert ("gemini37flash", "gan_llm_encode", "test450") in present


def test_promote_gan_test450_rejects_row_level_comparison(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_holdout_work_cell(tmp_path, "gan_llm_with_rules", "grok46")
    comparison_path = (
        tmp_path / "scratch/holdout/paper/gan_llm_with_rules/grok46/test450/comparison.json"
    )
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison["incorrect_source_row_indices"] = [10]
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    (tmp_path / "paper_experiments").mkdir()
    (tmp_path / "paper_experiments/inventory.json").write_text(
        json.dumps({"present": [], "missing": []}),
        encoding="utf-8",
    )
    _patch_panel_paths(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="aggregate-only"):
        promote_gan("gan_llm_with_rules", "grok46", "test450")
