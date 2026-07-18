"""Reconcile the retained GPT-4.1-mini Gan v0.5 artifact without row readout.

The retained test artifact is recovered from Git history in memory. This script
replays only its saved raw model outputs through the current parser, repair
stack, normalization, and scorer. It emits aggregate compatibility counts and
fingerprints; it never prints a test-row identifier, note, prediction, or
failure example.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    PROMPT_VERSION_V0_5,
    StructuredRepairConfig,
    build_prompt_input,
    parse_structured_json,
)

ARTIFACT_COMMIT = "facfd07d9789b633e6a583f1ca1a6bd7b8f09558"
ARTIFACT_PATH = (
    "experiments/gan2026_test450_phase4_frozen_audit_"
    "hybrid_structured_events_gpt41mini_2026-06-09.jsonl"
)
PROMPT_SNAPSHOT_PATH = Path(
    "tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.5.txt"
)
CODE_PATHS = (
    Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py"),
    Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py"),
    Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py"),
    Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py"),
    Path("src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py"),
)


def _git_blob() -> bytes:
    result = subprocess.run(
        ["git", "cat-file", "blob", f"{ARTIFACT_COMMIT}:{ARTIFACT_PATH}"],
        check=True,
        capture_output=True,
    )
    return result.stdout


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count_stored(rows: list[dict[str, Any]], field: str) -> int:
    return sum(bool(row.get(field)) for row in rows)


def main() -> None:
    blob = _git_blob()
    raw_rows = [json.loads(line) for line in blob.splitlines() if line.strip()]
    records = load_records_for_split("test")
    records_by_index = {record.source_row_index: record for record in records}

    old_purist = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in raw_rows)
    old_pragmatic = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in raw_rows
    )
    old_prompt_versions = sorted({str(row.get("prompt_version")) for row in raw_rows})
    old_splits = sorted({str(row.get("split")) for row in raw_rows})
    old_manifests = sorted({str(row.get("split_manifest")) for row in raw_rows})

    prompt_payload_matches = 0
    structured_record_matches = 0
    normalized_events_matches = 0
    parse_errors_matches = 0
    current_purist = 0
    current_pragmatic = 0
    current_parse_failures = 0
    current_evidence_valid = 0
    current_json_dialect_repairs = 0
    current_label_repairs = 0
    current_final_label_changes = 0

    repair_config = StructuredRepairConfig.for_mode("hybrid_full_stack")
    for old_row in raw_rows:
        source_row_index = int(old_row["source_row_index"])
        record = records_by_index[source_row_index]
        old_prompt = json.loads(str(old_row["prompt_input_json"]))
        current_prompt = json.loads(
            build_prompt_input(record, prompt_version=PROMPT_VERSION_V0_5)
        )
        if old_prompt == current_prompt:
            prompt_payload_matches += 1

        extraction, normalized_events, parse_errors = parse_structured_json(
            str(old_row.get("raw_output") or ""),
            note_text=record.note_text,
            repair_config=repair_config,
        )
        current_structured = extraction.model_dump() if extraction else None
        current_normalized = [event.model_dump() for event in normalized_events]
        if current_structured == old_row.get("structured_record"):
            structured_record_matches += 1
        if current_normalized == old_row.get("normalized_events"):
            normalized_events_matches += 1
        if parse_errors == old_row.get("parse_errors"):
            parse_errors_matches += 1

        if extraction is None or not extraction.selection.final_label:
            current_parse_failures += 1
            continue
        try:
            predicted = label_to_frequency_record(extraction.selection.final_label)
        except ValueError:
            current_parse_failures += 1
            continue
        predicted_purist = str(map_purist(predicted.monthly_frequency))
        predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
        current_purist += predicted_purist == str(map_purist(record.gold_monthly_frequency))
        current_pragmatic += predicted_pragmatic == str(
            map_pragmatic(record.gold_monthly_frequency)
        )
        current_evidence_valid += bool(
            extraction.selection.evidence and extraction.selection.evidence in record.note_text
        )
        current_json_dialect_repairs += any(
            str(error).startswith("json_dialect_repaired:") for error in parse_errors
        )
        current_label_repairs += any(
            str(error).startswith("final_label_repaired:") for error in parse_errors
        )
        current_final_label_changes += (
            extraction.selection.final_label
            != (old_row.get("structured_record") or {}).get("selection", {}).get("final_label")
        )

    counts = {
        "rows": len(raw_rows),
        "prompt_payload_matches": prompt_payload_matches,
        "structured_record_matches": structured_record_matches,
        "normalized_events_matches": normalized_events_matches,
        "parse_errors_matches": parse_errors_matches,
        "current_final_label_changes": current_final_label_changes,
    }
    current = {
        "purist_correct": current_purist,
        "pragmatic_correct": current_pragmatic,
        "parse_or_validation_failures": current_parse_failures,
        "evidence_valid": current_evidence_valid,
        "json_dialect_repairs": current_json_dialect_repairs,
        "label_repairs": current_label_repairs,
    }
    exact_non_prompt_replay = (
        current_purist == old_purist
        and current_pragmatic == old_pragmatic
        and structured_record_matches == len(raw_rows)
        and normalized_events_matches == len(raw_rows)
        and parse_errors_matches == len(raw_rows)
    )
    result = {
        "artifact": {
            "git_commit": ARTIFACT_COMMIT,
            "path": ARTIFACT_PATH,
            "blob_sha256": hashlib.sha256(blob).hexdigest(),
            "bytes": len(blob),
            "rows": len(raw_rows),
            "stored_purist_correct": old_purist,
            "stored_pragmatic_correct": old_pragmatic,
            "prompt_versions": old_prompt_versions,
            "splits": old_splits,
            "split_manifests": old_manifests,
            "call_failures": _count_stored(raw_rows, "call_error"),
        },
        "current_non_prompt_replay": current,
        "compatibility_counts": counts,
        "fingerprints": {
            "v05_rendered_snapshot_sha256": _sha256(PROMPT_SNAPSHOT_PATH),
            "v05_rendered_snapshot_bytes": PROMPT_SNAPSHOT_PATH.stat().st_size,
            "current_code_sha256": {str(path): _sha256(path) for path in CODE_PATHS},
        },
        "decision": {
            "prompt_payloads_match": prompt_payload_matches == len(raw_rows),
            "exact_non_prompt_replay": exact_non_prompt_replay,
            "reuse_gpt41mini": exact_non_prompt_replay,
            "rerun_gpt41mini_required": not exact_non_prompt_replay,
        },
        "claim_boundary": (
            "Aggregate-only no-call reconciliation; no held-out row identifiers, notes, "
            "predictions, or failures are emitted."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
