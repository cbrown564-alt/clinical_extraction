#!/usr/bin/env python3
"""Predeclared Aggregate-Only test450 Holdout Confirmation for Cluster Burden Rule Tuning v2.

Follow-on to the 2026-08-10 cluster burden tuning pass. A dev750 recoverability audit of
the remaining `cluster_burden` hybrid wrongs classified 24/96 as syntax-variant failures
where the model's selected evidence still names cluster structure but the assembler grammar
missed it (reversed period/count order, "N cluster days this month" without a strict tail,
"weekly ... N per cluster" order, adjective-separated counts). This pass adds targeted
grammar coverage for those variants only; the remaining ~72 wrongs do not mention "cluster"
in the selected evidence at all and are an upstream evidence-selection gap, out of scope here.

Evaluates the tuned cluster evidence normalization rules across the 2,700 model x note cells
(450 notes x 6 retained panel models) on the locked test450 split.

Outputs ONLY aggregate scores. No row-level test inspection or failure leakage.

Generates:
  - experiments/gan2026_cluster_burden_tuning_v2_test450_20260811.json
  - docs/research/gan2026_cluster_burden_tuning_v2_test450_confirmation_2026-08-11.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (  # noqa: E402
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (  # noqa: E402
    hybrid_structured_events,
)

REPORT_DATE = "2026-08-11"

MODEL_SPECS = [
    ("gpt56sol", "GPT-5.6 Sol"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt41mini", "GPT-4.1-mini"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6 35B"),
    ("gemma4_26b", "Gemma 4 26B"),
]

GAN_HYBRID_SOURCES = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt41mini/rows.jsonl",
    "gpt56luna": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl",
    "gpt56sol": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt56sol/rows.jsonl",
    "deepseek_v4_flash": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05/deepseek_v4_flash/rows.jsonl"
    ),
    "qwen36_35b": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05_local/qwen36_35b/rows.jsonl"
    ),
    "gemma4_26b": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05_local/gemma4_26b/rows.jsonl"
    ),
}

GAN_HYBRID_MODELS = {
    "gpt41mini": ("openai/gpt-4.1-mini", 0.0, 10_000),
    "gpt56luna": ("openai/gpt-5.6-luna", 1.0, 10_000),
    "gpt56sol": ("openai/gpt-5.6-sol", 0.0, 10_000),
    "deepseek_v4_flash": ("deepseek/deepseek-v4-flash", 0.0, 32_000),
    "qwen36_35b": ("ollama_chat/qwen3.6:35b", 0.0, 16_000),
    "gemma4_26b": ("ollama_chat/gemma4:26b", 0.0, 16_000),
}


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


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def replay_model_holdout(slug: str) -> list[dict[str, Any]]:
    source = GAN_HYBRID_SOURCES[slug]
    model, temperature, max_tokens = GAN_HYBRID_MODELS[slug]
    source_rows = load_jsonl_rows(source)
    raw_outputs = {
        int(row["source_row_index"]): str(row.get("raw_output") or "")
        for row in source_rows
    }
    hybrid_structured_events.set_active_prompt_version(
        hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    manifest = load_split_manifest()
    replay_rows, _metadata = hybrid_structured_events.run_split(
        load_records_for_split("test"),
        split="test",
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode="prompt-only",
        dspy_cache=False,
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(source.relative_to(REPO_ROOT).as_posix()),
    )
    return replay_rows


def run_holdout_confirmation() -> dict[str, Any]:
    model_stats: dict[str, Any] = {}
    total_purist_correct = 0
    total_pragmatic_correct = 0
    total_cells = 0

    for slug, display in MODEL_SPECS:
        print(f"Replaying {display} on locked test450 split...", flush=True)
        rows = replay_model_holdout(slug)

        m_purist_correct = 0
        m_pragmatic_correct = 0
        m_cells = len(rows)

        by_bucket: dict[str, dict[str, int]] = {}

        for r in rows:
            c = r.get("comparison") or {}
            bucket = str(r.get("a_priori_bucket") or "unknown")

            if bucket not in by_bucket:
                by_bucket[bucket] = {"total": 0, "purist": 0, "pragmatic": 0}

            by_bucket[bucket]["total"] += 1

            p_ok = bool(c.get("purist_correct"))
            prag_ok = bool(c.get("pragmatic_correct"))

            if p_ok:
                m_purist_correct += 1
                by_bucket[bucket]["purist"] += 1
            if prag_ok:
                m_pragmatic_correct += 1
                by_bucket[bucket]["pragmatic"] += 1

        total_cells += m_cells
        total_purist_correct += m_purist_correct
        total_pragmatic_correct += m_pragmatic_correct

        p_acc = m_purist_correct / m_cells if m_cells else 0.0
        prag_acc = m_pragmatic_correct / m_cells if m_cells else 0.0

        bucket_summary = {}
        for b, b_data in by_bucket.items():
            tot = b_data["total"]
            bucket_summary[b] = {
                "total": tot,
                "purist_correct": b_data["purist"],
                "purist_acc": round(b_data["purist"] / tot, 4) if tot else 0.0,
                "pragmatic_correct": b_data["pragmatic"],
                "pragmatic_acc": round(b_data["pragmatic"] / tot, 4) if tot else 0.0,
            }

        model_stats[slug] = {
            "model_display": display,
            "total_cells": m_cells,
            "purist_correct": m_purist_correct,
            "purist_acc": round(p_acc, 4),
            "pragmatic_correct": m_pragmatic_correct,
            "pragmatic_acc": round(prag_acc, 4),
            "by_bucket": bucket_summary,
        }

    overall_purist_acc = total_purist_correct / total_cells if total_cells else 0.0
    overall_pragmatic_acc = total_pragmatic_correct / total_cells if total_cells else 0.0

    return {
        "schema_version": "gan2026.cluster_burden_tuning_v2_test450_confirmation.v1",
        "date": REPORT_DATE,
        "git": _git_note(),
        "dataset": "Gan 2026 Seizure Frequency",
        "split": "test450 (locked aggregate-only split)",
        "overall_summary": {
            "total_cells": total_cells,
            "purist_correct": total_purist_correct,
            "purist_acc": round(overall_purist_acc, 4),
            "pragmatic_correct": total_pragmatic_correct,
            "pragmatic_acc": round(overall_pragmatic_acc, 4),
        },
        "per_model_results": model_stats,
        "claim_boundary": (
            "Predeclared aggregate-only holdout evaluation on locked test450 split across "
            "six retained structured model sidecars. Zero row-level test inspection."
        ),
    }


def render_report(artifact: dict[str, Any]) -> str:
    summary = artifact["overall_summary"]
    models = artifact["per_model_results"]

    lines = [
        "# Predeclared test450 Holdout Confirmation: Cluster Burden Rule Tuning v2",
        "",
        f"Date: {REPORT_DATE}  ",
        (
            "Artifact: [`experiments/gan2026_cluster_burden_tuning_v2_test450_20260811.json`]"
            "(../../experiments/gan2026_cluster_burden_tuning_v2_test450_20260811.json)  "
        ),
        "",
        "## Executive Summary",
        "",
        (
            f"Aggregate-only evaluation of **{summary['total_cells']:,}** model×note cells "
            "across all six panel models on the locked `test450` split following a second "
            "cluster burden evidence rule tuning pass (dev750 recoverability audit: 14 "
            "rescued / 0 harmed on 4,500 cells, +0.31% overall Purist)."
        ),
        "",
        (
            f"- Overall Purist Accuracy:   **{summary['purist_acc']:.4f}** "
            f"({summary['purist_correct']}/{summary['total_cells']})"
        ),
        (
            f"- Overall Pragmatic Accuracy: **{summary['pragmatic_acc']:.4f}** "
            f"({summary['pragmatic_correct']}/{summary['total_cells']})"
        ),
        "",
        "## Per-Model Aggregate Scores on test450",
        "",
        "| Model | Total Cells | Purist Correct | Purist Acc | Pragmatic Correct | Pragmatic Acc |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for _slug, m in models.items():
        lines.append(
            f"| {m['model_display']} | {m['total_cells']} | {m['purist_correct']} | "
            f"**{m['purist_acc']:.4f}** | {m['pragmatic_correct']} | "
            f"**{m['pragmatic_acc']:.4f}** |"
        )

    lines.extend([
        "",
        "## Claim Boundary",
        "",
        (
            "Aggregate-only holdout evaluation on locked `test450`. No row-level note "
            "text, identifier, or failure was inspected."
        ),
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run test450 holdout evaluation for cluster burden rule tuning v2."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "experiments/gan2026_cluster_burden_tuning_v2_test450_20260811.json",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=(
            REPO_ROOT
            / "docs/research/gan2026_cluster_burden_tuning_v2_test450_confirmation_2026-08-11.md"
        ),
    )
    args = parser.parse_args()

    print("Running predeclared aggregate-only test450 holdout evaluation...", flush=True)
    result = run_holdout_confirmation()

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)

    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote JSON artifact to {args.json_out}", flush=True)

    report_md = render_report(result)
    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Wrote report to {args.report_out}", flush=True)


if __name__ == "__main__":
    main()
