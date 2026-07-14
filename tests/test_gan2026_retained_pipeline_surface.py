from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026 import runner


def test_gan2026_cli_exposes_only_retained_architectures() -> None:
    assert set(runner.get_cli_specs()) == {
        "deterministic_canonical_pipeline",
        "llm_only_canonical_pipeline",
        "hybrid_structured_events",
    }


def test_gan2026_single_item_runner_exposes_exact_three_family_matrix() -> None:
    assert set(runner._ITEM_RUNNERS) == {
        "deterministic_canonical_pipeline",
        "llm_only_canonical_pipeline",
        "hybrid_structured_events",
    }
