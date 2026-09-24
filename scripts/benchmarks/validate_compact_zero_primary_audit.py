"""Validate the zero-primary Pro audit against its immutable source packet."""

from __future__ import annotations

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
    rows = packet["rows"]
    decisions = answer["decisions"]
    if answer["input_packet_sha256"] != sha256(packet_path):
        raise ValueError("Packet hash mismatch")
    if answer["input_candidate_sha256_as_supplied"] != packet["candidate_sha256"]:
        raise ValueError("Candidate hash mismatch")
    if len(rows) != packet["source_rows"] or len(decisions) != len(rows):
        raise ValueError("Row coverage mismatch")
    if answer["coverage"]["source_ids_in_packet_order"] != [r["source_id"] for r in rows]:
        raise ValueError("Source order mismatch")
    schema = json.loads(SCHEMA.read_text())
    finding = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    counts: Counter[str] = Counter()
    for index, (row, decision) in enumerate(zip(rows, decisions, strict=True)):
        source_id = row["source_id"]
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"{source_id}: source hash mismatch")
        for key, value in (
            ("packet_row_index", index),
            ("source_id", source_id),
            ("source_row_index", row["source_row_index"]),
            ("source_sha256", row["source_sha256"]),
            ("quotation", row["quotation"]),
            ("lead_kind", row["lead_kind"]),
            ("input_annotation_state", row["annotation_state"]),
            ("existing_inventory_legacy_ids", [c["legacy_id"] for c in row["existing_claims"]]),
        ):
            if decision.get(key) != value:
                raise ValueError(f"{source_id}: {key} mismatch")
        if row["quotation"] not in row["note"]:
            raise ValueError(f"{source_id}: input quotation mismatch")
        disposition = decision["disposition"]
        if disposition not in {
            "add_primary", "already_covered", "context_or_exclude", "unresolved"
        }:
            raise ValueError(f"{source_id}: invalid disposition")
        counts[disposition] += 1
        if not str(decision.get("decision_reason", "")).strip():
            raise ValueError(f"{source_id}: missing reason")
        evidence = decision.get("decision_evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(span, str) or not span or span not in row["note"] for span in evidence
        ):
            raise ValueError(f"{source_id}: decision evidence mismatch")
        ids = {c["legacy_id"] for c in row["existing_claims"]}
        overlap = decision.get("overlap_legacy_ids")
        if not isinstance(overlap, list) or any(value not in ids for value in overlap):
            raise ValueError(f"{source_id}: overlap ID mismatch")
        record = decision.get("proposed_finding")
        if disposition == "add_primary":
            finding.validate(record)
            if any(span not in row["note"] for span in record["evidence"]):
                raise ValueError(f"{source_id}: finding evidence mismatch")
        elif record is not None:
            raise ValueError(f"{source_id}: non-addition has finding")
        if disposition == "unresolved" and not str(decision.get("remaining_question", "")).strip():
            raise ValueError(f"{source_id}: unresolved question missing")
    if dict(counts) != answer["disposition_counts"]:
        raise ValueError("Disposition count mismatch")
    return {
        "packet_sha256": sha256(packet_path),
        "answer_sha256": sha256(answer_path),
        "source_rows": len(rows),
        "dispositions": dict(counts),
        "checks": "packet, IDs/hashes/order, schema, quotations, evidence, attribution",
        "clinical_adjudication": "not performed by this validator",
    }


if __name__ == "__main__":
    root = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
    result = validate(
        root / "zero_primary_source_audit_packet.json",
        root / "compact_zero_primary_source_audit_proposal.json",
    )
    print(json.dumps(result, indent=2))
