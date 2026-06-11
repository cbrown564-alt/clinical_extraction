"""CLI runner for the ExECTv2 hybrid (candidate + assessment) SF extractor.

Usage examples::

    # Pilot 25 letters, prompt-only smoke test (no LLM calls)
    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_hybrid_sf \\
        --mode prompt-only --pilot 25

    # Full dev split, live
    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_hybrid_sf \\
        --model openai/gpt-4.1-mini --mode live --temperature 0.0 --max-tokens 2400 \\
        --out-jsonl experiments/exectv2_hybrid_dev_gpt41mini_2026-06-11.jsonl \\
        --out-report experiments/exectv2_hybrid_dev_gpt41mini_2026-06-11.md

For long runs use the detached Start-Process pattern (Phase 7 risk register) to
survive the harness ~9-minute background kill.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.clinical_assessment import (
    run_split,
    write_jsonl,
    write_report,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ExECTv2 hybrid SF runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--split", default="dev", help="Data split (dev only for development).")
    p.add_argument("--model", default="openai/gpt-4.1-mini", help="DSPy model string.")
    p.add_argument(
        "--mode",
        choices=["live", "prompt-only"],
        default="prompt-only",
        help="'live' makes real LLM calls; 'prompt-only' builds prompts only.",
    )
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=2400)
    p.add_argument("--no-dspy-cache", action="store_true", help="Disable DSPy response caching.")
    p.add_argument("--api-base", default=None, help="Optional OpenAI-compatible API base URL.")
    p.add_argument("--pilot", type=int, default=None, help="Restrict to the first N letters.")
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing --out-jsonl checkpoint, skipping done letters.",
    )
    p.add_argument("--progress-every", type=int, default=25, help="Checkpoint every N letters.")
    p.add_argument("--out-jsonl", type=Path, default=None, help="Output JSONL path.")
    p.add_argument("--out-report", type=Path, default=None, help="Output Markdown report path.")
    return p


def _auto_path(split: str, model: str, n: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = f"exectv2_hybrid_{split}{n_str}_{model_slug}_{today}"
    return Path("experiments") / f"{name}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()

    if args.split == "test":
        print(
            "ERROR: test split is a locked holdout — only dev is permitted for "
            "development runs. Use --split dev.",
            file=sys.stderr,
        )
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]

    n = len(letters)
    print(f"Loaded {n} letters from split '{args.split}'.", flush=True)

    jsonl_path = args.out_jsonl or _auto_path(args.split, args.model, n, "jsonl")
    report_path = args.out_report or _auto_path(args.split, args.model, n, "md")

    print(
        f"Running hybrid / mode={args.mode} / model={args.model} over {n} letters ...",
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
    scores = summary.get("scores", {})

    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Letters: {summary.get('examples', 0)}", flush=True)
    print(f"Call failures: {summary.get('call_failures', 0)}", flush=True)
    print(f"Parse failures: {summary.get('parse_failures', 0)}", flush=True)
    print(
        f"Candidates: {summary.get('n_candidates', 0)}  "
        f"Kept: {summary.get('n_mentions_raw', 0)}  "
        f"Scored: {summary.get('n_mentions_scored', 0)}  "
        f"Routed: {summary.get('n_routed', 0)}",
        flush=True,
    )
    print(f"Routed taxonomy: {summary.get('routed_taxonomy', {})}", flush=True)

    for config_name in ("phrase_only", "sf_semantic", "sf_benchmark"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
        print(
            f"\n{config_name}:\n"
            f"  per-item: P={pi.get('precision', 0):.3f} "
            f"R={pi.get('recall', 0):.3f} F1={pi.get('f1', 0):.3f}\n"
            f"  per-letter: P={pl.get('precision', 0):.3f} "
            f"R={pl.get('recall', 0):.3f} F1={pl.get('f1', 0):.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
