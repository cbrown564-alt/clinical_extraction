"""Merge independently accepted zero-primary audit findings into dev750 candidate."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from validate_compact_zero_primary_audit import validate

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_heuristic_audit_review_in_progress.json"
PACKET = ROOT / "zero_primary_source_audit_packet.json"
PROPOSAL = ROOT / "compact_zero_primary_source_audit_proposal.json"
OUTPUT = ROOT / "candidate_v0_2_zero_primary_audit_reviewed.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    validation = validate(PACKET, PROPOSAL)
    packet = json.loads(PACKET.read_text())
    if packet["candidate_sha256"] != sha256(BASE):
        raise ValueError("Audit packet candidate hash mismatch")
    proposal = json.loads(PROPOSAL.read_text())
    result = copy.deepcopy(json.loads(BASE.read_text()))
    by_id = {row["source_id"]: row for row in result["rows"]}
    for decision in proposal["decisions"]:
        row = by_id[decision["source_id"]]
        index = decision["packet_row_index"]
        if decision["disposition"] == "add_primary":
            if decision["source_id"] != "3468":
                raise ValueError("Unexpected unreviewed addition")
            row.setdefault("added_claims", []).append(
                {
                    "id": f"zero_primary_{index:02d}",
                    "disposition": "primary",
                    "candidate": decision["proposed_finding"],
                    "source": "independently_reviewed_pro_zero_primary_audit",
                    "proposal_sha256": sha256(PROPOSAL),
                    "decision_index": index,
                    "quotation": decision["quotation"],
                    "decision_evidence": decision["decision_evidence"],
                    "decision_reason": decision["decision_reason"],
                    "overlap_legacy_ids": decision["overlap_legacy_ids"],
                }
            )
        elif decision["disposition"] == "unresolved":
            if decision["source_id"] != "8577":
                raise ValueError("Unexpected unreviewed unresolved lead")
            row.setdefault("unresolved_omission_suggestions", []).append(
                {
                    "decision_index": index,
                    "quotation": decision["quotation"],
                    "remaining_question": decision["remaining_question"],
                    "proposal_sha256": sha256(PROPOSAL),
                }
            )
            old = row.get("review_reason") or ""
            row["review_reason"] = (
                f"{old} Unresolved zero-primary lead {index}: "
                f"{decision['remaining_question']}"
            ).strip()
            row["annotation_state"] = "needs_review"
    counts = Counter(row["annotation_state"] for row in result["rows"])
    added = sum(len(row.get("added_claims", [])) for row in result["rows"])
    result["status"] = "provisional_with_unresolved_source_and_omission_rows"
    result["zero_primary_audit"] = {
        "packet": str(PACKET),
        "packet_sha256": sha256(PACKET),
        "proposal": str(PROPOSAL),
        "proposal_sha256": sha256(PROPOSAL),
        "validation": validation,
        "independent_source_review": {
            "accepted_addition_source_ids": ["3468"],
            "unresolved_source_ids": ["8577"],
            "note": "3468 occasional impaired-awareness progression is current and explicit; "
            "8577 app categories do not establish seizure identity.",
        },
    }
    result["summary"]["annotation_states"] = dict(counts)
    result["summary"]["added_primary_claims"] = added
    result["summary"]["unresolved_omission_suggestions"] = sum(
        len(row.get("unresolved_omission_suggestions", [])) for row in result["rows"]
    )
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"candidate": str(OUTPUT), "sha256": sha256(OUTPUT),
                      "states": dict(counts), "added_primary_claims": added}, indent=2))


if __name__ == "__main__":
    main()
