"""CLI runner for the ExECTv2 all-entity hybrid (satellite 09, Phase C).

Assembles the nine focused per-entity GPT passes into one combined prediction,
applies the deterministic gate + CUI projection, and scores overall + per entity
against the published cells. The LLM is the candidate source for every entity;
the deterministic layer only routes, projects, normalizes, and scores.

Two modes:

* ``--mode replay`` (default): read the focused per-entity GPT candidates from
  existing ``llm_only_per_entity`` JSONL artifacts (zero extra LLM calls). Point
  ``--candidate-prefix`` at the per-entity run prefix.
* ``--mode live``: regenerate the per-entity candidates first (one focused call
  per entity per letter, resumable per entity) and then assemble.

Usage::

    # Replay the dev140 Phase B per-entity candidates into the combined headline
    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_hybrid_all_entities \\
        --mode replay \\
        --candidate-prefix exectv2_llm_only_per_entity_dev140_gpt41mini_20260617

    # Same, with deterministic rule augmentation of the candidate set
    uv run python -m ... run_hybrid_all_entities --mode replay \\
        --candidate-prefix <prefix> --augment-rules

    # Live: regenerate candidates on gpt-4.1-mini, then assemble (resumable)
    uv run python -m ... run_hybrid_all_entities --mode live \\
        --model openai/gpt-4.1-mini --temperature 0.0
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_per_entity as per_entity,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ExECTv2 all-entity hybrid runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--split", default="dev", help="Data split (dev only for development).")
    p.add_argument(
        "--mode",
        choices=["replay", "live"],
        default="replay",
        help="'replay' reads existing per-entity candidates; 'live' regenerates them.",
    )
    p.add_argument("--model", default="openai/gpt-4.1-mini", help="Candidate-source model.")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=2400)
    p.add_argument("--no-dspy-cache", action="store_true")
    p.add_argument("--api-base", default=None)
    p.add_argument("--pilot", type=int, default=None, help="Restrict to the first N letters.")
    p.add_argument(
        "--augment-rules",
        action="store_true",
        help="Union deterministic all-9 rule candidates into the LLM candidate set.",
    )
    p.add_argument(
        "--candidate-prefix",
        default=None,
        help="Per-entity artifact prefix to replay (mode=replay) or write (mode=live).",
    )
    p.add_argument(
        "--candidate-dir",
        type=Path,
        default=Path("experiments"),
        help="Directory holding the per-entity candidate JSONL artifacts.",
    )
    p.add_argument("--out-dir", type=Path, default=Path("experiments"))
    p.add_argument("--out-prefix", default=None, help="Output prefix (auto if omitted).")
    p.add_argument("--progress-every", type=int, default=25)
    p.add_argument("--resume", action="store_true", help="Resume per-entity candidate gen (live).")
    return p


def _auto_prefix(split: str, model: str, n: int, *, augment_rules: bool) -> str:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    suffix = "_ruleaug" if augment_rules else ""
    return f"exectv2_hybrid_all_entities_{split}{n_str}_{model_slug}_{today}{suffix}"


def _generate_live_candidates(
    letters: Any,
    args: argparse.Namespace,
    candidate_prefix: str,
) -> dict[str, list[Any]]:
    """Run the focused per-entity extractor for every entity (resumable)."""
    rows_by_entity: dict[str, list[dict[str, Any]]] = {}
    for entity in hybrid.ENTITY_NAMES:
        jsonl_path = args.candidate_dir / f"{candidate_prefix}_{hybrid.entity_slug(entity)}.jsonl"
        report_path = args.candidate_dir / f"{candidate_prefix}_{hybrid.entity_slug(entity)}.md"
        print(f"\n=== candidate gen: {entity} over {len(letters)} letters ===", flush=True)
        rows, _meta = per_entity.run_split(
            letters,
            entity_name=entity,
            split=args.split,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            mode="live",
            dspy_cache=not args.no_dspy_cache,
            api_base=args.api_base,
            progress_every=args.progress_every,
            checkpoint_jsonl_path=jsonl_path,
            checkpoint_report_path=report_path,
            resume=args.resume,
        )
        per_entity.write_jsonl(rows, jsonl_path)
        per_entity.write_report(
            rows, _meta, report_path, jsonl_path=jsonl_path
        )
        rows_by_entity[entity] = rows
    return hybrid.candidates_from_per_entity_rows(rows_by_entity)


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

    if args.mode == "live":
        candidate_prefix = args.candidate_prefix or _auto_prefix(
            args.split, args.model, n, augment_rules=False
        ).replace("hybrid_all_entities", "llm_only_per_entity")
        candidates_by_letter = _generate_live_candidates(letters, args, candidate_prefix)
    else:
        if not args.candidate_prefix:
            print(
                "ERROR: --candidate-prefix is required for --mode replay.",
                file=sys.stderr,
            )
            sys.exit(1)
        candidates_by_letter = hybrid.load_candidates_from_per_entity(
            args.candidate_prefix, out_dir=args.candidate_dir
        )

    rows, metadata = hybrid.run_replay(
        letters,
        candidates_by_letter,
        split=args.split,
        model=args.model,
        augment_rules=args.augment_rules,
    )

    out_prefix = args.out_prefix or _auto_prefix(
        args.split, args.model, n, augment_rules=args.augment_rules
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / f"{out_prefix}.jsonl"
    report_path = args.out_dir / f"{out_prefix}.md"
    hybrid.write_jsonl(rows, jsonl_path)
    hybrid.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    summary = metadata.get("summary", {})
    scores = summary.get("scores", {})
    print(f"\nWrote: {report_path}", flush=True)
    print(
        f"Candidates={summary.get('n_candidates', 0)} "
        f"scored={summary.get('n_mentions_scored', 0)} "
        f"routed={summary.get('n_routed', 0)}",
        flush=True,
    )
    print(f"Routed taxonomy: {summary.get('routed_taxonomy', {})}", flush=True)
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


if __name__ == "__main__":
    main()
