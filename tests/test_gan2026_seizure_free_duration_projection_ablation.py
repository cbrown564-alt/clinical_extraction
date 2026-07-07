from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    seizure_free_duration_projection_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
)


def test_seizure_free_duration_ablation_compares_duration_policies() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=1,
        nodes=(
            _node("sg-001", "1 per week", GraphNodeKind.FREQUENCY_RATE),
            _node("sg-002", "seizure free for 6 month", GraphNodeKind.SEIZURE_FREE),
            _node("sg-003", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = seizure_free_duration_projection_ablation.run_seizure_free_duration_ablation(
        [
            {
                "source_row_index": 1,
                "source": "unit_surface",
                "source_artifact": "unit.jsonl",
                "gold_normalized_label": "seizure free for 6 month",
                "gold_label_kind": "seizure_free",
                "gold_monthly_frequency": 0.0,
                "graph": graph.model_dump(mode="json"),
                "baseline_projection_label": "1 per week",
                "failure_family": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    variant_results = rows[0]["variant_results"]
    assert variant_results["baseline_v0"]["final_label"] == "1 per week"
    assert variant_results["longest_seizure_free_duration"]["final_label"] == (
        "seizure free for multiple year"
    )
    assert variant_results["numeric_duration_priority"]["final_label"] == (
        "seizure free for 6 month"
    )
    assert variant_results["oracle_exact_seizure_free_node"]["correct"] is True
    assert metadata["summary"]["variants"]["numeric_duration_priority"]["exact_matches"] == 1
    assert metadata["summary"]["failure_modes"]["non_seizure_free_selected"] == 1


def test_seizure_free_duration_ablation_writes_report(tmp_path: Path) -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=2,
        nodes=(
            _node("sg-001", "seizure free for 4 month", GraphNodeKind.SEIZURE_FREE),
            _node("sg-002", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
        ),
    )
    rows, metadata = seizure_free_duration_projection_ablation.run_seizure_free_duration_ablation(
        [
            {
                "source_row_index": 2,
                "source": "unit_surface",
                "source_artifact": "unit.jsonl",
                "gold_normalized_label": "seizure free for multiple month",
                "gold_label_kind": "seizure_free",
                "gold_monthly_frequency": 0.0,
                "graph": graph.model_dump(mode="json"),
                "baseline_projection_label": "seizure free for multiple year",
                "failure_family": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    report_path = tmp_path / "report.md"
    seizure_free_duration_projection_ablation.write_duration_ablation_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Seizure-Free Duration Projection Ablation" in text
    assert "Scorer-Equivalent Duration Labels" in text


def test_seizure_free_duration_ablation_replays_named_graph_field() -> None:
    baseline_graph = ClinicalFrequencyStateGraph(
        source_row_index=3,
        nodes=(_node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),),
    )
    replayed_graph = ClinicalFrequencyStateGraph(
        source_row_index=3,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node("duration-sg-002", "seizure free for multiple month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = seizure_free_duration_projection_ablation.run_seizure_free_duration_ablation(
        [
            {
                "source_row_index": 3,
                "split": "validation_hard_slices",
                "source_artifact": "node_replay.jsonl",
                "gold_normalized_label": "seizure free for multiple month",
                "gold_label_kind": "seizure_free",
                "gold_monthly_frequency": 0.0,
                "baseline_graph": baseline_graph.model_dump(mode="json"),
                "replayed_graph": replayed_graph.model_dump(mode="json"),
                "replayed_projection": {"final_label": "seizure free for multiple year"},
                "source_failure_mode": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        graph_key="replayed_graph",
        source_artifact_override="node_replay.jsonl",
    )

    assert metadata["graph_key"] == "replayed_graph"
    assert rows[0]["source"] == "validation_hard_slices"
    assert rows[0]["source_artifact"] == "node_replay.jsonl"
    assert rows[0]["baseline_projection_label"] == "seizure free for multiple year"
    assert rows[0]["exact_gold_seizure_free_node_present"] is True
    assert rows[0]["variant_results"]["oracle_exact_seizure_free_node"]["correct"] is True
    assert metadata["summary"]["variants"]["oracle_exact_seizure_free_node"]["exact_matches"] == 1


def test_month_bucket_duration_policy_prefers_broad_month_over_numeric_conflict() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=4,
        nodes=(
            _node("sg-001", "seizure free for 3 month", GraphNodeKind.SEIZURE_FREE),
            _node("sg-002", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node("duration-sg-003", "seizure free for multiple month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = seizure_free_duration_projection_ablation.run_seizure_free_duration_ablation(
        [
            {
                "source_row_index": 4,
                "source": "unit_surface",
                "source_artifact": "unit.jsonl",
                "gold_normalized_label": "seizure free for multiple month",
                "gold_label_kind": "seizure_free",
                "gold_monthly_frequency": 0.0,
                "graph": graph.model_dump(mode="json"),
                "baseline_projection_label": "seizure free for multiple year",
                "failure_family": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    assert rows[0]["variant_results"]["month_bucket_duration_selection"]["final_label"] == (
        "seizure free for multiple month"
    )
    assert metadata["summary"]["variants"]["month_bucket_duration_selection"]["exact_matches"] == 1


def test_month_bucket_duration_policy_preserves_plural_numeric_month_surface() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=5,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node("duration-sg-002", "seizure free for 6 month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = seizure_free_duration_projection_ablation.run_seizure_free_duration_ablation(
        [
            {
                "source_row_index": 5,
                "source": "unit_surface",
                "source_artifact": "unit.jsonl",
                "gold_normalized_label": "seizure free for 6 months",
                "gold_label_kind": "seizure_free",
                "gold_monthly_frequency": 0.0,
                "graph": graph.model_dump(mode="json"),
                "baseline_projection_label": "seizure free for multiple year",
                "failure_family": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    result = rows[0]["variant_results"]["month_bucket_duration_selection"]
    assert result["final_label"] == "seizure free for 6 months"
    assert result["projection_policy"] == (
        "gan2026_state_graph_projection_ablation_month_bucket_duration_selection"
    )
    assert metadata["summary"]["variants"]["month_bucket_duration_selection"]["exact_matches"] == 1


def _node(
    node_id: str,
    label: str,
    kind: GraphNodeKind,
) -> StateGraphNode:
    parsed = label_to_frequency_record(label)
    return StateGraphNode(
        node_id=node_id,
        kind=kind,
        normalized_label=parsed.normalized_label,
        semantic_kind=parsed.kind,
        monthly_frequency=parsed.monthly_frequency,
        evidence=EvidenceSpan(text=label),
    )
