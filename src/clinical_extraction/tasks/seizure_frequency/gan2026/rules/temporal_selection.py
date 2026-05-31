from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

TEMPORAL_SELECTION_RULE_PREFIX = "temporal_selection."


def _noop_build(_match: re.Match[str], _context: ExtractionContext) -> None:
    return None


def _selection_rule(rule_id: str, description: str, example: str) -> RuleSpec:
    return RuleSpec(
        rule_id=f"{TEMPORAL_SELECTION_RULE_PREFIX}{rule_id}",
        group=RuleGroup.TEMPORAL_SELECTION,
        portability=Portability.SEIZURE_FREQUENCY,
        description=description,
        pattern=re.compile(r".*", re.DOTALL),
        build=_noop_build,
        examples=(RuleExample(text=example),),
        provenance="V1 final-selection priority rule.",
    )


TEMPORAL_SELECTION_RULES: tuple[RuleSpec, ...] = (
    _selection_rule(
        "frequency_current_summary",
        "Prefer frequency evidence with current-summary cues over lower-priority candidates.",
        "Current seizure frequency summary: 2 per month.",
    ),
    _selection_rule(
        "frequency_monthly_rate",
        "Rank ordinary normalized frequency candidates by monthly frequency.",
        "Current seizures are four times per day.",
    ),
    _selection_rule(
        "specific_current_multiple",
        "Prefer specific current unresolved-multiple evidence over generic multiple evidence.",
        "Several episodes per week are reported.",
    ),
    _selection_rule(
        "generic_unresolved_multiple",
        "Retain generic unresolved-multiple evidence below normalized frequencies.",
        "Seizures occur multiple times.",
    ),
    _selection_rule(
        "current_seizure_free",
        "Prefer current seizure-free assertions over generic seizure-free mentions.",
        "Seizure freedom continues.",
    ),
    _selection_rule(
        "generic_seizure_free",
        "Use generic seizure-free evidence below stronger current-control assertions.",
        "She remains seizure-free for two years.",
    ),
    _selection_rule(
        "trigger_conditioned_unknown",
        "Prefer trigger-conditioned unknown-frequency evidence over stale numeric rates.",
        "Events occur only when significantly short on sleep.",
    ),
    _selection_rule(
        "generic_unknown",
        "Use generic unknown-frequency evidence above no-reference fallback.",
        "Frequency remains unclear.",
    ),
    _selection_rule(
        "no_reference",
        "Use no-reference fallback only when no stronger candidate is available.",
        "No seizure-frequency evidence is present.",
    ),
)


def temporal_selection_rule_is_enabled(
    reason: str,
    ablation_config: AblationConfig,
    specs: Sequence[RuleSpec] = TEMPORAL_SELECTION_RULES,
) -> bool:
    rule_id = f"{TEMPORAL_SELECTION_RULE_PREFIX}{reason}"
    spec_by_id = {spec.rule_id: spec for spec in specs}
    spec = spec_by_id.get(rule_id)
    if spec is None:
        raise KeyError(f"Unknown temporal selection rule reason: {reason}")
    return ablation_config.rule_is_enabled(
        rule_id=spec.rule_id,
        group=spec.group,
        portability=spec.portability,
    )
