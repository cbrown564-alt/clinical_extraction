"""Narrow floors that keep Luna rescues while cutting Qwen/DeepSeek regressions.

Portability: ``benchmark_format`` for singleton-cluster dual-form; otherwise
``seizure_frequency``.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    typical_recurring_rate_over_ytd_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
)


def test_singleton_cluster_cadence_collapses_to_unknown() -> None:
    assert repair_prediction_label("1 cluster per month") == "unknown"
    assert repair_prediction_label("1 clusters per day") == "unknown"
    assert repair_prediction_label("1 cluster in 1 day") == "unknown"


def test_multi_cluster_cadence_still_dual_forms() -> None:
    assert repair_prediction_label("3 clusters per month") == (
        "3 cluster per month, multiple per cluster"
    )
    assert repair_prediction_label("2 clusters over 3 weeks") == (
        "2 cluster per 3 week, multiple per cluster"
    )


def test_diary_still_preserves_explicit_fortnight_range() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "2 in Aug, 0 in Jul, one in Jun",
                    "applies_to": None,
                    "time_window": "Jun-Aug",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "earlier two in Aug, 0 in Jul and one in Jun",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "seven to nine seizures during the last two weeks",
                    "applies_to": None,
                    "time_window": "last fortnight",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "over the last fortnight she has had seven to nine seizures "
                        "during the last two weeks"
                    ),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "7 to 9 per 2 weeks",
                "evidence": (
                    "over the last fortnight she has had seven to nine seizures "
                    "during the last two weeks"
                ),
                "confidence": "high",
                "rationale": "Recent two-week overall seizure count.",
            },
        }
    )
    note = (
        "Clinic Date: 10 September 2024. this month so far she has 2 seizures; "
        "earlier two in Aug, 0 in Jul and one in Jun. In contrast, over the last "
        "fortnight she has had seven to nine seizures during the last two weeks."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label == "7 to 9 per 2 week"


def test_diary_may_overwrite_short_current_month_seizure_free() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "2 in May, 2 in Jun, 2 in Jul, 2 in Aug",
                    "applies_to": None,
                    "time_window": "May-Aug",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "May 2, June 2, July 2, August 2 seizures",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "seizure free for this month",
                    "applies_to": None,
                    "time_window": "this month",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "She has been seizure free for this month",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for this month",
                "evidence": "She has been seizure free for this month",
                "confidence": "medium",
                "rationale": "Current month without seizures.",
            },
        }
    )
    note = (
        "Clinic Date: 10 September 2024. "
        "May 2, June 2, July 2, August 2 seizures. "
        "She has been seizure free for this month."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert not extraction.selection.final_label.startswith("seizure free")


def test_diary_still_preserves_dated_seizure_free_since() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "five seizures during sleep and three while awake",
                    "applies_to": None,
                    "time_window": "February",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": (
                        "in February she had five seizures during sleep and three while awake"
                    ),
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "seizure-free since 29/09/2017",
                    "applies_to": None,
                    "time_window": "since 29/09/2017",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "Importantly, Liam Carter has been seizure-free since 29/09/2017."
                    ),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free since 29/09/2017",
                "evidence": (
                    "Importantly, Liam Carter has been seizure-free since 29/09/2017."
                ),
                "confidence": "high",
                "rationale": "Sustained current seizure freedom since 29/09/2017.",
            },
        }
    )
    note = (
        "Clinic Date: 14 June 2018. "
        "in February she had five seizures during sleep and three while awake, "
        "prior to the sustained improvement. Importantly, Liam Carter has been "
        "seizure-free since 29/09/2017."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label.startswith("seizure free")


def test_typical_ytd_requires_year_to_date_selection_language() -> None:
    extraction = SimpleNamespace(
        events=[
            SimpleNamespace(
                event_id="e2",
                kind="frequency_rate",
                raw_value="a focal seizure monthly",
                applies_to=None,
                time_window="present",
                temporality="current",
                assertion_status="asserted",
                evidence="At present, his typical pattern is a focal seizure monthly",
                notes=None,
            )
        ],
        selection=SimpleNamespace(
            selected_event_ids=["e1"],
            final_kind="frequency",
            final_label="7 per 4 month",
            evidence="seven seizures over four months",
            confidence="high",
            rationale="Observation total over recent months.",
        ),
    )
    assert typical_recurring_rate_over_ytd_from_events(extraction, "7 per 4 month") is None


def test_typical_ytd_still_fires_with_so_far_this_year_selection() -> None:
    extraction = SimpleNamespace(
        events=[
            SimpleNamespace(
                event_id="e2",
                kind="frequency_rate",
                raw_value="a focal seizure monthly",
                applies_to=None,
                time_window="present",
                temporality="current",
                assertion_status="asserted",
                evidence="At present, his typical pattern is a focal seizure monthly",
                notes=None,
            )
        ],
        selection=SimpleNamespace(
            selected_event_ids=["e1"],
            final_kind="frequency",
            final_label="7 so far this year",
            evidence="only seven seizures reported so far this year",
            confidence="high",
            rationale="Year-to-date count.",
        ),
    )
    assert (
        typical_recurring_rate_over_ytd_from_events(extraction, "7 per 10 month")
        == "1 per month"
    )
