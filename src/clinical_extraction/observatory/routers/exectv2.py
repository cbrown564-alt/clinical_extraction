"""ExECTv2 cached JSON routes for the Observatory."""

from __future__ import annotations

from fastapi import APIRouter

from clinical_extraction.observatory.cached_routes import cached_json_route
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import (
    cached_component_ablation_json,
    cached_component_transitions_json,
    cached_exectv2_runs_json,
    cached_reliability_scorecard_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.sf_inspection import (
    cached_sf_inspection_json,
)

router = APIRouter(tags=["exectv2"])


@router.get("/exectv2/runs")
def get_exectv2_runs():
    """Live ExECTv2 frontend dataset — parity with Gan's live registry/artifacts."""
    return cached_json_route(
        cached_exectv2_runs_json,
        error_detail="Failed to build ExECTv2 runs",
    )()


@router.get("/exectv2/reliability-scorecard")
def get_exectv2_reliability_scorecard():
    """Structured ExECTv2 reliability scorecard for the frontend view."""
    return cached_json_route(
        cached_reliability_scorecard_json,
        error_detail="Failed to build ExECTv2 reliability scorecard",
    )()


@router.get("/exectv2/component-ablation")
def get_exectv2_component_ablation():
    """Structured ExECTv2 layered component-impact replay for the frontend."""
    return cached_json_route(
        cached_component_ablation_json,
        error_detail="Failed to build ExECTv2 component ablation payload",
    )()


@router.get("/exectv2/component-transitions")
def get_exectv2_component_transitions():
    """Illustrative per-letter stage-transition examples for the Component Impact sidebar."""
    return cached_json_route(
        cached_component_transitions_json,
        error_detail="Failed to build ExECTv2 component transition examples",
    )()


@router.get("/exectv2/sf-inspection")
def get_exectv2_sf_inspection():
    """SeizureFrequency gold-vs-prediction inspection payload.

    Serves the scorer-faithful, per-letter Layer A (schema attributes) / Layer B
    (11 scoring components) detail the frontend ``/exectv2-sf-inspection`` route
    renders. The payload is built once per process and the faithfulness gate runs
    inside the builder, so drift surfaces as a 500 rather than a bad payload.
    """
    return cached_json_route(
        cached_sf_inspection_json,
        error_detail="Failed to build ExECTv2 SF inspection payload",
    )()
