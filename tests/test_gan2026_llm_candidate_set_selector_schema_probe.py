import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    SourcePhraseOnlyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_selector_schema_probe as selector_probe,
)


def test_selector_inputs_include_candidates_without_gold_labels() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:201:1", "two seizures per month"),
        _unknown_candidate("llm:201:2", "a few events recently"),
    )
    record = _record(201, "Current baseline is two seizures per month.")

    inputs = selector_probe.build_selector_inputs(record, candidate_set)

    assert inputs["source_row_index"] == 201
    assert inputs["candidate_set"]["candidates"][0]["candidate_id"] == "det:201:1"
    assert "benchmark label" in " ".join(inputs["task_instructions"])
    assert "gold" not in json.dumps(inputs).lower()


def test_assemble_selected_fact_fills_evidence_from_selected_candidate() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:202:1", "two seizures per month"),
        _unknown_candidate("llm:202:2", "a few events recently"),
        source_row_index=202,
    )
    draft = selector_probe.SelectionDraft(
        selection_status="selected",
        selection_basis="direct_candidate_selection",
        clinical_fact_kind="frequency_rate",
        selected_candidate_ids=["det:202:1"],
        rejected_candidate_ids=["llm:202:2"],
        primary_evidence_texts=["two seizures per month"],
        rationale="Explicit current rate beats vague quantity wording.",
    )

    selection, errors = selector_probe.assemble_selected_fact(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert selection is not None
    assert selection.selection_status == "selected"
    assert selection.primary_evidence == [
        EvidenceSpan(text="two seizures per month", start_char=0, end_char=22)
    ]
    assert selection.source_ids == ["note:202:span:0-22"]
    assert selection.rejected_candidate_ids == ["llm:202:2"]


def test_assemble_selected_fact_reports_unknown_candidate_id() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:203:1", "two seizures per month"),
        source_row_index=203,
    )
    draft = selector_probe.SelectionDraft(
        selection_status="selected",
        selection_basis="direct_candidate_selection",
        clinical_fact_kind="frequency_rate",
        selected_candidate_ids=["missing-id"],
        primary_evidence_texts=["two seizures per month"],
    )

    selection, errors = selector_probe.assemble_selected_fact(
        draft,
        candidate_set=candidate_set,
    )

    assert selection is None
    assert any("unknown_candidate_id:missing-id" in error for error in errors)
    assert any("selected status requires primary_evidence" in error for error in errors)


def test_run_split_prompt_only_uses_default_candidate_set_artifact(
    tmp_path: Path,
    monkeypatch,
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:204:1", "two seizures per month"),
        source_row_index=204,
    )
    candidate_path = tmp_path / "candidate_sets.jsonl"
    candidate_path.write_text(
        json.dumps({"candidate_set": candidate_set.model_dump()}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(selector_probe, "DEFAULT_CANDIDATE_SET_JSONL_PATH", candidate_path)

    rows, metadata = selector_probe.run_split(
        [_record(204, "Current baseline is two seizures per month.")],
        split="validation",
        split_manifest="test_manifest",
        model="test-model",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
    )

    assert rows[0]["typed_input"]["candidate_set"]["candidates"][0]["candidate_id"] == "det:204:1"
    assert rows[0]["parse_errors"] == ["not_run", "selection_draft_missing"]
    assert metadata["summary"]["examples"] == 1
    assert metadata["summary"]["selected_fact_rows"] == 0


def _candidate_set(
    *candidates: ExtractedCandidate,
    source_row_index: int = 201,
) -> CandidateSet:
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["gan2026_validation250_candidate_set_v2_high_recall"],
        candidates=list(candidates),
    )


def _frequency_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="deterministic_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="frequency_rate",
        event_type="seizure",
        frequency=FrequencyDetails(source_phrase=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _unknown_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="unknown_frequency",
        event_type="seizure",
        unknown_frequency=SourcePhraseOnlyDetails(source_phrase=evidence),
        temporality="current",
        certainty="uncertain",
        certainty_reason="vague_count",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def _record(source_row_index: int, note_text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=0.0,
    )
