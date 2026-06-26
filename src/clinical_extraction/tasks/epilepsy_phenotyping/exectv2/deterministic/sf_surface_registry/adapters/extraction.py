"""Extraction-phase adapter — assembles Stack A RuleSpec lists from catalog + builders."""
from __future__ import annotations

from functools import lru_cache

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import RuleSpec
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.anchor import ANCHOR_EXTRACT_IMPLS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import CHANGE_EXTRACT_IMPLS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.extract_impl_types import ExtractRuleImpl
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.rate_builders import RATE_EXTRACT_IMPLS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.seizure_free import SEIZURE_FREE_EXTRACT_IMPLS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.temporal import TEMPORAL_EXTRACT_IMPLS

from ..extract_catalog import ExtractCatalogEntry, extract_rules_for_set, load_extract_catalog
from ..patterns import PERIOD_UNIT

_EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
    **ANCHOR_EXTRACT_IMPLS,
    **RATE_EXTRACT_IMPLS,
    **SEIZURE_FREE_EXTRACT_IMPLS,
    **CHANGE_EXTRACT_IMPLS,
    **TEMPORAL_EXTRACT_IMPLS,
}


def _resolve_exclude(entry: ExtractCatalogEntry, impl: ExtractRuleImpl) -> tuple:
    if entry.exclude:
        by_name = {fn.__name__: fn for fn in impl.exclude}
        return tuple(by_name[name] for name in entry.exclude)
    return impl.exclude


def _build_rule_spec(entry: ExtractCatalogEntry) -> RuleSpec:
    impl = _EXTRACT_IMPLS[entry.rule_id]
    return RuleSpec(
        rule_id=entry.rule_id,
        group=entry.group,
        portability=entry.portability,
        description=entry.description,
        pattern=impl.pattern,
        build=impl.build,
        exclude=_resolve_exclude(entry, impl),
        examples=entry.examples,
        provenance=entry.provenance,
    )


@lru_cache(maxsize=8)
def _rule_set(rule_set: str) -> tuple[RuleSpec, ...]:
    return tuple(_build_rule_spec(entry) for entry in extract_rules_for_set(rule_set))


def rule_by_id(rule_id: str) -> RuleSpec:
    for entry in load_extract_catalog():
        if entry.rule_id == rule_id:
            return _build_rule_spec(entry)
    raise KeyError(rule_id)


ANCHOR_RULES: list[RuleSpec] = list(_rule_set("anchor"))
RATE_RULES: list[RuleSpec] = list(_rule_set("rate"))
SEIZURE_FREE_RULES: list[RuleSpec] = list(_rule_set("seizure_free"))
CHANGE_RULES: list[RuleSpec] = list(_rule_set("change"))
TEMPORAL_RULES: list[RuleSpec] = list(_rule_set("temporal"))

SEIZURE_TYPE_ANCHOR_RULE = rule_by_id("anchor.seizure_type_phrase")
SEIZURE_FREE_ANCHOR_RULE = rule_by_id("anchor.seizure_free_phrase")

__all__ = [
    "ANCHOR_RULES", "CHANGE_RULES", "PERIOD_UNIT", "RATE_RULES",
    "SEIZURE_FREE_ANCHOR_RULE", "SEIZURE_FREE_RULES", "SEIZURE_TYPE_ANCHOR_RULE",
    "TEMPORAL_RULES", "rule_by_id",
]
