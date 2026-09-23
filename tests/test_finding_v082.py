from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v082


def test_duration_is_scored_and_since_anchor_is_context() -> None:
    note = "Seizure-free for two years since May 2023."
    base = {
        "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
        "timing": "current",
        "evidence": note,
    }
    gold = {
        **base,
        "id": "g",
        "measurement": {
            "type": "seizure_free",
            "duration": {"type": "number", "value": 2, "unit": "year"},
            "since": {"time": "May 2023", "form": "calendar"},
        },
    }
    prediction = {
        **base,
        "id": "p",
        "measurement": {
            "type": "seizure_free",
            "duration": {"type": "number", "value": 2, "unit": "year"},
        },
    }
    assert finding_v082.compatible(prediction, gold, note)
    prediction["measurement"]["duration"]["value"] = 1
    assert not finding_v082.compatible(prediction, gold, note)
