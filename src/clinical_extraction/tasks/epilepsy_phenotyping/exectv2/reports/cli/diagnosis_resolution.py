"""Freeze a completed ExECTv2 Diagnosis review into a mechanism ledger."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_resolution import build_review_ledger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl"),
    )
    parser.add_argument("--completed-overlay-json", type=Path, required=True)
    parser.add_argument(
        "--out-frozen-overlay-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_review_completed_dev140_20260714.json"),
    )
    parser.add_argument(
        "--out-ledger-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_resolution_ledger_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--out-summary-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_resolution_summary_dev140_20260714.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_review_ledger(
        audit_jsonl=args.audit_jsonl,
        completed_overlay_json=args.completed_overlay_json,
        out_frozen_overlay_json=args.out_frozen_overlay_json,
        out_ledger_jsonl=args.out_ledger_jsonl,
        out_summary_json=args.out_summary_json,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
