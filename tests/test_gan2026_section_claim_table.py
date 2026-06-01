import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind
from clinical_extraction.tasks.seizure_frequency.gan2026.section_claim_table import (
    PROMPT_VERSION,
    SectionClaimTableExtractionRecord,
    build_prompt_input,
    parse_section_claim_table_json,
    run_split,
    summarize_records,
    write_report,
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


def _raw_claim_table(final_label: str = "2 per months") -> str:
    return json.dumps(
        {
            "claims": [
                {
                    "claim_id": "c1",
                    "section": "Interval history",
                    "claim_type": "frequency",
                    "evidence": "two focal seizures per month",
                    "anchor_text": "Present seizure frequency",
                    "raw_frequency": "two focal seizures per month",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "semiology": "focal seizures",
                    "uncertainty": "low",
                },
                {
                    "claim_id": "c2",
                    "section": "Past history",
                    "claim_type": "frequency",
                    "evidence": "daily seizures in 2020",
                    "anchor_text": "Past history",
                    "raw_frequency": "daily seizures",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "semiology": "seizures",
                    "uncertainty": "low",
                },
            ],
            "final_query": {
                "selected_claim_ids": ["c1"],
                "answer_kind": "frequency",
                "final_label": final_label,
                "evidence": "two focal seizures per month",
                "confidence": "high",
                "rationale": "The current interval-history claim is the Gan-facing answer.",
            },
        }
    )


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["note_text"] == _record().note_text
    assert prompt["claim_schema"]["claim_id"] == "stable string such as c1"
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_parse_section_claim_table_json_validates_flat_claim_table() -> None:
    extraction, errors = parse_section_claim_table_json(
        _raw_claim_table(),
        note_text=_record().note_text,
    )

    assert isinstance(extraction, SectionClaimTableExtractionRecord)
    assert extraction.claims[0].claim_id == "c1"
    assert extraction.final_query.selected_claim_ids == ["c1"]
    assert errors == []


def test_parse_section_claim_table_json_repairs_common_model_shape_aliases() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][0]["claim_type"] = ["frequency"]
    payload["claims"][0]["temporality"] = ["current"]
    payload["final_query"]["selected_claim_ids"] = "c1,c2"

    extraction, errors = parse_section_claim_table_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.claims[0].claim_type == "frequency"
    assert extraction.claims[0].temporality == "current"
    assert extraction.final_query.selected_claim_ids == ["c1", "c2"]
    assert errors == []


def test_run_split_does_not_score_schema_failures_as_no_reference() -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: '{"claims": []}'},
    )

    assert rows[0]["structured_record"] is None
    assert rows[0]["score_layers"]["strict_format"]["scorable"] is False
    assert rows[0]["score_layers"]["clean_scorer_facing"]["scorable"] is False
    assert metadata["summary"]["clean_scorer_facing_scorable"] == 0


def test_run_split_records_raw_strict_and_clean_scoring_layers() -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_claim_table("most weekdays")},
    )

    row = rows[0]
    assert metadata["pipeline_name"] == "gan2026_section_claim_table_v0"
    assert row["component_status"]["claim_extraction"] == "ok"
    assert row["score_layers"]["raw"]["scorable"] is False
    assert row["score_layers"]["strict_format"]["final_label"] == "most weekdays"
    assert row["score_layers"]["clean_scorer_facing"]["final_label"] == "multiple per week"
    assert row["repair_changes"] == [
        {
            "layer": "clean_scorer_facing",
            "before": "most weekdays",
            "after": "multiple per week",
        }
    ]
    assert metadata["summary"]["raw_scorable"] == 0
    assert metadata["summary"]["clean_scorer_facing_purist_correct"] == 0


def test_summarize_records_counts_claim_and_selected_evidence() -> None:
    rows, _ = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_claim_table()},
    )

    summary = summarize_records(rows)

    assert summary["claim_evidence_valid"] == 2
    assert summary["claim_evidence_total"] == 2
    assert summary["selected_evidence_valid"] == 1
    assert summary["strict_format_purist_correct"] == 1
    assert summary["clean_scorer_facing_purist_correct"] == 1


def test_write_report_includes_component_localized_failure_metadata(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_claim_table()},
    )
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 Section Claim Table V0" in report
    assert "raw final-query score" in report
    assert "claim_extraction" in report
    assert "final_query" in report
    assert "scorer_format" in report
