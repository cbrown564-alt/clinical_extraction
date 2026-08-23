from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
    repair_mode_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence.codebook_encode import (
    CODEBOOK_ENCODE_RULE_IDS,
    repair_codebook_label_with_evidence,
)


def _repair(
    label: str,
    evidence: str,
    *,
    kinds: tuple[str, ...] = ("frequency_rate",),
    context: str = "Clinic Date: 02 October 2025",
    enabled: frozenset[str] | None = None,
) -> str:
    return repair_codebook_label_with_evidence(
        label,
        evidence,
        selected_event_kinds=kinds,
        context_text=context,
        enabled_rule_ids=enabled,
    ).final_label


def test_codebook_encode_preserves_already_encoded_labels() -> None:
    assert _repair(
        "9 per 3 month",
        "a seizure to date in September, five in August and 3 in July",
    ) == "9 per 3 month"
    assert _repair(
        "5 cluster per month, multiple per cluster",
        "clusters of absence seizures on five days each month",
        kinds=("cluster_frequency",),
    ) == "5 cluster per month, multiple per cluster"
    assert _repair("unknown", "several episodes over the past six weeks") == "unknown"
    assert _repair(
        "1 cluster per 4 to 5 week, multiple per cluster",
        "events group over several days roughly every four to five weeks; "
        "the number in each group was not logged",
        kinds=("cluster_frequency",),
    ) == "1 cluster per 4 to 5 week, multiple per cluster"
    assert _repair(
        "seizure free for a vague duration",
        "No seizures have been noted since the previous review",
        kinds=("seizure_free",),
    ) == "seizure free for a vague duration"


def test_codebook_encode_sums_complete_month_sequences() -> None:
    assert _repair(
        "1 per month",
        "He experienced a seizure so far in Sep, 1 in Aug, and three in Jul",
    ) == "5 per 3 month"
    assert _repair(
        "seizure free for 1 month",
        "She noted no seizures in June, four in May, and four in April",
    ) == "8 per 3 month"
    assert _repair(
        "9 per 3 month",
        "He recorded a seizure to date in September, five in August and 3 in July",
    ) == "9 per 3 month"


def test_codebook_encode_repairs_selected_diary_forms() -> None:
    assert _repair(
        "unknown",
        "Seizure events on 06-03, 06-13, 09-23 as recorded in the diary",
        kinds=("last_event_only",),
    ) == "3 per 3 month"
    assert _repair(
        "0 to 2 per month",
        "2019: Aug x0, Sep x0, Oct x1, Nov x0, Dec x1. "
        "2020: Jan x0, Feb x2, Mar x0, Apr x1, May x0, Jun x1, Jul x0",
    ) == "6 per 12 month"


def test_codebook_encode_repairs_high_precision_unknown_forms() -> None:
    assert _repair("unknown", "Electrographic seizures frequent on EEG (~9/h)") == (
        "multiple per day"
    )
    assert _repair("unknown", "a single very brief event last month") == "1 per month"
    assert _repair(
        "unknown",
        "brief absences occurring on most weekdays",
        kinds=("cluster_frequency",),
    ) == "multiple per week"


def test_codebook_encode_completes_cluster_cadence() -> None:
    assert _repair(
        "unknown, 5 per cluster",
        "clusters arise on several evenings per fortnight, roughly 5 spells per cluster",
        kinds=("cluster_frequency",),
    ) == "multiple cluster per 2 week, 5 per cluster"
    assert _repair(
        "unknown",
        "Seizure diary shows 2 cluster days this month; sizes unrecorded",
        kinds=("cluster_frequency",),
    ) == "2 cluster per month, multiple per cluster"


def test_codebook_encode_prefers_explicit_cluster_interval_over_secondary_daily_phrase() -> None:
    assert _repair(
        "unknown, multiple per cluster",
        "seizures occur in clusters, generally spaced four to five days apart, "
        "though brief periods of daily seizures have been reported",
        kinds=("cluster_frequency",),
    ) == "1 per 4 to 5 day"
    assert _repair(
        "unknown",
        "clusters generally spaced 5 days apart, though brief periods of daily "
        "seizures have been reported",
        kinds=("unknown_frequency",),
    ) == "1 per 5 day"


def test_codebook_encode_repairs_year_to_date_and_unknown_wrapper() -> None:
    assert _repair(
        "5 per year",
        "only five seizures so far this year",
        context="Clinic Date: 14 May 2025",
    ) == "5 per 5 month"
    assert _repair(
        "unknown, 1 per day",
        "clusters of jumps almost 1 per day",
        kinds=("cluster_frequency",),
    ) == "1 per day"


def test_codebook_encode_rules_are_independently_switchable() -> None:
    evidence = "Electrographic seizures frequent on EEG (~9/h)"
    all_rules = _repair("unknown", evidence)
    no_rules = _repair("unknown", evidence, enabled=frozenset())
    hourly_only = _repair(
        "unknown",
        evidence,
        enabled=frozenset({"gan.encode.codebook.hourly_rate"}),
    )
    assert all_rules == "multiple per day"
    assert no_rules == "unknown"
    assert hourly_only == "multiple per day"
    assert "gan.encode.codebook.hourly_rate" in CODEBOOK_ENCODE_RULE_IDS


def test_codebook_encode_trace_records_the_rule() -> None:
    trace = repair_codebook_label_with_evidence(
        "unknown",
        "a single very brief event last month",
        selected_event_kinds=("last_event_only",),
    )
    assert trace.final_label == "1 per month"
    assert [event.rule_id for event in trace.events] == [
        "gan.encode.codebook.single_last_period"
    ]
    assert trace.events[0].before == "unknown"
    assert trace.events[0].after == "1 per month"
    assert trace.events[0].effect_class == "semantic_deterministic_repair"
    assert trace.events[0].portability == "seizure_frequency"


def test_codebook_encode_unknown_wrapper_is_semantic_benchmark_repair() -> None:
    trace = repair_codebook_label_with_evidence(
        "unknown, 1 per day",
        "clusters of jumps almost 1 per day",
        selected_event_kinds=("cluster_frequency",),
    )
    assert trace.final_label == "1 per day"
    assert trace.events[0].effect_class == "semantic_deterministic_repair"
    assert trace.events[0].portability == "benchmark_format"


def test_codebook_encode_repair_mode_only_enables_the_candidate_rules() -> None:
    config = StructuredRepairConfig.for_mode("gan_rules_encode")
    assert config.encode_enabled() is True
    assert config.select_enabled() is False
    assert config.codebook_label_repair is True
    assert config.basic_label_repair is False
    assert config.selected_evidence_repair is False
    assert config.resolved_repair_mode == "gan_rules_encode"
    metadata = repair_mode_metadata("gan_rules_encode")
    assert metadata["repair_family"] == (
        "codebook_label_preservation_with_named_gap_repairs"
    )
    assert metadata["deterministic_semantic_repair"] is True


def test_codebook_encode_mode_records_named_rule_hop_without_reselecting() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "~9/h",
                    "applies_to": "electrographic seizures",
                    "time_window": "recent monitoring",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "Electrographic seizures frequent on EEG (~9/h)",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "Electrographic seizures frequent on EEG (~9/h)",
                "confidence": "high",
                "rationale": "The frequency was not encoded.",
            },
        }
    )
    extraction, _, _, trace = parse_structured_json_with_trace(
        raw,
        note_text="Electrographic seizures frequent on EEG (~9/h)",
        repair_config=StructuredRepairConfig.for_mode("gan_rules_encode"),
    )
    assert extraction is not None
    assert extraction.selection.selected_event_ids == ["e1"]
    assert extraction.selection.final_label == "multiple per day"
    changed = [hop for hop in trace["answer_states"] if hop["changed"]]
    assert [hop["stage_id"] for hop in changed] == [
        "gan.model.selection",
        "gan.encode.codebook.hourly_rate",
    ]
