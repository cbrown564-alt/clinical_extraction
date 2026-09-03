"""Extract content recall helpers and sealed holdout aggregates."""

from __future__ import annotations

from clinical_extraction.paper.gan_extract_content_recall import (
    CITED_CELL3_TEST450,
    CITED_CELL5_TEST450,
    answer_hit,
    content_hits,
    evidence_hit,
    fold_surface,
    measure_extract_content_recall,
    surfaces_overlap,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
)


def _record(*, gold_label: str, gold_reference: str) -> GanFrequencyRecord:
    frequency = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=1,
        note_text="Patient has seizures every 4 weeks according to the diary.",
        gold_label=gold_label,
        gold_reference=gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=frequency.normalized_label,
        gold_label_kind=frequency.kind,
        gold_yearly_bounds=frequency.yearly_bounds,
        gold_monthly_frequency=frequency.monthly_frequency,
    )


def _extraction(
    *,
    final_label: str,
    events: list[dict[str, object]],
    selection_evidence: str = "",
) -> StructuredExtractionRecord:
    return StructuredExtractionRecord.model_validate(
        {
            "events": events,
            "selection": {
                "selected_event_ids": [str(events[0]["event_id"])] if events else [],
                "final_kind": "frequency",
                "final_label": final_label,
                "evidence": selection_evidence,
                "confidence": "medium",
                "rationale": "test",
            },
        }
    )


def test_fold_surface_normalizes_inequality_and_dashes() -> None:
    assert fold_surface("≤ four per day") == "<= four per day"
    assert fold_surface("every 3 – 4 weeks") == "every 3 - 4 weeks"


def test_surfaces_overlap_is_either_contains() -> None:
    assert surfaces_overlap("every 4 weeks", "clusters every 4 weeks")
    assert surfaces_overlap("clusters every 4 weeks", "every 4 weeks")
    assert not surfaces_overlap("daily", "most weekdays")


def test_answer_hit_via_normalized_event_not_selected_surface() -> None:
    record = _record(gold_label="1 per 4 week", gold_reference="daily")
    extraction = _extraction(
        final_label="unknown",
        events=[
            {
                "event_id": "e1",
                "kind": "frequency_rate",
                "raw_value": "every 4 weeks",
                "evidence": "diary shows every 4 weeks",
                "assertion_status": "asserted",
                "temporality": "current",
            }
        ],
    )
    assert answer_hit(record, extraction)
    assert not evidence_hit(record, extraction)
    assert content_hits(record, extraction)["either"]


def test_evidence_hit_without_purist_answer() -> None:
    record = _record(gold_label="1 per year", gold_reference="yearly seizures")
    extraction = _extraction(
        final_label="unknown",
        events=[
            {
                "event_id": "e1",
                "kind": "frequency_rate",
                "raw_value": "with some years having one event and others none",
                "evidence": 'pattern as "yearly seizures," with some years having one',
                "assertion_status": "asserted",
                "temporality": "current",
            }
        ],
    )
    assert evidence_hit(record, extraction)
    assert not answer_hit(record, extraction)
    assert content_hits(record, extraction)["either"]


def test_measure_test450_reproduces_sealed_aggregates() -> None:
    payload = measure_extract_content_recall("test450")
    pools = payload["pools"]
    assert pools["answer_or_evidence"]["correct"] == 433
    assert pools["answer"]["correct"] == 382
    assert pools["evidence"]["correct"] == 308
    assert payload["decide_stops_purist"]["cell3_hybrid"]["correct"] == CITED_CELL3_TEST450
    assert payload["decide_stops_purist"]["cell5_llm_only"]["correct"] == CITED_CELL5_TEST450
    assert payload["decide_correct_but_extract_miss"]["cell3_hybrid"] == 1
    assert payload["decide_correct_but_extract_miss"]["cell5_llm_only"] == 0
    assert "source_row_index" not in str(payload)
