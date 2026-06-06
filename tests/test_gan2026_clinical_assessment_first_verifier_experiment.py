import json

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_first_verifier_experiment as experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    clinical_assessment_first_verifier,
)


def _input_row(*, main_score_table: bool = True) -> dict:
    return {
        "source_row_index": 101,
        "route_bucket": (
            "verifier_eligible_ambiguity"
            if main_score_table
            else "upstream_policy_appendix"
        ),
        "report_section": (
            "main_ambiguity_score_table"
            if main_score_table
            else "upstream_policy_appendix"
        ),
        "provenance_sidecar_present": False,
        "provenance_sidecar_families": [],
        "appendix_policy": {
            "main_score_table": main_score_table,
            "appendix_only": not main_score_table,
        },
        "verifier_model_input": {
            "verification_case": {
                "baseline_verification_decision_v0": {
                    "action": "abstain",
                    "action_basis": "route_family_policy",
                    "action_reason": "baseline abstain",
                    "proposed_rendered_label": None,
                },
                "candidate_evidence_packets": [
                    {
                        "candidate_id": "llm:101:1",
                        "source_ids": ["note:101:span:0-10"],
                    }
                ],
            }
        },
    }


def _output_json(
    *,
    action: str = "affirm",
    baseline_action: str = "abstain",
    cited_candidate_ids: list[str] | None = None,
    cited_source_ids: list[str] | None = None,
    final_rendered_label: str | None = None,
    replacement_rendered_label: str | None = None,
) -> str:
    return json.dumps(
        {
            "source_row_index": 101,
            "component_owner": "llm_verifier",
            "schema_version": clinical_assessment_first_verifier.SCHEMA_VERSION,
            "verifier_policy_id": clinical_assessment_first_verifier.POLICY_ID,
            "baseline_action": baseline_action,
            "action": action,
            "action_basis": "evidence_supports_action",
            "cited_candidate_ids": cited_candidate_ids or ["llm:101:1"],
            "cited_source_ids": cited_source_ids or ["note:101:span:0-10"],
            "issue_flags": ["mixed_window_or_vague_addition"],
            "rationale": "The packet supports a direct action decision.",
            "proposed_rendered_label": None,
            "final_rendered_label": final_rendered_label,
            "replacement_rendered_label": replacement_rendered_label,
        }
    )


def test_first_verifier_contract_accepts_row_local_action_only_output() -> None:
    row = _input_row()
    parsed, errors = clinical_assessment_first_verifier.parse_output(_output_json())

    decision = clinical_assessment_first_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert errors == []
    assert decision["action"] == "affirm"
    assert decision["contract_ok"] is True
    assert decision["citations_valid"] is True


def test_first_verifier_contract_rejects_nonlocal_citations() -> None:
    row = _input_row()
    parsed, errors = clinical_assessment_first_verifier.parse_output(
        _output_json(cited_candidate_ids=["llm:999:1"])
    )

    decision = clinical_assessment_first_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["citations_valid"] is False
    assert decision["contract_ok"] is False


def test_first_verifier_contract_rejects_label_mutation_fields() -> None:
    row = _input_row()
    parsed, errors = clinical_assessment_first_verifier.parse_output(
        _output_json(final_rendered_label="1 per month")
    )

    decision = clinical_assessment_first_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["first_experiment_label_policy_ok"] is False
    assert decision["contract_ok"] is False


def test_first_verifier_summary_reports_contract_failure() -> None:
    main_row = _input_row(main_score_table=True)
    appendix_row = _input_row(main_score_table=False)
    appendix_row["source_row_index"] = 202
    appendix_row["verifier_model_input"]["verification_case"]["candidate_evidence_packets"][0][
        "candidate_id"
    ] = "llm:202:1"
    appendix_row["verifier_model_input"]["verification_case"]["candidate_evidence_packets"][0][
        "source_ids"
    ] = ["note:202:span:0-10"]
    rows = []
    for row, raw_output in [
        (main_row, _output_json(action="affirm")),
        (
            appendix_row,
            json.dumps(
                {
                    "source_row_index": 202,
                    "component_owner": "llm_verifier",
                    "schema_version": clinical_assessment_first_verifier.SCHEMA_VERSION,
                    "verifier_policy_id": clinical_assessment_first_verifier.POLICY_ID,
                    "baseline_action": "abstain",
                    "action": "abstain",
                    "action_basis": "insufficient_support",
                    "cited_candidate_ids": ["llm:bad"],
                    "cited_source_ids": ["note:202:span:0-10"],
                    "issue_flags": [],
                    "rationale": "Needs caution.",
                    "proposed_rendered_label": None,
                    "final_rendered_label": None,
                    "replacement_rendered_label": None,
                }
            ),
        ),
    ]:
        parsed, errors = clinical_assessment_first_verifier.parse_output(raw_output)
        decision = clinical_assessment_first_verifier.verifier_decision(
            parsed,
            row,
            parse_errors=errors,
        )
        rows.append(
            {
                "source_row_index": row["source_row_index"],
                "route_bucket": row["route_bucket"],
                "report_section": row["report_section"],
                "appendix_policy": row["appendix_policy"],
                "call_status": "ok",
                "parse_errors": errors,
                "usage": {},
                "latency_seconds": 0.0,
                "verifier_decision": decision,
                "verifier_vs_baseline": {
                    "action_changed": decision["action"] != decision["baseline_action"]
                },
            }
        )

    metadata = experiment.summarize_results(
        rows,
        model="openai/gpt-4.1-mini",
        source_artifact=experiment.DEFAULT_INPUT_JSONL_PATH,
    )

    assert metadata["metrics"]["main_score_table_rows"] == 1
    assert metadata["metrics"]["appendix_rows"] == 1
    assert metadata["decision"] == "contract_failures_present"
