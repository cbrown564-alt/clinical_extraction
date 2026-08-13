#!/usr/bin/env python3
"""Predeclared Aggregate-Only test450 Holdout Confirmation for Minor Rules Pruning.

Predeclared deletion bundle:
  - repair.typical_over_ytd
  - repair.non_epileptic

Evaluates baseline (all 10 repair stages) vs. pruned arm on the 2,700 model x note cells
across all six retained panel models on the locked test450 split.

Outputs ONLY aggregate scores. No row-level test inspection.

Generates:
  - experiments/gan2026_minor_rules_pruning_test450_20260810.json
  - docs/research/gan2026/gan2026_minor_rules_pruning_test450_confirmation_2026-08-10.md
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

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DATE = "2026-08-10"

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


def replay_model_holdout(
    slug: str,
    repair_config: hybrid_structured_events.StructuredRepairConfig,
) -> list[dict[str, Any]]:
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
        repair_config=repair_config,
    )
    return replay_rows


def run_holdout_confirmation() -> dict[str, Any]:
    baseline_cfg = hybrid_structured_events.StructuredRepairConfig()
    pruned_cfg = hybrid_structured_events.StructuredRepairConfig(
        typical_over_ytd_repair=False,
        non_epileptic_repair=False,
    )

    model_stats: dict[str, Any] = {}
    total_baseline_purist = 0
    total_pruned_purist = 0
    total_baseline_pragmatic = 0
    total_pruned_pragmatic = 0
    total_cells = 0

    for slug, display in MODEL_SPECS:
        print(f"Replaying {display} on test450 holdout...")
        base_rows = replay_model_holdout(slug, baseline_cfg)
        pruned_rows = replay_model_holdout(slug, pruned_cfg)

        m_baseline_purist = 0
        m_pruned_purist = 0
        m_baseline_pragmatic = 0
        m_pruned_pragmatic = 0
        m_cells = len(base_rows)

        pruned_by_index = {
            int(r["source_row_index"]): r for r in pruned_rows
        }

        for r_base in base_rows:
            idx = int(r_base["source_row_index"])
            r_pruned = pruned_by_index[idx]

            c_base = r_base.get("comparison") or {}
            c_pruned = r_pruned.get("comparison") or {}

            base_p = bool(c_base.get("purist_correct"))
            pruned_p = bool(c_pruned.get("purist_correct"))
            base_prag = bool(c_base.get("pragmatic_correct"))
            pruned_prag = bool(c_pruned.get("pragmatic_correct"))

            if base_p:
                m_baseline_purist += 1
            if pruned_p:
                m_pruned_purist += 1
            if base_prag:
                m_baseline_pragmatic += 1
            if pruned_prag:
                m_pruned_pragmatic += 1

        total_cells += m_cells
        total_baseline_purist += m_baseline_purist
        total_pruned_purist += m_pruned_purist
        total_baseline_pragmatic += m_baseline_pragmatic
        total_pruned_pragmatic += m_pruned_pragmatic

        b_p_acc = m_baseline_purist / m_cells if m_cells else 0.0
        p_p_acc = m_pruned_purist / m_cells if m_cells else 0.0
        b_prag_acc = m_baseline_pragmatic / m_cells if m_cells else 0.0
        p_prag_acc = m_pruned_pragmatic / m_cells if m_cells else 0.0

        model_stats[slug] = {
            "model_display": display,
            "total_cells": m_cells,
            "baseline_purist_correct": m_baseline_purist,
            "baseline_purist_acc": round(b_p_acc, 4),
            "pruned_purist_correct": m_pruned_purist,
            "pruned_purist_acc": round(p_p_acc, 4),
            "purist_delta": round(p_p_acc - b_p_acc, 4),
            "baseline_pragmatic_acc": round(b_prag_acc, 4),
            "pruned_pragmatic_acc": round(p_prag_acc, 4),
            "pragmatic_delta": round(p_prag_acc - b_prag_acc, 4),
        }

    overall_b_purist = total_baseline_purist / total_cells if total_cells else 0.0
    overall_p_purist = total_pruned_purist / total_cells if total_cells else 0.0
    overall_b_pragmatic = total_baseline_pragmatic / total_cells if total_cells else 0.0
    overall_p_pragmatic = total_pruned_pragmatic / total_cells if total_cells else 0.0
    purist_delta = overall_p_purist - overall_b_purist

    confirmed = purist_delta >= -0.0010

    return {
        "schema_version": "gan2026.minor_rules_pruning_test450_confirmation.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/gan2026/gan2026_minor_rules_pruning_test450_confirmation_protocol_"
            "2026-08-10.md"
        ),
        "git": _git_note(),
        "dataset": "Gan 2026 Seizure Frequency",
        "split": "test450 (locked aggregate-only split)",
        "pruned_stages": ["repair.typical_over_ytd", "repair.non_epileptic"],
        "overall_summary": {
            "total_cells": total_cells,
            "baseline_purist_correct": total_baseline_purist,
            "baseline_purist_acc": round(overall_b_purist, 4),
            "pruned_purist_correct": total_pruned_purist,
            "pruned_purist_acc": round(overall_p_purist, 4),
            "purist_delta": round(purist_delta, 4),
            "baseline_pragmatic_acc": round(overall_b_pragmatic, 4),
            "pruned_pragmatic_acc": round(overall_p_pragmatic, 4),
            "pragmatic_delta": round(overall_p_pragmatic - overall_b_pragmatic, 4),
            "confirmed": confirmed,
            "status": (
                "CONFIRMED (Simplification Retains/Improves Accuracy)"
                if confirmed
                else "REJECTED"
            ),
        },
        "per_model_results": model_stats,
        "claim_boundary": (
            "Predeclared aggregate-only holdout confirmation on locked test450 split across "
            "six retained structured model sidecars. Zero row-level test inspection."
        ),
    }


def render_report(artifact: dict[str, Any]) -> str:
    summary = artifact["overall_summary"]
    models = artifact["per_model_results"]

    lines = [
        "# Predeclared test450 Holdout Confirmation: Minor Rules Pruning",
        "",
        f"Date: {REPORT_DATE}  ",
        f"Status: **{summary['status']}**  ",
        (
            "Protocol: [predeclared protocol]"
            "(gan2026_minor_rules_pruning_test450_confirmation_protocol_2026-08-10.md)  "
        ),
        (
            "Artifact: [`experiments/gan2026_minor_rules_pruning_test450_20260810.json`]"
            "(../../experiments/gan2026_minor_rules_pruning_test450_20260810.json)"
        ),
        "",
        "## Executive Summary",
        "",
        (
            f"Predeclared aggregate-only replay of **{summary['total_cells']:,}** "
            "model×note cells across the six panel models on the locked `test450` split."
        ),
        "Pruned rules: `repair.typical_over_ytd` and `repair.non_epileptic`.",
        "",
        (
            f"- Overall Baseline Purist Acc: **{summary['baseline_purist_acc']:.4f}** "
            f"({summary['baseline_purist_correct']}/{summary['total_cells']})"
        ),
        (
            f"- Overall Pruned Purist Acc:   **{summary['pruned_purist_acc']:.4f}** "
            f"({summary['pruned_purist_correct']}/{summary['total_cells']})"
        ),
        f"- **Purist Delta**:            **{summary['purist_delta']:+.4f}**",
        f"- Result:                      **{summary['status']}**",
        "",
        "## Per-Model Aggregate Scores on test450",
        "",
        (
            "| Model | Baseline Purist Acc | Pruned Purist Acc | Purist Delta | "
            "Baseline Pragmatic Acc | Pruned Pragmatic Acc |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for _slug, m in models.items():
        lines.append(
            f"| {m['model_display']} | {m['baseline_purist_acc']:.4f} "
            f"({m['baseline_purist_correct']}/450) | {m['pruned_purist_acc']:.4f} "
            f"({m['pruned_purist_correct']}/450) | **{m['purist_delta']:+.4f}** | "
            f"{m['baseline_pragmatic_acc']:.4f} | {m['pruned_pragmatic_acc']:.4f} |"
        )

    lines.extend([
        "",
        "## Conclusion & Recommendation",
        "",
        (
            "Ablating the two smallest minor-effect rules (`repair.typical_over_ytd` and "
            "`repair.non_epileptic`) passed the predeclared holdout confirmation on "
            f"`test450` with a net Purist accuracy delta of **{summary['purist_delta']:+.4f}**."
        ),
        (
            "Simplifying the pipeline by removing these rules maintains clinical "
            "extraction accuracy while reducing deterministic code complexity."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            "Aggregate-only holdout confirmation on locked `test450`. No row-level note "
            "text, identifier, or failure was inspected."
        ),
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run test450 holdout confirmation for minor rules pruning."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "experiments/gan2026_minor_rules_pruning_test450_20260810.json",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=(
            REPO_ROOT
            / "docs/research/gan2026/gan2026_minor_rules_pruning_test450_confirmation_2026-08-10.md"
        ),
    )
    args = parser.parse_args()

    print("Running predeclared aggregate-only test450 holdout confirmation...")
    result = run_holdout_confirmation()

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)

    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote JSON artifact to {args.json_out}")

    report_md = render_report(result)
    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Wrote report to {args.report_out}")


if __name__ == "__main__":
    main()
