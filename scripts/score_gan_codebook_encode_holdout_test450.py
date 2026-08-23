#!/usr/bin/env python3
"""Aggregate-only test450 replay of frozen codebook encode. No row dumps."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.gan_later_stage import extract_rows_path
from clinical_extraction.paper.gan_cell_replay import score_label
from clinical_extraction.paper.methods import gan_machine_split, gan_row_count
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)

ROOT = discover_repo_root(start=Path(__file__))
SPLIT = "test450"
SLUG = "gemini37flash"
N = gan_row_count(SPLIT)
ARMS = (
    "raw_model",
    "llm_encode",
    "llm_encode_codebook",
    "llm_select_after_codebook",
    "llm_select",
    "llm_select_only",
)
LOCKED_CELL3 = {
    "raw_model": 354,
    "llm_encode": 346,
    "llm_select": 362,
    "llm_select_only": 368,
}
LOCKED_GRID = {
    "rules": {"extract": 329, "encode": 329, "select": 329},
    "rules_then_llm": {"extract": 371, "encode": 361, "select": 368},
    "llm": {"extract": 354, "encode": 354, "select": 357},
}
OUT_DIR = ROOT / "experiments/gan_codebook_encode_holdout_20260822"
PROTOCOL = (
    "docs/research/gan2026/gan_codebook_encode_holdout_protocol_2026-08-22.md"
)


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "not-installed"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _score_arm(
    raw_output: str,
    record: GanFrequencyRecord,
    mode: str,
) -> dict[str, bool]:
    extraction, _, _, _ = parse_structured_json_with_trace(
        raw_output,
        note_text=record.note_text,
        repair_config=StructuredRepairConfig.for_mode(mode),
    )
    label = None if extraction is None else extraction.selection.final_label
    scored = score_label(record, label)
    return {
        "purist_correct": bool(scored["purist_correct"]),
        "pragmatic_correct": bool(scored["pragmatic_correct"]),
        "scorable": bool(scored["scorable"]),
    }


def _empty_counts() -> dict[str, int]:
    return {"purist_correct": 0, "pragmatic_correct": 0, "scorable": 0}


def main() -> None:
    extract_path = extract_rows_path(SPLIT, SLUG)
    records = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(SPLIT))
    }
    raw_by_index: dict[int, str] = {}
    with extract_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            raw_by_index[int(row["source_row_index"])] = str(row["raw_output"])
    if len(raw_by_index) != N or len(records) != N:
        raise RuntimeError(
            f"expected {N} extract rows and gold records, "
            f"found {len(raw_by_index)} / {len(records)}"
        )

    totals = {arm: _empty_counts() for arm in ARMS}
    for source_row_index, record in records.items():
        raw_output = raw_by_index[source_row_index]
        for arm in ARMS:
            scored = _score_arm(raw_output, record, arm)
            for key, value in scored.items():
                totals[arm][key] += int(value)

    arms: dict[str, Any] = {}
    for arm, counts in totals.items():
        payload = {
            "repair_mode": arm,
            "n": N,
            "purist_correct": counts["purist_correct"],
            "purist_accuracy": counts["purist_correct"] / N,
            "pragmatic_correct": counts["pragmatic_correct"],
            "pragmatic_accuracy": counts["pragmatic_correct"] / N,
            "scorable": counts["scorable"],
        }
        locked = LOCKED_CELL3.get(arm)
        if locked is not None:
            payload["matches_locked_cell"] = counts["purist_correct"] == locked
        arms[arm] = payload

    if not all(arms[arm]["matches_locked_cell"] for arm in LOCKED_CELL3):
        raise RuntimeError("replay did not reproduce a locked cell-3/4 stop")

    candidate_encode = arms["llm_encode_codebook"]["purist_correct"]
    candidate_select = arms["llm_select_after_codebook"]["purist_correct"]
    five_cell = {
        "1_rules": LOCKED_GRID["rules"],
        "2_rules_then_llm": {
            "extract_source": "gan_llm_pre_post_label_forms",
            **LOCKED_GRID["rules_then_llm"],
        },
        "3_llm_then_rules": {
            "extract_source": "gan_llm_extract_label_forms",
            "encode_repair_mode": "llm_encode_codebook",
            "select_repair_mode": "llm_select_after_codebook",
            "extract": arms["raw_model"]["purist_correct"],
            "encode": candidate_encode,
            "select": candidate_select,
            "historical_encode": arms["llm_encode"]["purist_correct"],
            "historical_select": arms["llm_select"]["purist_correct"],
        },
        "4_llm_encode_rules_select": {
            "extract_source": "gan_llm_extract_label_forms",
            "repair_mode": "llm_select_only",
            "extract": arms["raw_model"]["purist_correct"],
            "encode": arms["raw_model"]["purist_correct"],
            "select": arms["llm_select_only"]["purist_correct"],
        },
        "5_llm": {
            "extract_source": "gan_llm_extract_label_forms",
            **LOCKED_GRID["llm"],
        },
    }
    summary = {
        "schema_version": "gan2026.codebook_encode_holdout.test450.v1",
        "generated_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL,
        "dataset": "Gan 2026 synthetic",
        "split": SPLIT,
        "split_machine": gan_machine_split(SPLIT),
        "split_manifest": "gan2026_split_v1",
        "n": N,
        "row_policy": "aggregate_only",
        "inspection": "Do not inspect holdout rows. Do not dump failure ids.",
        "model": "gemini/gemini-3.7-flash",
        "prompt_version": "gan_llm_extract_label_forms",
        "call_mode": "saved_output_deterministic_replay",
        "model_calls": 0,
        "scorer": "Gan Purist category accuracy",
        "source_extract_path": extract_path.relative_to(ROOT).as_posix(),
        "source_extract_sha256": _file_sha256(extract_path),
        "git_head": _git_output("rev-parse", "HEAD"),
        "git_dirty": bool(_git_output("status", "--porcelain")),
        "package_versions": {
            "clinical-extraction": _package_version("clinical-extraction"),
        },
        "implementation_sha256": {
            "codebook_encode.py": _file_sha256(
                ROOT
                / "src/clinical_extraction/tasks/seizure_frequency/"
                "gan2026/selected_evidence/codebook_encode.py"
            )
        },
        "arms": arms,
        "five_cell_purist_counts": five_cell,
        "five_cell_purist_accuracy": {
            name: {
                stage: round(count / N, 4) if isinstance(count, int) else count
                for stage, count in cell.items()
                if stage in {"extract", "encode", "select"}
            }
            for name, cell in five_cell.items()
        },
        "claim_boundary": (
            "Frozen-candidate holdout aggregates. Not a paper column. "
            "Do not inspect holdout rows."
        ),
    }
    forbidden = ("source_row_index", "note_text", "gold_label", "final_label")
    encoded = json.dumps(summary)
    if any(key in encoded for key in forbidden):
        raise RuntimeError("holdout summary leaked a row-identifying field")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "summary.json"
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": out.relative_to(ROOT).as_posix(), "arms": arms}, indent=2))


if __name__ == "__main__":
    main()
