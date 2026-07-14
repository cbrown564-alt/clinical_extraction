"""CLI entry point for the ExECTv2 deterministic all-9 scorecard."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..deterministic_all9_scorecard import (
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RUN_INDEX_PATH,
    write_scorecard_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 deterministic all-9 scorecard",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_deterministic_all9_dev_20260617.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/exectv2_deterministic_all9_dev_20260617.md"),
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    parser.add_argument("--no-register", action="store_true")
    args = parser.parse_args()

    json_path, md_path = write_scorecard_artifacts(
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
        registry_path=None if args.no_register else args.registry,
        run_index_path=args.run_index,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
