from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AssertionStatus(StrEnum):
    ASSERTED = "asserted"
    NEGATED = "negated"
    HISTORICAL = "historical"
    HYPOTHETICAL = "hypothetical"
    UNKNOWN = "unknown"


class Temporality(StrEnum):
    CURRENT = "current"
    RECENT = "recent"
    HISTORICAL = "historical"
    FUTURE = "future"
    UNCLEAR = "unclear"


class Uncertainty(StrEnum):
    CERTAIN = "certain"
    UNCERTAIN = "uncertain"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(description="Shortest useful source quote supporting the extraction.")
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)


class SeizureEvent(BaseModel):
    raw_value: str
    evidence: str
    assertion_status: AssertionStatus = AssertionStatus.UNKNOWN
    temporality: Temporality = Temporality.UNCLEAR
    uncertainty: Uncertainty = Uncertainty.UNKNOWN
    normalized_value: str | None = None
    anchor_date: date | None = None


class FinalExtraction(BaseModel):
    final_value: str
    rationale: str
    evidence: str

