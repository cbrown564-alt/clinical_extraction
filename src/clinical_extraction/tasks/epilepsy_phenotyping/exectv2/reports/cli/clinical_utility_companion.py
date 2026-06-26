"""CLI entry point for the ExECTv2 clinical-utility companion report."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_utility_companion import (
    RunSpec,
    write_companion_artifacts,
)


def _parse_run_arg(value: str) -> RunSpec:
    parts = value.split("=", 1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("--run must be id=report.json,rows.jsonl")
    run_id, paths = parts
    path_parts = paths.split(",", 1)
    if len(path_parts) != 2:
        raise argparse.ArgumentTypeError("--run must be id=report.json,rows.jsonl")
    return RunSpec(run_id=run_id, report_json=Path(path_parts[0]), rows_jsonl=Path(path_parts[1]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write an ExECTv2 clinical-utility companion report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--run", action="append", type=_parse_run_arg, default=[])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.md"),
    )
    args = parser.parse_args()
    json_path, md_path = write_companion_artifacts(
        out_json=args.out_json,
        out_md=args.out_md,
        run_specs=args.run or None,
        split=args.split,
        sample_limit=args.sample_limit,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    raise SystemExit(main())
