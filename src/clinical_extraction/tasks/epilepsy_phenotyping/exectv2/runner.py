"""Public runner boundary for selected ExECTv2 methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .data import ExectLetter
from .llm.pipelines.key_entities_structured.constants import PromptProfile
from .orchestration import rules, structured_one_call
from .orchestration.contracts import StructuredMethodConfig
from .runners.naming import ActiveMethodName, active_method_name


@dataclass(frozen=True)
class Exectv2PipelineConfiguration:
    """Configuration for a selected ExECT method."""

    method: str = "rules"
    include_diagnosis_resolution_candidate: bool = False
    include_diagnosis_benchmark_residuals: bool = False
    model: str = ""
    temperature: float = 0.0
    max_tokens: int = 900
    mode: Literal["live", "prompt-only", "replay"] = "prompt-only"
    raw_output: str | None = None
    api_base: str | None = None
    api_key: str | None = None
    timeout: int | None = None
    route: str | None = None
    dspy_cache: bool = True
    program: Any | None = None
    format_retry_program: Any | None = None
    split: str = "dev"
    prompt_profile: PromptProfile = "full"


@dataclass(frozen=True)
class Exectv2RunResult:
    """Stable public result that keeps method identity beside the trace."""

    method: ActiveMethodName
    result: Any

    def model_dump(self, *, mode: str = "python") -> dict[str, Any]:
        del mode
        return {
            "method": self.method,
            "prediction": self.result.prediction.model_dump(mode="json"),
            "comparison_projection": (
                self.result.comparison_projection.model_dump(mode="json")
                if hasattr(self.result, "comparison_projection")
                else self.result.scorer_projection
            ),
            "stage_events": [event.to_dict() for event in self.result.stage_events],
        }


class Exectv2PipelineRunner:
    """Run one selected ExECT method through its canonical entry point."""

    def __init__(self, config: Exectv2PipelineConfiguration) -> None:
        self.config = config

    def run(self, letter: ExectLetter) -> Exectv2RunResult:
        method = active_method_name(self.config.method)
        result: Any
        if method == "rules":
            result = rules.run_letter(
                letter,
                include_diagnosis_resolution_candidate=(
                    self.config.include_diagnosis_resolution_candidate
                ),
                include_diagnosis_benchmark_residuals=self.config.include_diagnosis_benchmark_residuals,
            )
        elif method == "llm":
            if self.config.mode not in {"live", "prompt-only", "replay"}:
                raise ValueError("ExECT llm mode must be live, prompt-only, or replay")
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                mode=self.config.mode,
                raw_output=self.config.raw_output,
                api_base=(
                    self.config.route
                    if self.config.route is not None
                    else self.config.api_base
                ),
                api_key=self.config.api_key,
                timeout=self.config.timeout,
                dspy_cache=self.config.dspy_cache,
                split=self.config.split,
                program=self.config.program,
                format_retry_program=self.config.format_retry_program,
                config=StructuredMethodConfig.selected(
                    prompt_profile=self.config.prompt_profile
                ),
            )
            result = structured_one_call.run_llm_only_letter(letter, producer)
        else:
            raise ValueError("ExECT llm_with_rules remains a separate migration phase")
        return Exectv2RunResult(method=method, result=result)


__all__ = [
    "Exectv2PipelineConfiguration",
    "Exectv2PipelineRunner",
    "Exectv2RunResult",
]
