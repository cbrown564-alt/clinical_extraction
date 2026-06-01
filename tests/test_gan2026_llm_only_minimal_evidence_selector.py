import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_minimal_evidence_selector as minimal_selector,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text=(
            "Interval history: Present seizure frequency is two focal seizures per month. "
            "Past history included daily seizures in 2020."
        ),
        gold_label="2 per month",
        gold_reference="two focal seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _raw_minimal(answer_text: str = "two focal seizures per month") -> str:
    return json.dumps(
        {
            "answer": {
                "state": "frequency",
                "answer_text": answer_text,
                "evidence": "two focal seizures per month",
                "confidence": "high",
                "reason": "The interval history gives the current frequency.",
            },
            "supporting_facts": [
                {
                    "fact_id": "f1",
                    "role": "selected",
                    "state": "frequency",
                    "fact_text": "two focal seizures per month",
                    "evidence": "two focal seizures per month",
                },
                {
                    "fact_id": "f2",
                    "role": "rejected",
                    "state": "frequency",
                    "fact_text": "daily seizures",
                    "evidence": "daily seizures in 2020",
                },
            ],
        }
    )


def test_build_prompt_input_exposes_minimal_contract_without_rich_selector_state() -> None:
    prompt = json.loads(minimal_selector.build_prompt_input(_record()))

    assert prompt["prompt_version"] == minimal_selector.PROMPT_VERSION
    assert prompt["prompt_version"] == "gan2026_llm_only_minimal_evidence_selector_v0"
    assert prompt["prompt_policy_taxonomy"] == minimal_selector.PROMPT_POLICY_TAXONOMY
    assert prompt["answer_schema"]["answer_text"] == "source-near selected answer text"
    assert prompt["supporting_fact_schema"]["fact_id"] == "stable string such as f1"
    prompt_text = json.dumps(prompt)
    assert "Do not create a nested final_query object" in prompt_text
    assert "Do not fill cluster_axis" in prompt_text
    assert "gold_label" not in prompt_text
    assert "candidate_events" not in prompt
    assert "final_query_schema" not in prompt
    assert "cluster_axis" not in prompt["answer_schema"]
    assert "boundary_state" not in prompt["answer_schema"]


def test_parse_minimal_evidence_selector_json_validates_shallow_schema() -> None:
    extraction, errors, diagnostics = minimal_selector.parse_minimal_evidence_selector_json(
        _raw_minimal()
    )

    assert isinstance(extraction, minimal_selector.MinimalEvidenceExtractionRecord)
    assert extraction.answer.state == "frequency"
    assert extraction.answer.answer_text == "two focal seizures per month"
    assert extraction.supporting_facts[0].fact_id == "f1"
    assert errors == []
    assert diagnostics["raw_json_valid"] is True
    assert diagnostics["schema_valid"] is True
    assert diagnostics["repair_applied"] is False


def test_parse_minimal_evidence_selector_json_repairs_qwen_style_final_selector_alias() -> None:
    raw = json.dumps(
        {
            "claims": [
                {
                    "claim_id": "c1",
                    "claim_type": "frequency",
                    "raw_frequency": "<= four per day",
                    "evidence": "two focal seizures per month",
                }
            ],
            "final_query": "What is the patient's current seizure frequency?",
            "final_selector": {
                "answer_kind": "frequency",
                "final_label": "2 per month",
                "evidence": "two focal seizures per month",
                "reasoning": "The selected claim gives the current frequency.",
            },
        }
    )

    extraction, errors, diagnostics = minimal_selector.parse_minimal_evidence_selector_json(raw)

    assert extraction is not None
    assert extraction.answer.state == "frequency"
    assert extraction.answer.answer_text == "2 per month"
    assert extraction.supporting_facts[0].fact_id == "c1"
    assert "schema_repair: final_selector mapped to answer" in errors
    assert "schema_repair: claims mapped to supporting_facts" in errors
    assert diagnostics["repair_applied"] is True
    assert diagnostics["repair_policy"] == "minimal_alias_shape_repair_v0"
    assert diagnostics["extra_fields_seen"] == ["claims", "final_query", "final_selector"]


def test_run_split_records_score_layers_evidence_and_derived_projection() -> None:
    rows, metadata = minimal_selector.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_minimal("2 per month")},
    )

    row = rows[0]
    assert metadata["pipeline_name"] == "gan2026_llm_only_minimal_evidence_selector_v0"
    assert metadata["schema_contract"] == "minimal_model_boundary_plus_derived_diagnostics_v0"
    assert row["minimal_record"]["answer"]["state"] == "frequency"
    assert row["evidence_summary"]["answer_evidence_valid"] is True
    assert row["evidence_summary"]["supporting_fact_evidence_valid"] == 2
    assert row["score_layers"]["raw"]["scorable"] is True
    assert row["score_layers"]["clean_scorer_facing"]["final_label"] == "2 per month"
    assert row["score_layers"]["clean_scorer_facing"]["purist_correct"] is True
    assert row["derived_diagnostics"]["derived_state"]["boundary_state"] == "ordinary_frequency"
    assert row["derived_diagnostics"]["review_projection"]["final_query"]["derived_from"] == (
        "minimal_answer"
    )
    assert metadata["summary"]["clean_scorer_facing_purist_correct"] == 1


def test_run_split_maps_boundary_states_to_scorable_sentinels() -> None:
    payload = json.loads(_raw_minimal())
    payload["answer"]["state"] = "unknown_frequency"
    payload["answer"]["answer_text"] = "frequency unclear"

    rows, _ = minimal_selector.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: json.dumps(payload)},
    )

    row = rows[0]
    assert row["score_layers"]["raw"]["final_label"] == "unknown"
    assert row["derived_diagnostics"]["derived_state"]["boundary_state"] == "unknown_frequency"
    assert row["derived_diagnostics"]["normalization"]["semantic_kind"] == "unknown"


def test_summarize_records_counts_contract_and_evidence_failures() -> None:
    rows, _ = minimal_selector.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: "{'answer': 'bad'}"},
    )

    summary = minimal_selector.summarize_records(rows)

    assert summary["minimal_records"] == 0
    assert summary["invalid_json_failures"] == 1
    assert summary["schema_failures"] == 0
    assert summary["answer_evidence_valid"] == 0


def test_write_report_includes_minimal_contract_metadata(tmp_path: Path) -> None:
    rows, metadata = minimal_selector.run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_minimal("most weekdays")},
    )
    report_path = tmp_path / "report.md"

    minimal_selector.write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 LLM-Only Minimal Evidence Selector V0" in report
    assert "Schema contract" in report
    assert "Raw minimal-answer score" in report
    assert "Contract And Evidence Issues" in report
    assert "cluster_axis=none" in report
