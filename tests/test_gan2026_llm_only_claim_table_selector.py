import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_claim_table_selector import (
    PROMPT_POLICY_TAXONOMY,
    PROMPT_VERSION,
    REQUIRED_ABLATIONS_BEFORE_LADDER,
    SectionClaimTableExtractionRecord,
    build_prompt_input,
    parse_llm_only_claim_table_selector_json,
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
                    "cluster_axis": "none",
                    "boundary_state": "ordinary_frequency",
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
                    "cluster_axis": "none",
                    "boundary_state": "ordinary_frequency",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "semiology": "seizures",
                    "uncertainty": "low",
                },
            ],
            "final_query": {
                "selected_claim_ids": ["c1"],
                "selector_decision": "select_single_claim",
                "answer_kind": "frequency",
                "cluster_axis": "none",
                "boundary_state": "ordinary_frequency",
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
    assert prompt["prompt_version"] == "gan2026_llm_only_claim_table_selector_v5"
    assert prompt["note_text"] == _record().note_text
    assert prompt["claim_schema"]["claim_id"] == "stable string such as c1"
    assert "cluster_axis" in prompt["claim_schema"]
    assert "boundary_state" in prompt["claim_schema"]
    assert "selector_decision" in prompt["final_query_schema"]
    assert "cluster_axis" in prompt["final_query_schema"]
    assert "boundary_state" in prompt["final_query_schema"]
    assert "raw_selected_frequency" in prompt["final_query_schema"]
    assert "conversion_note" in prompt["final_query_schema"]
    assert prompt["required_ablations_before_ladder_runs"] == REQUIRED_ABLATIONS_BEFORE_LADDER
    assert "constrained final selector" in json.dumps(prompt)
    assert "Do not let final_label hide" in json.dumps(prompt)
    assert "1 per 7 to 10 day" in json.dumps(prompt)
    assert "bimonthly means every two months" in json.dumps(prompt)
    assert "Cluster cadence can be the ordinary Gan-facing frequency" in json.dumps(prompt)
    assert "twice a month -> 2 per month" in json.dumps(prompt)
    assert "5 or 7 focal onset seizures in three weeks -> 5 to 7 per 3 week" in json.dumps(prompt)
    assert "An explicit current cluster cadence normally outranks" in json.dumps(prompt)
    assert "short subsequent seizure-free span does not by itself erase" in json.dumps(prompt)
    assert "several events across most months -> multiple per month" in json.dumps(prompt)
    assert "Do not use historical as claim_type" in json.dumps(prompt)
    assert "1 cluster per month, 6 to 7 per cluster" in json.dumps(prompt)
    assert (
        "six drop attacks plus two absence seizures over two months -> 8 per 2 month"
        in json.dumps(prompt)
    )
    assert "Rescue medication use frequency" in json.dumps(prompt)
    assert "q2-3wk" in json.dumps(prompt)
    assert "as many as seven in a week" in json.dumps(prompt)
    assert "claim_type_note" not in prompt["claim_schema"]
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_prompt_input_names_prompt_policies_as_controlled_variables() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    policy_ids = {policy["policy_id"] for policy in prompt["prompt_policy_taxonomy"]}

    assert prompt["prompt_policy_taxonomy"] == PROMPT_POLICY_TAXONOMY
    assert "sct_v5.schema.scalar_enum_output" in policy_ids
    assert "sct_v5.gan_label.interval_preservation" in policy_ids
    assert "sct_v5.gan_label.cluster_dual_axis" in policy_ids
    assert "sct_v5.schema.cluster_axis_state" in policy_ids
    assert "sct_v5.selection.current_burden_precedence" in policy_ids
    assert "sct_v5.boundary.unknown_no_reference_seizure_free" in policy_ids
    assert "sct_v5.schema.boundary_state" in policy_ids
    assert "sct_v5.selection.constrained_selector" in policy_ids
    assert all(policy["status"] == "active" for policy in prompt["prompt_policy_taxonomy"])
    assert all(policy["controlled_variable"] for policy in prompt["prompt_policy_taxonomy"])
    assert all(
        policy["portability"]
        in {"general", "seizure_frequency", "gan2026_specific", "benchmark_format"}
        for policy in prompt["prompt_policy_taxonomy"]
    )


def test_parse_llm_only_claim_table_selector_json_validates_flat_claim_table() -> None:
    extraction, errors = parse_llm_only_claim_table_selector_json(
        _raw_claim_table(),
        note_text=_record().note_text,
    )

    assert isinstance(extraction, SectionClaimTableExtractionRecord)
    assert extraction.claims[0].claim_id == "c1"
    assert extraction.claims[0].cluster_axis == "none"
    assert extraction.claims[0].boundary_state == "ordinary_frequency"
    assert extraction.final_query.selected_claim_ids == ["c1"]
    assert extraction.final_query.selector_decision == "select_single_claim"
    assert errors == []


def test_parse_llm_only_claim_table_selector_json_repairs_common_model_shape_aliases() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][0]["claim_type"] = ["frequency"]
    payload["claims"][0]["temporality"] = ["current"]
    payload["claims"][1]["claim_type"] = ["frequency", "unknown_frequency"]
    payload["claims"][1]["temporality"] = ["current", "recent"]
    payload["final_query"]["selected_claim_ids"] = "c1,c2"

    extraction, errors = parse_llm_only_claim_table_selector_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.claims[0].claim_type == "frequency"
    assert extraction.claims[0].temporality == "current"
    assert extraction.claims[1].claim_type == "frequency"
    assert extraction.claims[1].temporality == "current"
    assert extraction.final_query.selected_claim_ids == ["c1", "c2"]
    assert errors == []


def test_parse_llm_only_claim_table_selector_json_repairs_extra_evidence_offsets() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][0]["evidence_start"] = 0
    payload["claims"][0]["evidence_end"] = 10

    extraction, errors = parse_llm_only_claim_table_selector_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.claims[0].claim_type == "frequency"
    assert errors == []


def test_parse_llm_only_claim_table_selector_json_repairs_nested_claim_schema_echo() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][0]["claim_schema"] = {
        "claim_id": "c1",
        "claim_type": "frequency",
        "evidence": "two focal seizures per month",
    }

    extraction, errors = parse_llm_only_claim_table_selector_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.claims[0].claim_id == "c1"
    assert errors == []


def test_parse_llm_only_claim_table_selector_json_repairs_cluster_answer_kind_alias() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][0]["claim_type"] = "cluster_frequency"
    payload["final_query"]["answer_kind"] = "cluster_frequency"

    extraction, errors = parse_llm_only_claim_table_selector_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.claims[0].claim_type == "cluster_frequency"
    assert extraction.final_query.answer_kind == "frequency"
    assert errors == []


def test_parse_llm_only_claim_table_selector_json_repairs_missing_final_query_rationale() -> None:
    payload = json.loads(_raw_claim_table("2 per month"))
    del payload["final_query"]["rationale"]

    extraction, errors = parse_llm_only_claim_table_selector_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert extraction.final_query.rationale == "two focal seizures per month"
    assert extraction.final_query.conversion_note == (
        "Non-semantic schema repair: final_query.rationale was omitted, "
        "so it was copied from final_query.evidence."
    )
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
    assert metadata["pipeline_name"] == "gan2026_llm_only_claim_table_selector_v5"
    assert metadata["prompt_policy_ids"] == [
        policy["policy_id"] for policy in PROMPT_POLICY_TAXONOMY
    ]
    assert metadata["required_ablations_before_ladder_runs"] == REQUIRED_ABLATIONS_BEFORE_LADDER
    assert metadata["repair_mode_layers"]["raw_model"]["repair_family"] == "none"
    assert metadata["repair_mode_layers"]["strict_format"]["repair_family"] == (
        "format_preserving_label_repair"
    )
    assert metadata["repair_mode_layers"]["clean_scorer_facing"]["repair_family"] == (
        "clean_scorer_facing_gold_policy"
    )
    assert row["component_status"]["claim_extraction"] == "ok"
    assert row["score_layers"]["raw"]["scorable"] is False
    assert row["score_layers"]["raw"]["repair_mode_metadata"]["repair_mode"] == "raw_model"
    assert row["score_layers"]["strict_format"]["final_label"] == "most weekdays"
    assert row["score_layers"]["strict_format"]["repair_mode_metadata"]["repair_mode"] == (
        "strict_format"
    )
    assert row["score_layers"]["clean_scorer_facing"]["final_label"] == "multiple per week"
    assert row["score_layers"]["clean_scorer_facing"]["repair_mode_metadata"]["repair_mode"] == (
        "clean_scorer_facing"
    )
    assert row["repair_mode_layers"]["clean_scorer_facing"]["semantic_selection_owner"] == "llm"
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


def test_evidence_summary_exposes_non_exact_selected_evidence_for_review() -> None:
    payload = json.loads(_raw_claim_table())
    payload["claims"][1]["evidence"] = "daily seizures historically"
    payload["final_query"]["evidence"] = "two focal seizures monthly"

    rows, _ = run_split(
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

    evidence_summary = rows[0]["evidence_summary"]
    assert evidence_summary["claim_evidence_valid"] == 1
    assert evidence_summary["claim_evidence_invalid"] == [
        {
            "claim_id": "c2",
            "evidence": "daily seizures historically",
        }
    ]
    assert evidence_summary["selected_evidence_valid"] is False
    assert evidence_summary["selected_evidence"] == "two focal seizures monthly"


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
        reuse_raw_outputs={10: _raw_claim_table("1 seizure every 2 days")},
    )
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 LLM-Only Claim Table Selector V5" in report
    assert "Required ablations before 25/50/250 ladder runs" in report
    assert "raw final-query score" in report
    assert "Reviewable Failure Details" in report
    assert "unparsable_label" in report
    assert "claim_extraction" in report
    assert "final_query" in report
    assert "scorer_format" in report
