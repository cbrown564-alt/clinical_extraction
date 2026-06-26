"""Type aliases for target-indicator projection (no LLM imports)."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar


class MentionLike(Protocol):
    """Minimal mention interface used by evidence repair."""

    entity: str
    text: str
    evidence: str
    attributes: dict[str, Any]
    confidence: str
    rationale: str

    def model_copy(self, *, update: dict[str, Any]) -> Any: ...


MentionT = TypeVar("MentionT", bound=MentionLike)
