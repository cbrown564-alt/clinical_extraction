"""Reparse saved local-model outputs without making model calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.local_structured_output import assess_structured_output
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as exect_structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

_BLOCKING_PREFIXES = (
    "invalid_json:",
    "schema_validation_error:",
    "unscorable_final_label:",
    "not_run",
)


def _is_blocking(errors: list[object] | tuple[object, ...] | None) -> bool:
    return any(str(error).startswith(_BLOCKING_PREFIXES) for error in errors or [])


def reparse_exect(path: Path) -> dict[str, Any]:
    rows = load_jsonl_rows(path)
    for row in rows:
        old_errors = list(row.get("parse_errors") or [])
        if not _is_blocking(old_errors):
            continue
        raw_output = str(row.get("raw_output") or "")
        record, parse_errors = (
            exect_structured.parse_structured_events_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        if _is_blocking(old_errors) and not _is_blocking(parse_errors):
            parse_errors = [*parse_errors, "no_call_schema_reparse_applied"]
        prompt = json.loads(str(row.get("prompt_input_json") or "{}"))
        note_text = str(prompt.get("letter_text") or "")
        mentions = exect_structured.flatten_events(record) if record else []
        predicted, gate_warnings = exect_structured.to_predicted_letter(
            str(row["letter_id"]),
            mentions,
            note_text=note_text,
            prompt_version=str(row.get("prompt_version") or ""),
        )
        assessment = assess_structured_output(
            raw_output, parse_errors, call_error=row.get("call_error")
        )
        row.update(
            {
                "parse_errors": parse_errors,
                "structured_output_failure_codes": list(assessment.failure_codes),
                "gate_warnings": gate_warnings,
                "n_events_raw": len(record.clinical_events) if record else 0,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted.mentions),
                "structured_events": [
                    event.model_dump() for event in (record.clinical_events if record else [])
                ],
                "predicted_mentions": [
                    {
                        "entity": mention.entity,
                        "text": mention.text,
                        "attributes": dict(mention.attributes),
                        "evidence": mention.evidence,
                        "confidence": mention.confidence,
                        "rationale": mention.rationale,
                    }
                    for mention in predicted.mentions
                ],
            }
        )
    summary = exect_structured.summarize_rows(rows)
    write_jsonl_rows(rows, path)
    first = rows[0] if rows else {}
    exect_structured.write_report(
        rows,
        {
            "prompt_version": first.get("prompt_version"),
            "prompt_profile": first.get("prompt_profile"),
            "pipeline_family": first.get("pipeline_family"),
            "split": first.get("split"),
            "model": first.get("model"),
            "mode": "diagnostic no-call reparse",
            "n_letters": len(rows),
            "summary": summary,
        },
        path.with_suffix(".md"),
        jsonl_path=path,
    )
    return summary


def reparse_gan(path: Path) -> dict[str, Any]:
    old_rows = load_jsonl_rows(path)
    old_by_index = {int(row["source_row_index"]): row for row in old_rows}
    failed_indices = {
        index for index, row in old_by_index.items() if _is_blocking(row.get("parse_errors"))
    }
    raw_outputs = {
        index: str(row.get("raw_output") or "")
        for index, row in old_by_index.items()
        if index in failed_indices
    }
    prompt_version = str(old_rows[0].get("prompt_version"))
    hybrid_structured_events.set_active_prompt_version(prompt_version)
    records = [
        record
        for record in load_records_for_split("test")
        if record.source_row_index in failed_indices
    ]
    repaired_rows, metadata = hybrid_structured_events.run_split(
        records,
        split="test",
        split_manifest=str(old_rows[0].get("split_manifest") or "gan2026_split_v1"),
        model=_model_for_path(path),
        temperature=0.0,
        max_tokens=0,
        mode="prompt-only",
        dspy_cache=False,
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(path),
    )
    repaired_by_index = {
        int(row["source_row_index"]): row for row in repaired_rows
    }
    for row in repaired_rows:
        old = old_by_index[int(row["source_row_index"])]
        if _is_blocking(old.get("parse_errors")) and not _is_blocking(row.get("parse_errors")):
            row["parse_errors"] = [*row["parse_errors"], "no_call_schema_reparse_applied"]
        row["initial_parse_errors"] = old.get("initial_parse_errors", [])
        row["format_retry_output"] = old.get("format_retry_output", "")
        row["format_retry_notes"] = old.get("format_retry_notes", [])
    rows = [
        repaired_by_index.get(int(old["source_row_index"]), old) for old in old_rows
    ]
    metadata["mode"] = "diagnostic no-call reparse"
    metadata["summary"] = hybrid_structured_events.summarize_records(rows)
    hybrid_structured_events.write_jsonl(rows, path)
    hybrid_structured_events.write_report(
        rows, metadata, path.with_name("test450_aggregate.md"), jsonl_path=path
    )
    return metadata["summary"]


def _model_for_path(path: Path) -> str:
    normalized = path.as_posix().lower()
    if "qwen36_35b" in normalized:
        return "ollama_chat/qwen3.6:35b"
    if "gemma4_26b" in normalized:
        return "ollama_chat/gemma4:26b"
    return "saved-local-model"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exect", type=Path, action="append", default=[])
    parser.add_argument("--gan", type=Path, action="append", default=[])
    args = parser.parse_args()
    for path in args.exect:
        print(json.dumps({"path": str(path), "summary": reparse_exect(path)}, sort_keys=True))
    for path in args.gan:
        print(json.dumps({"path": str(path), "summary": reparse_gan(path)}, sort_keys=True))


if __name__ == "__main__":
    main()
