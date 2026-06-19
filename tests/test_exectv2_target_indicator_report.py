from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
    build_target_indicator_report,
    render_target_indicator_markdown,
)


def test_target_indicator_report_is_limited_to_adr_0030_families() -> None:
    source = {
        "pipeline_family": "example",
        "row_count": 2,
        "candidates": [
            {
                "name": "candidate_a",
                "ownership": "hybrid",
                "routed_primary_recovery": {
                    "overall": {"f1": 0.5},
                    "headline_scores": {
                        "Diagnosis": {
                            "precision": 1.0,
                            "recall": 0.5,
                            "f1": 0.6667,
                            "tp": 1,
                            "fp": 0,
                            "fn": 1,
                            "pred_count": 1,
                            "gold_count": 2,
                        },
                        "SeizureFrequency": {
                            "precision": 1.0,
                            "recall": 1.0,
                            "f1": 1.0,
                            "tp": 1,
                            "fp": 0,
                            "fn": 0,
                            "pred_count": 1,
                            "gold_count": 1,
                        },
                        "Prescription": {
                            "precision": 1.0,
                            "recall": 1.0,
                            "f1": 1.0,
                            "tp": 1,
                            "fp": 0,
                            "fn": 0,
                            "pred_count": 1,
                            "gold_count": 1,
                        },
                        "Investigations": {
                            "precision": 1.0,
                            "recall": 1.0,
                            "f1": 1.0,
                            "tp": 1,
                            "fp": 0,
                            "fn": 0,
                            "pred_count": 1,
                            "gold_count": 1,
                        },
                        "EpilepsyCause": {
                            "precision": 0.0,
                            "recall": 0.0,
                            "f1": 0.0,
                            "tp": 0,
                            "fp": 1,
                            "fn": 1,
                            "pred_count": 1,
                            "gold_count": 1,
                        },
                    },
                },
                "routed_primary_errors": {
                    "per_entity": {
                        "Diagnosis": {"candidate_miss": 1},
                        "SeizureFrequency": {"candidate_miss": 0},
                        "Prescription": {"candidate_miss": 0},
                        "Investigations": {"candidate_miss": 0},
                        "EpilepsyCause": {"candidate_miss": 99},
                    },
                },
            }
        ],
    }

    report = build_target_indicator_report(source, threshold=0.9)

    assert tuple(report["target_indicators"]) == TARGET_INDICATORS
    candidate = report["candidates"][0]
    assert set(candidate["headline_scores"]) == set(TARGET_INDICATORS)
    assert "EpilepsyCause" not in candidate["error_analysis"]["per_indicator"]
    assert candidate["meets_all_targets"] is False
    assert candidate["blocking_indicators"] == ["Diagnosis"]
    assert candidate["headline_scores"]["Diagnosis"]["shortfall_to_target"] == 0.2333
    assert report["headline_score_policies"]["Diagnosis"].startswith(
        "projected clinical-fact concept_only score"
    )

    markdown = render_target_indicator_markdown(report)
    assert "## Headline Scoring Policy" in markdown
    assert "projected clinical-fact concept_only score" in markdown


def test_target_indicator_report_marks_candidate_when_all_targets_clear() -> None:
    scores = {
        entity: {
            "precision": 0.95,
            "recall": 0.95,
            "f1": 0.95,
            "tp": 19,
            "fp": 1,
            "fn": 1,
            "pred_count": 20,
            "gold_count": 20,
        }
        for entity in TARGET_INDICATORS
    }
    source = {
        "pipeline_family": "example",
        "row_count": 2,
        "candidates": [
            {
                "name": "candidate_a",
                "ownership": "hybrid",
                "routed_primary_recovery": {
                    "overall": {"f1": 0.95},
                    "headline_scores": scores,
                },
            }
        ],
    }

    report = build_target_indicator_report(source, threshold=0.9)

    assert report["candidates"][0]["meets_all_targets"] is True
    assert report["candidates"][0]["blocking_indicators"] == []
