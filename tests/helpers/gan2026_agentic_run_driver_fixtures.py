"""Shared record + structured-event row fixtures for the gan2026 agentic run-driver dispatch tests.

Extracted from ``test_gan2026_agentic_run_driver.py`` when that megatest was
split into stage-family files to satisfy the ``tests<=800`` line-count gate
(``scripts/check_line_counts.py``). These are pure constructors with no LLM
calls; consumers import them aliased to their original underscore names.
"""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def metadata_without_timestamps(metadata: dict) -> dict:
    filtered = dict(metadata)
    filtered.pop("created_at_utc", None)
    filtered.pop("date", None)
    return filtered


def record(
    source_row_index: int,
    note_text: str,
    *,
    gold_label: str = "unknown",
    gold_monthly_frequency: float = 1000.0,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )


def llm_reasoner_structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": final_label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "one seizure per month",
                    "time_window": "current",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": "one seizure per month",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def router_structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two recent occasions (July and September)",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": (
                        "brief collapses have occurred on two recent occasions (July and September)"
                    ),
                    "time_window": "recent",
                },
                {
                    "event_id": "e2",
                    "kind": "unknown_frequency",
                    "raw_value": "spells are uncommon when meals are regular",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "spells",
                    "evidence": "spells are uncommon when meals are regular",
                    "time_window": "current",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": (
                    "brief collapses have occurred on two recent occasions (July and September)"
                ),
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 0.6666666667,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": "unknown",
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
    replacement_normalized_label: str,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": final_label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "one seizure per month",
                    "time_window": "current",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "two seizures per week",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "two seizures per week",
                    "time_window": "current",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": "one seizure per month",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": replacement_normalized_label,
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def temporal_sentinel_boundary_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "a very infrequent, short event a fortnight ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "a very infrequent, short event a fortnight ago",
                    "time_window": "a fortnight ago",
                    "notes": "isolated last event",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per 2 week",
                "evidence": "a very infrequent, short event a fortnight ago",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "no seizure frequency reference",
                "semantic_kind": "no_reference",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": False,
            "pragmatic_correct": False,
        },
        "evidence_valid": True,
    }


def completion_structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "unknown_frequency",
                    "raw_value": "unclear frequency",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "unclear frequency",
                    "time_window": "current",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": "unclear frequency",
                "confidence": "medium",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def agent_row(
    source_row_index: int,
    *,
    label: str,
    kind: str,
    evidence: str,
    purist_correct: bool = False,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "prompt_version": "fixture_structured_events",
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate" if kind == "frequency" else kind,
                    "raw_value": label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": evidence,
                    "time_window": "current",
                    "notes": "fixture event",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": kind,
                "final_label": label,
                "evidence": evidence,
                "confidence": "high",
                "rationale": f"Fixture selected {label}.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": label,
                "semantic_kind": kind,
                "monthly_frequency": 1.0138888888888888 if label == "1 per month" else 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
