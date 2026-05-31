from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, Protocol, TypeVar

from pydantic import BaseModel, Field

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class Pipeline(Protocol[InputT, OutputT]):
    def run(self, item: InputT) -> OutputT:
        """Run one extraction item through the pipeline."""


class PipelineResult(BaseModel, Generic[OutputT]):
    output: OutputT
    diagnostics: Mapping[str, Any] = Field(default_factory=dict)

