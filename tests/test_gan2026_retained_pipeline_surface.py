from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026 import runner


def test_gan2026_cli_uses_plain_pipeline_names() -> None:
    assert set(runner.get_cli_specs()) == {
        "rules",
        "llm",
        "llm_with_rules",
    }


def test_gan2026_internal_runners_keep_retained_evidence_ids() -> None:
    assert set(runner._ITEM_RUNNERS) == {
        "deterministic_canonical_pipeline",
        "llm_only_canonical_pipeline",
        "hybrid_structured_events",
    }


def test_gan2026_retained_ids_have_plain_method_labels() -> None:
    assert runner.PIPELINE_METHOD == {
        "deterministic_canonical_pipeline": "rules_only",
        "llm_only_canonical_pipeline": "llm_only",
        "hybrid_structured_events": "llm_with_rules",
    }
