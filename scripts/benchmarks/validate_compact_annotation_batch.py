"""Check one GPT-6 Pro compact-annotation batch against its frozen input.

This checks identity, completeness, source occurrence and structure. It does not
adjudicate clinical correctness or update the accepted development reference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750/batches")
SCHEMA = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.schema.json"
)


def load_rows(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text())
    rows = obj.get("rows") if isinstance(obj, dict) else obj
    if not isinstance(rows, list):
        raise ValueError(f"Expected a rows array in {path}")
    return rows


def validate(batch: int, review_path: Path) -> dict[str, Any]:
    input_path = ROOT / f"batch_{batch:02d}_input.json"
    inputs = load_rows(input_path)
    review = json.loads(review_path.read_text())
    outputs = review.get("rows") if isinstance(review, dict) else review
    if not isinstance(outputs, list):
        raise ValueError(f"Expected a rows array in {review_path}")
    if len(inputs) != 150 or len(outputs) != 150:
        raise ValueError(f"Batch {batch}: expected 150 input and 150 output rows")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    finding_validator = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    dispositions: Counter[str] = Counter()
    states: Counter[str] = Counter()
    edits = 0
    omissions = 0
    unresolved_primary = 0
    for old, new in zip(inputs, outputs, strict=True):
        index = old["source_row_index"]
        for key in ("source_row_index", "source_id", "source_sha256"):
            if old[key] != new.get(key):
                raise ValueError(f"Batch {batch} row {index}: {key} changed")
        if new.get("note") != old["note"]:
            raise ValueError(f"Batch {batch} row {index}: source note changed")
        if hashlib.sha256(old["note"].encode()).hexdigest() != old["source_sha256"]:
            raise ValueError(f"Batch {batch} row {index}: input source hash failed")
        state = new.get("annotation_state")
        if state not in {"complete", "needs_review"}:
            raise ValueError(f"Batch {batch} row {index}: invalid annotation_state")
        states[state] += 1
        if state == "needs_review" and not new.get("review_reason"):
            raise ValueError(f"Batch {batch} row {index}: review_reason required")
        old_claims = old["claims"]
        new_claims = new.get("claims")
        if not isinstance(new_claims, list) or len(old_claims) != len(new_claims):
            raise ValueError(f"Batch {batch} row {index}: claim inventory changed")
        for before, after in zip(old_claims, new_claims, strict=True):
            ident = before["legacy_id"]
            if after.get("legacy_id") != ident:
                raise ValueError(f"Batch {batch} row {index}: legacy ID/order changed")
            if after.get("original_record") != before:
                raise ValueError(f"Batch {batch} row {index}/{ident}: original record changed")
            disposition = after.get("disposition")
            if disposition not in {"primary", "context", "exclude"}:
                raise ValueError(f"Batch {batch} row {index}/{ident}: disposition missing")
            dispositions[disposition] += 1
            if not isinstance(after.get("edit_reason"), str) or not after["edit_reason"].strip():
                raise ValueError(f"Batch {batch} row {index}/{ident}: edit_reason missing")
            candidate = after.get("candidate")
            if disposition == "primary" and candidate is None:
                if state != "needs_review":
                    raise ValueError(
                        f"Batch {batch} row {index}/{ident}: primary candidate missing"
                    )
                unresolved_primary += 1
            if candidate is not None:
                finding_validator.validate(candidate)
                if any(span not in old["note"] for span in candidate["evidence"]):
                    raise ValueError(f"Batch {batch} row {index}/{ident}: evidence not exact")
                if candidate != before["candidate"]:
                    edits += 1
        suggestions = new.get("possible_omissions", [])
        if not isinstance(suggestions, list):
            raise ValueError(f"Batch {batch} row {index}: possible_omissions is not a list")
        for suggestion in suggestions:
            if not isinstance(suggestion, dict):
                raise ValueError(f"Batch {batch} row {index}: malformed omission suggestion")
            quote = suggestion.get("quotation", suggestion.get("evidence"))
            if not isinstance(quote, str) or not quote or quote not in old["note"]:
                raise ValueError(f"Batch {batch} row {index}: omission evidence not exact")
            if (
                not isinstance(suggestion.get("rationale"), str)
                or not suggestion["rationale"].strip()
            ):
                raise ValueError(f"Batch {batch} row {index}: omission rationale missing")
            omissions += 1
    if isinstance(review, dict):
        input_by_index = {row["source_row_index"]: row for row in inputs}
        for suggestion in review.get("possible_omissions", []):
            row = input_by_index.get(suggestion.get("source_row_index"))
            if row is None or suggestion.get("source_id") != row["source_id"]:
                raise ValueError(f"Batch {batch}: omission source identity changed")
            if suggestion.get("source_sha256") != row["source_sha256"]:
                raise ValueError(f"Batch {batch}: omission source hash changed")
            quote = suggestion.get("quotation", suggestion.get("evidence"))
            if not isinstance(quote, str) or not quote or quote not in row["note"]:
                raise ValueError(f"Batch {batch}: omission evidence not exact")
            if not isinstance(suggestion.get("rationale"), str) or not suggestion[
                "rationale"
            ].strip():
                raise ValueError(f"Batch {batch}: omission rationale missing")
            omissions += 1
    return {
        "batch": batch,
        "input": str(input_path),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "review": str(review_path),
        "review_sha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
        "rows": len(outputs),
        "claims": sum(dispositions.values()),
        "dispositions": dict(dispositions),
        "annotation_states": dict(states),
        "candidate_edits": edits,
        "possible_omissions": omissions,
        "unresolved_primary_without_candidate": unresolved_primary,
        "checks": (
            "identity, order, legacy coverage, schema, exact evidence, "
            "disposition, review reasons"
        ),
        "clinical_adjudication": "not performed by this validator",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True, choices=range(1, 6))
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.batch, args.review)
    report = ROOT / f"batch_{args.batch:02d}_validation.json"
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
