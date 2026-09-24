"""Build the provisional dev750 compact v0.2 candidate from reviewed batches.

Only the 18 full-source null-primary decisions in the policy proposal are
applied here. All other needs_review rows stay unresolved. This never modifies
the frozen reference or the five returned review batches.
"""

from __future__ import annotations

import copy
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


def main() -> None:
    proposal_path = ROOT / "compact_policy_adjudication_proposal.json"
    packet_path = ROOT / "adjudication_policy_packet.json"
    proposal = json.loads(proposal_path.read_text())
    if proposal["input_packet_sha256"] != sha256(packet_path):
        raise ValueError("Policy proposal packet hash mismatch")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})

    rows: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []
    for batch in range(1, 6):
        review_path = ROOT / "batches" / f"batch_{batch:02d}_review.json"
        input_path = ROOT / "batches" / f"batch_{batch:02d}_input.json"
        batch_rows = json.loads(review_path.read_text())["rows"]
        input_rows = json.loads(input_path.read_text())["rows"]
        if len(batch_rows) != 150 or len(input_rows) != 150:
            raise ValueError(f"Batch {batch} does not contain 150 rows")
        rows.extend(copy.deepcopy(batch_rows))
        inputs.extend(input_rows)

    applied: list[dict[str, str]] = []
    recommendations = proposal["row_recommendations"]
    for row in rows:
        source_id = row["source_id"]
        if source_id not in recommendations:
            continue
        recommendation = recommendations[source_id]
        if row["source_sha256"] != recommendation["source_sha256"]:
            raise ValueError(f"Source hash changed for {source_id}")
        for claim in row["claims"]:
            legacy_id = claim["legacy_id"]
            decision = recommendation["claims"][legacy_id]
            if not decision["is_target_null_primary"]:
                continue
            if claim["disposition"] != "primary" or claim["candidate"] is not None:
                raise ValueError(f"Expected a null primary: {source_id}/{legacy_id}")
            action = decision["recommendation"]
            if action == "recommend_schema_change":
                candidate = decision["compact_record"]
                validator.validate(candidate)
                if any(span not in row["note"] for span in candidate["evidence"]):
                    raise ValueError(f"Evidence mismatch: {source_id}/{legacy_id}")
                claim["candidate"] = candidate
            elif action == "downgrade_to_context":
                claim["disposition"] = "context"
            elif action != "leave_unresolved":
                raise ValueError(f"Unexpected decision {action}: {source_id}/{legacy_id}")
            claim["v0_2_adjudication"] = {
                "action": action,
                "source": "compact_policy_adjudication_proposal.json",
                "policy_reason": decision["policy_reason"],
            }
            applied.append({"source_id": source_id, "legacy_id": legacy_id, "action": action})

    if len(applied) != 18:
        raise ValueError(f"Expected 18 target decisions, got {len(applied)}")
    if len(rows) != 750 or len({r["source_id"] for r in rows}) != 750:
        raise ValueError("Candidate row coverage failed")
    if len(inputs) != 750:
        raise ValueError("Input row coverage failed")
    dispositions: Counter[str] = Counter()
    states: Counter[str] = Counter()
    null_primary = 0
    for old, row in zip(inputs, rows, strict=True):
        for key in ("source_row_index", "source_id", "source_sha256", "note"):
            if row[key] != old[key]:
                raise ValueError(f"Source identity changed: {row['source_id']}/{key}")
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"Source hash failed: {row['source_id']}")
        states[row["annotation_state"]] += 1
        if len(old["claims"]) != len(row["claims"]):
            raise ValueError(f"Claim inventory changed: {row['source_id']}")
        for before, claim in zip(old["claims"], row["claims"], strict=True):
            if claim["legacy_id"] != before["legacy_id"] or claim["original_record"] != before:
                raise ValueError(f"Legacy claim changed: {row['source_id']}")
            dispositions[claim["disposition"]] += 1
            candidate = claim["candidate"]
            if candidate is None:
                if claim["disposition"] == "primary":
                    if row["annotation_state"] != "needs_review":
                        raise ValueError(f"Complete row with null primary: {row['source_id']}")
                    null_primary += 1
            else:
                validator.validate(candidate)
                if any(span not in row["note"] for span in candidate["evidence"]):
                    raise ValueError(f"Candidate evidence mismatch: {row['source_id']}")

    result = {
        "policy": "compact_primary_finding_candidate_v0_2",
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "status": "review_in_progress_not_accepted_gold",
        "schema": str(SCHEMA),
        "schema_sha256": sha256(SCHEMA),
        "proposal": str(proposal_path),
        "proposal_sha256": sha256(proposal_path),
        "applied_target_decisions": applied,
        "summary": {
            "rows": len(rows),
            "claims": sum(dispositions.values()),
            "dispositions": dict(dispositions),
            "annotation_states": dict(states),
            "null_primary_claims": null_primary,
        },
        "rows": rows,
    }
    output = ROOT / "candidate_v0_2_review_in_progress.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), **result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
