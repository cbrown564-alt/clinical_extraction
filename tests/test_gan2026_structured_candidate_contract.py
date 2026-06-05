from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_candidate_contract,
)


def test_structured_candidate_contract_accepts_exact_prediction_bearing_event() -> None:
    note_text = "She reports 2 seizures per month despite medication changes."
    row = {
        "source_row_index": 101,
        "split": "validation",
        "current_label": "unknown",
        "proposed_label": "2 per month",
        "gold_label": "2 per month",
        "candidate_id": "llm:event-1",
        "candidate_source": "llm_candidate",
        "event_kind": "frequency_rate",
        "event_target": "seizure",
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": "2 seizures per month",
        "note_text": note_text,
        "parse_ok": True,
        "selected_for_ablation": True,
        "panel_role": "hard",
    }

    candidate = structured_candidate_contract.build_candidate_event(row)

    assert candidate.source_row_index == 101
    assert candidate.prediction_bearing is True
    assert candidate.exact_evidence is True
    assert candidate.transition == "W_to_C"
    assert candidate.contract_issues == ()


def test_structured_candidate_contract_flags_missing_exact_evidence_and_parse() -> None:
    row = {
        "source_row_index": 102,
        "split": "validation",
        "current_label": "1 per month",
        "proposed_label": "2 per month",
        "gold_label": "1 per month",
        "candidate_id": "llm:event-2",
        "candidate_source": "llm_candidate",
        "event_kind": "frequency_rate",
        "event_target": "seizure",
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": "two seizures monthly",
        "note_text": "She reports one seizure per month.",
        "parse_ok": False,
        "selected_for_ablation": True,
        "panel_role": "control",
    }

    candidate = structured_candidate_contract.build_candidate_event(row)

    assert candidate.exact_evidence is False
    assert candidate.transition == "C_to_W"
    assert candidate.contract_issues == (
        "parse_not_ok",
        "evidence_not_exact",
    )


def test_structured_candidate_validation_gate_requires_coverage_and_safety() -> None:
    rows = []
    for index in range(150):
        is_opportunity = index < 60
        rows.append(
            {
                "source_row_index": index,
                "split": "validation",
                "current_label": "unknown",
                "proposed_label": "1 per month" if is_opportunity else "unknown",
                "gold_label": "1 per month" if is_opportunity else "unknown",
                "candidate_id": f"candidate-{index}",
                "candidate_source": "typed_candidate_contract",
                "event_kind": "frequency_rate" if is_opportunity else "unknown_frequency",
                "event_target": "seizure",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": (
                    "1 seizure per month"
                    if is_opportunity
                    else "No current seizure frequency is documented"
                ),
                "note_text": (
                    "Current frequency is 1 seizure per month."
                    if is_opportunity
                    else "No current seizure frequency is documented."
                ),
                "parse_ok": index < 145,
                "selected_for_ablation": True,
                "panel_role": "hard" if index < 75 else "control",
            }
        )
    events = structured_candidate_contract.build_candidate_events(rows)

    summary = structured_candidate_contract.summarize_validation_gate(events)

    assert summary["selected_prediction_bearing_rows"] == 150
    assert summary["w_to_c_rows"] == 60
    assert summary["c_to_w_rows"] == 0
    assert summary["parse_ok_exact_evidence_rate"] == 145 / 150
    assert summary["frozen_test_audit_ready"] is True
    assert summary["gate_failures"] == []


def test_structured_candidate_validation_gate_blocks_undercoverage_and_regression() -> None:
    rows = []
    for index in range(100):
        rows.append(
            {
                "source_row_index": index,
                "split": "validation",
                "current_label": "unknown" if index < 50 else "1 per month",
                "proposed_label": "1 per month" if index < 50 else "unknown",
                "gold_label": "1 per month",
                "candidate_id": f"candidate-{index}",
                "candidate_source": "typed_candidate_contract",
                "event_kind": "frequency_rate",
                "event_target": "seizure",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "1 seizure per month",
                "note_text": "Current frequency is 1 seizure per month.",
                "parse_ok": True,
                "selected_for_ablation": True,
                "panel_role": "hard",
            }
        )
    events = structured_candidate_contract.build_candidate_events(rows)

    summary = structured_candidate_contract.summarize_validation_gate(events)

    assert summary["selected_prediction_bearing_rows"] == 100
    assert summary["w_to_c_rows"] == 50
    assert summary["c_to_w_rows"] == 50
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == [
        "coverage_below_150",
        "c_to_w_above_5_percent",
    ]
