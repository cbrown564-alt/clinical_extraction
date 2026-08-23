"""Focused checks for the Gan teaching-letter library (TEACH-GAN-02/03).

The library extends the canonical teaching case with letters that each
isolate one mechanism: a monthly-diary span rescue and a preservation
stand-down. Building any case executes the real selected implementations
with fixture model output; no model calls are made and no locked rows are
read. If a repair family or preservation rule changes behaviour, these
tests fail rather than publish an invented mechanism story.
"""

from __future__ import annotations

import pytest

from clinical_extraction.architecture.teaching_case import (
    build_gan_letter_library,
    build_teaching_letters,
)


def _runs_by_method(case):
    return {run.method_id: run for run in case.runs}


def _repair_observations(run, family: str):
    return [
        obs
        for obs in run.observations
        if obs.stage_id == f"gan.llm_with_rules.repair.{family}"
    ]

@pytest.mark.local_corpus
def test_library_stays_apart_from_the_paper_explainer_letters():
    library = build_gan_letter_library()
    assert [case.letter_id for case in library] == ["TEACH-GAN-02", "TEACH-GAN-03"]
    assert all(case.task == "gan2026" for case in library)
    letters = build_teaching_letters()
    assert [case.letter_id for case in letters] == [
        "GAN-15431",
        "GAN-2166",
        "EA0186",
        "EA0057",
    ]
    assert all(case.story for case in library)


def test_diary_letter_recomputes_the_span_rate():
    diary = build_gan_letter_library()[0]
    runs = _runs_by_method(diary)

    # Two real failure modes on this letter: rules find no extraction target,
    # and the model answers from the most recent month.
    assert runs["gan2026_rules_only"].final_answer == "no seizure frequency reference"
    assert runs["gan2026_rules_only"].correct is False
    assert runs["gan2026_llm_only"].final_answer == "2 per month"
    assert runs["gan2026_llm_only"].correct is False

    # The hybrid is rescued by exactly one family: monthly_diary.
    hybrid = runs["gan2026_llm_with_rules"]
    assert hybrid.final_answer == "4 per 6 month"
    assert hybrid.correct is True
    fired = [obs for obs in hybrid.observations if ".repair." in obs.stage_id and obs.changed]
    assert [obs.stage_id for obs in fired] == ["gan.llm_with_rules.repair.monthly_diary"]
    assert str(fired[0].input_value) == "2 per month"
    assert str(fired[0].output_value) == "4 per 6 month"


def test_seizure_free_letter_surfaces_elapsed_since_date_duration():
    free = build_gan_letter_library()[1]
    runs = _runs_by_method(free)

    assert all(run.correct is True for run in runs.values())

    hybrid = runs["gan2026_llm_with_rules"]
    elapsed = _repair_observations(hybrid, "elapsed_anchor")
    assert len(elapsed) == 1
    obs = elapsed[0]
    assert obs.changed is False
    assert hybrid.final_answer == "seizure free for multiple month"
