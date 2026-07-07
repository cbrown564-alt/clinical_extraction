"""Cluster-frequency burden normalization."""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    ExtractedCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.burden.frequency import (
    _deterministic_label_from_source_phrase,
    _has_cluster_label,
    _parse_label_range,
    _rate_burden_from_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    _cluster_phrases,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
)


def _is_renderable_cluster_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.cluster_count_low is not None
        and burden.cluster_count_high is not None
        and burden.cluster_period_low is not None
        and burden.cluster_period_high is not None
        and burden.cluster_period_unit is not None
    )


def _cluster_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    text = "; ".join(_cluster_phrases(primary_candidates)) or source_phrase
    label = _deterministic_label_from_source_phrase(
        text,
        preferred_kind=DeterministicCandidateKind.CLUSTER_FREQUENCY,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_frequency_values_unparsed"
        ]
    burden, issues = _cluster_burden_from_label(label, source_phrase=source_phrase)
    return burden, issues


def _cluster_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    normalized = " ".join(label.lower().split())
    if not _has_cluster_label(normalized):
        burden, issues = _rate_burden_from_label(normalized, source_phrase=source_phrase)
        return (
            NormalizedBurden(
                cluster_count_low=burden.count_low,
                cluster_count_high=burden.count_high,
                cluster_period_low=burden.period_low,
                cluster_period_high=burden.period_high,
                cluster_period_unit=burden.period_unit,
                source_normalized_phrase=source_phrase,
            ),
            issues,
        )
    match = re.match(
        r"^(?P<count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"clusters?\s+per\s+"
        r"(?:(?P<period_count>\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+)?"
        r"(?P<period_unit>day|week|month|year),\s+"
        r"(?P<events>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"per\s+cluster$",
        normalized,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_label_values_unparsed"
        ]
    count_low, count_high, count_issue = _parse_label_range(match.group("count"))
    period_low, period_high, period_issue = _parse_label_range(match.group("period_count") or "1")
    events_low, events_high, events_issue = _parse_label_range(match.group("events"))
    issues = [issue for issue in (count_issue, period_issue, events_issue) if issue is not None]
    return (
        NormalizedBurden(
            cluster_count_low=count_low,
            cluster_count_high=count_high,
            cluster_period_low=period_low,
            cluster_period_high=period_high,
            cluster_period_unit=match.group("period_unit"),  # type: ignore[arg-type]
            events_per_cluster_low=events_low,
            events_per_cluster_high=events_high,
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )
