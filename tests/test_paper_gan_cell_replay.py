"""Gan rung replay is split-aware and holdout-safe."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.cli import main
from clinical_extraction.paper.gan_cell_replay import (
    _rung_summary,
    gan_living_extract_rows_path,
    gan_rung_out_dir,
    gan_source_near_rows_path,
    replay_gan_dev750,
    write_gan_rung_artifacts,
)
from clinical_extraction.paper.methods import gan_row_count


def _scored_row() -> dict[str, object]:
    rung = {
        "predicted_label": "1 per week",
        "scorable": True,
        "predicted_kind": "frequency",
        "purist_correct": True,
        "pragmatic_correct": True,
        "selected_event_ids": ["e1"],
    }
    return {
        "source_row_index": 10,
        "gold_label": "1 per week",
        "rungs": {
            "rules_only": {**rung, "selected_event_ids": []},
            "llm_extract": rung,
            "llm_encode": rung,
            "llm_select": rung,
        },
    }


def test_rung_summary_totals_predicted_candidates() -> None:
    rows = [
        {
            "rungs": {
                "llm_extract": {
                    "purist_correct": True,
                    "pragmatic_correct": True,
                    "scorable": True,
                    "predicted_kind": "frequency",
                    "predicted_candidate_count": 2,
                }
            }
        },
        {
            "rungs": {
                "llm_extract": {
                    "purist_correct": False,
                    "pragmatic_correct": False,
                    "scorable": True,
                    "predicted_kind": "unknown",
                    "predicted_candidate_count": 3,
                }
            }
        },
    ]

    summary = _rung_summary(rows, "llm_extract")

    assert summary["predicted_candidate_count"] == 5
    assert summary["purist_correct"] == 1


def test_gan_rung_paths_follow_slug_and_split() -> None:
    living = gan_living_extract_rows_path("grok46", "dev750").as_posix()
    assert living.endswith("gan_llm_extract/grok46/dev750/rows.jsonl")
    assert gan_source_near_rows_path("gemini37flash", "test450").as_posix().endswith(
        "paper_experiments/gan/gan_llm_extract_raw/gemini37flash/test450/rows.jsonl"
    )
    assert gan_rung_out_dir("grok46", "test450").as_posix().endswith(
        "paper_experiments/gan/rungs/grok46/test450"
    )
    assert gan_row_count("test450") == 450


def test_holdout_rung_artifacts_are_aggregates_only(tmp_path: Path) -> None:
    summary = {
        "claim_boundary": "Gan aggregate-only test450 replay. Do not inspect holdout rows.",
        "row_policy": "aggregate_only",
        "split": "test450",
        "model_slug": "grok46",
        "row_count": 1,
        "rungs": {
            "rules_only": {
                "purist_correct": 1,
                "purist_accuracy": 1.0,
                "pragmatic_correct": 1,
                "pragmatic_accuracy": 1.0,
                "scorable": 1,
                "predicted_kinds": {"frequency": 1},
            }
        },
        "format_only_check": {
            "selected_event_id_changes": 0,
            "used_as_rung_3": True,
        },
    }
    (tmp_path / "scored.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "hops.jsonl").write_text("{}\n", encoding="utf-8")

    written = write_gan_rung_artifacts(
        tmp_path,
        summary,
        scored=[_scored_row()],
        hops=[{"source_row_index": 10, "answer_states": []}],
        holdout=True,
    )

    assert written == tmp_path / "comparison.json"
    assert not (tmp_path / "scored.jsonl").exists()
    assert not (tmp_path / "hops.jsonl").exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    blob = json.dumps(payload)
    assert payload["row_policy"] == "aggregate_only"
    assert payload["claim_boundary"].startswith("Gan aggregate-only")
    assert "gold_label" not in blob
    assert "source_row_index" not in blob
    assert "incorrect_source_row_indices" not in payload
    assert "final_labels" not in payload


def test_development_rung_artifacts_keep_row_files(tmp_path: Path) -> None:
    summary = {
        "claim_boundary": "Gan development replay. Not holdout.",
        "split": "dev750",
        "row_count": 1,
        "rungs": {},
    }
    write_gan_rung_artifacts(
        tmp_path,
        summary,
        scored=[_scored_row()],
        hops=[{"source_row_index": 10, "answer_states": []}],
        holdout=False,
    )
    assert (tmp_path / "scored.jsonl").is_file()
    assert (tmp_path / "hops.jsonl").is_file()
    assert (tmp_path / "comparison.json").is_file()


def test_replay_gan_dev750_stays_a_development_alias() -> None:
    assert replay_gan_dev750.__doc__
    assert "development" in (replay_gan_dev750.__doc__ or "").lower()


def test_cli_replay_rungs_accepts_test450(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_replay(
        split: str, *, slug: str = "grok46", source: str = "living"
    ) -> dict[str, object]:
        captured["split"] = split
        captured["slug"] = slug
        captured["source"] = source
        return {"split": split, "model_slug": slug, "row_policy": "aggregate_only"}

    monkeypatch.setattr(
        "clinical_extraction.paper.cli.replay_gan_rungs", fake_replay
    )
    main(
        [
            "replay-rungs",
            "--method",
            "gan_llm_extract_raw",
            "--model",
            "grok46",
            "--split",
            "test450",
        ]
    )
    assert captured == {"split": "test450", "slug": "grok46", "source": "ablation"}
