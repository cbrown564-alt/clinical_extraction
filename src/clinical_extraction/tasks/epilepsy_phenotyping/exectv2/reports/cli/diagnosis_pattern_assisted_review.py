"""Build a conservative pattern-assisted ExECTv2 Diagnosis review overlay."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_pattern_assisted_review import build_pattern_assisted_review


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl"),
    )
    parser.add_argument("--manual-overlay-json", type=Path, required=True)
    parser.add_argument(
        "--out-overlay-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_pattern_assisted_overlay_20260714.json"),
    )
    parser.add_argument(
        "--out-summary-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_pattern_assisted_summary_20260714.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_pattern_assisted_review(
        audit_jsonl=args.audit_jsonl,
        manual_overlay_json=args.manual_overlay_json,
        out_overlay_json=args.out_overlay_json,
        out_summary_json=args.out_summary_json,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
