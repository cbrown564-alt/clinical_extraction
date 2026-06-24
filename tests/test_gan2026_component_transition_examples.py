"""Gan 2026 component transition-examples tests.

These cover the explanatory-only per-note label-trajectory artifact that backs the
Component Impact worked-example sidebar. The contract: it is illustrative only
(never a scoring surface), makes no model calls, selects example notes
deterministically, and reads its rungs through the same provider seam the
aggregate ladder scores — so ``predict_cells`` must project exactly onto
``predict``. Only the fast replay providers (structured-events + LLM-only) are
exercised; the deterministic re-run is covered by its own pipeline.
"""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    component_stage_ladder as csl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    component_transition_examples as cte,
)

_REPLAY_SPECS = tuple(
    spec
    for spec in csl.DEFAULT_ARCHITECTURE_SPECS
    if spec.kind in {"structured_events", "llm_only"}
)


def _spec(run_id: str) -> csl.ArchitectureSpec:
    return next(spec for spec in csl.DEFAULT_ARCHITECTURE_SPECS if spec.run_id == run_id)


def test_predict_cells_frequency_projection_equals_predict() -> None:
    """The refactor invariant: predict() is exactly the cells' monthly frequency."""

    provider = csl.StructuredEventsProvider(_spec("hybrid_structured_events"))
    stage_ids = [stage.stage_id for stage in provider.stages()]
    for index in range(len(stage_ids)):
        disabled = frozenset(stage_ids[index + 1 :])
        cells = provider.predict_cells(disabled)
        assert [cell.monthly_frequency for cell in cells] == provider.predict(disabled)


def test_payload_is_illustrative_only_and_makes_no_model_calls() -> None:
    payload = cte.build_component_transitions_payload(specs=_REPLAY_SPECS)

    assert payload["artifact_kind"] == "gan2026_component_transition_examples"
    assert payload["allow_model_calls"] is False
    assert payload["row_inspection_policy"] == "illustrative_examples_only"
    # The six boundary bands ship with the payload so the sidebar can resolve a
    # tone + short label for each rung without a second request.
    assert {c["id"] for c in payload["categories"]} == {
        band.id for band in csl.BAND_CATEGORIES
    }


def test_each_note_trajectory_matches_its_architecture_stage_order() -> None:
    payload = cte.build_component_transitions_payload(specs=_REPLAY_SPECS)

    by_run = {arch["run_id"]: arch for arch in payload["architectures"]}
    for spec in _REPLAY_SPECS:
        arch = by_run[spec.run_id]
        assert arch["examples"], f"{spec.run_id} should expose worked examples"
        stage_order = [stage.stage_id for stage in spec.stages]
        for example in arch["examples"]:
            assert [s["stage_id"] for s in example["stages"]] == stage_order
            # The baseline is the producer floor; nothing upstream changed it.
            assert example["stages"][0]["is_baseline"] is True
            assert example["stages"][0]["changed"] is False
            # The example's final label/band is its last rung.
            final = example["stages"][-1]
            assert example["final_label"] == final["predicted_label"]
            assert example["final_band"] == final["band"]
            assert example["final_correct"] == final["correct"]


def test_examples_are_chosen_deterministically_by_most_change() -> None:
    payload = cte.build_component_transitions_payload(specs=_REPLAY_SPECS)
    first = cte.build_component_transitions_payload(specs=_REPLAY_SPECS)

    for arch_a, arch_b in zip(payload["architectures"], first["architectures"], strict=True):
        rows_a = [ex["row_id"] for ex in arch_a["examples"]]
        rows_b = [ex["row_id"] for ex in arch_b["examples"]]
        assert rows_a == rows_b  # stable across builds
        # Chosen notes are ranked by band changes (descending) then label changes.
        keys = [
            (ex["band_change_count"], ex["change_count"]) for ex in arch_a["examples"]
        ]
        assert keys == sorted(keys, reverse=True)


def test_llm_only_floor_to_repair_moves_a_real_label() -> None:
    payload = cte.build_component_transitions_payload(
        specs=(_spec("llm_only_canonical_pipeline"),)
    )
    arch = payload["architectures"][0]
    # The most-illustrative LLM-only notes are exactly the ones label repair rescues
    # from an unscorable raw label into the correct band.
    top = arch["examples"][0]
    repair = next(s for s in top["stages"] if s["stage_id"] == "label_repair")
    assert repair["changed"] is True
    assert repair["band_changed"] is True
