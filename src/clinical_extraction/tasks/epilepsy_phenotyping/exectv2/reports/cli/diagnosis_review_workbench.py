"""CLI for the self-contained ExECTv2 Diagnosis review workbench."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_review_workbench import build_review_workbench


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.json"),
    )
    parser.add_argument(
        "--out-html",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_interpretation_review_workbench_20260714.html"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_review_workbench(
        audit_jsonl=args.audit_jsonl,
        summary_json=args.summary_json,
        out_html=args.out_html,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

