"""Validate dev750 compact candidate provenance and score partition.

Structural and exact-evidence checks cannot establish clinical correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
SCHEMA = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.v0_2.schema.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(candidate_path: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text())
    if candidate["schema_sha256"] != sha256(SCHEMA):
        raise ValueError("Candidate schema hash mismatch")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    finding = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    source_rows = []
    for batch in range(1, 6):
        packet = json.loads((ROOT / "batches" / f"batch_{batch:02d}_input.json").read_text())
        source_rows.extend(packet["rows"])
    rows = candidate["rows"]
    if len(rows) != len(source_rows) or len(rows) != 750:
        raise ValueError("Source row coverage mismatch")
    if len({row["source_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate source IDs")
    states: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    added = 0
    primary_complete = 0
    null_primary = 0
    for source, row in zip(source_rows, rows, strict=True):
        source_id = source["source_id"]
        for key in ("source_id", "source_row_index", "source_sha256", "note"):
            if row[key] != source[key]:
                raise ValueError(f"{source_id}: source {key} mismatch")
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"{source_id}: note hash mismatch")
        state = row["annotation_state"]
        if state not in {"complete", "needs_review"}:
            raise ValueError(f"{source_id}: invalid annotation state")
        if state == "needs_review" and not str(row.get("review_reason", "")).strip():
            raise ValueError(f"{source_id}: missing review reason")
        states[state] += 1
        before = source["claims"]
        after = row["claims"]
        if len(after) != len(before):
            raise ValueError(f"{source_id}: legacy claim coverage mismatch")
        for old, claim in zip(before, after, strict=True):
            legacy_id = old["legacy_id"]
            if claim["legacy_id"] != legacy_id or claim["original_record"] != old:
                raise ValueError(f"{source_id}/{legacy_id}: original claim changed")
            disposition = claim["disposition"]
            if disposition not in {"primary", "context", "exclude"}:
                raise ValueError(f"{source_id}/{legacy_id}: invalid disposition")
            dispositions[disposition] += 1
            record = claim.get("candidate")
            if disposition == "primary" and record is None:
                null_primary += 1
                if state != "needs_review":
                    raise ValueError(f"{source_id}/{legacy_id}: complete primary is null")
            if record is not None:
                finding.validate(record)
                if any(span not in row["note"] for span in record["evidence"]):
                    raise ValueError(f"{source_id}/{legacy_id}: evidence is not exact")
            if disposition == "primary" and state == "complete":
                primary_complete += 1
        additions = row.get("added_claims", [])
        if state == "complete" and row.get("unresolved_omission_suggestions"):
            raise ValueError(f"{source_id}: unresolved omission on complete row")
        for claim in additions:
            if claim.get("disposition") != "primary":
                raise ValueError(f"{source_id}: added claim not primary")
            record = claim["candidate"]
            finding.validate(record)
            if any(span not in row["note"] for span in record["evidence"]):
                raise ValueError(f"{source_id}: added evidence is not exact")
            if claim.get("quotation") not in row["note"]:
                raise ValueError(f"{source_id}: addition quotation is not exact")
            if not claim.get("proposal_sha256") or not claim.get("decision_index"):
                raise ValueError(f"{source_id}: addition attribution missing")
            added += 1
            if state == "complete":
                primary_complete += 1
    if candidate["summary"]["claims"] != sum(dispositions.values()):
        raise ValueError("Legacy claim summary mismatch")
    if candidate["summary"]["annotation_states"] != dict(states):
        raise ValueError("Annotation state summary mismatch")
    if candidate["summary"].get("added_primary_claims", 0) != added:
        raise ValueError("Added claim summary mismatch")
    return {
        "candidate": str(candidate_path),
        "candidate_sha256": sha256(candidate_path),
        "source_rows": len(rows),
        "legacy_claims": sum(dispositions.values()),
        "legacy_dispositions": dict(dispositions),
        "added_primary_claims": added,
        "annotation_states": dict(states),
        "complete_row_primary_records": primary_complete,
        "null_primary_claims_on_unresolved_rows": null_primary,
        "checks": (
            "source IDs/hashes/order, original records, claim coverage/order, "
            "v0.2 schema, exact evidence, score partition and addition attribution"
        ),
        "clinical_adjudication": "not performed by this validator",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.candidate), indent=2))


if __name__ == "__main__":
    main()
