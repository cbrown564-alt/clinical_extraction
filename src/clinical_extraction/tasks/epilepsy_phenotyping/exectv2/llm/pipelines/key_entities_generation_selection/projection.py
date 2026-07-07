"""Projection of final model selections into benchmark prediction rows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.constants import (
    COMPONENT_OWNER,
    FACT_ORIGIN,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    component_owner_for_model,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.facts import (
    clinical_facts_to_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.records import (
    DedupClinicalFactsRecord,
)


def to_predicted_letter(
    letter: ExectLetter,
    final_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str]]:
    record = _coerce_record(final_record)
    return structured.to_predicted_letter(
        letter.letter_id,
        structured.flatten_events(record),
        note_text=letter.note_text,
        prompt_version=PROMPT_VERSION,
        component_owner=component_owner,
        pipeline_family=PIPELINE_FAMILY,
    )


def to_predicted_letter_from_mentions(
    letter: ExectLetter,
    final_mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str]]:
    mentions = _coerce_mentions(final_mentions)
    return structured.to_predicted_letter(
        letter.letter_id,
        mentions,
        note_text=letter.note_text,
        prompt_version=PROMPT_VERSION,
        component_owner=component_owner,
        pipeline_family=PIPELINE_FAMILY,
    )


def to_predicted_letter_from_dedup_facts(
    letter: ExectLetter,
    record: DedupClinicalFactsRecord | Mapping[str, Any],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str], list[dict[str, Any]], list[str]]:
    fact_record = (
        record
        if isinstance(record, DedupClinicalFactsRecord)
        else DedupClinicalFactsRecord.model_validate(record)
    )
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(fact_record.clinical_facts)
    predicted, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return predicted, gate_warnings, provenance, adapter_notes


def row_from_final_record(
    letter: ExectLetter,
    final_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    raw_selection_output: str = "",
    generation_parse_errors: Sequence[str] = (),
    selection_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project final model-selected events to the benchmark row format."""

    record = _coerce_record(final_record)
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter(
        letter,
        record,
        component_owner=component_owner,
    )
    mentions_raw = structured.flatten_events(record)
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_selection_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(selection_parse_errors),
        "gate_warnings": gate_warnings,
        "n_events_final": len(record.clinical_events),
        "n_mentions_raw": len(mentions_raw),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions_raw) - len(predicted_letter.mentions),
        "structured_events_final": [event.model_dump() for event in record.clinical_events],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def row_from_final_dedup_facts(
    letter: ExectLetter,
    record: DedupClinicalFactsRecord | Mapping[str, Any],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    generation_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project model-selected de-duplicated facts to the benchmark row format."""

    fact_record = (
        record
        if isinstance(record, DedupClinicalFactsRecord)
        else DedupClinicalFactsRecord.model_validate(record)
    )
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(fact_record.clinical_facts)
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_generation_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(generation_parse_errors),
        "adapter_parse_errors": adapter_notes,
        "gate_warnings": [*adapter_notes, *gate_warnings],
        "n_events_final": 0,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
        "n_clinical_facts_final": len(fact_record.clinical_facts),
        "clinical_facts_final": [fact.model_dump() for fact in fact_record.clinical_facts],
        "adapter_provenance": provenance,
        "structured_events_final": [],
        "structured_mentions_final": [mention.model_dump() for mention in mentions],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def row_from_final_mentions(
    letter: ExectLetter,
    final_mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    raw_selection_output: str = "",
    generation_parse_errors: Sequence[str] = (),
    selection_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project final model-selected direct mentions to the benchmark row format."""

    mentions = _coerce_mentions(final_mentions)
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_selection_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(selection_parse_errors),
        "gate_warnings": gate_warnings,
        "n_events_final": 0,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
        "structured_events_final": [],
        "structured_mentions_final": [mention.model_dump() for mention in mentions],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def _coerce_record(
    record: structured.StructuredExtractionRecord | Mapping[str, Any],
) -> structured.StructuredExtractionRecord:
    if isinstance(record, structured.StructuredExtractionRecord):
        return record
    return structured.StructuredExtractionRecord.model_validate(record)


def _coerce_mentions(
    mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
) -> list[structured.MentionForEvidence]:
    return [
        mention
        if isinstance(mention, structured.MentionForEvidence)
        else structured.MentionForEvidence.model_validate(mention)
        for mention in mentions
    ]


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner,
    }
