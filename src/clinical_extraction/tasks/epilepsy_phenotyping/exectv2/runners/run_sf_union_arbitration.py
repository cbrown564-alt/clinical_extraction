"""CLI runner for ExECTv2 SeizureFrequency union arbitration."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as arbitration,
)

DEFAULT_CURRENT_JSONL = Path(
    "experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay deterministic union arbitration over the saved GPT SF lane "
            "and deterministic all-entity SF extractor."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--current-jsonl", type=Path, default=DEFAULT_CURRENT_JSONL)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--row-count", type=int, default=140)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(suffix: str) -> Path:
    today = date.today().isoformat().replace("-", "")
    return Path("experiments") / f"exectv2_hybrid_sf_union_arbitration_v08_dev140_{today}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()
    if not args.current_jsonl.exists():
        print(f"ERROR: input JSONL does not exist: {args.current_jsonl}", file=sys.stderr)
        sys.exit(1)
    letters = load_letters_for_split(args.split)[: args.row_count]
    current_rows = arbitration.read_rows(args.current_jsonl)
    deterministic_rows = arbitration.deterministic_rows_from_letters(
        letters,
        split=args.split,
    )
    jsonl_path = args.out_jsonl or _auto_path("jsonl")
    report_path = args.out_report or _auto_path("md")
    metadata = arbitration.write_rows_and_report(
        current_rows,
        deterministic_rows,
        jsonl_path=jsonl_path,
        report_path=report_path,
    )
    clinical = (
        metadata.get("summary", {})
        .get("clinical_recovery", {})
        .get(
            "seizure_frequency",
            {},
        )
    )
    print(f"Done. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(
        "SeizureFrequency clinical headline: "
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
