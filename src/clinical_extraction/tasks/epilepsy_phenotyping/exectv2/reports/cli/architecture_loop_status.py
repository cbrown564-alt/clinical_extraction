"""CLI entry point for the ExECTv2 architecture-loop status report."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.architecture_loop_status import (
    DEFAULT_REGISTRY_PATH,
    MODEL,
    write_status_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the GPT-first ExECTv2 architecture-loop status report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/exectv2_gpt_first_architecture_loop_status_20260617.md"),
    )
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--split", default="dev")
    args = parser.parse_args()

    path = write_status_report(
        args.out,
        registry_path=args.registry,
        model=args.model,
        split=args.split,
    )
    print(f"Wrote {path}")


if __name__ == "__main__":
    raise SystemExit(main())
