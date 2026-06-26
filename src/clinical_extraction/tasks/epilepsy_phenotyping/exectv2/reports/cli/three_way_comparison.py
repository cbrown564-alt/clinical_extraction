"""CLI entry point for the ExECTv2 three-way (rules/llm_only/hybrid) SF comparison report."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.three_way_comparison import (
    DEFAULT_REGISTRY_PATH,
    write_comparison_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ExECTv2 three-way (rules/llm_only/hybrid) SF comparison report",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--split", default="dev")
    parser.add_argument(
        "--registry", default=str(DEFAULT_REGISTRY_PATH), help="registry.jsonl path"
    )
    parser.add_argument(
        "--out", required=True, help="output Markdown path for the comparison report"
    )
    args = parser.parse_args()

    path = write_comparison_report(
        args.model,
        Path(args.out),
        registry_path=Path(args.registry),
        split=args.split,
    )
    print(f"Wrote {path}")


if __name__ == "__main__":
    raise SystemExit(main())
