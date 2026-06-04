from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq8_telemetry_guard,
)


def test_rq8_telemetry_guard_blocks_cost_latency_token_claims_when_missing() -> None:
    metadata = rq8_telemetry_guard.build_rq8_telemetry_guard(
        {
            "rows": [
                {
                    "component": "candidate_conditioned_evidence_only",
                    "surface": "hard_control",
                    "model": "openai/gpt-4.1-mini",
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                    "wall_clock_latency_seconds": None,
                    "retry_count": None,
                    "estimated_cost_per_1000_notes_usd": None,
                }
            ]
        }
    )

    assert metadata["cost_latency_token_claim_authorized"] is False
    assert metadata["missing_telemetry_rows"] == 1
    assert metadata["missing_field_counts"]["prompt_tokens"] == 1
    assert "blocked" in metadata["claim_boundary"]


def test_rq8_telemetry_guard_authorizes_only_complete_telemetry_matrix() -> None:
    metadata = rq8_telemetry_guard.build_rq8_telemetry_guard(
        {
            "rows": [
                {
                    "component": "candidate_conditioned_evidence_only",
                    "surface": "hard_control",
                    "model": "openai/gpt-4.1-mini",
                    "prompt_tokens": 1200,
                    "completion_tokens": 90,
                    "total_tokens": 1290,
                    "wall_clock_latency_seconds": 1.2,
                    "retry_count": 0,
                    "estimated_cost_per_1000_notes_usd": 10.0,
                }
            ]
        }
    )

    assert metadata["cost_latency_token_claim_authorized"] is True
    assert metadata["complete_telemetry_rows"] == 1
    assert metadata["missing_field_counts"] == {}
