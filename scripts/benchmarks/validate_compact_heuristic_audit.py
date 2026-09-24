"""Validate Pro's second dev750 omission-audit proposal against its packet."""

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


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def validate(packet_path: Path, answer_path: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text())
    answer = json.loads(answer_path.read_text())
    rows = packet["rows"]
    manifest = answer.get("source_manifest")
    decisions = answer.get("decisions")
    expected = [
        (row_index, lead_index, row, lead)
        for row_index, row in enumerate(rows)
        for lead_index, lead in enumerate(row["leads"])
    ]
    if answer.get("input_packet_sha256") != sha256(packet_path):
        raise ValueError("Input packet hash mismatch")
    if answer.get("input_candidate_sha256_as_declared_in_packet") != packet["candidate_sha256"]:
        raise ValueError("Candidate hash mismatch")
    if answer.get("schema_sha256") != sha256(SCHEMA):
        raise ValueError("Schema hash mismatch")
    if not isinstance(manifest, list) or len(manifest) != len(rows):
        raise ValueError("Source manifest coverage mismatch")
    if not isinstance(decisions, list) or len(decisions) != len(expected):
        raise ValueError("Lead coverage mismatch")
    if len(expected) != packet["lead_count"] or len(rows) != packet["source_rows"]:
        raise ValueError("Packet self-count mismatch")
    if answer.get("source_ids_in_packet_order") != [row["source_id"] for row in rows]:
        raise ValueError("Top-level source order mismatch")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    finding = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    counts: Counter[str] = Counter()
    for row_index, (row, listed) in enumerate(zip(rows, manifest, strict=True)):
        source_id = row["source_id"]
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"{source_id}: source hash mismatch")
        for key, value in (
            ("packet_row_index", row_index),
            ("source_id", source_id),
            ("source_row_index", row["source_row_index"]),
            ("source_sha256", row["source_sha256"]),
            ("input_annotation_state", row["annotation_state"]),
            ("lead_count", len(row["leads"])),
            ("existing_claim_ids", [c["legacy_id"] for c in row["existing_claims"]]),
            ("existing_claim_inventory_canonical_sha256", canonical_hash(row["existing_claims"])),
        ):
            if listed.get(key) != value:
                raise ValueError(f"{source_id}: manifest {key} mismatch")
    for index, (row_index, lead_index, row, lead) in enumerate(expected):
        decision = decisions[index]
        source_id = row["source_id"]
        for key, value in (
            ("decision_index", index),
            ("packet_row_index", row_index),
            ("lead_index_within_row", lead_index),
            ("source_id", source_id),
            ("source_row_index", row["source_row_index"]),
            ("source_sha256", row["source_sha256"]),
            ("source_annotation_state", row["annotation_state"]),
            ("quotation", lead["quotation"]),
            ("matched_phrase", lead["matched_phrase"]),
            ("lead_kind", lead["kind"]),
        ):
            if decision.get(key) != value:
                raise ValueError(f"{source_id}/lead {index}: {key} mismatch")
        if lead["quotation"] not in row["note"] or lead["matched_phrase"] not in lead[
            "quotation"
        ]:
            raise ValueError(f"{source_id}: packet quotation mismatch")
        disposition = decision.get("disposition")
        if disposition not in {
            "add_primary", "already_covered", "context_or_exclude", "unresolved"
        }:
            raise ValueError(f"{source_id}: invalid disposition")
        counts[disposition] += 1
        if not str(decision.get("decision_reason", "")).strip():
            raise ValueError(f"{source_id}: missing reason")
        evidence = decision.get("decision_evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(span, str) or not span or span not in row["note"]
            for span in evidence
        ):
            raise ValueError(f"{source_id}: decision evidence mismatch")
        ids = {claim["legacy_id"] for claim in row["existing_claims"]}
        overlap = decision.get("overlap_legacy_ids")
        if not isinstance(overlap, list) or any(value not in ids for value in overlap):
            raise ValueError(f"{source_id}: invalid overlap ID")
        record = decision.get("proposed_finding")
        if disposition == "add_primary":
            if record is None:
                raise ValueError(f"{source_id}: missing finding")
            finding.validate(record)
            if any(span not in row["note"] for span in record["evidence"]):
                raise ValueError(f"{source_id}: finding evidence mismatch")
        elif record is not None:
            raise ValueError(f"{source_id}: non-addition with finding")
        if disposition == "unresolved" and not str(
            decision.get("remaining_question", "")
        ).strip():
            raise ValueError(f"{source_id}: missing remaining question")
    if dict(counts) != answer.get("summary", {}).get("decision_counts"):
        raise ValueError("Summary counts mismatch")
    return {
        "packet_sha256": sha256(packet_path),
        "answer_sha256": sha256(answer_path),
        "source_rows": len(rows),
        "leads": len(decisions),
        "dispositions": dict(counts),
        "checks": (
            "source IDs/hashes/order, packet hash, schema, "
            "exact evidence, overlap attribution"
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
