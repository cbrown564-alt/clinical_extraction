import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ClusterDetails,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)


def test_assessment_inputs_include_general_grouping_policy_examples() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:301:1", "twelve seizures per month"),
        _cluster_candidate("llm:301:2", "clusters after sleep loss"),
    )
    record = _record(301, "Current baseline is twelve seizures per month.")

    inputs = assessment_probe.build_assessment_inputs(record, candidate_set)

    instructions = " ".join(inputs["task_instructions"])
    prompt_payload = json.dumps(inputs).lower()
    examples = json.dumps(inputs["policy_examples"])
    assert "one overarching clinical assessment" in instructions
    assert "primary_candidate_ids" in instructions
    assert "supporting_candidate_ids" in instructions
    assert "Never invent, renumber, or guess candidate ids" in instructions
    assert "at most one role" in instructions
    assert "Group primary candidates only" in instructions
    assert "For single_fact, use exactly one primary candidate" in instructions
    assert "Use additive_same_window only" in instructions
    assert "repeat the same current burden" in instructions
    assert "Do not use historical candidates as primary" in instructions
    assert "frequency_rate with zero primary candidates" in instructions
    assert "source_normalized_phrase should describe only" in instructions
    assert "do not fill seizure_free_duration fields" in instructions
    assert "outside-window seizure-free durations" in instructions
    assert "Total count plus subtype" in examples
    assert "Vague frequency plus isolated concrete event" in examples
    assert "No usable primary candidate" in examples
    assert "Primary with non-additive context" in examples
    assert "Repeated reference to same burden" in examples
    assert "Frequency plus cluster modifier" in examples
    assert "Current burden plus historical comparison" in examples
    assert "Recent cluster plus later seizure-free interval" in examples
    assert "Cluster cadence plus per-cluster burden" in examples
    assert "benchmark" not in instructions
    assert "scorer" not in instructions
    assert "external evaluator" not in instructions
    assert "final label" not in prompt_payload
    assert "gold" not in prompt_payload


def test_assemble_clinical_assessment_accepts_primary_with_context() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:302:1", "twelve seizures per month"),
        _cluster_candidate("llm:302:2", "clusters after sleep loss"),
        source_row_index=302,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:302:1"],
        supporting_candidate_ids=["llm:302:2"],
        rejected_candidate_ids=[],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            count_low=12,
            count_high=12,
            period_low=1,
            period_high=1,
            period_unit="month",
            source_normalized_phrase="twelve seizures per month",
        ),
        assessment_summary="Monthly frequency controls; clustering is context.",
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:302:1"]
    assert assessment.supporting_candidate_ids == ["llm:302:2"]
    assert assessment.aggregation_policy == "primary_with_context"
    assert assessment.normalization_policy_id == (
        "gan2026_clinical_assessment_normalization_v0"
    )
    assert assessment.normalized_burden.count_low == 12
    assert assessment.normalized_burden.count_high == 12
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalization_issues == []


def test_assemble_clinical_assessment_accepts_additive_same_window() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:303:1", "three focal aware seizures this month"),
        _frequency_candidate("llm:303:2", "two focal impaired-awareness seizures this month"),
        source_row_index=303,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:303:1", "llm:303:2"],
        aggregation_policy="additive_same_window",
        normalized_burden=NormalizedBurden(
            count_low=5,
            count_high=5,
            period_low=1,
            period_high=1,
            period_unit="month",
            source_normalized_phrase="five seizures this month",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.primary_candidate_ids == ["det:303:1", "llm:303:2"]
    assert assessment.normalized_burden.count_low == 5
    assert assessment.normalized_burden.count_high == 5
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalization_issues == []


def test_assemble_clinical_assessment_ignores_model_operand_leak() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:306:1", "two seizures per month"),
        _cluster_candidate("llm:306:2", "clusters after sleep loss"),
        source_row_index=306,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["det:306:1"],
        supporting_candidate_ids=["llm:306:2"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            count_low=999,
            count_high=999,
            period_low=1,
            period_high=1,
            period_unit="year",
            cluster_count_low=3,
            cluster_count_high=3,
            source_normalized_phrase="two seizures per month",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 2
    assert assessment.normalized_burden.count_high == 2
    assert assessment.normalized_burden.period_unit == "month"
    assert assessment.normalized_burden.cluster_count_low is None


def test_assemble_clinical_assessment_parses_seizure_free_duration() -> None:
    candidate_set = _candidate_set(
        _seizure_free_candidate("llm:307:1", "seizure free for nine months"),
        source_row_index=307,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="seizure_free",
        primary_candidate_ids=["llm:307:1"],
        aggregation_policy="seizure_free_state",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizure free for nine months",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.seizure_free_duration_low == 9
    assert assessment.normalized_burden.seizure_free_duration_high == 9
    assert assessment.normalized_burden.seizure_free_duration_unit == "month"


def test_assemble_clinical_assessment_parses_cluster_axes() -> None:
    candidate_set = _candidate_set(
        _cluster_candidate("llm:308:1", "3 clusters this month; each two to four events"),
        source_row_index=308,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="cluster_frequency",
        primary_candidate_ids=["llm:308:1"],
        aggregation_policy="cluster_axis",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="3 clusters this month; each two to four events",
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.cluster_count_low == 3
    assert assessment.normalized_burden.cluster_period_low == 1
    assert assessment.normalized_burden.cluster_period_unit == "month"
    assert assessment.normalized_burden.events_per_cluster_low == 2
    assert assessment.normalized_burden.events_per_cluster_high == 4


def test_assemble_clinical_assessment_parses_article_rate() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:309:1", "seizures once a week"),
        source_row_index=309,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:309:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(source_normalized_phrase="seizures once a week"),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_parses_every_other_interval() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:310:1", "seizures every other month"),
        source_row_index=310,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:310:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="seizures every other month"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 1
    assert assessment.normalized_burden.period_low == 2
    assert assessment.normalized_burden.period_unit == "month"


def test_assemble_clinical_assessment_parses_count_over_period_with_spasms() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:311:1", "21 to 28 epileptic spasms in three months"),
        source_row_index=311,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:311:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="21 to 28 epileptic spasms in three months"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.count_low == 21
    assert assessment.normalized_burden.count_high == 28
    assert assessment.normalized_burden.period_low == 3
    assert assessment.normalized_burden.period_unit == "month"


def test_assemble_clinical_assessment_parses_vague_count_over_period() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("llm:312:1", "multiple seizures in past week"),
        source_row_index=312,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["llm:312:1"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(
            source_normalized_phrase="multiple seizures in past week"
        ),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert errors == []
    assert assessment is not None
    assert assessment.normalized_burden.vague_count == "multiple"
    assert assessment.normalized_burden.period_low == 1
    assert assessment.normalized_burden.period_unit == "week"


def test_assemble_clinical_assessment_reports_unknown_candidate_id() -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:304:1", "two seizures per month"),
        source_row_index=304,
    )
    draft = assessment_probe.AssessmentDraft(
        assessment_kind="frequency_rate",
        primary_candidate_ids=["missing-id"],
        aggregation_policy="single_fact",
        normalized_burden=NormalizedBurden(source_normalized_phrase="two per month"),
    )

    assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
    )

    assert assessment is None
    assert any("primary_candidate_ids:unknown_candidate_id:missing-id" in error for error in errors)


def test_run_split_prompt_only_uses_default_candidate_set_artifact(
    tmp_path: Path,
) -> None:
    candidate_set = _candidate_set(
        _frequency_candidate("det:305:1", "two seizures per month"),
        source_row_index=305,
    )
    candidate_path = tmp_path / "candidate_sets.jsonl"
    candidate_path.write_text(
        json.dumps({"candidate_set": candidate_set.model_dump()}) + "\n",
        encoding="utf-8",
    )
    rows, metadata = assessment_probe.run_split(
        [_record(305, "Current baseline is two seizures per month.")],
        split="validation",
        split_manifest="test_manifest",
        model="test-model",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        candidate_set_jsonl_path=candidate_path,
    )

    assert rows[0]["typed_input"]["candidate_set"]["candidates"][0]["candidate_id"] == "det:305:1"
    assert rows[0]["parse_errors"] == ["not_run", "assessment_draft_missing"]
    assert metadata["candidate_set_jsonl_path"] == str(candidate_path)
    assert metadata["summary"]["examples"] == 1
    assert metadata["summary"]["clinical_assessment_rows"] == 0


def _candidate_set(
    *candidates: ExtractedCandidate,
    source_row_index: int = 301,
) -> CandidateSet:
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["gan2026_validation250_candidate_set_v2_high_recall"],
        candidates=list(candidates),
    )


def _frequency_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    source_type = (
        "deterministic_candidate" if candidate_id.startswith("det:") else "llm_candidate"
    )
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type=source_type,
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


def _cluster_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="cluster_frequency",
        event_type="seizure",
        cluster_details=ClusterDetails(cluster_frequency=evidence),
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


def _seizure_free_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="seizure_free",
        event_type="seizure",
        seizure_free=SeizureFreeDetails(source_phrase=evidence),
        temporality="current",
        certainty="certain",
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
