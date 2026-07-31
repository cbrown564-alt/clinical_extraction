"""Build the ExECTv2 architecture matrix consumed by the local explorer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.trace_explorer.exectv2_comparison import (
    write_exectv2_comparison,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("frontend/public/mock-data/exectv2/runs.json"),
    )
    args = parser.parse_args(argv)
    output = args.output
    if not output.is_absolute():
        output = args.repo_root / output
    written = write_exectv2_comparison(args.repo_root, output)
    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
