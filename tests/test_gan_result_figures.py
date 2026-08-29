"""Figure loaders read aggregate comparison.json only."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.gan_result_figures import (
    BARBELL_CONNECTOR_MIN_ABS_DELTA,
    BARBELL_DELTA_LABEL_MIN_ABS_DELTA,
    PRAGMATIC_DISPLAY_LABELS,
    PURIST_DISPLAY_LABELS,
    gemini_cells_1_3_5,
    gemini_cells_1_3_5_barbell,
    load_living_gemini_cells,
    load_living_gemini_dev_vs_test,
    load_living_six_model_cell3,
    six_model_cell3,
    wrap_category_label,
)


def test_display_labels_use_seizure_free_not_no_seizure() -> None:
    assert PURIST_DISPLAY_LABELS["currently_no_seizure"] == "Seizure free"
    assert PRAGMATIC_DISPLAY_LABELS["currently_no_seizure"] == "Seizure free"
    assert PURIST_DISPLAY_LABELS["seizure_freq_unknown"] == "Unknown"
    assert PRAGMATIC_DISPLAY_LABELS["seizure_freq_unknown"] == "Unknown"


def test_wrap_category_label_keeps_tokens_intact() -> None:
    assert wrap_category_label("Gemini 3.7 Flash", width=10) == "Gemini 3.7\nFlash"
    assert wrap_category_label("DeepSeek V4 Flash", width=10) == "DeepSeek\nV4 Flash"
    assert wrap_category_label("Grok 4.6", width=10) == "Grok 4.6"


def test_gemini_cells_use_five_cell_ablations_and_cited_select() -> None:
    payload = {
        "n": 450,
        "cells": {
            "rules": {"select": 321, "ablation": {"extract": 321, "encode": 321}},
            "llm_extract_then_rules": {
                "select": 373,
                "ablation": {"extract": 354, "encode": 359},
            },
            "llm": {"select": 357, "ablation": {"extract": 354, "encode": 354}},
        },
    }

    chart = gemini_cells_1_3_5(payload)

    assert chart.n == 450
    assert chart.categories == ["Rules", "Both", "LLM"]
    assert chart.series["Find"] == [321 / 450, 354 / 450, 354 / 450]
    assert chart.series["Encode"] == [321 / 450, 359 / 450, 354 / 450]
    assert chart.series["Select"] == [321 / 450, 373 / 450, 357 / 450]


def test_six_model_cell3_uses_codebook_rungs_ordered_by_select() -> None:
    rungs = {
        "gemini37flash": {
            "rungs": {
                "llm_extract": {"purist_correct": 355},
                "llm_encode": {"purist_correct": 360},
                "llm_select": {"purist_correct": 374},
            },
            "format_only_check": {
                "repair_mode": "gan_rules_encode",
                "select_repair_mode": "llm_select_after_codebook",
            },
            "row_count": 450,
        },
        "grok46": {
            "rungs": {
                "llm_extract": {"purist_correct": 355},
                "llm_encode": {"purist_correct": 365},
                "llm_select": {"purist_correct": 377},
            },
            "format_only_check": {
                "repair_mode": "gan_rules_encode",
                "select_repair_mode": "llm_select_after_codebook",
            },
            "row_count": 450,
        },
        "gpt56luna": {
            "rungs": {
                "llm_extract": {"purist_correct": 312},
                "llm_encode": {"purist_correct": 332},
                "llm_select": {"purist_correct": 350},
            },
            "format_only_check": {
                "repair_mode": "gan_rules_encode",
                "select_repair_mode": "llm_select_after_codebook",
            },
            "row_count": 450,
        },
    }

    chart = six_model_cell3(rungs)

    assert chart.categories == ["Grok 4.6", "Gemini 3.7 Flash", "GPT-5.6 Luna"]
    assert chart.series["Select"] == [377 / 450, 374 / 450, 350 / 450]
    assert chart.series["Find"] == [355 / 450, 355 / 450, 312 / 450]


def test_six_model_cell3_rejects_historical_encode() -> None:
    with pytest.raises(ValueError, match="gan_rules_encode"):
        six_model_cell3(
            {
                "grok46": {
                    "row_count": 450,
                    "format_only_check": {
                        "repair_mode": "llm_encode",
                        "select_repair_mode": "llm_select_after_codebook",
                    },
                    "rungs": {
                        "llm_extract": {"purist_correct": 355},
                        "llm_encode": {"purist_correct": 365},
                        "llm_select": {"purist_correct": 377},
                    },
                }
            }
        )


def test_living_figure_sources_match_sealed_aggregates() -> None:
    cells = load_living_gemini_cells()
    models = load_living_six_model_cell3()
    assert cells.categories == ["Rules", "Both", "LLM"]
    assert cells.series["Select"] == [325 / 450, 387 / 450, 357 / 450]
    assert cells.series["Find"] == [292 / 450, 354 / 450, 354 / 450]
    assert models.categories[0] == "Gemini 3.7 Flash"
    assert models.series["Select"][0] == 387 / 450


def test_gemini_barbell_uses_select_stops_on_both_splits() -> None:
    chart = gemini_cells_1_3_5_barbell(
        development={"n": 750, "select": {"rules": 669, "hybrid": 649, "llm": 590}},
        holdout={"n": 450, "select": {"rules": 321, "hybrid": 373, "llm": 357}},
    )

    assert chart.categories == ["Rules only", "LLM + rules", "LLM only"]
    assert chart.development == [669 / 750, 649 / 750, 590 / 750]
    assert chart.holdout == [321 / 450, 373 / 450, 357 / 450]


def test_living_barbell_matches_sealed_cell_selects() -> None:
    chart = load_living_gemini_dev_vs_test()
    assert chart.development == [691 / 750, 656 / 750, 590 / 750]
    assert chart.holdout == [325 / 450, 387 / 450, 357 / 450]
    hybrid_delta = abs(chart.holdout[1] - chart.development[1])
    assert BARBELL_CONNECTOR_MIN_ABS_DELTA <= hybrid_delta < BARBELL_DELTA_LABEL_MIN_ABS_DELTA


def test_living_purist_confusion_matrix_totals() -> None:
    from clinical_extraction.paper.gan_result_figures import (
        load_living_purist_confusion_matrix,
    )

    cm = load_living_purist_confusion_matrix("gemini37flash", "test450")
    assert cm.n == 450
    assert len(cm.labels) == 10
    total = sum(sum(row) for row in cm.matrix)
    assert total == 450
    correct = sum(cm.matrix[i][i] for i in range(10))
    assert correct == 387
    assert cm.labels[-1] == "Seizure free"


def test_living_pragmatic_confusion_matrix_totals() -> None:
    from clinical_extraction.paper.gan_result_figures import (
        load_living_pragmatic_confusion_matrix,
    )

    cm = load_living_pragmatic_confusion_matrix("gemini37flash", "test450")
    assert cm.n == 450
    assert len(cm.labels) == 4
    total = sum(sum(row) for row in cm.matrix)
    assert total == 450
    correct = sum(cm.matrix[i][i] for i in range(4))
    assert correct == 396
    assert cm.labels == ["Frequent", "Infrequent", "Unknown", "Seizure free"]

