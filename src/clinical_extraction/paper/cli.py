"""One command for paper live cells."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from clinical_extraction.paper.exect import (
    MODELS,
    run_compact,
    run_full_ledger,
    run_llm_only,
    verify_compact,
    verify_full_ledger,
    verify_llm_only,
)
from clinical_extraction.paper.exect_panel import promote_exect
from clinical_extraction.paper.gan import run_gan, verify_gan
from clinical_extraction.paper.gan_panel import promote_gan
from clinical_extraction.paper.methods import LIVE_METHODS, method_spec, split_for


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify a paper method cell.",
    )
    parser.add_argument(
        "action",
        choices=("verify", "run", "promote-gan", "promote-exect"),
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
    args = parser.parse_args(argv)
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
        if args.method != "exect_llm_with_rules":
            raise SystemExit("promote-exect is Compact only")
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
        if method == "exect_full_ledger":
            return verify_full_ledger(split=split, slug=slug)
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
) -> dict[str, Any]:
    """Run one allowed paper cell."""

    spec = method_spec(method)
    split_for(method, split)
    if spec["task"] == "exectv2":
        if method == "exect_full_ledger":
            return run_full_ledger(
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
    )
