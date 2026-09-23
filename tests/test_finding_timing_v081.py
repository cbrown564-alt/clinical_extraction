from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)
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


def test_adjudication_examples_and_rendered_r9_prompt() -> None:
    decisions = overrides()
    assert decisions[14530, "f1"][0] == "current"
    assert decisions[2965, "f4"][0] == "historical"
    assert (4597, "f3") not in decisions  # ongoing eight-week absence
    payload = r9.prompt_payload(
        "Clinic Date: 14 June 2019. Initial seizure in March 2019."
    )
    instructions = " ".join(payload["schema_instructions"])
    assert "more than one calendar year" in instructions
    assert "Exactly one year ago" in instructions
    assert "no usable date" in instructions
    assert "short, source-supported name" in instructions
    assert "brief nocturnal episodes" in instructions
    assert "seizures, seizure days and clusters" in instructions
    assert "the next sentence says only 'seizure frequency'" in instructions
    assert "Do not narrow an overall event rate to the predominant subtype" in instructions
    assert "name convulsive activity and keep the log wording" in instructions
    assert "historical only when the source explicitly marks" not in instructions
    assert payload["output_schema"]["$defs"]["QualitativeFrequency"]["properties"][
        "frequency"
    ]["enum"] == ["occasional", "frequent"]
