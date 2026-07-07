"""Read-only ``/gold-noise`` routes for gold-quality inspection.

The companion to ``/gold-audit``. Where the gold-audit tab is an active triage
queue (write-back decisions over the Gan validation ambiguity review), this tab
is **read-only**: it surfaces the per-item gold-vs-pred evidence the four
ExECT ``gold_case_ledger_{family}.jsonl`` files already carry, plus the Gan RQ10
scorer-ambiguity audit, the genuine-defects list, and the hypothesis registry.

This is the "honest headline" surface: the four ceiling percentages currently
cited as bare numbers in ``PROJECT_STATUS.md`` are made inspectable. The ceiling
is *derived live* from each ledger's ``verdict == "gold_right"`` fraction rather
than hard-coded, so the tab cannot silently drift from the ledgers it reports
on.

The ledgers are produced by the offline canonical adjudicators; this surface
does not write to them. File parsing is a raw ``json`` read (the same pattern
``gold_audit_store`` uses) rather than importing the ``exectv2_ledger`` package,
which is a script namespace under ``experiments/`` and is not installed.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from clinical_extraction.observatory.helpers import resolve_under_root
from clinical_extraction.observatory.models import ObservatorySettings
from clinical_extraction.observatory.responses import (
    GoldNoiseGanAuditResponse,
    GoldNoiseHypothesesResponse,
    GoldNoiseIssuesResponse,
    GoldNoiseLedgersResponse,
    GoldNoiseRowResponse,
)

router = APIRouter(tags=["gold-noise"])

#: The four ExECT families this surface reports on, in canonical display order.
#: ``key`` is the ledger filename segment; ``family`` is the value embedded in
#: each row (and the canonical display label).
FAMILIES: tuple[dict[str, str], ...] = (
    {"key": "diagnosis", "family": "Diagnosis"},
    {"key": "seizurefrequency", "family": "SeizureFrequency"},
    {"key": "prescription", "family": "Prescription"},
    {"key": "investigations", "family": "Investigations"},
)

#: Source tag stamped on every normalized item so the UI can label origin.
EXECLEDGER_SOURCE = "exectv2_gold_case_ledger"

DEFAULT_GAN_AUDIT_PATH = Path(
    "experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json"
)
DEFAULT_GOLD_ISSUES_PATH = Path("experiments/gold_data_issues.jsonl")
DEFAULT_HYPOTHESIS_REGISTRY_PATH = Path("experiments/hypothesis_registry.jsonl")

#: The note that the Gan RQ10 taxonomy is *not* commensurable with ExECT's
#: ``Mechanism`` enum, surfaced verbatim so the UI never mixes the two.
GAN_TAXONOMY_NOTE = (
    "Gan RQ10 uses its own class taxonomy (rq10_class: true_extraction_failure, "
    "benchmark_convention_dominated, underdetermined_note, "
    "clinically_defensible_alternative, possible_gold_weakness, "
    "instrumentation_gap). It is NOT commensurable with ExECT's Mechanism enum "
    "and must never be summed or averaged against it."
)


def _settings(request: Request) -> ObservatorySettings:
    return request.app.state.observatory_settings


def _ledger_path(settings: ObservatorySettings, key: str) -> Path:
    return resolve_under_root(settings.repo_root, Path(f"experiments/gold_case_ledger_{key}.jsonl"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a newline-delimited JSON file, tolerant of missing files / bad lines.

    Mirrors ``gold_audit_store.load_gold_audit_decisions``: a missing file is an
    empty list (not a 500), and malformed lines are skipped so one bad row can
    never blank the whole surface.
    """

    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _to_gold_noise_item(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize one ExECT ``GoldCaseRow`` JSON record to the unified item shape.

    This is the single adapter the two incompatible schemas touch through. The
    ExECT ledger's ``provenance.reason`` is the adjudication rationale a reader
    needs at the item level; ``gold``/``pred`` carry the mention text the
    ``LetterRenderer`` highlights.
    """

    provenance = record.get("provenance") or {}
    return {
        "family": record.get("family", ""),
        "letter_id": record.get("letter_id", ""),
        "row_id": record.get("row_id", ""),
        "disagreement_type": record.get("disagreement_type", ""),
        "match_key": record.get("match_key", ""),
        "mechanism": record.get("mechanism", "unadjudicated"),
        "verdict": record.get("verdict", "unadjudicated"),
        "gold": record.get("gold"),
        "pred": record.get("pred"),
        "reason": provenance.get("reason", "") or "",
        "run_id": record.get("run_id", ""),
        "source_letter_text": record.get("source_letter_text", ""),
        "source": EXECLEDGER_SOURCE,
    }


def _family_summary(family: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive the per-family ceiling + breakdowns from raw ledger rows.

    The ceiling is the ``verdict == "gold_right"`` fraction: the share of
    disagreements where the model genuinely erred (vs the gold being
    contestable). Its complement (model_defensible + both_defensible) is the
    gold-contested share. Both are surfaced with honest numerators.
    """

    verdict_counts = Counter(row.get("verdict", "unadjudicated") for row in rows)
    mechanism_counts = Counter(row.get("mechanism", "unadjudicated") for row in rows)
    return {
        "family": family,
        "total": len(rows),
        "gold_right": verdict_counts.get("gold_right", 0),
        "model_defensible": verdict_counts.get("model_defensible", 0),
        "both_defensible": verdict_counts.get("both_defensible", 0),
        "unadjudicated": verdict_counts.get("unadjudicated", 0),
        "by_verdict": dict(verdict_counts),
        "by_mechanism": dict(mechanism_counts),
        "rows": [_to_gold_noise_item(row) for row in rows],
    }


@router.get("/gold-noise/ledgers", response_model=GoldNoiseLedgersResponse)
def gold_noise_ledgers(request: Request) -> GoldNoiseLedgersResponse:
    settings = _settings(request)
    families = [
        _family_summary(spec["family"], _read_jsonl(_ledger_path(settings, spec["key"])))
        for spec in FAMILIES
    ]
    return GoldNoiseLedgersResponse(families=families)


@router.get("/gold-noise/gan-audit", response_model=GoldNoiseGanAuditResponse)
def gold_noise_gan_audit(request: Request) -> GoldNoiseGanAuditResponse:
    settings = _settings(request)
    path = resolve_under_root(settings.repo_root, DEFAULT_GAN_AUDIT_PATH)
    audit = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    return GoldNoiseGanAuditResponse(
        audit=audit,
        taxonomy="rq10_class",
        taxonomy_note=GAN_TAXONOMY_NOTE,
    )


@router.get("/gold-noise/issues", response_model=GoldNoiseIssuesResponse)
def gold_noise_issues(request: Request) -> GoldNoiseIssuesResponse:
    settings = _settings(request)
    path = resolve_under_root(settings.repo_root, DEFAULT_GOLD_ISSUES_PATH)
    issues = _read_jsonl(path)
    return GoldNoiseIssuesResponse(count=len(issues), issues=issues)


@router.get("/gold-noise/row", response_model=GoldNoiseRowResponse)
def gold_noise_row(
    request: Request,
    family: str = Query(...),
    row_id: str = Query(...),
) -> GoldNoiseRowResponse:
    settings = _settings(request)
    spec = next((s for s in FAMILIES if s["family"] == family), None)
    if spec is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown family: {family!r}. "
            f"Expected one of {[s['family'] for s in FAMILIES]}.",
        )
    rows = _read_jsonl(_ledger_path(settings, spec["key"]))
    record = next((row for row in rows if row.get("row_id") == row_id), None)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No ledger row with row_id={row_id!r} in family {family!r}.",
        )
    return GoldNoiseRowResponse(**_to_gold_noise_item(record))


@router.get("/gold-noise/hypotheses", response_model=GoldNoiseHypothesesResponse)
def gold_noise_hypotheses(request: Request) -> GoldNoiseHypothesesResponse:
    settings = _settings(request)
    path = resolve_under_root(settings.repo_root, DEFAULT_HYPOTHESIS_REGISTRY_PATH)
    entries = _read_jsonl(path)
    by_family: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        by_family.setdefault(str(entry.get("family", "cross_family")), []).append(entry)
    return GoldNoiseHypothesesResponse(count=len(entries), by_family=by_family, entries=entries)
