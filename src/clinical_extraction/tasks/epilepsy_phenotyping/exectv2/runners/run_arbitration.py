"""CLI runner for the ExECTv2 Stage-2 GPT arbitration pass (satellite 09).

Reads the nine focused per-entity GPT candidates as a recall pool and runs one
arbitration call per letter that re-types, merges, de-duplicates, and selects the
canonical mention set. Replay-first for the candidate pool; only the per-letter
arbitration call is live. Resumable.

Usage::

    uv run python -m \\
      clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_arbitration \\
      --candidate-prefix exectv2_llm_only_per_entity_dev140_gpt41mini_20260617 \\
      --model openai/gpt-4.1-mini --temperature 0.0 --resume

    # Dry run the assembled prompt without any LLM call
    uv run python -m ... run_arbitration --candidate-prefix <prefix> --mode prompt-only
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import arbitration


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ExECTv2 Stage-2 arbitration runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--split", default="dev")
    p.add_argument("--mode", choices=["live", "prompt-only"], default="live")
    p.add_argument("--model", default="openai/gpt-4.1-mini")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=6000)
    p.add_argument("--no-dspy-cache", action="store_true")
    p.add_argument("--api-base", default=None)
    p.add_argument("--pilot", type=int, default=None)
    p.add_argument(
        "--candidate-prefix",
        required=True,
        help="Per-entity candidate artifact prefix to use as the recall pool.",
    )
    p.add_argument("--candidate-dir", type=Path, default=Path("experiments"))
    p.add_argument("--out-dir", type=Path, default=Path("experiments"))
    p.add_argument("--out-prefix", default=None)
    p.add_argument("--progress-every", type=int, default=10)
    p.add_argument("--resume", action="store_true")
    return p


def _auto_prefix(split: str, model: str, n: int) -> str:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    return f"exectv2_arbitration_{split}{n_str}_{model_slug}_{today}"


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        print("ERROR: test split is a locked holdout — use --split dev.", file=sys.stderr)
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]
    n = len(letters)
    print(f"Loaded {n} letters from split '{args.split}'.", flush=True)

    pool = arbitration.load_candidate_pool(args.candidate_prefix, out_dir=args.candidate_dir)
    print(
        f"Loaded candidate pool for {len(pool)} letters "
        f"({sum(len(v) for v in pool.values())} raw candidates).",
        flush=True,
    )

    out_prefix = args.out_prefix or _auto_prefix(args.split, args.model, n)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / f"{out_prefix}.jsonl"
    report_path = args.out_dir / f"{out_prefix}.md"

    rows, metadata = arbitration.run_arbitration(
        letters,
        pool,
        split=args.split,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=jsonl_path,
        resume=args.resume,
    )

    arbitration.write_jsonl(rows, jsonl_path)
    # Reuse the all-entity hybrid report writer (same row + summary shape).
    hybrid.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    diag = metadata.get("arbitration_diagnostics", {})
    summary = metadata.get("summary", {})
    scores = summary.get("scores", {})
    print(f"\nWrote: {report_path}", flush=True)
    print(
        f"call_failures={diag.get('call_failures', 0)} "
        f"parse_failures={diag.get('parse_failures', 0)} "
        f"raw={diag.get('n_mentions_raw', 0)} scored={diag.get('n_mentions_scored', 0)} "
        f"drops={diag.get('drops', {})}",
        flush=True,
    )
    for config_name in ("semantic", "benchmark", "phrase_only"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
        print(
            f"  {config_name:<11} item F1={pi.get('f1', 0):.3f} "
            f"(P={pi.get('precision', 0):.3f} R={pi.get('recall', 0):.3f})  "
            f"letter F1={pl.get('f1', 0):.3f}",
            flush=True,
        )
    per_entity = scores.get("semantic", {}).get("per_entity", {})
    print("  per-entity semantic item F1:", flush=True)
    for entity in hybrid.ENTITY_NAMES:
        f1 = per_entity.get(entity, {}).get("per_item", {}).get("f1", 0)
        print(f"    {entity:<18} {f1:.3f}", flush=True)


if __name__ == "__main__":
    main()
