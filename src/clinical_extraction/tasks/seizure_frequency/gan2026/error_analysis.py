from __future__ import annotations

from pydantic import BaseModel


class ErrorSlice(BaseModel):
    name: str
    count: int
    notes: str = ""

