from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v08 as v08


def finding(
    ident: str,
    event: str,
    measurement: dict,
    evidence: str,
    *,
    period: str | None = None,
) -> dict:
    result = {
        "id": ident,
        "event": {"type": event, "scope": "unspecified", "seizure_status": "stated"},
        "measurement": measurement,
        "timing": "current",
        "evidence": evidence,
    }
    if period:
        result["period"] = {"time": period}
    return result


def test_numeric_and_qualitative_companion_become_one_finding() -> None:
    note = "Events are now infrequent, with two seizures this month."
    source = [
        finding(
            "f1",
            "seizures",
            {"type": "count", "count": {"type": "number", "value": 2}},
            note,
            period="this month",
        ),
        finding("f2", "seizures", {"type": "qualitative", "frequency": "decreased"}, note),
        finding("f3", "seizures", {"type": "qualitative", "frequency": "rare"}, note),
    ]
    output, actions = v08.project(note, source)
    assert [item["id"] for item in output] == ["f1"]
    assert {item["rule"] for item in actions} == {
        "drop_nonlevel_qualitative",
        "map_qualitative_level",
        "drop_level_companion",
    }


def test_diary_months_include_zero_and_reverse_order() -> None:
    note = "Clinic Date: 24 September 2011. Seizures: 2 so far in Sep, one in Aug, and 0 in Jul."
    source = [
        finding(
            "f1",
            "seizures",
            {"type": "count", "count": {"type": "number", "value": 2}},
            "2 so far in Sep",
            period="so far in Sep",
        ),
        finding(
            "f2",
            "seizures",
            {"type": "count", "count": {"type": "number", "value": 1}},
            "one in Aug",
            period="Aug",
        ),
        finding(
            "f3",
            "seizures",
            {"type": "seizure_free", "duration": {"type": "qualitative", "quantity": "Jul"}},
            "0 in Jul",
            period="in Jul",
        ),
    ]
    output, actions = v08.project(note, source, source_row_index=16091)
    assert len(output) == 1
    assert output[0]["measurement"]["count"]["value"] == 3
    assert output[0]["period"]["time"] == "in Jul to so far in Sep"
    assert [item["rule"] for item in actions] == ["combine_month_counts"]


def test_historical_incidents_and_mixed_event_types_are_not_summed() -> None:
    note = "A seizure in May 2017. Another seizure in November 2017."
    source = [
        finding(
            "f1",
            "seizure",
            {
                "type": "count",
                "count": {"type": "number", "value": 1},
                "occurred_at": {"time": "May 2017"},
            },
            "A seizure in May 2017.",
        ),
        finding(
            "f2",
            "seizure",
            {
                "type": "count",
                "count": {"type": "number", "value": 1},
                "occurred_at": {"time": "November 2017"},
            },
            "Another seizure in November 2017.",
        ),
    ]
    output, actions = v08.project(note, source, source_row_index=14524)
    assert output == source
    assert not actions


def test_same_source_window_wording_matches_but_other_denominator_does_not() -> None:
    note = 'Over the past week she reports "2 or 4 seizures this week".'
    count = {"type": "count", "count": {"type": "range", "lower": 2, "upper": 4}}
    gold = finding("g", "seizures", count, note, period="the past week")
    prediction = finding("p", "seizures", count, "2 or 4 seizures this week", period="this week")
    assert v08.compatible(prediction, gold, note)
    other = finding("p", "seizures", count, "2 or 4 seizures this week", period="this year")
    assert not v08.compatible(other, gold, note)


def test_dated_list_is_one_count_and_shared_negative_is_one_finding() -> None:
    note = (
        "Seizure events on 06-03, 06-13, 09-23 as recorded in the diary. "
        "No auras, convulsions or other seizures since March."
    )
    dates = [
        finding(
            f"f{i}",
            "seizures",
            {
                "type": "count",
                "count": {"type": "number", "value": 1},
                "occurred_at": {"time": date},
            },
            "Seizure events on 06-03, 06-13, 09-23",
        )
        for i, date in enumerate(("06-03", "06-13", "09-23"), start=1)
    ]
    absence = [
        finding(
            f"f{i}",
            label,
            {"type": "seizure_free", "since": {"time": "March"}},
            "No auras, convulsions or other seizures since March.",
            period="since March",
        )
        for i, label in enumerate(("auras", "convulsions", "seizures"), start=4)
    ]
    output, actions = v08.project(note, dates + absence, source_row_index=4337)
    assert len(output) == 2
    assert output[0]["measurement"]["count"]["value"] == 3
    assert output[1]["event"]["type"] == "events"
    assert {action["rule"] for action in actions} == {
        "combine_date_counts",
        "combine_negative_list",
    }
