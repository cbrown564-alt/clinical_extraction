"""Stable observatory-facing facade for Gan 2026 cached report builders and registry readers.

Observatory routers should import from this module rather than deep-importing
``artifact_analysis/*`` monoliths or cross-task report modules. Both the live
API routes and static frontend mock generators can depend on this surface so
served data and committed dev fallbacks stay aligned.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    cached_gan_reliability_scorecard_json,
    cached_gan_reliability_scorecard_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.component_stage_ladder import (  # noqa: E501
    cached_component_stage_ladder_json,
    cached_component_stage_ladder_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.component_transition_examples import (  # noqa: E501
    cached_component_transitions_json,
    cached_component_transitions_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    load_run_registry,
)

__all__ = [
    "cached_component_stage_ladder_json",
    "cached_component_stage_ladder_payload",
    "cached_component_transitions_json",
    "cached_component_transitions_payload",
    "cached_gan_reliability_scorecard_json",
    "cached_gan_reliability_scorecard_payload",
    "load_run_registry",
]
