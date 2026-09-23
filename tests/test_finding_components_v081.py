from __future__ import annotations

from scripts.benchmarks.score_finding_components_v081 import score_row


def finding(ident: str, event: str, evidence: str, count: int) -> dict:
    return {
        "id": ident,
        "event": {"type": event, "seizure_status": "stated"},
        "measurement": {
            "type": "rate",
            "count": {"type": "number", "value": count},
            "per": {"type": "number", "value": 1, "unit": "month"},
        },
        "timing": "current",
        "evidence": evidence,
    }


def test_same_source_rate_gets_credit_when_subtype_is_lost() -> None:
    note = "Focal impaired-awareness episodes occur monthly."
    row = {
        "source_row_index": 3999,
        "note": note,
        "usable": True,
        "reference": [finding("g", "focal impaired-awareness episodes", note, 1)],
        "predicted": [finding("p", "seizures", "occur monthly", 1)],
        "pairs": [],
    }
    result = score_row(row)
    assert result["pairs"] == [
        {
            "gold_id": "g",
            "prediction_id": "p",
            "measurement_correct": True,
            "subtype_correct": False,
            "event_correct": False,
        }
    ]


def test_different_rates_do_not_gain_measurement_credit() -> None:
    note = "Focal impaired-awareness episodes occur monthly."
    row = {
        "source_row_index": 1,
        "note": note,
        "usable": True,
        "reference": [finding("g", "focal impaired-awareness episodes", note, 1)],
        "predicted": [finding("p", "focal impaired-awareness episodes", note, 2)],
        "pairs": [],
    }
    assert score_row(row)["pairs"][0] == {
        "gold_id": "g",
        "prediction_id": "p",
        "measurement_correct": False,
        "subtype_correct": True,
        "event_correct": True,
    }


def test_different_source_passages_do_not_cross_match() -> None:
    note = "Focal seizures occur monthly. Absence seizures occur weekly."
    row = {
        "source_row_index": 2,
        "note": note,
        "usable": True,
        "reference": [finding("g", "focal seizures", "Focal seizures occur monthly", 1)],
        "predicted": [finding("p", "focal seizures", "Absence seizures occur weekly", 1)],
        "pairs": [],
    }
    result = score_row(row)
    assert result["pairs"] == []
    assert result["unpaired_gold"] == ["g"]
    assert result["unpaired_predictions"] == ["p"]


def test_cluster_unit_is_separate_from_subtype() -> None:
    note = "Two clusters of focal seizures this month."
    row = {
        "source_row_index": 3,
        "note": note,
        "usable": True,
        "reference": [finding("g", "clusters of focal seizures", note, 2)],
        "predicted": [finding("p", "focal seizures", note, 2)],
        "pairs": [],
    }
    pair = score_row(row)["pairs"][0]
    assert pair["measurement_correct"]
    assert pair["subtype_correct"]
    assert not pair["event_correct"]
