"""Small public contracts for the source handoff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerationSettings:
    temperature: float = 0.0
    seed: int | None = 0
    max_completion_tokens: int = 16_000
    timeout_seconds: float = 300.0
    retry_count: int = 1
    thinking: bool = False
    reasoning_effort: str | None = None
    json_response_mode: str = "json_schema"


@dataclass(frozen=True)
class ModelResponse:
    content: str
    requested_model: str
    response_model: str | None = None
    reasoning_content_present: bool = False
    finish_reason: str | None = None
    structured_output_mode: str = "json_schema"
    request_attempts: int = 1
    usage: dict[str, int] = field(default_factory=dict)


class ModelClient(Protocol):
    def complete_json(
        self,
        *,
        messages: list[dict[str, str]],
        schema: dict[str, object],
        settings: GenerationSettings,
    ) -> ModelResponse: ...


@dataclass(frozen=True)
class WorkflowOutput:
    result: dict[str, Any]
    trace: dict[str, Any]
    model_response: ModelResponse

