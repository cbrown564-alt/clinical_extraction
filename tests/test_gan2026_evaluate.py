from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_frequency_records,
    evaluate_predictions,
)


def test_evaluate_predictions_matches_expected_micro_macro_weighted_metrics() -> None:
    results = evaluate_predictions([0, 1.0, 4.0], [0, 1.0, 30.0], method="purist")

    assert results["micro_f1"] == 0.6667
    assert results["micro"] == {
        "precision": 0.6667,
        "recall": 0.6667,
        "f1": 0.6667,
        "micro_f1": 0.6667,
        "accuracy": 0.6667,
    }
    assert results["macro"]["f1"] == 0.5
    assert results["weighted"]["f1"] == 0.6667


def test_evaluate_frequency_records_can_score_known_gold_frequencies() -> None:
    records = [
        {"source_row_index": 1, "gold_monthly_frequency": 0.0, "prediction": 0.0},
        {"source_row_index": 2, "gold_monthly_frequency": 1.0, "prediction": 30.0},
    ]

    results = evaluate_frequency_records(records, prediction_key="prediction", method="purist")

    assert results["micro"]["accuracy"] == 0.5
