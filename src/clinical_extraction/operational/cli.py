"""Command-line interface for operational Gan and ExECT extraction."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.operational.exect import run_exect_notes
from clinical_extraction.operational.gan import run_gan_notes
from clinical_extraction.operational.io import read_notes, write_jsonl_atomic
from clinical_extraction.operational.provider import probe_endpoint
from clinical_extraction.operational.runtime import RuntimeConfig


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "exect" and args.method == "rules":
            runtime = RuntimeConfig(
                base_url="",
                api_key="",
                model="(model-independent)",
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout_seconds=args.timeout,
            )
        else:
            runtime = RuntimeConfig.from_environment(
                base_url=args.base_url,
                api_key=args.api_key,
                model=args.model,
                temperature=getattr(args, "temperature", 0.0),
                max_tokens=getattr(args, "max_tokens", 16000),
                timeout_seconds=args.timeout,
            )
    except ValueError as exc:
        parser.error(str(exc))

    if args.command == "probe":
        print(json.dumps(probe_endpoint(runtime), indent=2, sort_keys=True))
        return 0
    if args.output.exists() and not args.overwrite:
        parser.error(f"output already exists; pass --overwrite to replace it: {args.output}")
    try:
        notes = read_notes(args.input)
    except ValueError as exc:
        parser.error(str(exc))
    rows = (
        run_gan_notes(notes, runtime)
        if args.command == "gan"
        else run_exect_notes(notes, runtime, method=args.method)
    )
    write_jsonl_atomic(rows, args.output)
    failures = sum(row.get("status") != "ok" for row in rows)
    print(json.dumps({"rows": len(rows), "failures": failures, "output": str(args.output)}))
    return 1 if failures else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("gan", "exect"):
        child = subparsers.add_parser(command)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--output", type=Path, required=True)
        child.add_argument("--overwrite", action="store_true")
        child.add_argument("--temperature", type=float, default=0.0)
        child.add_argument("--max-tokens", type=int, default=16000)
        if command == "exect":
            child.add_argument(
                "--method",
                choices=("rules", "llm", "llm_with_rules"),
                default="llm_with_rules",
            )
        _add_runtime_arguments(child)
    probe = subparsers.add_parser("probe")
    _add_runtime_arguments(probe)
    return parser


def _add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", help="OpenAI-compatible API base URL")
    parser.add_argument(
        "--api-key",
        help=(
            "endpoint API key; optional for vllm/<served-model> routes, "
            "which default to EMPTY"
        ),
    )
    parser.add_argument(
        "--model",
        help=(
            "provider/model identifier; use vllm/<model> for vLLM chat-template "
            "settings or gemini/<model> for Gemini via OpenRouter or Google"
        ),
    )
    parser.add_argument("--timeout", type=float, default=300.0)


if __name__ == "__main__":
    sys.exit(main())
