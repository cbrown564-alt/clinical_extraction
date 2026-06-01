from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, Protocol, TypeVar

from pydantic import BaseModel, Field

InputT = TypeVar("InputT", contravariant=True)
OutputT = TypeVar("OutputT", covariant=True)
ResultT = TypeVar("ResultT")


class Pipeline(Protocol[InputT, OutputT]):
    def run(self, item: InputT) -> OutputT:
        """Run one extraction item through the pipeline."""


class PipelineResult(BaseModel, Generic[ResultT]):
    output: ResultT
    diagnostics: Mapping[str, Any] = Field(default_factory=dict)
