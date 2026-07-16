from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
)
from scripts import check_exectv2_diagnosis_guard_ablation as diagnosis_check


def _record(model: str, letter: str, direction: str) -> dict[str, object]:
    model_correct = direction in {"correct_to_wrong", "changed_still_correct"}
    final_correct = direction in {"wrong_to_correct", "changed_still_correct"}
    return {
        "model_label": model,
        "family": "Diagnosis",
        "letter_id": letter,
        "family_local_change_direction": direction,
        "family_local_model_owned_correct": model_correct,
        "family_local_final_correct": final_correct,
        "evidence_status": "exact",
    }


def test_diagnosis_gate_rejects_unexpected_lost_rescue_identity() -> None:
    comparator = [
        _record("model", f"DEV-{index}", "wrong_to_correct") for index in range(81)
    ]
    candidate = [
        _record("model", f"DEV-{index}", "wrong_to_correct") for index in range(75)
    ]

    gates = diagnosis_check._evaluate_gates(
        comparator,
        candidate,
        [],
        diagnostics_match=True,
        allowed_lost_rescues={
            ("model", f"DEV-{index}") for index in range(5)
        },
    )

    assert gates["checks"]["lost_rescues_confined_to_predeclared_rows"] is False
    assert gates["status"] == "fail"


def test_diagnosis_ablation_artifact_is_dev_only_and_has_four_variants() -> None:
    artifact = json.loads(
        Path(
            "experiments/exectv2_diagnosis_guard_ablation_dev140_20260715.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    dev_ids = set(manifest["splits"]["dev"]["letter_ids"])
    test_ids = set(manifest["splits"]["test"]["letter_ids"])
    retained_ids = {str(row["letter_id"]) for row in artifact["rows"]}

    assert artifact["split"] == "dev140"
    assert artifact["new_model_calls"] == 0
    assert set(artifact["ablations"]) == set(diagnosis_check.DIAGNOSIS_VARIANTS)
    assert retained_ids <= dev_ids
    assert retained_ids.isdisjoint(test_ids)
    assert {row["family"] for row in artifact["rows"]} == {"Diagnosis"}
    assert {row["evidence_status"] for row in artifact["rows"]} == {"exact"}
