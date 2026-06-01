from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

RepairFunction = Callable[[str], str]


@dataclass(frozen=True)
class BenchmarkRepairStep:
    rule_id: str
    description: str
    apply: RepairFunction
    group: RuleGroup = RuleGroup.BENCHMARK_REPAIR
    portability: Portability = Portability.BENCHMARK_FORMAT


@dataclass(frozen=True)
class BenchmarkRepairEvent:
    rule_id: str
    group: RuleGroup
    portability: Portability
    before: str
    after: str


@dataclass(frozen=True)
class BenchmarkRepairTrace:
    raw_label: str | None
    initial_label: str
    final_label: str
    events: tuple[BenchmarkRepairEvent, ...]


def benchmark_repair_rule(
    *,
    rule_id: str,
    description: str,
    apply: RepairFunction,
) -> RuleSpec:
    def build(match: re.Match[str], _context: ExtractionContext) -> str:
        return apply(match.group("label"))

    return RuleSpec(
        rule_id=rule_id,
        group=RuleGroup.BENCHMARK_REPAIR,
        portability=Portability.BENCHMARK_FORMAT,
        description=description,
        pattern=re.compile(r"\A(?P<label>.*)\Z", re.DOTALL),
        build=build,
        examples=(RuleExample(text="about twice weekly"),),
        provenance="Gan-compatible prediction-label repair.",
    )


def apply_benchmark_repair_rules(
    text: str,
    rules: Sequence[RuleSpec],
    ablation_config: AblationConfig,
) -> tuple[str, tuple[BenchmarkRepairEvent, ...]]:
    events: list[BenchmarkRepairEvent] = []
    current = text
    context = ExtractionContext(text=current)
    for rule in rules:
        if not ablation_config.rule_is_enabled(
            rule_id=rule.rule_id,
            group=rule.group,
            portability=rule.portability,
        ):
            continue
        match = rule.pattern.match(current)
        if match is None:
            continue
        updated_result = rule.build(match, context)
        if not isinstance(updated_result, str):
            raise TypeError(f"Benchmark repair rule {rule.rule_id} must return str")
        updated = updated_result
        if updated != current:
            events.append(
                BenchmarkRepairEvent(
                    rule_id=rule.rule_id,
                    group=rule.group,
                    portability=rule.portability,
                    before=current,
                    after=updated,
                )
            )
        current = updated
        context = ExtractionContext(text=current)
    return current, tuple(events)


def apply_benchmark_repair_steps(
    text: str,
    steps: Sequence[BenchmarkRepairStep],
) -> tuple[str, tuple[BenchmarkRepairEvent, ...]]:
    rules = tuple(
        benchmark_repair_rule(
            rule_id=step.rule_id,
            description=step.description,
            apply=step.apply,
        )
        for step in steps
    )
    return apply_benchmark_repair_rules(text, rules, AblationConfig())


def validate_benchmark_repair_steps(steps: Sequence[BenchmarkRepairStep]) -> None:
    seen_rule_ids: set[str] = set()
    for step in steps:
        if step.rule_id in seen_rule_ids:
            raise ValueError(f"Duplicate benchmark repair rule_id: {step.rule_id}")
        seen_rule_ids.add(step.rule_id)
        if not step.rule_id.strip():
            raise ValueError("BenchmarkRepairStep rule_id must be set")
        if not step.description.strip():
            raise ValueError(f"BenchmarkRepairStep {step.rule_id} needs a description")
        if step.group is not RuleGroup.BENCHMARK_REPAIR:
            raise ValueError(f"BenchmarkRepairStep {step.rule_id} must use benchmark_repair")
        if step.portability is not Portability.BENCHMARK_FORMAT:
            raise ValueError(f"BenchmarkRepairStep {step.rule_id} must be benchmark_format")
