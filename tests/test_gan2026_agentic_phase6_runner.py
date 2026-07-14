from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import runner as agentic_runner
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    DEFAULT_CONDITIONS,
    PROMPT_VERSION,
    run_split,
    summarize_rows,
    write_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)


def test_prompt_only_runner_emits_matched_budget_traces_without_predictions() -> None:
    rows, metadata = run_split(
        [_record(101, "Clinic Date: 12 June 2026\nShe has 2 seizures per week.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert metadata["artifact_kind"] == "gan2026_agentic_matched_budget_trace"
    assert metadata["summary"]["rows"] == 1
    assert metadata["summary"]["conditions"] == list(DEFAULT_CONDITIONS)
    assert metadata["summary"]["prediction_bearing_rows"] == 0

    row = rows[0]
    assert row["source_row_index"] == 101
    assert row["split"] == "validation"
    assert row["final_label"] is None
    assert set(row["condition_traces"]) == set(DEFAULT_CONDITIONS)

    single_agent = row["condition_traces"]["single_agent_tools"]
    assert single_agent["budget"]["model_calls_per_row"] == 4
    assert single_agent["attribution_layer"] == "no_prediction"
    assert single_agent["model_call_plans"][0]["call_role"] == "agent_loop"
    assert single_agent["tool_calls"][0]["tool_name"] == "parse_seizure_frequency_candidates"
    assert single_agent["tool_calls"][0]["status"] == "contract_smoke"
    assert single_agent["tool_calls"][0]["result"]["candidates"]

    multi_agent = row["condition_traces"]["multi_agent_matched"]
    assert multi_agent["budget"] == single_agent["budget"]
    assert [call["call_role"] for call in multi_agent["model_call_plans"]] == [
        "extractor_agent",
        "boundary_agent",
        "adjudicator_agent",
        "coordinator_agent",
    ]

    payload_text = str(row).lower()
    assert "gold_label" not in payload_text
    assert "gold_normalized_label" not in payload_text


def test_runner_writes_jsonl_and_markdown_report(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record(102, "Clinic Date: 12 June 2026\nMedication reviewed.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )
    jsonl_path = tmp_path / "agentic.jsonl"
    report_path = tmp_path / "agentic.md"

    write_jsonl_rows(rows, jsonl_path)
    write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    assert jsonl_path.read_text(encoding="utf-8").count("\n") == 1
    report = report_path.read_text(encoding="utf-8")
    assert "# Gan 2026 Agentic Matched-Budget Trace" in report
    assert "single_agent_tools" in report
    assert "no-call contract smoke" in report


def test_summarize_rows_counts_tool_smoke_activity() -> None:
    rows, _ = run_split(
        [_record(103, "Clinic Date: 12 June 2026\nShe has cluster seizures twice per month.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    summary = summarize_rows(rows)

    assert summary["rows"] == 1
    assert summary["tool_smoke_calls"] >= 1
    assert summary["prediction_bearing_rows"] == 0


def test_live_runner_uses_model_outputs_and_scores_each_condition(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del prompt_input_json, model, temperature, max_tokens
        calls.append({"called": True})
        return (
            '{"final_label":"2 per week","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(agentic_runner, "_run_model_call", fake_model_call)

    rows, metadata = run_split(
        [
            _record(
                104,
                "Clinic Date: 12 June 2026\nShe has 2 seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.666666666666666,
            )
        ],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert len(calls) == 14
    assert metadata["summary"]["prediction_bearing_rows"] == 1
    assert metadata["summary"]["model_calls_attempted"] == 14
    assert metadata["summary"]["decision_records"] == 14
    assert rows[0]["final_label"] == "2 per week"

    trace = rows[0]["condition_traces"]["single_greedy"]
    assert trace["final_label"] == "2 per week"
    assert trace["attribution_layer"] == "raw_model"
    assert trace["model_call_results"][0]["decision_record"]["final_label"] == "2 per week"
    assert trace["model_call_results"][0]["comparison"]["purist_correct"] is True
    assert trace["model_call_results"][0]["prompt_version"] == PROMPT_VERSION
    prompt_input = trace["model_call_results"][0]["prompt_input_json"]
    assert "spaces, not underscores" in prompt_input
    assert "multiple_per_day" in prompt_input


def test_live_runner_can_filter_to_single_agent_conditions(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del prompt_input_json, temperature, max_tokens
        calls.append({"model": model})
        return (
            '{"final_label":"2 per week","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(agentic_runner, "_run_model_call", fake_model_call)

    active_conditions = (
        "single_greedy",
        "single_self_consistency_temperature",
        "single_agent_tools",
    )
    rows, metadata = run_split(
        [
            _record(
                106,
                "Clinic Date: 12 June 2026\nShe has 2 seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.666666666666666,
            )
        ],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
        conditions=active_conditions,
    )

    assert set(rows[0]["condition_traces"]) == set(active_conditions)
    assert "multi_agent_matched" not in rows[0]["condition_traces"]
    assert "single_self_consistency_cross_model" not in rows[0]["condition_traces"]
    assert metadata["summary"]["conditions"] == list(active_conditions)
    assert metadata["summary"]["model_calls_attempted"] == 6
    assert metadata["matched_budget"].keys() == set(active_conditions)
    assert len(calls) == 6


def test_live_runner_votes_over_deterministically_normalized_labels(monkeypatch) -> None:
    raw_labels = iter(("two_per_week", "2 per week", "2/month", "two per week"))

    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del prompt_input_json, model, temperature, max_tokens
        label = next(raw_labels)
        return (
            f'{{"final_label":"{label}","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(agentic_runner, "_run_model_call", fake_model_call)

    rows, metadata = run_split(
        [
            _record(
                107,
                "Clinic Date: 12 June 2026\nShe has 2 seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.666666666666666,
            )
        ],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
        conditions=("single_self_consistency_temperature",),
    )

    trace = rows[0]["condition_traces"]["single_self_consistency_temperature"]

    assert trace["final_label"] == "2 per week"
    assert trace["attribution_layer"] == "raw_model_plus_deterministic_format_vote"
    assert rows[0]["final_label"] == "2 per week"
    assert rows[0]["attribution_layer"] == "raw_model_plus_deterministic_format_vote"
    assert trace["normalized_label_vote"] == {
        "method": "deterministic_normalized_label_vote",
        "selected_label": "2 per week",
        "raw_labels": ["two_per_week", "2 per week", "2/month", "two per week"],
        "vote_input_labels": ["2 per week", "2 per week", "2 per month", "2 per week"],
        "normalized_labels": ["2 per week", "2 per week", "2 per month", "2 per week"],
        "vote_counts": {"2 per week": 3, "2 per month": 1},
        "tie_break": "first_normalized_label_in_call_order",
        "repair_event_counts": {},
    }
    assert metadata["summary"]["normalized_label_vote_repairs"] == 0
    assert trace["model_call_results"][0]["raw_model_final_label"] == "two_per_week"
    assert trace["model_call_results"][0]["normalized_vote_input_label"] == "2 per week"
    assert trace["model_call_results"][0]["normalized_vote_label"] == "2 per week"
    assert trace["model_call_results"][0]["normalized_vote_repair_events"] == []


def test_live_runner_votes_over_parser_repaired_decision_labels(monkeypatch) -> None:
    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del prompt_input_json, model, temperature, max_tokens
        return (
            '{"final_label":"1 per month","evidence":"one seizure every three to four weeks",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states one seizure every three to four weeks."}'
        )

    monkeypatch.setattr(agentic_runner, "_run_model_call", fake_model_call)

    rows, _metadata = run_split(
        [
            _record(
                108,
                "Clinic Date: 12 June 2026\nShe has one seizure every three to four weeks.",
                gold_label="1 per 3 to 4 week",
                gold_monthly_frequency=1.267361111111111,
            )
        ],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
        conditions=("multi_agent_matched",),
    )

    trace = rows[0]["condition_traces"]["multi_agent_matched"]

    assert trace["final_label"] == "1 per 3 to 4 week"
    assert trace["normalized_label_vote"]["raw_labels"] == ["1 per month"] * 4
    assert trace["normalized_label_vote"]["vote_input_labels"] == ["1 per 3 to 4 week"] * 4
    assert trace["model_call_results"][0]["raw_model_final_label"] == "1 per month"
    assert trace["model_call_results"][0]["decision_record"]["final_label"] == ("1 per 3 to 4 week")


def test_live_runner_keeps_failed_calls_non_prediction(monkeypatch) -> None:
    def failing_model_call(
        prompt_input_json: str, *, model: str, temperature: float, max_tokens: int
    ):
        del prompt_input_json, model, temperature, max_tokens
        raise RuntimeError("no test transport")

    monkeypatch.setattr(agentic_runner, "_run_model_call", failing_model_call)

    rows, metadata = run_split(
        [_record(105, "Clinic Date: 12 June 2026\nMedication reviewed.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert rows[0]["final_label"] is None
    assert rows[0]["attribution_layer"] == "no_prediction"
    assert metadata["summary"]["call_failures"] == 14


def _record(
    source_row_index: int,
    note_text: str,
    *,
    gold_label: str = "unknown",
    gold_monthly_frequency: float = -1.0,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )
