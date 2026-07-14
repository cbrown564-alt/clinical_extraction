"""Extraction-phase adapter — assembles Stack A RuleSpec lists from catalog + builders."""

from __future__ import annotations

from functools import lru_cache

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    RuleSpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.anchor import (
    ANCHOR_EXTRACT_IMPLS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_EXTRACT_IMPLS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.temporal import (
    TEMPORAL_EXTRACT_IMPLS,
)

from ...rules.extract_impl_types import (
    ExtractRuleImpl,
)
from ...rules.rate_builders import (
    RATE_EXTRACT_IMPLS,
)
from ...rules.seizure_free import (
    SEIZURE_FREE_EXTRACT_IMPLS,
)
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

_NAMED_RULE_IDS = {
    "ADVERBIAL_RULE": "rate.adverbial",
    "ARTICLE_SEIZURE_COUNT_RULE": "rate.article_seizure_count",
    "BETWEEN_RANGE_PER_PERIOD_RULE": "rate.between_range_per_period",
    "COUNT_IN_LAST_PERIOD_RULE": "rate.count_in_last_period",
    "COUNT_PER_FORTNIGHT_RULE": "rate.count_per_fortnight",
    "COUNT_PER_PERIOD_RULE": "rate.count_per_period",
    "EVERY_N_PERIODS_RULE": "rate.every_n_periods",
    "EVERY_PERIOD_RULE": "rate.every_period",
    "HEADER_CONTINUATION_RATE_RULE": "rate.header_continuation_rate",
    "N_TIMES_PER_PERIOD_RULE": "rate.n_times_per_period",
    "PERIOD_RANGE_RULE": "rate.period_range",
    "RANGE_EVERY_PERIOD_RULE": "rate.range_every_period",
    "RANGE_OF_SEIZURE_TERMS_RULE": "rate.range_of_seizure_terms",
    "RANGE_OVER_PERIOD_RULE": "rate.range_over_period",
    "RANGE_PER_PERIOD_RULE": "rate.range_per_period",
    "SEVERAL_TIMES_PER_PERIOD_RULE": "rate.several_times_per_period",
    "CONTROL_PHRASE_RULE": "sf.control_phrase",
    "NO_HAD_DURATION_RULE": "sf.no_had_duration",
    "SF_BARE_RULE": "sf.bare",
    "SF_WITH_DURATION_RULE": "sf.duration",
    "DECREASED_RULE": "change.decreased",
    "INCREASED_RULE": "change.increased",
    "SAME_RULE": "change.same",
    "DATE_MONTH_RULE": "temporal.date_month",
    "DATE_MY_RULE": "temporal.date_month_year",
    "LAST_EVENT_DATE_RULE": "temporal.last_event_date",
    "LAST_EVENT_AGO_RULE": "temporal.last_event_ago",
    "LAST_SEIZURE_DATE_RULE": "temporal.last_seizure_date",
    "PIT_SINCE_RULE": "temporal.point_in_time_since",
    "PIT_STANDALONE_DURING_RULE": "temporal.point_in_time_standalone_during",
    "SEIZURE_TERM_MONTH_YEAR_RULE": "temporal.seizure_term_month_year",
    "SEIZURE_TERM_YEAR_RULE": "temporal.seizure_term_year",
}

for _export_name, _rule_id in _NAMED_RULE_IDS.items():
    globals()[_export_name] = rule_by_id(_rule_id)

__all__ = [
    "ANCHOR_RULES",
    "CHANGE_RULES",
    "PERIOD_UNIT",
    "RATE_RULES",
    "SEIZURE_FREE_ANCHOR_RULE",
    "SEIZURE_FREE_RULES",
    "SEIZURE_TYPE_ANCHOR_RULE",
    "TEMPORAL_RULES",
    "rule_by_id",
    *_NAMED_RULE_IDS.keys(),
]
