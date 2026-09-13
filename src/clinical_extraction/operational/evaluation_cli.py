"""One command for paper live cells."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any, cast

from clinical_extraction.evaluation.letter_benchmarks.five_cell import write_five_cell_grid
from clinical_extraction.evaluation.letter_benchmarks.methods import (
    LIVE_METHODS,
    canonical_exect_method,
    method_spec,
    split_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.evaluation.exect import (
    RUNNABLE_MODELS,
    rescore_inventory_baseline,
    rescore_inventory_residuals,
    verify_compact,
    verify_llm_extract,
    verify_llm_extract_filtered,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.evaluation.exect_cell_replay import (
    replay_exect_pre_post_encode,
    replay_exect_rungs,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.evaluation.exect_later_stage import (
    LaterStageMethod as ExectLaterStageMethod,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.evaluation.exect_later_stage import (
    verify_later_stage_prompt,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.evaluation.exect_panel import (
    promote_exect,
    promote_exect_later_stage,
    promote_exect_llm_extract,
    promote_exect_llm_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan import (
    reparse_gan_llm_extract_raw,
    verify_gan,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan_cell_replay import (
    replay_gan_rungs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan_panel import promote_gan


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify a paper method cell.",
    )
    parser.add_argument(
        "action",
        choices=(
            "verify",
            "promote-gan",
            "promote-exect",
            "replay-rungs",
            "reparse-gan",
            "write-five-cell",
            "score-inventory",
            "score-inventory-residual",
        ),
    )
    parser.add_argument("--method", required=True, choices=sorted(LIVE_METHODS))
    parser.add_argument("--model", choices=tuple(RUNNABLE_MODELS))
    parser.add_argument("--split", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high"))
    parser.add_argument("--thinking", choices=("enabled", "disabled"))
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--row-limit", type=int)
    parser.add_argument("--slice")
    parser.add_argument("--work-leaf")
    parser.add_argument("--recorded-prompt-version")
    parser.add_argument("--live-sync", action="store_true")
    parser.add_argument(
        "--extract-method",
        choices=("gan_llm_extract", "gan_llm_extract_raw"),
    )
    parser.add_argument("--encode-work-leaf")
    parser.add_argument("--encode-rows-path")
    args = parser.parse_args(argv)
    if args.action == "score-inventory":
        if canonical_exect_method(args.method) != "exect_llm_extract":
            raise SystemExit("score-inventory requires --method exect_llm_extract")
        if args.split != "dev140":
            raise SystemExit("score-inventory is DEV140 only")
        print(
            json.dumps(
                rescore_inventory_baseline(slug=args.model or "gemini37flash"),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.action == "score-inventory-residual":
        if canonical_exect_method(args.method) != "exect_llm_extract":
            raise SystemExit("score-inventory-residual requires --method exect_llm_extract")
        if args.split != "dev140":
            raise SystemExit("score-inventory-residual is DEV140 only")
        print(
            json.dumps(
                rescore_inventory_residuals(slug=args.model or "gemini37flash"),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.action == "write-five-cell":
        slug = args.model or "gemini37flash"
        print(
            json.dumps(
                write_five_cell_grid(args.method, slug=slug, split=args.split),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.action == "replay-rungs":
        ablation = args.method in {
            "gan_llm_extract_raw",
            "gan_llm_only",
            "exect_llm_only",
            "exect_llm_extract_filtered",
            "exect_llm_extract_and_select",
        }
        source = "ablation" if ablation else "living"
        if args.split in {"dev750", "test450"}:
            slug = args.model or "grok46"
            print(
                json.dumps(
                    replay_gan_rungs(args.split, slug=slug, source=source),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        if args.split in {"dev140", "test60"}:
            slug = args.model or "grok46"
            if args.method in {"exect_llm_pre_post", "exect_llm_with_rules"}:
                print(
                    json.dumps(
                        replay_exect_pre_post_encode(args.split, slug=slug),
                        indent=2,
                        sort_keys=True,
                    )
                )
                return
            print(
                json.dumps(
                    replay_exect_rungs(args.split, slug=slug, source=source),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        raise SystemExit("replay-rungs accepts --split dev750, test450, dev140, or test60")
    if args.action == "reparse-gan":
        if args.method != "gan_llm_extract_raw":
            raise SystemExit("reparse-gan only accepts --method gan_llm_extract_raw")
        if args.model is None:
            raise SystemExit("reparse-gan requires --model")
        if args.split not in {"dev750", "test450"}:
            raise SystemExit("reparse-gan only accepts --split dev750 or test450")
        print(
            json.dumps(
                reparse_gan_llm_extract_raw(args.model, args.split),
                indent=2,
                sort_keys=True,
            )
        )
        return
    split_for(args.method, args.split)
    if args.action == "promote-gan":
        if args.model is None:
            raise SystemExit("promote-gan requires --model")
        if args.split not in {"dev750", "test450"}:
            raise SystemExit("promote-gan only accepts --split dev750 or test450")
        print(
            json.dumps(
                promote_gan(args.method, args.model, args.split),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.action == "promote-exect":
        if args.model is None:
            raise SystemExit("promote-exect requires --model")
        if args.split not in {"dev140", "test60"}:
            raise SystemExit("promote-exect only accepts --split dev140 or test60")
        if canonical_exect_method(args.method) == "exect_llm_extract":
            print(
                json.dumps(
                    promote_exect_llm_extract(args.model, args.split),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        if canonical_exect_method(args.method) == "exect_llm_extract_and_select":
            print(
                json.dumps(
                    promote_exect_llm_only(args.model, args.split),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        if args.method in {"exect_llm_encode", "exect_llm_select"}:
            print(
                json.dumps(
                    promote_exect_later_stage(args.method, args.model, args.split),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        if args.method not in {"exect_llm_pre_post", "exect_llm_with_rules"}:
            raise SystemExit("promote-exect is ExECT pre-post, LLM only, encode, or select")
        print(
            json.dumps(
                promote_exect(args.model, args.split),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.action == "verify":
        print(json.dumps(verify(args.method, args.split, args.model), indent=2, sort_keys=True))
        return


def verify(method: str, split: str, slug: str | None = None) -> dict[str, Any]:
    """Verify a paper method cell without calling a model."""

    spec = method_spec(method)
    split_for(method, split)
    if spec["task"] == "exectv2":
        if method in {"exect_llm_encode", "exect_llm_select"}:
            if slug is not None and slug != "gemini37flash":
                raise RuntimeError("later-stage ExECT encode and select run on Gemini only")
            verify_later_stage_prompt(cast(ExectLaterStageMethod, method))
            return {
                "ok": True,
                "method": method,
                "prompt_version": (
                    "exect_llm_encode" if method == "exect_llm_encode" else "exect_llm_select"
                ),
                "split": split,
                "row_policy": (
                    "aggregate_only" if split == "test60" else "development_review_permitted"
                ),
            }
        resolved = canonical_exect_method(method)
        if resolved == "exect_llm_extract_and_select":
            return verify_llm_extract_filtered(split=split, slug=slug)
        if resolved == "exect_llm_extract":
            return verify_llm_extract(split=split, slug=slug)
        return verify_compact(split=split, slug=slug)
    return verify_gan(method, split, slug)
