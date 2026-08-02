"""Gates on the executable teaching cases.

A teaching case is only worth publishing if it runs the real pipeline and
covers every stage the manifest claims exists. These tests enforce both, plus
the specific ownership facts the 2026-07-30 review found misstated.
"""

from __future__ import annotations

import pytest

from clinical_extraction.architecture import stage_manifest as sm
from clinical_extraction.architecture import teaching_case as tc


@pytest.fixture(scope="module")
def cases() -> tuple[tc.TeachingCase, ...]:
    return tc.build_all_cases()


def test_both_teaching_cases_build(cases: tuple[tc.TeachingCase, ...]) -> None:
    assert len(cases) == 2
    for case in cases:
        assert len(case.runs) == 3


def test_every_manifest_stage_is_observed(cases: tuple[tc.TeachingCase, ...]) -> None:
    """A stage nobody can show running is a stage nobody can trust."""

    for case in cases:
        for run in case.runs:
            manifest = sm.load_manifest(run.method_id)
            observed = {obs.stage_id for obs in run.observations}
            declared = {stage.stage_id for stage in manifest.stages}
            assert observed == declared, (
                f"{run.method_id}: missing {sorted(declared - observed)}, "
                f"unexpected {sorted(observed - declared)}"
            )


def test_observations_follow_manifest_order(cases: tuple[tc.TeachingCase, ...]) -> None:
    for case in cases:
        for run in case.runs:
            manifest = sm.load_manifest(run.method_id)
            assert [obs.stage_id for obs in run.observations] == [
                stage.stage_id for stage in manifest.stages
            ], run.method_id


def test_gan_case_shows_rules_rescuing_the_model(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    """The teaching point of the Gan case, asserted rather than narrated."""

    gan = cases[0]
    by_method = {run.method_id: run for run in gan.runs}

    llm_only = by_method["gan2026_llm_only"]
    hybrid = by_method["gan2026_llm_with_rules"]

    # Both methods start from the same wrong model answer.
    assert llm_only.final_answer == "7 per year"
    assert llm_only.correct is False

    # The hybrid's deterministic layer corrects it to the gold answer.
    assert hybrid.final_answer == gan.gold
    assert hybrid.correct is True


def test_gan_hybrid_selection_is_attributed_to_the_model(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    """Review finding 5: the selection belongs to the model, not to a rule."""

    hybrid = cases[0].runs[2]
    model_call = next(
        obs for obs in hybrid.observations if obs.stage_id == "gan.hybrid.model_call"
    )
    assert model_call.owner == "model"
    assert "selected_event_ids" in str(model_call.output_value)

    resolve = next(
        obs for obs in hybrid.observations if obs.stage_id == "gan.hybrid.resolve_label"
    )
    assert resolve.owner == "deterministic"
    assert "model selected" in str(resolve.input_value)


def test_exactly_one_repair_family_is_credited_with_the_gan_rescue(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    """The rescue must be attributed to a named family, not to 'the rules'."""

    hybrid = cases[0].runs[2]
    fired = [
        obs
        for obs in hybrid.observations
        if obs.stage_id.startswith("gan.hybrid.repair.") and obs.changed
    ]
    assert len(fired) == 1
    assert fired[0].stage_id == "gan.hybrid.repair.typical_over_ytd"
    assert fired[0].input_value == "7 per year"
    assert fired[0].output_value == "1 per month"


def test_repair_walk_refuses_to_publish_an_unreproducible_attribution() -> None:
    """The attribution guard must actually raise, not merely exist."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events as hybrid,
    )

    extraction, _, _, trace = hybrid.parse_structured_json_with_trace(
        tc.GAN_HYBRID_RAW_OUTPUT,
        note_text=tc.GAN_NOTE_TEXT,
        repair_config=hybrid.StructuredRepairConfig.for_mode("hybrid_full_stack"),
    )
    model_extraction = hybrid.StructuredExtractionRecord.model_validate(
        trace["model_prediction"]["record"]
    )
    with pytest.raises(tc.RepairAttributionError):
        tc._gan_repair_walk(
            model_extraction,
            trace["deterministic_semantic"]["before_label"],
            note_text=tc.GAN_NOTE_TEXT,
            repair_config=hybrid.StructuredRepairConfig.for_mode("hybrid_full_stack"),
            expected_final_label="a label the pipeline never produced",
        )


def test_exect_case_keeps_the_comparison_boundary_visible(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    """Review finding 7: nine entities is not four families."""

    exect = cases[1]
    rules_only = exect.runs[0]
    scoring = rules_only.observations[-1]
    assert "nine entities" in scoring.input_value

    for run in exect.runs[1:]:
        assert "four families" in run.observations[-1].input_value


def test_teaching_cases_claim_no_correctness_without_gold(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    for run in cases[1].runs:
        assert run.correct is None
        assert "no correctness verdict is claimed" in run.correctness_note
        assert "unscored scorer-boundary illustration" in run.observations[-1].note.lower()


def test_teaching_cases_label_their_fixture_boundary(
    cases: tuple[tc.TeachingCase, ...],
) -> None:
    """A fixture that does not announce itself is how a trace misleads."""

    for case in cases:
        assert "fixture" in case.fixture_note.lower()
        assert "no model call is made" in case.fixture_note.lower()
        model_stages = [
            obs
            for run in case.runs
            for obs in run.observations
            if obs.owner == "model"
        ]
        assert model_stages
        for obs in model_stages:
            assert "fixture" in obs.note.lower()
