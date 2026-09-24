"""Offline R9 development rescore with the versioned window-equivalence correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v04 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)
from scripts.benchmarks import score_compact_findings_v03 as base

PREDICTIONS = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/parsed_predictions.jsonl")
METADATA = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/run_metadata.json")
ORIGINAL = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/frozen_score/score.json"
)
OUTPUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/window_audit_v03_v3"
)
LOCAL = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/window_audit_v03_v3")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--local", type=Path, default=LOCAL)
    args = parser.parse_args()
    if args.output.exists() or args.local.exists():
        raise FileExistsError("Versioned output exists; preserve the prior rescore")
    references, manifest = base.load_reference()
    predictions = [json.loads(line) for line in PREDICTIONS.read_text().splitlines() if line]
    by_index = {row["source_row_index"]: row for row in predictions}
    if len(predictions) != 750 or len(by_index) != 750:
        raise ValueError("Prediction coverage must be 750 unique rows")
    run_metadata = json.loads(METADATA.read_text())
    if (
        run_metadata["prompt_version"] != r9.VERSION
        or run_metadata["prompt_revision"] != r9.REVISION
    ):
        raise ValueError("R9 prompt identity changed")
    validator = Draft202012Validator(json.loads(r9.SCHEMA_PATH.read_text()))
    scores: list[dict[str, Any]] = []
    local_rows = []
    invalid: dict[str, int] = {}
    for ref in references:
        pred = by_index.pop(ref["source_row_index"])
        if any(pred[key] != ref[key] for key in ("source_id", "source_sha256")):
            raise ValueError(f"Source identity mismatch: {ref['source_row_index']}")
        findings, reason = base.validate_response(pred.get("response"), ref["note"], validator)
        score = scorer.score_letter(ref["note"], ref["findings"], findings)
        scores.append(score)
        if reason:
            invalid[reason] = invalid.get(reason, 0) + 1
        local_rows.append(
            {
                "source_row_index": ref["source_row_index"],
                "source_id": ref["source_id"],
                "source_sha256": ref["source_sha256"],
                "score": score,
                "invalid_reason": reason,
            }
        )
    if by_index:
        raise ValueError("Unmatched prediction rows")
    summary = scorer.aggregate(scores)
    summary.update(manifest)
    summary["scorer"] = scorer.VERSION
    summary["scorer_source_sha256"] = hashlib.sha256(Path(scorer.__file__).read_bytes()).hexdigest()
    summary["prediction_sha256"] = base.sha(PREDICTIONS)
    summary["run_metadata_sha256"] = base.sha(METADATA)
    summary["reference_sha256"] = base.sha(base.REFERENCE)
    summary["invalid_reasons"] = invalid
    summary["run_metadata"] = run_metadata
    summary["original_score_sha256"] = base.sha(ORIGINAL)
    args.local.mkdir(parents=True)
    args.output.mkdir(parents=True)
    base.write_jsonl(args.local / "per_letter.jsonl", local_rows)
    base.write_json(args.output / "score.json", summary)
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "scorer",
                    "tp",
                    "fp",
                    "fn",
                    "precision",
                    "recall",
                    "f1",
                    "source_aligned",
                    "components",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
