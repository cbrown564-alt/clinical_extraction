"""Run the ADR 0030 target-indicators single-call ExECTv2 extractor."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    run_split,
    write_jsonl,
    write_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--pilot", type=int, default=None)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="prompt-only")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--no-dspy-cache", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    args = parser.parse_args()

    if args.split == "test":
        print("ERROR: test split is locked for development.", file=sys.stderr)
        raise SystemExit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot is not None:
        letters = letters[: args.pilot]
    model_slug = args.model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n = len(letters)
    base = f"exectv2_target_indicators_single_call_{args.split}{n}_{model_slug}_{today}"
    jsonl_path = args.out_jsonl or Path("experiments") / f"{base}.jsonl"
    report_path = args.out_report or Path("experiments") / f"{base}.md"

    rows, metadata = run_split(
        letters,
        split=args.split,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=args.resume,
    )
    write_jsonl(rows, jsonl_path)
    write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    summary = metadata["summary"]
    candidate = summary["target_report"]["candidates"][0]
    print(f"Done. JSONL: {jsonl_path}  Report: {report_path}")
    print(f"Target overall F1: {candidate['overall_target_score']['f1']:.4f}")
    for indicator, score in candidate["headline_scores"].items():
        print(
            f"{indicator}: F1={score['f1']:.4f} "
            f"P={score['precision']:.4f} R={score['recall']:.4f}"
        )


if __name__ == "__main__":
    main()

