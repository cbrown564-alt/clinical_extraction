"""One command for paper live cells."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any, cast

from clinical_extraction.paper.exect import (
    MODELS,
    rescore_inventory_baseline,
    rescore_inventory_residuals,
    run_compact,
    run_llm_extract,
    run_llm_extract_filtered,
    verify_compact,
    verify_llm_extract,
    verify_llm_extract_filtered,
)
from clinical_extraction.paper.exect_cell_replay import (
    replay_exect_pre_post_encode,
    replay_exect_rungs,
)
from clinical_extraction.paper.exect_later_stage import (
    LaterStageMethod as ExectLaterStageMethod,
)
from clinical_extraction.paper.exect_later_stage import (
    run_later_stage as run_exect_later_stage,
)
from clinical_extraction.paper.exect_later_stage import (
    verify_later_stage_prompt,
)
from clinical_extraction.paper.exect_panel import (
    promote_exect,
    promote_exect_later_stage,
    promote_exect_llm_extract,
    promote_exect_llm_only,
)
from clinical_extraction.paper.gan import run_gan, verify_gan
from clinical_extraction.paper.gan_cell_replay import replay_gan_rungs
from clinical_extraction.paper.gan_panel import promote_gan
from clinical_extraction.paper.methods import (
    LIVE_METHODS,
    canonical_exect_method,
    method_spec,
    split_for,
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify a paper method cell.",
    )
    parser.add_argument(
        "action",
        choices=(
            "verify",
            "run",
            "promote-gan",
            "promote-exect",
            "replay-rungs",
            "score-inventory",
            "score-inventory-residual",
        ),
    )
    parser.add_argument("--method", required=True, choices=sorted(LIVE_METHODS))
    parser.add_argument("--model", choices=tuple(MODELS))
    parser.add_argument("--split", required=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high"))
    parser.add_argument("--thinking", choices=("enabled", "disabled"))
    parser.add_argument("--row-limit", type=int)
    parser.add_argument("--slice")
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
            raise SystemExit(
                "score-inventory-residual requires --method exect_llm_extract"
            )
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
    if args.action == "replay-rungs":
        if args.split in {"dev750", "test450"}:
            slug = args.model or "grok46"
            print(
                json.dumps(
                    replay_gan_rungs(args.split, slug=slug),
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
                    replay_exect_rungs(args.split, slug=slug),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        raise SystemExit(
            "replay-rungs accepts --split dev750, test450, dev140, or test60"
        )
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
        if canonical_exect_method(args.method) == "exect_llm_extract_filtered":
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
            raise SystemExit(
                "promote-exect is ExECT pre-post, LLM only, encode, or select"
            )
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
    if not args.live:
        raise SystemExit("run requires --live")
    if args.model is None:
        raise SystemExit("run requires --model")
    print(
        json.dumps(
            run(
                args.method,
                args.model,
                args.split,
                overwrite=args.overwrite,
                api_base=args.api_base,
                timeout=args.timeout,
                progress_every=args.progress_every,
                reasoning_effort=args.reasoning_effort,
                thinking=args.thinking,
                row_limit=args.row_limit,
                slice_name=args.slice,
            ),
            indent=2,
            sort_keys=True,
        )
    )


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
                    "exect_llm_encode"
                    if method == "exect_llm_encode"
                    else "exect_llm_select"
                ),
                "split": split,
                "row_policy": (
                    "aggregate_only"
                    if split == "test60"
                    else "development_review_permitted"
                ),
            }
        resolved = canonical_exect_method(method)
        if resolved == "exect_llm_extract_filtered":
            return verify_llm_extract_filtered(split=split, slug=slug)
        if resolved == "exect_llm_extract":
            return verify_llm_extract(split=split, slug=slug)
        return verify_compact(split=split, slug=slug)
    return verify_gan(method, split, slug)


def run(
    method: str,
    slug: str,
    split: str,
    *,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    reasoning_effort: str | None = None,
    thinking: str | None = None,
    row_limit: int | None = None,
    slice_name: str | None = None,
) -> dict[str, Any]:
    """Run one allowed paper cell."""

    spec = method_spec(method)
    split_for(method, split)
    if row_limit is not None or slice_name is not None:
        raise SystemExit("--row-limit and --slice were removed with gan_llm_pre_post")
    if spec["task"] == "exectv2":
        if method in {"exect_llm_encode", "exect_llm_select"}:
            return run_exect_later_stage(
                cast(ExectLaterStageMethod, method),
                slug,
                split=split,
                overwrite=overwrite,
                api_base=api_base,
                timeout=timeout,
                progress_every=progress_every,
                reasoning_effort=reasoning_effort,
            )
        resolved = canonical_exect_method(method)
        if resolved == "exect_llm_extract":
            return run_llm_extract(
                slug,
                live=True,
                split=split,
                overwrite=overwrite,
                api_base=api_base,
                timeout=timeout,
                progress_every=progress_every,
                thinking=thinking,
                reasoning_effort=reasoning_effort,
            )
        if resolved == "exect_llm_extract_filtered":
            return run_llm_extract_filtered(
                slug,
                live=True,
                split=split,
                overwrite=overwrite,
                api_base=api_base,
                timeout=timeout,
                progress_every=progress_every,
                thinking=thinking,
                reasoning_effort=reasoning_effort,
            )
        return run_compact(
            slug,
            live=True,
            split=split,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout,
            progress_every=progress_every,
            thinking=thinking,
            reasoning_effort=reasoning_effort,
        )
    return run_gan(
        method,
        slug,
        live=True,
        split=split,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
    )
