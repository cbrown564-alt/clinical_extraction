"""Projection and anti-regression floor for Luna residual rows.

Portability:
- cluster/range projection steps are ``benchmark_format``
- monthly-diary anti-regression is ``seizure_frequency``
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    Portability,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_STEPS,
    repair_prediction_label,
    repair_prediction_label_with_evidence,
)


def test_projection_steps_are_benchmark_format() -> None:
    rule_ids = {
        "benchmark_repair.or_count_ranges",
        "benchmark_repair.cluster_over_in_window",
    }
    matched = [step for step in BENCHMARK_REPAIR_STEPS if step.rule_id in rule_ids]
    assert {step.rule_id for step in matched} == rule_ids
    assert all(step.portability is Portability.BENCHMARK_FORMAT for step in matched)


def test_repair_projects_or_count_range_to_to_range() -> None:
    assert repair_prediction_label("1 or 3 per month") == "1 to 3 per month"


def test_repair_with_evidence_keeps_or_count_range_as_to_range() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 or 3 per month",
            "one or three seizures last month",
        )
        == "1 to 3 per month"
    )


def test_repair_projects_cadence_only_cluster_to_multiple_per_cluster() -> None:
    assert repair_prediction_label("3 clusters per month") == (
        "3 cluster per month, multiple per cluster"
    )
    assert repair_prediction_label("2 clusters per 3 weeks") == (
        "2 cluster per 3 week, multiple per cluster"
    )


def test_repair_projects_cluster_over_window_before_unknown() -> None:
    assert repair_prediction_label("2 clusters over 3 weeks") == (
        "2 cluster per 3 week, multiple per cluster"
    )
    assert repair_prediction_label("2 clusters in 3 weeks") == (
        "2 cluster per 3 week, multiple per cluster"
    )


def _record(note_text: str, gold_label: str, monthly: float) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=1,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference=gold_label,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(monthly * 12.0, monthly * 12.0),
        gold_monthly_frequency=monthly,
    )


def test_monthly_diary_does_not_overwrite_selected_seizure_free() -> None:
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
                    "kind": "frequency_rate",
                    "raw_value": "two in sleep and three while awake",
                    "applies_to": None,
                    "time_window": "March",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "in March she had two in sleep and three while awake",
                    "notes": None,
                },
                {
                    "event_id": "e3",
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
                "selected_event_ids": ["e3"],
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
        "and in March she had two in sleep and three while awake, prior to the "
        "sustained improvement. Importantly, Liam Carter has been seizure-free "
        "since 29/09/2017."
    )
    extraction, _, errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label.startswith("seizure free")
    assert "13 per 2 month" not in " ".join(errors)


def test_monthly_diary_does_not_overwrite_selected_recent_week_rate() -> None:
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
