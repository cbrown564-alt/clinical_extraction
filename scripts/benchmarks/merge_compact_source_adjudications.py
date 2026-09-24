"""Merge three validated source reviews into a provisional compact v0.2 dev750 file."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from validate_compact_source_adjudication import validate

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_review_in_progress.json"
SCHEMA = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.v0_2.schema.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    base = json.loads(BASE.read_text())
    result = copy.deepcopy(base)
    rows = result["rows"]
    by_id = {row["source_id"]: row for row in rows}
    if len(rows) != 750 or len(by_id) != 750:
        raise ValueError("Base candidate must cover 750 unique source rows")
    packet_provenance: list[dict[str, Any]] = []
    reviewed_ids: set[str] = set()
    changed_claims = 0
    for index in range(1, 4):
        packet_path = ROOT / f"source_adjudication_packet_{index:02}.json"
        answer_path = ROOT / f"compact_source_adjudication_{index:02}.json"
        check = validate(packet_path, answer_path)
        packet = json.loads(packet_path.read_text())
        answer = json.loads(answer_path.read_text())
        packet_provenance.append(check)
        for source, decision in zip(packet["rows"], answer["rows"], strict=True):
            source_id = source["source_id"]
            if source_id in reviewed_ids:
                raise ValueError(f"Source reviewed twice: {source_id}")
            reviewed_ids.add(source_id)
            row = by_id[source_id]
            for key in ("source_id", "source_row_index", "source_sha256", "note"):
                if row[key] != source[key]:
                    raise ValueError(f"Candidate source changed: {source_id}/{key}")
            if row["annotation_state"] != "needs_review":
                raise ValueError(f"Expected needs_review before source adjudication: {source_id}")
            row["annotation_state"] = decision["annotation_state"]
            if decision["annotation_state"] == "complete":
                row.pop("review_reason", None)
            else:
                row["review_reason"] = decision["review_reason"]
            for claim, reviewed in zip(row["claims"], decision["claim_decisions"], strict=True):
                if claim["legacy_id"] != reviewed["legacy_id"]:
                    raise ValueError(f"Claim order changed: {source_id}")
                if (
                    claim["disposition"] != reviewed["disposition"]
                    or claim["candidate"] != reviewed["candidate"]
                ):
                    changed_claims += 1
                claim["disposition"] = reviewed["disposition"]
                claim["candidate"] = reviewed["candidate"]
                claim["source_adjudication"] = {
                    "packet": index,
                    "answer_sha256": sha256(answer_path),
                    "decision_reason": reviewed["decision_reason"],
                    "decision_evidence": reviewed["decision_evidence"],
                }
    if len(reviewed_ids) != 98:
        raise ValueError(f"Expected 98 reviewed rows, got {len(reviewed_ids)}")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    finding = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    states: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    null_primary = 0
    for row in rows:
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"Source hash changed: {row['source_id']}")
        state = row["annotation_state"]
        if state not in {"complete", "needs_review"}:
            raise ValueError(f"Invalid state: {row['source_id']}")
        if state == "needs_review" and not str(row.get("review_reason", "")).strip():
            raise ValueError(f"Unexplained needs_review row: {row['source_id']}")
        states[state] += 1
        for claim in row["claims"]:
            dispositions[claim["disposition"]] += 1
            candidate = claim["candidate"]
            if claim["disposition"] == "primary" and candidate is None:
                if state != "needs_review":
                    raise ValueError(f"Complete row has null primary: {row['source_id']}")
                null_primary += 1
            if candidate is not None:
                finding.validate(candidate)
                if any(span not in row["note"] for span in candidate["evidence"]):
                    raise ValueError(f"Non-exact evidence: {row['source_id']}")
    result["status"] = "source_adjudicated_provisional_not_accepted_gold"
    result["base_candidate"] = str(BASE)
    result["base_candidate_sha256"] = sha256(BASE)
    result["source_adjudication_packets"] = packet_provenance
    result["summary"] = {
        "rows": len(rows),
        "claims": sum(dispositions.values()),
        "source_adjudicated_rows": len(reviewed_ids),
        "source_adjudication_changed_claims": changed_claims,
        "dispositions": dict(dispositions),
        "annotation_states": dict(states),
        "null_primary_claims": null_primary,
        "scored_partition": "complete rows only; needs_review rows remain provisional",
    }
    output = ROOT / "candidate_v0_2_source_adjudicated_review_in_progress.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
