"""Task-neutral source, request, artifact, and lifecycle records.

These records sit beside the historical benchmark result types.  They preserve
the model-visible source and response before task-owned compatibility parsing or
clinical projection takes place.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, Generic, Literal, TypeVar, cast

from pydantic import BaseModel

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
ContentT = TypeVar("ContentT")
DecisionT = TypeVar("DecisionT")


class FrozenJsonMap(Mapping[str, Any]):
    """Small immutable mapping used inside frozen provenance records."""

    __slots__ = ("_items",)

    def __init__(self, values: Mapping[str, Any]) -> None:
        self._items = tuple((str(key), value) for key, value in values.items())

    def __getitem__(self, key: str) -> Any:
        for candidate, value in self._items:
            if candidate == key:
                return value
        raise KeyError(key)

    def __iter__(self):
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __deepcopy__(self, _memo: dict[int, Any]) -> FrozenJsonMap:
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return False
        return _json_value(self) == _json_value(other)

    def __repr__(self) -> str:
        return f"FrozenJsonMap({dict(self._items)!r})"


def freeze_json(value: Any) -> Any:
    """Return a deeply immutable JSON-compatible value."""

    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Enum):
        return freeze_json(value.value)
    if isinstance(value, BaseModel):
        return freeze_json(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return freeze_json(asdict(value))
    if isinstance(value, Mapping):
        return FrozenJsonMap(
            {str(key): freeze_json(item) for key, item in value.items()}
        )
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return tuple(freeze_json(item) for item in value)
    raise TypeError(f"value is not JSON serializable: {type(value).__name__}")


def sha256_bytes(value: bytes) -> str:
    """Return a lower-case SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    """Hash UTF-8 text exactly as supplied."""

    return sha256_bytes(value.encode("utf-8"))


def canonical_json(value: Any) -> str:
    """Serialize a record deterministically for identity and manifests."""

    return json.dumps(_json_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


@dataclass(frozen=True)
class SourceRef:
    """Identity of the exact text view used by a request."""

    source_id: str
    version_id: str
    original_content_sha256: str
    text_sha256: str
    metadata_sha256: str

    def to_dict(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], asdict(self))


@dataclass(frozen=True)
class SourceDocument:
    """A source and its immutable model-visible text view.

    ``original_content_sha256`` may identify bytes before ingestion cleanup;
    evidence offsets always address ``text`` and ``text_sha256``.
    """

    source_id: str
    version_id: str
    text: str = field(repr=False)
    original_content_sha256: str
    text_sha256: str
    media_type: str = "text/plain"
    metadata: Mapping[str, JsonValue] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.version_id.strip():
            raise ValueError("source_id and version_id must be non-empty")
        if sha256_text(self.text) != self.text_sha256:
            raise ValueError("text_sha256 does not match the supplied model-visible text")
        object.__setattr__(self, "metadata", freeze_json(self.metadata))

    @classmethod
    def from_text(
        cls,
        *,
        source_id: str,
        text: str,
        version_id: str | None = None,
        original_bytes: bytes | None = None,
        media_type: str = "text/plain",
        metadata: Mapping[str, JsonValue] | None = None,
    ) -> SourceDocument:
        original = original_bytes if original_bytes is not None else text.encode("utf-8")
        original_hash = sha256_bytes(original)
        return cls(
            source_id=source_id,
            version_id=version_id or f"sha256:{original_hash}",
            text=text,
            original_content_sha256=original_hash,
            text_sha256=sha256_text(text),
            media_type=media_type,
            metadata=dict(metadata or {}),
        )

    def ref(self) -> SourceRef:
        return SourceRef(
            source_id=self.source_id,
            version_id=self.version_id,
            original_content_sha256=self.original_content_sha256,
            text_sha256=self.text_sha256,
            metadata_sha256=sha256_json(self.metadata),
        )

    def to_dict(self, *, include_text: bool = True) -> dict[str, JsonValue]:
        record: dict[str, JsonValue] = {
            **self.ref().to_dict(),
            "media_type": self.media_type,
            "metadata": cast(dict[str, JsonValue], _json_value(self.metadata)),
        }
        if include_text:
            record["text"] = self.text
        return record


EvidenceLocationStatus = Literal[
    "exact",
    "unique_exact_match",
    "ambiguous",
    "not_found",
    "invalid_offsets",
    "empty",
]


@dataclass(frozen=True)
class EvidenceRef:
    """Evidence location tied to one immutable source text view."""

    source: SourceRef
    quote: str
    start_char: int | None
    end_char: int | None
    location_status: EvidenceLocationStatus
    supplied_start_char: int | None = None
    supplied_end_char: int | None = None

    @property
    def location_valid(self) -> bool:
        return self.location_status in {"exact", "unique_exact_match"}

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "source": self.source.to_dict(),
            "quote": self.quote,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "location_status": self.location_status,
            "supplied_start_char": self.supplied_start_char,
            "supplied_end_char": self.supplied_end_char,
        }


def locate_text_evidence(
    source: SourceDocument,
    quote: str,
    *,
    start_char: int | None = None,
    end_char: int | None = None,
) -> EvidenceRef:
    """Locate an exact quote without silently choosing among repeated matches."""

    if not quote:
        return EvidenceRef(source.ref(), quote, None, None, "empty", start_char, end_char)
    if start_char is not None or end_char is not None:
        if (
            start_char is not None
            and end_char is not None
            and 0 <= start_char < end_char <= len(source.text)
            and source.text[start_char:end_char] == quote
        ):
            return EvidenceRef(
                source.ref(), quote, start_char, end_char, "exact", start_char, end_char
            )
        matches = _exact_match_offsets(source.text, quote)
        if len(matches) == 1:
            resolved_start, resolved_end = matches[0]
            return EvidenceRef(
                source.ref(),
                quote,
                resolved_start,
                resolved_end,
                "unique_exact_match",
                start_char,
                end_char,
            )
        return EvidenceRef(
            source.ref(),
            quote,
            None,
            None,
            "ambiguous" if matches else "invalid_offsets",
            start_char,
            end_char,
        )
    matches = _exact_match_offsets(source.text, quote)
    if len(matches) == 1:
        resolved_start, resolved_end = matches[0]
        return EvidenceRef(
            source.ref(), quote, resolved_start, resolved_end, "unique_exact_match"
        )
    return EvidenceRef(
        source.ref(), quote, None, None, "ambiguous" if matches else "not_found"
    )


@dataclass(frozen=True)
class PromptComponent:
    """Inspectable, versioned logical component of a rendered prompt."""

    component_id: str
    version: str
    content: JsonValue = field(repr=False)
    content_sha256: str = ""
    rendered_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "content", freeze_json(self.content))
        expected = sha256_json(self.content)
        if self.content_sha256 and self.content_sha256 != expected:
            raise ValueError(f"component hash mismatch for {self.component_id}")
        if not self.content_sha256:
            object.__setattr__(self, "content_sha256", expected)

    @classmethod
    def from_value(
        cls,
        component_id: str,
        version: str,
        content: Any,
        *,
        rendered_paths: Sequence[str] = (),
    ) -> PromptComponent:
        return cls(
            component_id=component_id,
            version=version,
            content=_json_value(content),
            rendered_paths=tuple(rendered_paths),
        )

    def to_dict(self, *, include_content: bool = True) -> dict[str, JsonValue]:
        record: dict[str, JsonValue] = {
            "component_id": self.component_id,
            "version": self.version,
            "content_sha256": self.content_sha256,
            "rendered_paths": list(self.rendered_paths),
        }
        if include_content:
            record["content"] = _json_value(self.content)
        return record


@dataclass(frozen=True)
class TaskProfile:
    """Capture scope and prompt/schema identity for one extraction task."""

    task_id: str
    profile_id: str
    profile_version: str
    schema_version: str
    capture_families: tuple[str, ...]
    prompt_components: tuple[PromptComponent, ...]
    compatible_policies: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        component_ids = [component.component_id for component in self.prompt_components]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("task profile component ids must be unique")
        object.__setattr__(self, "compatible_policies", freeze_json(self.compatible_policies))

    @property
    def components_sha256(self) -> str:
        return sha256_json(
            [component.to_dict(include_content=False) for component in self.prompt_components]
        )

    def to_dict(self, *, include_component_content: bool = True) -> dict[str, JsonValue]:
        return {
            "task_id": self.task_id,
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "schema_version": self.schema_version,
            "capture_families": list(self.capture_families),
            "prompt_components": [
                component.to_dict(include_content=include_component_content)
                for component in self.prompt_components
            ],
            "components_sha256": self.components_sha256,
            "compatible_policies": {
                key: list(value) for key, value in self.compatible_policies.items()
            },
        }


@dataclass(frozen=True)
class PreparedExtractionRequest:
    """Exact model request plus all identities required to replay it."""

    request_id: str
    task_id: str
    profile_id: str
    profile_version: str
    schema_version: str
    sources: tuple[SourceRef, ...]
    prompt_input_json: str = field(repr=False)
    prompt_input_sha256: str
    rendered_messages: tuple[Mapping[str, JsonValue], ...] = field(repr=False)
    rendered_messages_sha256: str
    prompt_components: tuple[PromptComponent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rendered_messages",
            tuple(freeze_json(message) for message in self.rendered_messages),
        )

    @classmethod
    def create(
        cls,
        *,
        profile: TaskProfile,
        sources: Sequence[SourceDocument],
        prompt_input_json: str,
        rendered_messages: Sequence[Mapping[str, Any]],
    ) -> PreparedExtractionRequest:
        source_refs = tuple(source.ref() for source in sources)
        messages = tuple(
            cast(Mapping[str, JsonValue], _json_value(message)) for message in rendered_messages
        )
        prompt_hash = sha256_text(prompt_input_json)
        messages_hash = sha256_json(messages)
        identity = {
            "task_id": profile.task_id,
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
            "schema_version": profile.schema_version,
            "sources": [source.to_dict() for source in source_refs],
            "prompt_input_sha256": prompt_hash,
            "rendered_messages_sha256": messages_hash,
            "components_sha256": profile.components_sha256,
        }
        return cls(
            request_id=f"request:{sha256_json(identity)}",
            task_id=profile.task_id,
            profile_id=profile.profile_id,
            profile_version=profile.profile_version,
            schema_version=profile.schema_version,
            sources=source_refs,
            prompt_input_json=prompt_input_json,
            prompt_input_sha256=prompt_hash,
            rendered_messages=messages,
            rendered_messages_sha256=messages_hash,
            prompt_components=profile.prompt_components,
        )

    def to_dict(self, *, include_prompt: bool = True) -> dict[str, JsonValue]:
        record: dict[str, JsonValue] = {
            "request_id": self.request_id,
            "task_id": self.task_id,
            "profile_id": self.profile_id,
            "profile_version": self.profile_version,
            "schema_version": self.schema_version,
            "sources": [source.to_dict() for source in self.sources],
            "prompt_input_sha256": self.prompt_input_sha256,
            "rendered_messages_sha256": self.rendered_messages_sha256,
            "prompt_components": [
                component.to_dict(include_content=include_prompt)
                for component in self.prompt_components
            ],
        }
        if include_prompt:
            record["prompt_input_json"] = self.prompt_input_json
            record["rendered_messages"] = [
                cast(dict[str, JsonValue], _json_value(message))
                for message in self.rendered_messages
            ]
        return record


AttemptStatus = Literal["captured", "provider_error", "not_run"]
AttemptKind = Literal["primary", "format_retry", "replay"]


@dataclass(frozen=True)
class InferenceAttempt:
    """One provider or replay attempt; empty output remains an explicit capture."""

    attempt_id: str
    request_id: str
    kind: AttemptKind
    status: AttemptStatus
    response_text: str = field(default="", repr=False)
    response_sha256: str = ""
    error_type: str | None = None
    error_message: str | None = None
    provider_metadata: Mapping[str, JsonValue] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        expected = sha256_text(self.response_text)
        if self.response_sha256 and self.response_sha256 != expected:
            raise ValueError("response_sha256 does not match response_text")
        if not self.response_sha256:
            object.__setattr__(self, "response_sha256", expected)
        if self.status == "provider_error" and not self.error_message:
            raise ValueError("provider_error attempts require an error message")
        object.__setattr__(self, "provider_metadata", freeze_json(self.provider_metadata))

    @classmethod
    def captured(
        cls,
        *,
        request: PreparedExtractionRequest,
        response_text: str,
        attempt_id: str = "attempt-1",
        kind: AttemptKind = "primary",
        provider_metadata: Mapping[str, JsonValue] | None = None,
    ) -> InferenceAttempt:
        return cls(
            attempt_id=attempt_id,
            request_id=request.request_id,
            kind=kind,
            status="captured",
            response_text=response_text,
            provider_metadata=dict(provider_metadata or {}),
        )

    @classmethod
    def failed(
        cls,
        *,
        request: PreparedExtractionRequest,
        error: BaseException | str,
        attempt_id: str = "attempt-1",
        kind: AttemptKind = "primary",
        provider_metadata: Mapping[str, JsonValue] | None = None,
    ) -> InferenceAttempt:
        if isinstance(error, BaseException):
            error_type = type(error).__name__
            error_message = str(error) or error_type
        else:
            error_type = "provider_error"
            error_message = error or error_type
        return cls(
            attempt_id=attempt_id,
            request_id=request.request_id,
            kind=kind,
            status="provider_error",
            error_type=error_type,
            error_message=error_message,
            provider_metadata=dict(provider_metadata or {}),
        )

    def to_dict(self, *, include_response: bool = True) -> dict[str, JsonValue]:
        record: dict[str, JsonValue] = {
            "attempt_id": self.attempt_id,
            "request_id": self.request_id,
            "kind": self.kind,
            "status": self.status,
            "response_sha256": self.response_sha256,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "provider_metadata": cast(
                dict[str, JsonValue], _json_value(self.provider_metadata)
            ),
        }
        if include_response:
            record["response_text"] = self.response_text
        return record


def replay_attempt(
    request: PreparedExtractionRequest,
    *,
    saved_request_id: str,
    response_text: str,
    attempt_id: str = "replay-1",
    provider_metadata: Mapping[str, JsonValue] | None = None,
) -> InferenceAttempt:
    """Create a no-call replay attempt only when the exact request matches."""

    if saved_request_id != request.request_id:
        raise ValueError(
            "saved response request identity does not match the prepared extraction request"
        )
    return InferenceAttempt.captured(
        request=request,
        response_text=response_text,
        attempt_id=attempt_id,
        kind="replay",
        provider_metadata=provider_metadata,
    )


@dataclass(frozen=True)
class Assertion(Generic[ContentT]):
    """Artifact-scoped typed assertion with source-versioned evidence."""

    assertion_id: str
    content: ContentT
    evidence: tuple[EvidenceRef, ...]
    producer: str
    raw_position: int | None = None
    provenance: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", freeze_json(self.provenance))

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "assertion_id": self.assertion_id,
            "content": _json_value(self.content),
            "evidence": [item.to_dict() for item in self.evidence],
            "producer": self.producer,
            "raw_position": self.raw_position,
            "provenance": cast(dict[str, JsonValue], _json_value(self.provenance)),
        }


@dataclass(frozen=True)
class Relationship:
    """A domain-owned relationship between retained assertion identities."""

    relationship_id: str
    relation_type: str
    source_assertion_id: str
    target_assertion_id: str
    evidence: tuple[EvidenceRef, ...] = ()
    derivation_id: str = ""
    provenance: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", freeze_json(self.provenance))

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "relationship_id": self.relationship_id,
            "relation_type": self.relation_type,
            "source_assertion_id": self.source_assertion_id,
            "target_assertion_id": self.target_assertion_id,
            "evidence": [item.to_dict() for item in self.evidence],
            "derivation_id": self.derivation_id,
            "provenance": cast(dict[str, JsonValue], _json_value(self.provenance)),
        }


@dataclass(frozen=True)
class CoverageRecord:
    """Declared capture capability and source processing outcome."""

    capture_families: tuple[str, ...]
    processed_source_ids: tuple[str, ...]
    failed_source_ids: tuple[str, ...] = ()
    unsupported_fields: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], _json_value(asdict(self)))


ArtifactStatus = Literal["ready", "failed"]


@dataclass(frozen=True)
class ExtractionArtifact(Generic[ContentT]):
    """Original response plus derived typed assertions and compatibility output."""

    artifact_id: str
    status: ArtifactStatus
    request: PreparedExtractionRequest
    attempts: tuple[InferenceAttempt, ...]
    raw_payload: JsonValue
    assertions: tuple[Assertion[ContentT], ...]
    relationships: tuple[Relationship, ...]
    coverage: CoverageRecord
    diagnostics: Mapping[str, JsonValue] = field(default_factory=dict)
    compatibility_output: JsonValue = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_payload", freeze_json(self.raw_payload))
        object.__setattr__(self, "diagnostics", freeze_json(self.diagnostics))
        object.__setattr__(self, "compatibility_output", freeze_json(self.compatibility_output))

    @classmethod
    def create(
        cls,
        *,
        status: ArtifactStatus,
        request: PreparedExtractionRequest,
        attempts: Sequence[InferenceAttempt],
        raw_payload: Any,
        assertions: Sequence[Assertion[ContentT]],
        coverage: CoverageRecord,
        relationships: Sequence[Relationship] = (),
        diagnostics: Mapping[str, Any] | None = None,
        compatibility_output: Any = None,
    ) -> ExtractionArtifact[ContentT]:
        attempt_tuple = tuple(attempts)
        for attempt in attempt_tuple:
            if attempt.request_id != request.request_id:
                raise ValueError("artifact attempt does not belong to its request")
        identity = {
            "status": status,
            "request_id": request.request_id,
            "attempts": [attempt.to_dict(include_response=False) for attempt in attempt_tuple],
            "response_hashes": [attempt.response_sha256 for attempt in attempt_tuple],
            "raw_payload": raw_payload,
            "assertions": [assertion.to_dict() for assertion in assertions],
            "relationships": [relationship.to_dict() for relationship in relationships],
            "coverage": coverage.to_dict(),
            "diagnostics": diagnostics or {},
            "compatibility_output": compatibility_output,
        }
        return cls(
            artifact_id=f"artifact:{sha256_json(identity)}",
            status=status,
            request=request,
            attempts=attempt_tuple,
            raw_payload=_json_value(raw_payload),
            assertions=tuple(assertions),
            relationships=tuple(relationships),
            coverage=coverage,
            diagnostics=cast(Mapping[str, JsonValue], _json_value(diagnostics or {})),
            compatibility_output=_json_value(compatibility_output),
        )

    def to_dict(self, *, include_payloads: bool = True) -> dict[str, JsonValue]:
        record: dict[str, JsonValue] = {
            "artifact_id": self.artifact_id,
            "status": self.status,
            "request": self.request.to_dict(include_prompt=include_payloads),
            "attempts": [
                attempt.to_dict(include_response=include_payloads) for attempt in self.attempts
            ],
            "assertions": [assertion.to_dict() for assertion in self.assertions],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "coverage": self.coverage.to_dict(),
            "diagnostics": cast(dict[str, JsonValue], _json_value(self.diagnostics)),
        }
        if include_payloads:
            record["raw_payload"] = _json_value(self.raw_payload)
            record["compatibility_output"] = _json_value(self.compatibility_output)
        return record

    @property
    def content_sha256(self) -> str:
        return sha256_json(self.to_dict(include_payloads=True))


@dataclass(frozen=True)
class DecisionRecord(Generic[DecisionT]):
    """Immutable downstream policy result over saved extraction artifacts."""

    policy_id: str
    policy_version: str
    artifact_ids: tuple[str, ...]
    parameters: Mapping[str, JsonValue]
    status: Literal["ready", "unsupported", "failed"]
    result: DecisionT | None
    evidence: tuple[EvidenceRef, ...] = ()
    unresolved_requirements: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_json(self.parameters))
        if self.result is not None:
            object.__setattr__(self, "result", freeze_json(self.result))

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "artifact_ids": list(self.artifact_ids),
            "parameters": cast(dict[str, JsonValue], _json_value(self.parameters)),
            "status": self.status,
            "result": _json_value(self.result),
            "evidence": [item.to_dict() for item in self.evidence],
            "unresolved_requirements": list(self.unresolved_requirements),
        }


@dataclass(frozen=True)
class ExecutionConfiguration:
    """Provider/runtime settings kept outside task-owned clinical code."""

    runtime_id: str
    provider: str
    model: str
    model_revision: str = ""
    temperature: float = 0.0
    max_tokens: int = 0
    retry_limit: int = 0
    hardware: str = "unreported"
    quantisation: str = "unreported"
    settings: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", freeze_json(self.settings))

    def to_dict(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], _json_value(asdict(self)))


@dataclass(frozen=True)
class LifecycleManifest:
    """Portable manifest for one artifact without imposing a common scorer."""

    manifest_version: str
    artifact_id: str
    task_id: str
    profile_id: str
    schema_version: str
    prompt_components_sha256: str
    program_version: str
    scorer_version: str | None
    dataset_id: str | None
    split: str | None
    row_policy: str | None
    source_hashes: Mapping[str, str]
    output_hashes: Mapping[str, str]
    runtime: ExecutionConfiguration
    replay_mode: str
    call_count: int
    failure_count: int
    total_latency_ms: float | None
    input_tokens: int | None
    output_tokens: int | None
    cost: float | None
    cost_currency: str | None
    format_changes: tuple[str, ...] = ()
    semantic_changes: tuple[str, ...] = ()
    reviewer_decisions: tuple[str, ...] = ()
    artifact_visibility: str = "local"

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_hashes", freeze_json(self.source_hashes))
        object.__setattr__(self, "output_hashes", freeze_json(self.output_hashes))

    def to_dict(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], _json_value(asdict(self)))


def lifecycle_manifest_from_artifact(
    artifact: ExtractionArtifact[Any],
    *,
    runtime: ExecutionConfiguration,
    program_version: str,
    replay_mode: str,
    scorer_version: str | None = None,
    dataset_id: str | None = None,
    split: str | None = None,
    row_policy: str | None = None,
    format_changes: Sequence[str] = (),
    semantic_changes: Sequence[str] = (),
    reviewer_decisions: Sequence[str] = (),
    artifact_visibility: str = "local",
) -> LifecycleManifest:
    """Adapt one artifact to the common lifecycle without reading source paths."""

    expected_runtime = runtime.to_dict()
    for attempt in artifact.attempts:
        captured_runtime = attempt.provider_metadata.get("runtime")
        if captured_runtime is not None and canonical_json(captured_runtime) != canonical_json(
            expected_runtime
        ):
            raise ValueError(
                "lifecycle runtime does not match the runtime captured with the attempt"
            )
    total_latency_ms = _sum_attempt_number(artifact.attempts, "latency_ms", float)
    input_tokens = cast(
        int | None, _sum_attempt_number(artifact.attempts, "input_tokens", int)
    )
    output_tokens = cast(
        int | None, _sum_attempt_number(artifact.attempts, "output_tokens", int)
    )
    cost = _sum_attempt_number(artifact.attempts, "cost", float)
    currencies = {
        value
        for attempt in artifact.attempts
        if isinstance((value := attempt.provider_metadata.get("cost_currency")), str)
        and value
    }

    return LifecycleManifest(
        manifest_version="clinical-extraction.lifecycle.v1",
        artifact_id=artifact.artifact_id,
        task_id=artifact.request.task_id,
        profile_id=artifact.request.profile_id,
        schema_version=artifact.request.schema_version,
        prompt_components_sha256=sha256_json(
            [
                component.to_dict(include_content=False)
                for component in artifact.request.prompt_components
            ]
        ),
        program_version=program_version,
        scorer_version=scorer_version,
        dataset_id=dataset_id,
        split=split,
        row_policy=row_policy,
        source_hashes={source.source_id: source.text_sha256 for source in artifact.request.sources},
        output_hashes={
            "artifact": artifact.content_sha256,
            **{
                f"attempt:{attempt.attempt_id}": attempt.response_sha256
                for attempt in artifact.attempts
            },
        },
        runtime=runtime,
        replay_mode=replay_mode,
        call_count=sum(attempt.kind != "replay" for attempt in artifact.attempts),
        failure_count=(
            sum(attempt.status != "captured" for attempt in artifact.attempts)
            + int(
                artifact.status == "failed"
                and all(attempt.status == "captured" for attempt in artifact.attempts)
            )
        ),
        total_latency_ms=total_latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        cost_currency=next(iter(currencies)) if len(currencies) == 1 else None,
        format_changes=tuple(format_changes),
        semantic_changes=tuple(semantic_changes),
        reviewer_decisions=tuple(reviewer_decisions),
        artifact_visibility=artifact_visibility,
    )


def _sum_attempt_number(
    attempts: Sequence[InferenceAttempt],
    key: str,
    result_type: type[int] | type[float],
) -> int | float | None:
    values = [
        value
        for attempt in attempts
        if isinstance((value := attempt.provider_metadata.get(key)), int | float)
        and not isinstance(value, bool)
    ]
    if not values:
        return None
    return result_type(sum(values))


def _exact_match_offsets(text: str, quote: str) -> list[tuple[int, int]]:
    matches: list[tuple[int, int]] = []
    start = 0
    while True:
        found = text.find(quote, start)
        if found < 0:
            return matches
        matches.append((found, found + len(quote)))
        start = found + 1


def _json_value(value: Any) -> JsonValue:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Enum):
        return _json_value(value.value)
    if isinstance(value, BaseModel):
        return _json_value(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_json_value(item) for item in value]
    raise TypeError(f"value is not JSON serializable: {type(value).__name__}")
