"""Gates on the explanatory architecture layer.

These tests are the reason a method card can be trusted: they fail when the
manifest, the code, the teaching cases, and the published documents stop
agreeing with each other.
"""

from __future__ import annotations

import json

import pytest

from clinical_extraction.architecture import stage_manifest as sm
from clinical_extraction.architecture.render import all_documents
from clinical_extraction.architecture.teaching_case import build_all_cases
from scripts.build_architecture_docs import build


def test_every_selected_method_has_a_manifest() -> None:
    assert len(sm.load_manifests()) == len(sm.METHOD_IDS) == 6


def test_manifests_agree_with_the_repository() -> None:
    problems = sm.validate_all()
    assert problems == [], sm.format_problems(problems)


def test_every_manifest_stage_resolves_to_a_real_callable() -> None:
    for manifest, stage in sm.iter_stages():
        assert stage.implementation.resolve() is not None, (
            f"{manifest.method_id}/{stage.stage_id}"
        )


def test_every_method_names_exactly_one_first_proposer() -> None:
    for manifest in sm.load_manifests():
        proposing = [
            stage
            for stage in manifest.stages
            if stage.effect_class == "clinical_meaning"
        ]
        assert proposing, f"{manifest.method_id} has no clinical-meaning stage"
        assert manifest.prediction_owner.strip(), manifest.method_id


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


def test_gan_hybrid_prediction_ownership_is_stated_as_model_led() -> None:
    """Finding 5 of the 2026-07-30 review: this is the fact that was wrong."""

    manifest = sm.load_manifest("gan2026_llm_with_rules")
    model_call = manifest.stage("gan.llm_with_rules.model_call")
    assert model_call.owner == "model"
    assert "select" in model_call.operation.lower()
    assert "selected_event_ids" in model_call.operation


def test_gan_llm_only_declares_its_repair_as_a_clinical_stage() -> None:
    """Finding 4: the LLM-only adapter is not merely formatting."""

    manifest = sm.load_manifest("gan2026_llm_only")
    repair = manifest.stage("gan.llm.selected_evidence_repair")
    assert repair.effect_class == "clinical_meaning"
    assert repair.owner == "deterministic"


def test_exect_hybrid_names_the_historical_v08_control_as_not_this_method() -> None:
    """Finding 2: current and historical must not share an unqualified name."""

    manifest = sm.load_manifest("exectv2_llm_with_rules")
    roles = {related.role for related in manifest.related_paths}
    assert "historical performance control" in roles
    historical = [
        related
        for related in manifest.related_paths
        if related.role == "historical performance control"
    ]
    assert any("v08" in related.note for related in historical)


def test_manifest_json_round_trips() -> None:
    for method_id in sm.METHOD_IDS:
        manifest = sm.load_manifest(method_id)
        payload = json.loads(sm.manifest_path(method_id).read_text(encoding="utf-8"))
        assert manifest.to_dict()["stages"][0]["stage_id"] == (
            payload["stages"][0]["stage_id"]
        )


def test_stage_ids_are_unique_across_the_whole_system() -> None:
    seen: set[str] = set()
    for _manifest, stage in sm.iter_stages():
        assert stage.stage_id not in seen, f"duplicate {stage.stage_id}"
        seen.add(stage.stage_id)


def test_ownership_matrix_covers_every_method() -> None:
    rows = sm.ownership_matrix()
    assert {row["method_id"] for row in rows} == set(sm.METHOD_IDS)


@pytest.mark.parametrize("method_id", sm.METHOD_IDS)
def test_one_sentence_and_sixty_second_explanations_exist(method_id: str) -> None:
    manifest = sm.load_manifest(method_id)
    assert len(manifest.one_sentence.split()) >= 8
    assert len(manifest.sixty_second.split()) >= 60


def test_published_documents_match_the_pipeline() -> None:
    """The drift gate: docs/architecture/ must match a fresh render."""

    root = sm.repo_root()
    for path, content in build(root).items():
        relative = path.relative_to(root)
        assert path.is_file(), f"missing generated document: {relative}"
        assert path.read_text(encoding="utf-8") == content, (
            f"{relative} is stale; run python scripts/build_architecture_docs.py"
        )


def test_rendered_documents_cover_all_six_methods_and_both_cases() -> None:
    documents = all_documents(build_all_cases())
    for method_id in sm.METHOD_IDS:
        assert f"method_cards/{method_id}.md" in documents
    assert "teaching_cases/gan2026.md" in documents
    assert "teaching_cases/exectv2.md" in documents
    walkthrough = documents["teaching_cases/six_paths.md"]
    assert walkthrough.count("### ") == 6
    assert "Deliberate failure and recovery" in walkthrough
    assert "gan2026_llm_only" in walkthrough
    assert "exectv2_llm_with_rules" in walkthrough
