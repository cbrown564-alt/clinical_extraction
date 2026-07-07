"""Apply the deterministic benchmark-altitude projection to a fixed LLM prediction.

Reads an all-entity hybrid JSONL (the LLM clinical layer), applies
``deterministic.benchmark_altitude.project_altitude`` per letter, re-scores with
the shared all-entity scorer, and writes a report comparing pre- vs
post-projection per entity. Zero LLM calls — pure deterministic projection credit.

Usage::

    uv run python -m \\
      clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_benchmark_altitude_projection \\
      --in-jsonl experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.benchmark_altitude import (
    project_altitude,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)


def _mention_from_row(m: dict[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=str(m["entity"]),
        text=str(m["text"]),
        attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
        evidence=str(m.get("evidence", "")),
        confidence=m.get("confidence") or "medium",
        rationale=str(m.get("rationale", "")),
        component_owner=str(m.get("component_owner", "")),
    )


def _mention_to_row(m: PredictedMention) -> dict[str, Any]:
    return {
        "entity": m.entity,
        "text": m.text,
        "attributes": dict(m.attributes),
        "evidence": m.evidence,
        "confidence": m.confidence,
        "rationale": m.rationale,
        "component_owner": m.component_owner,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="ExECTv2 benchmark-altitude projection")
    p.add_argument("--in-jsonl", type=Path, required=True)
    p.add_argument("--out-prefix", default=None)
    p.add_argument("--out-dir", type=Path, default=Path("experiments"))
    args = p.parse_args()

    in_rows = [
        json.loads(line)
        for line in args.in_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out_rows: list[dict[str, Any]] = []
    for row in in_rows:
        mentions = [_mention_from_row(m) for m in (row.get("predicted_mentions") or [])]
        projected = project_altitude(
            PredictedLetter(letter_id=row["letter_id"], mentions=tuple(mentions))
        )
        out_rows.append(
            {
                **{k: row[k] for k in ("letter_id", "split") if k in row},
                "prompt_version": "benchmark_altitude_v0.1",
                "model": row.get("model", "projection"),
                "predicted_mentions": [_mention_to_row(m) for m in projected.mentions],
                "gold_mentions": row.get("gold_mentions", []),
            }
        )

    summary = hybrid.summarize_rows(out_rows)
    out_prefix = args.out_prefix or (args.in_jsonl.stem + "_altitude_proj")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / f"{out_prefix}.jsonl"
    report_path = args.out_dir / f"{out_prefix}.md"
    hybrid.write_jsonl(out_rows, jsonl_path)
    hybrid.write_report(
        out_rows,
        {
            "summary": summary,
            "split": in_rows[0].get("split"),
            "model": "altitude_projection",
            "prompt_version": "benchmark_altitude_v0.1",
        },
        report_path,
        jsonl_path=jsonl_path,
    )

    # Pre vs post comparison.
    pre = hybrid.summarize_rows(
        [
            {**r, "predicted_mentions": orig.get("predicted_mentions", [])}
            for r, orig in zip(out_rows, in_rows, strict=True)
        ]
    )

    def f1(s: dict, layer: str) -> tuple[float, float, float]:
        pi = s.get("scores", {}).get(layer, {}).get("per_item", {})
        return pi.get("precision", 0.0), pi.get("recall", 0.0), pi.get("f1", 0.0)

    print(f"Wrote: {report_path}\n")
    for layer in ("semantic", "benchmark"):
        pp, pr, pf = f1(pre, layer)
        qp, qr, qf = f1(summary, layer)
        print(
            f"{layer:<10} pre  F1={pf:.3f} (P={pp:.3f} R={pr:.3f})  ->  post F1={qf:.3f} (P={qp:.3f} R={qr:.3f})"
        )
    print("\nper-entity semantic item F1 (pre -> post):")
    pre_e = pre.get("scores", {}).get("semantic", {}).get("per_entity", {})
    post_e = summary.get("scores", {}).get("semantic", {}).get("per_entity", {})
    for entity in hybrid.ENTITY_NAMES:
        a = pre_e.get(entity, {}).get("per_item", {}).get("f1", 0.0)
        b = post_e.get(entity, {}).get("per_item", {}).get("f1", 0.0)
        print(f"  {entity:<18} {a:.3f} -> {b:.3f}")


if __name__ == "__main__":
    main()
