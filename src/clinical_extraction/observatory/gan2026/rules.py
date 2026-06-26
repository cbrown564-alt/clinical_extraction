"""Deterministic rule catalog helpers for Observatory routes."""

from __future__ import annotations

from typing import Any

from clinical_extraction.observatory.models import TEMPORAL_SELECTION_RULES
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import RuleSpec
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.cluster import (
    CLUSTER_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.diary import (
    DIARY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.gan_shorthand import (
    GAN_SHORTHAND_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.rate import (
    PORTABLE_RATE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.seizure_free import (
    SEIZURE_FREE_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import BENCHMARK_REPAIR_RULES


def all_rule_specs() -> tuple[RuleSpec, ...]:
    return (
        *PORTABLE_RATE_RULES,
        *CLUSTER_RULES,
        *DIARY_RULES,
        *SEIZURE_FREE_RULES,
        *GAN_SHORTHAND_RULES,
        *TEMPORAL_SELECTION_RULES,
        *BENCHMARK_REPAIR_RULES,
    )


def rule_payload(spec: RuleSpec) -> dict[str, Any]:
    return {
        "rule_id": spec.rule_id,
        "group": spec.group.value,
        "portability": spec.portability.value,
        "description": spec.description,
        "regex_preview": spec.pattern.pattern,
        "provenance": spec.provenance,
        "examples": [rule_example_payload(example) for example in spec.examples],
        "has_exclusions": bool(spec.exclude),
    }


def rule_example_payload(example: Any) -> dict[str, Any]:
    return {
        "text": example.text,
        "expected_label": example.expected_label,
        "expected_evidence": example.expected_evidence,
        "anti_example": example.anti_example,
        "note": example.note,
    }
