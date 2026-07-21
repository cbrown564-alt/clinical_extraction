"""Selected Gan v0.5 model call followed by its deterministic repair path."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from clinical_extraction.core.local_structured_output import (
    assess_structured_output,
    build_format_only_retry_input,
    validate_format_retry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

from ..errors import SchemaValidationError
from ..models import GenerationSettings, ModelClient, WorkflowOutput

PROMPT_VERSION = hybrid_structured_events.PROMPT_VERSION_V0_5
RULE_SET_VERSION = "gan2026_v05_selected_repair_default"


class SeizureFrequencyPipeline:
    def __init__(self, model: ModelClient, settings: GenerationSettings) -> None:
        self.model = model
        self.settings = settings

    def run(self, *, note_id: str, text: str) -> WorkflowOutput:
        empty = label_to_frequency_record("unknown")
        record = GanFrequencyRecord(
            source_row_index=0,
            note_text=text,
            gold_label="unknown",
            gold_reference="",
            labels_match_all_categories=False,
            quotes_ok_all_categories=False,
            row_ok=True,
            raw={"id": note_id},
            gold_normalized_label=empty.normalized_label,
            gold_label_kind=empty.kind,
            gold_yearly_bounds=empty.yearly_bounds,
            gold_monthly_frequency=empty.monthly_frequency,
        )
        prompt_input = hybrid_structured_events.build_prompt_input(
            record, prompt_version=PROMPT_VERSION
        )
        schema: dict[str, object] = (
            hybrid_structured_events.StructuredExtractionRecord.model_json_schema()
        )
        response = self.model.complete_json(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract seizure-frequency events and choose one current answer. "
                        "Return exactly one JSON object with events and selection; no markdown."
                    ),
                },
                {"role": "user", "content": prompt_input},
            ],
            schema=schema,
            settings=self.settings,
        )
        extraction, events, parse_errors, row_trace = (
            hybrid_structured_events.parse_structured_json_with_trace(
                response.content,
                note_text=text,
                repair_config=hybrid_structured_events.StructuredRepairConfig(),
            )
        )
        initial_content = response.content
        initial_errors = list(parse_errors)
        retry_content = ""
        retry_notes: list[str] = []
        assessment = assess_structured_output(initial_content, initial_errors)
        if extraction is None and assessment.retry_eligible:
            retry = self.model.complete_json(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Correct JSON shape only. Keep every clinical fact and value "
                            "unchanged. Return one JSON object and no markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_format_only_retry_input(
                            malformed_output=initial_content, schema=schema
                        ),
                    },
                ],
                schema=schema,
                settings=self.settings,
            )
            retry_content = retry.content
            validation = validate_format_retry(initial_content, initial_errors, retry_content)
            retry_notes = list(validation.notes)
            if validation.accepted:
                retried = hybrid_structured_events.parse_structured_json_with_trace(
                    retry_content,
                    note_text=text,
                    repair_config=hybrid_structured_events.StructuredRepairConfig(),
                )
                if retried[0] is not None:
                    extraction, events, parse_errors, row_trace = retried
                    response = replace(
                        retry,
                        request_attempts=response.request_attempts + retry.request_attempts,
                    )
        if extraction is None:
            raise SchemaValidationError()
        selection = extraction.selection
        evidence_valid = bool(selection.evidence and selection.evidence in text)
        semantic = row_trace["deterministic_semantic"]
        changes: list[dict[str, Any]] = []
        if semantic.get("before_label") != semantic.get("after_label"):
            changes.append(
                {
                    "owner": "deterministic_rule",
                    "category": semantic.get("rule_category"),
                    "before": semantic.get("before_label"),
                    "after": semantic.get("after_label"),
                    "actions": semantic.get("events", []),
                }
            )
        result = {
            "value": semantic.get("after_label") or selection.final_label or "unknown",
            "kind": selection.final_kind,
            "evidence": selection.evidence,
            "evidence_exact": evidence_valid,
            "rationale": selection.rationale,
            "first_prediction_owner": "model",
            "deterministic_changes": changes,
        }
        trace = {
            "workflow": "seizure_frequency",
            "prompt_version": PROMPT_VERSION,
            "rule_set_version": RULE_SET_VERSION,
            "prompt_input": prompt_input,
            "response_schema": schema,
            "raw_model_response": response.content,
            "initial_raw_model_response": initial_content,
            "format_retry_output": retry_content,
            "format_retry_notes": retry_notes,
            "parse_errors": parse_errors,
            "normalized_events": [event.model_dump() for event in events],
            "component_trace": row_trace,
        }
        return WorkflowOutput(result=result, trace=trace, model_response=response)
