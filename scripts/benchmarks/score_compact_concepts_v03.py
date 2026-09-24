"""Build a versioned scored-concept reference and exploratory saved-R9 rescore.

This is a development candidate. Its flagged projections need source review
before anyone uses the aggregate as a paper result. No model calls or repairs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    compact_scored_terms_v03 as terms,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v07 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)
from scripts.benchmarks import score_compact_findings_v03 as base

PREDICTIONS = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/parsed_predictions.jsonl")
METADATA = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/run_metadata.json")
LOCAL = Path("runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate")
RESULT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/"
    "dev750/concepts_v03_policy_candidate"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scored_claim(finding: dict[str, Any], origin: str) -> dict[str, Any]:
    event = terms.event_key(finding["event"])
    restriction = terms.restriction_key(finding)
    flags = []
    if event[0] == "named" and not event[1]:
        flags.append("named_without_standard_type")
    if event[0] == "combined" and len(event[1]) < 2:
        flags.append("combined_with_fewer_than_two_standard_types")
    if finding.get("restriction") and not restriction:
        flags.append("literal_restriction_not_scored")
    return {
        "origin_id": origin,
        "event_scope": event[0],
        "scored_event_types": list(event[1]),
        "scored_restrictions": list(restriction),
        "literal_event_label": finding["event"]["label"],
        "literal_restriction": finding.get("restriction"),
        "review_flags": flags,
    }


def main() -> None:
    if LOCAL.exists() or RESULT.exists():
        raise FileExistsError("Candidate output exists; preserve prior projection")
    references, manifest = base.load_reference()
    predictions = [json.loads(line) for line in PREDICTIONS.read_text().splitlines() if line]
    by_index = {row["source_row_index"]: row for row in predictions}
    if len(predictions) != 750 or len(by_index) != 750:
        raise ValueError("Prediction file must cover 750 unique rows")
    metadata = json.loads(METADATA.read_text())
    if metadata["prompt_version"] != r9.VERSION or metadata["prompt_revision"] != r9.REVISION:
        raise ValueError("Wrong saved R9 prompt")
    validator = Draft202012Validator(json.loads(r9.SCHEMA_PATH.read_text()))
    scored_rows = []
    per_letter = []
    review_queue = []
    score_rows = []
    invalid: dict[str, int] = {}
    for ref in references:
        pred = by_index.pop(ref["source_row_index"])
        if any(pred[k] != ref[k] for k in ("source_id", "source_sha256")):
            raise ValueError(f"Source identity mismatch: {ref['source_id']}")
        claims = [
            scored_claim(finding, origin)
            for finding, origin in zip(ref["findings"], ref["origin_ids"], strict=True)
        ]
        scored_rows.append(
            {
                "source_row_index": ref["source_row_index"],
                "source_id": ref["source_id"],
                "source_sha256": ref["source_sha256"],
                "scored_claims": claims,
            }
        )
        for claim in claims:
            if claim["review_flags"]:
                review_queue.append(
                    {
                        "source_row_index": ref["source_row_index"],
                        "source_id": ref["source_id"],
                        "source_sha256": ref["source_sha256"],
                        **claim,
                    }
                )
        findings, error = base.validate_response(pred.get("response"), ref["note"], validator)
        if error:
            invalid[error] = invalid.get(error, 0) + 1
        score = scorer.score_letter(ref["note"], ref["findings"], findings)
        score_rows.append(score)
        per_letter.append(
            {
                "source_row_index": ref["source_row_index"],
                "source_id": ref["source_id"],
                "source_sha256": ref["source_sha256"],
                "score": score,
                "invalid_reason": error,
            }
        )
    if by_index:
        raise ValueError("Unmatched prediction rows")
    LOCAL.mkdir(parents=True)
    RESULT.mkdir(parents=True)
    base.write_jsonl(LOCAL / "scored_reference.jsonl", scored_rows)
    base.write_jsonl(LOCAL / "reference_review_queue.jsonl", review_queue)
    base.write_jsonl(LOCAL / "per_letter.jsonl", per_letter)
    aggregate = scorer.aggregate(score_rows)
    aggregate.update(manifest)
    aggregate.update(
        {
            "scorer": scorer.VERSION,
            "scorer_source_sha256": sha(Path(scorer.__file__)),
            "term_dictionary": terms.VERSION,
            "term_dictionary_sha256": sha(Path(terms.__file__)),
            "reference_projection_sha256": sha(LOCAL / "scored_reference.jsonl"),
            "review_queue_sha256": sha(LOCAL / "reference_review_queue.jsonl"),
            "reference_projection_status": (
                "development candidate; flagged mappings require source review"
            ),
            "prediction_sha256": sha(PREDICTIONS),
            "run_metadata_sha256": sha(METADATA),
            "reference_sha256": sha(base.REFERENCE),
            "invalid_reasons": invalid,
            "run_metadata": metadata,
            "flagged_reference_claims": len(review_queue),
        }
    )
    base.write_json(RESULT / "score.json", aggregate)
    print(
        json.dumps(
            {
                k: aggregate[k]
                for k in (
                    "scorer",
                    "tp",
                    "fp",
                    "fn",
                    "precision",
                    "recall",
                    "f1",
                    "flagged_reference_claims",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
