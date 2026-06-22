import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    clinical_utility_companion as companion,
)


def test_companion_report_tracks_evidence_utility_and_gold_review_flags(tmp_path: Path) -> None:
    row_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.json"
    row_path.write_text(json.dumps(_row()) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(_assembly_report()), encoding="utf-8")

    report = companion.build_companion_report(
        [companion.RunSpec("unit", report_path, row_path)],
        generated_on="2026-06-22",
        gold_loader=lambda _split: [_letter()],
    )

    run = report["runs"][0]
    quality = run["clinical_utility"]["evidence_quality"]
    assert quality["exact_evidence_rate"] == 1.0
    assert quality["attribute_signal_mentions"] == 2
    assert quality["status_counts"]["future"] == 1

    review = run["gold_disagreement_review"]
    assert review["review_row_count"] == 1
    assert review["flag_counts"]["gold_likely_incomplete"] == 1
    assert review["flag_counts"]["gold_span_drift_or_truncation"] == 1
    assert review["flag_counts"]["prediction_plausible_but_overcalled"] == 1
    assert review["flag_counts"]["deterministic_repair_changed_clinical_meaning"] == 1


def test_companion_report_splits_deterministic_actions_and_labels_proxy_surfaces(
    tmp_path: Path,
) -> None:
    row_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.json"
    row_path.write_text(json.dumps(_row()) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(_assembly_report()), encoding="utf-8")

    report = companion.build_companion_report(
        [companion.RunSpec("unit", report_path, row_path)],
        generated_on="2026-06-22",
        gold_loader=lambda _split: [_letter()],
    )

    run = report["runs"][0]
    buckets = run["deterministic_action_buckets"]["bucket_counts"]
    assert buckets["clinical_useful"] == 1
    assert buckets["benchmark_format"] == 1

    surfaces = run["repair_ablation"]["surfaces"]
    assert surfaces["source_model_scored_output"]["overall"]["f1"] == 0.5
    assert surfaces["dictionary_normalization_only"]["overall"]["f1"] == 0.8
    assert surfaces["dictionary_normalization_only"]["materialization"] == "directly_scored"
    assert surfaces["residual_benchmark_additions"]["overall"]["f1"] == 0.85
    assert surfaces["full_final_assembly"]["overall"]["f1"] == 0.88
    assert surfaces["clinical_headline"]["overall"]["f1"] == 0.9


def _letter() -> ExectLetter:
    note = (
        "Current medication: lamotrigine 100 mg twice a day. "
        "I will arrange a repeat MRI scan next month."
    )
    return ExectLetter(
        letter_id="EA1",
        note_text=note,
        annotations=(
            ExectAnnotation(
                entity="Prescription",
                text="lamotrigine-",
                attributes={"DrugName": "lamotrigine", "DrugDose": "100"},
            ),
        ),
    )


def _row() -> dict:
    return {
        "letter_id": "EA1",
        "gold_mentions": [
            {
                "entity": "Prescription",
                "text": "lamotrigine-",
                "attributes": {"DrugName": "lamotrigine", "DrugDose": "100"},
            }
        ],
        "raw_lane_mentions": [
            {
                "entity": "Prescription",
                "text": "lamotrigine",
                "attributes": {"DrugName": "lamotrigine"},
                "evidence": "Current medication: lamotrigine 100 mg twice a day.",
            }
        ],
        "predicted_mentions": [
            {
                "entity": "Prescription",
                "text": "lamotrigine",
                "attributes": {"DrugName": "lamotrigine", "DrugDose": "100"},
                "evidence": "Current medication: lamotrigine 100 mg twice a day.",
                "evidence_valid": True,
                "provenance": [
                    {"owner": "single_gpt_key_family_event_ledger", "action": "emitted"},
                    {
                        "owner": "standard_dictionary",
                        "action": "normalized_prescription_from_dictionary",
                        "portability": "clinical_epilepsy",
                    },
                ],
            },
            {
                "entity": "Investigations",
                "text": "repeat MRI scan",
                "attributes": {"MRI_Performed": "Yes"},
                "evidence": "I will arrange a repeat MRI scan next month.",
                "evidence_valid": True,
                "provenance": [
                    {
                        "owner": "deterministic_residual_benchmark_repair",
                        "action": "added_investigation_residual_benchmark_concept",
                        "portability": "benchmark_format",
                    }
                ],
            },
        ],
    }


def _assembly_report() -> dict:
    def surface(f1: float) -> dict:
        return {
            "overall": {"f1": f1},
            "by_indicator": {
                "Diagnosis": {"f1": f1},
                "SeizureFrequency": {"f1": f1},
                "Prescription": {"f1": f1},
                "Investigations": {"f1": f1},
            },
        }

    return {
        "candidate_name": "unit",
        "score_ladder": {
            "raw_lane_score": surface(0.5),
            "evidence_valid_score": surface(0.7),
            "headline_target": surface(0.9),
            "materialized_surfaces": {
                "source_scored": surface(0.5),
                "evidence_valid": surface(0.7),
                "dictionary_normalized": surface(0.8),
                "residual_benchmark_added": surface(0.85),
                "final": surface(0.88),
            },
        },
    }
