from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    boundary_state_graph_replay,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_accepted_boundary_node_replay_gains_representability_only() -> None:
    record = _record(
        source_row_index=338,
        note_text=(
            "Current diary says many convulsions in past month. "
            "No tonic-clonic seizures for two weeks."
        ),
        gold_label="multiple per month",
    )
    boundary_rows = [
        _boundary_row(
            source_row_index=338,
            gold_label="multiple per month",
            nodes=[
                {
                    "semantic_kind": "unknown",
                    "node_normalized_label": "unknown",
                    "evidence": "many convulsions in past month",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "certainty": "high",
                    "rationale": "Vague frequency evidence exists.",
                },
                {
                    "semantic_kind": "unresolved_multiple",
                    "node_normalized_label": "multiple per month",
                    "evidence": "many convulsions in past month",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "certainty": "high",
                    "rationale": "Multiple events with a month unit.",
                },
            ],
        )
    ]

    rows, metadata = boundary_state_graph_replay.run_accepted_boundary_node_replay(
        [record],
        boundary_rows,
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="boundary.jsonl",
    )

    assert rows[0]["baseline_oracle_representable"] is False
    assert rows[0]["replayed_oracle_representable"] is True
    assert rows[0]["accepted_hosted_node_count"] == 1
    assert rows[0]["accepted_hosted_nodes"][0]["normalized_label"] == "multiple per month"
    assert metadata["summary"]["coverage"]["representability_gains"] == 1
    assert metadata["summary"]["projection"]["changed_from_baseline"] == 0
    assert "Diagnostic graph replay only" in metadata["claim_language"]


def test_accepted_boundary_node_replay_filters_non_gain_and_parse_error_rows() -> None:
    accepted = _boundary_row(
        source_row_index=1317,
        gold_label="unknown",
        nodes=[
            {
                "semantic_kind": "unknown",
                "node_normalized_label": "unknown",
                "evidence": "diagnostic classification not yet determined",
                "temporality": "current",
                "assertion_status": "asserted",
                "certainty": "medium",
                "rationale": "Boundary-state uncertainty.",
            }
        ],
    )
    non_gain = {**accepted, "source_row_index": 1318, "representability_gain_candidate": False}
    parse_error = {**accepted, "source_row_index": 1319, "parse_errors": ["bad"]}
    records = [
        _record(
            source_row_index=1317,
            note_text="Seizures noted; diagnostic classification not yet determined.",
            gold_label="unknown",
        ),
        _record(
            source_row_index=1318,
            note_text="Seizures are discussed.",
            gold_label="unknown",
        ),
        _record(
            source_row_index=1319,
            note_text="Seizures are discussed.",
            gold_label="unknown",
        ),
    ]

    rows, metadata = boundary_state_graph_replay.run_accepted_boundary_node_replay(
        records,
        [parse_error, non_gain, accepted],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="boundary.jsonl",
    )

    assert [row["source_row_index"] for row in rows] == [1317]
    assert metadata["summary"]["coverage"]["accepted_boundary_rows"] == 1


def test_accepted_boundary_node_replay_writes_report(tmp_path) -> None:
    record = _record(
        source_row_index=3507,
        note_text="The current frequency remains unclear after review.",
        gold_label="unknown",
    )
    rows, metadata = boundary_state_graph_replay.run_accepted_boundary_node_replay(
        [record],
        [
            _boundary_row(
                source_row_index=3507,
                gold_label="unknown",
                nodes=[
                    {
                        "semantic_kind": "unknown",
                        "node_normalized_label": "unknown",
                        "evidence": "current frequency remains unclear",
                        "temporality": "current",
                        "assertion_status": "asserted",
                        "certainty": "high",
                        "rationale": "Frequency is explicitly unclear.",
                    }
                ],
            )
        ],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        source_artifact="boundary.jsonl",
    )
    report_path = tmp_path / "report.md"

    boundary_state_graph_replay.write_replay_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Coverage Replay" in text
    assert "Projection Replay" in text
    assert "not a benchmark result" in text


def _boundary_row(
    *,
    source_row_index: int,
    gold_label: str,
    nodes: list[dict[str, str]],
) -> dict:
    parsed = label_to_frequency_record(gold_label)
    return {
        "source_row_index": source_row_index,
        "surface_role": "validation_boundary_missing",
        "parse_errors": [],
        "representability_gain_candidate": True,
        "structured_record": {
            "nodes": nodes,
            "no_reference_vs_unknown_rationale": "The note discusses seizure frequency.",
        },
        "reference": {
            "gold_label": gold_label,
            "gold_normalized_label": parsed.normalized_label,
            "gold_label_kind": parsed.kind.value,
            "row_ok": True,
        },
        "raw_output": json.dumps({"nodes": nodes}),
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
