"""Run the fixed dev140 Diagnosis-only GPT-4.1-mini candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer as decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    sha256_file,
    write_artifact_bundle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev",), default="dev")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=3200)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--draft-jsonl", type=Path, default=None)
    parser.add_argument("--dspy-cache", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument(
        "--out-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_llm_only_candidate_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--out-metadata-json",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_llm_only_candidate_dev140_20260714.json"
        ),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path(
            "docs/experiments/exectv2/diagnosis/"
            "exectv2_diagnosis_llm_only_candidate_2026-07-14.md"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    letters = load_letters_for_split(args.split)
    drafts = decomposer.read_draft_rows(args.draft_jsonl)
    rows, metadata = decomposer.run_split(
        letters,
        draft_rows=drafts,
        split=args.split,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=args.dspy_cache,
        progress_every=args.progress_every,
        checkpoint_jsonl_path=args.out_jsonl,
        checkpoint_report_path=args.out_md,
        resume=args.resume,
        prompt_profile="full",
        prompt_variant="resolution_v02",
    )
    runtime_usage = _resume_runtime_usage(
        _runtime_usage(),
        metadata_path=args.out_metadata_json,
        resume=args.resume,
    )
    metadata.update(
        {
            "architecture": "llm_only",
            "row_policy": "dev140_rows_permitted_test60_forbidden",
            "draft_source": str(args.draft_jsonl) if args.draft_jsonl else None,
            "post_model_clinical_repair": "none",
            "post_model_format_projection": "deterministic_CUI_projection_only",
            "pre_model_span_hints": (
                "deterministic nonbinding sentence checklist; full letter also supplied"
            ),
            "semantic_decision_owner": "model",
            "architecture_classification_reason": (
                "No draft predictions were supplied and no clinical fact was added, "
                "removed, or changed after the model response."
            ),
            "dspy_cache": args.dspy_cache,
            "prompt_payloads_sha256": _prompt_payloads_sha256(rows),
            "prompt_corpus_sha256": sha256_file(
                Path(decomposer.prompt_loader.__file__).parent / "corpus.yaml"
            ),
            "candidate_rules_sha256": sha256_file(
                Path(decomposer.prompt_loader.__file__).parent
                / "resolution_candidate_rules.yaml"
            ),
            "runtime_usage": runtime_usage,
            "claim_boundary": (
                "Fixed-prompt dev140 development candidate only; not test60, holdout, "
                "clinical validation, or a promoted reference."
            ),
        }
    )
    decomposer.write_jsonl(rows, args.out_jsonl)
    decomposer.write_report(rows, metadata, args.out_md, jsonl_path=args.out_jsonl)
    write_artifact_bundle(
        {args.out_metadata_json: json.dumps(metadata, indent=2, sort_keys=True) + "\n"}
    )
    return 0


def _prompt_payloads_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = "\n".join(str(row.get("prompt_input_json", "")) for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _runtime_usage() -> dict[str, Any]:
    lm = getattr(dspy.settings, "lm", None)
    history = getattr(lm, "history", ()) if lm is not None else ()
    usage_totals: dict[str, int] = {}
    total_cost = 0.0
    for entry in history:
        usage = entry.get("usage") or {}
        for key, value in usage.items():
            if isinstance(value, int):
                usage_totals[key] = usage_totals.get(key, 0) + value
        cost = entry.get("cost")
        if isinstance(cost, int | float):
            total_cost += float(cost)
    return {
        "history_entries": len(history),
        "usage": usage_totals,
        "reported_cost": total_cost,
    }


def _resume_runtime_usage(
    current: dict[str, Any], *, metadata_path: Path, resume: bool
) -> dict[str, Any]:
    if not resume or current.get("history_entries") or not metadata_path.exists():
        return current
    previous = json.loads(metadata_path.read_text(encoding="utf-8"))
    recorded = previous.get("runtime_usage")
    return recorded if isinstance(recorded, dict) else current


if __name__ == "__main__":
    raise SystemExit(main())
