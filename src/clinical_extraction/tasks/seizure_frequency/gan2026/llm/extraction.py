"""Source-first Gan extraction artifact path for the selected one-call prompt.

The historical runner remains the benchmark adapter.  This module prepares the
same request from an ordinary source document, then preserves the response and
typed source-near events before the legacy compatibility parser is consulted.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from typing import Any, cast

from clinical_extraction.core.artifacts import (
    ArtifactStatus,
    Assertion,
    CoverageRecord,
    ExtractionArtifact,
    InferenceAttempt,
    JsonValue,
    PreparedExtractionRequest,
    PromptComponent,
    SourceDocument,
    TaskProfile,
    canonical_json,
    freeze_json,
    locate_text_evidence,
    replay_attempt,
)
from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events as legacy,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
)

GAN_ARTIFACT_SCHEMA_VERSION = "gan2026.structured_events.artifact.v1"
GAN_ARTIFACT_PROFILE_VERSION = "gan2026.gan_llm_extract.profile.v1"


@dataclass(frozen=True)
class _PromptNote:
    """Minimal structural input accepted by the historical prompt builders."""

    note_text: str


@dataclass(frozen=True)
class GanEventContent:
    """One unnormalised Gan model event, retaining its original fields."""

    event_id: str | None
    kind: str
    raw_value: str
    applies_to: str | None
    time_window: str | None
    temporality: str | None
    assertion_status: str | None
    notes: str | None
    raw_event: Mapping[str, JsonValue]

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_event", freeze_json(self.raw_event))


@cache
def gan_extraction_profile(prompt_version: str = GAN_LLM_EXTRACT) -> TaskProfile:
    """Return an immutable profile for one existing Gan prompt identity."""

    if prompt_version != GAN_LLM_EXTRACT:
        raise ValueError(
            "the reconstruction slice supports only the explicit gan_llm_extract profile"
        )
    template = _payload_for_text("", prompt_version=prompt_version)
    components = (
        PromptComponent.from_value(
            "task_definition",
            f"{prompt_version}.task.v1",
            template.get("task"),
            rendered_paths=("task",),
        ),
        PromptComponent.from_value(
            "instructions",
            f"{prompt_version}.instructions.v1",
            template.get("instructions", []),
            rendered_paths=("instructions",),
        ),
        PromptComponent.from_value(
            "examples",
            f"{prompt_version}.examples.v1",
            _examples_component(template),
            rendered_paths=("label_forms.forms[].examples", "examples"),
        ),
        PromptComponent.from_value(
            "allowed_label_presentation",
            f"{prompt_version}.allowed-labels.v1",
            _allowed_labels_component(template),
            rendered_paths=("label_forms", "answer_schema"),
        ),
        PromptComponent.from_value(
            "evidence_requirements",
            f"{prompt_version}.evidence.v1",
            _evidence_component(template),
            rendered_paths=("instructions[]", "event_schema.evidence", "selection_schema.evidence"),
        ),
        PromptComponent.from_value(
            "schema_presentation",
            f"{prompt_version}.schema.v1",
            {
                key: value
                for key, value in template.items()
                if key.endswith("_schema") or key == "allowed_decision_fields"
            },
            rendered_paths=("event_schema", "selection_schema", "answer_schema"),
        ),
    )
    return TaskProfile(
        task_id="gan2026.seizure_frequency",
        profile_id=prompt_version,
        profile_version=GAN_ARTIFACT_PROFILE_VERSION,
        schema_version=GAN_ARTIFACT_SCHEMA_VERSION,
        capture_families=("seizure_frequency",),
        prompt_components=components,
        compatible_policies={
            "gan2026.label_projection": ("seizure_frequency",),
            "read_only.event_inventory": ("seizure_frequency",),
        },
    )


def prepare_gan_request(
    source: SourceDocument,
    *,
    profile: TaskProfile | None = None,
) -> PreparedExtractionRequest:
    """Prepare the selected Gan request without a benchmark or gold record."""

    selected = profile or gan_extraction_profile()
    prompt_input_json = _compose_prompt_input(source.text, selected)
    rendered_messages = legacy.DspyStructuredExtractor().render_messages(
        prompt_input_json=prompt_input_json
    )
    return PreparedExtractionRequest.create(
        profile=selected,
        sources=(source,),
        prompt_input_json=prompt_input_json,
        rendered_messages=rendered_messages,
    )


def execute_gan_request(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    completion: Callable[[PreparedExtractionRequest], str],
    provider_metadata: Mapping[str, JsonValue] | None = None,
) -> ExtractionArtifact[GanEventContent]:
    """Execute exactly one explicitly supplied completion callable."""

    _require_request_source(request, source)
    try:
        response = completion(request)
    except Exception as exc:  # Provider adapters deliberately stop at this boundary.
        attempt = InferenceAttempt.failed(
            request=request,
            error=exc,
            provider_metadata=provider_metadata,
        )
    else:
        attempt = InferenceAttempt.captured(
            request=request,
            response_text=str(response),
            provider_metadata=provider_metadata,
        )
    return consume_gan_attempt(request, source=source, attempt=attempt)


def replay_gan_response(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    saved_request_id: str,
    response_text: str,
    provider_metadata: Mapping[str, JsonValue] | None = None,
) -> ExtractionArtifact[GanEventContent]:
    """Consume a saved response; this function has no model-call path."""

    _require_request_source(request, source)
    attempt = replay_attempt(
        request,
        saved_request_id=saved_request_id,
        response_text=response_text,
        provider_metadata=provider_metadata,
    )
    return consume_gan_attempt(request, source=source, attempt=attempt)


def consume_gan_attempt(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    attempt: InferenceAttempt,
) -> ExtractionArtifact[GanEventContent]:
    """Decode a captured attempt before applying the named legacy parser."""

    _require_request_source(request, source)
    if attempt.request_id != request.request_id:
        raise ValueError("Gan attempt does not match the prepared request")
    raw_payload: Any = None
    raw_decode_notes: list[str] = []
    raw_decode_error: str | None = None
    if attempt.status == "captured" and attempt.response_text:
        try:
            raw_payload, raw_decode_notes = parse_json_payload_with_schema_repair(
                extract_json_object(attempt.response_text)
            )
        except json.JSONDecodeError as exc:
            raw_decode_error = f"invalid_json: {exc.msg}"
    elif attempt.status == "captured":
        raw_decode_error = "empty_captured_response"
    else:
        raw_decode_error = attempt.error_message or attempt.status

    assertions = _raw_assertions(raw_payload, source=source)
    raw_schema_errors = _raw_schema_errors(raw_payload)
    compatibility_record = None
    normalized_events: Sequence[Any] = ()
    compatibility_notes: list[str] = []
    row_trace: Mapping[str, Any] = {}
    if attempt.status == "captured" and attempt.response_text:
        compatibility_record, normalized_events, compatibility_notes, row_trace = (
            legacy.parse_structured_json_with_trace(
                attempt.response_text,
                note_text=source.text,
            )
        )
    status: ArtifactStatus = (
        "ready"
        if attempt.status == "captured"
        and raw_payload is not None
        and not raw_schema_errors
        and compatibility_record is not None
        else "failed"
    )
    coverage = CoverageRecord(
        capture_families=("seizure_frequency",),
        processed_source_ids=(source.source_id,) if status == "ready" else (),
        failed_source_ids=() if status == "ready" else (source.source_id,),
        unsupported_fields=(
            "diagnosis",
            "medication",
            "investigation",
            "longitudinal_event_identity",
        ),
        notes=("Processing success does not establish exhaustive frequency recall.",),
    )
    compatibility_output = (
        {
            "structured_record": compatibility_record.model_dump(mode="json"),
            "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
            "final_label": compatibility_record.selection.final_label,
            "evidence": compatibility_record.selection.evidence,
            "rationale": compatibility_record.selection.rationale,
        }
        if compatibility_record is not None
        else None
    )
    return ExtractionArtifact.create(
        status=status,
        request=request,
        attempts=(attempt,),
        raw_payload=raw_payload,
        assertions=assertions,
        coverage=coverage,
        diagnostics={
            "raw_decode_notes": raw_decode_notes,
            "raw_decode_error": raw_decode_error,
            "raw_schema_errors": raw_schema_errors,
            "compatibility_parser": "gan2026.hybrid_structured_events.v1",
            "compatibility_notes": compatibility_notes,
            "row_trace": row_trace,
            "evidence_locations": [
                evidence.to_dict()
                for assertion in assertions
                for evidence in assertion.evidence
            ],
        },
        compatibility_output=compatibility_output,
    )


def event_inventory(
    artifact: ExtractionArtifact[GanEventContent],
) -> tuple[GanEventContent, ...]:
    """Read typed events without scoring, projection, or another model call."""

    return tuple(assertion.content for assertion in artifact.assertions)


def _payload_json_for_text(text: str, *, prompt_version: str) -> str:
    note = cast(GanFrequencyRecord, _PromptNote(note_text=text))
    return legacy.build_prompt_input(note, prompt_version=prompt_version)


def _compose_prompt_input(text: str, profile: TaskProfile) -> str:
    if profile.task_id != "gan2026.seizure_frequency":
        raise ValueError("profile is not a Gan seizure-frequency task")
    if profile.profile_id != GAN_LLM_EXTRACT:
        raise ValueError(
            "the reconstruction slice supports only the explicit gan_llm_extract profile"
        )
    components = _component_values(
        profile,
        expected={
            "task_definition",
            "instructions",
            "examples",
            "allowed_label_presentation",
            "evidence_requirements",
            "schema_presentation",
        },
    )
    allowed_labels = _mutable_json(components["allowed_label_presentation"])
    examples = _mutable_json(components["examples"])
    schema = _mutable_json(components["schema_presentation"])
    if not isinstance(allowed_labels, dict) or not isinstance(examples, list):
        raise ValueError("Gan label and example components have incompatible shapes")
    if not isinstance(schema, dict):
        raise ValueError("Gan schema component must be an object")
    examples_by_form = {
        str(row["form"]): row.get("examples", [])
        for row in examples
        if isinstance(row, dict) and "form" in row
    }
    forms = allowed_labels.get("forms")
    if not isinstance(forms, list):
        raise ValueError("Gan allowed-label component must contain forms")
    merged_forms: list[dict[str, Any]] = []
    for value in forms:
        if not isinstance(value, dict) or "form" not in value:
            raise ValueError("each Gan label form must be an object with a form name")
        row = dict(value)
        form = str(row["form"])
        if form in examples_by_form:
            row["examples"] = examples_by_form[form]
        merged_forms.append(row)
    allowed_labels["forms"] = merged_forms
    payload: dict[str, Any] = {
        "task": _mutable_json(components["task_definition"]),
        "instructions": _mutable_json(components["instructions"]),
        "label_forms": allowed_labels,
        "event_schema": schema.get("event_schema"),
        "selection_schema": schema.get("selection_schema"),
    }
    recorded_evidence = _mutable_json(components["evidence_requirements"])
    if sorted(_evidence_component(payload)) != sorted(recorded_evidence):
        raise ValueError(
            "Gan evidence component is inconsistent with the composed prompt components"
        )
    payload["note_text"] = text
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _component_values(
    profile: TaskProfile,
    *,
    expected: set[str],
) -> dict[str, JsonValue]:
    values = {
        component.component_id: component.content for component in profile.prompt_components
    }
    if set(values) != expected:
        missing = sorted(expected - set(values))
        extra = sorted(set(values) - expected)
        raise ValueError(f"Gan profile component mismatch; missing={missing}, extra={extra}")
    return values


def _mutable_json(value: Any) -> Any:
    return json.loads(canonical_json(value))


def _payload_for_text(text: str, *, prompt_version: str) -> dict[str, Any]:
    payload = json.loads(_payload_json_for_text(text, prompt_version=prompt_version))
    if not isinstance(payload, dict):
        raise TypeError("Gan prompt builder must return one JSON object")
    payload.pop("note_text", None)
    return payload


def _examples_component(template: Mapping[str, Any]) -> Any:
    if "examples" in template:
        return template["examples"]
    forms = (template.get("label_forms") or {}).get("forms", [])
    return [
        {"form": row.get("form"), "examples": row.get("examples", [])}
        for row in forms
        if isinstance(row, Mapping) and row.get("examples")
    ]


def _allowed_labels_component(template: Mapping[str, Any]) -> Any:
    if "answer_schema" in template:
        return template["answer_schema"]
    label_forms = template.get("label_forms")
    if not isinstance(label_forms, Mapping):
        return None
    return {
        key: (
            [
                {
                    item_key: item_value
                    for item_key, item_value in row.items()
                    if item_key != "examples"
                }
                for row in value
            ]
            if key == "forms" and isinstance(value, list)
            else value
        )
        for key, value in label_forms.items()
    }


def _evidence_component(template: Mapping[str, Any]) -> list[str]:
    found: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str) and "evidence" in value.casefold():
            found.append(value)
        elif isinstance(value, Mapping):
            for key, item in value.items():
                if "evidence" in str(key).casefold():
                    found.append(f"{key}: {item}")
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(template)
    return found


def _raw_assertions(
    payload: Any,
    *,
    source: SourceDocument,
) -> tuple[Assertion[GanEventContent], ...]:
    if not isinstance(payload, Mapping):
        return ()
    events = payload.get("events")
    if not isinstance(events, list):
        return ()
    assertions: list[Assertion[GanEventContent]] = []
    for position, value in enumerate(events):
        if not isinstance(value, Mapping):
            continue
        raw_event = {str(key): _json_compatible(item) for key, item in value.items()}
        event_id = _optional_text(value.get("event_id"))
        content = GanEventContent(
            event_id=event_id,
            kind=str(value.get("kind") or ""),
            raw_value=str(value.get("raw_value") or ""),
            applies_to=_optional_text(value.get("applies_to")),
            time_window=_optional_text(value.get("time_window")),
            temporality=_optional_text(value.get("temporality")),
            assertion_status=_optional_text(value.get("assertion_status")),
            notes=_optional_text(value.get("notes")),
            raw_event=raw_event,
        )
        quote = str(value.get("evidence") or "")
        assertions.append(
            Assertion(
                assertion_id=event_id or f"raw-event-{position}",
                content=content,
                evidence=(locate_text_evidence(source, quote),),
                producer="model",
                raw_position=position,
                provenance={"raw_event_position": position},
            )
        )
    return tuple(assertions)


def _raw_schema_errors(payload: Any) -> list[str]:
    if not isinstance(payload, Mapping):
        return ["schema_validation_error: root must be an object"]
    events = payload.get("events")
    selection = payload.get("selection")
    errors: list[str] = []
    if not isinstance(events, list):
        errors.append("schema_validation_error: events must be an array")
    elif any(not isinstance(event, Mapping) for event in events):
        errors.append("schema_validation_error: every event must be an object")
    if not isinstance(selection, Mapping):
        errors.append("schema_validation_error: selection must be an object")
    return errors


def _require_request_source(
    request: PreparedExtractionRequest,
    source: SourceDocument,
) -> None:
    if request.task_id != "gan2026.seizure_frequency":
        raise ValueError("request is not a Gan seizure-frequency extraction")
    if request.sources != (source.ref(),):
        raise ValueError("source identity does not match the prepared Gan request")


def _optional_text(value: Any) -> str | None:
    return None if value is None else str(value)


def _json_compatible(value: Any) -> JsonValue:
    return cast(JsonValue, json.loads(json.dumps(value, ensure_ascii=False)))


__all__ = [
    "GAN_ARTIFACT_PROFILE_VERSION",
    "GAN_ARTIFACT_SCHEMA_VERSION",
    "GanEventContent",
    "consume_gan_attempt",
    "event_inventory",
    "execute_gan_request",
    "gan_extraction_profile",
    "prepare_gan_request",
    "replay_gan_response",
]
