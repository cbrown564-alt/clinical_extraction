"""Gates on the explanatory architecture layer.

These tests are the reason a method card can be trusted: they fail when the
manifest, the code, the teaching cases, and the published documents stop
agreeing with each other.
"""

from __future__ import annotations

import pytest

from clinical_extraction.architecture import stage_manifest as sm
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
