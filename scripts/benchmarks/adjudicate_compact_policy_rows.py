"""Resolve the 18 full-note policy rows under the versioned compact v0.2 rules.

Fifteen source-supported rows have no remaining source question. Three remain
unresolved. This changes only the provisional candidate, never frozen gold.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_source_adjudicated_review_in_progress.json"
PROPOSAL = ROOT / "compact_policy_adjudication_proposal.json"
COMPLETE = {
    "1317", "4478", "4480", "4562", "4563", "4574", "4592", "4597", "10673",
    "15715", "15745", "15766", "15768", "15772", "15774",
}
UNRESOLVED = {"959", "960", "15771"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    base = json.loads(BASE.read_text())
    proposal = json.loads(PROPOSAL.read_text())
    recs = proposal["row_recommendations"]
    if set(recs) != COMPLETE | UNRESOLVED:
        raise ValueError("The 18 full-source review rows changed")
    result = copy.deepcopy(base)
    reviewed = []
    for row in result["rows"]:
        source_id = row["source_id"]
        if source_id not in recs:
            continue
        rec = recs[source_id]
        if row["annotation_state"] != "needs_review":
            raise ValueError(f"Expected needs_review policy row: {source_id}")
        if row["source_sha256"] != rec["source_sha256"]:
            raise ValueError(f"Source hash mismatch: {source_id}")
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"Source note hash mismatch: {source_id}")
        if [claim["legacy_id"] for claim in row["claims"]] != rec["legacy_claim_order"]:
            raise ValueError(f"Legacy order mismatch: {source_id}")
        target = [x for x in rec["claims"].values() if x["is_target_null_primary"]]
        if len(target) != 1:
            raise ValueError(f"Expected one target policy claim: {source_id}")
        claim_rec = target[0]
        legacy_id = claim_rec["legacy_id"]
        claim = next(c for c in row["claims"] if c["legacy_id"] == legacy_id)
        if any(quote not in row["note"] for quote in claim_rec["exact_source_evidence"]):
            raise ValueError(f"Policy evidence is not exact: {source_id}/{legacy_id}")
        action = claim_rec["recommendation"]
        if source_id in COMPLETE:
            if rec["remaining_source_questions"]:
                raise ValueError(f"Source question remains: {source_id}")
            if action == "recommend_schema_change":
                if claim["disposition"] != "primary" or claim["candidate"] is None:
                    raise ValueError(f"Extension was not applied: {source_id}/{legacy_id}")
            elif action == "downgrade_to_context":
                if claim["disposition"] != "context" or claim["candidate"] is not None:
                    raise ValueError(f"Context decision was not applied: {source_id}/{legacy_id}")
            else:
                raise ValueError(f"Unexpected complete-row action: {source_id}/{action}")
            if any(c["disposition"] == "primary" and c["candidate"] is None for c in row["claims"]):
                raise ValueError(f"Complete row still has null primary: {source_id}")
            row["annotation_state"] = "complete"
            row.pop("review_reason", None)
        else:
            if not rec["remaining_source_questions"]:
                raise ValueError(f"Expected unresolved source question: {source_id}")
            if not str(row.get("review_reason", "")).strip():
                raise ValueError(f"Unresolved row has no reason: {source_id}")
        row["policy_row_adjudication"] = {
            "proposal_sha256": sha256(PROPOSAL),
            "target_legacy_id": legacy_id,
            "decision": "complete" if source_id in COMPLETE else "needs_review",
            "action": action,
            "exact_source_evidence": claim_rec["exact_source_evidence"],
            "policy_reason": claim_rec["policy_reason"],
            "remaining_source_questions": rec["remaining_source_questions"],
        }
        reviewed.append(source_id)
    if set(reviewed) != COMPLETE | UNRESOLVED:
        raise ValueError("Candidate policy row coverage changed")
    states = Counter(row["annotation_state"] for row in result["rows"])
    null_primary = sum(
        c["disposition"] == "primary" and c["candidate"] is None
        for row in result["rows"] for c in row["claims"]
    )
    result["status"] = "policy_and_source_adjudicated_provisional_not_accepted_gold"
    result["policy_row_base"] = str(BASE)
    result["policy_row_base_sha256"] = sha256(BASE)
    result["policy_row_summary"] = {
        "complete_from_18": len(COMPLETE),
        "unresolved_from_18": len(UNRESOLVED),
        "annotation_states": dict(states),
        "null_primary_claims": null_primary,
        "scored_partition": "complete rows only; needs_review rows remain provisional",
    }
    out = ROOT / "candidate_v0_2_policy_rows_adjudicated_review_in_progress.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(out), **result["policy_row_summary"]}, indent=2))


if __name__ == "__main__":
    main()
