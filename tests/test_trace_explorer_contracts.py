from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from clinical_extraction.trace_explorer.adapters.illustrative import (
    load_illustrative_artifact,
)
from clinical_extraction.trace_explorer.contracts import (
    EvidenceGrade,
    EvidenceReference,
    EvidenceRole,
    OperationOwner,
    StageCategory,
    TraceChange,
)

FIXTURE = (
    Path("src")
    / "clinical_extraction"
    / "trace_explorer"
    / "fixtures"
    / "syn_014.json"
)


def test_illustrative_fixture_preserves_task_specific_stages_and_evidence() -> None:
    imported = load_illustrative_artifact(FIXTURE)

    exect = imported.traces_by_run["syn-exect-014"]
    gan = imported.traces_by_run["syn-gan-014"]

    assert exect.source.source_id == gan.source.source_id == "SYN-014"
    assert exect.source.text == gan.source.text
    assert [stage.stage_id for stage in exect.stages] == [
        "source",
        "candidate-production",
        "family-assembly",
        "schedule-normalization",
        "evidence-validation",
        "scoring",
    ]
    assert [stage.category for stage in gan.stages][2:4] == [
        StageCategory.FORMAT_REPAIR,
        StageCategory.DETERMINISTIC_SEMANTIC,
    ]

    prescription = next(
        evidence
        for stage in exect.stages
        for evidence in stage.evidence
        if evidence.evidence_id == "ev-prescription"
    )
    assert prescription.citation == "lamotrigine 150 mg twice daily"
    assert prescription.grade is EvidenceGrade.EXACT
    assert exect.source.text[prescription.start : prescription.end] == prescription.citation

    rate_stage = next(stage for stage in gan.stages if stage.stage_id == "rate-normalization")
    assert rate_stage.category is StageCategory.DETERMINISTIC_SEMANTIC
    assert rate_stage.changes[0].clinical_meaning_changed is True
    assert {finding.finding_id for finding in gan.findings} >= {
        "gan-current-rate",
        "gan-cluster-event",
        "gan-seizure-free-event",
    }


def test_evidence_offsets_and_declared_grade_must_match_the_source() -> None:
    owner = OperationOwner(component_id="fixture", display_name="Fixture")
    evidence = EvidenceReference(
        evidence_id="ev-1",
        source_id="SYN-014",
        citation="lamotrigine",
        start=0,
        end=11,
        grade=EvidenceGrade.EXACT,
        role=EvidenceRole.SELECTED,
        finding_ids=("finding-1",),
        stage_ids=("stage-1",),
    )

    with pytest.raises(ValueError, match="evidence offsets"):
        evidence.verify_against_source("prefix lamotrigine")

    repaired = evidence.model_copy(update={"grade": EvidenceGrade.REPAIRED_CASE})
    with pytest.raises(ValueError, match="evidence grade"):
        repaired.verify_against_source("lamotrigine")

    assert owner.component_id == "fixture"


def test_format_repair_cannot_claim_a_semantic_change() -> None:
    owner = OperationOwner(component_id="schema", display_name="Schema repair")

    with pytest.raises(ValidationError, match="format-only"):
        TraceChange(
            change_id="change-1",
            stage_id="schema-repair",
            operation_owner=owner,
            kind="format_repair",
            before_ref="/raw",
            after_ref="/structured",
            before_value="four per month",
            after_value={"count": 4, "period": "month"},
            clinical_meaning_changed=True,
            reason="Made the payload schema-compatible.",
        )
