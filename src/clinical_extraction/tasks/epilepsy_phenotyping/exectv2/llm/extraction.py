"""Explicit ExECT extraction artifacts beside the historical benchmark runner."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
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
    freeze_json,
    locate_text_evidence,
    replay_attempt,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_overall,
)

from .pipelines.key_entities_structured.constants import (
    BOTH_EXTRACT_VERSIONS,
    EXECT_LLM_EXTRACT,
    FAMILY_TO_ENTITY,
    KEY_ENTITY_NAMES,
    LLM_ONLY_VERSIONS,
    prompt_version_for,
)
from .pipelines.key_entities_structured.parsing import (
    mentions_from_events,
    parse_structured_events_json,
)
from .pipelines.key_entities_structured.projection import (
    to_predicted_letter,
)
from .pipelines.key_entities_structured.prompt_builders import (
    build_prompt_input,
)
from .pipelines.key_entities_structured.prompt_content import suggested_evidence_rows
from .pipelines.key_entities_structured.records import (
    StructuredExtractionRecord,
)
from .pipelines.key_entities_structured.signatures import (
    DspyKeyEntitiesStructuredExtractor,
)
from .shared.json_parse import (
    parse_json_payload,
)

EXECT_ARTIFACT_SCHEMA_VERSION = "exectv2.compact.artifact.v1"
EXECT_ARTIFACT_PROFILE_VERSION = "exectv2.exect_llm_extract.profile.v1"
EXECT_CAPTURE_FAMILIES = (
    "medication",
    "diagnosis",
    "seizure_frequency",
    "investigation",
)
EXECT_SCORE_ENTITIES = (
    PRESCRIPTION.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    INVESTIGATIONS.name,
)


@dataclass(frozen=True)
class ExectEventContent:
    """One original-position Compact event before compatibility coercion."""

    family: str
    fact: str
    attributes: Mapping[str, JsonValue]
    raw_event: Mapping[str, JsonValue]

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", freeze_json(self.attributes))
        object.__setattr__(self, "raw_event", freeze_json(self.raw_event))


@dataclass(frozen=True)
class ExectProjectionResult:
    """Projected benchmark view plus its raw-event attribution and warnings."""

    prediction: PredictedLetter
    warnings: tuple[str, ...]
    compatibility_raw_positions: tuple[int, ...]
    projected_mention_raw_positions: tuple[int | None, ...]


@cache
def exect_extraction_profile(prompt_version: str = EXECT_LLM_EXTRACT) -> TaskProfile:
    """Return an explicit profile without reading the mutable prompt default."""

    selected_version = prompt_version_for(prompt_version=prompt_version)
    template = _payload_for_text("", prompt_version=selected_version)
    components = (
        PromptComponent.from_value(
            "task_definition",
            f"{selected_version}.task.v1",
            template.get("task"),
            rendered_paths=("task",),
        ),
        PromptComponent.from_value(
            "instructions",
            f"{selected_version}.instructions.v1",
            {
                "decision_procedure": template.get("decision_procedure", []),
                "family_guidance": template.get("family_guidance", {}),
                "clinical_rules": template.get("clinical_rules", {}),
            },
            rendered_paths=("decision_procedure", "family_guidance", "clinical_rules"),
        ),
        PromptComponent.from_value(
            "examples",
            f"{selected_version}.examples.v1",
            template.get("examples", []),
            rendered_paths=("examples",),
        ),
        PromptComponent.from_value(
            "allowed_value_presentation",
            f"{selected_version}.allowed-values.v1",
            template.get("attribute_vocabulary", {}),
            rendered_paths=("attribute_vocabulary",),
        ),
        PromptComponent.from_value(
            "evidence_requirements",
            f"{selected_version}.evidence.v1",
            _evidence_component(template),
            rendered_paths=("decision_procedure[]", "output_schema.clinical_events[].evidence"),
        ),
        PromptComponent.from_value(
            "schema_presentation",
            f"{selected_version}.schema.v1",
            template.get("output_schema", {}),
            rendered_paths=("output_schema",),
        ),
    )
    return TaskProfile(
        task_id="exectv2.key_entity_inventory",
        profile_id=selected_version,
        profile_version=EXECT_ARTIFACT_PROFILE_VERSION,
        schema_version=EXECT_ARTIFACT_SCHEMA_VERSION,
        capture_families=EXECT_CAPTURE_FAMILIES,
        prompt_components=components,
        compatible_policies={
            "exectv2.benchmark_mentions": EXECT_CAPTURE_FAMILIES,
            "read_only.family_inventory": EXECT_CAPTURE_FAMILIES,
        },
    )


def prepare_exect_request(
    source: SourceDocument,
    *,
    profile: TaskProfile | None = None,
) -> PreparedExtractionRequest:
    """Prepare one explicit ExECT profile without gold, corpus, or global mutation."""

    selected = profile or exect_extraction_profile()
    prompt_input_json = _compose_prompt_input(source, selected)
    rendered_messages = DspyKeyEntitiesStructuredExtractor(
        prompt_version=selected.profile_id
    ).render_messages(prompt_input_json=prompt_input_json)
    return PreparedExtractionRequest.create(
        profile=selected,
        sources=(source,),
        prompt_input_json=prompt_input_json,
        rendered_messages=rendered_messages,
    )


def execute_exect_request(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    completion: Callable[[PreparedExtractionRequest], str],
    provider_metadata: Mapping[str, JsonValue] | None = None,
) -> ExtractionArtifact[ExectEventContent]:
    """Execute one explicitly supplied model adapter and preserve its failure."""

    _require_request_source(request, source)
    try:
        response = completion(request)
    except Exception as exc:  # Provider errors become attempts, not empty findings.
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
    return consume_exect_attempt(request, source=source, attempt=attempt)


def replay_exect_response(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    saved_request_id: str,
    response_text: str,
    provider_metadata: Mapping[str, JsonValue] | None = None,
) -> ExtractionArtifact[ExectEventContent]:
    """Replay an exact saved request through a path with no completion callback."""

    _require_request_source(request, source)
    attempt = replay_attempt(
        request,
        saved_request_id=saved_request_id,
        response_text=response_text,
        provider_metadata=provider_metadata,
    )
    return consume_exect_attempt(request, source=source, attempt=attempt)


def consume_exect_attempt(
    request: PreparedExtractionRequest,
    *,
    source: SourceDocument,
    attempt: InferenceAttempt,
) -> ExtractionArtifact[ExectEventContent]:
    """Preserve raw positions, then run the named Compact compatibility parser."""

    _require_request_source(request, source)
    if attempt.request_id != request.request_id:
        raise ValueError("ExECT attempt does not match the prepared request")
    raw_payload: Any = None
    raw_decode_notes: list[str] = []
    raw_decode_error: str | None = None
    if attempt.status == "captured" and attempt.response_text:
        try:
            raw_payload, raw_decode_notes = parse_json_payload(attempt.response_text)
        except json.JSONDecodeError as exc:
            raw_decode_error = f"invalid_json: {exc.msg}"
    elif attempt.status == "captured":
        raw_decode_error = "empty_captured_response"
    else:
        raw_decode_error = attempt.error_message or attempt.status

    assertions = _raw_assertions(raw_payload, source=source)
    raw_schema_errors = _raw_schema_errors(raw_payload)
    compatibility_record = None
    compatibility_notes: list[str] = []
    if attempt.status == "captured" and attempt.response_text:
        compatibility_record, compatibility_notes = parse_structured_events_json(
            attempt.response_text,
            prompt_version=request.profile_id,
        )
    status: ArtifactStatus = (
        "ready"
        if attempt.status == "captured"
        and raw_payload is not None
        and not raw_schema_errors
        and compatibility_record is not None
        else "failed"
    )
    raw_families = [assertion.content.family for assertion in assertions]
    known_families = [family for family in raw_families if family in EXECT_CAPTURE_FAMILIES]
    compatibility_raw_positions = tuple(
        assertion.raw_position
        for assertion in assertions
        if assertion.content.family in EXECT_CAPTURE_FAMILIES
        and assertion.raw_position is not None
    )
    coverage = CoverageRecord(
        capture_families=EXECT_CAPTURE_FAMILIES,
        processed_source_ids=(source.source_id,) if status == "ready" else (),
        failed_source_ids=() if status == "ready" else (source.source_id,),
        unsupported_fields=(
            "medication_exposure_dates",
            "longitudinal_event_identity",
            "complete_negative_history",
        ),
        notes=(
            "Compact capture does not establish exhaustive recall or longitudinal coverage.",
        ),
    )
    compatibility_output = (
        compatibility_record.model_dump(mode="json")
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
            "compatibility_parser": "exectv2.compact.compatibility.v1",
            "compatibility_notes": compatibility_notes,
            "raw_event_count": len(assertions),
            "raw_family_counts": dict(Counter(raw_families)),
            "known_family_counts": dict(Counter(known_families)),
            "compatibility_event_count": (
                len(compatibility_record.clinical_events)
                if compatibility_record is not None
                else 0
            ),
            "compatibility_raw_positions": compatibility_raw_positions,
            "evidence_locations": [
                evidence.to_dict()
                for assertion in assertions
                for evidence in assertion.evidence
            ],
        },
        compatibility_output=compatibility_output,
    )


def project_exect_artifact(
    artifact: ExtractionArtifact[ExectEventContent],
    *,
    source: SourceDocument,
) -> PredictedLetter:
    """Apply the historical mention/evidence adapter without changing the artifact."""

    return project_exect_artifact_with_trace(artifact, source=source).prediction


def project_exect_artifact_with_trace(
    artifact: ExtractionArtifact[ExectEventContent],
    *,
    source: SourceDocument,
) -> ExectProjectionResult:
    """Project while retaining warnings and raw-event positions for each mention."""

    _require_request_source(artifact.request, source)
    if artifact.status != "ready" or not isinstance(
        artifact.compatibility_output, Mapping
    ):
        raise ValueError("cannot project a failed ExECT extraction artifact")
    record = StructuredExtractionRecord.model_validate(
        _mutable_json(artifact.compatibility_output)
    )
    mentions = mentions_from_events(record)
    position_values = artifact.diagnostics.get("compatibility_raw_positions")
    if not isinstance(position_values, (list, tuple)) or any(
        not isinstance(value, int) or isinstance(value, bool)
        for value in position_values
    ):
        raise ValueError("artifact lacks valid compatibility raw-event positions")
    raw_positions = tuple(cast(int, value) for value in position_values)
    candidate_positions = tuple(
        raw_position
        for event, raw_position in zip(
            record.clinical_events,
            raw_positions,
            strict=True,
        )
        if FAMILY_TO_ENTITY.get(event.family, "") in KEY_ENTITY_NAMES and event.fact
    )
    projected, warnings = to_predicted_letter(
        source.source_id,
        mentions,
        note_text=source.text,
        prompt_version=artifact.request.profile_id,
    )
    candidate_projections = []
    for mention, raw_position in zip(mentions, candidate_positions, strict=True):
        single_projection, _ = to_predicted_letter(
            source.source_id,
            [mention],
            note_text=source.text,
            prompt_version=artifact.request.profile_id,
        )
        candidate_projections.append((raw_position, single_projection.mentions))
    projected_positions: list[int | None] = []
    for projected_mention in projected.mentions:
        possible_positions = [
            raw_position
            for raw_position, single_mentions in candidate_projections
            if projected_mention in single_mentions
        ]
        projected_positions.append(
            possible_positions[0] if len(possible_positions) == 1 else None
        )
    return ExectProjectionResult(
        prediction=projected,
        warnings=tuple(warnings),
        compatibility_raw_positions=raw_positions,
        projected_mention_raw_positions=tuple(projected_positions),
    )


def score_exect_artifact(
    artifact: ExtractionArtifact[ExectEventContent],
    *,
    source: SourceDocument,
    reference: ExectLetter,
) -> dict[str, JsonValue]:
    """Task-owned benchmark scoring; the common lifecycle has no clinical score."""

    if reference.letter_id != source.source_id:
        raise ValueError("reference letter does not match the artifact source")
    prediction = project_exect_artifact(artifact, source=source)
    score = score_overall(
        [reference],
        [to_exect_letter(prediction, note_text=source.text)],
        EXECT_SCORE_ENTITIES,
        benchmark_config_for,
    )
    return cast(dict[str, JsonValue], score.model_dump(mode="json"))


def family_inventory(
    artifact: ExtractionArtifact[ExectEventContent],
) -> dict[str, tuple[ExectEventContent, ...]]:
    """Read all raw events, including unsupported families, without projection."""

    families: dict[str, list[ExectEventContent]] = {}
    for assertion in artifact.assertions:
        families.setdefault(assertion.content.family, []).append(assertion.content)
    return {family: tuple(events) for family, events in families.items()}


def _payload_for_text(text: str, *, prompt_version: str) -> dict[str, Any]:
    payload = json.loads(
        build_prompt_input(
            ExectLetter("profile-inspection", text),
            prompt_version=prompt_version,
        )
    )
    if not isinstance(payload, dict):
        raise TypeError("ExECT prompt builder must return one JSON object")
    payload.pop("letter_text", None)
    payload.pop("suggested_evidence", None)
    return payload


def _compose_prompt_input(source: SourceDocument, profile: TaskProfile) -> str:
    if profile.task_id != "exectv2.key_entity_inventory":
        raise ValueError("profile is not an ExECT key-entity task")
    selected_version = prompt_version_for(prompt_version=profile.profile_id)
    components = _component_values(
        profile,
        expected={
            "task_definition",
            "instructions",
            "examples",
            "allowed_value_presentation",
            "evidence_requirements",
            "schema_presentation",
        },
    )
    instructions = _mutable_json(components["instructions"])
    if not isinstance(instructions, dict):
        raise ValueError("ExECT instructions component must be an object")
    payload: dict[str, Any] = {
        "task": _mutable_json(components["task_definition"]),
        "output_schema": _mutable_json(components["schema_presentation"]),
        "decision_procedure": instructions.get("decision_procedure", []),
        "family_guidance": instructions.get("family_guidance", {}),
        "attribute_vocabulary": _mutable_json(
            components["allowed_value_presentation"]
        ),
        "clinical_rules": instructions.get("clinical_rules", {}),
    }
    examples = _mutable_json(components["examples"])
    if selected_version in LLM_ONLY_VERSIONS:
        if examples:
            raise ValueError("this ExECT prompt profile does not render an examples component")
    else:
        payload["examples"] = examples
    recorded_evidence = _mutable_json(components["evidence_requirements"])
    if _evidence_component(payload) != recorded_evidence:
        raise ValueError(
            "ExECT evidence component is inconsistent with the composed prompt components"
        )
    letter = ExectLetter(source.source_id, source.text)
    if selected_version in BOTH_EXTRACT_VERSIONS:
        payload["suggested_evidence"] = suggested_evidence_rows(letter)
    payload["letter_text"] = source.text
    return json.dumps(payload, ensure_ascii=False)


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
        raise ValueError(f"ExECT profile component mismatch; missing={missing}, extra={extra}")
    return values


def _mutable_json(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Mapping):
        return {str(key): _mutable_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_mutable_json(item) for item in value]
    raise TypeError(f"component value is not JSON-compatible: {type(value).__name__}")


def _raw_schema_errors(payload: Any) -> list[str]:
    if not isinstance(payload, Mapping):
        return ["schema_validation_error: root must be an object"]
    if "clinical_events" not in payload:
        return ["schema_validation_error: missing clinical_events"]
    events = payload.get("clinical_events")
    if not isinstance(events, list):
        return ["schema_validation_error: clinical_events must be an array"]
    errors: list[str] = []
    for position, event in enumerate(events):
        if not isinstance(event, Mapping):
            errors.append(f"schema_validation_error: event[{position}] must be an object")
            continue
        family = event.get("family", event.get("clinical_family"))
        if not isinstance(family, str) or not family.strip():
            errors.append(f"schema_validation_error: event[{position}].family is required")
        if "evidence" not in event or not isinstance(event.get("evidence"), str):
            errors.append(f"schema_validation_error: event[{position}].evidence is required")
        if not any(key in event for key in ("fact", "event")):
            errors.append(f"schema_validation_error: event[{position}].fact is required")
        elif not isinstance(event.get("fact", event.get("event")), str):
            errors.append(f"schema_validation_error: event[{position}].fact must be text")
        if "attributes" in event and not isinstance(event.get("attributes"), Mapping):
            errors.append(
                f"schema_validation_error: event[{position}].attributes must be an object"
            )
    return errors


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
) -> tuple[Assertion[ExectEventContent], ...]:
    if isinstance(payload, list):
        events = payload
    elif isinstance(payload, Mapping) and isinstance(payload.get("clinical_events"), list):
        events = payload["clinical_events"]
    else:
        return ()
    assertions: list[Assertion[ExectEventContent]] = []
    for position, value in enumerate(events):
        if not isinstance(value, Mapping):
            continue
        raw_event = {str(key): _json_compatible(item) for key, item in value.items()}
        attributes = value.get("attributes")
        typed_attributes = (
            {str(key): _json_compatible(item) for key, item in attributes.items()}
            if isinstance(attributes, Mapping)
            else {}
        )
        quote = str(value.get("evidence") or "")
        start = _optional_int(value.get("evidence_start", value.get("start_char")))
        end = _optional_int(value.get("evidence_end", value.get("end_char")))
        assertions.append(
            Assertion(
                assertion_id=f"raw-event-{position}",
                content=ExectEventContent(
                    family=str(value.get("family") or value.get("clinical_family") or ""),
                    fact=str(value.get("fact") or value.get("event") or ""),
                    attributes=typed_attributes,
                    raw_event=raw_event,
                ),
                evidence=(
                    locate_text_evidence(
                        source,
                        quote,
                        start_char=start,
                        end_char=end,
                    ),
                ),
                producer="model",
                raw_position=position,
                provenance={"raw_event_position": position},
            )
        )
    return tuple(assertions)


def _require_request_source(
    request: PreparedExtractionRequest,
    source: SourceDocument,
) -> None:
    if request.task_id != "exectv2.key_entity_inventory":
        raise ValueError("request is not an ExECT key-entity extraction")
    if request.sources != (source.ref(),):
        raise ValueError("source identity does not match the prepared ExECT request")


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json_compatible(value: Any) -> JsonValue:
    return cast(JsonValue, json.loads(json.dumps(value, ensure_ascii=False)))


__all__ = [
    "EXECT_ARTIFACT_PROFILE_VERSION",
    "EXECT_ARTIFACT_SCHEMA_VERSION",
    "ExectEventContent",
    "ExectProjectionResult",
    "consume_exect_attempt",
    "exect_extraction_profile",
    "execute_exect_request",
    "family_inventory",
    "prepare_exect_request",
    "project_exect_artifact",
    "project_exect_artifact_with_trace",
    "replay_exect_response",
    "score_exect_artifact",
]
