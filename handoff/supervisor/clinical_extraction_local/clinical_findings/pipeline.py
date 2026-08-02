"""Selected one-call ExECT workflow with visible family-level changes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from typing import Any

from clinical_extraction.core.local_structured_output import (
    assess_structured_output,
    build_format_only_retry_input,
    validate_format_retry,
)
from clinical_extraction.operational.exect import _assemble
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.constants import (  # noqa: E501
    PIPELINE_FAMILY,
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing import (  # noqa: E501
    flatten_events,
    parse_structured_events_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection import (  # noqa: E501
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_builders import (  # noqa: E501
    build_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.records import (  # noqa: E501
    StructuredExtractionRecord,
)

from ..errors import SchemaValidationError
from ..models import GenerationSettings, ModelClient, WorkflowOutput

RULE_SET_VERSION = "decision_0045_default_default_operational_v1"


class ClinicalFindingsPipeline:
    def __init__(self, model: ModelClient, settings: GenerationSettings) -> None:
        self.model = model
        self.settings = settings

    def run(self, *, note_id: str, text: str) -> WorkflowOutput:
        letter = ExectLetter(note_id, text)
        prompt_input = build_prompt_input(letter, prompt_profile="full")
        schema: dict[str, object] = StructuredExtractionRecord.model_json_schema()
        response = self.model.complete_json(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Read one clinical letter and return one JSON object with a "
                        "clinical_events list. Do not include markdown or hidden reasoning."
                    ),
                },
                {"role": "user", "content": prompt_input},
            ],
            schema=schema,
            settings=self.settings,
        )
        record, parse_errors = parse_structured_events_json(response.content)
        initial_content = response.content
        initial_errors = list(parse_errors)
        retry_content = ""
        retry_notes: list[str] = []
        assessment = assess_structured_output(initial_content, initial_errors)
        if record is None and assessment.retry_eligible:
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
                retry_record, retry_errors = parse_structured_events_json(retry_content)
                if retry_record is not None:
                    record = retry_record
                    parse_errors = [*retry_errors, *retry_notes]
                    response = replace(
                        retry,
                        request_attempts=response.request_attempts + retry.request_attempts,
                    )
        if record is None:
            raise SchemaValidationError()
        mentions = flatten_events(record)
        predicted, warnings = to_predicted_letter(
            note_id,
            mentions,
            note_text=text,
            prompt_version=PROMPT_VERSION,
        )
        row = {
            "letter_id": note_id,
            "split": "operational",
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "model": response.response_model or response.requested_model,
            "mode": "live",
            "call_error": None,
            "parse_errors": parse_errors,
            "gate_warnings": warnings,
            "predicted_mentions": [_mention_row(mention) for mention in predicted.mentions],
            "raw_output": response.content,
            "gold_mentions": [],
        }
        assembled = _assemble([letter], [row])[note_id]
        grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        family_names = {
            "Diagnosis": "diagnoses",
            "SeizureFrequency": "seizure_frequencies",
            "Prescription": "prescriptions",
            "Investigations": "investigations",
        }
        for mention in assembled["predicted_mentions"]:
            family = str(mention.get("entity", ""))
            grouped[family_names.get(family, family)].append(_public_finding(mention))
        result = {
            key: grouped.get(key, [])
            for key in ("diagnoses", "seizure_frequencies", "prescriptions", "investigations")
        }
        trace = {
            "workflow": "clinical_findings",
            "prompt_version": PROMPT_VERSION,
            "rule_set_version": RULE_SET_VERSION,
            "prompt_input": prompt_input,
            "response_schema": schema,
            "raw_model_response": response.content,
            "initial_raw_model_response": initial_content,
            "format_retry_output": retry_content,
            "format_retry_notes": retry_notes,
            "parse_errors": parse_errors,
            "gate_warnings": warnings,
            "structured_events": [event.model_dump() for event in record.clinical_events],
            "assembly": assembled,
        }
        return WorkflowOutput(result=result, trace=trace, model_response=response)


def _mention_row(mention: Any) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner,
    }


def _public_finding(mention: dict[str, Any]) -> dict[str, Any]:
    provenance = mention.get("provenance", [])
    return {
        "family": mention.get("entity"),
        "value": mention.get("text"),
        "attributes": mention.get("attributes", {}),
        "evidence": mention.get("evidence", ""),
        "evidence_exact": mention.get("evidence_valid", False),
        "first_prediction_owner": "model",
        "deterministic_actions": provenance,
        "warnings": [],
    }
