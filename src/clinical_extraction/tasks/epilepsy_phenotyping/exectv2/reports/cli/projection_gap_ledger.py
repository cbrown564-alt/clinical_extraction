"""CLI entry point for the ExECTv2 all-entity projection-gap ledger."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.projection_gap_ledger import (
    write_projection_gap_ledger_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 all-entity projection-gap ledger",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_projection_gap_ledger_dev.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/exectv2_projection_gap_ledger_dev.md"),
    )
    args = parser.parse_args()

    json_path, md_path = write_projection_gap_ledger_artifacts(
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    raise SystemExit(main())
