"""CLI for the ExECTv2 Diagnosis interpretation audit substrate."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_interpretation_audit import build_audit_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--out-summary",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_audit_artifacts(out_jsonl=args.out_jsonl, out_summary=args.out_summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

