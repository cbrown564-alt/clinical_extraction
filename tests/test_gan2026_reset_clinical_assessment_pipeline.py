from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    reset_clinical_assessment_pipeline as pipeline,
)


def test_reset_pipeline_composes_existing_stage_builders(monkeypatch) -> None:
    calls: list[str] = []

    def fake_projection_render(assessment_rows, **kwargs):
        calls.append("projection_render")
        assert assessment_rows == [{"source_row_index": 1}]
        assert kwargs["candidate_sets"] == {1: "candidate-set"}
        return (
            [{"source_row_index": 1, "stage": "projection"}],
            {
                "summary": {
                    "projection_rows": 1,
                    "rendered_label_rows": 1,
                    "null_rendered_label_rows": 0,
                }
            },
        )

    def fake_scoring(project_render_rows, **kwargs):
        calls.append("score")
        assert project_render_rows == [{"source_row_index": 1, "stage": "projection"}]
        assert kwargs["gold_records"] == {1: "gold"}
        return (
            [{"source_row_index": 1, "stage": "score"}],
            {"summary": {"scored_rows": 1, "purist_correct": 1}},
        )

    def fake_route(score_rows, **kwargs):
        calls.append("route")
        assert score_rows == [{"source_row_index": 1, "stage": "score"}]
        return (
            [{"source_row_index": 1, "verification_route": {"routed": True}}],
            {"summary": {"routed_rows": 1}},
        )

    def fake_decision(route_rows, **kwargs):
        calls.append("decision")
        assert route_rows == [{"source_row_index": 1, "verification_route": {"routed": True}}]
        return (
            [{"source_row_index": 1, "verification_decision": {"action": "abstain"}}],
            {"summary": {"decision_rows": 1, "action_counts": {"abstain": 1}}},
        )

    monkeypatch.setattr(
        pipeline.projection_render,
        "build_projection_render_artifact",
        fake_projection_render,
    )
    monkeypatch.setattr(pipeline.projection_score, "build_scoring_artifact", fake_scoring)
    monkeypatch.setattr(
        pipeline.verification_route,
        "build_verification_route_artifact",
        fake_route,
    )
    monkeypatch.setattr(
        pipeline.verification_decision,
        "build_verification_decision_artifact",
        fake_decision,
    )

    artifact = pipeline.build_reset_clinical_assessment_pipeline_artifact(
        assessment_rows=[{"source_row_index": 1}],
        candidate_sets={1: "candidate-set"},
        gold_records={1: "gold"},
        assessment_artifact_path="assessment.jsonl",
        candidate_set_artifact_path="candidate.jsonl",
    )

    assert calls == ["projection_render", "score", "route", "decision"]
    assert artifact.projection_render_rows[0]["stage"] == "projection"
    assert artifact.score_rows[0]["stage"] == "score"
    assert artifact.route_rows[0]["verification_route"]["routed"] is True
    assert artifact.decision_rows[0]["verification_decision"]["action"] == "abstain"
    assert artifact.metadata["summary"] == {
        "input_assessment_rows": 1,
        "projection_rows": 1,
        "rendered_label_rows": 1,
        "null_rendered_label_rows": 0,
        "scored_rows": 1,
        "purist_correct": 1,
        "routed_rows": 1,
        "decision_rows": 1,
        "action_counts": {"abstain": 1},
    }


def test_stage_paths_are_derived_from_output_prefix() -> None:
    paths = pipeline.stage_output_paths_from_prefix("experiments/example_run")

    assert paths.pipeline_json.name == "example_run.json"
    assert paths.pipeline_report.name == "example_run.md"
    assert paths.projection_render_jsonl.name == "example_run.projection_render.jsonl"
    assert paths.score_jsonl.name == "example_run.score.jsonl"
    assert paths.route_jsonl.name == "example_run.route.jsonl"
    assert paths.decision_jsonl.name == "example_run.verification_decision.jsonl"
