import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    saturated_surface_evaluation as saturated,
)


def _record(index: int, note: str, gold_label: str = "2 per month") -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=index,
        note_text=note,
        gold_label=gold_label,
        gold_reference=note[:30],
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=label_to_frequency_record(gold_label).kind,
        gold_yearly_bounds=None,
        gold_monthly_frequency=label_to_frequency_record(gold_label).monthly_frequency,
    )


def test_selective_action_summary_separates_raw_gated_and_flag_only() -> None:
    rows = [
        {
            "source_row_index": 1,
            "scores": {
                "deterministic_top": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
                "raw_adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
                "conservative_adjudicator": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
            },
            "decision_record": {"selected_event_ids": ["event_2"]},
            "deterministic_diagnostics": {
                "candidate_events": [{"event_id": "event_2", "evidence": "twice a month"}]
            },
            "conservative_gate": {"used_deterministic_fallback": True, "fired_gates": ["x"]},
            "parse_errors": [],
        },
        {
            "source_row_index": 2,
            "scores": {
                "deterministic_top": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
                "raw_adjudicator": {
                    "final_label": "unknown",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
                "conservative_adjudicator": {
                    "final_label": "unknown",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
            },
            "decision_record": {"selected_event_ids": []},
            "deterministic_diagnostics": {"candidate_events": []},
            "conservative_gate": {"used_deterministic_fallback": False, "fired_gates": []},
            "parse_errors": [],
        },
    ]

    summary = saturated.summarize_selective_actions(rows)

    assert summary["raw_change"]["changed_or_flagged"] == 2
    assert summary["raw_change"]["wrong_to_correct"] == 1
    assert summary["raw_change"]["correct_to_wrong"] == 1
    assert summary["gated_change"]["changed_or_flagged"] == 1
    assert summary["gated_change"]["changed_label_precision"] == 0.0
    assert summary["flag_only"]["changed_or_flagged"] == 2
    assert summary["flag_only"]["flagged_deterministic_misses"] == 1


def test_validation_hard_slices_record_membership_and_triggers() -> None:
    records = [
        _record(
            1,
            "Historically weekly seizures. Currently seizure free but had a breakthrough "
            "seizure last week.",
        ),
        _record(
            2,
            "No seizure frequency reference is documented, but seizure events are discussed.",
        ),
        _record(3, "Clusters every 2 weeks with 3 seizures per cluster."),
        _record(4, "Takes rescue medication; no explicit seizure rate is given."),
    ]
    rows = [
        {
            "source_row_index": 1,
            "scores": {
                "deterministic_top": {"final_label": "seizure free", "purist_correct": False}
            },
            "candidate_recall": {"purist_category_recalled": True},
        },
        {
            "source_row_index": 2,
            "scores": {
                "deterministic_top": {
                    "final_label": "no seizure frequency reference",
                    "purist_correct": True,
                }
            },
            "candidate_recall": {"purist_category_recalled": True},
        },
        {
            "source_row_index": 3,
            "scores": {
                "deterministic_top": {"final_label": "3 per month", "purist_correct": True}
            },
            "candidate_recall": {"purist_category_recalled": False},
        },
    ]

    artifact = saturated.build_validation_hard_slices(records, rows)

    names = {slice_["slice_name"] for slice_ in artifact["slices"]}
    assert "deterministic_miss" in names
    assert "seizure_free_overreach" in names
    assert "unknown_no_reference_boundary" in names
    assert "cluster_or_diary" in names
    slice_by_name = {slice_["slice_name"]: slice_ for slice_ in artifact["slices"]}
    assert slice_by_name["deterministic_miss"]["row_count"] == 1
    assert slice_by_name["cluster_or_diary"]["members"][0]["source_row_index"] == 3


def test_writes_saturated_surface_artifacts(tmp_path: Path) -> None:
    rows = [
        {
            "source_row_index": 1,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "scores": {
                "deterministic_top": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
                "raw_adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
                "conservative_adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
            },
            "decision_record": {"selected_event_ids": ["event_1"]},
            "deterministic_diagnostics": {
                "candidate_events": [{"event_id": "event_1", "evidence": "two per month"}]
            },
            "conservative_gate": {"used_deterministic_fallback": False, "fired_gates": []},
            "parse_errors": [],
        }
    ]
    slices = saturated.build_validation_hard_slices(
        [_record(1, "Current rate is two per month, previously daily.")], rows
    )
    result = saturated.build_saturated_surface_result(rows, slices=slices)
    json_path = tmp_path / "surface.json"
    md_path = tmp_path / "surface.md"

    saturated.write_saturated_surface_json(result, json_path)
    saturated.write_saturated_surface_report(result, md_path)

    assert json.loads(json_path.read_text(encoding="utf-8"))["row_count"] == 1
    report = md_path.read_text(encoding="utf-8")
    assert "Selective-Action Summary" in report
    assert "Validation Hard Slices" in report
