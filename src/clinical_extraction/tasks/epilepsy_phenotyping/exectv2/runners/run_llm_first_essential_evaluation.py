"""Driver for the LLM-first essential clinical evaluation (plan satellite 11).

Replays the rules_only, llm_first, and hybrid architectures over one canonical
``dev`` gold under the ownership-aware layer ladder, and emits the plan's six
required reports as one durable readout plus a machine-readable JSON.

Analysis-only: ``rules_only`` is generated deterministically; ``llm_first`` and
``hybrid`` are read from existing saved prediction artifacts. No model calls.

Run as a module (no arguments needed):
``...exectv2.runners.run_llm_first_essential_evaluation``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_readout import (
    build_evaluation,
    llm_first_error_ledger_rows,
    render_markdown,
    write_error_ledger_csv,
    write_error_ledger_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev")
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_llm_first_essential_evaluation_dev140_20260618.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path(
            "docs/experiments/exectv2/key_entities/"
            "exectv2_llm_first_essential_evaluation_2026-06-18.md"
        ),
    )
    parser.add_argument(
        "--out-error-ledger-csv",
        type=Path,
        default=Path(
            "experiments/"
            "exectv2_llm_first_essential_family_error_ledger_dev140_20260618.csv"
        ),
    )
    parser.add_argument(
        "--out-error-ledger-md",
        type=Path,
        default=Path(
            "docs/experiments/exectv2/key_entities/"
            "exectv2_llm_first_essential_family_error_ledger_2026-06-18.md"
        ),
    )
    args = parser.parse_args()

    report = build_evaluation(split=args.split)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out_md.write_text(render_markdown(report), encoding="utf-8")
    ledger_rows = llm_first_error_ledger_rows(report)
    write_error_ledger_csv(ledger_rows, args.out_error_ledger_csv)
    write_error_ledger_markdown(ledger_rows, args.out_error_ledger_md)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    print(f"Wrote {args.out_error_ledger_csv}")
    print(f"Wrote {args.out_error_ledger_md}")


if __name__ == "__main__":
    main()
