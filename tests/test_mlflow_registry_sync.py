from __future__ import annotations

from pathlib import Path

from clinical_extraction.core.mlflow_registry_sync import (
    build_registry_mlflow_sync_plan,
    build_run_sync_plan,
    infer_dataset,
    infer_task,
    render_sync_plan,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
)


def test_mlflow_registry_sync_dry_run_keeps_restricted_jsonl_pointer_only(
    tmp_path: Path,
) -> None:
    report = tmp_path / "experiments" / "full200.md"
    rows = tmp_path / "experiments" / "full200.jsonl"
    report.parent.mkdir()
    report.write_text("# Aggregate report\n", encoding="utf-8")
    rows.write_text('{"row": 1}\n', encoding="utf-8")
    entry = RunRegistryEntry(
        run_id="exectv2_same_core_full200_20260625",
        artifact_paths=("experiments/full200.md", "experiments/full200.jsonl"),
        date="2026-06-25",
        pipeline_family="exectv2_llm_only_same_core",
        split="full200_aggregate",
        row_count=200,
        model="deepseek/deepseek-reasoner",
        model_role="extractor",
        mode="replay",
        replay_status="saved_output_replay",
        decision="revise",
        primary_metrics={"clinical_headline_f1": 0.8566, "schema_note": "1 failure"},
        comparison_role="diagnostic",
    )

    plan = build_run_sync_plan(entry, repo_root=tmp_path)

    assert plan.experiment_name == "clinical-extraction/exectv2"
    assert plan.params["dataset"] == "ExECTv2 (2025)"
    assert plan.metrics == {"clinical_headline_f1": 0.8566}
    assert plan.tags["row_inspection_policy"] == "aggregate_only"
    assert plan.tags["restricted_surface"] == "true"
    assert [artifact.action for artifact in plan.artifacts] == [
        "log_artifact",
        "pointer_only",
    ]
    assert "restricted surface" in plan.artifacts[1].reason


def test_mlflow_registry_sync_defaults_unrestricted_jsonl_to_pointer(
    tmp_path: Path,
) -> None:
    report = tmp_path / "experiments" / "validation.md"
    rows = tmp_path / "experiments" / "validation.jsonl"
    report.parent.mkdir()
    report.write_text("# Validation report\n", encoding="utf-8")
    rows.write_text('{"row": 1}\n', encoding="utf-8")
    entry = RunRegistryEntry(
        run_id="gan2026_validation750_llm_only_gpt41mini_20260607",
        artifact_paths=("experiments/validation.md", "experiments/validation.jsonl"),
        date="2026-06-07",
        pipeline_family="llm_only_canonical_pipeline",
        split="validation",
        row_count=750,
        model="openai/gpt-4.1-mini",
        model_role="selector",
        mode="replay",
        replay_status="saved_output_replay",
        decision="revise",
        primary_metrics={"purist_accuracy": 0.8},
    )

    default_plan = build_run_sync_plan(entry, repo_root=tmp_path)
    full_plan = build_run_sync_plan(entry, repo_root=tmp_path, include_large_artifacts=True)

    assert [artifact.action for artifact in default_plan.artifacts] == [
        "log_artifact",
        "pointer_only",
    ]
    assert default_plan.tags["claim_boundary"] == "validation_development"
    assert [artifact.action for artifact in full_plan.artifacts] == [
        "log_artifact",
        "log_artifact",
    ]


def test_registry_mlflow_sync_plan_filters_and_renders(tmp_path: Path) -> None:
    old = RunRegistryEntry(
        run_id="old",
        artifact_paths=("experiments/old.md",),
        date="2026-06-01",
        pipeline_family="analysis",
        split="dev",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
    )
    selected = RunRegistryEntry(
        run_id="exectv2_new",
        artifact_paths=("experiments/new.md",),
        date="2026-06-26",
        pipeline_family="exectv2_reliability",
        split="dev",
        row_count=140,
        model="openai/gpt-4.1-mini",
        model_role="extractor",
        mode="replay",
        replay_status="saved_output_replay",
        decision="revise",
    )
    artifact = tmp_path / "experiments" / "new.md"
    artifact.parent.mkdir()
    artifact.write_text("# New\n", encoding="utf-8")

    plan = build_registry_mlflow_sync_plan(
        [old, selected],
        repo_root=tmp_path,
        since_date="2026-06-25",
    )
    rendered = render_sync_plan(plan)

    assert plan.selected_run_count == 1
    assert plan.runs[0].registry_run_id == "exectv2_new"
    assert "MLflow registry sync dry run" in rendered
    assert "exectv2_new" in rendered
    assert "old" not in rendered


def test_registry_sync_task_and_dataset_inference() -> None:
    exect = RunRegistryEntry(
        run_id="exectv2_example",
        artifact_paths=("experiments/example.md",),
        date="2026-06-26",
        pipeline_family="analysis",
        split="dev",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
    )
    gan = RunRegistryEntry(
        run_id="gan2026_example",
        artifact_paths=("experiments/example.md",),
        date="2026-06-26",
        pipeline_family="analysis",
        split="validation",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
    )

    assert infer_task(exect) == "exectv2"
    assert infer_dataset(exect) == "ExECTv2 (2025)"
    assert infer_task(gan) == "gan2026"
    assert infer_dataset(gan) == "Gan (2026)"
