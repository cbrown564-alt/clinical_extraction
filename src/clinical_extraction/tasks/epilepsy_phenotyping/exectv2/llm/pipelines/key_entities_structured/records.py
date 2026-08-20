"""Compact event records for the structured-event extractor."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from .constants import EventFamily


class CompactClinicalEvent(BaseModel):
    """One Compact finding: family, evidence, fact, and attributes."""

    model_config = ConfigDict(extra="ignore")

    family: EventFamily
    evidence: str
    fact: str
    attributes: dict[str, Any] = {}


class CompactExtractionRecord(BaseModel):
    """Compact output for one letter and for format-only retry."""

    model_config = ConfigDict(extra="ignore")

    clinical_events: list[CompactClinicalEvent] = []


StructuredExtractionRecord = CompactExtractionRecord


def format_retry_schema_for(prompt_version: str) -> dict[str, Any]:
    """JSON schema advertised to a format-only retry."""

    del prompt_version
    return CompactExtractionRecord.model_json_schema()
