from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    hidden_family_atlas,
)


def test_classify_hidden_families_tags_overlapping_clinical_axes() -> None:
    families = hidden_family_atlas.classify_hidden_families(
        note_text=(
            "Currently seizure-free since March, but diary entries describe "
            "clusters of focal auras every other week historically."
        ),
        gold_label="unknown",
        predicted_label="seizure free for multiple month",
    )

    assert "unknown_boundary" in families
    assert "seizure_free_duration" in families
    assert "cluster_burden" in families
    assert "diary_or_log_aggregation" in families
    assert "current_vs_historical" in families
    assert "benchmark_format_convention" in families


def test_classify_first_failure_for_decision0007_prefers_operand_exposure() -> None:
    owner, reason = hidden_family_atlas.classify_first_failure(
        {
            "component_status": {
                "evidence_exactness": "ok",
                "selected_fact_trace": "ok",
                "selected_operand_completeness": "fail",
            },
            "score_layers": {
                "raw_model_clinical_selection": {"purist_correct": True},
                "mechanical_adapter_label": {"purist_correct": False},
                "final_projected_label": {"purist_correct": False},
            },
        },
        layer_name="final_projected_label",
    )

    assert owner == "operand_exposure"
    assert "complete adapter operands" in reason


def test_classify_first_failure_for_hybrid_uses_candidate_recall_ceiling() -> None:
    owner, reason = hidden_family_atlas.classify_first_failure(
        {
            "diagnostics": {
                "deterministic_correct": False,
                "oracle_candidate_presence": False,
                "oracle_graph_representability": False,
            },
            "score_layers": {
                "hybrid_adjudicator_with_adapters": {"purist_correct": False},
            },
        },
        layer_name="hybrid_adjudicator_with_adapters",
    )

    assert owner == "candidate_generation"
    assert "absent from candidate set" in reason


def test_summarize_atlas_rows_counts_family_owner_pairs() -> None:
    summary = hidden_family_atlas.summarize_atlas_rows(
        [
            {
                "artifact_name": "a.jsonl",
                "primary_layer": "final_projected_label",
                "purist_correct": False,
                "pragmatic_correct": False,
                "hidden_families": "unknown_boundary;seizure_free_duration",
                "first_failure_owner": "llm_clinical_selection",
            },
            {
                "artifact_name": "a.jsonl",
                "primary_layer": "final_projected_label",
                "purist_correct": True,
                "pragmatic_correct": True,
                "hidden_families": "rate_bucket_or_denominator",
                "first_failure_owner": "none",
            },
        ]
    )

    assert summary["row_count"] == 2
    assert summary["incorrect_count"] == 1
    assert summary["first_failure_owners"] == {"llm_clinical_selection": 1}
    assert summary["family_by_first_failure"]["unknown_boundary"] == {
        "llm_clinical_selection": 1
    }


def test_build_atlas_hard_slice_manifest_fixes_candidate_and_projection_slices() -> None:
    manifest = hidden_family_atlas.build_atlas_hard_slice_manifest(
        [
            {
                "artifact_name": "hybrid.jsonl",
                "source_row_index": "10",
                "split": "validation",
                "primary_layer": "hybrid_adjudicator_with_adapters",
                "gold_label": "unknown",
                "predicted_label": "seizure free for multiple year",
                "purist_correct": "False",
                "hidden_families": "unknown_boundary;seizure_free_duration",
                "first_failure_owner": "candidate_generation",
                "first_failure_reason": "gold state absent from candidate set",
                "evidence_exact": "True",
                "deterministic_correct": "False",
                "oracle_candidate_presence": "False",
                "oracle_graph_representability": "False",
            },
            {
                "artifact_name": "hybrid.jsonl",
                "source_row_index": "20",
                "split": "validation",
                "primary_layer": "hybrid_adjudicator_with_adapters",
                "gold_label": "unknown",
                "predicted_label": "seizure free for multiple year",
                "purist_correct": "False",
                "hidden_families": "unknown_boundary;current_vs_historical",
                "first_failure_owner": "projection",
                "first_failure_reason": "gold appears representable but projection is wrong",
                "evidence_exact": "True",
                "deterministic_correct": "False",
                "oracle_candidate_presence": "True",
                "oracle_graph_representability": "True",
            },
            {
                "artifact_name": "hybrid.jsonl",
                "source_row_index": "30",
                "split": "validation",
                "primary_layer": "hybrid_adjudicator_with_adapters",
                "gold_label": "1 per month",
                "predicted_label": "1 per month",
                "purist_correct": "True",
                "hidden_families": "rate_bucket_or_denominator",
                "first_failure_owner": "none",
            },
        ],
        source_atlas_csv="atlas.csv",
    )

    slices = {slice_["slice_name"]: slice_ for slice_ in manifest["slices"]}

    assert slices["candidate_generation_rescue"]["row_count"] == 1
    assert slices["candidate_generation_rescue"]["members"][0]["source_row_index"] == 10
    assert (
        slices["candidate_generation_unknown_seizure_free_boundary"]["members"][0][
            "oracle_candidate_presence"
        ]
        is False
    )
    assert slices["projection_arbitration"]["row_count"] == 1
    assert slices["projection_unknown_seizure_free_arbitration"]["row_count"] == 1
    assert manifest["source_atlas_csv"] == "atlas.csv"
