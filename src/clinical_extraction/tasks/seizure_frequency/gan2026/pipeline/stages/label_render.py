"""Label rendering and formatting helpers for projection/render."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    ProjectionDecision,
)


def render_label(projection: ProjectionDecision) -> tuple[str | None, str, list[str]]:
    if projection.projected_label_semantics:
        return projection.projected_label_semantics, projection.projection_basis, []
    return None, projection.projection_basis, ["projection_semantics_missing"]


def rate_label(burden: NormalizedBurden) -> str | None:
    if burden.period_low is None or burden.period_high is None or burden.period_unit is None:
        return None
    if burden.count_low is None or burden.count_high is None:
        if burden.vague_count is None:
            return None
        return f"{burden.vague_count} per {format_period(burden)}"
    return f"{format_range(burden.count_low, burden.count_high)} per {format_period(burden)}"


def seizure_free_label(burden: NormalizedBurden) -> str | None:
    if (
        burden.seizure_free_duration_low is None
        or burden.seizure_free_duration_high is None
        or burden.seizure_free_duration_unit is None
    ):
        return None
    duration = format_range(
        burden.seizure_free_duration_low,
        burden.seizure_free_duration_high,
    )
    return f"seizure free for {duration} {burden.seizure_free_duration_unit}"


def format_period(burden: NormalizedBurden) -> str:
    assert burden.period_low is not None
    assert burden.period_high is not None
    assert burden.period_unit is not None
    if burden.period_low == burden.period_high == 1:
        return burden.period_unit
    return f"{format_range(burden.period_low, burden.period_high)} {burden.period_unit}"


def format_cluster_period(burden: NormalizedBurden) -> str:
    assert burden.cluster_period_low is not None
    assert burden.cluster_period_high is not None
    assert burden.cluster_period_unit is not None
    if burden.cluster_period_low == burden.cluster_period_high == 1:
        return burden.cluster_period_unit
    return (
        f"{format_range(burden.cluster_period_low, burden.cluster_period_high)} "
        f"{burden.cluster_period_unit}"
    )


def format_range(low: float, high: float) -> str:
    left = format_number(low)
    right = format_number(high)
    if left == right:
        return left
    return f"{left} to {right}"


def format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)
