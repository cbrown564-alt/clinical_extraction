"""CLI entry point for the ExECTv2 clinical-recovery error ledger."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.clinical_recovery_error_ledger import (
    write_error_ledger_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write an ExECTv2 clinical-recovery error ledger for key entities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--structured-jsonl", type=Path, required=True)
    parser.add_argument("--diagnosis-jsonl", type=Path, default=None)
    parser.add_argument("--sf-jsonl", type=Path, default=None)
    parser.add_argument("--investigations-jsonl", type=Path, default=None)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_key_entities_clinical_error_ledger.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/exectv2_key_entities_clinical_error_ledger.md"),
    )
    args = parser.parse_args()
    json_path, md_path = write_error_ledger_artifacts(
        structured_jsonl=args.structured_jsonl,
        diagnosis_jsonl=args.diagnosis_jsonl,
        sf_jsonl=args.sf_jsonl,
        investigations_jsonl=args.investigations_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    raise SystemExit(main())
