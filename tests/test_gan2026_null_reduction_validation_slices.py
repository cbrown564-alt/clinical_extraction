from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    null_reduction_validation_slices,
)


def test_build_validation_slices_reports_baseline_transitions_and_validity() -> None:
    baseline_score_rows = [
        _score_row(
            source_row_index=101,
            issues=["frequency_rate_values_unparsed"],
            rendered_label=None,
            purist_correct=False,
            pragmatic_correct=False,
            exact_trace=False,
            source_id_status="missing",
        ),
        _score_row(
            source_row_index=102,
            issues=["frequency_rate_values_unparsed"],
            rendered_label="2 per month",
            purist_correct=True,
            pragmatic_correct=True,
        ),
    ]
    baseline_route_rows = [
        _route_row(source_row_index=101, routed=True, route_families=["needs_projection"]),
        _route_row(source_row_index=102, routed=False),
    ]
    current_score_rows = [
        _score_row(
            source_row_index=101,
            issues=["frequency_rate_values_unparsed"],
            rendered_label="3 per 2 month",
            purist_correct=True,
            pragmatic_correct=True,
        ),
        _score_row(
            source_row_index=102,
            issues=["frequency_rate_values_unparsed"],
            rendered_label=None,
            purist_correct=False,
            pragmatic_correct=False,
        ),
        _score_row(
            source_row_index=103,
            issues=["frequency_rate_values_unparsed"],
            rendered_label="1 per month",
            purist_correct=True,
            pragmatic_correct=True,
        ),
    ]
    current_route_rows = [
        _route_row(source_row_index=101, routed=False),
        _route_row(source_row_index=102, routed=True, route_families=["new_gap"]),
        _route_row(source_row_index=103, routed=False),
    ]

    summary = null_reduction_validation_slices.build_validation_slices(
        current_score_rows,
        route_rows=current_route_rows,
        baseline_score_rows=baseline_score_rows,
        baseline_route_rows=baseline_route_rows,
    )

    freq = summary["slices"]["frequency_rate_values_unparsed"]
    assert summary["artifact_kind"] == "gan2026_validation750_null_reduction_slices_v1"
    assert summary["comparison_enabled"] is True
    assert freq["row_count"] == 3
    assert freq["rendered_count"] == 2
    assert freq["null_count"] == 1
    assert freq["routed_count"] == 1
    assert freq["trace_valid_count"] == 3
    assert freq["source_id_valid_count"] == 3
    assert freq["baseline"]["row_count"] == 2
    assert freq["baseline"]["rendered_count"] == 1
    assert freq["baseline"]["null_count"] == 1
    assert freq["baseline"]["routed_count"] == 1
    assert freq["transitions"] == {
        "shared_row_count": 2,
        "baseline_only_row_count": 0,
        "current_only_row_count": 1,
        "newly_rendered_count": 1,
        "newly_null_count": 1,
        "wrong_to_correct_count": 1,
        "correct_to_wrong_count": 1,
        "newly_routed_count": 1,
        "newly_unrouted_count": 1,
    }
    assert [row["source_row_index"] for row in freq["changed_rows"]] == [101, 102]


def test_write_report_includes_transition_section(tmp_path: Path) -> None:
    summary = null_reduction_validation_slices.build_validation_slices(
        [_score_row(source_row_index=201, issues=["vague_count"], rendered_label="multiple per week")],
        route_rows=[_route_row(source_row_index=201, routed=False)],
        baseline_score_rows=[_score_row(source_row_index=201, issues=["vague_count"], rendered_label=None)],
        baseline_route_rows=[_route_row(source_row_index=201, routed=True, route_families=["baseline"])],
    )
    report_path = tmp_path / "report.md"

    null_reduction_validation_slices.write_report(summary, report_path)

    report = report_path.read_text(encoding="utf-8")
    assert "Baseline Comparison" in report
    assert "Wrong-to-correct" in report
    assert "First 15 matching rows" in report


def _score_row(
    *,
    source_row_index: int,
    issues: list[str],
    rendered_label: str | None,
    purist_correct: bool = False,
    pragmatic_correct: bool = False,
    exact_trace: bool = True,
    source_id_status: str = "valid",
) -> dict:
    return {
        "source_row_index": source_row_index,
        "projection_decision": {
            "source_row_index": source_row_index,
            "source_normalized_phrase": f"phrase-{source_row_index}",
            "projection_issues": issues,
            "selected_evidence_status": {
                "exact_trace": exact_trace,
                "source_id_status": source_id_status,
            },
        },
        "final_rendered_label": {"rendered_label": rendered_label},
        "score": {
            "gold_label": f"gold-{source_row_index}",
            "purist_correct": purist_correct,
            "pragmatic_correct": pragmatic_correct,
        },
    }


def _route_row(
    *,
    source_row_index: int,
    routed: bool,
    route_families: list[str] | None = None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "verification_route": {
            "routed": routed,
            "route_families": route_families or [],
        },
    }
