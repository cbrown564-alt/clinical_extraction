"""Rule metadata framework for the ExECTv2 deterministic extractor.

Follows the same structural pattern as
``tasks/seizure_frequency/gan2026/deterministic/rule_metadata.py`` but uses
ExECTv2-specific enums (exectv2_specific portability, SF-centric rule groups).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from re import Match, Pattern
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .candidates import AnchorCandidate, AttributeExtraction

    RuleBuildResult: TypeAlias = "AnchorCandidate | AttributeExtraction | None"
else:
    RuleBuildResult: TypeAlias = object

RuleBuilder: TypeAlias = Callable[[Match[str], "ExtractionContext"], RuleBuildResult]
ExclusionPredicate: TypeAlias = Callable[[Match[str], "ExtractionContext"], bool]


class RuleGroup(StrEnum):
    ANCHOR_PHRASE = "anchor_phrase"
    RATE_EXPRESSIONS = "rate_expressions"
    SEIZURE_FREE = "seizure_free"
    FREQUENCY_CHANGE = "frequency_change"
    TEMPORAL_ANCHOR = "temporal_anchor"


class Portability(StrEnum):
    GENERAL = "general"
    CLINICAL_EPILEPSY = "clinical_epilepsy"
    SEIZURE_FREQUENCY = "seizure_frequency"
    EXECTV2_SPECIFIC = "exectv2_specific"
    BENCHMARK_FORMAT = "benchmark_format"


@dataclass(frozen=True)
class AblationConfig:
    enabled_groups: frozenset[RuleGroup] = frozenset(RuleGroup)
    enabled_portability: frozenset[Portability] = frozenset(Portability)
    disabled_rule_ids: frozenset[str] = frozenset()

    def rule_is_enabled(self, *, rule_id: str, group: RuleGroup, portability: Portability) -> bool:
        return (
            group in self.enabled_groups
            and portability in self.enabled_portability
            and rule_id not in self.disabled_rule_ids
        )


DEFAULT_ABLATION = AblationConfig()


@dataclass(frozen=True)
class ExtractionContext:
    text: str
    helpers: Mapping[str, object] | None = None


@dataclass(frozen=True)
class RuleExample:
    text: str
    expected_evidence: str | None = None
    expected_attributes: Mapping[str, str] | None = None
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

    def apply(self, context: ExtractionContext, ablation: AblationConfig) -> list[RuleBuildResult]:
        if not ablation.rule_is_enabled(
            rule_id=self.rule_id, group=self.group, portability=self.portability
        ):
            return []
        built: list[RuleBuildResult] = []
        for match in self.pattern.finditer(context.text):
            if any(excl(match, context) for excl in self.exclude):
                continue
            candidate = self.build(match, context)
            if candidate is not None:
                built.append(candidate)
        return built


def apply_rules(
    specs: list[RuleSpec],
    text: str,
    ablation: AblationConfig = DEFAULT_ABLATION,
) -> list[object]:
    context = ExtractionContext(text=text)
    results: list[object] = []
    for spec in specs:
        results.extend(spec.apply(context, ablation))
    return results


def validate_rule_registry(specs: list[RuleSpec]) -> None:
    seen: set[str] = set()
    for spec in specs:
        if spec.rule_id in seen:
            raise ValueError(f"Duplicate rule_id: {spec.rule_id!r}")
        seen.add(spec.rule_id)
        if not spec.examples:
            raise ValueError(f"RuleSpec {spec.rule_id!r} must have at least one example")
