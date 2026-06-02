from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    projection_arbitration_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
    build_state_graph,
)


def test_projection_arbitration_ablation_compares_named_variants() -> None:
    record = _record(
        source_row_index=1,
        note_text=(
            "Current diary says two focal seizures per month. "
            "Frequency later described as unclear after medication review."
        ),
        gold_label="unknown",
    )
    graph = _graph_with_frequency_and_unknown(record.source_row_index)
    row = {
        "source_row_index": record.source_row_index,
        "source": "unit_surface",
        "source_artifact": "unit.jsonl",
        "gold_normalized_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "graph": graph.model_dump(mode="json"),
        "baseline_projection_label": "2 per month",
        "failure_family": "unknown_arbitration",
    }

    rows, metadata = projection_arbitration_ablation.run_projection_arbitration_ablation(
        [row],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    variant_results = rows[0]["variant_results"]
    assert variant_results["baseline_v0"]["final_label"] == "2 per month"
    assert variant_results["boundary_state_priority"]["final_label"] == "unknown"
    assert variant_results["oracle_gold_node"]["correct"] is True
    assert metadata["summary"]["variants"]["boundary_state_priority"]["exact_matches"] == 1
    assert metadata["summary"]["variants"]["baseline_v0"]["exact_matches"] == 0


def test_projection_arbitration_ablation_writes_report(tmp_path) -> None:
    record = _record(
        source_row_index=2,
        note_text="No seizures for twelve months. A history section says one seizure per week.",
        gold_label="seizure free for 12 month",
    )
    graph = build_state_graph(record.note_text, source_row_index=record.source_row_index)
    rows, metadata = projection_arbitration_ablation.run_projection_arbitration_ablation(
        [
            {
                "source_row_index": record.source_row_index,
                "source": "unit_surface",
                "source_artifact": "unit.jsonl",
                "gold_normalized_label": record.gold_normalized_label,
                "gold_label_kind": record.gold_label_kind.value,
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "graph": graph.model_dump(mode="json"),
                "baseline_projection_label": "1 per week",
                "failure_family": "seizure_free_arbitration",
            }
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )

    report_path = tmp_path / "report.md"
    projection_arbitration_ablation.write_ablation_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Projection Variants" in text
    assert "Diagnostic only" in text


def _record(
    *,
    source_row_index: int,
    note_text: str,
    gold_label: str,
) -> GanFrequencyRecord:
    parsed = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=parsed.normalized_label,
        gold_label_kind=parsed.kind,
        gold_yearly_bounds=parsed.yearly_bounds,
        gold_monthly_frequency=parsed.monthly_frequency,
    )


def _graph_with_frequency_and_unknown(source_row_index: int) -> ClinicalFrequencyStateGraph:
    return ClinicalFrequencyStateGraph(
        source_row_index=source_row_index,
        nodes=(
            StateGraphNode(
                node_id="sg-001",
                kind=GraphNodeKind.FREQUENCY_RATE,
                normalized_label="2 per month",
                semantic_kind=label_to_frequency_record("2 per month").kind,
                monthly_frequency=2.0,
                evidence=EvidenceSpan(text="two focal seizures per month"),
            ),
            StateGraphNode(
                node_id="sg-002",
                kind=GraphNodeKind.UNKNOWN_FREQUENCY,
                normalized_label="unknown",
                semantic_kind=label_to_frequency_record("unknown").kind,
                monthly_frequency=1000.0,
                evidence=EvidenceSpan(text="frequency later described as unclear"),
            ),
        ),
    )
