"""Compatibility API for the established Next.js clinical explorer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import evaluate_predictions
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.deterministic_canonical import (
    run_item,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.naming import active_pipeline_name
from clinical_extraction.trace_explorer.api.dependencies import (
    FrontendDataDependency,
    ReviewStoreDependency,
    TraceIndexDependency,
)
from clinical_extraction.trace_explorer.api.errors import (
    TraceExplorerError,
    aggregate_only,
    not_found,
)

router = APIRouter(tags=["frontend-compatibility"])


class AblationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled_groups: list[str] | None = None
    enabled_portability: list[str] | None = None
    disabled_rule_ids: list[str] = Field(default_factory=list)


class RunNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note_text: str = Field(min_length=1, max_length=2_000_000)
    pipeline: str = "rules"
    source_row_index: int = 0
    gold_label: str | None = None
    gold_reference: str | None = None
    ablation_config: AblationPayload = Field(default_factory=AblationPayload)


class RunAblationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    split: str = "validation"
    pipeline: str = "rules"
    limit: int | None = Field(default=None, ge=1, le=100)
    ablation_config: AblationPayload = Field(default_factory=AblationPayload)


class QualifiedReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attribute_review_id: str = Field(min_length=1)
    fact_id: str | None = None
    letter_id: str | None = None
    attribute_name: str | None = None
    attribute_value: str | None = None
    reviewer_id: str = Field(min_length=1, max_length=120)
    correctness: Literal["correct", "incorrect"]
    review_notes: str | None = Field(default=None, max_length=10_000)


class SemanticSupportReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_item_id: str = Field(min_length=1, max_length=1000)
    reviewer_id: str = Field(min_length=1, max_length=120)
    clinical_support: Literal["supported", "unsupported", "unclear"]
    review_notes: str | None = Field(default=None, max_length=10_000)

_SEMANTIC_SUPPORT_ALLOWED_VALUES = {
    "clinical_support": ["supported", "unsupported", "unclear"],
}


class GoldAuditDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset: Literal["gan2026", "exectv2"] = "gan2026"
    audit_id: str | None = None
    source_row_index: int | None = None
    split: str
    simple_class: str | None = None
    rq10_class: str | None = None
    notes: str | None = None
    corrected_gold_label: str | None = None
    benchmark_convention_flag: bool | None = None
    all_system_fail: bool | None = None
    exact_evidence_but_scorer_wrong: bool | None = None
    clinically_defensible_alternative: bool | None = None
    likely_gold_defect: bool | None = None
    assertion_status: str | None = None
    attribute_entailment: str | None = None
    fact_boundaries: str | None = None
    clinical_interpretation: str | None = None
    reviewer_rationale: str | None = None
    review_confidence: str | None = None
    timestamp: str | None = None
    auditor: str | None = None


class TagErrorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gold_category: str
    predicted_category: str
    purist_correct: bool | None = None
    pragmatic_correct: bool | None = None


class HardSliceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rows: list[dict[str, Any]]


@router.get("/health")
def health(index: TraceIndexDependency) -> dict[str, object]:
    return {"status": "ok", "index_ready": index.ready}


@router.get("/registry")
def registry(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("registry")


@router.get("/pipeline-families")
def pipeline_families(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("pipeline_families")


@router.get("/rules")
def rules(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("rules")


@router.get("/prompts")
def prompts(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("prompts")


@router.get("/prompts/{module_name:path}/template")
def prompt_template(module_name: str, data: FrontendDataDependency) -> dict[str, Any]:
    prompt = data.prompt_template(module_name)
    if prompt is None:
        raise not_found()
    return {
        **prompt,
        "system_hint": prompt.get("system_hint"),
        "user_hint": prompt.get("user_hint"),
        "output_schema_hint": prompt.get("output_schema_hint"),
        "build_prompt_signature": prompt.get("build_prompt_signature"),
    }


@router.get("/records/{split}")
def records(split: str, data: FrontendDataDependency) -> dict[str, Any]:
    _check_record_split(split)
    payload = data.records(split)
    if payload is None:
        raise not_found()
    return payload


@router.get("/records/{split}/{source_row_index}")
def record(split: str, source_row_index: int, data: FrontendDataDependency) -> dict[str, Any]:
    _check_record_split(split)
    payload = data.record(split, source_row_index)
    if payload is None:
        raise not_found()
    return payload


@router.get("/artifacts/{run_id}")
def artifact(
    run_id: str,
    data: FrontendDataDependency,
    artifact_path: str | None = None,
    limit: int | None = Query(default=None, ge=1, le=1000),
) -> dict[str, Any]:
    del artifact_path
    payload = data.artifact(run_id, limit=limit)
    if payload is None:
        raise not_found()
    return payload


@router.post("/run/note")
def run_note(request: RunNoteRequest) -> dict[str, Any]:
    # Active API name is ``rules``. Legacy inbound names remain accepted and
    # echoed only for the established historical client response contract.
    try:
        canonical_pipeline = active_pipeline_name(request.pipeline)
    except ValueError:
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed execution is disabled; inspect an indexed saved replay instead.",
        ) from None
    if canonical_pipeline != "rules":
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed execution is disabled; inspect an indexed saved replay instead.",
        ) from None
    result = run_item(_gan_record(request), _pipeline_configuration(request.ablation_config))
    return {
        "pipeline": canonical_pipeline,
        "source_row_index": request.source_row_index,
        "gold_label": request.gold_label or "unknown",
        "result": result.model_dump(mode="json"),
    }


@router.post("/run/ablation")
def run_ablation(request: RunAblationRequest, data: FrontendDataDependency) -> dict[str, Any]:
    if request.split == "test":
        raise aggregate_only()
    if request.split != "validation":
        raise not_found()
    try:
        canonical_pipeline = active_pipeline_name(request.pipeline)
    except ValueError:
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed ablation is disabled; use saved comparison artifacts.",
        ) from None
    if canonical_pipeline != "rules":
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed ablation is disabled; use saved comparison artifacts.",
        ) from None
    record_list = data.records("validation")
    if record_list is None:
        raise not_found()
    summaries = record_list.get("records")
    if not isinstance(summaries, list):
        raise not_found()
    selected = summaries[: request.limit] if request.limit is not None else summaries
    rows: list[dict[str, Any]] = []
    gold_frequencies: list[float] = []
    predicted_frequencies: list[float] = []
    config = _pipeline_configuration(request.ablation_config)
    for summary in selected:
        source_row_index = int(summary["source_row_index"])
        full_record = data.record("validation", source_row_index)
        if full_record is None:
            continue
        item = _gan_record_from_fixture(full_record)
        result = run_item(item, config)
        selection = result.diagnostics["final_selection"]
        predicted_frequency = float(selection["monthly_frequency"])
        gold_frequency = label_to_frequency_record(item.gold_label).monthly_frequency
        gold_frequencies.append(gold_frequency)
        predicted_frequencies.append(predicted_frequency)
        purist_predicted = str(map_purist(predicted_frequency))
        purist_gold = str(map_purist(gold_frequency))
        pragmatic_predicted = str(map_pragmatic(predicted_frequency))
        pragmatic_gold = str(map_pragmatic(gold_frequency))
        rows.append(
            {
                "source_row_index": source_row_index,
                "prediction_label": result.output.final_value,
                "gold_label": item.gold_label,
                "purist_predicted_category": purist_predicted,
                "purist_gold_category": purist_gold,
                "pragmatic_predicted_category": pragmatic_predicted,
                "pragmatic_gold_category": pragmatic_gold,
                "evidence_valid": bool(result.diagnostics["evidence_valid"]),
            }
        )
    return {
        "split": request.split,
        "pipeline": "rules",
        "row_count": len(rows),
        "ablation_config": request.ablation_config.model_dump(mode="json", exclude_none=True),
        "summary": {
            "total": len(rows),
            "purist": _frontend_metrics(gold_frequencies, predicted_frequencies, "purist"),
            "pragmatic": _frontend_metrics(gold_frequencies, predicted_frequencies, "pragmatic"),
        },
        "rows": rows,
    }


_STATIC_ROUTES = {
    "/exectv2/sf-inspection": "exectv2_sf_inspection",
    "/gan2026/component-ablation": "gan2026_component_ablation",
    "/gan2026/component-transitions": "gan2026_component_transitions",
    "/gold-noise/ledgers": "gold_noise_ledgers",
    "/gold-noise/gan-audit": "gold_noise_gan_audit",
    "/gold-noise/issues": "gold_noise_issues",
    "/gold-noise/hypotheses": "gold_noise_hypotheses",
    "/gold-noise/row": "gold_noise_row",
}


def _add_static_route(path: str, resource: str) -> None:
    def endpoint(data: FrontendDataDependency) -> dict[str, Any]:
        return data.named(resource)

    endpoint.__name__ = f"frontend_{resource}"
    router.add_api_route(path, endpoint, methods=["GET"])


for _path, _resource in _STATIC_ROUTES.items():
    _add_static_route(_path, _resource)


@router.get("/exectv2/component-ablation")
def exectv2_component_ablation_unavailable() -> None:
    raise HTTPException(
        status_code=404,
        detail=(
            "ExECT component-ablation ladder is not exposed on the supervisor path; "
            "retained evidence lives in experiment reports."
        ),
    )


@router.get("/exectv2/component-transitions")
def exectv2_component_transitions_unavailable() -> None:
    raise HTTPException(
        status_code=404,
        detail=(
            "ExECT component-transition examples are not exposed on the supervisor path; "
            "retained evidence lives in experiment reports."
        ),
    )


@router.get("/exectv2/runs")
def exectv2_runs(data: FrontendDataDependency) -> dict[str, Any]:
    return data.exectv2_catalog()


@router.get("/exectv2/runs/{run_id}")
def exectv2_run(run_id: str, data: FrontendDataDependency) -> dict[str, Any]:
    payload = data.exectv2_run(run_id)
    if payload is None:
        raise not_found()
    return payload


@router.get("/qualified-review/packets")
def qualified_review_packets(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    reviewer_id: str | None = Query(default=None, min_length=1, max_length=120),
) -> dict[str, Any]:
    payload = data.qualified_review_packets()
    decisions = reviews.list(_correctness_review_kind(reviewer_id)) if reviewer_id else []
    decided_ids = {str(item["attribute_review_id"]) for item in decisions}
    packets = payload.get("packets")
    if isinstance(packets, list):
        for packet in packets:
            if isinstance(packet, dict):
                packet["has_decision"] = bool(packet.get("has_decision")) or str(
                    packet.get("attribute_review_id")
                ) in decided_ids
        payload["decided"] = sum(bool(packet.get("has_decision")) for packet in packets)
    return payload


@router.get("/qualified-review/decisions")
def qualified_review_decisions(
    reviews: ReviewStoreDependency,
    reviewer_id: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    decisions = reviews.list(_correctness_review_kind(reviewer_id))
    return {
        "reviewer_id": reviewer_id,
        "decisions": decisions,
        "count": len(decisions),
        "blinded": True,
    }


@router.post("/qualified-review/decide")
def qualified_review_decide(
    decision: QualifiedReviewDecision,
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> dict[str, Any]:
    if decision.attribute_review_id not in data.qualified_review_ids():
        raise not_found()
    payload = decision.model_dump(mode="json", exclude_none=True)
    saved = reviews.save_revisioned(
        _correctness_review_kind(decision.reviewer_id),
        decision.attribute_review_id,
        payload,
    )
    return {"status": "saved", "decision": saved}


@router.get("/semantic-support-review/packets")
def semantic_support_review_packets(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    reviewer_id: str | None = Query(default=None, min_length=1, max_length=120),
) -> dict[str, Any]:
    payload = data.semantic_support_review_packets()
    decisions = (
        reviews.list(_semantic_support_review_kind(reviewer_id)) if reviewer_id else []
    )
    decided_ids = {str(item["review_item_id"]) for item in decisions}
    packets = payload["packets"]
    for packet in packets:
        packet["has_decision"] = str(packet["review_item_id"]) in decided_ids
    return {
        **payload,
        "protocol_version": "exectv2-semantic-support-review-v2",
        "blinded": True,
        "reviewer_id": reviewer_id,
        "total": len(packets),
        "decided": len(decided_ids),
        "allowed_values": _SEMANTIC_SUPPORT_ALLOWED_VALUES,
    }


@router.get("/semantic-support-review/decisions")
def semantic_support_review_decisions(
    reviews: ReviewStoreDependency,
    reviewer_id: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    decisions = reviews.list(_semantic_support_review_kind(reviewer_id))
    return {
        "reviewer_id": reviewer_id,
        "decisions": decisions,
        "count": len(decisions),
        "blinded": True,
    }


@router.post("/semantic-support-review/decide")
def semantic_support_review_decide(
    decision: SemanticSupportReviewDecision,
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> dict[str, Any]:
    if decision.review_item_id not in data.semantic_support_review_ids():
        raise not_found()
    saved = reviews.save_revisioned(
        _semantic_support_review_kind(decision.reviewer_id),
        decision.review_item_id,
        decision.model_dump(mode="json", exclude_none=True),
    )
    return {"status": "saved", "decision": saved}


@router.get("/semantic-support-review/export")
def semantic_support_review_export(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    reviewer_id: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    review_kind = _semantic_support_review_kind(reviewer_id)
    decisions = reviews.list(review_kind)
    revisions = reviews.revisions(review_kind)
    source = data.semantic_support_review_packets()
    return {
        "schema_version": "exectv2-semantic-support-review-export-v2",
        "protocol_version": "exectv2-semantic-support-review-v2",
        "reviewer_id": reviewer_id,
        "claim_boundary": source["claim_boundary"],
        "completion": {"decided": len(decisions), "total": len(source["packets"])},
        "decisions": decisions,
        "revisions": revisions,
    }


@router.get("/gold-audit/rows")
def gold_audit_rows(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    split: str = "validation",
    dataset: Literal["gan2026", "exectv2"] = "gan2026",
) -> dict[str, Any]:
    del split
    payload = data.gold_audit_rows(dataset)
    decisions = _gold_decisions(data, reviews, dataset)
    decided_ids = {_gold_decision_identity(item) for item in decisions}
    rows = payload.get("rows")
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict):
                row["has_decision"] = bool(row.get("has_decision")) or _gold_row_identity(
                    row
                ) in decided_ids
        payload["decided"] = sum(bool(row.get("has_decision")) for row in rows)
    return payload


@router.get("/gold-audit/decisions")
def gold_audit_decisions(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    split: str | None = None,
    dataset: Literal["gan2026", "exectv2"] = "gan2026",
) -> dict[str, Any]:
    del split
    decisions = _gold_decisions(data, reviews, dataset)
    return {"decisions": decisions, "count": len(decisions)}


@router.get("/gold-audit/next")
def gold_audit_next(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    split: str = "validation",
    dataset: Literal["gan2026", "exectv2"] = "gan2026",
) -> dict[str, Any]:
    rows = gold_audit_rows(data, reviews, split, dataset).get("rows")
    next_row = next(
        (row for row in rows if isinstance(row, dict) and not row.get("has_decision")),
        None,
    ) if isinstance(rows, list) else None
    return {
        "dataset": dataset,
        "split": split,
        "row": next_row,
        "message": None if next_row is not None else "All rows adjudicated.",
    }


@router.post("/gold-audit/decide")
def gold_audit_decide(
    decision: GoldAuditDecision,
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> dict[str, Any]:
    if decision.split == "test":
        raise aggregate_only()
    payload = decision.model_dump(mode="json", exclude_none=True)
    identity = _gold_decision_identity(payload)
    if identity not in data.gold_audit_ids(decision.dataset):
        raise not_found()
    saved = reviews.save(f"gold:{decision.dataset}", identity, payload)
    return {"status": "saved", "decision": saved}


@router.post("/tag-error")
def tag_error(request: TagErrorRequest) -> dict[str, Any]:
    if request.gold_category == request.predicted_category or request.purist_correct is True:
        return {"error_type": "correct", "severity": 0, "severity_level": "none"}
    if "unknown" in request.predicted_category:
        return {"error_type": "false_negative", "severity": 4, "severity_level": "significant"}
    if "unknown" in request.gold_category:
        return {"error_type": "false_positive", "severity": 4, "severity_level": "significant"}
    return {"error_type": "near_miss", "severity": 1, "severity_level": "near"}


@router.get("/error-taxonomy/schema")
def error_taxonomy_schema() -> dict[str, Any]:
    return {
        "error_types": [
            {"id": "correct", "description": "Predicted and gold categories agree."},
            {"id": "false_negative", "description": "A supported frequency was missed."},
            {
                "id": "false_positive",
                "description": "A frequency was predicted without gold support.",
            },
            {"id": "near_miss", "description": "Prediction and gold fall in adjacent bands."},
        ],
        "severity": {
            "description": "Ordinal impact of the category mismatch.",
            "levels": ["none", "near", "moderate", "significant", "severe"],
        },
    }


@router.get("/hard-slices/definitions")
def hard_slice_definitions() -> dict[str, Any]:
    return {"slices": _hard_slice_definitions()}


@router.post("/hard-slices/membership")
def hard_slice_membership(request: HardSliceRequest) -> dict[str, Any]:
    rows = []
    for row in request.rows:
        rows.append(
            {
                "source_row_index": row.get("source_row_index"),
                "hidden_families": list(row.get("hidden_families") or []),
            }
        )
    return {"rows": rows}


@router.get("/meta")
def meta() -> dict[str, Any]:
    return {
        "git": {"branch": None, "commit": None, "dirty": True, "remote_url": None},
        "observatory_version": "trace-explorer.v1",
        "timestamp": datetime.now(UTC).isoformat(),
    }


def _check_record_split(split: str) -> None:
    if split == "test":
        raise aggregate_only()
    if split != "validation":
        raise not_found()


def _pipeline_configuration(payload: AblationPayload) -> PipelineConfiguration:
    enabled_groups = (
        frozenset(RuleGroup(value) for value in payload.enabled_groups)
        if payload.enabled_groups is not None
        else frozenset(RuleGroup)
    )
    enabled_portability = (
        frozenset(Portability(value) for value in payload.enabled_portability)
        if payload.enabled_portability is not None
        else frozenset(Portability)
    )
    return PipelineConfiguration(
        architecture="rules",
        ablation_config=AblationConfig(
            enabled_groups=enabled_groups,
            enabled_portability=enabled_portability,
            disabled_rule_ids=frozenset(payload.disabled_rule_ids),
        ),
    )


def _gan_record(request: RunNoteRequest) -> GanRecord:
    return GanRecord(
        source_row_index=request.source_row_index,
        note_text=request.note_text,
        gold_label=request.gold_label or "unknown",
        gold_reference=request.gold_reference or "",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


def _gan_record_from_fixture(record: dict[str, Any]) -> GanRecord:
    return GanRecord(
        source_row_index=int(record["source_row_index"]),
        note_text=str(record["note_text"]),
        gold_label=str(record["gold_label"]),
        gold_reference=str(record["gold_reference"]),
        labels_match_all_categories=bool(record["labels_match_all_categories"]),
        quotes_ok_all_categories=bool(record["quotes_ok_all_categories"]),
        row_ok=bool(record["row_ok"]),
        raw=record,
    )


def _frontend_metrics(
    gold: list[float],
    predicted: list[float],
    method: Literal["purist", "pragmatic"],
) -> dict[str, Any]:
    metrics = evaluate_predictions(gold, predicted, method=method)["micro"]
    return {**metrics, "per_label": {}}


def _merge_decisions(
    seed: list[dict[str, Any]],
    local: list[dict[str, Any]],
    identity,
) -> list[dict[str, Any]]:
    merged = {identity(item): item for item in seed}
    merged.update({identity(item): item for item in local})
    return list(merged.values())


def _semantic_support_review_kind(reviewer_id: str) -> str:
    return f"semantic-support:{reviewer_id.strip()}"


def _correctness_review_kind(reviewer_id: str) -> str:
    return f"correctness:{reviewer_id.strip()}"


def _qualified_decisions(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> list[dict[str, Any]]:
    seed = data.qualified_review_decisions().get("decisions")
    return _merge_decisions(
        seed if isinstance(seed, list) else [],
        reviews.list("qualified"),
        lambda item: str(item["attribute_review_id"]),
    )


def _gold_decisions(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    dataset: Literal["gan2026", "exectv2"],
) -> list[dict[str, Any]]:
    seed = data.gold_audit_decisions(dataset).get("decisions")
    return _merge_decisions(
        seed if isinstance(seed, list) else [],
        reviews.list(f"gold:{dataset}"),
        _gold_decision_identity,
    )


def _gold_decision_identity(decision: dict[str, Any]) -> str:
    return str(decision.get("audit_id") or decision.get("source_row_index") or "missing")


def _gold_row_identity(row: dict[str, Any]) -> str:
    return str(row.get("audit_id") or row.get("source_row_index") or "missing")


def _hard_slice_definitions() -> list[dict[str, str]]:
    return [
        {
            "slice_name": "candidate_generation_rescue",
            "component_focus": "candidate generation",
            "membership_rule": "Purist-wrong rows first lost at candidate generation.",
            "primary_metric": "Candidate-recall rescue rate before final-label projection.",
        },
        {
            "slice_name": "projection_arbitration",
            "component_focus": "final projection",
            "membership_rule": "Purist-wrong rows first lost at projection.",
            "primary_metric": "Projection correction precision and selected-evidence validity.",
        },
    ]
