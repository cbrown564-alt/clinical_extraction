"""Gold audit worklist routes for the Observatory."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query, Request

from clinical_extraction.observatory.helpers import resolve_under_root
from clinical_extraction.observatory.models import GoldAuditDecision, ObservatorySettings
from clinical_extraction.observatory.gan2026.gold_audit_sampler import (
    _latest_decisions,
    enrich_rows_for_active_sampling,
)

router = APIRouter(tags=["gold-audit"])

DEFAULT_GOLD_AUDIT_CSV = Path(
    "experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv"
)
DEFAULT_GOLD_AUDIT_DECISIONS = Path("experiments/gold_audit_decisions.jsonl")

RQ10_CLASS_ORDER = [
    "true_extraction_failure",
    "benchmark_convention_dominated",
    "underdetermined_note",
    "clinically_defensible_alternative",
    "possible_gold_weakness",
    "instrumentation_gap",
]


def _settings(request: Request) -> ObservatorySettings:
    return request.app.state.observatory_settings


def _load_gold_audit_rows(
    settings: ObservatorySettings, split: str = "validation"
) -> list[dict[str, Any]]:
    csv_path = resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_CSV)
    if not csv_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("split") == split:
                rows.append(dict(row))
    return rows


def _load_gold_audit_decisions(settings: ObservatorySettings) -> list[dict[str, Any]]:
    path = resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_DECISIONS)
    if not path.exists():
        return []
    decisions: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                decisions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return decisions


def _save_gold_audit_decision(settings: ObservatorySettings, decision: dict[str, Any]) -> None:
    """Upsert a decision by (split, source_row_index) and rewrite the JSONL store."""

    path = resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_DECISIONS)
    merged = dict(_latest_decisions(_load_gold_audit_decisions(settings)))
    key = (str(decision.get("split", "")), int(decision.get("source_row_index", 0)))
    merged[key] = decision
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in merged.values():
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _compute_next_row(
    rows: Sequence[Mapping[str, Any]], decisions: Sequence[Mapping[str, Any]]
) -> dict[str, Any] | None:
    enriched, _model_summary = enrich_rows_for_active_sampling(rows, decisions)
    candidates = [
        (float(row["active_learning_score"]), row) for row in enriched if not row["has_decision"]
    ]

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return dict(candidates[0][1])


@router.get("/gold-audit/rows")
def gold_audit_rows(
    request: Request,
    split: str = Query(default="validation"),
) -> dict[str, Any]:
    settings = _settings(request)
    rows = _load_gold_audit_rows(settings, split=split)
    decisions = _load_gold_audit_decisions(settings)
    class_counts: dict[str, int] = {c: 0 for c in RQ10_CLASS_ORDER}
    for d in decisions:
        c = str(d.get("rq10_class", ""))
        if c in class_counts:
            class_counts[c] += 1
    enriched, model_summary = enrich_rows_for_active_sampling(rows, decisions)
    for row in enriched:
        row["priority_score"] = row["active_learning_score"]
    return {
        "split": split,
        "total": len(rows),
        "decided": sum(1 for row in enriched if row["has_decision"]),
        "class_counts": class_counts,
        "sampling_model": model_summary,
        "rows": enriched,
    }


@router.get("/gold-audit/decisions")
def gold_audit_decisions(
    request: Request,
    split: str | None = Query(default=None),
) -> dict[str, Any]:
    settings = _settings(request)
    all_decisions = _load_gold_audit_decisions(settings)
    if split is not None:
        all_decisions = [d for d in all_decisions if d.get("split") == split]
    return {"decisions": all_decisions, "count": len(all_decisions)}


@router.post("/gold-audit/decide")
def gold_audit_decide(decision: GoldAuditDecision, request: Request) -> dict[str, Any]:
    settings = _settings(request)
    payload = decision.model_dump(mode="json")
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.now(UTC).isoformat()
    _save_gold_audit_decision(settings, payload)
    return {"status": "saved", "decision": payload}


@router.get("/gold-audit/next")
def gold_audit_next(
    request: Request,
    split: str = Query(default="validation"),
) -> dict[str, Any]:
    settings = _settings(request)
    rows = _load_gold_audit_rows(settings, split=split)
    decisions = _load_gold_audit_decisions(settings)
    next_row = _compute_next_row(rows, decisions)
    if next_row is None:
        return {"split": split, "row": None, "message": "All rows have been audited."}
    return {"split": split, "row": next_row}
