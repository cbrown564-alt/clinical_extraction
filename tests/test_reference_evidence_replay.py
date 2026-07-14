from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.evidence_replay import (
    replay_exectv2_deterministic,
    replay_exectv2_finding_assembly,
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


def test_replay_exectv2_deterministic_matches_retained_reference() -> None:
    result = replay_exectv2_deterministic(split="dev")

    assert result["row_count"] == 140
    assert result["benchmark_per_item_f1"] == 0.3548
    assert result["evidence_validity_rate"] == 1.0


def test_replay_exectv2_gepa_predictions_uses_current_scorer() -> None:
    result = replay_exectv2_saved_predictions(
        ROOT / "experiments" / "exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.jsonl",
        split="dev",
    )

    assert result["row_count"] == 140
    assert result["clinical_headline_f1"] == 0.7393
    assert result["strict_benchmark_per_item_f1"] == 0.1356


def test_replay_exectv2_v08_p7_config_matches_primary_reference() -> None:
    result = replay_exectv2_finding_assembly(
        ROOT
        / "configs"
        / "exectv2"
        / "finding_assembly"
        / "exectv2_holistic_finding_assembly_v08_p7_dev140.yaml"
    )

    assert result["row_count"] == 140
    assert result["clinical_headline_f1"] == 0.9189
    assert result["evidence_valid_f1"] == 0.8913
