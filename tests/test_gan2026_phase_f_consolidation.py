from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    boundary_diagnostic,
    candidate_state_matrix,
    get_phase_f_analyzer_registry,
    phase_f_completion_summary,
    projection_scoring,
    scoped_ablation_analyzer,
)


def test_phase_f_registry_names_cluster_level_analyzers() -> None:
    registry = get_phase_f_analyzer_registry()

    assert set(registry) == {
        "ablation",
        "boundary_seizure_free",
        "candidate_state",
        "projection_render_scoring",
    }
    assert registry["ablation"].module == "scoped_ablation_analyzer"
    assert registry["boundary_seizure_free"].module == "boundary_diagnostic"
    assert registry["candidate_state"].module == "candidate_state_matrix"
    assert registry["projection_render_scoring"].module == "projection_scoring"

    summary = phase_f_completion_summary()
    assert summary["phase"] == "F"
    assert summary["consolidated_analyzer_modules"] == 4
    assert summary["survey_cluster_files_replaced"] == 32
    assert summary["claim_boundary"] == "cluster-level analysis API; no scoring-policy change"


def test_consolidated_analyzers_emit_phase_f_metadata(tmp_path: Path) -> None:
    ablation = scoped_ablation_analyzer.ScopedAblationAnalyzer(
        name="unit_scope",
        description="Unit scoped ablation",
        variants=[
            scoped_ablation_analyzer.AblationVariant(
                name="baseline",
                description="Baseline",
                run_fn=lambda row: (row["baseline_label"], row["baseline_frequency"]),
            )
        ],
    )
    rows, ablation_metadata = ablation.run_ablation(
        [
            {
                "source_row_index": 1,
                "gold_label": "1 per month",
                "gold_frequency": 1.0,
                "baseline_label": "1 per month",
                "baseline_frequency": 1.0,
            }
        ],
        split="validation",
        split_manifest="gan2026_split_v1",
        gold_frequency_extractor=lambda row: row["gold_frequency"],
        gold_label_extractor=lambda row: row["gold_label"],
    )

    assert rows[0]["variant_results"]["baseline"]["correct"] is True
    assert ablation_metadata["phase_f_consolidated"] is True
    assert ablation_metadata["analyzer_cluster"] == "ablation"

    boundary = boundary_diagnostic.BoundaryDiagnosticAnalyzer(
        name="boundary_scope",
        description="Boundary scope",
    ).run_diagnostic(
        [
            {
                "source_row_index": 2,
                "semantic_kind": "seizure_free",
                "normalized_label": "seizure free for 3 month",
                "boundary_matched": True,
            }
        ],
        diagnostic_family="seizure_free_duration",
    )
    assert boundary["phase_f_consolidated"] is True
    assert boundary["analyzer_cluster"] == "boundary_seizure_free"

    candidate = candidate_state_matrix.CandidateStateMatrixAnalyzer(
        name="candidate_scope",
        description="Candidate scope",
    ).compare_candidate_sets(
        [{"source_row_index": 3, "candidates": [{"label": "1 per month"}]}],
        [{"source_row_index": 3, "candidates": [{"label": "1 per month"}]}],
    )
    assert candidate["phase_f_consolidated"] is True
    assert candidate["summary"]["exact_candidate_set_matches"] == 1

    projection = projection_scoring.ProjectionScoringAnalyzer(
        name="projection_scope",
        description="Projection scope",
    ).analyze_pipeline_stages(
        projection_rows=[{"source_row_index": 4}],
        score_rows=[{"comparison": {"purist_correct": True}}],
        route_rows=[{"verification_route": {"routed": True}}],
        decision_rows=[{"verification_decision": {"action": "abstain"}}],
    )
    assert projection["phase_f_consolidated"] is True
    assert projection["summary"]["purist_accuracy"] == 1.0

    report_path = tmp_path / "projection.md"
    projection_scoring.ProjectionScoringAnalyzer(
        name="projection_scope",
        description="Projection scope",
    ).write_summary_report(projection, report_path)
    assert "Projection & Scoring Analysis" in report_path.read_text(encoding="utf-8")
