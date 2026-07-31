from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clinical_extraction.core.evidence import (
    EvidenceGrade,
    grade_evidence,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.trace_explorer.policy import RowPolicy

TRACE_SCHEMA_VERSION: Literal["trace.v1"] = "trace.v1"
INDEX_SCHEMA_VERSION: Literal["trace-index.v1"] = "trace-index.v1"


class StageCategory(StrEnum):
    SOURCE = "source"
    MODEL = "model"
    FORMAT_REPAIR = "format_repair"
    DETERMINISTIC_SEMANTIC = "deterministic_semantic"
    EVIDENCE_VALIDATION = "evidence_validation"
    ASSEMBLY = "assembly"
    PROJECTION = "projection"
    SCORING = "scoring"


class StageStatus(StrEnum):
    NOT_RUN = "not_run"
    RUNNING = "running"
    PASSED = "passed"
    REPAIRED = "repaired"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class RuleCategory(StrEnum):
    GENERAL = "general"
    CLINICAL_EPILEPSY = "clinical_epilepsy"
    SEIZURE_FREQUENCY = "seizure_frequency"
    GAN2026_SPECIFIC = "gan2026_specific"
    BENCHMARK_FORMAT = "benchmark_format"


class ChangeKind(StrEnum):
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    SELECT = "select"
    SUPPRESS = "suppress"
    SPLIT = "split"
    MERGE = "merge"
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    FORMAT_REPAIR = "format_repair"
    PROJECT = "project"


class EvidenceRole(StrEnum):
    SELECTED = "selected"
    SUPPORTING = "supporting"
    REJECTED = "rejected"
    DIAGNOSTIC = "diagnostic"


class DiagnosticSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class OwnerKind(StrEnum):
    """Who performed a change.

    A change that alters clinical meaning must name a deterministic rule and
    rule category - unless the model itself made the change, which has no
    deterministic rule to name. Before this distinction existed a trace could
    not express "the model made a clinical selection", which is exactly the
    prediction-ownership misstatement reported in the 2026-07-30 pipeline
    understandability review.
    """

    MODEL = "model"
    DETERMINISTIC = "deterministic"
    SCORER = "scorer"


class OperationOwner(BaseModel):
    model_config = ConfigDict(frozen=True)

    component_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    owner_kind: OwnerKind = OwnerKind.DETERMINISTIC


class TraceDiagnostic(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: DiagnosticSeverity = DiagnosticSeverity.INFO


class EvidenceReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    citation: str
    start: int | None = Field(default=None, ge=0)
    end: int | None = Field(default=None, ge=0)
    grade: EvidenceGrade
    role: EvidenceRole
    finding_ids: tuple[str, ...] = ()
    stage_ids: tuple[str, ...] = ()
    repaired_citation: str | None = None
    repair_kind: str | None = None

    @model_validator(mode="after")
    def validate_offsets(self) -> EvidenceReference:
        if (self.start is None) != (self.end is None):
            raise ValueError("evidence start and end must be supplied together")
        if self.start is not None and self.end is not None and self.end < self.start:
            raise ValueError("evidence end must not precede start")
        return self

    def verify_against_source(self, source_text: str) -> None:
        actual_grade = grade_evidence(source_text, self.citation)
        if actual_grade is not self.grade:
            raise ValueError(
                f"evidence grade mismatch for {self.evidence_id}: "
                f"declared {self.grade.value}, computed {actual_grade.value}"
            )

        located = locate_evidence(source_text, self.citation)
        grounded = self.grade not in {EvidenceGrade.ABSENT, EvidenceGrade.EMPTY}
        if grounded and located != (self.start, self.end):
            raise ValueError(f"evidence offsets do not match source for {self.evidence_id}")
        if not grounded and (self.start is not None or self.end is not None):
            raise ValueError(f"ungrounded evidence cannot carry offsets for {self.evidence_id}")

        if grounded and self.start is not None and self.end is not None:
            matched = source_text[self.start : self.end]
            expected = repair_evidence_text_if_source_exact(self.citation, source_text)
            if matched != expected:
                raise ValueError(f"evidence offsets do not resolve citation for {self.evidence_id}")


class TraceChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    change_id: str = Field(min_length=1)
    stage_id: str = Field(min_length=1)
    operation_owner: OperationOwner
    kind: ChangeKind
    operation: str | None = None
    before_ref: str | None = None
    after_ref: str | None = None
    before_value: Any = None
    after_value: Any = None
    clinical_meaning_changed: bool | Literal["unknown"]
    deterministic_rule: str | None = None
    rule_category: RuleCategory | None = None
    evidence_ids: tuple[str, ...] = ()
    reason: str = Field(min_length=1)
    first_unrecoverable_component: str | None = None

    @model_validator(mode="after")
    def validate_change_category(self) -> TraceChange:
        if self.kind is ChangeKind.FORMAT_REPAIR and self.clinical_meaning_changed is not False:
            raise ValueError("format-only repair must state that clinical meaning is unchanged")
        if (
            self.clinical_meaning_changed is True
            and self.operation_owner.owner_kind is OwnerKind.DETERMINISTIC
            and (self.deterministic_rule is None or self.rule_category is None)
        ):
            raise ValueError("a deterministic semantic change requires its rule and rule category")
        if (
            self.operation_owner.owner_kind is OwnerKind.MODEL
            and self.deterministic_rule is not None
        ):
            raise ValueError("a model-owned change must not claim a deterministic rule")
        return self


class TraceStage(BaseModel):
    model_config = ConfigDict(frozen=True)

    stage_id: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    name: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    semantic_role: str = Field(min_length=1)
    category: StageCategory
    owner: OperationOwner
    rule_category: RuleCategory | None = None
    status: StageStatus
    diagnostics: tuple[TraceDiagnostic, ...] = ()
    input_refs: tuple[str, ...]
    output_ref: str
    inline_summary: dict[str, Any] | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    payload_truncated: bool = False
    payload_bytes: int | None = Field(default=None, ge=0)
    changes: tuple[TraceChange, ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    predecessor_stage_ids: tuple[str, ...] = ()
    successor_stage_ids: tuple[str, ...] = ()
    elapsed_ms: float | None = Field(default=None, ge=0)
    provider_usage: dict[str, int | float] | None = None

    @model_validator(mode="after")
    def validate_deterministic_stage(self) -> TraceStage:
        if self.category is StageCategory.DETERMINISTIC_SEMANTIC and self.rule_category is None:
            raise ValueError("deterministic semantic stages require a rule category")
        if self.category is StageCategory.FORMAT_REPAIR:
            if any(change.clinical_meaning_changed is not False for change in self.changes):
                raise ValueError("format repair stages may contain format-only changes only")
        if any(change.stage_id != self.stage_id for change in self.changes):
            raise ValueError("every change must name its containing stage")
        return self


class RunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(min_length=1)
    task: Literal["exectv2", "gan2026", "synthetic"]
    dataset: str = Field(min_length=1)
    split: str = Field(min_length=1)
    row_policy: RowPolicy
    method: Literal["rules", "llm", "llm_with_rules"]
    pipeline_family: str = Field(min_length=1)
    model: str | None = None
    model_route: str | None = None
    mode: str = "saved_output"
    prompt_version: str | None = None
    program_version: str | None = None
    profile: str | None = None
    repair_policy: str = Field(min_length=1)
    scorer: str = Field(min_length=1)
    replay_mode: str = Field(min_length=1)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_path: str = Field(min_length=1)
    artifact_timestamp: str | None = None
    run_state: Literal[
        "complete", "partial", "contaminated", "rejected", "illustrative", "integrity_failed"
    ]


class SourceRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(min_length=1)
    text: str
    character_count: int = Field(ge=0)
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_content_identity(self) -> SourceRecord:
        if self.character_count != len(self.text):
            raise ValueError("source character count does not match text")
        digest = hashlib.sha256(self.text.encode("utf-8")).hexdigest()
        if digest != self.text_sha256:
            raise ValueError("source text hash does not match text")
        return self


class FindingSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_id: str = Field(min_length=1)
    entity: str = Field(min_length=1)
    text: str
    normalized_concept: str | None = None
    assertion: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    producer: str = Field(min_length=1)
    fact_origin: str = Field(min_length=1)
    raw_surface: str | None = None
    evidence_status: str = Field(min_length=1)
    state: str = Field(min_length=1)
    selected: bool
    task_payload: dict[str, Any] = Field(default_factory=dict)


class ScoreView(BaseModel):
    model_config = ConfigDict(frozen=True)

    score_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    value: float | None = None
    display_value: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    status: str = Field(min_length=1)
    description: str = Field(min_length=1)


class TraceEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal["trace.v1"] = TRACE_SCHEMA_VERSION
    trace_id: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    run: RunMetadata
    source: SourceRecord
    stages: tuple[TraceStage, ...]
    findings: tuple[FindingSnapshot, ...]
    score_views: tuple[ScoreView, ...]
    diagnostics: tuple[TraceDiagnostic, ...] = ()

    @model_validator(mode="after")
    def validate_trace_graph_and_evidence(self) -> TraceEnvelope:
        stage_ids = {stage.stage_id for stage in self.stages}
        if len(stage_ids) != len(self.stages):
            raise ValueError("stage IDs must be unique")
        if [stage.sequence for stage in self.stages] != list(range(len(self.stages))):
            raise ValueError("stage sequence must be contiguous and ordered")

        for stage in self.stages:
            linked = set(stage.predecessor_stage_ids) | set(stage.successor_stage_ids)
            if not linked.issubset(stage_ids):
                raise ValueError("stage graph references an unknown stage")
            for evidence in stage.evidence:
                if evidence.source_id != self.source.source_id:
                    raise ValueError("evidence source ID does not match the trace source")
                evidence.verify_against_source(self.source.text)

        visited: set[str] = set()
        active: set[str] = set()
        by_id = {stage.stage_id: stage for stage in self.stages}

        def visit(stage_id: str) -> None:
            if stage_id in active:
                raise ValueError("stage graph must be acyclic")
            if stage_id in visited:
                return
            active.add(stage_id)
            for successor in by_id[stage_id].successor_stage_ids:
                visit(successor)
            active.remove(stage_id)
            visited.add(stage_id)

        for stage_id in stage_ids:
            visit(stage_id)
        return self


class LedgerRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    ledger_id: str
    sequence: int
    stage_id: str
    stage_name: str
    category: StageCategory
    owner: OperationOwner
    input_ref: str | None
    operation: str
    output_ref: str
    change_type: ChangeKind | None
    selected_evidence: tuple[EvidenceReference, ...]
    status: StageStatus
    diagnostics: tuple[TraceDiagnostic, ...]
    before_value: Any = None
    after_value: Any = None
    provenance: dict[str, Any] = Field(default_factory=dict)


class GraphNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    stage_id: str
    sequence: int
    name: str
    category: StageCategory
    owner: OperationOwner
    status: StageStatus
    input_summary: tuple[str, ...]
    output_summary: str
    evidence_count: int


class GraphEdge(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    target: str


class BuildManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal["trace-index.v1"] = INDEX_SCHEMA_VERSION
    build_id: str
    created_at: str
    artifact_hashes: dict[str, str]
    run_count: int
    trace_count: int
    record_count: int
    quarantined_run_count: int = 0
    diagnostics: tuple[TraceDiagnostic, ...] = ()
