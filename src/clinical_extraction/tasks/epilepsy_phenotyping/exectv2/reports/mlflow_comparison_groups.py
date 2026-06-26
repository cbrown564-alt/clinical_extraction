"""ExECTv2 MLflow parent/child comparison group definitions.

Experiment-specific grouping constants live here rather than in core so the
registry sync planner stays task-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MlflowComparisonGroup:
    """One parent/child MLflow comparison group backed by registry rows."""

    comparison_id: str
    child_run_ids: tuple[str, ...]
    parent_artifact_paths: tuple[str, ...]


SAME_CORE_DEV140_MLFLOW_GROUP = MlflowComparisonGroup(
    comparison_id="exectv2_same_core_model_swap_dev140_20260625",
    child_run_ids=(
        "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
        "exectv2_2call_no_sf_adjudicator_deepseek_dev140",
        "exectv2_2call_no_sf_adjudicator_qwen36_dev140",
        "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140",
    ),
    parent_artifact_paths=(
        "docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md",
        "experiments/exectv2_same_core_model_swap_dev140_20260625.json",
    ),
)
