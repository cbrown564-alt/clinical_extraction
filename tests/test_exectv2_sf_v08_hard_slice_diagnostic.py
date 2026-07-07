"""Tests for the ExECTv2 SF v0.8 hard-slice diagnostic panel."""

from __future__ import annotations

from experiments import build_exectv2_sf_v08_hard_slice_diagnostic as panel


def _record(
    *,
    letter_id: str,
    side: str,
    key: str,
    evidence: str,
    text: str | None = None,
    count: int = 1,
) -> dict[str, object]:
    return {
        "letter_id": letter_id,
        "entity": "SeizureFrequency",
        "side": side,
        "key": key,
        "count": count,
        "example_text": text or evidence,
        "example_attributes": {},
        "evidence": evidence,
        "note_excerpt": evidence,
    }


def test_panel_includes_all_sf_residual_units_and_required_tables() -> None:
    ledger = {
        "generated_on": "2026-06-18",
        "split": "dev",
        "sf_jsonl": "sf.jsonl",
        "records": [
            _record(
                letter_id="L1",
                side="gold",
                key='[["cui", "C0036572"], "seizure-free"]',
                evidence="seizures",
                count=2,
            ),
            _record(
                letter_id="L1",
                side="predicted",
                key='[["cui", "C1299590"], "seizure-free"]',
                evidence="seizure free",
            ),
            _record(
                letter_id="L2",
                side="gold",
                key='[["cui", "C0494475"], "active-rate"]',
                evidence="tonic clonic seizures",
            ),
            _record(
                letter_id="L2",
                side="predicted",
                key='[["cui", "C0494475"], "unknown"]',
                evidence="tonic clonic seizures are worse",
            ),
        ],
    }
    rows = [
        {
            "letter_id": "L1",
            "candidate_spans": [
                {
                    "candidate_type": "generic_seizure_free_anchor",
                    "decision_lane": "seizure_free",
                    "state_hint": "seizure-free",
                    "text_hint": "seizures",
                    "evidence": "remains seizure free",
                }
            ],
        },
        {"letter_id": "L2", "candidate_spans": []},
    ]

    result = panel.build_panel(ledger, rows)

    assert result["residual_unit_count"] == 5
    assert result["residual_record_count"] == 4
    assert result["bucket_counts_by_side_state"]["seizure_free_cui_convention"] == {
        "gold/seizure-free": 2,
        "predicted/seizure-free": 1,
    }
    assert result["bucket_counts_by_side_state"]["state_swap"] == {
        "gold/active-rate": 1,
        "predicted/unknown": 1,
    }
    assert result["possible_fix_counts_by_action_class"] == {
        "repair_benchmark_format": 3,
        "repair_state": 2,
    }
    assert {item["pattern"] for item in result["top_letter_pair_patterns"]} >= {
        "gold:active-rate -> predicted:unknown"
    }


def test_panel_distinguishes_context_span_and_true_candidate_gap() -> None:
    ledger = {
        "generated_on": "2026-06-18",
        "split": "dev",
        "sf_jsonl": "sf.jsonl",
        "records": [
            _record(
                letter_id="L3",
                side="predicted",
                key='[["cui", "C0036572"], "unknown"]',
                evidence="family history of seizures",
            ),
            _record(
                letter_id="L4",
                side="gold",
                key='[["cui", "C0563606"], "active-rate"]',
                evidence="absences daily",
            ),
        ],
    }
    rows = [
        {"letter_id": "L3", "candidate_spans": []},
        {
            "letter_id": "L4",
            "candidate_spans": [
                {
                    "candidate_type": "diagnosis_context",
                    "decision_lane": "reject",
                    "state_hint": "reject",
                    "text_hint": "absences",
                    "evidence": "history of absences",
                }
            ],
        },
    ]

    result = panel.build_panel(ledger, rows)
    buckets = {item["letter_id"]: item["bucket"] for item in result["panel"]}

    assert buckets["L3"] == "diagnosis_context_span"
    assert buckets["L4"] == "true_candidate_gap"
    assert result["possible_fix_counts_by_action_class"] == {
        "drop": 1,
        "no_action": 1,
    }
