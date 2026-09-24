"""Validate one Pro source-adjudication result against its local review packet.

Checks provenance, exact evidence, and record shape, not clinical correctness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.v0_2.schema.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(packet_path: Path, answer_path: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text())
    answer = json.loads(answer_path.read_text())
    source_rows = packet["rows"]
    decisions = answer.get("rows")
    if not isinstance(decisions, list) or len(decisions) != len(source_rows):
        raise ValueError("Output must contain every packet row exactly once")
    if answer.get("input_packet_sha256") != sha256(packet_path):
        raise ValueError("Input packet SHA-256 mismatch")
    if answer.get("source_ids") != [row["source_id"] for row in source_rows]:
        raise ValueError("Top-level source ID order mismatch")
    attached_schema_hash = answer.get("schema_sha256")
    if attached_schema_hash is None:
        matches = [
            item.get("sha256")
            for item in answer.get("input_files", [])
            if item.get("role") == "schema"
        ]
        attached_schema_hash = matches[0] if len(matches) == 1 else None
    if attached_schema_hash is None:
        attached_schema_hash = answer.get("inputs", {}).get("schema", {}).get("sha256")
    if attached_schema_hash != sha256(SCHEMA):
        raise ValueError("Schema SHA-256 mismatch")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    finding = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    states: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    changed_claims = 0
    for before, after in zip(source_rows, decisions, strict=True):
        source_id = before["source_id"]
        for key in ("source_id", "source_sha256"):
            if after.get(key) != before[key]:
                raise ValueError(f"{source_id}: {key} changed")
        if hashlib.sha256(before["note"].encode()).hexdigest() != before["source_sha256"]:
            raise ValueError(f"{source_id}: source note SHA-256 mismatch")
        state = after.get("annotation_state")
        if state not in {"complete", "needs_review"}:
            raise ValueError(f"{source_id}: invalid annotation_state")
        if state == "needs_review" and not str(after.get("review_reason", "")).strip():
            raise ValueError(f"{source_id}: needs_review requires review_reason")
        states[state] += 1
        claims = before["claims"]
        claim_decisions = after.get("claim_decisions")
        if not isinstance(claim_decisions, list) or len(claim_decisions) != len(claims):
            raise ValueError(f"{source_id}: claim inventory changed")
        for old, new in zip(claims, claim_decisions, strict=True):
            legacy_id = old["legacy_id"]
            if new.get("legacy_id") != legacy_id:
                raise ValueError(f"{source_id}: legacy claim order changed")
            disposition = new.get("disposition")
            if disposition not in {"primary", "context", "exclude"}:
                raise ValueError(f"{source_id}/{legacy_id}: invalid disposition")
            dispositions[disposition] += 1
            if not str(new.get("decision_reason", "")).strip():
                raise ValueError(f"{source_id}/{legacy_id}: missing decision reason")
            evidence = new.get("decision_evidence")
            if not isinstance(evidence, list) or not evidence:
                raise ValueError(f"{source_id}/{legacy_id}: decision evidence required")
            if any(not isinstance(span, str) or span not in before["note"] for span in evidence):
                raise ValueError(f"{source_id}/{legacy_id}: decision evidence is not exact")
            candidate = new.get("candidate")
            if disposition == "primary" and candidate is None and state != "needs_review":
                raise ValueError(f"{source_id}/{legacy_id}: complete primary record is null")
            if candidate is not None:
                finding.validate(candidate)
                if any(span not in before["note"] for span in candidate["evidence"]):
                    raise ValueError(f"{source_id}/{legacy_id}: evidence is not exact")
            if disposition != old["disposition"] or candidate != old["candidate"]:
                changed_claims += 1
    return {
        "packet": str(packet_path),
        "packet_sha256": sha256(packet_path),
        "answer": str(answer_path),
        "answer_sha256": sha256(answer_path),
        "rows": len(decisions),
        "claims": sum(dispositions.values()),
        "dispositions": dict(dispositions),
        "annotation_states": dict(states),
        "changed_claims": changed_claims,
        "checks": (
            "packet hash, source IDs/hashes/order, claim IDs/order, "
            "schema, exact evidence, reasons"
        ),
        "clinical_adjudication": "not performed by this validator",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--answer", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.packet, args.answer), indent=2))


if __name__ == "__main__":
    main()
