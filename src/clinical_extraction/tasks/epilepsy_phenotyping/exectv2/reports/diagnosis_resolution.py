"""Freeze completed Diagnosis review decisions into a mechanism ledger."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

LEDGER_SCHEMA = "exectv2_diagnosis_resolution_ledger_v1"

_RULE_MECHANISMS = {
    "non_target_diagnosis_scope": "non_target_diagnosis",
    "opposite_direction_same_cui": "same_cui_representation",
    "related_gold_representation": "clinical_granularity",
    "related_prediction_representation": "clinical_granularity",
    "reviewed_equivalence_pair": "reviewed_equivalence",
    "reviewed_negated_focal_pattern": "context_scope_error",
    "supported_gold_omission": "likely_gold_omission",
    "unsupported_gold_concept_miss": "missed_named_diagnosis",
    "unsupported_spurious_concept": "unsupported_spurious_diagnosis",
}


def build_review_ledger(
    *,
    audit_jsonl: Path,
    completed_overlay_json: Path,
    out_frozen_overlay_json: Path | None = None,
    out_ledger_jsonl: Path | None = None,
    out_summary_json: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Merge one completed review decision into every fixed audit row."""

    rows = [
        json.loads(line)
        for line in audit_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    row_by_key = {str(row["review_key"]): row for row in rows}
    if len(row_by_key) != len(rows):
        raise ValueError("audit contains duplicate review keys")

    overlay = json.loads(completed_overlay_json.read_text(encoding="utf-8"))
    decisions: dict[str, Mapping[str, Any]] = overlay.get("decisions", {})
    if set(decisions) != set(row_by_key) or overlay.get("triaged_count") != len(rows):
        raise ValueError("completed overlay must contain one complete decision per audit row")
    expected = overlay.get("source_review_row_count")
    if expected is not None and expected != len(rows):
        raise ValueError(f"overlay row count mismatch: overlay={expected}, audit={len(rows)}")

    ledger: list[dict[str, Any]] = []
    triage_counts: Counter[str] = Counter()
    mechanism_counts: Counter[str] = Counter()
    provenance_counts: Counter[str] = Counter()
    method_memberships: Counter[str] = Counter()
    direction_counts: Counter[str] = Counter()
    for row in rows:
        key = str(row["review_key"])
        decision = decisions[key]
        triage = str(decision.get("triage", ""))
        note = str(decision.get("note", ""))
        rule_ids = _rule_ids(note)
        provenance = "pattern_assisted" if rule_ids else "manual"
        mechanism = _mechanism(triage, rule_ids)
        ledger_row = dict(row)
        ledger_row["resolution_schema_version"] = LEDGER_SCHEMA
        ledger_row["review_decision"] = {
            "triage": triage,
            "provenance": provenance,
            "mechanism": mechanism,
            "rule_ids": rule_ids,
            "note": note,
        }
        ledger.append(ledger_row)
        triage_counts[triage] += 1
        mechanism_counts[mechanism] += 1
        provenance_counts[provenance] += 1
        direction_counts[f"{triage}:{row['direction']}"] += 1
        method_memberships.update(row.get("methods", []))

    summary = {
        "schema_version": LEDGER_SCHEMA,
        "audit_jsonl": str(audit_jsonl),
        "audit_sha256": _sha256(audit_jsonl),
        "completed_overlay_json": str(completed_overlay_json),
        "completed_overlay_sha256": _sha256(completed_overlay_json),
        "review_row_count": len(ledger),
        "triage_counts": dict(sorted(triage_counts.items())),
        "mechanism_counts": dict(sorted(mechanism_counts.items())),
        "decision_provenance_counts": dict(sorted(provenance_counts.items())),
        "triage_direction_counts": dict(sorted(direction_counts.items())),
        "method_memberships": dict(sorted(method_memberships.items())),
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
    }
    _write_json(out_frozen_overlay_json, overlay)
    _write_jsonl(out_ledger_jsonl, ledger)
    _write_json(out_summary_json, summary)
    return ledger, summary


def _rule_ids(note: str) -> list[str]:
    if "[auto:" not in note:
        return []
    value = note.split("[auto:", 1)[1].split("]", 1)[0]
    return sorted(part.strip() for part in value.split(",") if part.strip())


def _mechanism(triage: str, rule_ids: list[str]) -> str:
    if not rule_ids:
        return {
            "representation": "manual_representation",
            "extraction_error": "manual_extraction_error",
            "uncertain": "unresolved_clinical_ambiguity",
        }.get(triage, "manual_unclassified")
    mechanisms = {_RULE_MECHANISMS.get(rule, "pattern_unclassified") for rule in rule_ids}
    priorities = (
        "non_target_diagnosis",
        "context_scope_error",
        "missed_named_diagnosis",
        "unsupported_spurious_diagnosis",
        "same_cui_representation",
        "reviewed_equivalence",
        "likely_gold_omission",
        "clinical_granularity",
    )
    return next((value for value in priorities if value in mechanisms), "pattern_unclassified")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_jsonl(path: Path | None, rows: list[dict[str, Any]]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_json(path: Path | None, payload: Mapping[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
