"""Run orchestration, summaries, and report/metadata for the target single call.

Pure relocation from ``llm_target_indicators_single_call``.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    _mention_to_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.constants import (  # noqa: E501
    COMPONENT_OWNER,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    Mode,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.parsing import (  # noqa: E501
    _parse_target_extraction_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.projection import (  # noqa: E501
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.prompt_builders import (  # noqa: E501
    build_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.signatures import (  # noqa: E501
    DspyTargetIndicatorsExtractor,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
    build_target_indicator_report,
    render_target_indicator_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

__all__ = ["run_split", "summarize_rows", "write_jsonl", "write_report"]


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Mode,
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyTargetIndicatorsExtractor()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    requested = set(order)
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            _parse_target_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": _count_evidence_invalid_warnings(gate_warnings),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in TARGET_INDICATORS
                ],
            }
        )
        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def _count_evidence_invalid_warnings(warnings: Sequence[str]) -> int:
    return sum("dropped_evidence_not_substring" in warning for warning in warnings)


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters, pred_letters = _letters_from_rows(rows)
    arch = architecture_report(
        name=PIPELINE_FAMILY,
        ownership="llm_first_with_deterministic_normalization_projection",
        gold_letters=gold_letters,
        pred_letters=pred_letters,
    )
    routed_like = {
        "pipeline_family": PIPELINE_FAMILY,
        "generated_on": "",
        "split": rows[0].get("split", ""),
        "stage": f"dev{len(rows)}",
        "row_count": len(rows),
        "candidates": [
            {
                "name": PIPELINE_FAMILY,
                "ownership": arch["ownership"],
                "routed_primary_recovery": {
                    "overall": arch["clinical_recovery"]["cui_projected_overall"],
                    "headline_scores": {
                        indicator: arch["clinical_recovery"]["cui_projected_headline_scores"][
                            indicator
                        ]
                        for indicator in TARGET_INDICATORS
                    },
                },
                "routed_primary_errors": {
                    "per_entity": arch["error_taxonomy"]["per_entity"],
                },
                "fidelity_companions": arch["clinical_recovery"].get("fidelity_companions", {}),
            }
        ],
    }
    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_mentions_raw": sum(int(r.get("n_mentions_raw", 0)) for r in rows),
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": sum(int(r.get("n_evidence_invalid", 0)) for r in rows),
        "target_report": build_target_indicator_report(routed_like),
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = dict(metadata.get("summary") or summarize_rows(rows))
    target_report = summary["target_report"]
    lines = [
        "# ExECTv2 Target Indicators Single-Call Run",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        "",
        render_target_indicator_markdown(target_report),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _letters_from_rows(
    rows: Sequence[dict[str, Any]],
) -> tuple[list[ExectLetter], list[PredictedLetter]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (  # noqa: PLC0415
        ExectAnnotation,
        load_letters_for_split,
    )

    split = str(rows[0].get("split", "dev")) if rows else "dev"
    note_by_id = {letter.letter_id: letter.note_text for letter in load_letters_for_split(split)}
    gold_letters = []
    pred_letters = []
    for row in rows:
        letter_id = str(row["letter_id"])
        gold_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text=note_by_id.get(letter_id, ""),
                annotations=tuple(
                    ExectAnnotation(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                        },
                    )
                    for m in row.get("gold_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
        pred_letters.append(
            PredictedLetter(
                letter_id=str(row["letter_id"]),
                mentions=tuple(
                    PredictedMention(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                        },
                        evidence=str(m.get("evidence", "")),
                        confidence=m.get("confidence"),
                        rationale=str(m.get("rationale", "")),
                        component_owner=COMPONENT_OWNER,
                    )
                    for m in row.get("predicted_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
    return gold_letters, pred_letters


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
            },
            report_path.with_name(f"{report_path.stem}_checkpoint{report_path.suffix}"),
            jsonl_path=jsonl_path,
        )
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": summary.get("call_failures", 0),
                "parse_failures": summary.get("parse_failures", 0),
                "n_mentions_scored": summary.get("n_mentions_scored", 0),
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )
