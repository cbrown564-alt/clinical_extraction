from __future__ import annotations

from scripts.benchmarks.retime_findings_v081 import one_year_classification, overrides


def test_one_year_boundary_and_coarse_date_uncertainty() -> None:
    clinic = "14 June 2024"
    assert one_year_classification("14 June 2023", clinic) == "current"
    assert one_year_classification("13 June 2023", clinic) == "historical"
    assert one_year_classification("March 2024", clinic) == "current"
    assert one_year_classification("March 2022", clinic) == "historical"
    assert one_year_classification("2023", clinic) is None
    assert one_year_classification("14 months ago", clinic) == "historical"
    assert one_year_classification("six months ago", clinic) == "current"


def test_adjudication_examples() -> None:
    decisions = overrides()
    assert decisions[14530, "f1"][0] == "current"
    assert decisions[2965, "f4"][0] == "historical"
    assert (4597, "f3") not in decisions  # ongoing eight-week absence
