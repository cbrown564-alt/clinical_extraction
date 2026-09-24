"""Compare saved R9/R11 dev750 outputs under the common compact scorer."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks import run_r8
from scripts.benchmarks import score_compact_findings_v03 as base

R9 = Path("runs/one_shot_frequency_v2_measurements_r9/dev750")
R11 = Path("runs/one_shot_frequency_v2_measurements_r11/dev750")
RESULT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11/"
    "dev750/r9_r11_paired_comparison.json"
)
SEED = 20260924
BOOTSTRAPS = 5000


def by_index(path: Path) -> dict[int, dict]:
    rows = [json.loads(line) for line in path.open()]
    found = {row["source_row_index"]: row for row in rows}
    if len(rows) != 750 or len(found) != 750:
        raise ValueError(f"Expected 750 unique rows: {path}")
    return found


def f1(tp: int, fp: int, fn: int) -> float:
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0


def native_correct(pred: dict[str, Any], record: Any, method: str) -> bool:
    response = pred.get("response")
    answer = response.get("answer") if isinstance(response, dict) else None
    projected = (
        {"label": answer.get("label"), "evidence": answer.get("evidence")}
        if isinstance(answer, dict)
        else None
    )
    checked = study.r4.v1.inspect_output(
        json.dumps({"answer": projected}) if projected else None,
        record.note_text,
        "simple",
    )
    return (
        checked["failure"] is None
        and checked["categories"][method] == (study.old.gold_categories(record.raw)[method])
    )


def main() -> None:
    if RESULT.exists():
        raise FileExistsError(RESULT)
    s9 = by_index(R9 / "calendar_window_v04/per_letter.jsonl")
    s11 = by_index(R11 / "per_letter.jsonl")
    p9 = by_index(R9 / "parsed_predictions.jsonl")
    p11 = by_index(R11 / "parsed_predictions.jsonl")
    records = {record.source_row_index: record for record in run_r8.records("dev750")}
    rows = []
    native = {method: Counter() for method in ("purist", "pragmatic")}
    for index in sorted(records):
        if any(
            row["source_sha256"] != s9[index]["source_sha256"]
            for row in (s11[index], p9[index], p11[index])
        ):
            raise ValueError(f"Source mismatch: {index}")
        before, after = s9[index]["score"], s11[index]["score"]
        rows.append((before, after))
        for method in native:
            old = native_correct(p9[index], records[index], method)
            new = native_correct(p11[index], records[index], method)
            native[method]["r9_correct"] += old
            native[method]["r11_correct"] += new
            native[method]["r11_win"] += new and not old
            native[method]["r9_win"] += old and not new
    rng = random.Random(SEED)
    differences = []
    for _ in range(BOOTSTRAPS):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        old = [sum(pair[0][key] for pair in sample) for key in ("tp", "fp", "fn")]
        new = [sum(pair[1][key] for pair in sample) for key in ("tp", "fp", "fn")]
        differences.append(f1(*new) - f1(*old))
    differences.sort()
    result = {
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all 750 including row_ok=False",
        "model": "DeepSeek V4.1 Flash",
        "reference_sha256": base.sha(base.REFERENCE),
        "scorer": "finding_compact_concepts_v04",
        "replay_mode": "saved first responses",
        "repair_policy": "none",
        "r9_prediction_sha256": base.sha(R9 / "parsed_predictions.jsonl"),
        "r11_prediction_sha256": base.sha(R11 / "parsed_predictions.jsonl"),
        "r9": {key: sum(pair[0][key] for pair in rows) for key in ("tp", "fp", "fn")},
        "r11": {key: sum(pair[1][key] for pair in rows) for key in ("tp", "fp", "fn")},
        "bootstrap": {
            "seed": SEED,
            "samples": BOOTSTRAPS,
            "f1_difference_r11_minus_r9": f1(
                **{key: sum(pair[1][key] for pair in rows) for key in ("tp", "fp", "fn")}
            )
            - f1(**{key: sum(pair[0][key] for pair in rows) for key in ("tp", "fp", "fn")}),
            "percentile_95_interval": [
                differences[int(0.025 * BOOTSTRAPS)],
                differences[int(0.975 * BOOTSTRAPS)],
            ],
        },
        "native": {method: dict(counts) for method, counts in native.items()},
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    base.write_json(RESULT, result)
    print(json.dumps({"bootstrap": result["bootstrap"], "native": result["native"]}, indent=2))


if __name__ == "__main__":
    main()
