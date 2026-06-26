"""ExECTv2 cached JSON routes for the Observatory."""

from __future__ import annotations

from fastapi import APIRouter

from clinical_extraction.observatory.cached_routes import cached_json_route
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import (
    cached_exectv2_runs_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (  # noqa: E501
    cached_component_ablation_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_transition_examples import (  # noqa: E501
    cached_component_transitions_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    cached_reliability_scorecard_json,
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
