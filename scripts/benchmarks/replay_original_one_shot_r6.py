"""Fixed aggregate-only r6 replication of the 20260910 saved outputs; no model calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.gan_cell_replay import (
    score_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_original_r6 as r6

SOURCE = Path("scratch/holdout/paper/gan_llm_extract_encode_select/deepseek_v41_flash/20260910")


def main() -> None:
    comparison = json.loads((SOURCE / "comparison.json").read_text())
    records = {r.source_row_index: r for r in load_records_for_split("test")}
    rows = [json.loads(line) for line in (SOURCE / "rows.jsonl").read_text().splitlines()]
    if (
        len(rows) != 450
        or len(records) != 450
        or {r["source_row_index"] for r in rows} != set(records)
    ):
        raise ValueError("Holdout coverage mismatch; no row details exposed")
    totals = {"n": 450, "purist_correct": 0, "pragmatic_correct": 0, "parse_failures": 0}
    for row in rows:
        if row["prompt_version"] != "gan_llm_extract_encode_select":
            raise ValueError("Prompt identity mismatch; no row details exposed")
        record = records[row["source_row_index"]]
        try:
            extraction = r6.parse(row["raw_output"], record)
        except Exception:
            raise RuntimeError("Replay exception; inspect development fixtures only") from None
        scored = score_label(record, extraction.selection.final_label if extraction else None)
        totals["parse_failures"] += int(extraction is None)
        for method in ("purist", "pragmatic"):
            totals[method + "_correct"] += int(scored[method + "_correct"])
    expected = {k: comparison["summary"][k] for k in ("purist_correct", "pragmatic_correct")}
    report = {
        "version": r6.VERSION,
        "runtime": r6.RUNTIME,
        "source": str(SOURCE),
        "source_sha256": {
            name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
            for name in ("comparison.json", "rows.jsonl")
        },
        "dataset": "Gan 2026 synthetic",
        "split": "test450",
        "row_policy": "aggregate_only",
        "scorer": "historical raw_model parser plus native Purist/Pragmatic score_label",
        "replay_mode": "saved outputs; no model calls",
        "model_calls": 0,
        "expected": expected,
        "observed": totals,
        "matches": all(totals[k] == v for k, v in expected.items()),
        "claim": "Scoring/parser replay only; not a fresh model replication.",
    }
    out = Path("results/letter-benchmarks/gan/one_shot_original_r6")
    out.mkdir(parents=True, exist_ok=True)
    (out / "replay.aggregate.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
