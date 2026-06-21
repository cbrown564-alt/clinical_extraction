"""CLI runner for the ExECTv2 Diagnosis Phase 2 residual panel."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_phase2_panel as phase2,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ExECTv2 Diagnosis Phase 2 residual-panel runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev", help="Data split; test is locked.")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--mode", choices=["live", "prompt-only"], default="prompt-only")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2600)
    parser.add_argument("--no-dspy-cache", action="store_true")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--panel-size", type=int, default=32)
    parser.add_argument(
        "--variant",
        choices=[*phase2.VARIANTS, "both"],
        default="both",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--ledger-json", type=Path, required=True)
    parser.add_argument("--current-jsonl", type=Path, required=True)
    parser.add_argument("--verifier-jsonl", type=Path, required=True)
    parser.add_argument("--decomposer-jsonl", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    return parser


def _auto_path(split: str, model: str, panel_size: int, suffix: str) -> Path:
    model_slug = model.split("/")[-1].replace("-", "").replace(".", "")
    today = date.today().isoformat().replace("-", "")
    stem = f"exectv2_diagnosis_phase2_panel_{split}{panel_size}_{model_slug}_{today}"
    return Path("experiments") / f"{stem}.{suffix}"


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        print("ERROR: test split is locked; only dev is permitted.", file=sys.stderr)
        sys.exit(1)

    variants = (
        phase2.VARIANTS
        if args.variant == "both"
        else (args.variant,)
    )
    panel = phase2.load_panel_from_ledger(args.ledger_json, panel_size=args.panel_size)
    if not panel:
        print("ERROR: no panel rows selected from ledger.", file=sys.stderr)
        sys.exit(1)

    letters = load_letters_for_split(args.split)
    current_rows = phase2.read_jsonl(args.current_jsonl)
    verifier_rows = phase2.read_jsonl(args.verifier_jsonl)
    decomposer_rows = phase2.read_jsonl(args.decomposer_jsonl)

    jsonl_path = args.out_jsonl or _auto_path(args.split, args.model, len(panel), "jsonl")
    json_path = args.out_json or _auto_path(args.split, args.model, len(panel), "json")
    report_path = args.out_report or _auto_path(args.split, args.model, len(panel), "md")

    print(
        f"Running Diagnosis Phase 2 panel / mode={args.mode} / model={args.model} "
        f"/ panel={len(panel)} / variants={','.join(variants)} ...",
        flush=True,
    )
    rows, metadata = phase2.run_panel(
        letters,
        panel=panel,
        current_rows=current_rows,
        verifier_rows=verifier_rows,
        decomposer_rows=decomposer_rows,
        variants=variants,
        split=args.split,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.no_dspy_cache,
        api_base=args.api_base,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=args.resume,
        progress_every=args.progress_every,
    )
    write_jsonl(rows, jsonl_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    phase2.write_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
        current_rows=current_rows,
    )

    summary = metadata["summary"]
    print(f"\nDone. JSONL: {jsonl_path}  Report: {report_path}", flush=True)
    print(f"Panel letters: {summary.get('panel_letters', 0)}", flush=True)
    print(
        "v02 panel control: "
        f"F1={summary.get('baseline_v02', {}).get('f1', 0):.3f}",
        flush=True,
    )
    for variant, score in summary.get("variant_scores", {}).items():
        print(
            f"{variant}: F1={score.get('f1', 0):.3f} "
            f"delta={score.get('delta_f1_vs_v02', 0):+.3f} "
            f"calls={score.get('call_failures', 0)} parses={score.get('parse_failures', 0)} "
            f"evidence={score.get('evidence_validity_rate', 0):.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
