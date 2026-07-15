from __future__ import annotations

from pathlib import Path

from scripts.build_exectv2_annotation_evidence_synthesis import build_synthesis

ROOT = Path(__file__).resolve().parents[1]


def test_annotation_synthesis_reconciles_retained_sources() -> None:
    payload = build_synthesis(ROOT)

    assert payload["schema_version"] == "exectv2_annotation_evidence_synthesis_v1"
    assert payload["call_mode"] == "no_model_calls_retained_artifact_synthesis"
    assert payload["gold_changed"] is False
    assert payload["scorer_changed"] is False
    assert len(payload["sources"]) == 13
    assert {source["hash_status"] for source in payload["sources"]} == {"matched_manifest"}

    summary = payload["summary"]
    assert summary["taxonomy_entry_count"] == 584
    assert summary["entries_by_record_type"] == {
        "completed_diagnosis_review_case": 246,
        "direct_gold_issue": 4,
        "retained_family_ledger_case": 334,
    }
    assert summary["current_diagnosis_triage"] == {
        "extraction_error": 72,
        "representation": 173,
        "uncertain": 1,
    }
    assert summary["current_diagnosis_sensitivity_treatment"] == {
        "forgiven_in_conservative_and_reviewed_interpretation_views": 133,
        "forgiven_only_in_widest_reviewed_interpretation_view": 40,
        "not_forgiven_in_diagnosis_sensitivity_views": 73,
    }
    assert summary["direct_gold_issue_status"] == {"fixed": 1, "open": 3}
    assert summary["legacy_diagnosis_reported_disagreement_count"] == 209
    assert summary["legacy_diagnosis_ledger_row_count"] == 199
    assert summary["legacy_diagnosis_unmaterialized_row_count"] == 10
    assert summary["cited_letter_count"] == 57
    assert summary["unmapped_cited_letter_count"] == 0


def test_annotation_synthesis_keeps_clinical_review_boundary() -> None:
    payload = build_synthesis(ROOT)

    assert all(
        entry["clinical_review_state"] != "independently_clinically_reviewed"
        for entry in payload["taxonomy_entries"]
    )
    statement = next(
        item
        for item in payload["evidence_statements"]
        if item["statement_id"] == "boundary:independent_clinical_review"
    )
    assert statement["handling"] == (
        "Require independent clinical review before making clinical-validity claims."
    )
