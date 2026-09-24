"""Apply independently checked omission decisions to a provisional dev750 candidate.

New claims retain separate provenance; the 1,524 legacy claims are unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from validate_compact_omission_sweep import validate

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_policy_rows_adjudicated_review_in_progress.json"
PACKET = ROOT / "omission_review_packet.json"
PROPOSAL = ROOT / "compact_omission_sweep_proposal.json"
OUTPUT = ROOT / "candidate_v0_2_omission_review_in_progress.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    validation = validate(PACKET, PROPOSAL)
    base = json.loads(BASE.read_text())
    packet = json.loads(PACKET.read_text())
    proposal = json.loads(PROPOSAL.read_text())
    if sha256(BASE) != packet["candidate_sha256"]:
        raise ValueError("The omission packet was prepared from a different candidate")
    result = copy.deepcopy(base)
    by_id = {row["source_id"]: row for row in result["rows"]}
    accepted_addition_indices = [
        decision["decision_index"]
        for decision in proposal["suggestion_decisions"]
        if decision["disposition"] == "add_primary"
    ]
    # Each proposed addition was checked against its full note, current claim
    # inventory, and the narrower primary policy before inclusion here.
    if len(accepted_addition_indices) != 16:
        raise ValueError("Unexpected set of source-reviewed additions")
    newly_unresolved: list[str] = []
    for decision in proposal["suggestion_decisions"]:
        row = by_id[decision["source_id"]]
        if row["source_sha256"] != decision["source_sha256"]:
            raise ValueError("Source identity changed")
        if decision["disposition"] == "add_primary":
            row.setdefault("added_claims", []).append(
                {
                    "id": f"omission_{decision['decision_index']:02d}",
                    "disposition": "primary",
                    "candidate": decision["proposed_finding"],
                    "source": "independently_reviewed_pro_omission_proposal",
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
                    "issue_category": decision["issue_category"],
                    "proposal_sha256": sha256(PROPOSAL),
                }
            )
            question = decision["remaining_question"]
            prior_reason = row.get("review_reason", "").strip()
            prefix = f"Unresolved omission {decision['decision_index']}: {question}"
            row["review_reason"] = f"{prior_reason} {prefix}".strip()
            if row["annotation_state"] == "complete":
                row["annotation_state"] = "needs_review"
                newly_unresolved.append(row["source_id"])
    result["status"] = "provisional_with_unresolved_source_and_omission_rows"
    result["omission_review"] = {
        "packet": str(PACKET),
        "packet_sha256": sha256(PACKET),
        "proposal": str(PROPOSAL),
        "proposal_sha256": sha256(PROPOSAL),
        "validation": validation,
        "added_claims": len(accepted_addition_indices),
        "newly_needs_review_source_ids": newly_unresolved,
        "unresolved_suggestions": validation["dispositions"]["unresolved"],
    }
    states = Counter(row["annotation_state"] for row in result["rows"])
    result["summary"]["annotation_states"] = dict(states)
    result["summary"]["added_primary_claims"] = len(accepted_addition_indices)
    result["summary"]["unresolved_omission_suggestions"] = validation["dispositions"][
        "unresolved"
    ]
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "output_sha256": sha256(OUTPUT),
                "source_rows": len(result["rows"]),
                "legacy_claims": sum(len(row["claims"]) for row in result["rows"]),
                "added_claims": len(accepted_addition_indices),
                "annotation_states": dict(states),
                "newly_needs_review_source_ids": newly_unresolved,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
