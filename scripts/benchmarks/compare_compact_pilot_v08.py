"""Replay the fixed 16-row R9/R10/R11 pilot with one calendar-window scorer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v08 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r11 as prompt,
)
from scripts.benchmarks import run_r11_dev750 as runner
from scripts.benchmarks import score_compact_findings_v03 as base

RESULT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11/"
    "dev750_pilot16/calendar_window_v04_comparison.json"
)
SOURCES = {
    "R9": Path("runs/one_shot_frequency_v2_measurements_r9/dev750/parsed_predictions.jsonl"),
    "R10": Path(
        "runs/one_shot_frequency_v2_measurements_r10/dev750_pilot16/parsed_predictions.jsonl"
    ),
    "R11": Path(
        "runs/one_shot_frequency_v2_measurements_r11/dev750_pilot16/parsed_predictions.jsonl"
    ),
}


def main() -> None:
    if RESULT.exists():
        raise FileExistsError(RESULT)
    references, _ = base.load_reference()
    refs = [row for row in references if str(row["source_id"]) in runner.PILOT_IDS]
    if len(refs) != len(runner.PILOT_IDS):
        raise ValueError("Pilot reference coverage changed")
    validator = Draft202012Validator(json.loads(prompt.SCHEMA_PATH.read_text()))
    output: dict[str, Any] = {
        "dataset": "Gan 2026 synthetic",
        "split": "selected dev750 pilot16",
        "selection": list(runner.PILOT_IDS),
        "scorer": scorer.VERSION,
        "scorer_sha256": base.sha(Path(scorer.__file__)),
        "reference_sha256": base.sha(base.REFERENCE),
        "replay_mode": "saved first responses",
        "repair_policy": "none",
        "models": {},
    }
    for name, path in SOURCES.items():
        predictions = {
            row["source_row_index"]: row for row in (json.loads(line) for line in path.open())
        }
        scores = []
        per_letter = []
        invalid: dict[str, int] = {}
        for ref in refs:
            pred = predictions[ref["source_row_index"]]
            if any(pred[key] != ref[key] for key in ("source_id", "source_sha256")):
                raise ValueError(f"Source mismatch: {name} {ref['source_id']}")
            findings, error = base.validate_response(pred.get("response"), ref["note"], validator)
            if error:
                invalid[error] = invalid.get(error, 0) + 1
            score = scorer.score_letter(ref["note"], ref["findings"], findings)
            scores.append(score)
            per_letter.append(
                {
                    "source_id": ref["source_id"],
                    "tp": score["tp"],
                    "fp": score["fp"],
                    "fn": score["fn"],
                    "invalid_reason": error,
                }
            )
        aggregate = scorer.aggregate(scores)
        output["models"][name] = {
            "prediction_sha256": base.sha(path),
            "tp": aggregate["tp"],
            "fp": aggregate["fp"],
            "fn": aggregate["fn"],
            "precision": aggregate["precision"],
            "recall": aggregate["recall"],
            "f1": aggregate["f1"],
            "invalid_reasons": invalid,
            "per_letter": per_letter,
        }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    base.write_json(RESULT, output)
    print(
        json.dumps(
            {
                name: {k: row[k] for k in ("tp", "fp", "fn", "f1")}
                for name, row in output["models"].items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
