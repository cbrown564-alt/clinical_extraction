"""CLI runner for ExECTv2 Investigations verifier arbitration."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_arbitration as arbitration,
)

DEFAULT_VERIFIER_JSONL = Path(
    "experiments/exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay deterministic pending-test arbitration over the saved "
            "GPT-4.1-mini Investigations verifier."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--verifier-jsonl", type=Path, default=DEFAULT_VERIFIER_JSONL)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(suffix: str) -> Path:
    today = date.today().isoformat().replace("-", "")
    return (
        Path("experiments") / f"exectv2_llm_investigations_arbitration_v02_dev140_{today}.{suffix}"
    )


def main() -> None:
    args = _build_parser().parse_args()
    if not args.verifier_jsonl.exists():
        print(f"ERROR: input JSONL does not exist: {args.verifier_jsonl}", file=sys.stderr)
        sys.exit(1)
    rows = arbitration.read_rows(args.verifier_jsonl)
    jsonl_path = args.out_jsonl or _auto_path("jsonl")
    report_path = args.out_report or _auto_path("md")
    metadata = arbitration.write_rows_and_report(
        rows,
        jsonl_path=jsonl_path,
        report_path=report_path,
    )
    clinical = (
        metadata.get("summary", {})
        .get("clinical_recovery", {})
        .get(
            "investigations",
            {},
        )
    )
    print(f"Done. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(
        "Investigations clinical headline: "
        f"P={clinical.get('precision', 0):.3f} "
        f"R={clinical.get('recall', 0):.3f} "
        f"F1={clinical.get('f1', 0):.3f} "
        f"TP={clinical.get('tp', 0)} "
        f"FP={clinical.get('fp', 0)} "
        f"FN={clinical.get('fn', 0)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
