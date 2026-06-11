"""Tests for the ExECTv2 three-way (rules/llm_only/hybrid) comparison report."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    three_way_comparison as twc,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.three_way_comparison import (
    ARCHITECTURE_FAMILY,
    ComparisonRow,
    build_comparison_rows,
    render_comparison_markdown,
)

_FULL_METRICS = {
    "phrase_only_per_item_f1": 0.5,
    "phrase_only_per_letter_f1": 0.7,
    "sf_semantic_per_item_f1": 0.3,
    "sf_semantic_per_letter_f1": 0.5,
    "sf_benchmark_per_item_f1": 0.3,
    "sf_benchmark_per_letter_f1": 0.5,
}


def _registry_record(run_id: str, family: str, model: str, row_count: int) -> dict:
    return {
        "run_id": run_id,
        "pipeline_family": family,
        "split": "dev",
        "model": model,
        "row_count": row_count,
        "primary_metrics": dict(_FULL_METRICS),
    }


def test_architecture_family_mapping_covers_all_four_families() -> None:
    assert ARCHITECTURE_FAMILY["exectv2_deterministic"] == "rules"
    assert ARCHITECTURE_FAMILY["exectv2_llm_only_single_pass"] == "llm_only"
    assert ARCHITECTURE_FAMILY["exectv2_llm_only_per_entity"] == "llm_only"
    assert ARCHITECTURE_FAMILY["exectv2_hybrid"] == "hybrid"


def test_render_includes_every_family_and_the_benchmark_target() -> None:
    rows = [
        ComparisonRow(
            "rules", "deterministic_sf", "(model-independent)", 140, _FULL_METRICS, "live"
        ),
        ComparisonRow("llm_only", "single_pass", "m", 140, _FULL_METRICS, "registry:r1"),
        ComparisonRow("hybrid", "candidate_assessment", "m", 140, _FULL_METRICS, "registry:r2"),
    ]
    md = render_comparison_markdown("m", rows, "dev")

    assert "| rules |" in md
    assert "| llm_only |" in md
    assert "| hybrid |" in md
    # benchmark target row carries the published SF cell
    assert f"{twc.SF_BENCHMARK_PER_ITEM_F1:.3f}" in md
    assert f"{twc.SF_BENCHMARK_PER_LETTER_F1:.3f}" in md
    # provenance for registered rows is traced
    assert "r1" in md and "r2" in md


def test_partial_run_excluded_from_table_and_listed_separately() -> None:
    rows = [
        ComparisonRow(
            "rules", "deterministic_sf", "(model-independent)", 140, _FULL_METRICS, "live"
        ),
        ComparisonRow(
            "hybrid", "candidate_assessment", "m", 50, _FULL_METRICS,
            "registry:partial", partial=True,
        ),
    ]
    md = render_comparison_markdown("m", rows, "dev")

    assert "## Excluded partial runs" in md
    assert "## Coverage gaps" in md  # hybrid has no full run for this model
    # the partial row's config does not appear as a scored table row
    score_section = md.split("## Provenance")[0]
    assert "candidate_assessment" not in score_section


def test_build_filters_by_model_and_split(tmp_path: Path, monkeypatch) -> None:
    rules_row = ComparisonRow(
        "rules", "deterministic_sf", "(model-independent)", 140, _FULL_METRICS, "live"
    )
    monkeypatch.setattr(twc, "compute_rules_row", lambda split="dev": rules_row)

    registry = tmp_path / "registry.jsonl"
    records = [
        _registry_record("a", "exectv2_hybrid", "model-a", 140),
        _registry_record("b", "exectv2_llm_only_single_pass", "model-b", 140),
        _registry_record("c", "exectv2_hybrid", "model-a", 50),  # partial
    ]
    registry.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

    rows = build_comparison_rows("model-a", registry, "dev")

    assert rows[0].family == "rules"  # always first, model-independent
    # model-b's run is filtered out; only model-a's two hybrid runs remain
    non_rules = [r for r in rows if r.family != "rules"]
    assert {r.model for r in non_rules} == {"model-a"}
    assert all(r.family == "hybrid" for r in non_rules)
    # one full (140) and one partial (50) hybrid run, the latter flagged
    assert sorted((r.n_letters, r.partial) for r in non_rules) == [(50, True), (140, False)]
