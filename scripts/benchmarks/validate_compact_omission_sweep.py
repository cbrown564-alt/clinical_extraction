"""Check a Pro omission proposal against its immutable source packet.

This checks provenance and record shape, not whether a proposed claim is true.
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


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def validate(packet_path: Path, answer_path: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text())
    answer = json.loads(answer_path.read_text())
    rows = packet["rows"]
    decisions = answer.get("suggestion_decisions")
    manifest = answer.get("source_manifest")
    if answer.get("input_packet_sha256") != sha256(packet_path):
        raise ValueError("Input packet hash mismatch")
    if answer.get("input_candidate_sha256_as_supplied") != packet["candidate_sha256"]:
        raise ValueError("Candidate hash mismatch")
    if answer.get("schema_sha256") != sha256(SCHEMA):
        raise ValueError("Schema hash mismatch")
    if answer.get("accepted_gold") is not False:
        raise ValueError("Proposal must not claim accepted gold")
    if not isinstance(manifest, list) or len(manifest) != len(rows):
        raise ValueError("Source manifest coverage mismatch")
    expected = [
        (row_index, suggestion_index, row, suggestion)
        for row_index, row in enumerate(rows)
        for suggestion_index, suggestion in enumerate(row["possible_omissions"])
    ]
    if not isinstance(decisions, list) or len(decisions) != len(expected):
        raise ValueError("Suggestion coverage mismatch")
    if len(expected) != packet["suggestions"] or len(rows) != packet["source_rows"]:
        raise ValueError("Packet self-count mismatch")
    finding_schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(finding_schema)
    finding = Draft202012Validator(
        {"$defs": finding_schema["$defs"], "$ref": "#/$defs/finding"}
    )
    counts: Counter[str] = Counter()
    additions = 0
    for row_index, (row, listed) in enumerate(zip(rows, manifest, strict=True)):
        source_id = row["source_id"]
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"{source_id}: packet note hash mismatch")
        for key in ("source_id", "source_row_index", "source_sha256"):
            if listed.get(key) != row[key]:
                raise ValueError(f"{source_id}: manifest {key} mismatch")
        if listed.get("input_annotation_state") != row["annotation_state"]:
            raise ValueError(f"{source_id}: manifest annotation state mismatch")
        if listed.get("input_existing_claims_count") != len(row["existing_claims"]):
            raise ValueError(f"{source_id}: existing claim count mismatch")
        if listed.get("input_existing_claims_canonical_sha256") != canonical_hash(
            row["existing_claims"]
        ):
            raise ValueError(f"{source_id}: existing claim hash mismatch")
        expected_indices = [
            index + 1 for index, (i, _, _, _) in enumerate(expected) if i == row_index
        ]
        if listed.get("suggestion_decision_indices") != expected_indices:
            raise ValueError(f"{source_id}: suggestion manifest indices mismatch")
    for index, (row_index, suggestion_index, row, suggestion) in enumerate(
        expected, start=1
    ):
        decision = decisions[index - 1]
        source_id = row["source_id"]
        for key, expected_value in (
            ("decision_index", index),
            ("source_row_packet_index", row_index),
            ("suggestion_index_within_source", suggestion_index),
            ("source_id", source_id),
            ("source_row_index", row["source_row_index"]),
            ("source_sha256", row["source_sha256"]),
            ("source_annotation_state", row["annotation_state"]),
            ("quotation", suggestion["quotation"]),
        ):
            if decision.get(key) != expected_value:
                raise ValueError(f"{source_id}/suggestion {index}: {key} mismatch")
        if suggestion["quotation"] not in row["note"]:
            raise ValueError(f"{source_id}: packet quotation not exact")
        disposition = decision.get("disposition")
        if disposition not in {
            "add_primary", "already_covered", "context_or_exclude", "unresolved"
        }:
            raise ValueError(f"{source_id}: invalid disposition")
        counts[disposition] += 1
        if not str(decision.get("decision_reason", "")).strip():
            raise ValueError(f"{source_id}: missing decision reason")
        evidence = decision.get("decision_evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(span, str) or not span or span not in row["note"]
            for span in evidence
        ):
            raise ValueError(f"{source_id}: decision evidence is not exact")
        overlap = decision.get("overlap_legacy_ids")
        ids = {claim["legacy_id"] for claim in row["existing_claims"]}
        if not isinstance(overlap, list) or any(legacy_id not in ids for legacy_id in overlap):
            raise ValueError(f"{source_id}: invalid overlap legacy ID")
        candidate = decision.get("proposed_finding")
        if disposition == "add_primary":
            if candidate is None:
                raise ValueError(f"{source_id}: missing proposed finding")
            finding.validate(candidate)
            if any(span not in row["note"] for span in candidate["evidence"]):
                raise ValueError(f"{source_id}: proposed evidence is not exact")
            additions += 1
        elif candidate is not None:
            raise ValueError(f"{source_id}: non-addition has proposed finding")
        if disposition == "unresolved" and not str(
            decision.get("remaining_question", "")
        ).strip():
            raise ValueError(f"{source_id}: missing remaining question")
    if dict(counts) != answer.get("summary", {}).get("suggestion_decisions_by_disposition"):
        raise ValueError("Decision summary mismatch")
    if additions != answer.get("summary", {}).get("proposed_findings"):
        raise ValueError("Addition summary mismatch")
    return {
        "packet_sha256": sha256(packet_path),
        "answer_sha256": sha256(answer_path),
        "source_rows": len(rows),
        "suggestions": len(decisions),
        "dispositions": dict(counts),
        "proposed_additions": additions,
        "checks": (
            "packet and candidate hashes, source IDs/hashes/order, "
            "quotations, schema, evidence, attribution"
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
