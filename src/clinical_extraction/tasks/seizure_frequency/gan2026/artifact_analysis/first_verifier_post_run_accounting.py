"""Implement post-run comparison/accounting summarizing first-verifier actions against deterministic V0 by bucket and report section."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_INPUT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_accounting_v6_2026-06-06.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_first_verifier_accounting_v6_2026-06-06.md"
)


def compute_accounting(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Perform post-run comparison/accounting of verifier actions vs baseline V0 actions."""
    
    by_bucket: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_section: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    
    for row in rows:
        bucket = str(row.get("route_bucket", "unknown"))
        section = str(row.get("report_section", "unknown"))
        by_bucket[bucket].append(row)
        by_section[section].append(row)

    bucket_summaries = {}
    for bucket, bucket_rows in by_bucket.items():
        cross_tab = Counter()
        for r in bucket_rows:
            decision = r.get("verifier_decision") or {}
            action = str(decision.get("action", "unknown"))
            baseline = str(decision.get("baseline_action", "unknown"))
            cross_tab[(baseline, action)] += 1
        
        bucket_summaries[bucket] = [
            {
                "baseline_action": b,
                "verifier_action": v,
                "count": count,
            }
            for (b, v), count in sorted(cross_tab.items())
        ]

    section_summaries = {}
    for section, section_rows in by_section.items():
        cross_tab = Counter()
        for r in section_rows:
            decision = r.get("verifier_decision") or {}
            action = str(decision.get("action", "unknown"))
            baseline = str(decision.get("baseline_action", "unknown"))
            cross_tab[(baseline, action)] += 1
            
        section_summaries[section] = [
            {
                "baseline_action": b,
                "verifier_action": v,
                "count": count,
            }
            for (b, v), count in sorted(cross_tab.items())
        ]

    return {
        "artifact_kind": "gan2026_validation750_first_verifier_post_run_accounting",
        "date": "2026-06-06",
        "source_artifact": str(DEFAULT_INPUT_JSONL_PATH),
        "total_rows_processed": len(rows),
        "by_bucket": dict(sorted(bucket_summaries.items())),
        "by_section": dict(sorted(section_summaries.items())),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 First Verifier Post-Run Accounting V6",
        "",
        "validation-development first action-only verifier comparison/accounting against deterministic V0.",
        "",
        "## Summary",
        "",
        f"- Source verifier live run: `{metadata['source_artifact']}`",
        f"- Output JSON data: `{json_path}`",
        f"- Total rows processed: {metadata['total_rows_processed']}",
        "",
        "## Accounting By Route Bucket",
        "",
    ]
    for bucket, entries in sorted(metadata["by_bucket"].items()):
        lines.extend([
            f"### Bucket: `{bucket}`",
            "",
            "| V0 Baseline Action | Verifier Action | Count |",
            "| --- | --- | ---: |",
        ])
        for entry in entries:
            lines.append(
                f"| `{entry['baseline_action']}` | `{entry['verifier_action']}` | {entry['count']} |"
            )
        lines.append("")

    lines.extend([
        "## Accounting By Report Section",
        "",
    ])
    for section, entries in sorted(metadata["by_section"].items()):
        lines.extend([
            f"### Section: `{section}`",
            "",
            "| V0 Baseline Action | Verifier Action | Count |",
            "| --- | --- | ---: |",
        ])
        for entry in entries:
            lines.append(
                f"| `{entry['baseline_action']}` | `{entry['verifier_action']}` | {entry['count']} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl-path", type=Path, default=DEFAULT_INPUT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows = load_jsonl_rows(args.input_jsonl_path)
    metadata = compute_accounting(rows)
    metadata["source_artifact"] = str(args.input_jsonl_path)
    
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, json_path=args.json_path)
    
    print(f"Processed {len(rows)} rows. Written accounting report to {args.report_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
