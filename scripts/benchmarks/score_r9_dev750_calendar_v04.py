"""Rescore saved R9 dev750 responses with the R11 calendar-window scorer."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v08 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as prompt,
)
from scripts.benchmarks import score_compact_findings_v03 as base

PREDICTIONS = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/parsed_predictions.jsonl")
LOCAL = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/calendar_window_v04")
RESULT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/calendar_window_v04"
)


def main() -> None:
    if LOCAL.exists() or RESULT.exists():
        raise FileExistsError("R9 calendar-window replay exists")
    references, manifest = base.load_reference()
    predictions = {
        row["source_row_index"]: row for row in (json.loads(line) for line in PREDICTIONS.open())
    }
    if len(predictions) != len(references):
        raise ValueError("R9 predictions do not cover dev750")
    validator = Draft202012Validator(json.loads(prompt.SCHEMA_PATH.read_text()))
    scores = []
    per_letter = []
    invalid: dict[str, int] = {}
    for ref in references:
        pred = predictions.pop(ref["source_row_index"])
        if any(pred[key] != ref[key] for key in ("source_id", "source_sha256")):
            raise ValueError(f"Source mismatch: {ref['source_id']}")
        findings, error = base.validate_response(pred.get("response"), ref["note"], validator)
        if error:
            invalid[error] = invalid.get(error, 0) + 1
        score = scorer.score_letter(ref["note"], ref["findings"], findings)
        scores.append(score)
        per_letter.append(
            {
                "source_id": ref["source_id"],
                "source_row_index": ref["source_row_index"],
                "source_sha256": ref["source_sha256"],
                "score": score,
                "invalid_reason": error,
            }
        )
    if predictions:
        raise ValueError("Unexpected R9 predictions")
    LOCAL.mkdir(parents=True)
    RESULT.mkdir(parents=True)
    base.write_jsonl(LOCAL / "per_letter.jsonl", per_letter)
    aggregate = scorer.aggregate(scores)
    aggregate.update(manifest)
    aggregate.update(
        {
            "scorer": scorer.VERSION,
            "scorer_sha256": base.sha(Path(scorer.__file__)),
            "prediction_sha256": base.sha(PREDICTIONS),
            "reference_sha256": base.sha(base.REFERENCE),
            "model": "deepseek-flash",
            "prompt_version": prompt.VERSION,
            "prompt_revision": prompt.REVISION,
            "replay_mode": "saved first responses",
            "repair_policy": "none",
            "invalid_reasons": invalid,
        }
    )
    base.write_json(RESULT / "score.json", aggregate)
    print(json.dumps({k: aggregate[k] for k in ("tp", "fp", "fn", "f1")}))


if __name__ == "__main__":
    main()
