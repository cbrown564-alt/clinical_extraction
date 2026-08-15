#!/usr/bin/env python3
"""Aggregate-only test450 confirmation of the inexact-span family-rewrite block.

See docs/research/gan2026/inexact_span_family_rewrite_protocol_2026-08-15.md.
Zero model calls. Public output is counts only.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
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

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = REPO_ROOT / "docs/research/gan2026/inexact_span_family_rewrite_protocol_2026-08-15.md"
FILLS = REPO_ROOT / "experiments/current_stack/latest/fills.json"
OUTPUT = REPO_ROOT / "experiments/gan2026_inexact_span_family_rewrite_test450_20260815.json"
SCRATCH = REPO_ROOT / "scratch/validation/inexact_span_family_rewrite_test450"
SIDECAR_DIR = REPO_ROOT / "experiments/current_stack/sidecars/gan_test450"

MODELS = (
    ("gemini37flash", "gemini/gemini-3.7-flash", "Gemini 3.7 Flash", 0.0, 16_000, "gemini37flash"),
    ("gpt56luna", "openai/gpt-5.6-luna", "GPT-5.6 Luna", 1.0, 10_000, "gpt56luna"),
    ("gpt56sol", "openai/gpt-5.6-sol", "GPT-5.6 Sol", 0.0, 10_000, "gpt56sol"),
    (
        "deepseek_v4_flash",
        "deepseek/deepseek-v4-flash",
        "DeepSeek V4 Flash 0731",
        0.0,
        32_000,
        "deepseek_v4_flash_0731",
    ),
    ("qwen36_35b", "ollama_chat/qwen3.6:35b", "Qwen 3.6:35B", 0.0, 16_000, "qwen36_35b"),
    ("gemma4_26b", "ollama_chat/gemma4:26b", "Gemma 4 26B", 0.0, 16_000, "gemma4_26b"),
)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _score(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "n": len(rows),
        "purist": sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows),
        "pragmatic": sum(
            bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
        ),
        "parse_missing": sum(row.get("comparison") is None for row in rows),
    }


def main() -> None:
    if not PROTOCOL.exists():
        raise SystemExit(f"predeclared protocol missing: {PROTOCOL}")
    fills = json.loads(FILLS.read_text(encoding="utf-8"))
    published = (fills.get("hybrid") or {}).get("gan_test450") or {}
    records = load_records_for_split("test")
    expected = {int(record.source_row_index) for record in records}
    if len(expected) != 450:
        raise ValueError(f"test split has {len(expected)} rows, expected 450")
    manifest = load_split_manifest()
    cells: dict[str, Any] = {}
    for slug, model, display, temperature, max_tokens, sidecar_name in MODELS:
        source = SIDECAR_DIR / f"{sidecar_name}.jsonl"
        if not source.is_file():
            raise FileNotFoundError(source)
        source_rows = load_jsonl_rows(source)
        versions = {row.get("prompt_version") for row in source_rows}
        if versions != {hybrid_structured_events.PROMPT_VERSION_V0_5}:
            raise ValueError(f"{slug} prompt {versions} != v0.5")
        source_ids = {int(row["source_row_index"]) for row in source_rows}
        if source_ids != expected:
            raise ValueError(f"{slug} is not a complete unique test450 sidecar")
        raw_outputs = {
            int(row["source_row_index"]): str(row.get("raw_output") or "")
            for row in source_rows
        }
        if any(not value.strip() for value in raw_outputs.values()):
            raise ValueError(f"{slug} has empty raw outputs")
        hybrid_structured_events.set_active_prompt_version(
            hybrid_structured_events.PROMPT_VERSION_V0_5
        )
        replay_rows, _metadata = hybrid_structured_events.run_split(
            records,
            split="test",
            split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode="prompt-only",
            dspy_cache=False,
            reuse_raw_outputs=raw_outputs,
            reuse_source=str(source.relative_to(REPO_ROOT).as_posix()),
            repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
                "hybrid_full_stack"
            ),
            progress_every=150,
        )
        scratch = SCRATCH / slug
        scratch.mkdir(parents=True, exist_ok=True)
        (scratch / "test450.rows.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in replay_rows),
            encoding="utf-8",
        )
        after = _score(replay_rows)
        before_pub = published.get(slug) or {}
        before_purist = int(before_pub.get("purist") or 0)
        cells[slug] = {
            "label": display,
            "sidecar": source.relative_to(REPO_ROOT).as_posix(),
            "prompt_identity": hybrid_structured_events.PROMPT_VERSION_V0_5,
            "published_purist": before_purist,
            "published_pragmatic": int(before_pub.get("pragmatic") or 0),
            "after": after,
            "purist_delta": after["purist"] - before_purist,
        }
        print(
            json.dumps(
                {
                    "slug": slug,
                    "published_purist": before_purist,
                    "after_purist": after["purist"],
                    "delta": after["purist"] - before_purist,
                },
                sort_keys=True,
            ),
            flush=True,
        )

    payload = {
        "schema_version": "gan2026.inexact_span_family_rewrite_test450.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL.relative_to(REPO_ROOT).as_posix(),
        "git": _git_note(),
        "split": "test450",
        "row_policy": "aggregate_only",
        "prompt_identity": hybrid_structured_events.PROMPT_VERSION_V0_5,
        "call_mode": "saved_raw_output_no_call",
        "models": cells,
        "pooled_purist_delta": sum(cell["purist_delta"] for cell in cells.values()),
        "claim_boundary": (
            "Aggregate-only no-call replay of matched v0.5 test450 sidecars. "
            "No row identifiers in this file."
        ),
    }
    forbidden = {"letter_id", "source_row_index", "note_text", "raw_output", "rows"}
    dumped = json.dumps(payload)
    if any(key in dumped for key in ('"source_row_index"', '"note_text"', '"letter_id"')):
        raise SystemExit("refusing to write row-level holdout content")
    del forbidden
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "output": OUTPUT.as_posix()}, sort_keys=True))


if __name__ == "__main__":
    main()
