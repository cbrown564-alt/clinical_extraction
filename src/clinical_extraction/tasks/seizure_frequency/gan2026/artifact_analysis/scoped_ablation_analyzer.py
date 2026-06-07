"""Unified parameterized analyzer for ablation studies over Gan 2026 pipelines.

This module consolidates the shared metrics calculation, JSON summary writing,
and markdown report formatting previously duplicated across custom ablation scripts.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_predictions,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)


@dataclass(frozen=True)
class AblationVariant:
    name: str
    description: str
    run_fn: Callable[[Any], Any]  # function to compute predicted label / rate


class ScopedAblationAnalyzer:
    """Consolidated, parameterized engine for running ablation experiments."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        variants: Sequence[AblationVariant],
    ) -> None:
        self.name = name
        self.description = description
        self.variants = variants

    def run_ablation(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        split: str,
        split_manifest: str,
        gold_frequency_extractor: Callable[[Mapping[str, Any]], float],
        gold_label_extractor: Callable[[Mapping[str, Any]], str],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Run all variants over the records and compute comparative performance."""
        rows = []
        for record in records:
            gold_label = gold_label_extractor(record)
            gold_freq = gold_frequency_extractor(record)

            variant_results = {}
            for variant in self.variants:
                pred_label, pred_freq = variant.run_fn(record)
                variant_results[variant.name] = {
                    "final_label": pred_label,
                    "monthly_frequency": pred_freq,
                    "correct": pred_label == gold_label,
                }

            rows.append({
                "source_row_index": int(record["source_row_index"]),
                "source": str(record.get("source", "unknown")),
                "source_artifact": str(record.get("source_artifact", "unknown")),
                "gold_normalized_label": gold_label,
                "gold_monthly_frequency": gold_freq,
                "variant_results": variant_results,
            })

        # Calculate metrics for each variant
        variants_summary = {}
        for variant in self.variants:
            y_true = [row["gold_monthly_frequency"] for row in rows]
            y_pred = [row["variant_results"][variant.name]["monthly_frequency"] for row in rows]
            purist = evaluate_predictions(y_true, y_pred, method="purist")
            pragmatic = evaluate_predictions(y_true, y_pred, method="pragmatic")

            variants_summary[variant.name] = {
                "exact_matches": sum(bool(row["variant_results"][variant.name]["correct"]) for row in rows),
                "purist_accuracy": purist["micro"]["accuracy"],
                "purist_f1": purist["micro"]["f1"],
                "pragmatic_accuracy": pragmatic["micro"]["accuracy"],
                "pragmatic_f1": pragmatic["micro"]["f1"],
            }

        metadata = {
            "artifact_kind": f"gan2026_{self.name}_ablation",
            "date": "2026-06-07",
            "split": split,
            "split_manifest": split_manifest,
            "row_count": len(rows),
            "variants": {v.name: v.description for v in self.variants},
            "summary": {
                "variants": variants_summary,
            },
        }
        return rows, metadata

    def write_json(self, metadata: Mapping[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_report(
        self,
        rows: Sequence[Mapping[str, Any]],
        metadata: Mapping[str, Any],
        path: Path,
        *,
        jsonl_path: Path,
        json_path: Path,
    ) -> None:
        summary = metadata["summary"]
        lines = [
            f"# {self.description}",
            "",
            "Diagnostic only: this is validation-cycle replay over saved artifacts.",
            "",
            f"- Split: `{metadata['split']}`",
            f"- Split manifest: `{metadata['split_manifest']}`",
            f"- Rows: {metadata['row_count']}",
            f"- JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            "",
            "## Ablation Variants",
            "",
            "| Variant | Exact matches | Purist F1 | Pragmatic F1 |",
            "| --- | ---: | ---: | ---: |",
        ]
        for variant in self.variants:
            stats = summary["variants"][variant.name]
            lines.append(
                f"| `{variant.name}` | {stats['exact_matches']}/{metadata['row_count']} | "
                f"{stats['purist_f1']:.4f} | {stats['pragmatic_f1']:.4f} |"
            )

        lines.extend([
            "",
            "## Detailed Results",
            "",
            "| Row | Gold | " + " | ".join(f"{v.name}" for v in self.variants) + " |",
            "| ---: | --- | " + " | ".join("---" for _ in self.variants) + " |",
        ])
        for row in rows:
            variant_cells = [
                row["variant_results"][v.name]["final_label"] for v in self.variants
            ]
            lines.append(
                f"| {row['source_row_index']} | {row['gold_normalized_label']} | " + " | ".join(variant_cells) + " |"
            )

        write_markdown_report(path, lines)
