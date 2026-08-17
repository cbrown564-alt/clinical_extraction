from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.evidence_replay import (
    replay_current_stack_primary,
    replay_exectv2_deterministic,
    replay_exectv2_saved_predictions,
    replay_gan_saved_comparisons,
)

ROOT = Path(__file__).resolve().parents[1]


def test_replay_gan_saved_comparisons_counts_total_and_prediction_records(
    tmp_path: Path,
) -> None:
    path = tmp_path / "rows.jsonl"
    rows = [
        {
            "comparison": {"purist_correct": True, "pragmatic_correct": True},
            "final_label": "2 per week",
        },
        {
            "comparison": {"purist_correct": True, "pragmatic_correct": False},
            "decision_record": {"final_label": "no seizure frequency reference"},
        },
        {
            "comparison": None,
            "structured_record": {"selection": {"final_label": "unknown"}},
        },
        {"comparison": None},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    assert replay_gan_saved_comparisons(path) == {
        "rows": 4,
        "purist_correct": 2,
        "pragmatic_correct": 1,
        "prediction_records": 3,
    }


@pytest.mark.local_corpus
def test_replay_exectv2_deterministic_matches_retained_reference() -> None:
    result = replay_exectv2_deterministic(split="dev")

    assert result["row_count"] == 140
    assert result["benchmark_per_item_f1"] == 0.3943
    assert result["evidence_validity_rate"] == 0.9973


@pytest.mark.local_corpus
def test_replay_exectv2_gepa_predictions_uses_current_scorer() -> None:
    result = replay_exectv2_saved_predictions(
        ROOT / "experiments" / "exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.jsonl",
        split="dev",
    )

    assert result["row_count"] == 140
    assert result["clinical_headline_f1"] == 0.7410
    assert result["strict_benchmark_per_item_f1"] == 0.1356


@pytest.mark.local_corpus
def test_replay_current_stack_primary_matches_living_fills() -> None:
    result = replay_current_stack_primary(ROOT)

    assert result["gan_sol_hybrid_purist"] == 381
    assert result["exect_sol_hybrid_dev140_f1"] == 0.9119
    assert result["exect_sol_hybrid_test60_f1"] == 0.8302
    assert result["exect_rules_dev140_f1"] == 0.9042
    assert result["exect_rules_test60_f1"] == 0.7937
