"""Gan 2026 execution, records, rules, and cached analysis routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from clinical_extraction.observatory.cached_routes import cached_json_route
from clinical_extraction.observatory.gan2026 import (
    all_rule_specs,
    classify_error,
    load_split_records,
    prompt_payload,
    prompt_template_payload,
    request_record,
    rule_payload,
)
from clinical_extraction.observatory.helpers import require_supported_pipeline
from clinical_extraction.observatory.models import (
    ATLAS_HARD_SLICE_DEFINITIONS,
    PROMPT_MODULES,
    HardSliceMembershipRequest,
    RunAblationRequest,
    RunNoteRequest,
    TagErrorRequest,
    classify_hidden_families,
)
from clinical_extraction.observatory.responses import (
    HardSliceDefinitionsResponse,
    HardSliceMembershipResponse,
    HardSliceMembershipRow,
    PromptsResponse,
    RecordDetailResponse,
    RecordPreview,
    RecordsListResponse,
    RulesResponse,
    RunAblationResponse,
    RunAblationSummary,
    RunNoteResponse,
    TagErrorResponse,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import evaluate_predictions
from clinical_extraction.tasks.seizure_frequency.gan2026.frontend_review import (
    cached_component_stage_ladder_json,
    cached_gan_reliability_scorecard_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.frontend_review import (
    cached_component_transitions_json as cached_gan_component_transitions_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1

router = APIRouter(tags=["gan2026"])


def _settings(request: Request):
    return request.app.state.observatory_settings


@router.get("/gan2026/reliability-scorecard")
def get_gan2026_reliability_scorecard():
    """Structured Gan reliability scorecard for the frontend view."""
    return cached_json_route(
        cached_gan_reliability_scorecard_json,
        error_detail="Failed to build Gan reliability scorecard",
    )()


@router.get("/gan2026/component-ablation")
def get_gan2026_component_ablation():
    """Replay-only Gan component stage-ladder for the frontend view."""
    return cached_json_route(
        cached_component_stage_ladder_json,
        error_detail="Failed to build Gan component ablation payload",
    )()


@router.get("/gan2026/component-transitions")
def get_gan2026_component_transitions():
    """Illustrative per-note stage label trajectories for the Component Impact sidebar."""
    return cached_json_route(
        cached_gan_component_transitions_json,
        error_detail="Failed to build Gan component transition examples",
    )()


@router.post("/run/note", response_model=RunNoteResponse)
def run_note(request_body: RunNoteRequest) -> RunNoteResponse:
    require_supported_pipeline(request_body.pipeline)
    record = request_record(request_body)
    result = Gan2026PipelineV1(request_body.ablation_config.to_domain()).run(record)
    return RunNoteResponse(
        pipeline=request_body.pipeline,
        source_row_index=record.source_row_index,
        gold_label=record.gold_label,
        result=result.model_dump(mode="json"),
    )


@router.post("/run/ablation", response_model=RunAblationResponse)
def run_ablation(request_body: RunAblationRequest, request: Request) -> RunAblationResponse:
    settings = _settings(request)
    require_supported_pipeline(request_body.pipeline)
    records = load_split_records(settings, request_body.split)
    if request_body.limit is not None:
        records = records[: request_body.limit]
    pipeline = Gan2026PipelineV1(request_body.ablation_config.to_domain())
    rows = []
    predictions = []
    references = []
    for record in records:
        result = pipeline.run(record)
        final_selection = result.diagnostics["final_selection"]
        predicted_label = str(final_selection["final_label"])
        predicted_frequency = label_to_frequency_record(predicted_label).monthly_frequency
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "prediction_label": predicted_label,
                "prediction_monthly_frequency": predicted_frequency,
                "gold_label": record.gold_label,
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "evidence_valid": bool(result.diagnostics.get("evidence_valid")),
                "diagnostics": result.diagnostics,
                "purist_predicted_category": map_purist(predicted_frequency),
                "purist_gold_category": map_purist(record.gold_monthly_frequency),
                "pragmatic_predicted_category": map_pragmatic(predicted_frequency),
                "pragmatic_gold_category": map_pragmatic(record.gold_monthly_frequency),
            }
        )
        predictions.append(predicted_frequency)
        references.append(record.gold_monthly_frequency)
    return RunAblationResponse(
        split=request_body.split,
        pipeline=request_body.pipeline,
        row_count=len(rows),
        ablation_config=request_body.ablation_config.model_dump(mode="json"),
        summary=RunAblationSummary(
            total=len(rows),
            purist=evaluate_predictions(references, predictions, method="purist"),
            pragmatic=evaluate_predictions(references, predictions, method="pragmatic"),
        ),
        rows=rows,
    )


@router.get("/rules", response_model=RulesResponse)
def rules() -> RulesResponse:
    specs = all_rule_specs()
    return RulesResponse(
        groups=[group.value for group in RuleGroup],
        portability=[portability.value for portability in Portability],
        rules=[rule_payload(spec) for spec in specs],
    )


@router.get("/prompts", response_model=PromptsResponse)
def prompts() -> PromptsResponse:
    return PromptsResponse(prompts=[prompt_payload(module_name) for module_name in PROMPT_MODULES])


@router.get("/records/{split_name}", response_model=RecordsListResponse)
def records(split_name: str, request: Request) -> RecordsListResponse:
    settings = _settings(request)
    split_records = load_split_records(settings, split_name)
    return RecordsListResponse(
        split=split_name,
        count=len(split_records),
        records=[
            RecordPreview(
                source_row_index=r.source_row_index,
                gold_label=r.gold_label,
                gold_reference=r.gold_reference,
                row_ok=r.row_ok,
                note_preview=r.note_text[:200].replace("\n", " "),
            )
            for r in split_records
        ],
    )


@router.get("/records/{split_name}/{source_row_index}", response_model=RecordDetailResponse)
def record(split_name: str, source_row_index: int, request: Request) -> RecordDetailResponse:
    settings = _settings(request)
    split_records = load_split_records(settings, split_name)
    for r in split_records:
        if r.source_row_index == source_row_index:
            return RecordDetailResponse(
                split=split_name,
                source_row_index=r.source_row_index,
                gold_label=r.gold_label,
                gold_reference=r.gold_reference,
                row_ok=r.row_ok,
                note_text=r.note_text,
                labels_match_all_categories=r.labels_match_all_categories,
                quotes_ok_all_categories=r.quotes_ok_all_categories,
            )
    raise HTTPException(
        status_code=404,
        detail=f"Record {source_row_index} not found in split {split_name}",
    )


@router.get("/error-taxonomy/schema")
def error_taxonomy_schema() -> dict[str, Any]:
    return {
        "error_types": [
            {"id": "correct", "description": "Prediction exactly matches gold standard."},
            {
                "id": "false_negative",
                "description": ("Predicted no-seizure/unknown when note describes a frequency."),
            },
            {
                "id": "false_positive",
                "description": ("Predicted a frequency when gold is no-seizure/unknown."),
            },
            {"id": "over_estimate", "description": "Predicted higher frequency than gold."},
            {"id": "under_estimate", "description": "Predicted lower frequency than gold."},
            {"id": "near_miss", "description": "Off by exactly one category bucket."},
        ],
        "severity": {
            "description": "Absolute magnitude delta between gold and predicted category.",
            "levels": ["none", "near", "moderate", "significant", "severe"],
        },
    }


@router.post("/tag-error", response_model=TagErrorResponse)
def tag_error(request_body: TagErrorRequest) -> TagErrorResponse:
    return TagErrorResponse.model_validate(
        classify_error(
            request_body.gold_category,
            request_body.predicted_category,
            request_body.purist_correct,
        )
    )


@router.get("/hard-slices/definitions", response_model=HardSliceDefinitionsResponse)
def hard_slice_definitions() -> HardSliceDefinitionsResponse:
    return HardSliceDefinitionsResponse(
        slices=[dict(definition) for definition in ATLAS_HARD_SLICE_DEFINITIONS],
    )


@router.post("/hard-slices/membership", response_model=HardSliceMembershipResponse)
def hard_slice_membership(request_body: HardSliceMembershipRequest) -> HardSliceMembershipResponse:
    results = []
    for row in request_body.rows:
        note_text = str(row.get("note_text", ""))
        gold_label = str(row.get("gold_label", ""))
        predicted_label = str(row.get("predicted_label", ""))
        families = classify_hidden_families(
            note_text=note_text,
            gold_label=gold_label,
            predicted_label=predicted_label,
        )
        results.append(
            HardSliceMembershipRow(
                source_row_index=row.get("source_row_index"),
                hidden_families=list(families),
            )
        )
    return HardSliceMembershipResponse(rows=results)


@router.get("/prompts/{module_name}/template")
def prompt_template(module_name: str) -> dict[str, Any]:
    if module_name not in PROMPT_MODULES:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown prompt module: {module_name!r}. Expected one of {list(PROMPT_MODULES)}."
            ),
        )
    return prompt_template_payload(module_name)
