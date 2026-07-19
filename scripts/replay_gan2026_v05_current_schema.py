"""Replay complete Gan v0.5 raw outputs through today's shared schema repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_structured_events_report,
)

PROMPT_VERSION = hybrid_structured_events.PROMPT_VERSION_V0_5


@dataclass(frozen=True)
class Condition:
    source: Path
    model: str
    temperature: float
    max_tokens: int


CONDITIONS = {
    "gpt41mini": Condition(
        Path("scratch/holdout/gan2026_matched_v05/gpt41mini/rows.jsonl"),
        "openai/gpt-4.1-mini",
        0.0,
        10_000,
    ),
    "gpt56luna": Condition(
        Path("scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl"),
        "openai/gpt-5.6-luna",
        1.0,
        10_000,
    ),
    "gpt56sol": Condition(
        Path("scratch/holdout/gan2026_matched_v05/gpt56sol/rows.jsonl"),
        "openai/gpt-5.6-sol",
        0.0,
        10_000,
    ),
    "deepseek_v4_flash": Condition(
        Path("scratch/holdout/gan2026_matched_v05/deepseek_v4_flash/rows.jsonl"),
        "deepseek/deepseek-v4-flash",
        0.0,
        32_000,
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _selection_label(row: dict[str, Any]) -> str | None:
    structured = row.get("structured_record") or {}
    selection = structured.get("selection") or {}
    value = selection.get("final_label")
    return str(value) if value is not None else None


def _correct(row: dict[str, Any], key: str) -> bool:
    return bool((row.get("comparison") or {}).get(key))


def build_delta_summary(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> dict[str, int]:
    before_by_id = {int(row["source_row_index"]): row for row in before}
    after_by_id = {int(row["source_row_index"]): row for row in after}
    if before_by_id.keys() != after_by_id.keys():
        raise ValueError("replay source IDs differ from the original artifact")
    changed_labels = 0
    purist_wrong_to_correct = 0
    purist_correct_to_wrong = 0
    pragmatic_wrong_to_correct = 0
    pragmatic_correct_to_wrong = 0
    for source_id, old in before_by_id.items():
        new = after_by_id[source_id]
        changed_labels += _selection_label(old) != _selection_label(new)
        old_purist = _correct(old, "purist_correct")
        new_purist = _correct(new, "purist_correct")
        purist_wrong_to_correct += not old_purist and new_purist
        purist_correct_to_wrong += old_purist and not new_purist
        old_pragmatic = _correct(old, "pragmatic_correct")
        new_pragmatic = _correct(new, "pragmatic_correct")
        pragmatic_wrong_to_correct += not old_pragmatic and new_pragmatic
        pragmatic_correct_to_wrong += old_pragmatic and not new_pragmatic
    return {
        "changed_final_labels": changed_labels,
        "purist_wrong_to_correct": purist_wrong_to_correct,
        "purist_correct_to_wrong": purist_correct_to_wrong,
        "pragmatic_wrong_to_correct": pragmatic_wrong_to_correct,
        "pragmatic_correct_to_wrong": pragmatic_correct_to_wrong,
    }


def replay(condition_name: str, *, overwrite: bool = False) -> dict[str, Any]:
    condition = CONDITIONS[condition_name]
    source_rows = load_jsonl_rows(condition.source)
    test_records = load_records_for_split("test")
    test_ids = {record.source_row_index for record in test_records}
    source_ids = [int(row["source_row_index"]) for row in source_rows]
    if len(source_rows) != 450 or len(set(source_ids)) != 450 or set(source_ids) != test_ids:
        raise ValueError(f"{condition_name} is not a complete unique test450 artifact")
    if {row.get("prompt_version") for row in source_rows} != {PROMPT_VERSION}:
        raise ValueError(f"{condition_name} does not contain only v0.5 prompt rows")
    raw_outputs = {
        int(row["source_row_index"]): str(row.get("raw_output") or "") for row in source_rows
    }
    if len(raw_outputs) != 450 or any(not value for value in raw_outputs.values()):
        raise ValueError(f"{condition_name} has missing raw outputs")

    output_dir = (
        Path("scratch/holdout/gan2026_matched_v05_current_schema_replay") / condition_name
    )
    rows_path = output_dir / "rows.jsonl"
    report_path = output_dir / "report.md"
    aggregate_path = output_dir / "aggregate.json"
    if not overwrite and any(path.exists() for path in (rows_path, report_path, aggregate_path)):
        raise FileExistsError(f"replay output already exists for {condition_name}")

    hybrid_structured_events.set_active_prompt_version(PROMPT_VERSION)
    manifest = load_split_manifest()
    replay_rows, metadata = hybrid_structured_events.run_split(
        test_records,
        split="test",
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        model=condition.model,
        temperature=condition.temperature,
        max_tokens=condition.max_tokens,
        mode="prompt-only",
        dspy_cache=False,
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(condition.source),
        repair_config=hybrid_structured_events.StructuredRepairConfig(),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    hybrid_structured_events.write_jsonl(replay_rows, rows_path)
    llm_structured_events_report.write_report(
        replay_rows, metadata, report_path, jsonl_path=rows_path
    )
    summary = dict(metadata["summary"])
    aggregate = {
        "condition": condition_name,
        "model": condition.model,
        "dataset": "Gan 2026",
        "split": "test450",
        "row_policy": "aggregate_only",
        "prompt_version": PROMPT_VERSION,
        "call_mode": "no_call_saved_raw_output_replay",
        "schema_repair": "current_shared_schema_repair",
        "repair_mode": metadata["repair_mode"],
        "source_artifact": str(condition.source),
        "source_sha256": _sha256(condition.source),
        "rows": summary["examples"],
        "structured_records": summary["structured_records"],
        "reused_raw_outputs": summary["reused_raw_outputs"],
        "call_failures": summary["call_failures"],
        "parse_or_validation_failures": summary["parse_or_validation_failures"],
        "evidence_valid": summary["evidence_valid"],
        "purist_correct": summary["purist_correct"],
        "purist_accuracy": summary["purist_accuracy"],
        "pragmatic_correct": summary["pragmatic_correct"],
        "pragmatic_accuracy": summary["pragmatic_accuracy"],
        "delta": build_delta_summary(source_rows, replay_rows),
        "rows_artifact": str(rows_path),
        "rows_sha256": _sha256(rows_path),
    }
    aggregate_path.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(replay(args.condition, overwrite=args.overwrite), sort_keys=True))


if __name__ == "__main__":
    main()
