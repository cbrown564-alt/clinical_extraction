from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.llm_reasoning_stage0 import (
    build_family_slice_manifests,
    build_stage0_surfaces,
    run_stage0,
    score_v0_artifacts,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.shared.epilepsy.normalization import FrequencyLabelKind


def _record(
    source_row_index: int,
    *,
    note_text: str = "Focal seizures and tonic-clonic seizures occur weekly.",
    gold_label: str = "unknown",
    gold_kind: FrequencyLabelKind = FrequencyLabelKind.UNKNOWN,
    monthly: float = 1000.0,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="gold evidence",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=gold_kind,
        gold_yearly_bounds=None,
        gold_monthly_frequency=monthly,
    )


def _artifact_row(
    source_row_index: int,
    *,
    final_kind: str = "unknown",
    final_label: str = "unknown",
    purist_correct: bool = True,
    event_kind: str = "unknown_frequency",
    applies_to: str | None = None,
    evidence_valid: bool = True,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": event_kind,
                    "evidence": "evidence",
                    "raw_value": final_label,
                    "applies_to": applies_to,
                }
            ],
            "selection": {
                "final_kind": final_kind,
                "final_label": final_label,
                "selected_event_ids": ["e1"],
            },
        },
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": evidence_valid,
        "parse_errors": [],
    }


def test_family_slice_manifest_prioritizes_v0_misses() -> None:
    records = [
        _record(1, gold_label="unknown", gold_kind=FrequencyLabelKind.UNKNOWN),
        _record(2, gold_label="unknown", gold_kind=FrequencyLabelKind.UNKNOWN),
    ]
    manifests = build_family_slice_manifests(
        validation_records=records,
        v0_artifact_rows={
            "gpt": [
                _artifact_row(1, final_kind="unknown", purist_correct=True),
                _artifact_row(
                    2,
                    final_kind="frequency",
                    final_label="1 per month",
                    purist_correct=False,
                ),
            ]
        },
        source_artifacts={"gpt": "gpt.jsonl"},
        max_rows=1,
    )

    unknown_manifest = manifests["unknown_no_reference_validation50"]

    assert unknown_manifest["source_row_indices"] == [2]
    assert unknown_manifest["records"][0]["v0_purist_miss_artifacts"] == ["gpt"]
    assert (
        "v0_disagrees_with_boundary_gold_kind" in unknown_manifest["records"][0]["trigger_reasons"]
    )


def test_frequency_slice_excludes_duration_only_seizure_free_rows() -> None:
    records = [
        _record(
            1,
            note_text="The patient has been seizure-free for multiple months.",
            gold_label="seizure free for multiple month",
            gold_kind=FrequencyLabelKind.SEIZURE_FREE,
            monthly=0.0,
        )
    ]
    manifests = build_family_slice_manifests(
        validation_records=records,
        v0_artifact_rows={
            "gpt": [
                _artifact_row(
                    1,
                    final_kind="seizure_free",
                    final_label="seizure free for multiple month",
                    purist_correct=True,
                    event_kind="seizure_free",
                )
            ]
        },
        source_artifacts={"gpt": "gpt.jsonl"},
    )

    assert manifests["frequency_denominator_validation50"]["source_row_indices"] == []
    assert manifests["seizure_free_last_event_validation50"]["source_row_indices"] == [1]


def test_score_v0_artifacts_counts_missing_rows_against_surface_denominator() -> None:
    scores = score_v0_artifacts(
        {"gpt": [_artifact_row(1, purist_correct=True, evidence_valid=True)]},
        {"slice": [1, 2]},
    )

    summary = scores["slice"]["gpt"]

    assert summary["rows"] == 2
    assert summary["loaded_rows"] == 1
    assert summary["missing_rows"] == 1
    assert summary["purist_correct"] == 1
    assert summary["purist_accuracy"] == 0.5
    assert summary["evidence_valid_rate"] == 0.5


def test_score_v0_artifacts_buckets_loaded_rows_without_final_kind() -> None:
    scores = score_v0_artifacts(
        {
            "gpt": [
                {
                    "source_row_index": 1,
                    "comparison": {"purist_correct": False, "pragmatic_correct": False},
                    "evidence_valid": False,
                    "parse_errors": ["no structured selection"],
                }
            ]
        },
        {"slice": [1]},
    )

    summary = scores["slice"]["gpt"]

    assert summary["final_kind_counts"] == {"missing_final_kind": 1}
    assert summary["parse_error_rows"] == 1


def test_stage0_surfaces_include_prefixes_fixed_hard50_and_family_slices() -> None:
    records = [
        _record(index, gold_label="1 per week", gold_kind=FrequencyLabelKind.FREQUENCY)
        for index in range(1, 61)
    ]
    artifact_rows = {
        "gpt": [
            _artifact_row(
                index,
                final_kind="frequency",
                final_label="1 per week",
                purist_correct=True,
                event_kind="frequency_rate",
            )
            for index in range(1, 61)
        ]
    }
    stage0 = run_stage0(
        validation_records=records,
        v0_artifact_rows=artifact_rows,
        source_artifacts={"gpt": "gpt.jsonl"},
        fixed_hard50_manifest={"source_row_indices": [10, 11]},
    )

    surfaces = build_stage0_surfaces(
        validation_records=records,
        fixed_hard50_manifest={"source_row_indices": [10, 11]},
        family_manifests=stage0["family_manifests"],
    )

    assert surfaces["validation25_prefix"] == list(range(1, 26))
    assert surfaces["fixed_agentic_hard50"] == [10, 11]
    assert len(surfaces["frequency_denominator_validation50"]) == 50
    assert stage0["v0_scores"]["validation25_prefix"]["gpt"]["purist_correct"] == 25
