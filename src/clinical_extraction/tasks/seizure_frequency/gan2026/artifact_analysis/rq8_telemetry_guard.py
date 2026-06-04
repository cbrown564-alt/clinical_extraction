"""Check whether RQ8 cost, latency, and token claims are supported."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REQUIRED_TELEMETRY_FIELDS = (
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "wall_clock_latency_seconds",
    "retry_count",
    "estimated_cost_per_1000_notes_usd",
)
DEFAULT_MATRIX_JSON_PATH = Path("experiments/gan2026_rq8_operational_matrix_2026-06-04.json")
DEFAULT_GUARD_JSON_PATH = Path("experiments/gan2026_rq8_telemetry_guard_2026-06-04.json")
DEFAULT_GUARD_REPORT_PATH = Path("experiments/gan2026_rq8_telemetry_guard_2026-06-04.md")


def build_rq8_telemetry_guard(matrix: Mapping[str, Any]) -> dict[str, Any]:
    rows = [row for row in matrix.get("rows") or [] if isinstance(row, Mapping)]
    missing_by_row = [_row_missing_fields(row) for row in rows]
    missing_counts = Counter(field for fields in missing_by_row for field in fields)
    complete_rows = sum(not fields for fields in missing_by_row)
    return {
        "artifact_kind": "gan2026_rq8_telemetry_guard",
        "date": "2026-06-04",
        "source_matrix": str(DEFAULT_MATRIX_JSON_PATH),
        "row_count": len(rows),
        "required_telemetry_fields": list(REQUIRED_TELEMETRY_FIELDS),
        "complete_telemetry_rows": complete_rows,
        "missing_telemetry_rows": len(rows) - complete_rows,
        "missing_field_counts": dict(sorted(missing_counts.items())),
        "component_surface_missing_fields": [
            {
                "component": str(row.get("component") or ""),
                "surface": str(row.get("surface") or ""),
                "model": str(row.get("model") or ""),
                "missing_fields": fields,
            }
            for row, fields in zip(rows, missing_by_row, strict=True)
            if fields
        ],
        "cost_latency_token_claim_authorized": complete_rows == len(rows) and bool(rows),
        "claim_boundary": _claim_boundary(complete_rows=complete_rows, row_count=len(rows)),
    }


def write_guard_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_guard_report(metadata: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 RQ8 Telemetry Guard",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Matrix rows | {metadata['row_count']} |",
        f"| Complete telemetry rows | {metadata['complete_telemetry_rows']} |",
        f"| Missing telemetry rows | {metadata['missing_telemetry_rows']} |",
        "| Cost/latency/token claim authorized | "
        f"{metadata['cost_latency_token_claim_authorized']} |",
        "",
        "## Missing Fields",
        "",
        "| Field | Rows missing |",
        "| --- | ---: |",
    ]
    for field, count in metadata["missing_field_counts"].items():
        lines.append(f"| `{field}` | {count} |")
    lines.extend(
        [
            "",
            "## Required Next Step",
            "",
            "Run a telemetry-only pass over the surviving primitives or recover call "
            "telemetry before making RQ8 dollar, runtime, or token-efficiency claims.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _row_missing_fields(row: Mapping[str, Any]) -> list[str]:
    return [
        field
        for field in REQUIRED_TELEMETRY_FIELDS
        if row.get(field) is None or row.get(field) == ""
    ]


def _claim_boundary(*, complete_rows: int, row_count: int) -> str:
    if row_count and complete_rows == row_count:
        return (
            "RQ8 cost, latency, and token-efficiency claims are authorized for this "
            "matrix, subject to the saved-artifact and split-discipline boundaries."
        )
    return (
        "RQ8 cost, latency, and token-efficiency claims are blocked: the operational "
        "matrix is missing required telemetry fields. Reliability and complexity "
        "claims may still be stated with their saved-artifact boundary."
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-json-path", type=Path, default=DEFAULT_MATRIX_JSON_PATH)
    parser.add_argument("--guard-json-path", type=Path, default=DEFAULT_GUARD_JSON_PATH)
    parser.add_argument("--guard-report-path", type=Path, default=DEFAULT_GUARD_REPORT_PATH)
    args = parser.parse_args(argv)

    matrix = json.loads(args.matrix_json_path.read_text(encoding="utf-8"))
    metadata = {
        **build_rq8_telemetry_guard(matrix),
        "source_matrix": str(args.matrix_json_path),
    }
    write_guard_json(metadata, args.guard_json_path)
    write_guard_report(metadata, args.guard_report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
