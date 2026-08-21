"""Invariant-focused tests for gan2026 normalize governance."""


from clinical_extraction.tasks.seizure_frequency.gan2026.contract import (
    benchmark_prediction_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
    validate_rule_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    benchmark_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_RULES,
    BENCHMARK_REPAIR_STEPS,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS,
    repair_prediction_label,
    repair_prediction_label_with_trace,
)

validate_benchmark_repair_steps = benchmark_repair.validate_benchmark_repair_steps


def test_benchmark_repair_steps_are_valid_and_benchmark_format_only() -> None:
    validate_benchmark_repair_steps(BENCHMARK_REPAIR_STEPS)
    validate_benchmark_repair_steps(FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS)
    validate_rule_registry(BENCHMARK_REPAIR_RULES)
    validate_rule_registry(FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES)
    assert BENCHMARK_REPAIR_STEPS
    assert BENCHMARK_REPAIR_RULES
    assert FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
    assert FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
    assert len(FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS) < len(BENCHMARK_REPAIR_STEPS)
    assert {(step.group, step.portability) for step in BENCHMARK_REPAIR_STEPS} == {
        (RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)
    }
    assert {(rule.group, rule.portability) for rule in BENCHMARK_REPAIR_RULES} == {
        (RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)
    }


def test_benchmark_prediction_repair_owns_rule_tables() -> None:
    assert BENCHMARK_REPAIR_STEPS is benchmark_prediction_repair.BENCHMARK_REPAIR_STEPS
    assert BENCHMARK_REPAIR_RULES is benchmark_prediction_repair.BENCHMARK_REPAIR_RULES
    assert (
        FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
        is benchmark_prediction_repair.FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
    )
    assert (
        FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
        is benchmark_prediction_repair.FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
    )


def test_repair_prediction_label_trace_exposes_benchmark_repair_events() -> None:
    trace = repair_prediction_label_with_trace("about twice weekly")

    assert trace.final_label == "2 per week"
    assert repair_prediction_label("about twice weekly") == trace.final_label
    assert [event.rule_id for event in trace.events] == [
        "benchmark_repair.once_twice_thrice",
        "benchmark_repair.period_words",
        "benchmark_repair.drop_prediction_noise",
    ]
    assert all(event.group is RuleGroup.BENCHMARK_REPAIR for event in trace.events)
    assert all(event.portability is Portability.BENCHMARK_FORMAT for event in trace.events)


def test_repair_prediction_label_respects_rule_id_ablation() -> None:
    trace = repair_prediction_label_with_trace(
        "about twice weekly",
        AblationConfig(disabled_rule_ids=frozenset({"benchmark_repair.once_twice_thrice"})),
    )

    assert trace.final_label == "1 per week"
    assert "benchmark_repair.once_twice_thrice" not in {event.rule_id for event in trace.events}
