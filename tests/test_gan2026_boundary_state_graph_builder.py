from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    boundary_state_graph_builder,
)


def test_boundary_state_builder_spec_targets_missing_validation_rows_only() -> None:
    records = [
        _record(
            source_row_index=338,
            note_text="Diary reports several seizures each week but the count is unclear.",
            gold_label="multiple per week",
        ),
        _record(
            source_row_index=5551,
            note_text="Several episodes per day.",
            gold_label="multiple per day",
        ),
    ]

    selected = boundary_state_graph_builder.select_validation_missing_rows(records)

    assert [record.source_row_index for record in selected] == [338]


def test_boundary_state_builder_prompt_forbids_final_label_emission() -> None:
    record = _record(
        source_row_index=338,
        note_text="Diary reports several seizures each week but the count is unclear.",
        gold_label="multiple per week",
    )

    payload = json.loads(
        boundary_state_graph_builder.build_prompt_input(
            record,
            surface_role="validation_boundary_missing",
        )
    )

    assert payload["prompt_version"] == boundary_state_graph_builder.PROMPT_VERSION
    assert payload["allowed_node_semantic_kinds"] == ["unknown", "unresolved_multiple"]
    assert "Do not emit a final Gan label" in payload["instructions"]
    assert "top_level" not in payload["output_schema"]
    assert "top_level" in payload["forbidden_output_keys"]
    assert "seizures continue but frequency is unclear" in payload["unknown_state_examples"]
    assert "final_label" not in payload["output_schema"]["node"].values()


def test_boundary_state_builder_replay_validates_exact_evidence_and_no_final_label() -> None:
    record = _record(
        source_row_index=338,
        note_text="Diary reports several seizures each week but the count is unclear.",
        gold_label="multiple per week",
    )
    raw_output = json.dumps(
        {
            "nodes": [
                {
                    "semantic_kind": "unresolved_multiple",
                    "node_normalized_label": "multiple per week",
                    "evidence": "several seizures each week",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "certainty": "medium",
                    "rationale": "The diary states recurring seizures without exact count.",
                }
            ],
            "no_reference_vs_unknown_rationale": "The note discusses seizures.",
        }
    )

    rows, metadata = boundary_state_graph_builder.run_boundary_state_graph_builder_split(
        [record],
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=700,
        mode="prompt-only",
        reuse_raw_outputs={338: raw_output},
    )

    assert rows[0]["parse_errors"] == []
    assert rows[0]["evidence_summary"]["exact_evidence_valid"] == 1
    assert rows[0]["representability_gain_candidate"] is True
    assert "final_label" not in rows[0]["structured_record"]
    assert metadata["summary"]["schema_valid_rows"] == 1
    assert metadata["summary"]["representability_gain_candidates"] == 1


def test_boundary_state_builder_rejects_final_label_and_inexact_evidence() -> None:
    record = _record(
        source_row_index=1317,
        note_text="Events are mentioned but the current frequency is unclear.",
        gold_label="unknown",
    )
    raw_output = json.dumps(
        {
            "final_label": "unknown",
            "nodes": [
                {
                    "semantic_kind": "unknown",
                    "node_normalized_label": "unknown",
                    "evidence": "frequency cannot be determined",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "certainty": "medium",
                    "rationale": "Paraphrased evidence should fail.",
                }
            ],
        }
    )

    parsed, errors = boundary_state_graph_builder.parse_boundary_state_builder_json(
        raw_output,
        note_text=record.note_text,
    )

    assert parsed is not None
    assert "final_label_emitted" in errors
    assert "node[0].evidence_not_exact" in errors


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
