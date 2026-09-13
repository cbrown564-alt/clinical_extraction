"""Artifact adapter for the existing longitudinal history/query implementation."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from typing import Any, Literal, cast

from clinical_extraction.core.artifacts import (
    Assertion,
    CoverageRecord,
    DecisionRecord,
    ExtractionArtifact,
    InferenceAttempt,
    JsonValue,
    PreparedExtractionRequest,
    PromptComponent,
    Relationship,
    SourceDocument,
    TaskProfile,
    canonical_json,
    freeze_json,
    locate_text_evidence,
)

from .history import link_assertions
from .queries import evaluate_query

LONGITUDINAL_ARTIFACT_SCHEMA_VERSION = "longitudinal.assertions.artifact.v1"
LONGITUDINAL_ARTIFACT_PROFILE_VERSION = "longitudinal.annotation-adapter.v1"
LONGITUDINAL_CAPTURE_FAMILIES = (
    "diagnosis",
    "seizure",
    "medication",
    "investigation",
)
QueryRelationshipMode = Literal["retained", "infer"]


@dataclass(frozen=True)
class LongitudinalAssertionContent:
    """All non-evidence fields of one existing longitudinal assertion."""

    family: str
    record: Mapping[str, JsonValue]

    def __post_init__(self) -> None:
        object.__setattr__(self, "record", freeze_json(self.record))


@dataclass(frozen=True)
class LongitudinalPolicyRequirement:
    policy_id: str
    policy_version: str
    required_families: tuple[str, ...]
    required_fields: tuple[str, ...]


POLICY_REQUIREMENTS: Mapping[str, LongitudinalPolicyRequirement] = {
    "Q1": LongitudinalPolicyRequirement(
        "longitudinal.Q1.diagnosis-and-event",
        "phase4.v1",
        ("diagnosis", "seizure"),
        ("time", "polarity", "certainty", "coverage"),
    ),
    "Q2": LongitudinalPolicyRequirement(
        "longitudinal.Q2.overlapping-patterns",
        "phase4.v1",
        ("seizure",),
        ("time", "polarity", "certainty", "coverage"),
    ),
    "Q3": LongitudinalPolicyRequirement(
        "longitudinal.Q3.medication-initiation",
        "phase4.v1",
        ("medication",),
        ("time", "polarity", "certainty", "coverage"),
    ),
    "Q4": LongitudinalPolicyRequirement(
        "longitudinal.Q4.investigation-window",
        "phase4.v1",
        ("investigation",),
        ("time", "polarity", "certainty", "coverage"),
    ),
    "Q5": LongitudinalPolicyRequirement(
        "longitudinal.Q5.reinterpretation",
        "phase4.v1",
        ("seizure",),
        ("time", "polarity", "certainty", "coverage"),
    ),
}


@cache
def longitudinal_artifact_profile() -> TaskProfile:
    """Profile for adapting the already-defined longitudinal assertion schema."""

    components = (
        PromptComponent.from_value(
            "annotation_schema",
            "longitudinal.annotation.schema.v0.3",
            {
                "capture_families": list(LONGITUDINAL_CAPTURE_FAMILIES),
                "evidence_offsets": "zero-based, end-exclusive",
                "source_accounts": "preserved",
            },
            rendered_paths=(),
        ),
    )
    return TaskProfile(
        task_id="longitudinal.epilepsy_history",
        profile_id="longitudinal.annotation-adapter",
        profile_version=LONGITUDINAL_ARTIFACT_PROFILE_VERSION,
        schema_version=LONGITUDINAL_ARTIFACT_SCHEMA_VERSION,
        capture_families=LONGITUDINAL_CAPTURE_FAMILIES,
        prompt_components=components,
        compatible_policies={
            requirement.policy_id: requirement.required_families
            for requirement in POLICY_REQUIREMENTS.values()
        },
    )


def source_documents_from_longitudinal(
    documents: Mapping[str, Mapping[str, Any]],
) -> dict[str, SourceDocument]:
    """Create versioned source views without changing document text or dates."""

    sources: dict[str, SourceDocument] = {}
    for source_id, document in documents.items():
        text = str(document["text"])
        recorded_hash = str(document.get("sha256") or "")
        version_id = f"sha256:{recorded_hash}" if recorded_hash else None
        metadata = {
            str(key): _json_compatible(value)
            for key, value in document.items()
            if key not in {"text", "sha256", "path"}
        }
        sources[source_id] = SourceDocument.from_text(
            source_id=source_id,
            text=text,
            version_id=version_id,
            metadata=metadata,
        )
    return sources


def build_longitudinal_artifact(
    documents: Mapping[str, Mapping[str, Any]],
    annotations: Mapping[str, Any],
    *,
    artifact_kind: str,
    query_independent_capture: bool,
    input_cutoff: str | None = None,
) -> ExtractionArtifact[LongitudinalAssertionContent]:
    """Adapt retained facts and links without changing their clinical fields."""

    selected_documents = {
        source_id: document
        for source_id, document in documents.items()
        if input_cutoff is None or str(document["available_date"]) <= input_cutoff
    }
    sources = source_documents_from_longitudinal(selected_documents)
    profile = longitudinal_artifact_profile()
    assertion_records = [
        record
        for record in _record_list(annotations.get("assertions"))
        if str(record.get("letter_id") or "") in sources
    ]
    retained_assertion_ids = {str(record.get("assertion_id") or "") for record in assertion_records}
    relationship_records = [
        record
        for record in _record_list(annotations.get("links"))
        if str(record.get("earlier_assertion") or "") in retained_assertion_ids
        and str(record.get("later_assertion") or "") in retained_assertion_ids
    ]
    captured_annotations = {
        **{
            str(key): _json_compatible(value)
            for key, value in annotations.items()
            if key not in {"assertions", "links"}
        },
        "assertions": assertion_records,
        "links": relationship_records,
    }
    adapter_input = {
        "adapter": profile.profile_id,
        "artifact_kind": artifact_kind,
        "query_independent_capture": query_independent_capture,
        "input_cutoff": input_cutoff,
        "sources": [source.ref().to_dict() for source in sources.values()],
    }
    request = PreparedExtractionRequest.create(
        profile=profile,
        sources=tuple(sources.values()),
        prompt_input_json=canonical_json(adapter_input),
        rendered_messages=(),
    )
    captured_annotations_json = canonical_json(captured_annotations)
    attempt = InferenceAttempt.captured(
        request=request,
        response_text=captured_annotations_json,
        attempt_id="annotation-adapter-1",
        kind="replay",
        provider_metadata={"artifact_kind": artifact_kind},
    )
    assertions = tuple(
        _assertion_from_record(record, sources=sources) for record in assertion_records
    )
    relationships = tuple(
        _relationship_from_record(record, sources=sources) for record in relationship_records
    )
    invalid_source_ids = {
        evidence.source.source_id
        for assertion in assertions
        for evidence in assertion.evidence
        if not evidence.location_valid
    }
    invalid_source_ids.update(
        evidence.source.source_id
        for relationship in relationships
        for evidence in relationship.evidence
        if not evidence.location_valid
    )
    present_families = tuple(sorted({assertion.content.family for assertion in assertions}))
    return ExtractionArtifact.create(
        status="failed" if invalid_source_ids else "ready",
        request=request,
        attempts=(attempt,),
        raw_payload=captured_annotations,
        assertions=assertions,
        relationships=relationships,
        coverage=CoverageRecord(
            capture_families=profile.capture_families,
            processed_source_ids=tuple(
                source_id for source_id in sources if source_id not in invalid_source_ids
            ),
            failed_source_ids=tuple(sorted(invalid_source_ids)),
            unsupported_fields=(),
            notes=(
                "Availability cutoffs are applied before linking and policy evaluation.",
                (
                    "Capture is reusable across declared queries."
                    if query_independent_capture
                    else "Capture is query-conditioned and cannot be reused across queries."
                ),
            ),
        ),
        diagnostics={
            "artifact_kind": artifact_kind,
            "query_independent_capture": query_independent_capture,
            "input_cutoff": input_cutoff,
            "observed_families": present_families,
            "excluded_source_ids": sorted(set(documents) - set(selected_documents)),
            "invalid_evidence_source_ids": sorted(invalid_source_ids),
        },
        compatibility_output=captured_annotations,
    )


def evaluate_artifact_query(
    artifact: ExtractionArtifact[LongitudinalAssertionContent],
    documents: Mapping[str, Mapping[str, Any]],
    request: Mapping[str, Any],
    *,
    relationship_mode: QueryRelationshipMode = "retained",
) -> DecisionRecord[dict[str, JsonValue]]:
    """Evaluate one declared query while preserving artifact bytes and cutoffs."""

    query_id = str(request.get("query_id") or "")
    requirement = POLICY_REQUIREMENTS.get(query_id)
    if requirement is None:
        return DecisionRecord(
            policy_id=f"longitudinal.{query_id or 'unknown'}",
            policy_version="unavailable",
            artifact_ids=(artifact.artifact_id,),
            parameters=_json_mapping(request),
            status="unsupported",
            result=None,
            unresolved_requirements=("unsupported_query_id",),
        )
    requested_cutoff = str(request.get("information_cutoff") or "")
    permitted_source_ids = {
        source_id
        for source_id, document in documents.items()
        if str(document["available_date"]) <= requested_cutoff
    }
    unavailable = _unavailable_requirements(
        artifact,
        requirement,
        permitted_source_ids=permitted_source_ids,
    )
    capture_is_independent = bool(artifact.diagnostics.get("query_independent_capture", False))
    saved_cutoff = artifact.diagnostics.get("input_cutoff")
    current_sources = source_documents_from_longitudinal(documents)
    artifact_sources = {source.source_id: source for source in artifact.request.sources}
    unavailable.extend(
        f"source_document_mismatch:{source_id}"
        for source_id, source in artifact_sources.items()
        if current_sources.get(source_id) is None or current_sources[source_id].ref() != source
    )
    unavailable.extend(
        f"source_not_captured:{source_id}"
        for source_id in sorted(permitted_source_ids - set(artifact_sources))
    )
    if not capture_is_independent and saved_cutoff != requested_cutoff:
        unavailable.append("query_conditioned_capture_for_different_cutoff")
    if not capture_is_independent:
        unavailable.append("query_conditioned_capture_not_reusable")
    if artifact.status != "ready":
        unavailable.append("failed_extraction_artifact")
    if unavailable:
        return DecisionRecord(
            policy_id=requirement.policy_id,
            policy_version=requirement.policy_version,
            artifact_ids=(artifact.artifact_id,),
            parameters=_json_mapping(request),
            status="unsupported",
            result=None,
            unresolved_requirements=tuple(dict.fromkeys(unavailable)),
        )

    annotations = _legacy_annotations(artifact)
    permitted = {
        source_id: dict(document)
        for source_id, document in documents.items()
        if str(document["available_date"]) <= requested_cutoff
    }
    if relationship_mode == "infer":
        facts = [
            assertion
            for assertion in annotations["assertions"]
            if assertion["letter_id"] in permitted
        ]
        annotations = {
            "assertions": facts,
            "links": link_assertions(facts, permitted),
        }
    result = evaluate_query(annotations, dict(documents), dict(request))
    source_lookup = source_documents_from_longitudinal(documents)
    evidence = tuple(
        locate_text_evidence(
            source_lookup[str(span["letter_id"])],
            str(span["text"]),
            start_char=int(span["start"]),
            end_char=int(span["end"]),
        )
        for span in result.get("evidence", [])
    )
    return DecisionRecord(
        policy_id=requirement.policy_id,
        policy_version=requirement.policy_version,
        artifact_ids=(artifact.artifact_id,),
        parameters=_json_mapping(request),
        status="ready",
        result=_json_mapping(result),
        evidence=evidence,
    )


def _assertion_from_record(
    record: Mapping[str, Any],
    *,
    sources: Mapping[str, SourceDocument],
) -> Assertion[LongitudinalAssertionContent]:
    content = record.get("content")
    family = str(content.get("family") if isinstance(content, Mapping) else "")
    non_evidence = {
        str(key): _json_compatible(value)
        for key, value in record.items()
        if key not in {"assertion_id", "evidence"}
    }
    evidence = tuple(
        _evidence_from_span(span, sources=sources) for span in _record_list(record.get("evidence"))
    )
    return Assertion(
        assertion_id=str(record["assertion_id"]),
        content=LongitudinalAssertionContent(family=family, record=non_evidence),
        evidence=evidence,
        producer="reference_or_saved_extraction",
        provenance={"legacy_assertion_id": str(record["assertion_id"])},
    )


def _relationship_from_record(
    record: Mapping[str, Any],
    *,
    sources: Mapping[str, SourceDocument],
) -> Relationship:
    evidence = tuple(
        _evidence_from_span(span, sources=sources) for span in _record_list(record.get("evidence"))
    )
    remainder = {
        str(key): _json_compatible(value)
        for key, value in record.items()
        if key
        not in {
            "link_id",
            "relation",
            "earlier_assertion",
            "later_assertion",
            "evidence",
        }
    }
    return Relationship(
        relationship_id=str(record["link_id"]),
        relation_type=str(record["relation"]),
        source_assertion_id=str(record["earlier_assertion"]),
        target_assertion_id=str(record["later_assertion"]),
        evidence=evidence,
        derivation_id=str(record.get("rule_id") or "reference"),
        provenance={"legacy_fields": remainder},
    )


def _evidence_from_span(
    span: Mapping[str, Any],
    *,
    sources: Mapping[str, SourceDocument],
):
    source = sources[str(span["letter_id"])]
    return locate_text_evidence(
        source,
        str(span["text"]),
        start_char=int(span["start"]),
        end_char=int(span["end"]),
    )


def _legacy_annotations(
    artifact: ExtractionArtifact[LongitudinalAssertionContent],
) -> dict[str, list[dict[str, Any]]]:
    assertions: list[dict[str, Any]] = []
    for assertion in artifact.assertions:
        row = cast(dict[str, Any], _thaw(assertion.content.record))
        row["assertion_id"] = assertion.assertion_id
        row["evidence"] = [_legacy_span(item) for item in assertion.evidence]
        assertions.append(row)
    links: list[dict[str, Any]] = []
    for relationship in artifact.relationships:
        legacy = relationship.provenance.get("legacy_fields", {})
        row = cast(dict[str, Any], _thaw(legacy))
        row.update(
            link_id=relationship.relationship_id,
            relation=relationship.relation_type,
            earlier_assertion=relationship.source_assertion_id,
            later_assertion=relationship.target_assertion_id,
            evidence=[_legacy_span(item) for item in relationship.evidence],
        )
        links.append(row)
    return {"assertions": assertions, "links": links}


def _legacy_span(value: Any) -> dict[str, Any]:
    if not value.location_valid or value.start_char is None or value.end_char is None:
        raise ValueError("longitudinal policy cannot consume unresolved evidence")
    return {
        "letter_id": value.source.source_id,
        "start": value.start_char,
        "end": value.end_char,
        "text": value.quote,
    }


def _unavailable_requirements(
    artifact: ExtractionArtifact[LongitudinalAssertionContent],
    requirement: LongitudinalPolicyRequirement,
    *,
    permitted_source_ids: set[str],
) -> list[str]:
    available_families = set(artifact.coverage.capture_families)
    unavailable = [
        f"capture_family:{family}"
        for family in requirement.required_families
        if family not in available_families
    ]
    for field_name in requirement.required_fields:
        relevant = [
            assertion
            for assertion in artifact.assertions
            if assertion.content.family in requirement.required_families
            and str(assertion.content.record.get("letter_id") or "") in permitted_source_ids
        ]
        if relevant and any(field_name not in assertion.content.record for assertion in relevant):
            unavailable.append(f"assertion_field:{field_name}")
    return unavailable


def _record_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _json_mapping(value: Mapping[str, Any]) -> dict[str, JsonValue]:
    return {str(key): _json_compatible(item) for key, item in value.items()}


def _json_compatible(value: Any) -> JsonValue:
    return cast(JsonValue, json.loads(json.dumps(value, ensure_ascii=False)))


def _thaw(value: Any) -> Any:
    return json.loads(canonical_json(value))


__all__ = [
    "LONGITUDINAL_ARTIFACT_PROFILE_VERSION",
    "LONGITUDINAL_ARTIFACT_SCHEMA_VERSION",
    "LongitudinalAssertionContent",
    "build_longitudinal_artifact",
    "evaluate_artifact_query",
    "longitudinal_artifact_profile",
    "source_documents_from_longitudinal",
]


def load_longitudinal_artifact(
    record: Mapping[str, Any],
) -> ExtractionArtifact[LongitudinalAssertionContent]:
    """Restore task-owned content from the common immutable artifact format."""
    from clinical_extraction.core.artifact_store import artifact_from_record

    return artifact_from_record(
        record, content_decoder=lambda value: LongitudinalAssertionContent(**value)
    )
