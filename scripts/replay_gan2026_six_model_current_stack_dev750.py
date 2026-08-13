#!/usr/bin/env python3
"""No-call replay of retained six-model Gan hybrid raw outputs through HEAD.

See docs/research/gan2026_six_model_current_stack_dev750_replay_protocol_2026-08-13.md.
Zero model calls. Development split only.
"""

from __future__ import annotations

import argparse
import hashlib
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
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "experiments/gan2026_six_model_current_stack_dev750_replay_20260813"
SCRATCH_DIR = REPO_ROOT / "scratch/validation/gan2026_six_model_current_stack_dev750_20260813"
PROTOCOL = (
    "docs/research/gan2026_six_model_current_stack_dev750_replay_protocol_2026-08-13.md"
)

MODELS = [
    ("gpt41mini", "openai/gpt-4.1-mini", 0.0, 10_000),
    ("gpt56luna", "openai/gpt-5.6-luna", 1.0, 10_000),
    ("gpt56sol", "openai/gpt-5.6-sol", 0.0, 10_000),
    ("deepseek_v4_flash", "deepseek/deepseek-v4-flash", 0.0, 32_000),
    ("qwen36_35b", "ollama_chat/qwen3.6:35b", 0.0, 16_000),
    ("gemma4_26b", "ollama_chat/gemma4:26b", 0.0, 16_000),
]

JULY18_ROOT = REPO_ROOT / "experiments/gan2026_six_model_validation_20260718"
JUNE07_MINI = REPO_ROOT / (
    "experiments/gan2026_three_way_comparison_validation750_"
    "hybrid_structured_events_gpt41mini_2026-06-07.jsonl"
)

JULY27_V05_PANEL = {
    "gpt41mini": {"purist": 668, "pragmatic": 686},
    "gpt56luna": {"purist": 646, "pragmatic": 671},
    "gpt56sol": {"purist": 656, "pragmatic": 678},
    "deepseek_v4_flash": {"purist": 619, "pragmatic": 641},
    "qwen36_35b": {"purist": 660, "pragmatic": 680},
    "gemma4_26b": {"purist": 643, "pragmatic": 676},
}

JULY31_FLOORS_AFTER = {
    "gpt41mini": {"purist": 677, "pragmatic": 695},
    "gpt56luna": {"purist": 660, "pragmatic": 687},
    "gpt56sol": {"purist": 660, "pragmatic": 685},
    "deepseek_v4_flash": {"purist": 627, "pragmatic": 653},
    "qwen36_35b": {"purist": 657, "pragmatic": 676},
    "gemma4_26b": {"purist": 647, "pragmatic": 681},
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _selection_label(row: dict[str, Any]) -> str | None:
    structured = row.get("structured_record") or {}
    selection = structured.get("selection") or {}
    value = selection.get("final_label")
    if value is None:
        return None
    return str(value)


def _correct(row: dict[str, Any], key: str) -> bool:
    comparison = row.get("comparison")
    return bool(comparison and comparison.get(key))


def _parse_missing(row: dict[str, Any]) -> bool:
    return row.get("comparison") is None


def _score_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "rows": len(rows),
        "purist": sum(_correct(row, "purist_correct") for row in rows),
        "pragmatic": sum(_correct(row, "pragmatic_correct") for row in rows),
        "parse_missing": sum(_parse_missing(row) for row in rows),
    }


def _delta(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    before_by_id = {int(row["source_row_index"]): row for row in before}
    after_by_id = {int(row["source_row_index"]): row for row in after}
    if before_by_id.keys() != after_by_id.keys():
        raise ValueError("replay source IDs differ from the original artifact")
    changed: list[dict[str, Any]] = []
    counts = {
        "changed_final_labels": 0,
        "purist_wrong_to_correct": 0,
        "purist_correct_to_wrong": 0,
        "pragmatic_wrong_to_correct": 0,
        "pragmatic_correct_to_wrong": 0,
        "parse_missing_rescued": 0,
    }
    for source_id, old in before_by_id.items():
        new = after_by_id[source_id]
        old_label = _selection_label(old)
        new_label = _selection_label(new)
        old_p = _correct(old, "purist_correct")
        new_p = _correct(new, "purist_correct")
        old_g = _correct(old, "pragmatic_correct")
        new_g = _correct(new, "pragmatic_correct")
        label_changed = old_label != new_label
        if label_changed:
            counts["changed_final_labels"] += 1
        counts["purist_wrong_to_correct"] += not old_p and new_p
        counts["purist_correct_to_wrong"] += old_p and not new_p
        counts["pragmatic_wrong_to_correct"] += not old_g and new_g
        counts["pragmatic_correct_to_wrong"] += old_g and not new_g
        if _parse_missing(old) and not _parse_missing(new):
            counts["parse_missing_rescued"] += 1
        if label_changed or old_p != new_p or old_g != new_g:
            changed.append(
                {
                    "source_row_index": source_id,
                    "before_label": old_label,
                    "after_label": new_label,
                    "before_purist": old_p,
                    "after_purist": new_p,
                    "before_pragmatic": old_g,
                    "after_pragmatic": new_g,
                }
            )
    return counts, changed


def _replay(
    *,
    slug: str,
    model: str,
    temperature: float,
    max_tokens: int,
    source: Path,
    prompt_version: str,
    overwrite: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source_rows = load_jsonl_rows(source)
    records = load_records_for_split("validation")
    expected = {int(record.source_row_index) for record in records}
    source_ids = [int(row["source_row_index"]) for row in source_rows]
    if len(source_rows) != 750 or set(source_ids) != expected:
        raise ValueError(f"{slug} is not a complete unique dev750 artifact")
    versions = {row.get("prompt_version") for row in source_rows}
    if versions != {prompt_version} and prompt_version not in versions:
        # June 7 mini may omit a uniform prompt_version field on every row.
        if prompt_version != hybrid_structured_events.PROMPT_VERSION_V0_5:
            raise ValueError(f"{slug} prompt versions {versions} != {prompt_version}")
    raw_outputs = {
        int(row["source_row_index"]): str(row.get("raw_output") or "")
        for row in source_rows
    }
    if any(not value.strip() for value in raw_outputs.values()):
        raise ValueError(f"{slug} has empty raw outputs")

    scratch = SCRATCH_DIR / slug
    rows_path = scratch / "validation750.rows.jsonl"
    if rows_path.exists() and not overwrite:
        replay_rows = load_jsonl_rows(rows_path)
        return source_rows, replay_rows, {"reused_scratch": True, "rows_path": rows_path}

    hybrid_structured_events.set_active_prompt_version(prompt_version)
    manifest = load_split_manifest()
    replay_rows, metadata = hybrid_structured_events.run_split(
        records,
        split="validation",
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode="prompt-only",
        dspy_cache=False,
        escalation_reason="Predeclared 2026-08-13 six-model current-stack no-call replay",
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(source.relative_to(REPO_ROOT)),
        repair_config=hybrid_structured_events.StructuredRepairConfig.for_mode(
            "hybrid_full_stack"
        ),
        progress_every=150,
    )
    scratch.mkdir(parents=True, exist_ok=True)
    hybrid_structured_events.write_jsonl(replay_rows, rows_path)
    return source_rows, replay_rows, {
        "reused_scratch": False,
        "rows_path": rows_path,
        "metadata_summary": metadata.get("summary"),
    }


def _model_payload(
    slug: str,
    model: str,
    source_rows: list[dict[str, Any]],
    replay_rows: list[dict[str, Any]],
    source: Path,
    prompt_version: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    before = _score_rows(source_rows)
    after = _score_rows(replay_rows)
    delta, changed = _delta(source_rows, replay_rows)
    return {
        "slug": slug,
        "model": model,
        "prompt_version": prompt_version,
        "source_artifact": source.relative_to(REPO_ROOT).as_posix(),
        "source_sha256": _sha256(source),
        "scratch_rows": extra["rows_path"].relative_to(REPO_ROOT).as_posix(),
        "before": before,
        "after": after,
        "delta_purist": after["purist"] - before["purist"],
        "delta_pragmatic": after["pragmatic"] - before["pragmatic"],
        "transitions": delta,
        "historical_not_same_raw": {
            "july27_v05_panel": JULY27_V05_PANEL.get(slug),
            "july31_floors_after": JULY31_FLOORS_AFTER.get(slug),
        },
        "changed_row_count": len(changed),
        "changed_rows": changed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--skip-mini-companion",
        action="store_true",
        help="Skip the June 7 v0.5 GPT-4.1-mini companion cell",
    )
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cells: dict[str, Any] = {}
    all_changed: list[dict[str, Any]] = []
    for slug, model, temperature, max_tokens in MODELS:
        source = JULY18_ROOT / f"{slug}--llm_with_rules.jsonl"
        print(f"replaying {slug} from {source.relative_to(REPO_ROOT)}", flush=True)
        source_rows, replay_rows, extra = _replay(
            slug=slug,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            source=source,
            prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_7,
            overwrite=args.overwrite,
        )
        payload = _model_payload(
            slug,
            model,
            source_rows,
            replay_rows,
            source,
            hybrid_structured_events.PROMPT_VERSION_V0_7,
            extra,
        )
        for row in payload["changed_rows"]:
            all_changed.append({"model_slug": slug, **row})
        published = {k: v for k, v in payload.items() if k != "changed_rows"}
        cells[slug] = published
        print(
            f"  {slug}: {payload['before']['purist']} -> {payload['after']['purist']} Purist "
            f"({payload['delta_purist']:+d})",
            flush=True,
        )

    pooled_before_p = sum(cell["before"]["purist"] for cell in cells.values())
    pooled_after_p = sum(cell["after"]["purist"] for cell in cells.values())
    pooled_before_g = sum(cell["before"]["pragmatic"] for cell in cells.values())
    pooled_after_g = sum(cell["after"]["pragmatic"] for cell in cells.values())
    pooled_parse_before = sum(cell["before"]["parse_missing"] for cell in cells.values())
    pooled_parse_after = sum(cell["after"]["parse_missing"] for cell in cells.values())

    companion = None
    if not args.skip_mini_companion:
        print("replaying June 7 v0.5 mini companion", flush=True)
        source_rows, replay_rows, extra = _replay(
            slug="gpt41mini_v05_june07",
            model="openai/gpt-4.1-mini",
            temperature=0.0,
            max_tokens=10_000,
            source=JUNE07_MINI,
            prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_5,
            overwrite=args.overwrite,
        )
        companion = _model_payload(
            "gpt41mini_v05_june07",
            "openai/gpt-4.1-mini",
            source_rows,
            replay_rows,
            JUNE07_MINI,
            hybrid_structured_events.PROMPT_VERSION_V0_5,
            extra,
        )
        companion_changed = companion.pop("changed_rows")
        companion["changed_row_count"] = len(companion_changed)
        write_jsonl_rows(
            [{"model_slug": "gpt41mini_v05_june07", **row} for row in companion_changed],
            OUT_DIR / "june07_mini_v05_changed_rows.jsonl",
        )
        print(
            f"  mini v0.5: {companion['before']['purist']} -> "
            f"{companion['after']['purist']} Purist",
            flush=True,
        )

    summary = {
        "schema_version": "gan2026.six_model_current_stack_dev750_replay.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL,
        "git": _git_note(),
        "dataset": "Gan 2026",
        "split": "dev750",
        "split_machine": "validation",
        "method": "llm_with_rules",
        "call_mode": "saved_raw_output_no_call",
        "repair_mode": "hybrid_full_stack",
        "current_repair": (
            "HEAD hybrid_full_stack including floors, selected-evidence, "
            "diary, breakthrough, cluster-burden v1/v2, unique-month calendar log"
        ),
        "claim_boundary": (
            "Development no-call replay. Primary six-model cell uses July 18 v0.7 "
            "saved raw outputs. Selected paper prompt remains v0.5; that six-model "
            "raw set is not on this checkout. Not holdout. Not rules-only or llm-only. "
            "Does not rewrite Decision 0046/0047 or C16 holdout fills."
        ),
        "dev750_v07_july18": {
            "models": cells,
            "pooled": {
                "rows": 4500,
                "before_purist": pooled_before_p,
                "after_purist": pooled_after_p,
                "delta_purist": pooled_after_p - pooled_before_p,
                "before_pragmatic": pooled_before_g,
                "after_pragmatic": pooled_after_g,
                "delta_pragmatic": pooled_after_g - pooled_before_g,
                "before_parse_missing": pooled_parse_before,
                "after_parse_missing": pooled_parse_after,
                "purist_wrong_to_correct": sum(
                    cell["transitions"]["purist_wrong_to_correct"]
                    for cell in cells.values()
                ),
                "purist_correct_to_wrong": sum(
                    cell["transitions"]["purist_correct_to_wrong"]
                    for cell in cells.values()
                ),
                "pragmatic_wrong_to_correct": sum(
                    cell["transitions"]["pragmatic_wrong_to_correct"]
                    for cell in cells.values()
                ),
                "pragmatic_correct_to_wrong": sum(
                    cell["transitions"]["pragmatic_correct_to_wrong"]
                    for cell in cells.values()
                ),
                "changed_final_labels": sum(
                    cell["transitions"]["changed_final_labels"]
                    for cell in cells.values()
                ),
            },
        },
        "dev750_v05_june07_mini_companion": companion,
    }
    write_jsonl_rows(all_changed, OUT_DIR / "dev750_v07_changed_rows.jsonl")
    summary_path = OUT_DIR / "replay_summary.json"
    # Drop per-model changed row lists from JSON (they live in jsonl).
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary["dev750_v07_july18"]["pooled"], indent=2))
    print(f"wrote {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
