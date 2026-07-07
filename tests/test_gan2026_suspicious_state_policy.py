from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.suspicious_state_policy import (
    final_policy_label,
    first_failure_owner,
    routing_action,
    suspicious_flags,
)


def test_suspicious_policy_routes_count_blocking_ambiguity_to_unknown() -> None:
    flags = suspicious_flags(
        {
            "state_kind": "frequency",
            "ambiguity_flags": ["The exact number of current seizure events is unclear."],
        },
        exact_trace=True,
        source_id_status="valid",
    )

    assert flags == ["frequency_with_count_blocking_ambiguity"]
    assert routing_action(flags) == "route_unknown"
    assert final_policy_label("1 per month", "route_unknown") == "unknown"
    assert first_failure_owner(flags) == "selected_state_ambiguity"


def test_suspicious_policy_routes_missing_exact_evidence_to_review() -> None:
    flags = suspicious_flags(
        {"state_kind": "frequency"},
        exact_trace=False,
        source_id_status="invalid",
    )

    assert flags == ["selected_evidence_missing_exact_trace"]
    assert routing_action(flags) == "route_review"
    assert final_policy_label("1 per month", "route_review") is None
    assert first_failure_owner(flags) == "evidence_trace"


def test_suspicious_policy_renders_clean_state() -> None:
    flags = suspicious_flags(
        {
            "state_kind": "frequency",
            "rate": {
                "count_low": 1,
                "time_unit": "month",
                "rate_time_basis_known": True,
            },
            "selected_evidence": "Current seizures occur once per month.",
        },
        exact_trace=True,
        source_id_status="not_instrumented",
    )

    assert flags == []
    assert routing_action(flags) == "render"
    assert final_policy_label("1 per month", "render") == "1 per month"
    assert first_failure_owner(flags) == "none"
