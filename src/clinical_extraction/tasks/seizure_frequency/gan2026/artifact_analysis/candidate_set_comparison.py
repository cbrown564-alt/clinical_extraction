"""Compare deterministic and LLM validation250 CandidateSet diagnostics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_set_diagnostics import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_DETERMINISTIC_DIAGNOSTICS_JSONL,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_LLM_DIAGNOSTICS_JSONL = Path(
    "experiments/gan2026_validation250_llm_candidate_set_diagnostics_v0.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_candidate_set_comparison_v0.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_candidate_set_comparison_v0.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_candidate_set_comparison_v0.md")


def build_candidate_set_comparison(
    deterministic_rows: Sequence[Mapping[str, Any]],
    llm_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    llm_by_index = {int(row["source_row_index"]): row for row in llm_rows}
    rows = [
        _comparison_row(det_row, llm_by_index[int(det_row["source_row_index"])])
        for det_row in deterministic_rows
    ]
    return rows, summarize_comparison(rows)


def summarize_comparison(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    both = [row for row in rows if row["deterministic_compatible"] and row["llm_compatible"]]
    deterministic_only = [
        row for row in rows if row["deterministic_compatible"] and not row["llm_compatible"]
    ]
    llm_only = [
        row for row in rows if row["llm_compatible"] and not row["deterministic_compatible"]
    ]
    neither = [
        row for row in rows if not row["deterministic_compatible"] and not row["llm_compatible"]
    ]
    union = [row for row in rows if row["union_compatible"]]
    by_gold_kind: dict[str, Counter[str]] = {}
    for row in rows:
        kind = str(row["gold_candidate_kind"])
        by_gold_kind.setdefault(kind, Counter())
        by_gold_kind[kind]["rows"] += 1
        if row["deterministic_compatible"]:
            by_gold_kind[kind]["deterministic"] += 1
        if row["llm_compatible"]:
            by_gold_kind[kind]["llm"] += 1
        if row["union_compatible"]:
            by_gold_kind[kind]["union"] += 1
    return {
        "artifact_name": "gan2026_validation250_candidate_set_comparison_v0",
        "row_count": len(rows),
        "claim_boundary": (
            "Validation250 extract-stage comparison only. Compatible-kind coverage "
            "is not normalized-label recall and makes no benchmark-comparable claim."
        ),
        "summary": {
            "deterministic_compatible_rows": sum(row["deterministic_compatible"] for row in rows),
            "llm_compatible_rows": sum(row["llm_compatible"] for row in rows),
            "union_compatible_rows": len(union),
            "deterministic_compatible_rate": _rate(
                sum(row["deterministic_compatible"] for row in rows), len(rows)
            ),
            "llm_compatible_rate": _rate(sum(row["llm_compatible"] for row in rows), len(rows)),
            "union_compatible_rate": _rate(len(union), len(rows)),
            "both_compatible_rows": len(both),
            "deterministic_only_rows": len(deterministic_only),
            "llm_only_rows": len(llm_only),
            "neither_rows": len(neither),
            "llm_diagnostic_issue_rows": sum(bool(row["llm_diagnostic_issues"]) for row in rows),
            "llm_missing_candidate_set_rows": sum(
                row["llm_candidate_set_status"] == "missing" for row in rows
            ),
            "by_gold_candidate_kind": {
                kind: {
                    "rows": counts["rows"],
                    "deterministic_compatible_rows": counts["deterministic"],
                    "llm_compatible_rows": counts["llm"],
                    "union_compatible_rows": counts["union"],
                    "union_compatible_rate": _rate(counts["union"], counts["rows"]),
                }
                for kind, counts in sorted(by_gold_kind.items())
            },
            "llm_only_source_row_indices": [int(row["source_row_index"]) for row in llm_only],
            "deterministic_only_source_row_indices": [
                int(row["source_row_index"]) for row in deterministic_only
            ],
            "neither_source_row_indices": [int(row["source_row_index"]) for row in neither],
        },
        "inspection_examples": {
            "llm_only_rows": _examples(llm_only),
            "deterministic_only_rows": _examples(deterministic_only),
            "neither_rows": _examples(neither),
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Validation250 Candidate Set Comparison",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Comparison JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Deterministic compatible rows: {summary['deterministic_compatible_rows']}",
        f"- LLM compatible rows: {summary['llm_compatible_rows']}",
        f"- Union compatible rows: {summary['union_compatible_rows']}",
        f"- Deterministic-only rows: {summary['deterministic_only_rows']}",
        f"- LLM-only rows: {summary['llm_only_rows']}",
        f"- Neither rows: {summary['neither_rows']}",
        f"- LLM diagnostic issue rows: {summary['llm_diagnostic_issue_rows']}",
        "",
        "## By Gold Candidate Kind",
        "",
        "| Gold kind | Rows | Det | LLM | Union | Union rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for kind, values in summary["by_gold_candidate_kind"].items():
        lines.append(
            f"| `{kind}` | {values['rows']} | "
            f"{values['deterministic_compatible_rows']} | "
            f"{values['llm_compatible_rows']} | "
            f"{values['union_compatible_rows']} | "
            f"{values['union_compatible_rate']:.3f} |"
        )
    lines.extend(["", "## Inspection Examples", ""])
    for title, examples in metadata["inspection_examples"].items():
        lines.extend([f"### {title.replace('_', ' ').title()}", ""])
        if not examples:
            lines.append("- None.")
        for row in examples:
            lines.append(
                "- "
                f"{row['source_row_index']}: gold `{row['gold_label']}` "
                f"({row['gold_candidate_kind']}), det={row['deterministic_kinds']}, "
                f"llm={row['llm_kinds']}, excerpt: {row['note_excerpt']}"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _comparison_row(
    deterministic: Mapping[str, Any],
    llm: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "source_row_index": int(deterministic["source_row_index"]),
        "gold_label": deterministic["gold_label"],
        "gold_candidate_kind": deterministic["gold_candidate_kind"],
        "deterministic_compatible": bool(deterministic["compatible_candidate_present"]),
        "llm_compatible": bool(llm["compatible_candidate_present"]),
        "union_compatible": bool(
            deterministic["compatible_candidate_present"] or llm["compatible_candidate_present"]
        ),
        "deterministic_candidate_count": int(deterministic["candidate_count"]),
        "llm_candidate_count": int(llm["candidate_count"]),
        "deterministic_kinds": list(deterministic["candidate_kinds_present"]),
        "llm_kinds": list(llm["candidate_kinds_present"]),
        "llm_candidate_set_status": llm["candidate_set_status"],
        "llm_diagnostic_issues": list(llm["diagnostic_issues"]),
        "note_excerpt": deterministic["note_excerpt"],
    }


def _examples(rows: Sequence[Mapping[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    return [
        {
            "source_row_index": int(row["source_row_index"]),
            "gold_label": row["gold_label"],
            "gold_candidate_kind": row["gold_candidate_kind"],
            "deterministic_kinds": list(row["deterministic_kinds"]),
            "llm_kinds": list(row["llm_kinds"]),
            "note_excerpt": row["note_excerpt"],
        }
        for row in rows[:limit]
    ]


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deterministic-diagnostics-jsonl",
        type=Path,
        default=DEFAULT_DETERMINISTIC_DIAGNOSTICS_JSONL,
    )
    parser.add_argument(
        "--llm-diagnostics-jsonl",
        type=Path,
        default=DEFAULT_LLM_DIAGNOSTICS_JSONL,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows, metadata = build_candidate_set_comparison(
        load_jsonl_rows(args.deterministic_diagnostics_jsonl),
        load_jsonl_rows(args.llm_diagnostics_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
