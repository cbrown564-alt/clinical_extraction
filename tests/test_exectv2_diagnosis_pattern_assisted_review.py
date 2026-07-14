import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_pattern_assisted_review import (  # noqa: E501
    build_pattern_assisted_review,
)


def _mention(concept: str, cui: str | None = None) -> dict[str, object]:
    attributes = {"CUI": cui} if cui else {}
    return {
        "entity": "Diagnosis",
        "text": concept,
        "attributes": attributes,
        "normalized_diagnosis_concepts": [concept],
    }


def test_pattern_assisted_review_preserves_manual_and_labels_observable_patterns(
    tmp_path: Path,
) -> None:
    rows = [
        {
            "review_key": "EA0001|missed|epileptic attack",
            "letter_id": "EA0001",
            "direction": "missed",
            "normalized_concept": "epileptic attack",
            "methods": ["llm_only"],
            "note_text": "She has epileptic attacks.",
            "gold_diagnosis_mentions": [_mention("epileptic attack", "C0014544")],
            "method_records": {
                "llm_only": {"diagnosis_candidate_mentions": [_mention("epilepsy", "C0014544")]}
            },
        },
        {
            "review_key": "EA0001|spurious|epilepsy",
            "letter_id": "EA0001",
            "direction": "spurious",
            "normalized_concept": "epilepsy",
            "methods": ["llm_only"],
            "note_text": "She has epileptic attacks.",
            "gold_diagnosis_mentions": [_mention("epileptic attack", "C0014544")],
            "method_records": {
                "llm_only": {"diagnosis_candidate_mentions": [_mention("epilepsy", "C0014544")]}
            },
        },
        {
            "review_key": "EA0002|spurious|stroke",
            "letter_id": "EA0002",
            "direction": "spurious",
            "normalized_concept": "stroke",
            "methods": ["llm_only"],
            "note_text": "Previous stroke.",
            "gold_diagnosis_mentions": [],
            "method_records": {
                "llm_only": {"diagnosis_candidate_mentions": [_mention("stroke")]}
            },
        },
        {
            "review_key": "EA0003|spurious|absence seizures",
            "letter_id": "EA0003",
            "direction": "spurious",
            "normalized_concept": "absence seizures",
            "methods": ["llm_only"],
            "note_text": "She described absence-like episodes.",
            "gold_diagnosis_mentions": [],
            "method_records": {
                "llm_only": {"diagnosis_candidate_mentions": [_mention("absence seizures")]}
            },
        },
        {
            "review_key": "EA0004|missed|occipital lobe epilepsy",
            "letter_id": "EA0004",
            "direction": "missed",
            "normalized_concept": "occipital lobe epilepsy",
            "methods": ["rules_only"],
            "note_text": "Possible occipital lobe epilepsy.",
            "gold_diagnosis_mentions": [_mention("occipital lobe epilepsy")],
            "method_records": {"rules_only": {"diagnosis_candidate_mentions": []}},
        },
    ]
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    manual_path = tmp_path / "manual.json"
    manual_decision = {
        "triage": "extraction_error",
        "note": "manual",
        "updated_at": "2026-07-14T20:00:00Z",
    }
    manual_path.write_text(
        json.dumps(
            {
                "schema_version": "exectv2_diagnosis_review_overlay_v1",
                "source_gold_sha256": "gold",
                "source_review_row_count": 5,
                "triaged_count": 1,
                "decisions": {rows[4]["review_key"]: manual_decision},
            }
        ),
        encoding="utf-8",
    )

    overlay, summary = build_pattern_assisted_review(
        audit_jsonl=audit_path,
        manual_overlay_json=manual_path,
        timestamp="2026-07-14T21:00:00Z",
    )

    decisions = overlay["decisions"]
    assert decisions[rows[0]["review_key"]]["triage"] == "representation"
    assert decisions[rows[1]["review_key"]]["triage"] == "representation"
    assert decisions[rows[2]["review_key"]]["triage"] == "extraction_error"
    assert decisions[rows[3]["review_key"]]["triage"] == "uncertain"
    assert decisions[rows[4]["review_key"]] == manual_decision
    assert summary["manual_decision_count"] == 1
    assert summary["automatic_decision_count"] == 4
    assert summary["remaining_manual_review_count"] == 0
    assert summary["remaining_manual_review_keys"] == []


def test_pattern_assisted_review_prioritizes_exact_scope_rule(tmp_path: Path) -> None:
    rows = [
        {
            "review_key": "EA0001|missed|epilepsy",
            "letter_id": "EA0001",
            "direction": "missed",
            "normalized_concept": "epilepsy",
            "methods": ["llm_only"],
            "note_text": "Previous stroke.",
            "gold_diagnosis_mentions": [_mention("epilepsy", "C0014544")],
            "method_records": {"llm_only": {"diagnosis_candidate_mentions": []}},
        },
        {
            "review_key": "EA0001|spurious|stroke",
            "letter_id": "EA0001",
            "direction": "spurious",
            "normalized_concept": "stroke",
            "methods": ["llm_only"],
            "note_text": "Previous stroke.",
            "gold_diagnosis_mentions": [],
            "method_records": {
                "llm_only": {"diagnosis_candidate_mentions": [_mention("stroke", "C0014544")]}
            },
        },
    ]
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    manual_path = tmp_path / "manual.json"
    manual_path.write_text(
        json.dumps(
            {
                "schema_version": "exectv2_diagnosis_review_overlay_v1",
                "source_review_row_count": 2,
                "triaged_count": 0,
                "decisions": {},
            }
        ),
        encoding="utf-8",
    )

    overlay, summary = build_pattern_assisted_review(
        audit_jsonl=audit_path,
        manual_overlay_json=manual_path,
        timestamp="2026-07-14T21:00:00Z",
    )

    assert overlay["decisions"][rows[1]["review_key"]]["triage"] == "extraction_error"
    assert summary["conflict_count"] == 0
    assert summary["remaining_manual_review_count"] == 0
