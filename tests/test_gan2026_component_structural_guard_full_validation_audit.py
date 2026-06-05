from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structural_guard_full_validation_audit,
)


def test_structural_guard_selects_comparator_absent_candidate(monkeypatch) -> None:
    monkeypatch.setattr(
        structural_guard_full_validation_audit.candidate_union,
        "_deterministic_candidates",
        lambda _note, _source: [
            {
                "candidate_kind": "frequency_rate",
                "normalized_label": "1 per week",
                "evidence": "seizures weekly",
                "metadata": {"rule_id": "rate.occurring_adjective"},
            }
        ],
    )

    rows = structural_guard_full_validation_audit.build_structural_guard_audit_rows(
        [
            {
                "source_row_index": 1,
                "prediction_label": "",
                "gold_label": "1 per week",
                "final_purist_correct": False,
            }
        ],
        [SimpleNamespace(source_row_index=1, note_text="note")],
    )

    assert rows[0]["candidate_label"] == "1 per week"
    assert rows[0]["selected_transition"] == "W_to_C"


def test_structural_guard_skips_when_base_label_is_present(monkeypatch) -> None:
    monkeypatch.setattr(
        structural_guard_full_validation_audit.candidate_union,
        "_deterministic_candidates",
        lambda _note, _source: [
            {
                "candidate_kind": "frequency_rate",
                "normalized_label": "1 per week",
                "metadata": {"rule_id": "rate.occurring_adjective"},
            },
            {
                "candidate_kind": "frequency_rate",
                "normalized_label": "1 per month",
                "metadata": {"rule_id": "rate.direct_count_per_period"},
            },
        ],
    )

    rows = structural_guard_full_validation_audit.build_structural_guard_audit_rows(
        [
            {
                "source_row_index": 1,
                "prediction_label": "1 per week",
                "gold_label": "1 per week",
                "final_purist_correct": True,
            }
        ],
        [SimpleNamespace(source_row_index=1, note_text="note")],
    )

    assert rows == []


def test_structural_guard_summary_freezes_only_clean_selected_rows() -> None:
    summary = structural_guard_full_validation_audit.summarize_structural_guard_audit_rows(
        [
            {
                "candidate_kind": "frequency_rate",
                "candidate_rule_id": "rate.occurring_adjective",
                "selected_transition": "W_to_C",
            },
            {
                "candidate_kind": "unknown_frequency",
                "candidate_rule_id": "unknown",
                "selected_transition": "C_to_C",
            },
        ],
        [
            {"source_row_index": 1, "final_purist_correct": False},
            {"source_row_index": 2, "final_purist_correct": True},
        ],
    )

    assert summary["selected_candidate_rows"] == 2
    assert summary["selected_transition_counts"] == {"C_to_C": 1, "W_to_C": 1}
    assert summary["projected_correct_rows"] == 2
    assert summary["decision"] == "freeze_candidate_for_aggregate_audit"
