"""CLI for the ExECTv2 GPT-first reliability scorecard (satellite 09, Phase E).

Reads a combined all-entity hybrid JSONL, recomputes the scorecard + bootstrap
CIs, and writes the compact reliability scorecard with the promotion-gate
verdict. It never makes model calls and never touches the locked test split; the
full-200 audit stays gated behind the freeze targets.

Usage::

    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_reliability_scorecard \\
        --in-jsonl experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617_ruleaug.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability_scorecard import (
    build_scorecard,
    render_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="ExECTv2 reliability scorecard")
    parser.add_argument("--in-jsonl", type=Path, required=True)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--split", default="dev")
    parser.add_argument("--bootstrap-reps", type=int, default=1000)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    rows = load_jsonl_rows(args.in_jsonl)
    augment_rules = bool(rows and rows[0].get("augment_rules"))
    summary = hybrid.summarize_rows(rows)
    scorecard = build_scorecard(
        rows,
        summary,
        model=args.model,
        split=args.split,
        augment_rules=augment_rules,
        bootstrap_reps=args.bootstrap_reps,
    )

    out_md = args.out_md or args.in_jsonl.with_name(args.in_jsonl.stem + "_scorecard.md")
    out_json = args.out_json or args.in_jsonl.with_name(args.in_jsonl.stem + "_scorecard.json")
    out_md.write_text(render_markdown(scorecard, source=str(args.in_jsonl)), encoding="utf-8")
    out_json.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    gate = scorecard["promotion_gate"]
    print(f"Wrote: {out_md}")
    print(
        f"Benchmark per-item F1 {gate['benchmark_per_item_f1']:.3f} / "
        f"per-letter {gate['benchmark_per_letter_f1']:.3f} "
        f"(targets {gate['freeze_target_per_item']:.2f}/{gate['freeze_target_per_letter']:.2f})"
    )
    print(f"Gate met: {gate['gate_met']} -> full-200 audit authorized: "
          f"{gate['full_200_audit_authorized']}")


if __name__ == "__main__":
    main()
