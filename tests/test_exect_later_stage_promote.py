"""Exact rescore and promote for ExECT later-stage Gemini cells."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.cli import main
from clinical_extraction.paper.exect_later_stage import rescore_later_stage
from clinical_extraction.paper.exect_panel import promote_exect_later_stage
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)


def _letter() -> ExectLetter:
    return ExectLetter(
        letter_id="EA0001",
        note_text="note",
        annotations=(
            ExectAnnotation(
                entity="Diagnosis",
                text="epilepsy",
                attributes={},
            ),
        ),
    )


def _work_row(*, mentions: list[dict[str, object]]) -> dict[str, object]:
    return {
        "letter_id": "EA0001",
        "prompt_version": "exect_llm_encode",
        "raw_output": '{"mentions":[{"mention_id":"m1"}]}',
        "gold_mentions": ["do-not-promote"],
        "encoded_mentions": mentions,
        "selected_mentions": mentions,
        "call_error": None,
    }


def _write_work_cell(
    tmp_path: Path,
    method: str,
    split: str,
    *,
    mentions: list[dict[str, object]],
    headline_f1: float,
) -> Path:
    root = (
        tmp_path / "scratch/holdout/paper"
        if split == "test60"
        else tmp_path / "experiments/paper"
    )
    cell = root / method / "gemini37flash" / split
    cell.mkdir(parents=True)
    (cell / "rows.jsonl").write_text(
        json.dumps(_work_row(mentions=mentions)) + "\n",
        encoding="utf-8",
    )
    (cell / "comparison.json").write_text(
        json.dumps(
            {
                "method": method,
                "split": split,
                "row_policy": (
                    "aggregate_only"
                    if split == "test60"
                    else "development_review_permitted"
                ),
                "four_family_headline_f1": headline_f1,
                "reasoning_effort": "low",
            }
        ),
        encoding="utf-8",
    )
    return cell


def _patch_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paper = tmp_path / "paper_experiments"
    exect = paper / "exect"
    monkeypatch.setattr("clinical_extraction.paper.exect_later_stage.ROOT", tmp_path)
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_later_stage.WORK_ROOT",
        tmp_path / "experiments/paper",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_later_stage.HOLDOUT_SCRATCH",
        tmp_path / "scratch/holdout/paper",
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_later_stage.letters_for_split",
        lambda split: [_letter()],
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_later_stage.exect_row_count",
        lambda split: 1,
    )
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.exect_row_count",
        lambda split: 1,
    )
    monkeypatch.setattr("clinical_extraction.paper.exect_panel.ROOT", tmp_path)
    monkeypatch.setattr("clinical_extraction.paper.exect_panel.PAPER_EXECT", exect)
    monkeypatch.setattr(
        "clinical_extraction.paper.exect_panel.INVENTORY_PATH",
        paper / "inventory.json",
    )
    paper.mkdir(parents=True)
    (paper / "inventory.json").write_text(
        json.dumps({"present": [], "missing": []}),
        encoding="utf-8",
    )


def test_rescore_later_stage_writes_exact_scorer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_roots(tmp_path, monkeypatch)
    _write_work_cell(
        tmp_path,
        "exect_llm_encode",
        "dev140",
        mentions=[
            {
                "entity": "Diagnosis",
                "standard_name": "focal epilepsy",
                "attributes": {},
            }
        ],
        headline_f1=0.8545,
    )
    payload = rescore_later_stage("exect_llm_encode", "gemini37flash", "dev140")
    comparison = json.loads(
        (
            tmp_path
            / "experiments/paper/exect_llm_encode/gemini37flash/dev140/comparison.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["ok"] is True
    assert comparison["scorer"] == "clinical_headline_unit_keys"
    assert comparison["four_family_headline_f1"] != 0.8545
    assert comparison["prior_four_family_headline_f1"] == 0.8545
    assert "letter_ids" not in comparison


def test_promote_later_stage_dev140_strips_replay_and_writes_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_roots(tmp_path, monkeypatch)
    _write_work_cell(
        tmp_path,
        "exect_llm_encode",
        "dev140",
        mentions=[{"entity": "Diagnosis", "standard_name": "epilepsy", "attributes": {}}],
        headline_f1=0.1,
    )
    result = promote_exect_later_stage("exect_llm_encode", "gemini37flash", "dev140")
    dest = tmp_path / "paper_experiments/exect/exect_llm_encode/gemini37flash/dev140"
    replay = json.loads((dest / "rows.jsonl").read_text(encoding="utf-8").splitlines()[0])
    scored = json.loads((dest / "scored.jsonl").read_text(encoding="utf-8").splitlines()[0])
    comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
    assert result["cell"]["method"] == "exect_llm_encode"
    assert set(replay) == {"letter_id", "prompt_version", "raw_output"}
    assert scored["method"] == "exect_llm_encode"
    assert comparison["scorer"] == "clinical_headline_unit_keys"
    inventory = json.loads(
        (tmp_path / "paper_experiments/inventory.json").read_text(encoding="utf-8")
    )
    present = {
        (row["model_slug"], row["method"], row["split"]) for row in inventory["present"]
    }
    assert ("gemini37flash", "exect_llm_encode", "dev140") in present


def test_promote_later_stage_test60_is_aggregate_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_roots(tmp_path, monkeypatch)
    _write_work_cell(
        tmp_path,
        "exect_llm_select",
        "test60",
        mentions=[{"entity": "Diagnosis", "standard_name": "epilepsy", "attributes": {}}],
        headline_f1=0.1,
    )
    result = promote_exect_later_stage("exect_llm_select", "gemini37flash", "test60")
    dest = tmp_path / "paper_experiments/exect/exect_llm_select/gemini37flash/test60"
    assert result["cell"]["row_policy"] == "aggregate_only"
    assert (dest / "rows.jsonl").is_file()
    assert not (dest / "scored.jsonl").is_file()
    comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["row_policy"] == "aggregate_only"
    assert "letter_ids" not in comparison
    assert "changed_rows" not in comparison


def test_promote_later_stage_rejects_non_gemini() -> None:
    with pytest.raises(RuntimeError, match="Gemini only"):
        promote_exect_later_stage("exect_llm_encode", "grok46", "dev140")


def test_promote_exect_cli_accepts_later_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_promote(method: str, slug: str, split: str) -> dict[str, object]:
        captured["method"] = method
        captured["slug"] = slug
        captured["split"] = split
        return {"ok": True}

    monkeypatch.setattr(
        "clinical_extraction.paper.cli.promote_exect_later_stage",
        fake_promote,
    )
    main(
        [
            "promote-exect",
            "--method",
            "exect_llm_encode",
            "--model",
            "gemini37flash",
            "--split",
            "dev140",
        ]
    )
    assert captured == {
        "method": "exect_llm_encode",
        "slug": "gemini37flash",
        "split": "dev140",
    }
