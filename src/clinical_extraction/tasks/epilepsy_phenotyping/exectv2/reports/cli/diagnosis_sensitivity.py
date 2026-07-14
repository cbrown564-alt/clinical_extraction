"""Build reviewed ExECTv2 Diagnosis sensitivity views without changing scoring."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_sensitivity import build_sensitivity_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_resolution_ledger_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--audit-summary-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.json"),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_sensitivity_dev140_20260714.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_sensitivity_report(
        ledger_jsonl=args.ledger_jsonl,
        audit_summary_json=args.audit_summary_json,
        out_json=args.out_json,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
