from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    seizure_free_duration_node_replay,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
)


def test_duration_node_replay_adds_exact_evidence_month_nodes() -> None:
    record = _record(
        source_row_index=5345,
        note_text=(
            "Seizures: Bill maintains a simple calendar record. He and his key "
            "worker report he has been free of events for several months, with no "
            "witnessed episodes or post-event confusion."
        ),
        gold_label="seizure free for multiple month",
    )
    baseline_graph = ClinicalFrequencyStateGraph(
        source_row_index=5345,
        nodes=(
            _node(
                "sg-001",
                "seizure free for multiple year",
                "free of events for several months",
            ),
        ),
    )

    rows, metadata = seizure_free_duration_node_replay.run_duration_node_replay(
        [record],
        [_projection_row(record, baseline_graph, failure_mode="only_broad_duration_nodes")],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="projection.jsonl",
    )

    row = rows[0]
    assert row["new_duration_node_count"] == 1
    assert row["new_duration_nodes"][0]["normalized_label"] == (
        "seizure free for multiple month"
    )
    assert row["new_duration_nodes"][0]["graph_errors"] == []
    assert row["replayed_exact_gold_duration_node_present"] is True
    assert row["month_scale_representability_gain"] is True
    assert metadata["summary"]["node_coverage"]["month_scale_representability_gains"] == 1
    assert metadata["summary"]["evidence"]["exact_evidence_valid_nodes"] == 1


def test_duration_node_replay_emits_numeric_and_broad_month_equivalents() -> None:
    record = _record(
        source_row_index=5379,
        note_text=(
            "Recent spells have not been epileptic in nature based on description "
            "and collateral, and there have been no witnessed focal impaired-awareness "
            "seizures during this interval. She last had a clearly epileptic focal "
            "event approximately six months ago."
        ),
        gold_label="seizure free for multiple month",
    )
    baseline_graph = ClinicalFrequencyStateGraph(
        source_row_index=5379,
        nodes=(
            _node(
                "sg-001",
                "seizure free for 6 month",
                "last had a clearly epileptic focal event approximately six months ago",
            ),
        ),
    )

    rows, _metadata = seizure_free_duration_node_replay.run_duration_node_replay(
        [record],
        [
            _projection_row(
                record,
                baseline_graph,
                failure_mode="numeric_duration_present_but_gold_absent",
            )
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="projection.jsonl",
    )

    new_labels = {
        node["normalized_label"]
        for node in rows[0]["new_duration_nodes"]
    }
    replayed_labels = {
        item["label"]
        for item in rows[0]["replayed_graph_labels"]
        if item["kind"] == "seizure_free"
    }
    assert new_labels == {"seizure free for multiple month"}
    assert replayed_labels == {
        "seizure free for 6 month",
        "seizure free for multiple month",
    }
    assert rows[0]["replayed_exact_gold_duration_node_present"] is True


def test_duration_node_replay_writes_report(tmp_path: Path) -> None:
    record = _record(
        source_row_index=1,
        note_text="The patient reports no events for many months.",
        gold_label="seizure free for multiple month",
    )
    graph = ClinicalFrequencyStateGraph(
        source_row_index=1,
        nodes=(_node("sg-001", "seizure free for multiple year", "no events for many months"),),
    )
    rows, metadata = seizure_free_duration_node_replay.run_duration_node_replay(
        [record],
        [_projection_row(record, graph, failure_mode="only_broad_duration_nodes")],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="projection.jsonl",
    )

    report_path = tmp_path / "report.md"
    seizure_free_duration_node_replay.write_duration_node_replay_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Seizure-Free Duration Node Replay" in text
    assert "Node Coverage" in text
    assert "unchanged projection" in text


def _projection_row(
    record: GanFrequencyRecord,
    graph: ClinicalFrequencyStateGraph,
    *,
    failure_mode: str,
) -> dict:
    return {
        "source_row_index": record.source_row_index,
        "source": "unit_surface",
        "source_artifact": "projection_arbitration.jsonl",
        "gold_normalized_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "failure_mode": failure_mode,
        "graph": graph.model_dump(mode="json"),
        "variant_results": {
            "baseline_v0": {
                "final_label": "seizure free for multiple year",
                "monthly_frequency": 0.0,
            }
        },
    }


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


def _node(node_id: str, label: str, evidence: str) -> StateGraphNode:
    parsed = label_to_frequency_record(label)
    return StateGraphNode(
        node_id=node_id,
        kind=GraphNodeKind.SEIZURE_FREE,
        normalized_label=parsed.normalized_label,
        semantic_kind=parsed.kind,
        monthly_frequency=parsed.monthly_frequency,
        evidence=EvidenceSpan(text=evidence),
        rule_id="unit.baseline",
    )
