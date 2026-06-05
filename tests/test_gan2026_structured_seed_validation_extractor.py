from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_validation_extractor,
)


def test_validation_extractor_emits_yearly_to_daily_candidate() -> None:
    panel_row = _panel_row(
        "yearly_to_daily",
        "hard",
        "1 per day",
        "Seizure control is inconsistent and she continues to have nightly "
        "generalised tonic-clonic seizures and intermittent tonic seizures four "
        "times per year.",
    )
    record = {"note_text": panel_row["note_text"]}

    row = structured_seed_validation_extractor.build_extractor_row(panel_row, record)

    assert row["generator_action"] == "emit_candidate"
    assert row["candidate_label"] == "1 per day"
    assert row["candidate_event_kind"] == "frequency_rate"
    assert row["exact_evidence"] is True


def test_validation_extractor_suppresses_seizure_free_control() -> None:
    panel_row = _panel_row(
        "seizure_free_to_unknown",
        "control",
        None,
        "Seizure-free since 27 March 2024",
    )
    record = {"note_text": panel_row["note_text"]}

    row = structured_seed_validation_extractor.build_extractor_row(panel_row, record)

    assert row["generator_action"] == "suppress_candidate"
    assert row["candidate_label"] is None
    assert row["expected_action_matched"] is True


def test_validation_extractor_summary_reports_action_quality() -> None:
    rows = [
        {
            "panel_role": "hard",
            "seed_family": "yearly_to_daily",
            "generator_action": "emit_candidate",
            "expected_action_matched": True,
            "exact_evidence": True,
        },
        {
            "panel_role": "control",
            "seed_family": "yearly_to_daily",
            "generator_action": "suppress_candidate",
            "expected_action_matched": True,
            "exact_evidence": True,
        },
    ]

    summary = structured_seed_validation_extractor.summarize_extractor_rows(rows)

    assert summary["row_count"] == 2
    assert summary["hard_emit_rows"] == 1
    assert summary["control_suppressed_rows"] == 1
    assert summary["expected_action_mismatch_rows"] == 0
    assert summary["decision"] == "validation_smoke_passed_undercoverage"


def _panel_row(
    family: str,
    panel_role: str,
    expected_candidate_label: str | None,
    evidence: str,
) -> dict[str, object]:
    return {
        "source_row_index": 1,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "panel_role": panel_role,
        "seed_family": family,
        "expected_generator_action": (
            "emit_candidate" if panel_role == "hard" else "suppress_candidate"
        ),
        "expected_candidate_label": expected_candidate_label,
        "expected_evidence_substring": evidence,
        "note_text": f"Clinical note. {evidence} Follow-up planned.",
    }
