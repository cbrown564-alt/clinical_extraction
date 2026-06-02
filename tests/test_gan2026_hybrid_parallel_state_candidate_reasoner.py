import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    hybrid_parallel_state_candidate_reasoner as reasoner,
)

PIPELINE_FAMILY = reasoner.PIPELINE_FAMILY
PROMPT_VERSION = reasoner.PROMPT_VERSION
HybridParallelAdjudicatorDecision = reasoner.HybridParallelAdjudicatorDecision
build_adjudicator_prompt_input = reasoner.build_adjudicator_prompt_input
build_llm_candidate_prompt_input = reasoner.build_llm_candidate_prompt_input
parse_adjudicator_json = reasoner.parse_adjudicator_json
parse_llm_candidate_json = reasoner.parse_llm_candidate_json
run_split = reasoner.run_split
summarize_records = reasoner.summarize_records
write_report = reasoner.write_report


def _record() -> GanFrequencyRecord:
    parsed = label_to_frequency_record("2 per month")
    return GanFrequencyRecord(
        source_row_index=22,
        note_text=(
            "Current seizure frequency is two focal seizures per month. "
            "No tonic-clonic seizures for one year."
        ),
        gold_label="2 per month",
        gold_reference="two focal seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=parsed.yearly_bounds,
        gold_monthly_frequency=parsed.monthly_frequency,
    )


def _llm_candidate_raw(final_label: str = "twice per month") -> str:
    return json.dumps(
        {
            "candidates": [
                {
                    "candidate_id": "llm-1",
                    "kind": "frequency_rate",
                    "applies_to": "focal seizures",
                    "evidence": "two focal seizures per month",
                    "raw_value": "two per month",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "normalized_label": final_label,
                    "confidence": "high",
                    "rationale": "Current quantified seizure frequency.",
                }
            ],
            "selection": {
                "selected_candidate_ids": ["llm-1"],
                "final_label": final_label,
                "final_kind": "frequency",
                "selected_evidence": "two focal seizures per month",
                "rationale": "Current quantified seizure frequency.",
            },
        }
    )


def _adjudicator_raw(final_label: str = "twice per month") -> str:
    return json.dumps(
        {
            "final_label": final_label,
            "final_kind": "frequency",
            "selected_source_ids": ["llm:llm-1"],
            "selected_source_types": ["llm_candidate"],
            "selected_evidence": "two focal seizures per month",
            "confidence": "high",
            "rationale": "The LLM candidate and deterministic candidate agree.",
        }
    )


def test_prompt_inputs_exclude_gold_and_include_parallel_sources() -> None:
    candidate_prompt = json.loads(build_llm_candidate_prompt_input(_record()))
    rows, _metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        reuse_llm_candidate_outputs={22: _llm_candidate_raw()},
        reuse_adjudicator_outputs={22: _adjudicator_raw()},
    )
    adjudicator_prompt = json.loads(build_adjudicator_prompt_input(rows[0]["component_inputs"]))

    assert candidate_prompt["pipeline_family"] == PIPELINE_FAMILY
    assert candidate_prompt["prompt_version"] == PROMPT_VERSION
    assert "gold_label" not in json.dumps(candidate_prompt)
    assert "gold_label" not in json.dumps(adjudicator_prompt)
    assert adjudicator_prompt["score_layers_to_report"] == [
        *reasoner.SCORE_LAYER_NAMES,
        *reasoner.ANALYSIS_LAYER_NAMES,
    ]
    assert adjudicator_prompt["deterministic_candidates"]
    assert adjudicator_prompt["state_graph_nodes"]
    assert adjudicator_prompt["llm_candidates"][0]["candidate_id"] == "llm-1"


def test_parse_adjudicator_repairs_label_and_checks_source_ids() -> None:
    decision, errors = parse_adjudicator_json(
        _adjudicator_raw("twice per month"),
        allowed_source_ids={"det:event_1", "graph:sg-001", "llm:llm-1"},
        note_text=_record().note_text,
    )

    assert isinstance(decision, HybridParallelAdjudicatorDecision)
    assert decision.final_label == "2 per month"
    assert decision.selected_source_ids == ["llm:llm-1"]
    assert errors == ["final_label_repaired: 'twice per month' -> '2 per month'"]


def test_parse_adjudicator_flags_unknown_source_id() -> None:
    decision, errors = parse_adjudicator_json(
        _adjudicator_raw("2 per month").replace("llm:llm-1", "llm:missing"),
        allowed_source_ids={"det:event_1", "graph:sg-001", "llm:llm-1"},
        note_text=_record().note_text,
    )

    assert decision is not None
    assert "selected_source_ids: unknown ids ['llm:missing']" in errors


def test_parse_llm_candidate_json_validates_exact_evidence() -> None:
    packet, errors = parse_llm_candidate_json(_llm_candidate_raw(), note_text=_record().note_text)

    assert packet is not None
    assert packet.selection.selected_candidate_ids == ["llm-1"]
    assert errors == []


def test_run_split_records_required_smoke_layers() -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        reuse_llm_candidate_outputs={22: _llm_candidate_raw()},
        reuse_adjudicator_outputs={22: _adjudicator_raw()},
    )

    row = rows[0]
    assert metadata["pipeline_family"] == PIPELINE_FAMILY
    assert metadata["validation_smoke_stop_rule"]["call_success_minimum"] == "25/25"
    assert row["component_status"]["deterministic_top"] == "ok"
    assert row["component_status"]["state_graph_projection"] == "ok"
    assert row["component_status"]["llm_candidate_selector"] == "ok"
    assert row["component_status"]["hybrid_adjudicator"] == "ok"
    assert row["score_layers"]["deterministic_top_candidate"]["final_label"] == "2 per month"
    assert row["score_layers"]["state_graph_projection"]["final_label"] == "2 per month"
    assert row["score_layers"]["llm_candidate_selector_raw"]["final_label"] == "twice per month"
    assert row["score_layers"]["llm_candidate_selector_raw"]["scorable"] is False
    assert row["score_layers"]["hybrid_adjudicator_raw"]["final_label"] == "2 per month"
    assert row["score_layers"]["hybrid_adjudicator_with_adapters"]["final_label"] == "2 per month"
    assert row["score_layers"]["adapter_only_sidecar_from_adjudicator_selection"][
        "final_label"
    ] == "2 per month"
    assert row["analysis_layers"]["oracle_candidate_presence"]["present"] is True
    assert row["analysis_layers"]["oracle_graph_representability"]["present"] is True
    assert row["diagnostics"]["selected_source_ids_exist"] is True
    assert row["diagnostics"]["selected_evidence_exact"] is True
    assert row["diagnostics"]["selected_source_provenance_counts"] == {"llm_candidate": 1}
    assert metadata["summary"]["structured_adjudicator_records"] == 1
    assert metadata["summary"]["selected_evidence_exact"] == 1
    assert metadata["summary"]["deterministic_correct_regressions"] == 0


def test_prompt_only_without_reuse_marks_llm_layers_not_run() -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
    )

    assert rows[0]["llm_candidate_parse_errors"] == ["not_run"]
    assert rows[0]["adjudicator_parse_errors"] == ["not_run"]
    assert rows[0]["component_status"]["llm_candidate_selector"] == "fail"
    assert rows[0]["score_layers"]["hybrid_adjudicator_raw"]["scorable"] is False
    assert metadata["summary"]["parse_or_validation_failures"] == 1


def test_load_reusable_outputs_and_write_report(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        reuse_llm_candidate_outputs={22: _llm_candidate_raw("twice per month")},
        reuse_adjudicator_outputs={22: _adjudicator_raw("twice per month")},
    )
    summary = summarize_records(rows)
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    assert summary["hybrid_adjudicator_with_adapters_purist_correct"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Hybrid Parallel State Candidate Reasoner" in report
    assert "`deterministic_top_candidate`" in report
    assert "candidate-recall rescue" in report
