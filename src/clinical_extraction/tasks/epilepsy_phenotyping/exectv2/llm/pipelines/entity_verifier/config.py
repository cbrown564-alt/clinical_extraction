"""Verifier pipeline configuration."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter


@dataclass(frozen=True)
class VerifierConfig:
    """Entity-specific verifier pipeline wiring."""

    entity_name: str
    prompt_version: str
    pipeline_family: str
    component_owner: str
    dspy_signature: type[dspy.Signature]
    draft_field_name: str
    report_title: str
    draft_mentions_label: str
    clinical_recovery_section_title: str
    clinical_recovery_key: str
    task_text: str
    output_schema: Mapping[str, Any]
    clinical_rules: Callable[[], list[str]]
    worked_examples: Callable[[], list[dict[str, Any]]]
    summarize_rows: Callable[[Sequence[dict[str, Any]]], dict[str, Any]]
    include_source_near_in_report: bool = True
    draft_entity_names: tuple[str, ...] | None = None
    include_entity_in_draft: bool = False

    def build_prompt_input(
        self,
        letter: ExectLetter,
        draft_mentions: Sequence[Mapping[str, Any]],
        timeline_context: str | None = None,
    ) -> str:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.prompt import (
            build_prompt_input,
        )

        return build_prompt_input(letter, draft_mentions, self, timeline_context=timeline_context)

    def draft_mentions_by_letter(
        self,
        rows: Sequence[Mapping[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
            draft_mentions_by_letter,
        )

        return draft_mentions_by_letter(rows, self)

    def read_draft_rows(self, path: Path | None) -> list[dict[str, Any]]:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
            read_draft_rows,
        )

        return read_draft_rows(path)

    def run_split(self, letters: Sequence[ExectLetter], **kwargs: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
            run_split,
        )

        return run_split(letters, config=self, **kwargs)

    def write_report(
        self,
        rows: Sequence[dict[str, Any]],
        metadata: Mapping[str, Any],
        path: Path,
        *,
        jsonl_path: Path,
    ) -> None:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
            write_report,
        )

        write_report(rows, metadata, path, config=self, jsonl_path=jsonl_path)
