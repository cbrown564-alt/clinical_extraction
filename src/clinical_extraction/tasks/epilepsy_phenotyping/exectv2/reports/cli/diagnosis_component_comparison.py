"""Build the final ExECTv2 Diagnosis component comparison on dev140."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from ..diagnosis_component_comparison import build_component_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-summary-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.json"),
    )
    parser.add_argument(
        "--ledger-jsonl",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_resolution_ledger_dev140_20260714.jsonl"),
    )
    parser.add_argument(
        "--sensitivity-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_sensitivity_dev140_20260714.json"),
    )
    parser.add_argument(
        "--llm-candidate-jsonl",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_llm_only_candidate_dev140_20260714.jsonl"
        ),
    )
    parser.add_argument(
        "--hybrid-candidate-jsonl",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_hybrid_resolution_candidate_dev140_20260714.jsonl"
        ),
    )
    parser.add_argument(
        "--out-rules-boundary-jsonl",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_rules_boundary_candidate_dev140_20260714.jsonl"
        ),
    )
    parser.add_argument(
        "--out-rules-full-jsonl",
        type=Path,
        default=Path(
            "experiments/exectv2_diagnosis_rules_resolution_candidate_dev140_20260714.jsonl"
        ),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_diagnosis_component_comparison_dev140_20260714.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path(
            "docs/experiments/exectv2/diagnosis/"
            "exectv2_diagnosis_component_comparison_2026-07-14.md"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    build_component_comparison(
        audit_summary_json=args.audit_summary_json,
        ledger_jsonl=args.ledger_jsonl,
        sensitivity_json=args.sensitivity_json,
        llm_candidate_jsonl=args.llm_candidate_jsonl,
        hybrid_candidate_jsonl=args.hybrid_candidate_jsonl,
        out_rules_boundary_jsonl=args.out_rules_boundary_jsonl,
        out_rules_full_jsonl=args.out_rules_full_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
