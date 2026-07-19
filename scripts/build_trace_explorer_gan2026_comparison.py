"""Build the Gan pipeline selector from retained aggregate evidence."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.trace_explorer.gan2026_comparison import (
    write_gan2026_pipeline_families,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--scorecard",
        type=Path,
        default=Path("experiments/shared_reliability_scorecard_20260718.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("frontend/frontend/public/mock-data/pipeline-families.json"),
    )
    args = parser.parse_args(argv)
    scorecard = (
        args.scorecard if args.scorecard.is_absolute() else args.repo_root / args.scorecard
    )
    output = args.output if args.output.is_absolute() else args.repo_root / args.output
    written = write_gan2026_pipeline_families(scorecard, output)
    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
