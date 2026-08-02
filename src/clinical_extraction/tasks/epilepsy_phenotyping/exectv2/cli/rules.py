"""Run the ExECT rules method over an allowed development split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import guard_test_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--pilot", type=int, default=None)
    parser.add_argument("--out-jsonl", type=Path, required=True)
    parser.add_argument("--out-report", type=Path, required=True)
    args = parser.parse_args(argv)
    guard_test_split(args.split)

    letters = load_letters_for_split(args.split)
    if args.pilot is not None:
        letters = letters[: args.pilot]
    rows, metadata = run_split(letters, method="rules", split=args.split)
    write_jsonl_rows(rows, args.out_jsonl)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
