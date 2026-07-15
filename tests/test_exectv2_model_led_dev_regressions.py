from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_led_dev_regressions,
)


@pytest.mark.parametrize(
    ("source_correct", "final_correct", "expected"),
    [
        (False, True, "wrong_to_correct"),
        (True, False, "correct_to_wrong"),
        (False, False, "changed_still_wrong"),
        (True, True, "changed_still_correct"),
    ],
)
def test_change_direction_names_both_safety_and_benefit(
    source_correct: bool,
    final_correct: bool,
    expected: str,
) -> None:
    assert (
        model_led_dev_regressions.change_direction(source_correct, final_correct)
        == expected
    )


def test_filter_jsonl_bytes_retains_only_declared_dev_ids() -> None:
    payload = b"\n".join(
        [
            json.dumps({"letter_id": "DEV-1", "prediction": "keep"}).encode(),
            json.dumps({"letter_id": "TEST-1", "prediction": "discard"}).encode(),
            json.dumps({"letter_id": "DEV-2", "prediction": "keep"}).encode(),
        ]
    )

    filtered = model_led_dev_regressions.filter_jsonl_bytes(
        payload,
        allowed_ids={"DEV-1", "DEV-2"},
    )
    rows = [json.loads(line) for line in filtered.splitlines()]

    assert [row["letter_id"] for row in rows] == ["DEV-1", "DEV-2"]
    assert b"TEST-1" not in filtered


def test_filter_jsonl_bytes_rejects_missing_or_duplicate_dev_rows() -> None:
    duplicate = b"\n".join(
        [
            json.dumps({"letter_id": "DEV-1"}).encode(),
            json.dumps({"letter_id": "DEV-1"}).encode(),
        ]
    )

    with pytest.raises(ValueError, match="duplicate dev row"):
        model_led_dev_regressions.filter_jsonl_bytes(duplicate, allowed_ids={"DEV-1"})

    with pytest.raises(ValueError, match="missing dev rows"):
        model_led_dev_regressions.filter_jsonl_bytes(
            json.dumps({"letter_id": "DEV-1"}).encode(),
            allowed_ids={"DEV-1", "DEV-2"},
        )


def test_retained_dev140_regression_artifact_contains_no_test60_rows() -> None:
    artifact = json.loads(
        Path(
            "experiments/exectv2_model_led_dev140_regression_analysis_20260715.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(
        DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8")
    )
    dev_ids = set(manifest["splits"]["dev"]["letter_ids"])
    test_ids = set(manifest["splits"]["test"]["letter_ids"])
    retained_ids = {str(row["letter_id"]) for row in artifact["rows"]}

    assert artifact["split"] == "dev140"
    assert artifact["row_policy"] == "dev140_rows_permitted_test60_forbidden"
    assert artifact["new_model_calls"] == 0
    assert retained_ids <= dev_ids
    assert retained_ids.isdisjoint(test_ids)
    assert artifact["summary"]["changed_rows"] == len(artifact["rows"])
    assert artifact["summary"]["evidence_status"] == {"exact": len(artifact["rows"])}
