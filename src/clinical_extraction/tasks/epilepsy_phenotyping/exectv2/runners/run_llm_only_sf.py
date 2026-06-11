"""CLI runner for ExECTv2 LLM-only SeizureFrequency extractors.

Usage examples::

    # Pilot 25 letters with single-pass config, prompt-only mode (smoke test)
    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_sf \\
        --config single_pass \\
        --model openai/gpt-4.1-mini \\
        --mode prompt-only \\
        --pilot 25

    # Full dev split, live
    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_llm_only_sf \\
        --config single_pass \\
        --model openai/gpt-4.1-mini \\
        --mode live \\
        --temperature 0.0 \\
        --max-tokens 2400 \\
        --out-jsonl experiments/exectv2_llm_only_sp_dev_gpt41mini_2026-06-10.jsonl \\
        --out-report experiments/exectv2_llm_only_sp_dev_gpt41mini_2026-06-10.md

For long runs use the detached Start-Process pattern documented in the
Phase 7 risk register to survive the harness ~9-minute background kill.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ExECTv2 LLM-only SF runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--config",
        choices=["single_pass", "per_entity"],
        default="single_pass",
        help="LLM-only extractor configuration.",
    )
    p.add_argument(
        "--split",
        default="dev",
        help="Data split to run (dev or test). Only dev is permitted for development.",
    )
    p.add_argument("--model", default="openai/gpt-4.1-mini", help="DSPy model string.")
    p.add_argument(
        "--mode",
        choices=["live", "prompt-only"],
        default="prompt-only",
        help="'live' makes real LLM calls; 'prompt-only' emits prompts only.",
    )
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=2400)
    p.add_argument(
        "--no-dspy-cache",
        action="store_true",
        help="Disable DSPy response caching.",
    )
    p.add_argument(
        "--api-base",
        default=None,
        help="Optional OpenAI-compatible API base URL.",
    )
    p.add_argument(
        "--pilot",
        type=int,
        default=None,
        help="Restrict to the first N letters (pilot run).",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing --out-jsonl checkpoint, skipping done letters.",
    )
    p.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Emit a checkpoint every N letters.",
    )
    p.add_argument(
        "--out-jsonl",
        type=Path,
        default=None,
        help="Output JSONL path. Auto-generated if omitted.",
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=None,
        help="Output Markdown report path. Auto-generated if omitted.",
    )
    return p


def _auto_path(config: str, split: str, model: str, n: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = f"exectv2_llm_only_{config}_{split}{n_str}_{model_slug}_{today}"
    return Path("experiments") / f"{name}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()

    if args.split == "test":
        print(
            "ERROR: test split is a locked holdout — only dev is permitted "
            "for development runs. Use --split dev.",
            file=sys.stderr,
        )
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]

    n = len(letters)
    print(f"Loaded {n} letters from split '{args.split}'.", flush=True)

    jsonl_path = args.out_jsonl or _auto_path(args.config, args.split, args.model, n, "jsonl")
    report_path = args.out_report or _auto_path(args.config, args.split, args.model, n, "md")

    if args.config == "single_pass":
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
            run_split,
            write_jsonl,
            write_report,
        )
    else:
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_per_entity import (
            run_split,
            write_jsonl,
            write_report,
        )

    print(
        f"Running {args.config} / mode={args.mode} / model={args.model} "
        f"over {n} letters ...",
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
        f"Mentions scored: {summary.get('n_mentions_scored', 0)} / "
        f"{summary.get('n_mentions_raw', 0)}",
        flush=True,
    )

    for config_name in ("phrase_only", "sf_semantic", "sf_benchmark"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
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
