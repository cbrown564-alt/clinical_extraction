"""Unified parameterized runner framework for Gan 2026 pipelines.

Thin facade over the ``runners/`` package. Every public symbol is re-exported
so existing importers keep working.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    GanRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
    deterministic_canonical,
    hybrid_structured_events,
    llm_only_canonical,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.cli_specs import (
    get_cli_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    ARCHITECTURE_FAMILY,
    PipelineArchitecture,
    PipelineConfiguration,
    PipelineOutputArtifact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
    write_deterministic_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

__all__ = [
    "ARCHITECTURE_FAMILY",
    "Gan2026PipelineRunner",
    "PipelineArchitecture",
    "PipelineConfiguration",
    "PipelineOutputArtifact",
    "get_cli_specs",
    "run_split",
    "write_deterministic_report",
]

_ITEM_RUNNERS = {
    "deterministic_canonical_pipeline": deterministic_canonical.run_item,
    "hybrid_structured_events": hybrid_structured_events.run_item,
    "llm_only_canonical_pipeline": llm_only_canonical.run_item,
}


class Gan2026PipelineRunner:
    """Unified runner capable of executing all Gan 2026 pipeline configurations."""

    def __init__(self, config: PipelineConfiguration) -> None:
        self.config = config

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        """Run a single record through the unified schema flow based on architecture."""
        if self.config.architecture == "deterministic_canonical_pipeline":
            return deterministic_canonical.run_item(item, self.config)

        if not isinstance(item, GanFrequencyRecord):
            raise TypeError(
                f"{self.config.architecture} requires a GanFrequencyRecord with "
                "normalized gold frequency fields"
            )
        if self.config.architecture == "hybrid_structured_events":
            return hybrid_structured_events.run_item(item, self.config)
        if self.config.architecture == "llm_only_canonical_pipeline":
            return llm_only_canonical.run_item(item, self.config)
        raise ValueError(
            f"Unsupported architecture for single-item run: {self.config.architecture}"
        )

    def run_split(
        self,
        records: Sequence,
        *,
        split: str,
        split_manifest: str,
        mode: Literal["live", "prompt-only"],
        escalation_reason: str | None = None,
        progress_every: int | None = None,
        checkpoint_jsonl_path: Path | None = None,
        checkpoint_report_path: Path | None = None,
        candidate_set_jsonl_path: Path | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return run_split(
            records,
            architecture=self.config.architecture,
            split=split,
            split_manifest=split_manifest,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            mode=mode,
            dspy_cache=self.config.dspy_cache,
            api_base=None,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
            candidate_set_jsonl_path=candidate_set_jsonl_path,
        )
