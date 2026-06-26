"""Shared CLI helpers for ExECTv2 verifier runners."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)

TEST_SPLIT_ERROR = "ERROR: test split is locked; only dev is permitted."


def guard_test_split(split: str) -> None:
    if split == "test":
        print(TEST_SPLIT_ERROR, file=sys.stderr)
        sys.exit(1)


def auto_experiment_path(prefix: str, split: str, model: str, n: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = f"{prefix}_{split}{n_str}_{model_slug}_{today}"
    return Path("experiments") / f"{name}.{suffix}"


def add_llm_run_args(
    parser: argparse.ArgumentParser,
    *,
    default_max_tokens: int = 2400,
) -> None:
    parser.add_argument("--split", default="dev", help="Data split; test is locked.")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="prompt-only")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=default_max_tokens)
    parser.add_argument("--no-dspy-cache", action="store_true")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--pilot", type=int, default=None)
    parser.add_argument("--resume", action="store_true")


def add_verifier_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--draft-jsonl", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)


def build_verifier_parser(
    description: str,
    *,
    default_max_tokens: int = 2400,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    add_llm_run_args(parser, default_max_tokens=default_max_tokens)
    add_verifier_io_args(parser)
    return parser


def load_jsonl_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def print_verifier_summary(
    jsonl_path: Path,
    report_path: Path,
    summary: dict,
    *,
    headline_label: str | None = None,
    entity_headline_key: str | None = None,
    print_headlines: Callable[[dict], None] | None = None,
) -> None:
    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Letters: {summary.get('examples', 0)}", flush=True)
    print(f"Call failures: {summary.get('call_failures', 0)}", flush=True)
    print(f"Parse failures: {summary.get('parse_failures', 0)}", flush=True)
    print(f"Evidence validity: {summary.get('evidence_validity_rate', 0):.4f}", flush=True)
    if print_headlines is not None:
        print_headlines(summary)
    elif entity_headline_key and headline_label:
        clinical = summary.get("clinical_recovery", {}).get(entity_headline_key, {})
        print(
            f"{headline_label} clinical headline: "
            f"P={clinical.get('precision', 0):.3f} "
            f"R={clinical.get('recall', 0):.3f} "
            f"F1={clinical.get('f1', 0):.3f}",
            flush=True,
        )


def run_verifier_cli(
    verifier_module: Any,
    *,
    prefix: str,
    description: str,
    verifier_display_name: str,
    entity_headline_key: str | None = None,
    headline_label: str | None = None,
    default_max_tokens: int = 2400,
    print_headlines: Callable[[dict], None] | None = None,
    argv: list[str] | None = None,
) -> None:
    parser = build_verifier_parser(description, default_max_tokens=default_max_tokens)
    args = parser.parse_args(argv)
    guard_test_split(args.split)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]
    draft_rows = verifier_module.read_draft_rows(args.draft_jsonl)
    n = len(letters)
    jsonl_path = args.out_jsonl or auto_experiment_path(prefix, args.split, args.model, n, "jsonl")
    report_path = args.out_report or auto_experiment_path(prefix, args.split, args.model, n, "md")

    print(
        f"Running {verifier_display_name} / mode={args.mode} / model={args.model} "
        f"over {n} letters from split '{args.split}' ...",
        flush=True,
    )
    rows, metadata = verifier_module.run_split(
        letters,
        draft_rows=draft_rows,
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
    verifier_module.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    summary = metadata.get("summary", {})
    print_verifier_summary(
        jsonl_path,
        report_path,
        summary,
        headline_label=headline_label,
        entity_headline_key=entity_headline_key,
        print_headlines=print_headlines,
    )
