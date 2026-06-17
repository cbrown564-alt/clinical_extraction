"""Tests for the GPT-first ExECTv2 architecture-loop status report."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    architecture_loop_status as status_report,
)


def _record(
    run_id: str,
    family: str,
    *,
    row_count: int = 140,
    metrics: dict | None = None,
    model_role: str = "",
) -> dict:
    return {
        "run_id": run_id,
        "pipeline_family": family,
        "split": "dev",
        "row_count": row_count,
        "model": "openai/gpt-4.1-mini",
        "model_role": model_role,
        "evidence_validity": "evidence_is_substring",
        "primary_metrics": metrics or {},
        "artifact_paths": [f"experiments/{run_id}.jsonl", f"experiments/{run_id}.md"],
    }


def test_record_scope_distinguishes_all9_from_sf_only() -> None:
    all9 = _record(
        "all9",
        "exectv2_llm_only_all_entities",
        metrics={"semantic_per_item_f1": 0.1, "benchmark_per_item_f1": 0.0},
    )
    sf = _record(
        "sf",
        "exectv2_hybrid",
        metrics={"sf_semantic_per_item_f1": 0.3, "sf_benchmark_per_item_f1": 0.2},
    )

    assert status_report.record_scope(all9) == "all9"
    assert status_report.record_scope(sf) == "sf_only"


def test_build_track_statuses_keeps_evidence_but_flags_strategy_gaps() -> None:
    records = [
        _record(
            "llm_all9_single",
            "exectv2_llm_only_all_entities",
            metrics={
                "semantic_per_item_f1": 0.087,
                "semantic_per_letter_f1": 0.236,
                "benchmark_per_item_f1": 0.0,
                "benchmark_per_letter_f1": 0.0,
                "call_failures": 0,
                "parse_failures": 0,
                "evidence_validity_rate": 0.94,
            },
            model_role="all-entity single-pass extractor",
        ),
        _record(
            "hybrid_sf",
            "exectv2_hybrid",
            metrics={
                "sf_semantic_per_item_f1": 0.327,
                "sf_semantic_per_letter_f1": 0.578,
                "sf_benchmark_per_item_f1": 0.327,
                "sf_benchmark_per_letter_f1": 0.578,
                "mentions_routed": 37,
            },
            model_role="SeizureFrequency only",
        ),
    ]

    statuses = status_report.build_track_statuses(records, model="openai/gpt-4.1-mini")
    by_track = {status.track: status for status in statuses}

    assert by_track["rules_only"].status == "missing_required_run"
    assert by_track["llm_only"].status == "shape_gap"
    assert by_track["llm_only"].best_run_id == "llm_all9_single"
    assert by_track["hybrid"].status == "scope_gap"
    assert by_track["hybrid"].best_run_id == "hybrid_sf"


def test_render_status_markdown_blocks_freeze_when_tracks_or_targets_missing() -> None:
    statuses = [
        status_report.TrackStatus(
            track="rules_only",
            required_shape="deterministic all-9 baseline",
            status="missing_required_run",
            next_action="implement deterministic all-9 baseline",
        ),
        status_report.TrackStatus(
            track="llm_only",
            required_shape="GPT per-entity all-9 structured mention frames",
            status="satisfied",
            next_action="freeze candidate if ablations pass",
            best_run_id="llm_per_entity_all9",
            scope="all9",
            row_count=140,
            semantic_per_item_f1=0.88,
            semantic_per_letter_f1=0.91,
            benchmark_per_item_f1=0.88,
            benchmark_per_letter_f1=0.91,
        ),
        status_report.TrackStatus(
            track="hybrid",
            required_shape="GPT all-9 candidate assessment",
            status="satisfied",
            next_action="freeze candidate if ablations pass",
            best_run_id="hybrid_all9",
            scope="all9",
            row_count=140,
            semantic_per_item_f1=0.9,
            semantic_per_letter_f1=0.92,
            benchmark_per_item_f1=0.9,
            benchmark_per_letter_f1=0.92,
        ),
    ]

    md = status_report.render_status_markdown(statuses, generated_on="2026-06-17")

    assert "Architecture freeze readiness: `not ready`" in md
    assert f"{status_report.FREEZE_TARGET_PER_ITEM:.2f}" in md
    assert f"{status_report.FREEZE_TARGET_PER_LETTER:.2f}" in md
    assert "missing_required_run" in md
    assert "implement deterministic all-9 baseline" in md


def test_write_status_report_reads_jsonl_registry(tmp_path: Path) -> None:
    registry = tmp_path / "registry.jsonl"
    registry.write_text(
        json.dumps(
            _record(
                "llm_all9_single",
                "exectv2_llm_only_all_entities",
                metrics={"semantic_per_item_f1": 0.1, "semantic_per_letter_f1": 0.2},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "status.md"

    status_report.write_status_report(out, registry_path=registry, generated_on="2026-06-17")

    text = out.read_text(encoding="utf-8")
    assert "llm_all9_single" in text
    assert "Architecture freeze readiness" in text
