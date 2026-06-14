from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    fresh_evidence_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_fresh_evidence_reasoner_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["fresh_evidence_reasoner"]

    assert "fresh-evidence" in spec.description
    assert spec.default_max_tokens == 2800
    assert spec.default_structured_event_jsonl_path is not None


def test_test_split_uses_frozen_test_structured_event_sources() -> None:
    validation_sources = fresh_evidence_reasoner._structured_event_source_paths_for_split(
        "validation",
        fresh_evidence_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
    )
    test_gpt_source = fresh_evidence_reasoner._gpt_structured_event_source_path(
        "test",
        fresh_evidence_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
    )
    test_sources = fresh_evidence_reasoner._structured_event_source_paths_for_split(
        "test",
        test_gpt_source,
    )

    assert validation_sources["gpt"] == (
        fresh_evidence_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    assert validation_sources["qwen"] == (
        fresh_evidence_reasoner.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH
    )
    assert validation_sources["deepseek"] == (
        fresh_evidence_reasoner.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
    )
    assert test_sources["gpt"] == (
        fresh_evidence_reasoner.TEST_GPT_STRUCTURED_EVENT_JSONL_PATH
    )
    assert test_sources["qwen"] == (
        fresh_evidence_reasoner.TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH
    )
    assert test_sources["deepseek"] == (
        fresh_evidence_reasoner.TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
    )


def test_fresh_evidence_prompt_excludes_forbidden_context() -> None:
    record = _record(
        950,
        (
            "Clinic Date: 12 June 2026\n"
            "Patient reports focal seizures twice per week despite older monthly history."
        ),
        gold_label="2 per week",
        gold_monthly_frequency=8.69047619047619,
    )

    prompt_input_json = fresh_evidence_reasoner.build_prompt_input(
        record,
        {
            "gpt": _structured_event_row(
                950,
                final_label="1 per month",
                final_kind="frequency",
                evidence="older monthly history",
                purist_correct=False,
            ),
            "qwen": None,
            "deepseek": None,
        },
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "2 per week" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V12_fresh_evidence_reasoner"
    assert "replace_with_fresh_evidence_final" in payload["required_output_schema"]["action"]
    assert "twice per week" in payload["raw_note_excerpt"]
    assert any(
        "Replacement is for represented-evidence" in item
        for item in payload["instructions"]
    )


def test_keep_action_renders_original_gpt_structured_event_final() -> None:
    parsed = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "keep_original_structured_event_final",
                "final_label": "2 per week",
                "final_kind": "frequency",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": [],
                "evidence": [
                    "twice per week",
                    "the current record proves twice per week",
                ],
                "boundary_profile": [],
                "calculation_trace": "2/week",
                "rationale": "The original answer is sufficient.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text="Patient reports twice per week.",
        structured_event_row=_structured_event_row(
            951,
            final_label="1 per month",
            final_kind="frequency",
            evidence="one per month",
            purist_correct=True,
        ),
    )

    assert parsed.raw_decision is not None
    assert parsed.raw_decision.final_label == "2 per week"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "1 per month"
    assert parsed.final_decision.selected_event_ids == ("e1",)
    assert parsed.final_decision.attribution == "llm_original_structured_event_kept"
    assert "decision_field_shape_repaired:clinical_rationale_alias" in parsed.parse_errors
    assert (
        "fresh_evidence_action_rendered:keep_original_structured_event_final"
        in parsed.action_render_events
    )


def test_live_fresh_evidence_replacement_scores_against_v0(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "deterministic_top" not in prompt_input_json
        return json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": [
                    "twice per week",
                    "the current record proves twice per week",
                ],
                "boundary_profile": ["fresh_evidence:frequency_denominator"],
                "calculation_trace": "twice per week = 2/week",
                "clinical_rationale": "The current statement overrides the older monthly history.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(fresh_evidence_reasoner, "_run_model_call", fake_model_call)

    rows, metadata = fresh_evidence_reasoner.run_split(
        [
            _record(
                952,
                (
                    "Clinic Date: 12 June 2026\n"
                    "Older history was one per month, but current seizures are twice per week."
                ),
                gold_label="2 per week",
                gold_monthly_frequency=8.69047619047619,
            )
        ],
        agent_rows_by_id={
            "gpt": [
                _structured_event_row(
                    952,
                    final_label="1 per month",
                    final_kind="frequency",
                    evidence="one per month",
                    purist_correct=False,
                )
            ],
            "qwen": [],
            "deepseek": [],
        },
        structured_event_rows=[
            _structured_event_row(
                952,
                final_label="1 per month",
                final_kind="frequency",
                evidence="one per month",
                purist_correct=False,
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2800,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    row = rows[0]

    assert metadata["summary"]["model_calls_attempted"] == 1
    assert metadata["summary"]["fresh_evidence_replace_actions"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert row["score_layers"]["raw_model"]["final_label"] == "two_per_week"
    assert row["score_layers"]["format_only"]["final_label"] == "2 per week"
    assert row["score_layers"]["final"]["final_label"] == "2 per week"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["evidence_valid"] is True
    assert (
        "fresh_evidence_action_rendered:replace_with_fresh_evidence_final"
        in row["action_render_events"]
    )
    assert "fresh_evidence_shape_repaired:filtered_non_exact_evidence" in (
        row["action_render_events"]
    )
    assert row["decision_record"]["evidence"] == ["twice per week"]


def test_unsupported_fresh_evidence_replacement_falls_back_to_original(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del prompt_input_json, model, temperature, max_tokens
        return json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "4 per day",
                "final_kind": "frequency",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["not actually in the note"],
                "boundary_profile": ["fresh_evidence:unsupported"],
                "calculation_trace": "unsupported",
                "clinical_rationale": "Unsupported replacement.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(fresh_evidence_reasoner, "_run_model_call", fake_model_call)

    rows, metadata = fresh_evidence_reasoner.run_split(
        [
            _record(
                953,
                "Clinic Date: 12 June 2026\nPatient reports one seizure per month.",
                gold_label="1 per month",
                gold_monthly_frequency=1.0138888888888888,
            )
        ],
        agent_rows_by_id={
            "gpt": [
                _structured_event_row(
                    953,
                    final_label="1 per month",
                    final_kind="frequency",
                    evidence="one seizure per month",
                    purist_correct=True,
                )
            ],
            "qwen": [],
            "deepseek": [],
        },
        structured_event_rows=[
            _structured_event_row(
                953,
                final_label="1 per month",
                final_kind="frequency",
                evidence="one seizure per month",
                purist_correct=True,
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2800,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    row = rows[0]

    assert metadata["summary"]["fresh_evidence_replace_actions"] == 1
    assert metadata["summary"]["fresh_evidence_gate_fallbacks"] == 1
    assert metadata["summary"]["correct_to_wrong_vs_v0"] == 0
    assert row["score_layers"]["raw_model"]["final_label"] == "4 per day"
    assert row["score_layers"]["final"]["final_label"] == "1 per month"
    assert row["decision_record"]["attribution"] == "llm_original_structured_event_kept"
    assert row["evidence_valid"] is True
    assert "fresh_evidence_gate_fallback: evidence_not_exact" in row["parse_errors"]


def test_safety_gate_blocks_seizure_free_demotions_and_bare_replacements() -> None:
    demotion = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "unknown",
                "final_kind": "unknown",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["non-epileptic spells are less troublesome"],
                "boundary_profile": ["seizure_free conflict"],
                "calculation_trace": None,
                "clinical_rationale": "Non-epileptic spells make frequency uncertain.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text="The patient is seizure free. non-epileptic spells are less troublesome.",
        structured_event_row=_structured_event_row(
            954,
            final_label="seizure free for multiple year",
            final_kind="seizure_free",
            evidence="The patient is seizure free.",
            purist_correct=True,
        ),
    )

    assert demotion.final_decision is not None
    assert demotion.final_decision.final_label == "seizure free for multiple year"
    assert (
        "fresh_evidence_gate_fallback: original_seizure_free_to_unknown_or_no_reference"
        in demotion.parse_errors
    )

    bare = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "seizure free",
                "final_kind": "seizure_free",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["has been seizure-free since"],
                "boundary_profile": ["explicit seizure-free interval"],
                "calculation_trace": "duration not rendered",
                "clinical_rationale": "The note states seizure-free since last event.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text="Her last reported event was recent and she has been seizure-free since.",
        structured_event_row=_structured_event_row(
            955,
            final_label="1 per month",
            final_kind="frequency",
            evidence="last reported event was recent",
            purist_correct=True,
        ),
    )

    assert bare.final_decision is not None
    assert bare.final_decision.final_label == "1 per month"
    assert "fresh_evidence_gate_fallback: bare_seizure_free_replacement" in (
        bare.parse_errors
    )

    short = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "seizure free for 1 month",
                "final_kind": "seizure_free",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["stable for over 4 weeks"],
                "boundary_profile": ["short seizure-free interval"],
                "calculation_trace": "only over 4 weeks",
                "clinical_rationale": "Recent last-event-only boundary.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text="She has been stable for over 4 weeks.",
        structured_event_row=_structured_event_row(
            956,
            final_label="1 per month",
            final_kind="frequency",
            evidence="last reported event was recent",
            purist_correct=True,
        ),
    )

    assert short.final_decision is not None
    assert short.final_decision.final_label == "1 per month"
    assert (
        "fresh_evidence_gate_fallback: short_seizure_free_replacement_from_frequency_original"
        in short.parse_errors
    )

    multiple = fresh_evidence_reasoner.parse_fresh_evidence_decision_json(
        json.dumps(
            {
                "action": "replace_with_fresh_evidence_final",
                "final_label": "multiple per week",
                "final_kind": "frequency",
                "selected_event_ids": ["fresh_evidence_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["overall frequency has been ≤ twice per week"],
                "boundary_profile": ["explicit numeric frequency"],
                "calculation_trace": "≤ twice per week",
                "clinical_rationale": "The explicit upper bound is not a fixed count.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        note_text="The overall frequency has been ≤ twice per week.",
        structured_event_row=_structured_event_row(
            957,
            final_label="15 per 3 month",
            final_kind="frequency",
            evidence="15 events in 3 months",
            purist_correct=True,
        ),
    )

    assert multiple.final_decision is not None
    assert multiple.final_decision.final_label == "15 per 3 month"
    assert (
        "fresh_evidence_gate_fallback: multiple_label_for_explicit_numeric_frequency"
        in multiple.parse_errors
    )


def test_write_report_keeps_validation_row_table(tmp_path: Path) -> None:
    report_path = tmp_path / "validation.md"
    fresh_evidence_reasoner.write_report(
        [_report_row(9901)],
        _report_metadata(split="validation"),
        report_path,
        jsonl_path=tmp_path / "validation.jsonl",
    )

    report = report_path.read_text(encoding="utf-8")

    assert "- Split: `validation`, manifest `gan2026_split_v1`." in report
    assert "- Format-only Purist: 1/1" in report
    assert "- Format-only Pragmatic: 1/1" in report
    assert "- Final Pragmatic: 1/1" in report
    assert "## Rows" in report
    assert "9901" in report


def test_write_report_omits_test_row_table_for_aggregate_only_readout(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    fresh_evidence_reasoner.write_report(
        [_report_row(9902)],
        _report_metadata(split="test"),
        report_path,
        jsonl_path=tmp_path / "test.jsonl",
    )

    report = report_path.read_text(encoding="utf-8")

    assert "frozen aggregate-only V12 fresh-evidence holdout audit" in report
    assert "- Split: `test`, manifest `gan2026_split_v1`." in report
    assert "- V0 Pragmatic: 0/1" in report
    assert "- Raw model Pragmatic: 1/1" in report
    assert "- Format-only Purist: 1/1" in report
    assert "- Format-only Pragmatic: 1/1" in report
    assert "- Final Pragmatic: 1/1" in report
    assert "## Aggregate-Only Holdout Readout" in report
    assert "## Rows" not in report
    assert "9902" not in report
    assert "secret test rationale" not in report


def test_test_split_summary_omits_profile_and_label_distributions() -> None:
    validation_summary = fresh_evidence_reasoner.summarize_rows(
        [_report_row(9903)],
        split="validation",
    )
    test_summary = fresh_evidence_reasoner.summarize_rows(
        [_report_row(9903)],
        split="test",
    )

    assert validation_summary["fresh_evidence_profiles"] == {"secret test rationale": 1}
    assert validation_summary["final_labels"] == {"2 per week": 1}
    assert "fresh_evidence_profiles" not in test_summary
    assert "final_labels" not in test_summary
    assert test_summary["aggregate_only_omitted_fields"] == [
        "final_labels",
        "fresh_evidence_profiles",
    ]


def _record(
    source_row_index: int,
    note_text: str,
    *,
    gold_label: str = "unknown",
    gold_monthly_frequency: float = 1000.0,
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
        gold_normalized_label=gold_label,
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )


def _structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    evidence: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": final_label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": evidence,
                    "time_window": "current",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": evidence,
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def _report_metadata(*, split: str) -> dict:
    return {
        "date": "2026-06-13",
        "split": split,
        "split_manifest": "gan2026_split_v1",
        "mode": "live",
        "model": "openai/gpt-4.1",
        "prompt_version": "gan2026_fresh_evidence_reasoner_v0_4",
        "claim_boundary": fresh_evidence_reasoner._claim_boundary_for_split(split),
        "summary": {
            "rows": 1,
            "prediction_bearing_rows": 1,
            "model_calls_attempted": 1,
            "call_failures": 0,
            "parse_or_validation_failures": 0,
            "fresh_evidence_replace_actions": 1,
            "fresh_evidence_gate_fallbacks": 0,
            "evidence_exact_substrings": 1,
            "v0_purist_correct": 0,
            "v0_pragmatic_correct": 0,
            "raw_model_purist_correct": 1,
            "raw_model_pragmatic_correct": 1,
            "format_only_purist_correct": 1,
            "format_only_pragmatic_correct": 1,
            "final_purist_correct": 1,
            "final_pragmatic_correct": 1,
            "net_purist_gain_vs_v0": 1,
            "changed_label_precision_vs_v0": 1.0,
            "fresh_evidence_actions": {"replace_with_fresh_evidence_final": 1},
            "fresh_evidence_profiles": {"secret test rationale": 1},
        },
        "gate": {"status": "promote", "interpretation": "test"},
    }


def _report_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "fresh_evidence_decision_record": {
            "action": "replace_with_fresh_evidence_final",
            "boundary_profile": ["secret test rationale"],
        },
        "score_layers": {
            "raw_model": {"final_label": "2 per week"},
            "final": {"final_label": "2 per week"},
        },
        "v0_reference": {"final_label": "1 per month"},
        "transition_vs_v0": {"purist_transition": "wrong_to_correct"},
        "evidence_valid": True,
        "parse_errors": [],
        "action_render_events": [],
    }
