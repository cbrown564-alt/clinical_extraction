"""Rule metadata for the Gan 2026 rules-only extract program.

The model-ledger rule catalogue is
``src/clinical_extraction/paper/rule_records.py`` and
``docs/research/paper/rule_catalogue_schema_format_post_2026-08-21.md``.
Same vocabulary, different program.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, is_dataclass, replace
from enum import StrEnum
from re import Match, Pattern
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .candidates import (
        RawCandidate,
    )

    RuleBuildResult: TypeAlias = RawCandidate | str | None
else:
    RuleBuildResult: TypeAlias = object

RuleBuilder: TypeAlias = Callable[[Match[str], "ExtractionContext"], RuleBuildResult]
ExclusionPredicate: TypeAlias = Callable[[Match[str], "ExtractionContext"], bool]


class RuleGroup(StrEnum):
    DATE_DURATION_UTILITIES = "date_duration_utilities"
    PORTABLE_RATE_EXPRESSIONS = "portable_rate_expressions"
    SEIZURE_FREE_NO_EVENT_ASSERTIONS = "seizure_free_no_event_assertions"
    CLUSTER_ARITHMETIC = "cluster_arithmetic"
    DIARY_LOG_AGGREGATION = "diary_log_aggregation"
    TEMPORAL_SELECTION = "temporal_selection"
    GAN_SHORTHAND = "gan_shorthand"
    BENCHMARK_REPAIR = "benchmark_repair"
    GOLD_NORMALIZATION_POLICY = "gold_normalization_policy"


class Portability(StrEnum):
    GENERAL = "general"
    CLINICAL_EPILEPSY = "clinical_epilepsy"
    SEIZURE_FREQUENCY = "seizure_frequency"
    GAN2026_SPECIFIC = "gan2026_specific"
    BENCHMARK_FORMAT = "benchmark_format"


@dataclass(frozen=True)
class AblationConfig:
    enabled_groups: frozenset[RuleGroup] = frozenset(RuleGroup)
    enabled_portability: frozenset[Portability] = frozenset(Portability)
    disabled_rule_ids: frozenset[str] = frozenset()

    def rule_is_enabled(
        self,
        *,
        rule_id: str,
        group: RuleGroup,
        portability: Portability,
    ) -> bool:
        return (
            group in self.enabled_groups
            and portability in self.enabled_portability
            and rule_id not in self.disabled_rule_ids
        )


@dataclass(frozen=True)
class ExtractionContext:
    text: str
    helpers: Mapping[str, object] | None = None

    def helper(self, name: str) -> object:
        if self.helpers is None or name not in self.helpers:
            raise KeyError(f"ExtractionContext helper is not available: {name}")
        return self.helpers[name]


@dataclass(frozen=True)
class RuleExample:
    text: str
    expected_label: str | None = None
    expected_evidence: str | None = None
    anti_example: bool = False
    note: str | None = None


@dataclass(frozen=True)
class RuleSpec:
    rule_id: str
    group: RuleGroup
    portability: Portability
    description: str
    pattern: Pattern[str]
    build: RuleBuilder
    exclude: tuple[ExclusionPredicate, ...] = ()
    examples: tuple[RuleExample, ...] = ()
    provenance: str | None = None

    def apply(
        self,
        context: ExtractionContext,
        ablation_config: AblationConfig,
    ) -> list[RuleBuildResult]:
        return apply_rule(self, context, ablation_config)


def _exclude_drop_reason(predicate: ExclusionPredicate) -> str:
    name = predicate.__name__
    if "medication" in name or "dose" in name:
        return "select.medication_dose_distractor_drop"
    if "historical" in name:
        return "select.historical_lead_in_drop"
    return "select.rule_exclude_drop"


def apply_rule(
    spec: RuleSpec,
    context: ExtractionContext,
    ablation_config: AblationConfig,
) -> list[RuleBuildResult]:
    if not ablation_config.rule_is_enabled(
        rule_id=spec.rule_id,
        group=spec.group,
        portability=spec.portability,
    ):
        return []
    built: list[RuleBuildResult] = []
    for match in spec.pattern.finditer(context.text):
        drop_reason: str | None = None
        for exclude in spec.exclude:
            if exclude(match, context):
                drop_reason = _exclude_drop_reason(exclude)
                break
        candidate = spec.build(match, context)
        if candidate is None:
            continue
        if (
            drop_reason is not None
            and is_dataclass(candidate)
            and hasattr(candidate, "deferred_drop")
        ):
            candidate = replace(candidate, deferred_drop=drop_reason)
        built.append(candidate)
    return built


def validate_rule_registry(specs: Sequence[RuleSpec]) -> None:
    seen_rule_ids: set[str] = set()
    for spec in specs:
        if spec.rule_id in seen_rule_ids:
            raise ValueError(f"Duplicate rule_id: {spec.rule_id}")
        seen_rule_ids.add(spec.rule_id)
        if not spec.rule_id.strip():
            raise ValueError("RuleSpec rule_id must be set")
        if not spec.description.strip():
            raise ValueError(f"RuleSpec {spec.rule_id} must have a description")
        if not spec.examples:
            raise ValueError(f"RuleSpec {spec.rule_id} must have at least one example")
