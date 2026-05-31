import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_first import (
    PROMPT_VERSION,
    LlmFirstDecisionRecord,
    build_prompt_input,
    parse_decision_json,
    run_split,
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_parse_decision_json_accepts_fenced_json_and_repairs_label() -> None:
    raw = """```json
    {
      "final_label": " 2 PER MONTH ",
      "evidence": "two seizures per month",
      "answer_kind": "frequency",
      "selected_seizure_type": "seizures",
      "time_window": "current",
      "confidence": "high",
      "rationale": "The note explicitly gives the current frequency."
    }
    ```"""

    decision, errors = parse_decision_json(raw)

    assert isinstance(decision, LlmFirstDecisionRecord)
    assert decision.final_label == "2 per month"
    assert errors == ["final_label_repaired: ' 2 PER MONTH ' -> '2 per month'"]


def test_parse_decision_json_repairs_common_model_aliases() -> None:
    raw = json.dumps(
        {
            "final_label": "1 every 2 days",
            "evidence": "seizures are occurring every 2 days on average",
            "answer_kind": "patient report",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "confidence": 0.9,
            "rationale": "The note gives a current diary average.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.answer_kind == "frequency"
    assert decision.confidence == "high"
    assert decision.final_label == "1 per 2 day"
    assert errors == ["final_label_repaired: '1 every 2 days' -> '1 per 2 day'"]


def test_parse_decision_json_repairs_benchmark_format_without_changing_interpretation() -> None:
    raw = json.dumps(
        {
            "final_label": "≤ four per week",
            "evidence": "overall a frequency of ≤ four seizures per week",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "confidence": "high",
            "rationale": "The note gives an upper-bound current rate.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.final_label == "4 per week"
    assert errors == ["final_label_repaired: '≤ four per week' -> '4 per week'"]


def test_prompt_only_run_writes_not_run_records(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
    )

    assert metadata["summary"]["decision_records"] == 0
    assert rows[0]["parse_errors"] == ["not_run"]
    assert rows[0]["prompt_version"] == PROMPT_VERSION

    path = tmp_path / "records.jsonl"
    write_jsonl(rows, path)
    assert json.loads(path.read_text(encoding="utf-8"))["source_row_index"] == 10
