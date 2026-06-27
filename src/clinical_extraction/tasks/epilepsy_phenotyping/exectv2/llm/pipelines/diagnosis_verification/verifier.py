"""Diagnosis entity verifier pipeline config and runtime facade."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.diagnosis_verification.verifier_content import (
    COMPONENT_OWNER,
    OUTPUT_SCHEMA,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    TASK_TEXT,
    ExECTv2DiagnosisVerifierSignature,
    _attribute_vocabulary,
    _clinical_rules,
    _worked_examples,
    summarize_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
    read_draft_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    make_dspy_module,
    mention_to_row,
    to_predicted_letter as _runner_to_predicted_letter,
)

CONFIG = VerifierConfig(
    entity_name=DIAGNOSIS.name,
    prompt_version=PROMPT_VERSION,
    pipeline_family=PIPELINE_FAMILY,
    component_owner=COMPONENT_OWNER,
    dspy_signature=ExECTv2DiagnosisVerifierSignature,
    draft_field_name="draft_diagnosis_mentions",
    report_title="ExECTv2 Diagnosis Verifier",
    draft_mentions_label="Draft Diagnosis mentions",
    clinical_recovery_section_title="Diagnosis Clinical-Recovery Headline",
    clinical_recovery_key="diagnosis",
    task_text=TASK_TEXT,
    output_schema=OUTPUT_SCHEMA,
    clinical_rules=_clinical_rules,
    worked_examples=_worked_examples,
    summarize_rows=summarize_rows,
    include_source_near_in_report=True,
)

DspyDiagnosisVerifier = make_dspy_module(CONFIG)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return CONFIG.draft_mentions_by_letter(rows)


def build_prompt_input(letter: ExectLetter, draft_mentions: Sequence[Mapping[str, Any]]) -> str:
    return CONFIG.build_prompt_input(letter, draft_mentions)


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
    )


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
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    return _runner_to_predicted_letter(CONFIG, letter_id, mentions, note_text=note_text)


_mention_to_row = mention_to_row

__all__ = [
    "COMPONENT_OWNER",
    "CONFIG",
    "DspyDiagnosisVerifier",
    "ExECTv2DiagnosisVerifierSignature",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "_attribute_vocabulary",
    "_clinical_rules",
    "_mention_to_row",
    "_worked_examples",
    "build_prompt_input",
    "draft_mentions_by_letter",
    "read_draft_rows",
    "run_split",
    "summarize_rows",
    "to_predicted_letter",
    "write_report",
]