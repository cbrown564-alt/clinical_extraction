import re

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
    apply_rule,
    validate_rule_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.rate import (
    PORTABLE_RATE_RULES,
)


def test_ablation_config_enables_every_rule_group_and_portability_by_default() -> None:
    config = AblationConfig()

    assert config.enabled_groups == frozenset(RuleGroup)
    assert config.enabled_portability == frozenset(Portability)
    assert config.disabled_rule_ids == frozenset()


def test_ablation_config_can_disable_group_portability_and_rule_id() -> None:
    config = AblationConfig(
        enabled_groups=frozenset({RuleGroup.PORTABLE_RATE_EXPRESSIONS}),
        enabled_portability=frozenset({Portability.SEIZURE_FREQUENCY}),
        disabled_rule_ids=frozenset({"rate.direct_count_per_period"}),
    )

    assert config.rule_is_enabled(
        rule_id="rate.every_n_interval",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )
    assert not config.rule_is_enabled(
        rule_id="rate.direct_count_per_period",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )
    assert not config.rule_is_enabled(
        rule_id="cluster.count",
        group=RuleGroup.CLUSTER_ARITHMETIC,
        portability=Portability.SEIZURE_FREQUENCY,
    )
    assert not config.rule_is_enabled(
        rule_id="gan.tc_shorthand",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.GAN2026_SPECIFIC,
    )


def test_rule_registry_validation_requires_unique_rule_ids_and_examples() -> None:
    spec = RuleSpec(
        rule_id="rate.example",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Example rate rule.",
        pattern=re.compile(r"twice weekly"),
        build=lambda _match, _context: None,
        examples=(RuleExample(text="Current seizures occur twice weekly."),),
    )

    validate_rule_registry((spec,))

    duplicate = RuleSpec(
        rule_id="rate.example",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Duplicate example rate rule.",
        pattern=re.compile(r"weekly"),
        build=lambda _match, _context: None,
        examples=(RuleExample(text="Weekly seizures continue."),),
    )
    missing_examples = RuleSpec(
        rule_id="rate.no_examples",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Undocumented rate rule.",
        pattern=re.compile(r"daily"),
        build=lambda _match, _context: None,
    )

    with pytest.raises(ValueError, match="Duplicate rule_id"):
        validate_rule_registry((spec, duplicate))
    with pytest.raises(ValueError, match="at least one example"):
        validate_rule_registry((missing_examples,))


def test_apply_rule_respects_ablation_config() -> None:
    spec = RuleSpec(
        rule_id="rate.example",
        group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Example rate rule.",
        pattern=re.compile(r"twice weekly"),
        build=lambda match, _context: match.group(0),
        examples=(RuleExample(text="Current seizures occur twice weekly."),),
    )
    context = ExtractionContext(text="Current seizures occur twice weekly.")

    assert apply_rule(spec, context, AblationConfig()) == ["twice weekly"]
    assert spec.apply(context, AblationConfig()) == ["twice weekly"]
    assert (
        spec.apply(
            context,
            AblationConfig(
                enabled_groups=frozenset({RuleGroup.CLUSTER_ARITHMETIC}),
            ),
        )
        == []
    )


def test_portable_rate_rule_registry_is_valid() -> None:
    validate_rule_registry(PORTABLE_RATE_RULES)
