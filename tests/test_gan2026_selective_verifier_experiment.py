import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_experiment as experiment,
)


def _predeclared_row(
    *,
    routing_label: str | None = "unknown",
    routing_action: str = "route_unknown",
    gold_label: str = "1 per month",
    output: str | None = None,
) -> tuple[dict, experiment.VerifierOutput]:
    if output is None:
        output = _output_json(
            recommendation="render_as_selected_state",
            recommended_label="1 per month",
            reason="The selected state gives a countable current rate.",
        )
    parsed, errors = experiment._parse_output(output)
    assert parsed is not None
    assert errors == []
    row = {
        "source_row_index": 101,
        "development_accounting": {
            "gold_label": gold_label,
            "routing_policy_action": routing_action,
            "routing_policy_label": routing_label,
        },
        "verifier_model_input": {
            "selected_state": {
                "selected_evidence": "Current seizures occur once per month.",
            },
            "provided_competing_hypotheses": [
                "A historical seizure-free interval is also mentioned."
            ],
        },
    }
    return row, parsed


def test_verifier_decision_counts_wrong_to_correct_against_routing_unknown() -> None:
    row, parsed = _predeclared_row()

    verifier = experiment._verifier_decision(parsed, row, parse_errors=[])
    routing = experiment._routing_decision(row)
    delta = experiment._delta(verifier, routing)

    assert verifier["label"] == "1 per month"
    assert verifier["purist_correct"] is True
    assert routing["purist_correct"] is False
    assert delta == {"decision_changed": True, "delta": "W_to_C"}


def test_verifier_decision_keeps_correct_to_wrong_regression_visible() -> None:
    row, parsed = _predeclared_row(
        routing_label="1 per month",
        gold_label="1 per month",
        output=_output_json(
            recommendation="render_as_unknown",
            recommended_label="unknown",
            reason="Ambiguous current rate.",
            confidence="medium",
        ),
    )

    verifier = experiment._verifier_decision(parsed, row, parse_errors=[])
    routing = experiment._routing_decision(row)
    delta = experiment._delta(verifier, routing)

    assert verifier["label"] == "unknown"
    assert verifier["purist_correct"] is False
    assert routing["purist_correct"] is True
    assert delta == {"decision_changed": True, "delta": "C_to_W"}


def test_abstain_is_reported_as_review_not_correct_label() -> None:
    row, parsed = _predeclared_row(
        output=_output_json(
            recommendation="abstain_review",
            recommended_label=None,
            reason="Needs review.",
            confidence="low",
        ),
    )

    verifier = experiment._verifier_decision(parsed, row, parse_errors=[])
    routing = experiment._routing_decision(row)
    delta = experiment._delta(verifier, routing)

    assert verifier["scorable"] is False
    assert verifier["purist_correct"] is None
    assert delta == {"decision_changed": True, "delta": "W_to_review"}


def test_render_unknown_is_unchanged_when_routing_already_outputs_unknown() -> None:
    row, parsed = _predeclared_row(
        output=_output_json(
            recommendation="render_as_unknown",
            recommended_label="unknown",
            reason="The state remains unresolved.",
            confidence="medium",
        ),
    )

    verifier = experiment._verifier_decision(parsed, row, parse_errors=[])
    routing = experiment._routing_decision(row)
    delta = experiment._delta(verifier, routing)

    assert verifier["label"] == routing["label"] == "unknown"
    assert delta == {"decision_changed": False, "delta": "unchanged"}


def test_non_exact_evidence_quote_fails_evidence_gate() -> None:
    row, parsed = _predeclared_row(
        output=_output_json(
            recommendation="render_as_selected_state",
            recommended_label="1 per month",
            reason="The selected state gives a countable current rate.",
            evidence_quotes=["not copied from the input"],
        ),
    )

    verifier = experiment._verifier_decision(parsed, row, parse_errors=[])

    assert verifier["all_evidence_quotes_exact"] is False


def test_summary_blocks_promotion_when_regression_exists() -> None:
    good_row, good_parsed = _predeclared_row()
    bad_row, bad_parsed = _predeclared_row(routing_label="1 per month", gold_label="1 per month")
    bad_parsed.recommendation = "render_as_unknown"
    bad_parsed.recommended_label = "unknown"
    rows = []
    for source_row_index, row, parsed in [
        (101, good_row, good_parsed),
        (202, bad_row, bad_parsed),
    ]:
        verifier = experiment._verifier_decision(parsed, row, parse_errors=[])
        routing = experiment._routing_decision(row)
        rows.append(
            {
                "source_row_index": source_row_index,
                "call_status": "ok",
                "parse_errors": [],
                "verifier_recommendation": parsed.recommendation,
                "verifier_decision": verifier,
                "routing_decision": routing,
                "verifier_vs_routing": experiment._delta(verifier, routing),
                "usage": {},
                "latency_seconds": 0.0,
            }
        )

    metadata = experiment.summarize_results(rows, model="openai/gpt-4.1-mini")

    assert metadata["metrics"]["w_to_c_vs_routing_rows"] == 1
    assert metadata["metrics"]["c_to_w_vs_routing_rows"] == 1
    assert "Do not promote" in metadata["interpretation"]


def _output_json(
    *,
    recommendation: str,
    recommended_label: str | None,
    reason: str,
    confidence: str = "high",
    evidence_quotes: list[str] | None = None,
) -> str:
    return json.dumps(
        {
            "recommendation": recommendation,
            "recommended_label": recommended_label,
            "chosen_competing_hypothesis": None,
            "evidence_quotes": evidence_quotes
            if evidence_quotes is not None
            else ["Current seizures occur once per month."],
            "reason": reason,
            "confidence": confidence,
        }
    )
