"""CLI runner for ExECTv2 LLM-only all-entity extraction.

Usage examples::

    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_all
        --mode prompt-only --pilot 25

    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_all
        --mode live --model openai/gpt-4.1-mini --max-tokens 4000 --resume
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    run_split,
    write_jsonl,
    write_report,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ExECTv2 LLM-only all-entity runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--split",
        default="dev",
        help="Data split to run. Only dev is permitted for development runs.",
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini", help="DSPy model string.")
    parser.add_argument(
        "--mode",
        choices=["live", "prompt-only"],
        default="prompt-only",
        help="'live' makes real LLM calls; 'prompt-only' emits prompts only.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument(
        "--no-dspy-cache",
        action="store_true",
        help="Disable DSPy response caching.",
    )
    parser.add_argument("--api-base", default=None, help="Optional OpenAI-compatible API base URL.")
    parser.add_argument("--pilot", type=int, default=None, help="Restrict to the first N letters.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing --out-jsonl checkpoint, skipping done letters.",
    )
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(split: str, model: str, n: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = f"exectv2_llm_only_all_entities_{split}{n_str}_{model_slug}_{today}"
    return Path("experiments") / f"{name}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()

    if args.split == "test":
        print(
            "ERROR: test split is a locked holdout — only dev is permitted for development runs.",
            file=sys.stderr,
        )
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]

    n = len(letters)
    jsonl_path = args.out_jsonl or _auto_path(args.split, args.model, n, "jsonl")
    report_path = args.out_report or _auto_path(args.split, args.model, n, "md")

    print(
        f"Running llm_only_all_entities / mode={args.mode} / model={args.model} "
        f"over {n} letters from split '{args.split}' ...",
        flush=True,
    )

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

    summary = metadata.get("summary", {})
    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Letters: {summary.get('examples', 0)}", flush=True)
    print(f"Call failures: {summary.get('call_failures', 0)}", flush=True)
    print(f"Parse failures: {summary.get('parse_failures', 0)}", flush=True)
    print(
        f"Mentions scored: {summary.get('n_mentions_scored', 0)} / "
        f"{summary.get('n_mentions_raw', 0)}",
        flush=True,
    )
    for config_name in ("semantic", "benchmark", "phrase_only"):
        scores = summary.get("scores", {}).get(config_name, {})
        pi = scores.get("per_item", {})
        pl = scores.get("per_letter", {})
        print(
            f"\n{config_name}:\n"
            f"  per-item: P={pi.get('precision', 0):.3f} "
            f"R={pi.get('recall', 0):.3f} "
            f"F1={pi.get('f1', 0):.3f}\n"
            f"  per-letter: P={pl.get('precision', 0):.3f} "
            f"R={pl.get('recall', 0):.3f} "
            f"F1={pl.get('f1', 0):.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
