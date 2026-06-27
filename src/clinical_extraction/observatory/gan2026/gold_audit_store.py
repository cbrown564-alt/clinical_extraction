"""Durable gold-audit worklist and decision store with atomic JSONL upsert."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.observatory.gan2026.gold_audit_sampler import latest_decisions
from clinical_extraction.observatory.helpers import resolve_under_root
from clinical_extraction.observatory.models import GoldAuditDecision, ObservatorySettings

DEFAULT_GOLD_AUDIT_CSV = Path(
    "experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv"
)
DEFAULT_GOLD_AUDIT_DECISIONS = Path("experiments/gold_audit_decisions.jsonl")

RQ10_CLASS_ORDER = (
    "true_extraction_failure",
    "benchmark_convention_dominated",
    "underdetermined_note",
    "clinically_defensible_alternative",
    "possible_gold_weakness",
    "instrumentation_gap",
)


def decisions_path(settings: ObservatorySettings) -> Path:
    return resolve_under_root(settings.repo_root, DEFAULT_GOLD_AUDIT_DECISIONS)


def load_gold_audit_rows(
    settings: ObservatorySettings,
    *,
    split: str = "validation",
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


def load_gold_audit_decisions(settings: ObservatorySettings) -> list[dict[str, Any]]:
    path = decisions_path(settings)
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


def rq10_class_counts(decisions: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {class_name: 0 for class_name in RQ10_CLASS_ORDER}
    for decision in decisions:
        class_name = str(decision.get("rq10_class", ""))
        if class_name in counts:
            counts[class_name] += 1
    return counts


def upsert_gold_audit_decision(
    settings: ObservatorySettings,
    decision: GoldAuditDecision | Mapping[str, Any],
) -> GoldAuditDecision:
    """Upsert one decision by (split, source_row_index) and atomically rewrite JSONL."""

    payload = (
        decision.model_dump(mode="json")
        if isinstance(decision, GoldAuditDecision)
        else dict(decision)
    )
    path = decisions_path(settings)
    merged = dict(latest_decisions(load_gold_audit_decisions(settings)))
    key = (str(payload.get("split", "")), int(payload.get("source_row_index", 0)))
    merged[key] = payload
    _atomic_write_jsonl(path, merged.values())
    return GoldAuditDecision.model_validate(payload)


def _atomic_write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
