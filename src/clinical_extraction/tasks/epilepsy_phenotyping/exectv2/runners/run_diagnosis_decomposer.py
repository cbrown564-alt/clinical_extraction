"""CLI runner for the ExECTv2 Diagnosis heading/narrative decomposer."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_decomposer as decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ExECTv2 Diagnosis heading/narrative decomposer over a structured "
            "key-entity draft"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev", help="Data split; test is locked.")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="prompt-only")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2600)
    parser.add_argument("--no-dspy-cache", action="store_true")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--pilot", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--draft-jsonl", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(split: str, model: str, n: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    n_str = str(n) if n else "all"
    name = f"exectv2_hybrid_diagnosis_decomposer_{split}{n_str}_{model_slug}_{today}"
    return Path("experiments") / f"{name}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        print("ERROR: test split is locked; only dev is permitted.", file=sys.stderr)
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    if args.pilot:
        letters = letters[: args.pilot]
    draft_rows = decomposer.read_draft_rows(args.draft_jsonl)
    n = len(letters)
    jsonl_path = args.out_jsonl or _auto_path(args.split, args.model, n, "jsonl")
    report_path = args.out_report or _auto_path(args.split, args.model, n, "md")

    print(
        f"Running diagnosis decomposer / mode={args.mode} / model={args.model} "
        f"over {n} letters from split '{args.split}' ...",
        flush=True,
    )
    rows, metadata = decomposer.run_split(
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
    decomposer.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("diagnosis", {})
    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Letters: {summary.get('examples', 0)}", flush=True)
    print(f"Call failures: {summary.get('call_failures', 0)}", flush=True)
    print(f"Parse failures: {summary.get('parse_failures', 0)}", flush=True)
    print(f"Evidence validity: {summary.get('evidence_validity_rate', 0):.4f}", flush=True)
    print(f"Diagnosis spans: {summary.get('n_diagnosis_spans', 0)}", flush=True)
    print(
        "Diagnosis clinical headline: "
        f"P={clinical.get('precision', 0):.3f} "
        f"R={clinical.get('recall', 0):.3f} "
        f"F1={clinical.get('f1', 0):.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
