"""Public runner boundary for selected ExECTv2 methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .data import ExectLetter
from .orchestration import rules
from .runners.naming import ActiveMethodName, active_method_name


@dataclass(frozen=True)
class Exectv2PipelineConfiguration:
    """Configuration for a selected ExECT method."""

    method: str = "rules"
    include_diagnosis_resolution_candidate: bool = False
    include_diagnosis_benchmark_residuals: bool = False


@dataclass(frozen=True)
class Exectv2RunResult:
    """Stable public result that keeps method identity beside the trace."""

    method: ActiveMethodName
    result: rules.RulesRecordResult

    def model_dump(self, *, mode: str = "python") -> dict[str, Any]:
        del mode
        return {
            "method": self.method,
            "prediction": self.result.prediction.model_dump(mode="json"),
            "comparison_projection": self.result.comparison_projection.model_dump(mode="json"),
            "stage_events": [event.to_dict() for event in self.result.stage_events],
        }


class Exectv2PipelineRunner:
    """Run one selected ExECT method through its canonical entry point."""

    def __init__(self, config: Exectv2PipelineConfiguration) -> None:
        self.config = config

    def run(self, letter: ExectLetter) -> Exectv2RunResult:
        method = active_method_name(self.config.method)
        if method != "rules":
            raise ValueError(
                "ExECT llm and llm_with_rules runners remain on the existing structured path; "
                "this vertical slice only exposes rules."
            )
        result = rules.run_letter(
            letter,
            include_diagnosis_resolution_candidate=(
                self.config.include_diagnosis_resolution_candidate
            ),
            include_diagnosis_benchmark_residuals=self.config.include_diagnosis_benchmark_residuals,
        )
        return Exectv2RunResult(method=method, result=result)


__all__ = [
    "Exectv2PipelineConfiguration",
    "Exectv2PipelineRunner",
    "Exectv2RunResult",
]
