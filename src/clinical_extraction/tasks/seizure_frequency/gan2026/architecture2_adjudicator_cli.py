"""CLI for Gan 2026 Architecture 2 candidate-adjudicator experiments."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.dspy_modules import (
    DEFAULT_ARCH2_JSONL_PATH,
    DEFAULT_ARCH2_REPORT_PATH,
    load_architecture2_raw_outputs,
    run_architecture2_split,
    write_architecture2_jsonl,
    write_architecture2_report,
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run Gan 2026 Architecture 2: deterministic candidate generator plus "
            "LLM adjudicator."
        )
    )
    parser.add_argument("--split", choices=("train", "validation"), default="validation")
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_ARCH2_JSONL_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_ARCH2_REPORT_PATH)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1100)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--reuse-jsonl", type=Path, action="append", default=[])
    parser.add_argument(
        "--escalation-reason",
        default=None,
        help="Reason for a broader validation run; recorded in the report.",
    )
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args(argv)

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))

    reuse_raw_outputs: dict[int, str] = {}
    for reuse_jsonl in args.reuse_jsonl:
        reuse_raw_outputs.update(load_architecture2_raw_outputs(reuse_jsonl))
    reuse_source = ", ".join(str(path) for path in args.reuse_jsonl) or None
    progress_every = args.progress_every if args.progress_every > 0 else None

    rows, metadata = run_architecture2_split(
        records,
        split=args.split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        reuse_raw_outputs=reuse_raw_outputs,
        reuse_source=reuse_source,
        escalation_reason=args.escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
    )
    write_architecture2_jsonl(rows, args.jsonl)
    write_architecture2_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
