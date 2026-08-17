"""One command for paper live cells."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from clinical_extraction.paper.exect import (
    HOSTED_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    run_compact,
    verify_compact,
)
from clinical_extraction.paper.methods import LIVE_METHODS, method_spec, split_for
from clinical_extraction.paper.roster import model_by_slug
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm as gan_llm_only,
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify a paper method cell.",
    )
    parser.add_argument("action", choices=("verify", "run"))
    parser.add_argument("--method", required=True, choices=sorted(LIVE_METHODS))
    parser.add_argument("--model", choices=tuple(MODELS))
    parser.add_argument("--split", required=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    split_for(args.method, args.split)
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
        return verify_compact(split=split, slug=slug)
    prompt = _gan_prompt(method)
    payload = {
        "ok": True,
        "method": method,
        "split": split,
        "prompt_version": prompt,
        "hosted": list(HOSTED_SLUGS),
        "local": list(LOCAL_SLUGS),
    }
    if slug is not None:
        payload["model"] = model_by_slug(slug)["model"]
    return payload


def run(
    method: str,
    slug: str,
    split: str,
    *,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
) -> dict[str, Any]:
    """Run one allowed paper cell."""

    spec = method_spec(method)
    split_for(method, split)
    if spec["task"] == "exectv2":
        return run_compact(
            slug,
            live=True,
            split=split,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout,
            progress_every=progress_every,
        )
    raise SystemExit(
        f"{method} live dispatch is not wired in this CLI yet; "
        "verify the prompt identity first"
    )


def _gan_prompt(method: str) -> str:
    if method == "gan_llm_only":
        return gan_llm_only.PROMPT_VERSION
    if method == "gan_llm_with_rules":
        return hybrid_structured_events.PROMPT_VERSION
    raise ValueError(method)
