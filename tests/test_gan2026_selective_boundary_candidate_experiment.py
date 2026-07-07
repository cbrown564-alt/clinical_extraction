import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_boundary_candidate_experiment as experiment,
)


def _candidate_payload(**overrides: object) -> dict:
    payload = {
        "candidate_kind": "cluster_frequency",
        "evidence_quote": "clusters every four to five weeks with several seizures per cluster",
        "currentness": "current",
        "assertion_status": "asserted",
        "seizure_type": "focal seizures",
        "rate": {
            "count_low": 1,
            "count_high": None,
            "count_is_multiple": False,
            "time_count_low": 4,
            "time_count_high": 5,
            "time_unit": "week",
            "rate_text": "clusters every four to five weeks",
        },
        "cluster": {
            "has_cluster_pattern": True,
            "cluster_cadence_text": "clusters every four to five weeks",
            "seizures_per_cluster_low": None,
            "seizures_per_cluster_high": None,
            "seizures_per_cluster_is_multiple": True,
            "cluster_uncertainty": None,
        },
        "seizure_free": {},
        "conditionality_note": None,
        "competing_state_summary": None,
        "ambiguity_flags": ["cluster burden"],
        "reason": "Cluster timing and burden are both stated.",
    }
    payload.update(overrides)
    return payload


def test_cluster_candidate_renders_multiple_burden_and_cadence_range() -> None:
    parsed, errors = experiment._parse_output(json.dumps({"candidates": [_candidate_payload()]}))

    assert errors == []
    assert parsed is not None
    label, label_errors = experiment._candidate_label(parsed.candidates[0])
    assert label_errors == []
    assert label == "1 cluster per 4 to 5 week, multiple per cluster"


def test_cluster_candidate_renders_unknown_cadence_with_burden() -> None:
    parsed, errors = experiment._parse_output(
        json.dumps(
            {
                "candidates": [
                    _candidate_payload(
                        rate={},
                        cluster={
                            "has_cluster_pattern": True,
                            "cluster_cadence_text": None,
                            "seizures_per_cluster_low": 4,
                            "seizures_per_cluster_high": 6,
                            "seizures_per_cluster_is_multiple": False,
                            "cluster_uncertainty": "timing not stated",
                        },
                    )
                ]
            }
        )
    )

    assert errors == []
    assert parsed is not None
    label, label_errors = experiment._candidate_label(parsed.candidates[0])
    assert label_errors == []
    assert label == "unknown, 4 to 6 per cluster"


def test_parse_output_repairs_no_reference_assertion_status_alias() -> None:
    parsed, errors = experiment._parse_output(
        json.dumps(
            {
                "candidates": [
                    _candidate_payload(
                        candidate_kind="no_reference",
                        assertion_status="no_reference",
                        rate={},
                        cluster={},
                    )
                ]
            }
        )
    )

    assert errors == []
    assert parsed is not None
    assert parsed.candidates[0].assertion_status == "asserted"


def test_parse_output_repairs_missing_reason_with_empty_string() -> None:
    payload = _candidate_payload()
    del payload["reason"]

    parsed, errors = experiment._parse_output(json.dumps({"candidates": [payload]}))

    assert errors == []
    assert parsed is not None
    assert parsed.candidates[0].reason == ""


def test_cluster_candidate_prefers_specific_burden_over_multiple_flag() -> None:
    parsed, errors = experiment._parse_output(
        json.dumps(
            {
                "candidates": [
                    _candidate_payload(
                        rate={
                            "count_low": 1,
                            "count_high": 1,
                            "count_is_multiple": False,
                            "time_count_low": 5,
                            "time_count_high": None,
                            "time_unit": "day",
                            "rate_text": "a day of clustering every five days",
                        },
                        cluster={
                            "has_cluster_pattern": True,
                            "cluster_cadence_text": "a day of clustering every five days",
                            "seizures_per_cluster_low": 2,
                            "seizures_per_cluster_high": 4,
                            "seizures_per_cluster_is_multiple": True,
                            "cluster_uncertainty": None,
                        },
                    )
                ]
            }
        )
    )

    assert errors == []
    assert parsed is not None
    label, label_errors = experiment._candidate_label(parsed.candidates[0])
    assert label_errors == []
    assert label == "1 cluster per 5 day, 2 to 4 per cluster"
