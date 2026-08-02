"""Typed boundaries for the Gan 2026 canonical orchestrators."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


@dataclass(frozen=True)
class GanStageEvent:
    """One observable stage transition in a canonical Gan record run."""

    stage_id: str
    owner: str
    effect_class: str
    input_value: Any = None
    output_value: Any = None
    changed: bool = False
    action: str = ""
    rule_category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "owner": self.owner,
            "effect_class": self.effect_class,
            "input_value": self.input_value,
            "output_value": self.output_value,
            "changed": self.changed,
            "action": self.action,
            "rule_category": self.rule_category,
        }


@dataclass(frozen=True)
class GanModelOutput:
    """Repository-owned model boundary value used by live and replay sources."""

    raw_output: str
    reused: bool = False
    call_error: str | None = None
    provider_metadata: Mapping[str, Any] = field(default_factory=dict)


class ModelOutputSource(Protocol):
    """Read one model result without exposing provider SDK objects downstream."""

    def read(
        self,
        record: GanRecord,
        *,
        prompt_input_json: str,
        config: PipelineConfiguration,
    ) -> GanModelOutput: ...


@dataclass(frozen=True)
class GanRecordResult:
    """Complete canonical result plus the evidence needed to audit its stages."""

    output: FinalExtraction
    diagnostics: Mapping[str, Any]
    stage_events: tuple[GanStageEvent, ...] = ()
    raw_model_output: str | None = None
    parsed_model_output: Any = None
    deterministic_output: Any = None
    first_prediction_changing_owner: str | None = None
    first_failure: str | None = None
    scorer_projection: Mapping[str, Any] = field(default_factory=dict)

    def to_pipeline_result(self) -> PipelineResult[FinalExtraction]:
        """Preserve the historical adapter shape without dropping typed trace data."""

        return PipelineResult(output=self.output, diagnostics=dict(self.diagnostics))
