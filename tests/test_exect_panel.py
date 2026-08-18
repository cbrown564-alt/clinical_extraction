"""Promote living ExECT Compact dev140 cells into the rectangular frontend panel."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.exect_panel import (
    promote_exect,
    promote_exect_dev140,
    rebuild_dev140_panel,
)
from clinical_extraction.paper.roster import living_models


def _patch_panel_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paper = tmp_path / "paper_experiments"
    exect = paper / "exect"
    monkeypatch.setattr("clinical_extraction.paper.exect_panel.ROOT", tmp_path)
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.WORK_ROOT",
        tmp_path / "experiments/paper/exect_llm_with_rules",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.HOLDOUT_ROOT",
        tmp_path / "scratch/holdout/paper/exect_llm_with_rules",
    )
    monkeypatch.setattr("clinical_extraction.paper.exect_panel.PAPER_EXECT", exect)
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.PANEL_PATH",
        exect / "dev140_panel.json",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.INVENTORY_PATH",
        paper / "inventory.json",
    )


def _write_work_cell(root: Path, slug: str) -> None:
    cell = root / "experiments/paper/exect_llm_with_rules" / slug / "dev140"
    nested = cell / "exect_llm_with_rules"
    nested.mkdir(parents=True, exist_ok=True)
    structured = []
    metrics = []
    for index in range(140):
        letter_id = f"EA{index + 1:04d}"
        structured.append(
            {
                "letter_id": letter_id,
                "prompt_version": "exectv2_compact_ledger",
                "raw_output": '{"mentions":[]}',
                "gold_mentions": ["do-not-promote"],
                "predicted_mentions": [],
            }
        )
        metrics.append(
            {
                "arm": "exect_llm_with_rules",
                "prompt_version": "exectv2_compact_ledger",
                "letter_id": letter_id,
                "raw_headline_prf": {"f1": 0.5},
                "hybrid_headline_prf": {"f1": 0.8},
                "raw_four_family_letter_exact": False,
                "hybrid_four_family_letter_exact": True,
                "family_letter_exact": {
                    "Diagnosis": {"raw": False, "hybrid": True},
                },
                "quality": {"parse": 0, "schema": 0},
            }
        )
    (nested / "structured.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in structured),
        encoding="utf-8",
    )
    (nested / "letter_metrics.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in metrics),
        encoding="utf-8",
    )
    (cell / "comparison.json").write_text(
        json.dumps(
            {
                "method": "exect_llm_with_rules",
                "split": "dev140",
                "reasoning_effort": "low",
                "row_count": 140,
                "arms": {
                    "exect_llm_with_rules": {
                        "raw_headline_f1": 0.5,
                        "hybrid_headline_f1": 0.8,
                    }
                },
            }
        ),
        encoding="utf-8",
    )


def _write_inventory(tmp_path: Path, *, present: list[dict[str, object]]) -> None:
    paper = tmp_path / "paper_experiments"
    paper.mkdir(exist_ok=True)
    (paper / "inventory.json").write_text(
        json.dumps(
            {
                "schema_version": "paper_experiments.inventory.v1",
                "strip": {"exect": ["letter_id", "prompt_version", "raw_output"]},
                "present": present,
                "missing": [
                    {
                        "model_slug": "grok46",
                        "method": "exect_llm_with_rules",
                        "split": "dev140",
                        "status": "missing",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_promote_strips_replay_and_writes_scored_panel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "grok46")
    _write_inventory(tmp_path, present=[])
    _patch_panel_paths(tmp_path, monkeypatch)

    payload = promote_exect_dev140("grok46")
    dest = tmp_path / "paper_experiments/exect/exect_llm_with_rules/grok46/dev140"
    replay = json.loads((dest / "structured.jsonl").read_text(encoding="utf-8").splitlines()[0])
    scored = json.loads((dest / "scored.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(replay) == {"letter_id", "prompt_version", "raw_output"}
    assert replay["prompt_version"] == "exectv2_compact_ledger"
    assert scored["letter_id"] == "EA0001"
    assert scored["hybrid_four_family_letter_exact"] is True
    assert scored["parse_ok"] is True
    panel = rebuild_dev140_panel()
    assert panel["method_identity"] == "grok46"
    assert panel["living_effort"]["hosted_reasoning"] == "low"
    assert len(panel["cells"]) == 6
    present = [cell for cell in panel["cells"] if cell["status"] == "present"]
    pending = [cell for cell in panel["cells"] if cell["status"] == "pending"]
    assert [cell["model_slug"] for cell in present] == ["grok46"]
    assert len(pending) == 5
    assert payload["cell"]["n"] == 140
    assert panel["models"] == [item["slug"] for item in living_models()]
    synced = json.loads(
        (tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8")
    )
    assert any(
        row["model_slug"] == "grok46"
        and row["method"] == "exect_llm_with_rules"
        and row["split"] == "dev140"
        for row in synced["present"]
    )
    assert not any(
        row.get("model_slug") == "grok46" and row.get("split") == "dev140"
        for row in synced["missing"]
    )
    assert any(
        row.get("model_slug") == "qwen38_27b" and row.get("split") == "dev140"
        for row in synced["missing"]
    )


def test_rebuild_keeps_existing_compact_present_without_cell_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "paper_experiments/exect/exect_llm_with_rules/gpt56luna/dev140"
    dest.mkdir(parents=True)
    dest.joinpath("structured.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "letter_id": f"EA{index + 1:04d}",
                    "prompt_version": "exectv2_compact_ledger",
                    "raw_output": "{}",
                }
            )
            + "\n"
            for index in range(140)
        ),
        encoding="utf-8",
    )
    dest.joinpath("comparison.json").write_text(
        json.dumps(
            {
                "split": "dev140",
                "arms": {"compact_ledger": {"hybrid_headline_f1": 0.8818}},
            }
        ),
        encoding="utf-8",
    )
    historical = {
        "model_slug": "gpt56luna",
        "model": "openai/gpt-5.6-luna",
        "method": "exect_llm_with_rules",
        "replay_alias": "exectv2_compact_ledger",
        "split": "dev140",
        "n": 140,
        "row_policy": "development_review_permitted",
        "path": "paper_experiments/exect/exect_llm_with_rules/gpt56luna/dev140/structured.jsonl",
        "status": "present",
        "empty_raw_count": 0,
    }
    _write_inventory(tmp_path, present=[historical])
    _patch_panel_paths(tmp_path, monkeypatch)
    panel = rebuild_dev140_panel()
    luna = next(cell for cell in panel["cells"] if cell["model_slug"] == "gpt56luna")
    assert luna["status"] == "present"
    assert luna["hybrid_headline_f1"] == 0.8818
    synced = json.loads(
        (tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8")
    )
    assert historical in synced["present"]


def test_promote_rejects_non_living_effort_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_work_cell(tmp_path, "grok46")
    comparison_path = (
        tmp_path / "experiments/paper/exect_llm_with_rules/grok46/dev140/comparison.json"
    )
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison["reasoning_effort"] = "high"
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    _write_inventory(tmp_path, present=[])
    _patch_panel_paths(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="living low-effort"):
        promote_exect_dev140("grok46")


def _write_holdout_work_cell(root: Path, slug: str) -> None:
    cell = root / "scratch/holdout/paper/exect_llm_with_rules" / slug / "test60"
    nested = cell / "exect_llm_with_rules"
    nested.mkdir(parents=True, exist_ok=True)
    structured = []
    for index in range(59):
        structured.append(
            {
                "letter_id": f"EA{index + 1:04d}",
                "prompt_version": "exectv2_compact_ledger",
                "raw_output": '{"mentions":[]}',
                "gold_mentions": ["do-not-promote"],
            }
        )
    (nested / "structured.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in structured),
        encoding="utf-8",
    )
    (cell / "comparison.json").write_text(
        json.dumps(
            {
                "method": "exect_llm_with_rules",
                "split": "test60",
                "reasoning_effort": "low",
                "row_count": 59,
                "row_policy": "aggregate_only",
                "arms": {
                    "exect_llm_with_rules": {
                        "raw_headline_f1": 0.7883,
                        "hybrid_headline_f1": 0.805,
                    }
                },
            }
        ),
        encoding="utf-8",
    )


def test_promote_exect_test60_strips_replay_and_updates_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_holdout_work_cell(tmp_path, "grok46")
    _write_inventory(
        tmp_path,
        present=[],
    )
    inventory_path = tmp_path / "paper_experiments/inventory.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload["missing"] = [
        {
            "model_slug": "grok46",
            "method": "exect_llm_with_rules",
            "split": "test60",
            "status": "missing",
        }
    ]
    inventory_path.write_text(json.dumps(payload), encoding="utf-8")
    _patch_panel_paths(tmp_path, monkeypatch)

    result = promote_exect("grok46", "test60")
    dest = tmp_path / "paper_experiments/exect/exect_llm_with_rules/grok46/test60"
    replay = json.loads((dest / "structured.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(replay) == {"letter_id", "prompt_version", "raw_output"}
    assert not (dest / "scored.jsonl").is_file()
    comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["row_policy"] == "aggregate_only"
    assert "letter_ids" not in comparison
    assert result["cell"]["n"] == 59
    assert result["cell"]["row_policy"] == "aggregate_only"
    synced = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert any(
        row["model_slug"] == "grok46"
        and row["method"] == "exect_llm_with_rules"
        and row["split"] == "test60"
        and row["row_policy"] == "aggregate_only"
        for row in synced["present"]
    )
    assert not any(
        row.get("model_slug") == "grok46" and row.get("split") == "test60"
        for row in synced["missing"]
    )


def test_promote_exect_test60_rejects_letter_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_holdout_work_cell(tmp_path, "grok46")
    comparison_path = (
        tmp_path / "scratch/holdout/paper/exect_llm_with_rules/grok46/test60/comparison.json"
    )
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison["letter_ids"] = ["EA0001"]
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    _write_inventory(tmp_path, present=[])
    _patch_panel_paths(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="aggregate-only"):
        promote_exect("grok46", "test60")
