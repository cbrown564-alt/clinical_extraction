"""CLI runner for attribution-clean Qwen key-entity generation-selection."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_generation_selection as route,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ExECTv2 Qwen LLM-only generation-selection key-entity runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--split",
        default="dev",
        help="Data split to run. Only dev is permitted for development runs.",
    )
    parser.add_argument("--model", default="ollama_chat/qwen3.6:35b", help="DSPy model string.")
    parser.add_argument(
        "--mode",
        choices=["live", "prompt-only"],
        default="prompt-only",
        help="'live' makes real LLM calls; 'prompt-only' emits prompts only.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=5000)
    parser.add_argument(
        "--no-dspy-cache",
        action="store_true",
        help="Disable DSPy response caching.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Optional API base URL for local/native model routing.",
    )
    parser.add_argument(
        "--ollama-num-ctx",
        type=int,
        default=None,
        help="Set CLINICAL_EXTRACTION_OLLAMA_NUM_CTX for native ollama_chat runs.",
    )
    parser.add_argument(
        "--prompt-profile",
        choices=["compact", "full_examples"],
        default="compact",
        help="Prompt payload profile. compact limits in-context examples for local Qwen.",
    )
    parser.add_argument(
        "--call-strategy",
        choices=[
            "single_call_dedup_facts",
            "single_call_inventory",
            "single_call_mentions",
            "single_call_per_entity_mentions",
            "single_call_typed_mentions",
            "single_call_mention_ids",
            "single_call_render_ids",
            "single_call_clean_render_ids",
            "single_call_per_entity_clean_render_ids",
            "qwen_pool_adjudication",
            "qwen_pool_entity_adjudication",
            "qwen_pool_group_adjudication",
            "two_stage",
        ],
        default="single_call_mentions",
        help="Model-owned generation/selection strategy to evaluate.",
    )
    parser.add_argument(
        "--pool-jsonl",
        action="append",
        type=Path,
        default=[],
        help=(
            "Prior attribution-clean llm_only JSONL artifact to use as a "
            "Qwen-generated mention pool. Repeat for multiple sources."
        ),
    )
    parser.add_argument(
        "--pool-mentions-only",
        action="store_true",
        help="Use only saved structured mention surfaces, excluding event-flattened surfaces.",
    )
    parser.add_argument("--pilot", type=int, default=None, help="Restrict to the first N letters.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing --out-jsonl checkpoint, skipping done letters.",
    )
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(
    split: str,
    model: str,
    n: int,
    suffix: str,
    *,
    prompt_profile: str,
    call_strategy: str,
) -> Path:
    model_slug = re.sub(r"[^A-Za-z0-9]+", "", model.split("/")[-1])
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = (
        "exectv2_llm_only_key_entities_generation_selection_"
        f"{call_strategy}_{prompt_profile}_{split}{n_str}_{model_slug}_{today}"
    )
    return Path("experiments") / f"{name}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        print(
            "ERROR: test split is a locked holdout; only dev is permitted for development runs.",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.ollama_num_ctx is not None:
        os.environ["CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"] = str(args.ollama_num_ctx)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]
    pool_mentions_by_letter = (
        route.load_model_generated_mention_pool(
            args.pool_jsonl,
            include_event_surfaces=not args.pool_mentions_only,
        )
        if args.pool_jsonl
        else None
    )

    n = len(letters)
    jsonl_path = args.out_jsonl or _auto_path(
        args.split,
        args.model,
        n,
        "jsonl",
        prompt_profile=args.prompt_profile,
        call_strategy=args.call_strategy,
    )
    report_path = args.out_report or _auto_path(
        args.split,
        args.model,
        n,
        "md",
        prompt_profile=args.prompt_profile,
        call_strategy=args.call_strategy,
    )

    print(
        "Running llm_only_key_entities_generation_selection / "
        f"mode={args.mode} / model={args.model} / "
        f"prompt_profile={args.prompt_profile} / "
        f"call_strategy={args.call_strategy} over {n} letters from split "
        f"'{args.split}' ...",
        flush=True,
    )
    if (
        args.call_strategy
        in {
            "qwen_pool_adjudication",
            "qwen_pool_entity_adjudication",
            "qwen_pool_group_adjudication",
        }
        and not pool_mentions_by_letter
    ):
        print(
            f"WARNING: {args.call_strategy} was requested without --pool-jsonl; "
            "the model will receive empty mention pools.",
            file=sys.stderr,
            flush=True,
        )

    rows, metadata = route.run_split(
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
        prompt_profile=args.prompt_profile,
        call_strategy=args.call_strategy,
        pool_mentions_by_letter=pool_mentions_by_letter,
    )

    write_jsonl(rows, jsonl_path)
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    summary = metadata.get("summary", {})
    canonical = (
        summary.get("protocol_surfaces", {})
        .get("model_preserving_canonical", {})
    )
    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Letters: {summary.get('examples', 0)}", flush=True)
    print(f"Generation call failures: {summary.get('generation_call_failures', 0)}", flush=True)
    print(f"Selection call failures: {summary.get('selection_call_failures', 0)}", flush=True)
    print(
        f"Model-preserving canonical F1: {canonical.get('f1', 0):.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
