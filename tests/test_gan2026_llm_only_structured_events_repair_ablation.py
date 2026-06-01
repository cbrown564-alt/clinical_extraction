import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    llm_only_structured_events_repair_ablation as repair_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind

repair_ablation_ladder = repair_ablation.repair_ablation_ladder
run_repair_ablation = repair_ablation.run_repair_ablation


def _record(source_row_index: int) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _raw_structured() -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two seizures per month",
                    "applies_to": "seizures",
                    "time_window": "present",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "two seizures per month",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 per months",
                "evidence": "two seizures per month",
                "confidence": "high",
                "rationale": "The note states the present seizure frequency.",
            },
        }
    )


def test_repair_ablation_ladder_matches_audit_condition_order() -> None:
    assert [name for name, _ in repair_ablation_ladder()] == [
        "A_raw_llm_final_label_only",
        "B_format_preserving_basic_label_repair",
        "C_full_basic_gan_label_repair",
        "D_selected_evidence_repair",
        "E_monthly_diary_arithmetic",
        "F_usual_interval_override",
        "G_breakthrough_after_seizure_free",
        "H_non_epileptic_override",
        "I_residual_jerk_date_anchor",
        "J_post_change_burst",
        "K_dated_sequence",
        "L_elapsed_anchor",
        "M_full_current_stack",
    ]


def test_run_repair_ablation_filters_to_rows_with_saved_raw_outputs(tmp_path: Path) -> None:
    reuse_jsonl = tmp_path / "prior.jsonl"
    reuse_jsonl.write_text(
        json.dumps({"source_row_index": 10, "raw_output": _raw_structured()}) + "\n",
        encoding="utf-8",
    )

    result = run_repair_ablation(
        [_record(10), _record(11)],
        split="validation",
        split_manifest="gan2026_split_v1",
        reuse_jsonl=reuse_jsonl,
    )

    raw_summary = result["conditions"][0]["summary"]
    basic_summary = result["conditions"][1]["summary"]
    full_basic_summary = result["conditions"][2]["summary"]
    assert result["conditions"][0]["repair_mode"] == "raw_model"
    assert result["conditions"][1]["repair_mode"] == "strict_format"
    assert raw_summary["rows"] == 1
    assert raw_summary["exact_label_accuracy"] == 0.0
    assert basic_summary["rows"] == 1
    assert basic_summary["exact_label_accuracy"] == 1.0
    assert full_basic_summary["exact_label_accuracy"] == 1.0
