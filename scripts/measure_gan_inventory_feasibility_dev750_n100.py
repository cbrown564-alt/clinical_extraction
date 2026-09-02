#!/usr/bin/env python3
"""Run the frozen inventory program on the prespecified Gan dev750 sample.

Protocol: docs/research/gan2026/gan_inventory_feasibility_dev750_n100_protocol_2026-08-28.md
Development letters only. The test split is never loaded.
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.paper.gan_inventory_feasibility import (
    FAMILIES,
    MACHINE_SPLIT,
    PERMITTED_SPLIT,
    PROGRAM_CONFIG,
    PROGRAM_ENTRY,
    SAMPLE_ID,
    SAMPLE_SEED,
    SAMPLE_SIZE,
    choose_illustration_indices,
    family_summaries,
    letter_excerpt,
    mention_subtype,
    require_permitted_split,
    select_sample_indices,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    run_letter,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
    load_split_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/gan_inventory_feasibility_dev750_n100_20260828"
PROTOCOL = (
    "docs/research/gan2026/gan_inventory_feasibility_dev750_n100_protocol_2026-08-28.md"
)


def _git_state() -> dict[str, str]:
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "source_commit": head,
        "dirty_tree": "yes" if dirty else "no",
    }


def _mention_payload(mention: Any) -> dict[str, Any]:
    attributes = {str(key): str(value) for key, value in dict(mention.attributes).items()}
    return {
        "entity": mention.entity,
        "text": mention.text,
        "subtype": mention_subtype(mention.entity, mention.text, attributes),
        "attributes": attributes,
        "evidence": mention.evidence,
    }


def main() -> int:
    require_permitted_split(PERMITTED_SPLIT)
    manifest = load_split_manifest(DEFAULT_SPLIT_MANIFEST_PATH)
    pool = [int(index) for index in manifest["splits"][MACHINE_SPLIT]["source_row_indices"]]
    selected = select_sample_indices(pool, size=SAMPLE_SIZE, seed=SAMPLE_SEED)
    records = {
        record.source_row_index: record
        for record in load_records_for_split(
            MACHINE_SPLIT,
            data_path=DEFAULT_DATA_PATH,
            manifest_path=DEFAULT_SPLIT_MANIFEST_PATH,
        )
    }
    rows: list[dict[str, Any]] = []
    notes: dict[int, str] = {}
    for source_row_index in selected:
        record = records[source_row_index]
        notes[source_row_index] = record.note_text
        letter = ExectLetter(
            letter_id=f"gan:{source_row_index}",
            note_text=record.note_text,
            annotations=(),
        )
        result = run_letter(letter)
        mentions = [
            _mention_payload(mention)
            for mention in result.comparison_projection.mentions
            if mention.entity in FAMILIES
        ]
        rows.append({"source_row_index": source_row_index, "mentions": mentions})

    summaries = family_summaries(rows)
    illustration_indices = choose_illustration_indices(rows)
    row_by_index = {int(row["source_row_index"]): row for row in rows}
    illustrations = []
    for source_row_index in illustration_indices:
        row = row_by_index[source_row_index]
        illustrations.append(
            {
                "source_row_index": source_row_index,
                "excerpt": letter_excerpt(notes[source_row_index]),
                "inventory": row["mentions"],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_path = OUT_DIR / "rows.jsonl"
    rows_path.write_text(
        "".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    summary = {
        "schema_version": "gan_inventory_feasibility.v1",
        "study": SAMPLE_ID,
        "date": date.today().isoformat(),
        "protocol": PROTOCOL,
        **_git_state(),
        "dataset": "Gan 2026",
        "split": PERMITTED_SPLIT,
        "machine_split": MACHINE_SPLIT,
        "row_policy": "all 750 development letters eligible; no row_ok filter",
        "sample_seed": SAMPLE_SEED,
        "sample_size": SAMPLE_SIZE,
        "selected_source_row_indices": list(selected),
        "program_entry": PROGRAM_ENTRY,
        "program_config": PROGRAM_CONFIG,
        "model": None,
        "scorer": None,
        "family_summaries": summaries,
        "illustration_source_row_indices": list(illustration_indices),
        "illustrations": illustrations,
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"wrote": str(OUT_DIR), "families": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
