from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(description="Shortest useful source quote supporting the extraction.")
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)


class FinalExtraction(BaseModel):
    final_value: str
    rationale: str
    evidence: str
