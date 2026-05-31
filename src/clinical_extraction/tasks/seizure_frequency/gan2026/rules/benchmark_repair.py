from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    Portability,
    RuleGroup,
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


def apply_benchmark_repair_steps(
    text: str,
    steps: Sequence[BenchmarkRepairStep],
) -> tuple[str, tuple[BenchmarkRepairEvent, ...]]:
    events: list[BenchmarkRepairEvent] = []
    current = text
    for step in steps:
        updated = step.apply(current)
        if updated != current:
            events.append(
                BenchmarkRepairEvent(
                    rule_id=step.rule_id,
                    group=step.group,
                    portability=step.portability,
                    before=current,
                    after=updated,
                )
            )
        current = updated
    return current, tuple(events)


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
