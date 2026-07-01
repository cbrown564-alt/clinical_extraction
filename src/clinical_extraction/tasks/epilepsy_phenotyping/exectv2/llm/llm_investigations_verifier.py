"""Investigations-focused verifier over the v0.5 structured key-entity draft."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
    read_draft_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.investigations import (
    CONFIG,
    DspyInvestigationsVerifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.investigations_content import (
    _attribute_vocabulary,
    _clinical_rules,
    _worked_examples,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    mention_to_row,
    to_predicted_letter as _runner_to_predicted_letter,
)

PROMPT_VERSION = CONFIG.prompt_version
PIPELINE_FAMILY = CONFIG.pipeline_family
COMPONENT_OWNER = CONFIG.component_owner
ExECTv2InvestigationsVerifierSignature = CONFIG.dspy_signature


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return CONFIG.draft_mentions_by_letter(rows)


def build_prompt_input(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]],
    timeline_context: str | None = None,
) -> str:
    return CONFIG.build_prompt_input(letter, draft_mentions, timeline_context=timeline_context)


def run_split(
    letters: Sequence[ExectLetter],
    *,
    draft_rows: Sequence[Mapping[str, Any]] = (),
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    timeline_context_by_letter: Mapping[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    return CONFIG.run_split(
        letters,
        draft_rows=draft_rows,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
        resume=resume,
        timeline_context_by_letter=timeline_context_by_letter,
    )


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return CONFIG.summarize_rows(rows)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    CONFIG.write_report(rows, metadata, path, jsonl_path=jsonl_path)


def to_predicted_letter(
    letter_id: str,
    mentions: Sequence[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    return _runner_to_predicted_letter(CONFIG, letter_id, mentions, note_text=note_text)


_mention_to_row = mention_to_row

__all__ = [
    "COMPONENT_OWNER",
    "DspyInvestigationsVerifier",
    "ExECTv2InvestigationsVerifierSignature",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "build_prompt_input",
    "draft_mentions_by_letter",
    "read_draft_rows",
    "run_split",
    "summarize_rows",
    "to_predicted_letter",
    "write_report",
    "_attribute_vocabulary",
    "_clinical_rules",
    "_mention_to_row",
    "_worked_examples",
]
