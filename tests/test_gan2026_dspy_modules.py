import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.dspy_modules import (
    PROMPT_VERSION,
    AdjudicatorDecisionRecord,
    build_prompt_input,
    parse_decision_json,
    run_adjudicator_devset,
    write_adjudicator_jsonl,
)


def _example() -> dict:
    return {
        "example_id": "gan2026-validation-1-demo",
        "task": "final_selection_adjudication",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_row_index": 1,
        "lesson_type": "deterministic_support_control",
        "ablation_condition": "disable_cluster_arithmetic",
        "row_ok": True,
        "input": {
            "candidate_events": [
                {
                    "event_id": "event_1",
                    "kind": "frequency_rate",
                    "raw_value": "2 per month",
                    "evidence": "two seizures per month",
                    "rule_id": "rate.demo",
                    "rule_group": "portable_rate_expressions",
                    "portability": "seizure_frequency",
                    "normalized_label": "2 per month",
                    "semantic_kind": "frequency",
                    "monthly_frequency": 2.0,
                }
            ],
            "normalized_events": [
                {
                    "event_id": "event_1",
                    "normalized_label": "2 per month",
                    "semantic_kind": "frequency",
                    "monthly_frequency": 2.0,
                    "validation_errors": [],
                }
            ],
            "deterministic_final_selection": {
                "final_label": "2 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["event_1"],
                "rationale": "Selected current frequency.",
                "evidence": "two seizures per month",
                "monthly_frequency": 2.0,
                "validation_errors": [],
            },
        },
        "reference": {
            "gold_label": "2 per month",
            "gold_category": "seizure_freq_more1mon_less1week",
            "baseline_prediction_label": "2 per month",
            "baseline_prediction_category": "seizure_freq_more1mon_less1week",
        },
        "adjudicator_target": {
            "decision_record_fields": [
                "assertion_status",
                "temporality",
                "seizure_or_event_target",
                "window",
                "normalized_rate",
                "uncertainty",
                "selected_event_ids",
                "final_label",
            ],
            "development_question": "Which candidate is current?",
        },
    }


def test_build_prompt_input_excludes_reference_labels() -> None:
    prompt = json.loads(build_prompt_input(_example()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["candidate_events"][0]["event_id"] == "event_1"
    assert "reference" not in prompt
    assert "gold_label" not in json.dumps(prompt)


def test_parse_decision_json_accepts_fenced_json_and_repairs_label() -> None:
    raw = """```json
    {
      "assertion_status": "asserted",
      "temporality": "current",
      "seizure_or_event_target": "seizures",
      "window": "current",
      "normalized_rate": "2 per month",
      "uncertainty": "low",
      "selected_event_ids": ["event_1"],
      "final_label": " 2 PER MONTH ",
      "rationale": "The current frequency is explicitly stated."
    }
    ```"""

    decision, errors = parse_decision_json(raw)

    assert isinstance(decision, AdjudicatorDecisionRecord)
    assert decision.final_label == "2 per month"
    assert errors == ["final_label_repaired: ' 2 PER MONTH ' -> '2 per month'"]


def test_parse_decision_json_repairs_common_model_schema_aliases() -> None:
    raw = json.dumps(
        {
            "assertion_status": "present",
            "temporality": "current",
            "seizure_or_event_target": "seizures",
            "window": "current",
            "normalized_rate": 2.0,
            "uncertainty": "certain",
            "selected_event_ids": ["event_1"],
            "final_label": "2 per month",
            "rationale": "The current frequency is explicitly stated.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.assertion_status == "asserted"
    assert decision.normalized_rate == "2.0"
    assert decision.uncertainty == "low"
    assert errors == []


def test_parse_decision_json_reports_schema_errors() -> None:
    decision, errors = parse_decision_json('{"final_label": "2 per month"}')

    assert decision is None
    assert errors[0].startswith("schema_validation_error")


def test_prompt_only_run_writes_not_run_records(tmp_path: Path) -> None:
    records, metadata = run_adjudicator_devset(
        [_example()],
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
    )

    assert metadata["summary"]["decision_records"] == 0
    assert records[0]["parse_errors"] == ["not_run"]
    assert records[0]["prompt_version"] == PROMPT_VERSION

    path = tmp_path / "records.jsonl"
    write_adjudicator_jsonl(records, path)
    assert json.loads(path.read_text(encoding="utf-8"))["example_id"] == "gan2026-validation-1-demo"
