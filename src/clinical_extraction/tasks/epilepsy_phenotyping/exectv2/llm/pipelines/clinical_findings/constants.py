"""Shared constants for the clinical-findings pipeline."""

from __future__ import annotations

from collections.abc import Mapping

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)

PROMPT_VERSION = "exectv2_llm_only_sf_clinical_findings_v0.19"
PIPELINE_FAMILY = "exectv2_llm_only_clinical_findings"
ENTITY_NAME = SEIZURE_FREQUENCY.name

_OUTPUT_LAYERS: tuple[str, ...] = ("format_projected", "cui_projected")
PLAN11_EVENT_STATE_ROUTE_VERSION = "exectv2_plan11_sf_event_state_route_v0.1"
PLAN11_EVENT_STATE_LAYER_LADDER: tuple[dict[str, str], ...] = (
    {
        "layer": "raw_event_frames",
        "owner": "llm",
        "allowed_behavior": "Event/state inventory, target status, operands, and evidence.",
        "claim_role": "Audit substrate for model-owned coverage and target selection.",
    },
    {
        "layer": "raw_findings",
        "owner": "llm",
        "allowed_behavior": "Final model-owned target findings.",
        "claim_role": "Primary clinical headline before deterministic adapters.",
    },
    {
        "layer": "schema_valid_findings",
        "owner": "deterministic_schema",
        "allowed_behavior": "Parse JSON, coerce scalar schema transport, drop invalid records.",
        "claim_role": "Transport health only.",
    },
    {
        "layer": "evidence_validated",
        "owner": "deterministic_validator",
        "allowed_behavior": "Exact source-substring evidence gate.",
        "claim_role": "Grounding gate.",
    },
    {
        "layer": "format_projected",
        "owner": "deterministic_adapter",
        "allowed_behavior": "Map emitted fields to ExECTv2 attributes without adding facts.",
        "claim_role": "Primary LLM-first scorer layer.",
    },
    {
        "layer": "cui_projected",
        "owner": "deterministic_benchmark_format",
        "allowed_behavior": "Attach CUI/CUIPhrase from the model-emitted phrase.",
        "claim_role": "Companion benchmark-format score only.",
    },
    {
        "layer": "certainty_projected",
        "owner": "deterministic_guideline_adapter",
        "allowed_behavior": "No-op sidecar for SeizureFrequency.",
        "claim_role": "Outside the model-owned SF headline.",
    },
    {
        "layer": "post_llm_state_policy",
        "owner": "deterministic_state_policy",
        "allowed_behavior": "Only named, predeclared post-LLM state policy actions.",
        "claim_role": "Declared sidecar; not hidden adapter behavior.",
    },
    {
        "layer": "benchmark_rendered",
        "owner": "deterministic_adapter",
        "allowed_behavior": "Render accepted mention dictionaries for the legacy scorer.",
        "claim_role": "Benchmark reproduction / continuity layer.",
    },
)
_DISALLOWED_MODEL_PROJECTION_FIELDS: frozenset[str] = frozenset(
    {"CUI", "CUIPhrase", "Certainty", "Negation"}
)

_SCALAR_FINDING_FIELDS: frozenset[str] = frozenset(
    {
        "text",
        "evidence",
        "clinical_kind",
        "frequency_statement_type",
        "source_role",
        "count",
        "count_low",
        "count_high",
        "period_count",
        "period_low",
        "period_high",
        "period_unit",
        "time_relation",
        "point_in_time",
        "day",
        "month",
        "year",
        "age_low",
        "age_high",
        "age_unit",
        "frequency_change",
        "confidence",
        "rationale",
    }
)

_SCALAR_EVENT_FRAME_FIELDS: frozenset[str] = _SCALAR_FINDING_FIELDS | frozenset(
    {
        "event_id",
        "seizure_phrase",
        "target_status",
        "statement_family",
        "finding_text",
    }
)

_TIME_RELATION_ALIASES: Mapping[str, str] = {
    "during": "During",
    "in": "During",
    "on": "During",
    "since": "Since",
    "after": "Since",
    "following": "Since",
    "from": "Since",
}

_POINT_IN_TIME_ALIASES: Mapping[str, str] = {
    "birthday": "Birthday",
    "birth day": "Birthday",
    "drug change": "DrugChange",
    "medication change": "DrugChange",
    "medicine change": "DrugChange",
    "dose change": "DrugChange",
    "last clinic": "LastClinic",
    "last appointment": "LastClinic",
    "last review": "LastClinic",
    "last month": "Last_Month",
    "last week": "Last_Week",
    "last year": "Last_Year",
    "surgery": "Surgery",
    "operation": "Surgery",
}

_FREQUENCY_CHANGE_ALIASES: Mapping[str, str] = {
    "decreased": "Decreased",
    "less frequent": "Decreased",
    "reduced": "Decreased",
    "better": "Decreased",
    "frequent": "Frequent",
    "increased": "Increased",
    "more frequent": "Increased",
    "worse": "Increased",
    "infrequent": "Infrequent",
    "rare": "Infrequent",
    "same": "Same",
    "unchanged": "Same",
    "stable": "Same",
}

_CLINICAL_KIND_VALUES: frozenset[str] = frozenset(
    {
        "frequency_rate",
        "seizure_free",
        "frequency_change",
        "dated_count",
        "last_event",
        "cluster_frequency",
        "other_frequency",
    }
)

_STATEMENT_TYPE_TO_KIND: Mapping[str, str] = {
    "header_count_since_anchor": "dated_count",
    "calendar_count": "dated_count",
    "calendar_occurrence_no_count": "dated_count",
    "recurrence_interval": "frequency_rate",
    "last_event_date": "last_event",
    "background_rate": "frequency_rate",
    "seizure_free_duration": "seizure_free",
    "current_control_no_duration": "seizure_free",
    "current_zero_no_duration": "seizure_free",
    "change_only": "frequency_change",
    "other_frequency": "other_frequency",
}
