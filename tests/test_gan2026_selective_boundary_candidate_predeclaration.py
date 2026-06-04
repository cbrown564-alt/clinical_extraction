from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_boundary_candidate_predeclaration as predecl,
)


def _candidate_union_row(
    *,
    source_row_index: int = 101,
    deterministic_recall: bool = False,
    llm_recall: bool = True,
    union_recall: bool = True,
    exact_evidence: bool = True,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "multiple per month",
        "hidden_families": ["unknown_boundary", "competing_semiologies"],
        "deterministic_top_label": "no seizure frequency reference",
        "gold_state_recall_summary": {
            "deterministic_candidates_recall": deterministic_recall,
            "llm_boundary_candidate_recall": llm_recall,
            "union_verified_candidate_recall": union_recall,
        },
        "union_verified_candidates": [
            {
                "candidate_kind": "frequency_rate",
                "evidence": "many seizures in the past month",
                "exact_evidence": exact_evidence,
                "source_id_status": "valid",
                "gate_failures": [] if exact_evidence else ["non_exact_evidence"],
                "provenance": ["llm_boundary_proposal"],
                "currentness": "current",
                "assertion_status": "asserted",
                "semiology": "focal seizures",
                "metadata": {"rate": {"rate_text": "many seizures in the past month"}},
            }
        ],
    }


def _metadata(**metric_overrides: int | float) -> dict:
    metrics = {
        "exact_evidence_rate": 1.0,
        "valid_source_id_rate": 1.0,
        "deterministic_recall_lost_rows": 0,
        "p90_union_candidate_count": 3.0,
        "unsupported_candidate_rate": 0.01,
        "llm_recall_rescue_rows": 1,
    }
    metrics.update(metric_overrides)
    return {"metrics": metrics}


def test_predeclaration_uses_saved_recall_rescue_slice_and_omits_gold_from_model_input() -> None:
    rows, summary = predecl.build_selective_boundary_candidate_predeclaration_rows(
        [
            _candidate_union_row(source_row_index=101),
            _candidate_union_row(source_row_index=202, deterministic_recall=True),
            _candidate_union_row(source_row_index=303, exact_evidence=False),
        ],
        _metadata(),
        rich_state_rows=[
            {
                "source_row_index": 101,
                "typed_input": {"note_text": "The note says many seizures in the past month."},
            }
        ],
    )

    assert [row["source_row_index"] for row in rows] == [101]
    row = rows[0]
    assert row["hard_families"] == ["unknown_boundary", "competing_semiologies"]
    assert row["model_input"]["note_text"] == ("The note says many seizures in the past month.")
    assert row["model_input"]["max_candidates"] == 4
    assert "gold_label" not in row["model_input"]
    assert "deterministic_top_label" not in row["model_input"]
    assert row["development_accounting"]["gold_label"] == "multiple per month"
    assert summary["stop_go_decision"]["decision"] == "go"
    assert summary["metrics"]["predeclared_rows"] == 1
    assert summary["metrics"]["rows_with_note_text"] == 1


def test_predeclaration_stops_when_saved_gate_metrics_do_not_authorize_calls() -> None:
    rows, summary = predecl.build_selective_boundary_candidate_predeclaration_rows(
        [_candidate_union_row()],
        _metadata(deterministic_recall_lost_rows=1),
    )

    assert rows == []
    assert summary["stop_go_decision"]["decision"] == "stop"
    assert summary["metrics"]["predeclared_rows"] == 0


def test_boundary_candidate_prompt_uses_plain_task_language() -> None:
    prompt = predecl.BOUNDARY_PROPOSER_SYSTEM_PROMPT

    assert "gold" not in prompt
    assert "benchmark" not in prompt
    assert "scorer" not in prompt
    assert "seizure-frequency answer" in prompt
    assert "one string value" in prompt
    assert "Use asserted, not no_reference" in prompt
    assert "Do not put seizures per cluster in rate count fields" in prompt
    assert "four to five weeks means time_count_low 4" in prompt
    assert "one to two times per month means count_low 1" in prompt
    assert "five days without seizures followed by a cluster means" in prompt


def test_boundary_candidate_schema_presents_choice_fields_as_scalars() -> None:
    schema_candidate = predecl.BOUNDARY_PROPOSER_OUTPUT_SCHEMA["candidates"][0]

    assert isinstance(schema_candidate["candidate_kind"], str)
    assert isinstance(schema_candidate["currentness"], str)
    assert isinstance(schema_candidate["assertion_status"], str)
    assert "candidate_kind no_reference, use asserted" in schema_candidate["assertion_status"]
    assert isinstance(schema_candidate["rate"]["time_unit"], str)
    assert isinstance(schema_candidate["seizure_free"]["duration_unit"], str)
    assert "seizures_per_cluster_is_multiple" in schema_candidate["cluster"]
    assert "does not give exact low/high numbers" in schema_candidate["cluster"][
        "seizures_per_cluster_is_multiple"
    ]
