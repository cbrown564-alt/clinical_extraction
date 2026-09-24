"""Keep calendar-window aliases narrow in compact finding scoring."""

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v08 as scorer,
)


def test_reported_month_range_aliases() -> None:
    assert scorer.window_equal("Jan through Jul 2022", "January–July 2022")
    assert scorer.window_equal("Jun to July", "June to July")
    assert scorer.window_equal("Oct and December", "October and December")


def test_separate_months_do_not_become_continuous_range() -> None:
    assert not scorer.window_equal("October and December", "October to December")
    assert not scorer.window_equal("Nov and Jan", "November to January")


def test_relative_window_distinctions_remain() -> None:
    assert scorer.window_equal("in the past six weeks", "past six weeks")
    assert not scorer.window_equal("past six weeks", "last six weeks")
