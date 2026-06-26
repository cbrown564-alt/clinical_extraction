from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.core import mlflow_registry_sync
from clinical_extraction.core.mlflow_registry_sync import (
    BACKFILL_SCOPES,
    build_mlflow_comparison_sync_plan,
    build_registry_mlflow_sync_plan,
    build_run_sync_plan,
    filter_registry_entries,
    infer_dataset,
    infer_task,
    render_comparison_sync_plan,
    render_sync_plan,
    resolve_backfill_filters,
    sync_comparison_plan_to_mlflow,
)
from clinical_extraction.core.mlflow_tracking import MlflowRunPayload
from clinical_extraction.core.registry import (
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


def test_resolve_backfill_filters_uses_paper_facing_defaults() -> None:
    scope, since_date, roles = resolve_backfill_filters(backfill_scope="paper_facing")

    assert scope == BACKFILL_SCOPES["paper_facing"]
    assert since_date == "2026-06-24"
    assert roles == BACKFILL_SCOPES["paper_facing"].registry_roles


def test_filter_registry_entries_matches_any_registry_role() -> None:
    paper = RunRegistryEntry(
        run_id="paper",
        artifact_paths=("experiments/paper.md",),
        date="2026-06-26",
        pipeline_family="analysis",
        split="validation",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
        registry_roles=("component_ladder",),
    )
    diagnostic = RunRegistryEntry(
        run_id="diagnostic",
        artifact_paths=("experiments/diagnostic.md",),
        date="2026-06-26",
        pipeline_family="analysis",
        split="validation",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
        registry_roles=("negative_attribution",),
    )

    selected = filter_registry_entries(
        [paper, diagnostic],
        registry_roles=BACKFILL_SCOPES["paper_facing"].registry_roles,
    )

    assert [entry.run_id for entry in selected] == ["paper"]


def test_registry_mlflow_sync_plan_backfill_scope_renders_metadata(tmp_path: Path) -> None:
    artifact = tmp_path / "experiments" / "paper.md"
    artifact.parent.mkdir()
    artifact.write_text("# Paper\n", encoding="utf-8")
    entry = RunRegistryEntry(
        run_id="gan2026_gate",
        artifact_paths=("experiments/paper.md",),
        date="2026-06-26",
        pipeline_family="analysis",
        split="validation",
        row_count=0,
        model="none",
        model_role="analysis",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
        registry_roles=("component_ladder",),
    )

    plan = build_registry_mlflow_sync_plan(
        [entry],
        repo_root=tmp_path,
        backfill_scope="paper_facing",
    )
    rendered = render_sync_plan(plan)

    assert plan.backfill_scope == "paper_facing"
    assert plan.since_date == "2026-06-24"
    assert "component_ladder" in plan.registry_roles
    assert "Backfill scope: paper_facing" in rendered


def test_comparison_sync_plan_groups_same_core_children(tmp_path: Path) -> None:
    parent_report = tmp_path / "docs" / "same_core.md"
    child_report = tmp_path / "experiments" / "child.md"
    child_rows = tmp_path / "experiments" / "child.jsonl"
    parent_report.parent.mkdir(parents=True)
    child_report.parent.mkdir(parents=True)
    parent_report.write_text("# Same core\n", encoding="utf-8")
    child_report.write_text("# Child\n", encoding="utf-8")
    child_rows.write_text('{"row": 1}\n', encoding="utf-8")
    gpt = _same_core_entry(
        "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
        model="openai/gpt-4.1-mini",
        clinical_headline_f1=0.8396,
        call_failures=0,
        parse_schema_failures=0,
    )
    qwen_repair = _same_core_entry(
        "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140",
        model="ollama_chat/qwen3.6:35b",
        clinical_headline_f1=None,
        call_failures=0,
        parse_schema_failures=0,
        decision="reject",
    )

    plan = build_mlflow_comparison_sync_plan(
        [qwen_repair, gpt],
        repo_root=tmp_path,
        comparison_id="exectv2_same_core_model_swap_dev140_20260625",
        child_run_ids=(gpt.run_id, qwen_repair.run_id),
        parent_artifact_paths=("docs/same_core.md",),
    )
    rendered = render_comparison_sync_plan(plan)

    assert plan.parent_tags["same_core_comparison"] == "true"
    assert plan.parent_tags["claim_boundary"] == "dev_only"
    assert plan.parent_tags["row_inspection_policy"] == "allowed"
    assert plan.parent_metrics["best_clinical_headline_f1"] == 0.8396
    assert plan.parent_metrics["child_run_count"] == 2.0
    assert plan.child_runs[0].registry_run_id == gpt.run_id
    assert plan.child_runs[1].registry_run_id == qwen_repair.run_id
    assert plan.child_runs[0].artifacts[0].action == "log_artifact"
    assert plan.child_runs[0].artifacts[1].action == "pointer_only"
    assert "child exectv2_2call_no_sf_adjudicator_gpt41mini_dev140" in rendered


def test_comparison_sync_creates_parent_then_children(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report = tmp_path / "docs" / "same_core.md"
    child_report = tmp_path / "experiments" / "child.md"
    report.parent.mkdir(parents=True)
    child_report.parent.mkdir(parents=True)
    report.write_text("# Same core\n", encoding="utf-8")
    child_report.write_text("# Child\n", encoding="utf-8")
    first = _same_core_entry(
        "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
        model="openai/gpt-4.1-mini",
        clinical_headline_f1=0.8396,
    )
    second = _same_core_entry(
        "exectv2_2call_no_sf_adjudicator_deepseek_dev140",
        model="deepseek/deepseek-chat",
        clinical_headline_f1=0.8596,
    )
    plan = build_mlflow_comparison_sync_plan(
        [first, second],
        repo_root=tmp_path,
        comparison_id="comparison",
        child_run_ids=(first.run_id, second.run_id),
        parent_artifact_paths=("docs/same_core.md",),
    )
    calls: list[MlflowRunPayload] = []

    def fake_mirror(payload: MlflowRunPayload, *, repo_root: Path | None = None) -> str:
        calls.append(payload)
        return "parent-id" if payload.parent_run_id is None else f"child-{len(calls) - 1}"

    monkeypatch.setattr(mlflow_registry_sync, "mirror_payload_to_mlflow", fake_mirror)

    result = sync_comparison_plan_to_mlflow(plan, repo_root=tmp_path)

    assert result.parent_run_id == "parent-id"
    assert result.mirrored_run_ids == {
        first.run_id: "child-1",
        second.run_id: "child-2",
    }
    assert calls[0].run_name == "comparison"
    assert calls[1].parent_run_id == "parent-id"
    assert calls[2].parent_run_id == "parent-id"


def _same_core_entry(
    run_id: str,
    *,
    model: str,
    clinical_headline_f1: float | None,
    call_failures: int = 0,
    parse_schema_failures: int = 0,
    decision: str = "revise",
) -> RunRegistryEntry:
    metrics: dict[str, float | int] = {
        "call_failures": call_failures,
        "parse_schema_failures": parse_schema_failures,
    }
    if clinical_headline_f1 is not None:
        metrics["clinical_headline_f1"] = clinical_headline_f1
    return RunRegistryEntry(
        run_id=run_id,
        artifact_paths=("experiments/child.md", "experiments/child.jsonl"),
        date="2026-06-25",
        pipeline_family="exectv2_same_core_model_swap",
        split="dev",
        row_count=140,
        model=model,
        model_role="same-core model-swap extractor",
        mode="live",
        replay_status="saved_output_replay",
        decision=decision,
        primary_metrics=metrics,
        evidence_validity="exact evidence summarized in report",
        architecture_family="llm_only",
        comparison_role="diagnostic",
    )
