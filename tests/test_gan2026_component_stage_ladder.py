"""Gan 2026 component stage-ladder replay tests.

These cover the consolidation goal of the component-impact ablation plan: every
architecture decomposes into a cumulative purist-accuracy ladder through one seam,
scored on one identical row basis, with no model calls. The fast, self-contained
replay providers (structured-events + LLM-only) are exercised here; the
deterministic re-run and hybrid deep-replay providers are covered by their own
pipelines and are not re-run in unit tests.
"""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    component_stage_ladder as csl,
)


def _spec(run_id: str) -> csl.ArchitectureSpec:
    return next(spec for spec in csl.DEFAULT_ARCHITECTURE_SPECS if spec.run_id == run_id)


def _ladder(run_id: str) -> dict[str, object]:
    return csl.build_architecture_ladder(
        _spec(run_id), records=None, generated_on="2026-06-24"
    )


def test_structured_events_decomposes_into_a_moving_four_stage_ladder() -> None:
    ladder = _ladder("hybrid_structured_events")
    stages = ladder["stages"]  # type: ignore[index]

    assert [s["stage_id"] for s in stages] == [
        "llm_selection",
        "normalize",
        "evidence_projection",
        "clinical_repair",
    ]
    assert ladder["row_count"] == 750

    # No longer a single flat bar: the deterministic stack lifts purist accuracy
    # by a large, real margin over the model's raw selection.
    assert stages[0]["is_baseline"] is True
    assert stages[0]["delta_from_previous"] == 0.0
    assert ladder["final_score"] == stages[-1]["score"] == 0.8893
    assert ladder["final_score"] - stages[0]["score"] > 0.25

    deltas = {s["stage_id"]: s["delta_from_previous"] for s in stages}
    # Evidence projection is the biggest single contributor.
    assert deltas["evidence_projection"] == max(deltas.values())
    assert deltas["evidence_projection"] > 0.1


def test_llm_only_configs_show_a_real_label_repair_contribution() -> None:
    expected_final = {
        "llm_only_canonical_pipeline": 0.7773,
    }
    for run_id, final in expected_final.items():
        ladder = _ladder(run_id)
        stages = ladder["stages"]  # type: ignore[index]
        assert [s["stage_id"] for s in stages] == ["model_label", "label_repair"]
        assert ladder["row_count"] == 750
        assert stages[0]["delta_from_previous"] == 0.0
        # Deterministic label repair turns raw model labels into scorable Gan labels.
        assert stages[1]["delta_from_previous"] > 0.05
        assert ladder["final_score"] == final


def test_provider_seam_baseline_equals_predict_with_downstream_off() -> None:
    spec = _spec("hybrid_structured_events")
    provider = csl.StructuredEventsProvider(spec)
    stage_ids = [stage.stage_id for stage in provider.stages()]

    floor = provider.predict(frozenset(stage_ids[1:]))
    baseline_score = round(csl._accuracy(floor, provider.golds()), 4)

    ladder = _ladder("hybrid_structured_events")
    assert baseline_score == ladder["stages"][0]["score"]  # type: ignore[index]


def test_replay_providers_share_one_750_row_basis() -> None:
    specs = tuple(
        spec
        for spec in csl.DEFAULT_ARCHITECTURE_SPECS
        if spec.kind in {"structured_events", "llm_only"}
    )
    payload = csl.build_component_stage_ladder_payload(specs=specs)

    assert payload["artifact_kind"] == "gan2026_component_stage_ladder_set"
    assert payload["allow_model_calls"] is False
    assert payload["row_inspection_policy"] == "aggregate_only"
    # Apples-to-apples cross-stack comparison requires one identical basis.
    assert {a["row_count"] for a in payload["architectures"]} == {750}
