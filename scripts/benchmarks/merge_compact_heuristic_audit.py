"""Merge source-supported heuristic-audit additions into provisional dev750 data."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from validate_compact_heuristic_audit import validate

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_omission_review_in_progress.json"
PACKET = ROOT / "heuristic_omission_audit_packet.json"
PROPOSAL = ROOT / "compact_heuristic_omission_audit_proposal.json"
OUTPUT = ROOT / "candidate_v0_2_heuristic_audit_review_in_progress.json"


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
        if decision["disposition"] == "add_primary":
            row.setdefault("added_claims", []).append(
                {
                    "id": f"heuristic_{decision['decision_index']:02d}",
                    "disposition": "primary",
                    "candidate": decision["proposed_finding"],
                    "source": "independently_reviewed_pro_heuristic_audit",
                    "proposal_sha256": sha256(PROPOSAL),
                    "decision_index": decision["decision_index"],
                    "quotation": decision["quotation"],
                    "decision_evidence": decision["decision_evidence"],
                    "decision_reason": decision["decision_reason"],
                    "overlap_legacy_ids": decision["overlap_legacy_ids"],
                }
            )
        elif decision["disposition"] == "unresolved":
            row.setdefault("unresolved_omission_suggestions", []).append(
                {
                    "decision_index": decision["decision_index"],
                    "quotation": decision["quotation"],
                    "remaining_question": decision["remaining_question"],
                    "proposal_sha256": sha256(PROPOSAL),
                }
            )
            reason = row.get("review_reason", "").strip()
            extra = (
                f"Unresolved heuristic lead {decision['decision_index']}: "
                f"{decision['remaining_question']}"
            )
            row["review_reason"] = f"{reason} {extra}".strip()
            row["annotation_state"] = "needs_review"
    counts = Counter(row["annotation_state"] for row in result["rows"])
    added = sum(len(row.get("added_claims", [])) for row in result["rows"])
    result["status"] = "provisional_with_unresolved_source_and_omission_rows"
    result["heuristic_omission_audit"] = {
        "packet": str(PACKET),
        "packet_sha256": sha256(PACKET),
        "proposal": str(PROPOSAL),
        "proposal_sha256": sha256(PROPOSAL),
        "validation": validation,
    }
    result["summary"]["annotation_states"] = dict(counts)
    result["summary"]["added_primary_claims"] = added
    result["summary"]["unresolved_omission_suggestions"] = sum(
        len(row.get("unresolved_omission_suggestions", [])) for row in result["rows"]
    )
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "output_sha256": sha256(OUTPUT),
                "source_rows": len(result["rows"]),
                "legacy_claims": sum(len(row["claims"]) for row in result["rows"]),
                "added_primary_claims": added,
                "annotation_states": dict(counts),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
