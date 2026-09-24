"""Check the owner-approved v0.3 overlay against its frozen v0.2 input."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from validate_compact_candidate_v0_2 import validate as validate_candidate

ROOT = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
BASE = ROOT / "candidate_v0_2_zero_primary_audit_reviewed.json"
TARGET = ROOT / "candidate_v0_3_owner_adjudicated.json"
ALLOWED_NEWLY_CHANGED_COMPLETE = {"10873"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, Any]:
    old = json.loads(BASE.read_text())
    new = json.loads(TARGET.read_text())
    base_review = {r["source_id"] for r in old["rows"] if r["annotation_state"] == "needs_review"}
    if new["owner_review"]["base_sha256"] != sha256(BASE):
        raise ValueError("Base candidate hash mismatch")
    if set(new["owner_review"]["reviewed_source_ids"]) != base_review:
        raise ValueError("Owner review did not cover exactly the unresolved rows")
    if len(base_review) != 64:
        raise ValueError("Unexpected input review count")
    if len(new["rows"]) != 750 or new["summary"]["annotation_states"] != {"complete": 750}:
        raise ValueError("Incomplete owner review output")
    changed_ids: set[str] = set()
    added = 0
    for before, after in zip(old["rows"], new["rows"], strict=True):
        sid = before["source_id"]
        if sid != after["source_id"] or before["note"] != after["note"]:
            raise ValueError(f"{sid}: source changed")
        if len(before["claims"]) != len(after["claims"]):
            raise ValueError(f"{sid}: claim inventory changed")
        claim_changed = False
        for original, revised in zip(before["claims"], after["claims"], strict=True):
            if original["original_record"] != revised["original_record"]:
                raise ValueError(f"{sid}: original claim changed")
            if (original["disposition"], original["candidate"]) != (
                revised["disposition"],
                revised["candidate"],
            ):
                claim_changed = True
        prior_additions = before.get("added_claims", [])
        after_additions = after.get("added_claims", [])
        if after_additions[: len(prior_additions)] != prior_additions:
            raise ValueError(f"{sid}: prior addition changed")
        new_additions = after_additions[len(prior_additions) :]
        if any(c["source"] != "owner_adjudication_2026_09_24" for c in new_additions):
            raise ValueError(f"{sid}: addition attribution mismatch")
        added += len(new_additions)
        if (
            claim_changed
            or new_additions
            or before["annotation_state"] != after["annotation_state"]
        ):
            changed_ids.add(sid)
            if not after.get("owner_adjudications"):
                raise ValueError(f"{sid}: missing decision attribution")
        if sid in base_review and after.get("prior_review_reason") != before.get("review_reason"):
            raise ValueError(f"{sid}: prior review reason not retained")
        if after.get("unresolved_omission_suggestions"):
            raise ValueError(f"{sid}: unresolved suggestion on complete row")
    if changed_ids - base_review != ALLOWED_NEWLY_CHANGED_COMPLETE:
        raise ValueError("Changes outside approved source set")
    if added != 14 or new["summary"]["added_primary_claims"] != 39:
        raise ValueError("Owner addition count mismatch")

    def record(sid: str, cid: str) -> dict[str, Any]:
        row = next(r for r in new["rows"] if r["source_id"] == sid)
        return next(c for c in row["claims"] if c["legacy_id"] == cid)

    for sid in ("959", "960"):
        measurement = record(sid, "f1")["candidate"]["measurement"]
        if measurement != {
            "kind": "rate",
            "quantity": {"kind": "number", "value": 1},
            "per": {"kind": "number", "value": 2, "unit": "month"},
        }:
            raise ValueError(f"{sid}: bimonthly meaning changed")
    for sid in ("12484", "12502", "12506"):
        tonic_id = "f6" if sid == "12484" else "f4"
        cluster_id = {"12484": "f9", "12502": "f7", "12506": "f6"}[sid]
        if record(sid, tonic_id)["candidate"]["measurement"]["kind"] != "rate":
            raise ValueError(f"{sid}: tonic cadence missing")
        cluster = record(sid, cluster_id)["candidate"]
        if cluster["counted_unit"] != "cluster" or cluster["measurement"]["kind"] != "cluster":
            raise ValueError(f"{sid}: myoclonic cluster unit changed")
    if record("10873", "f1")["candidate"]["status"] != "uncertain":
        raise ValueError("10873: possible seizure status lost")
    if record("15497", "f4")["disposition"] != "context":
        raise ValueError("15497: flight cluster duplicated")
    if record("15519", "f3")["disposition"] != "primary":
        raise ValueError("15519: early-morning claim lost")
    if record("13209", "f3")["candidate"]["time"]["phase"] != "past_or_unclear":
        raise ValueError("13209: undated cluster assigned current phase")
    structural = validate_candidate(TARGET)
    return {
        "candidate_sha256": sha256(TARGET),
        "owner_review_rows": len(base_review),
        "new_additions": added,
        "changed_source_rows": len(changed_ids),
        "source_ids_changed_outside_review": sorted(changed_ids - base_review),
        "structural_validation": structural,
        "clinical_limit": "Owner choices applied; independent annotator agreement not measured",
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
