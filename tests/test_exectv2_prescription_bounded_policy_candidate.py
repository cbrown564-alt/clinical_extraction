from __future__ import annotations

from scripts import check_exectv2_prescription_bounded_policy_candidate as candidate_check


def _record(index: int, direction: str) -> dict[str, object]:
    model_correct = direction in {"correct_to_wrong", "changed_still_correct"}
    final_correct = direction in {"wrong_to_correct", "changed_still_correct"}
    return {
        "model_label": "model",
        "family": "Prescription",
        "letter_id": f"DEV-{index}",
        "family_local_change_direction": direction,
        "family_local_model_owned_correct": model_correct,
        "family_local_final_correct": final_correct,
        "evidence_status": "exact",
        "deterministic_actions": [],
    }


def test_bounded_candidate_gate_requires_demonstrated_rescue_identities() -> None:
    comparator = [_record(index, "wrong_to_correct") for index in range(41)]
    candidate = [_record(index, "wrong_to_correct") for index in range(39)]
    changed_rows: list[dict[str, object]] = []
    required = {
        ("model", "EA0096"),
        ("model", "EA0127"),
        ("model", "EA0150"),
    }

    gates = candidate_check._evaluate_gates(
        comparator,
        candidate,
        changed_rows,
        diagnostics_match=True,
        required_rescues=required,
    )

    assert gates["checks"]["retain_all_demonstrated_missing_regimen_rescues"] is False
    assert gates["status"] == "fail"


def test_prescription_bounded_policy_dump_was_pruned() -> None:
    """Decision 0045 archived the policy; the dump is not a living owner."""

    from pathlib import Path

    assert not Path(
        "experiments/exectv2_prescription_bounded_policy_candidate_dev140_20260715.json"
    ).exists()
