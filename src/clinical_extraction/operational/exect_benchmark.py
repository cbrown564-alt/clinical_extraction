"""Run a canonical ExECT method over an allowed development split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.core.jsonl import write_jsonl_rows
from clinical_extraction.operational.benchmark_arguments import add_llm_run_args, guard_test_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli_specs import get_cli_specs
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    specs = get_cli_specs()
    parser.add_argument("--method", choices=sorted(specs), default="rules")
    add_llm_run_args(parser)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--out-jsonl", type=Path, required=True)
    parser.add_argument("--out-report", type=Path, required=True)
    args = parser.parse_args(argv)
    guard_test_split(args.split)

    letters = load_letters_for_split(args.split)
    if args.pilot is not None:
        letters = letters[: args.pilot]
    rows, metadata = specs[args.method].run_split(
        letters,
        split=args.split,
        model="(model-independent)" if args.method == "rules" else args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        api_key=args.api_key,
        timeout=args.timeout,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=args.out_jsonl,
        checkpoint_report_path=args.out_report,
        resume=args.resume,
    )
    write_jsonl_rows(rows, args.out_jsonl)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
