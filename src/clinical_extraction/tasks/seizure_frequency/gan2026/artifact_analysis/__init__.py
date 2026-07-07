"""Saved-artifact analysis and replay helpers for Gan 2026 experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseFAnalyzerSpec:
    """Official cluster-level analyzer created by repo-cleanup Phase F."""

    cluster: str
    module: str
    description: str
    survey_cluster_files_replaced: int


_PHASE_F_ANALYZER_REGISTRY: dict[str, PhaseFAnalyzerSpec] = {
    "ablation": PhaseFAnalyzerSpec(
        cluster="ablation",
        module="scoped_ablation_analyzer",
        description="Parameterized ablation metrics and reports.",
        survey_cluster_files_replaced=8,
    ),
    "boundary_seizure_free": PhaseFAnalyzerSpec(
        cluster="boundary_seizure_free",
        module="boundary_diagnostic",
        description="Boundary state and seizure-free diagnostics with named scopes.",
        survey_cluster_files_replaced=8,
    ),
    "candidate_state": PhaseFAnalyzerSpec(
        cluster="candidate_state",
        module="candidate_state_matrix",
        description="CandidateSet, union, and state-decision comparison matrices.",
        survey_cluster_files_replaced=11,
    ),
    "projection_render_scoring": PhaseFAnalyzerSpec(
        cluster="projection_render_scoring",
        module="projection_scoring",
        description="Projection/render/scoring/route/decision stage summaries.",
        survey_cluster_files_replaced=5,
    ),
}


def get_phase_f_analyzer_registry() -> dict[str, PhaseFAnalyzerSpec]:
    """Return the official Phase F cluster analyzer registry."""

    return dict(_PHASE_F_ANALYZER_REGISTRY)


def phase_f_completion_summary() -> dict[str, object]:
    """Return a compact machine-readable Phase F analyzer completion summary."""

    return {
        "phase": "F",
        "consolidated_analyzer_modules": len(_PHASE_F_ANALYZER_REGISTRY),
        "survey_cluster_files_replaced": sum(
            spec.survey_cluster_files_replaced for spec in _PHASE_F_ANALYZER_REGISTRY.values()
        ),
        "claim_boundary": "cluster-level analysis API; no scoring-policy change",
        "registry": {
            cluster: {
                "module": spec.module,
                "description": spec.description,
                "survey_cluster_files_replaced": spec.survey_cluster_files_replaced,
            }
            for cluster, spec in _PHASE_F_ANALYZER_REGISTRY.items()
        },
    }


__all__ = [
    "PhaseFAnalyzerSpec",
    "get_phase_f_analyzer_registry",
    "phase_f_completion_summary",
]
