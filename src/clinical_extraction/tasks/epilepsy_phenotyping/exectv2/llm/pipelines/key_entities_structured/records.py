"""Pydantic record models for the structured-event extractor.

Pure relocation of the model definitions from
``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from .constants import (
    EventFamily,
)


class RenderedMentionRecord(BaseModel):
    """One scorer-facing mention rendered from a structured clinical event."""

    model_config = ConfigDict(extra="ignore")

    entity: str
    text: str
    attributes: dict[str, Any] = {}


class StructuredClinicalEvent(BaseModel):
    """One source-near clinical event with one or more scorer-facing renderings."""

    model_config = ConfigDict(extra="ignore")

    family: EventFamily
    anchor_text: str
    evidence: str
    event_state: dict[str, Any] = {}
    mentions: list[RenderedMentionRecord] = []
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class StructuredExtractionRecord(BaseModel):
    """Structured output for one letter."""

    model_config = ConfigDict(extra="ignore")

    clinical_events: list[StructuredClinicalEvent] = []


class MentionForEvidence(BaseModel):
    """Minimal mention shape accepted by the shared evidence gate."""

    text: str
    attributes: dict[str, str] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""
    entity: str = ""
