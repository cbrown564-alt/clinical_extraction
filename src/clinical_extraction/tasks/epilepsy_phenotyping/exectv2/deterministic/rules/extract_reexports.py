"""Lazy re-exports of assembled RuleSpec objects for backward-compatible imports."""
from __future__ import annotations

import importlib
from typing import Any

_LIST_NAMES = frozenset({
    "ANCHOR_RULES", "CHANGE_RULES", "RATE_RULES", "SEIZURE_FREE_RULES", "TEMPORAL_RULES",
})
_NAMED_RULE_IDS = {
    "SEIZURE_TYPE_ANCHOR_RULE": "anchor.seizure_type_phrase",
    "SEIZURE_FREE_ANCHOR_RULE": "anchor.seizure_free_phrase",
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
_EXTRACTION_MODULE = (
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic."
    "sf_surface_registry.adapters.extraction"
)


def extract_reexport(name: str) -> Any:
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)
    if name not in _LIST_NAMES and name not in _NAMED_RULE_IDS:
        raise AttributeError(name)
    extraction = importlib.import_module(_EXTRACTION_MODULE)
    if name in _LIST_NAMES:
        return getattr(extraction, name)
    return extraction.rule_by_id(_NAMED_RULE_IDS[name])
