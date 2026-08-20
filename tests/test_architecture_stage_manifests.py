"""Gates on the explanatory architecture layer.

These tests are the reason a method card can be trusted: they fail when the
manifest, the code, the teaching cases, and the published documents stop
agreeing with each other.
"""

from __future__ import annotations

import pytest

from clinical_extraction.architecture import stage_manifest as sm
from clinical_extraction.architecture.paper_teaching_cases import (
    build_paper_teaching_letters,
)
from clinical_extraction.architecture.render import all_documents
from clinical_extraction.architecture.teaching_case import build_exect_case
from scripts.build_architecture_docs import build


def test_manifests_agree_with_the_repository() -> None:
    problems = sm.validate_all()
    assert problems == [], sm.format_problems(problems)


def test_every_manifest_stage_resolves_to_a_real_callable() -> None:
    for manifest, stage in sm.iter_stages():
        assert stage.implementation.resolve() is not None, (
            f"{manifest.method_id}/{stage.stage_id}"
        )


def test_model_owned_stages_are_clinical_meaning_stages() -> None:
    """A model call proposes clinical content; it can never be inert."""

    for manifest, stage in sm.iter_stages():
        if stage.owner == "model":
            assert stage.effect_class == "clinical_meaning", (
                f"{manifest.method_id}/{stage.stage_id}"
            )


def test_deterministic_stages_declare_a_rule_category() -> None:
    for manifest, stage in sm.iter_stages():
        if stage.owner == "deterministic":
            assert stage.rule_category in sm.RULE_CATEGORIES, (
                f"{manifest.method_id}/{stage.stage_id}"
            )


@pytest.mark.local_corpus
def test_published_documents_match_the_pipeline() -> None:
    """The drift gate: docs/architecture/ must match a fresh render."""

    root = sm.repo_root()
    for path, content in build(root).items():
        relative = path.relative_to(root)
        assert path.is_file(), f"missing generated document: {relative}"
        assert path.read_text(encoding="utf-8") == content, (
            f"{relative} is stale; run python scripts/build_architecture_docs.py"
        )


def test_ownership_matrix_covers_every_method() -> None:
    rows = sm.ownership_matrix()
    assert {row["method_id"] for row in rows} == set(sm.METHOD_IDS)


def test_teaching_documents_work_the_four_paper_letters() -> None:
    cases = build_paper_teaching_letters()
    assert [case.letter_id for case in cases] == [
        "GAN-15431",
        "GAN-2166",
        "EA0186",
        "EA0057",
    ]
    documents = all_documents(cases)
    walk = documents["teaching_cases/six_paths.md"]
    index = documents["README.md"]
    gan_hub = documents["teaching_cases/gan2026.md"]
    exect_hub = documents["teaching_cases/exectv2.md"]

    assert "TEACH-GAN-01" not in walk
    assert "TEACH-EXECT-01" not in walk
    assert "synthetic letters" not in walk
    assert "GAN-15431" in walk
    assert "GAN-2166" in walk
    assert "EA0186" in walk
    assert "EA0057" in walk
    assert "reaches `1 cluster per 4 month, 5 per cluster`" not in walk

    for case in cases:
        path = f"teaching_cases/{case.letter_id.lower()}.md"
        body = documents[path]
        assert case.story in body
        assert case.mechanism in body
        assert case.gold in body
        assert case.letter_id in index
        assert case.letter_id in walk
        assert f"{case.letter_id.lower()}.md" in (
            gan_hub if case.task == "gan2026" else exect_hub
        )


def test_paper_exect_score_shows_what_left_the_line() -> None:
    letter = next(
        case
        for case in build_paper_teaching_letters()
        if case.letter_id == "EA0186"
    )
    for run in letter.runs:
        assert "vs gold:" not in run.final_answer
        assert "Workbench" in run.correctness_note
        assert "focal epilepsy" in run.final_answer
        assert "lamotrigine" in run.final_answer
        for family in (
            "Diagnosis",
            "Seizure frequency",
            "Prescription",
            "Investigations",
        ):
            assert family in run.final_answer
        score = next(obs for obs in run.observations if obs.stage_id.endswith(".score"))
        assert "vs gold:" not in str(score.output_value)
        assert "Workbench" in score.note


def test_ea0057_hybrid_lenses_show_clinical_rewrites_not_json() -> None:
    letter = next(
        case
        for case in build_paper_teaching_letters()
        if case.letter_id == "EA0057"
    )
    hybrid = next(
        run for run in letter.runs if run.method_id == "exectv2_llm_pre_post"
    )
    lenses = {
        obs.stage_id.split(".")[-1]: obs
        for obs in hybrid.observations
        if ".lens." in obs.stage_id
    }
    diagnosis = lenses["diagnosis"]
    assert diagnosis.changed is True
    assert "symptomatic structural focal epilepsy" in str(diagnosis.output_value)
    assert "rewrote" in diagnosis.note.lower()
    assert "Canonical LLM-with-rules" not in diagnosis.note
    assert len(str(diagnosis.input_value)) < 600
    assert lenses["seizure_frequency"].changed is False
    assert lenses["prescription"].changed is False
    assert lenses["investigations"].changed is False


def test_synthetic_exect_score_stays_unscored_without_gold() -> None:
    run = build_exect_case().runs[0]
    assert "no gold annotations" in run.correctness_note
    assert not run.final_answer.startswith("clinical-fact F1")
