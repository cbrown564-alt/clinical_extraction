import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_resolution import (  # noqa: E501
    build_review_ledger,
)


def test_build_review_ledger_preserves_rows_and_decision_provenance(tmp_path: Path) -> None:
    audit_rows = [
        {
            "review_key": "EA0001|spurious|stroke",
            "letter_id": "EA0001",
            "direction": "spurious",
            "normalized_concept": "stroke",
            "methods": ["llm_only"],
        },
        {
            "review_key": "EA0002|missed|focal epilepsy",
            "letter_id": "EA0002",
            "direction": "missed",
            "normalized_concept": "focal epilepsy",
            "methods": ["rules_only"],
        },
    ]
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text(
        "".join(json.dumps(row) + "\n" for row in audit_rows), encoding="utf-8"
    )
    overlay_path = tmp_path / "overlay.json"
    overlay_path.write_text(
        json.dumps(
            {
                "schema_version": "exectv2_diagnosis_review_overlay_v1",
                "source_review_row_count": 2,
                "triaged_count": 2,
                "decisions": {
                    audit_rows[0]["review_key"]: {
                        "triage": "extraction_error",
                        "note": "[auto:non_target_diagnosis_scope] hypothesis",
                    },
                    audit_rows[1]["review_key"]: {
                        "triage": "representation",
                        "note": "manual",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    ledger, summary = build_review_ledger(
        audit_jsonl=audit_path,
        completed_overlay_json=overlay_path,
    )

    assert len(ledger) == 2
    assert ledger[0]["review_decision"] == {
        "triage": "extraction_error",
        "provenance": "pattern_assisted",
        "mechanism": "non_target_diagnosis",
        "rule_ids": ["non_target_diagnosis_scope"],
        "note": "[auto:non_target_diagnosis_scope] hypothesis",
    }
    assert ledger[1]["review_decision"]["provenance"] == "manual"
    assert ledger[1]["review_decision"]["mechanism"] == "manual_representation"
    assert summary["triage_counts"] == {"extraction_error": 1, "representation": 1}
    assert summary["decision_provenance_counts"] == {"manual": 1, "pattern_assisted": 1}


def test_build_review_ledger_requires_complete_overlay(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text(
        json.dumps(
            {
                "review_key": "EA0001|spurious|stroke",
                "letter_id": "EA0001",
                "direction": "spurious",
                "normalized_concept": "stroke",
                "methods": ["llm_only"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    overlay_path = tmp_path / "overlay.json"
    overlay_path.write_text(
        json.dumps({"source_review_row_count": 1, "triaged_count": 0, "decisions": {}}),
        encoding="utf-8",
    )

    try:
        build_review_ledger(
            audit_jsonl=audit_path,
            completed_overlay_json=overlay_path,
        )
    except ValueError as exc:
        assert "complete" in str(exc)
    else:
        raise AssertionError("incomplete overlay should be rejected")
