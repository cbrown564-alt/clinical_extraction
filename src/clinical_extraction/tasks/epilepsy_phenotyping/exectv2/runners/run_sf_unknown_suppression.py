"""CLI runner for ExECTv2 SF deterministic unknown suppression."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as suppression,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay SF unknown suppression over saved v0.6 projection JSONL.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(input_jsonl: Path, suffix: str) -> Path:
    today = date.today().isoformat().replace("-", "")
    stem = input_jsonl.stem.replace(
        "state_projection_v06_combined",
        "unknown_suppression_v07",
    )
    return Path("experiments") / f"{stem}_{today}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()
    if not args.input_jsonl.exists():
        print(f"ERROR: input JSONL does not exist: {args.input_jsonl}", file=sys.stderr)
        sys.exit(1)
    rows = suppression.read_rows(args.input_jsonl)
    jsonl_path = args.out_jsonl or _auto_path(args.input_jsonl, "jsonl")
    report_path = args.out_report or _auto_path(args.input_jsonl, "md")
    metadata = suppression.write_rows_and_report(
        rows,
        jsonl_path=jsonl_path,
        report_path=report_path,
    )
    clinical = metadata.get("summary", {}).get("clinical_recovery", {}).get(
        "seizure_frequency",
        {},
    )
    gate = metadata.get("gate", {})
    print(f"Done. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(
        "SeizureFrequency clinical headline: "
        f"P={clinical.get('precision', 0):.3f} "
        f"R={clinical.get('recall', 0):.3f} "
        f"F1={clinical.get('f1', 0):.3f} "
        f"promote={gate.get('promote')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
