"""One command for paper live cells."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from clinical_extraction.paper.exect import (
    MODELS,
    run_compact,
    run_llm_only,
    verify_compact,
    verify_llm_only,
)
from clinical_extraction.paper.exect_later_stage import (
    run_later_stage as run_exect_later_stage,
)
from clinical_extraction.paper.exect_later_stage import (
    verify_later_stage_prompt,
)
from clinical_extraction.paper.exect_panel import promote_exect, promote_exect_llm_only
from clinical_extraction.paper.exect_rung_replay import replay_exect_rungs
from clinical_extraction.paper.gan import run_gan, verify_gan
from clinical_extraction.paper.gan_panel import promote_gan
from clinical_extraction.paper.gan_rung_replay import replay_gan_rungs
from clinical_extraction.paper.methods import LIVE_METHODS, method_spec, split_for


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify a paper method cell.",
    )
    parser.add_argument(
        "action",
        choices=("verify", "run", "promote-gan", "promote-exect", "replay-rungs"),
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
        if args.method == "exect_llm_only":
            print(
                json.dumps(
                    promote_exect_llm_only(args.model, args.split),
                    indent=2,
                    sort_keys=True,
                )
            )
            return
        if args.method not in {"exect_llm_pre_post", "exect_llm_with_rules"}:
            raise SystemExit("promote-exect is ExECT pre-post or ExECT LLM only")
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
        if method == "exect_llm_encode":
            if slug is not None and slug != "gemini37flash":
                raise RuntimeError("later-stage ExECT encode runs on Gemini only")
            verify_later_stage_prompt(method)
            return {
                "ok": True,
                "method": method,
                "prompt_version": "exect_llm_encode",
                "split": split,
                "row_policy": "development_review_permitted",
            }
        if method == "exect_llm_only":
            return verify_llm_only(split=split, slug=slug)
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
    if row_limit is not None and method != "gan_llm_pre_post":
        raise SystemExit("--row-limit is only for gan_llm_pre_post development slices")
    if slice_name is not None and method != "gan_llm_pre_post":
        raise SystemExit("--slice is only for gan_llm_pre_post development slices")
    if row_limit is not None and slice_name is not None:
        raise SystemExit("--row-limit and --slice cannot be combined")
    if spec["task"] == "exectv2":
        if method == "exect_llm_encode":
            return run_exect_later_stage(
                method,
                slug,
                split=split,
                overwrite=overwrite,
                api_base=api_base,
                timeout=timeout,
                progress_every=progress_every,
                reasoning_effort=reasoning_effort,
            )
        if method == "exect_llm_only":
            return run_llm_only(
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
        row_limit=row_limit,
        slice_name=slice_name,
    )
