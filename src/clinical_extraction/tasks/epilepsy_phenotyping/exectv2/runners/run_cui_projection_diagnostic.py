"""CLI for the ExECTv2 benchmark CUI-projection ablation (satellite 09, Phase D).

Reads a combined all-entity prediction JSONL (gold + predicted mentions, as
written by ``run_hybrid_all_entities`` or ``run_llm_only_all``) and reports the
deterministic CUI projection's coverage and correctness per entity — the
separate post-step ablation the benchmark (with-CUI) headline depends on.

Usage::

    uv run python -m \\
        clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_cui_projection_diagnostic \\
        --in-jsonl experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cui_projection_diagnostic import (
    cui_projection_diagnostic,
    render_markdown,
)

ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)


def _letters_from_rows(rows: list[dict], key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in (row.get(key) or [])
        )
        letters.append(
            ExectLetter(letter_id=row["letter_id"], note_text="", annotations=annotations)
        )
    return letters


def main() -> None:
    parser = argparse.ArgumentParser(description="ExECTv2 CUI-projection ablation")
    parser.add_argument("--in-jsonl", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    rows = load_jsonl_rows(args.in_jsonl)
    gold = _letters_from_rows(rows, "gold_mentions")
    pred = _letters_from_rows(rows, "predicted_mentions")
    diagnostic = cui_projection_diagnostic(gold, pred, ENTITY_NAMES)

    out_md = args.out_md or args.in_jsonl.with_name(args.in_jsonl.stem + "_cui_projection.md")
    out_json = args.out_json or args.in_jsonl.with_name(args.in_jsonl.stem + "_cui_projection.json")
    markdown = render_markdown(diagnostic, entities=ENTITY_NAMES, source=str(args.in_jsonl))
    out_md.write_text(markdown, encoding="utf-8")

    payload: dict[str, Any] = {
        "source": str(args.in_jsonl),
        "per_entity": {e: asdict(d) for e, d in diagnostic.per_entity.items()},
        "overall": asdict(diagnostic.overall),
    }
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote: {out_md}")
    o = diagnostic.overall
    print(
        f"Overall CUI coverage {o.coverage:.2f} ({o.predicted_with_cui}/{o.predicted_mentions}); "
        f"agreement {o.cui_agreement_rate:.2f} ({o.cui_agree}/{o.cui_both_present}); "
        f"gold CUI density {o.gold_cui_density:.2f}"
    )


if __name__ == "__main__":
    main()
