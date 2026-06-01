import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    hybrid_rules_candidates_llm_adjudicator as hybrid,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind

PROMPT_VERSION = hybrid.PROMPT_VERSION
AdjudicatorDecisionRecord = hybrid.AdjudicatorDecisionRecord
build_hybrid_prompt_input = hybrid.build_hybrid_rules_candidates_llm_adjudicator_prompt_input
build_prompt_input = hybrid.build_prompt_input
parse_decision_json = hybrid.parse_decision_json
run_adjudicator_devset = hybrid.run_adjudicator_devset
run_hybrid_split = hybrid.run_hybrid_rules_candidates_llm_adjudicator_split
summarize_hybrid_records = hybrid.summarize_hybrid_rules_candidates_llm_adjudicator_records
write_adjudicator_jsonl = hybrid.write_adjudicator_jsonl


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
            "note_text": "Present seizure frequency: two seizures per month.",
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
      "accepted_event_ids": ["event_1"],
      "rejected_event_ids": [],
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
            "accepted_event_ids": ["event_1"],
            "rejected_event_ids": [],
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


def test_parse_decision_json_repairs_unclear_schema_aliases() -> None:
    raw = json.dumps(
        {
            "assertion_status": "unknown",
            "temporality": "current",
            "seizure_or_event_target": "seizures",
            "window": "current",
            "normalized_rate": "unknown",
            "uncertainty": "uncertain",
            "accepted_event_ids": [],
            "rejected_event_ids": ["event_1"],
            "selected_event_ids": [],
            "final_label": "no seizure frequency reference",
            "rationale": "Seizures are discussed but no current rate is supported.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.assertion_status == "unclear"
    assert decision.uncertainty == "high"
    assert errors == []


def test_parse_decision_json_repairs_temporality_range_alias() -> None:
    raw = json.dumps(
        {
            "assertion_status": "positive",
            "temporality": "current to recent",
            "seizure_or_event_target": "seizures",
            "window": "six months",
            "normalized_rate": "seizure free for 6 month",
            "uncertainty": "low",
            "accepted_event_ids": ["event_1"],
            "rejected_event_ids": [],
            "selected_event_ids": ["event_1"],
            "final_label": "seizure free for 6 month",
            "rationale": "The candidate states no seizures over the current recent window.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.assertion_status == "asserted"
    assert decision.temporality == "recent"
    assert errors == []


def test_parse_decision_json_repairs_nullable_string_fields() -> None:
    raw = json.dumps(
        {
            "assertion_status": "unknown",
            "temporality": "since 11 Aug 2023",
            "seizure_or_event_target": "seizures",
            "window": None,
            "normalized_rate": None,
            "uncertainty": "high",
            "accepted_event_ids": [],
            "rejected_event_ids": ["event_1"],
            "selected_event_ids": [],
            "final_label": "no seizure frequency reference",
            "rationale": "No current seizure-frequency rate is stated.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.assertion_status == "unclear"
    assert decision.temporality == "recent"
    assert decision.window == "unknown"
    assert decision.normalized_rate == "unknown"
    assert errors == []


def test_parse_decision_json_repairs_negative_and_null_uncertainty() -> None:
    raw = json.dumps(
        {
            "assertion_status": "negative",
            "temporality": "current",
            "seizure_or_event_target": "seizure frequency",
            "window": "current",
            "normalized_rate": "no seizure frequency reference",
            "uncertainty": None,
            "accepted_event_ids": ["event_1"],
            "rejected_event_ids": [],
            "selected_event_ids": ["event_1"],
            "final_label": "no seizure frequency reference",
            "rationale": "No epileptic seizure frequency is documented.",
        }
    )

    decision, errors = parse_decision_json(raw)

    assert decision is not None
    assert decision.assertion_status == "negated"
    assert decision.uncertainty == "high"
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


def test_build_hybrid_prompt_input_excludes_gold_and_scores() -> None:
    class Record:
        source_row_index = 10
        note_text = "Current seizure frequency is two per month."

    diagnostics = {
        "candidate_events": [
            {
                "event_id": "event_2",
                "kind": "frequency_rate",
                "raw_value": "2 per month",
                "evidence": "two per month",
                "rule_id": "rate.demo",
                "rule_group": "portable_rate_expressions",
                "portability": "seizure_frequency",
            }
        ],
        "normalized_events": [
            {
                "event_id": "event_2",
                "normalized_label": "2 per month",
                "semantic_kind": "frequency",
                "monthly_frequency": 2.0,
                "validation_errors": [],
            }
        ],
        "final_selection": {
            "final_label": "2 per month",
            "selected_event_ids": ["event_2"],
            "evidence": "two per month",
            "monthly_frequency": 2.0,
        },
    }

    prompt = json.loads(build_hybrid_prompt_input(Record(), diagnostics))

    assert prompt["claim_type"] == "hybrid_llm_adjudicator"
    assert prompt["candidate_events"][0]["normalized_label"] == "2 per month"
    assert "monthly_frequency" not in prompt["candidate_events"][0]
    assert "gold_label" not in json.dumps(prompt)


def test_hybrid_prompt_only_scores_deterministic_and_recall(monkeypatch) -> None:
    class Record:
        source_row_index = 10
        note_text = "Current seizure frequency is two per month."
        gold_label = "2 per month"
        gold_label_kind = FrequencyLabelKind.FREQUENCY
        gold_monthly_frequency = 2.0
        row_ok = True

    class Result:
        diagnostics = {
            "candidate_events": [
                {
                    "event_id": "event_1",
                    "kind": "frequency_rate",
                    "raw_value": "2 per month",
                    "evidence": "two per month",
                    "rule_id": "rate.demo",
                    "rule_group": "portable_rate_expressions",
                    "portability": "seizure_frequency",
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
            "final_selection": {
                "final_label": "2 per month",
                "selected_event_ids": ["event_1"],
                "evidence": "two per month",
                "monthly_frequency": 2.0,
            },
            "evidence_valid": True,
        }

    class Pipeline:
        def run(self, _record):
            return Result()

    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026."
        "hybrid_rules_candidates_llm_adjudicator.Gan2026PipelineV1",
        lambda: Pipeline(),
    )

    records, metadata = run_hybrid_split(
        [Record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=False,
        escalation_reason="unit-test escalation reason",
    )

    assert metadata["dspy_cache"] is False
    assert records[0]["parse_errors"] == ["not_run"]
    assert records[0]["candidate_recall"]["purist_category_recalled"] is True
    assert records[0]["scores"]["deterministic_top"]["purist_correct"] is True
    assert metadata["escalation_reason"] == "unit-test escalation reason"
    assert metadata["summary"]["candidate_purist_recall_rate"] == 1.0


def test_summarize_hybrid_records_counts_changes() -> None:
    summary = summarize_hybrid_records(
        [
            {
                "decision_record": {"final_label": "2 per month"},
                "candidate_recall": {"purist_category_recalled": True},
                "scores": {
                    "deterministic_top": {
                        "final_label": "1 per day",
                        "purist_correct": False,
                        "pragmatic_correct": False,
                    },
                    "adjudicator": {
                        "final_label": "2 per month",
                        "purist_correct": True,
                        "pragmatic_correct": True,
                    },
                },
                "parse_errors": [],
            }
        ]
    )

    assert summary["changed_final_labels"] == 1
    assert summary["deterministic_wrong_to_adjudicator_correct"] == 1
    assert summary["deterministic_correct_to_adjudicator_wrong"] == 0
