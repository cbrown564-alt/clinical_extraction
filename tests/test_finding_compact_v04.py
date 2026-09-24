"""The versioned window correction must preserve meaningful distinctions."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v04 as matcher,
)

FIXTURES = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_r9_compact_v03_no_call/"
    "v03_fictional_fixtures.json"
)


def test_relative_window_prefixes_match_without_changing_period() -> None:
    for left, right in (
        ("past six months", "the past six months"),
        ("over the past six months", "the past six months"),
        ("in the past three months", "the past three months"),
        ("current month to date", "the current month to date"),
    ):
        assert matcher.window_equal(left, right)
    for left, right in (
        ("past month", "past six months"),
        ("last week", "past week"),
        ("since March", "in March"),
        (None, "the past month"),
    ):
        assert not matcher.window_equal(left, right)
    assert matcher.window_equal("since March", "March", seizure_free=True)
    assert not matcher.window_equal("since March", "March")
    assert matcher.window_equal("in 2015 so far", "2015 so far")


def test_window_fix_does_not_hide_event_or_restriction_errors() -> None:
    case = json.loads(FIXTURES.read_text())[0]
    note = case["note"]
    gold = case["response"]["findings"]
    prediction = copy.deepcopy(gold[0])
    prediction["time"]["source"] = "past six months"
    reference = copy.deepcopy(gold[0])
    reference["time"]["source"] = "the past six months"
    assert "window" not in matcher.attribute_diffs(prediction, reference, note)
    prediction["event"]["scope"] = "overall"
    assert "event" in matcher.attribute_diffs(prediction, reference, note)
    prediction = copy.deepcopy(reference)
    prediction["restriction"] = "witnessed-only"
    assert "restriction" in matcher.attribute_diffs(prediction, reference, note)
