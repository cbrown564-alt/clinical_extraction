from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: str = "error"


class ValidationResult(BaseModel):
    ok: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
