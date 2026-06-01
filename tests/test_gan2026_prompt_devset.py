import csv
import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.ablation_analysis import (
    CHANGED_ROW_FIELDNAMES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import FrequencyLabelKind
from clinical_extraction.tasks.seizure_frequency.gan2026.prompt_devset import (
    AblationChangedRow,
    build_development_examples,
    load_changed_rows,
    select_development_rows,
    summarize_selection,
    write_jsonl,
)


def _changed_row(
    *,
    condition: str,
    source_row_index: int,
    baseline_correct: bool,
    ablated_correct: bool,
    baseline_error_type: str = "wrong_frequency_bucket",
    ablated_error_type: str = "correct",
    gold_category: str = "seizure_freq_more1mon_less1week",
) -> AblationChangedRow:
    return AblationChangedRow(
        condition=condition,
        source_row_index=source_row_index,
        baseline_correct=baseline_correct,
        ablated_correct=ablated_correct,
        baseline_prediction_label="1 per day",
        ablated_prediction_label="2 per month",
        gold_label="2 per month",
        baseline_prediction_category="seizure_freq_1ormore_daily",
        ablated_prediction_category=gold_category,
        gold_category=gold_category,
        baseline_error_type=baseline_error_type,
        ablated_error_type=ablated_error_type,
        baseline_selected_evidence_type="clinical_evidence",
        ablated_selected_evidence_type="clinical_evidence",
    )


def test_load_changed_rows_parses_booleans_and_source_indices(tmp_path: Path) -> None:
    path = tmp_path / "changed.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHANGED_ROW_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerow(
            {
                "condition": "disable_temporal_selection",
                "source_row_index": "123",
                "baseline_correct": "False",
                "ablated_correct": "True",
                "baseline_prediction_label": "1 per day",
                "ablated_prediction_label": "unknown",
                "gold_label": "unknown",
                "baseline_prediction_category": "seizure_freq_1ormore_daily",
                "ablated_prediction_category": "seizure_freq_unknown",
                "gold_category": "seizure_freq_unknown",
                "baseline_error_type": "overpredicted_frequency",
                "ablated_error_type": "correct",
                "baseline_selected_evidence_type": "clinical_evidence",
                "ablated_selected_evidence_type": "header_fallback",
            }
        )

    rows = load_changed_rows(path)

    assert rows == [
        AblationChangedRow(
            condition="disable_temporal_selection",
            source_row_index=123,
            baseline_correct=False,
            ablated_correct=True,
            baseline_prediction_label="1 per day",
            ablated_prediction_label="unknown",
            gold_label="unknown",
            baseline_prediction_category="seizure_freq_1ormore_daily",
            ablated_prediction_category="seizure_freq_unknown",
            gold_category="seizure_freq_unknown",
            baseline_error_type="overpredicted_frequency",
            ablated_error_type="correct",
            baseline_selected_evidence_type="clinical_evidence",
            ablated_selected_evidence_type="header_fallback",
        )
    ]


def test_select_development_rows_prioritizes_overreach_then_controls() -> None:
    rows = [
        _changed_row(
            condition="disable_portable_rate_expressions",
            source_row_index=1,
            baseline_correct=True,
            ablated_correct=False,
            ablated_error_type="missed_frequency_evidence",
        ),
        _changed_row(
            condition="disable_temporal_selection",
            source_row_index=2,
            baseline_correct=False,
            ablated_correct=True,
        ),
        _changed_row(
            condition="disable_seizure_free_no_event_assertions",
            source_row_index=3,
            baseline_correct=False,
            ablated_correct=True,
            baseline_error_type="overpredicted_frequency",
            gold_category="seizure_freq_unknown",
        ),
    ]

    selected = select_development_rows(rows, max_examples=3, max_per_condition=2)

    assert [row.source_row_index for row in selected] == [3, 2, 1]
    summary = summarize_selection(selected)
    assert summary["lesson_type"] == {
        "deterministic_overreach": 2,
        "deterministic_support_control": 1,
    }


def test_select_development_rows_diversifies_and_caps_per_condition() -> None:
    rows = [
        _changed_row(
            condition="disable_temporal_selection",
            source_row_index=index,
            baseline_correct=False,
            ablated_correct=True,
        )
        for index in range(1, 5)
    ]
    rows.append(
        _changed_row(
            condition="disable_portable_rate_expressions",
            source_row_index=20,
            baseline_correct=False,
            ablated_correct=True,
            baseline_error_type="overpredicted_frequency",
            gold_category="seizure_freq_unknown",
        )
    )

    selected = select_development_rows(rows, max_examples=4, max_per_condition=1)

    assert [row.condition for row in selected] == [
        "disable_portable_rate_expressions",
        "disable_temporal_selection",
    ]


def test_build_development_examples_attaches_deterministic_diagnostics(monkeypatch) -> None:
    record = GanFrequencyRecord(
        source_row_index=10,
        note_text="Present Seizure Frequency: Two seizures per month.",
        gold_label="2 per month",
        gold_reference="Two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )

    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.prompt_devset.load_records_for_split",
        lambda *args, **kwargs: [record],
    )
    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.prompt_devset.load_split_manifest",
        lambda _path: {"manifest_version": "gan2026_split_v1"},
    )

    examples = build_development_examples(
        [
            _changed_row(
                condition="disable_temporal_selection",
                source_row_index=10,
                baseline_correct=False,
                ablated_correct=True,
            )
        ]
    )

    assert examples[0]["example_id"] == "gan2026-validation-10-disable_temporal_selection"
    assert examples[0]["lesson_type"] == "deterministic_overreach"
    assert examples[0]["input"]["note_text"] == record.note_text
    assert examples[0]["input"]["deterministic_final_selection"]["final_label"] == "2 per month"
    assert examples[0]["input"]["candidate_events"][0]["normalized_label"] == "2 per month"
    assert "assertion_status" in examples[0]["adjudicator_target"]["decision_record_fields"]


def test_write_jsonl_writes_one_json_object_per_line(tmp_path: Path) -> None:
    path = tmp_path / "examples.jsonl"
    write_jsonl([{"b": 2, "a": 1}, {"c": 3}], path)

    lines = path.read_text(encoding="utf-8").splitlines()

    assert [json.loads(line) for line in lines] == [{"a": 1, "b": 2}, {"c": 3}]


def test_load_changed_rows_rejects_missing_fields(tmp_path: Path) -> None:
    path = tmp_path / "changed.csv"
    path.write_text("condition,source_row_index\nx,1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required fields"):
        load_changed_rows(path)
