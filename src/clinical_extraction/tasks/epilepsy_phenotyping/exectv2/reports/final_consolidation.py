"""Structured final-consolidation data for ExECTv2 reports and the frontend.

Phase 3 of the final consolidation plan needs one reusable source for the
cross-model comparison and reliability scorecard. This module deliberately reads
the canonical Markdown reports that remain paper-facing, then emits compact JSON
for tests, API responses, and the frontend static fallback. It makes no model
calls and never inspects held-out/full-200 row-level data.
"""

from __future__ import annotations

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[6]


REPO_ROOT = _find_repo_root()
RELIABILITY_SCORECARD_PATH = Path(
    "docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md"
)
CROSS_MODEL_REPORT_PATH = Path(
    "docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md"
)
GAN_RELIABILITY_SCORECARD_PATH = Path(
    "experiments/gan2026_reliability_master_scorecard_2026-06-17.md"
)


def _strip_inline(value: str) -> str:
    text = value.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return text.strip()


def _slug(value: str) -> str:
    text = _strip_inline(value).lower()
    text = text.replace("/", " ")
    words = re.findall(r"[a-z0-9]+", text)
    return "_".join(words)


def _as_float(value: str) -> float | None:
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


def _parse_fraction(value: str) -> tuple[int | None, int | None]:
    match = re.search(r"(\d+)\s*/\s*(\d+)", value)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if cells and set("".join(cells)) <= set("-: "):
        return []
    return cells


def parse_markdown_tables(md_text: str) -> list[list[list[str]]]:
    """Return all pipe tables as rows, including the header row."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in md_text.splitlines():
        cells = _table_cells(line)
        if cells is None:
            if current:
                tables.append(current)
                current = []
            continue
        if not cells:
            continue
        current.append(cells)
    if current:
        tables.append(current)
    return tables


def _table_by_header(tables: list[list[list[str]]], required: tuple[str, ...]) -> list[list[str]]:
    required_normalized = {_slug(item) for item in required}
    for table in tables:
        if not table:
            continue
        header = {_slug(cell) for cell in table[0]}
        if required_normalized.issubset(header):
            return table
    return []


def _rows_from_table(table: list[list[str]]) -> list[dict[str, str]]:
    if not table:
        return []
    headers = [_slug(cell) for cell in table[0]]
    rows: list[dict[str, str]] = []
    for row in table[1:]:
        if len(row) < len(headers):
            row = [*row, *([""] * (len(headers) - len(row)))]
        rows.append(
            {headers[index]: _strip_inline(cell) for index, cell in enumerate(row[: len(headers)])}
        )
    return rows


def load_markdown(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def parse_evidence_set(md_text: str) -> list[dict[str, Any]]:
    table = _table_by_header(
        parse_markdown_tables(md_text),
        ("Role", "Candidate", "Surface", "Overall F1", "Decision"),
    )
    rows = []
    for row in _rows_from_table(table):
        rows.append(
            {
                "role": row.get("role", ""),
                "candidate": row.get("candidate", ""),
                "surface": row.get("surface", ""),
                "overall_f1": _as_float(row.get("overall_f1", "")),
                "decision": row.get("decision", ""),
            }
        )
    return rows


def parse_scorecard_dimensions(md_text: str) -> list[dict[str, Any]]:
    table = _table_by_header(
        parse_markdown_tables(md_text),
        ("#", "Dimension", "Coverage", "Current evidence", "Gap to close"),
    )
    dimensions = []
    for row in _rows_from_table(table):
        coverage, coverage_max = _parse_fraction(row.get("coverage", ""))
        dimensions.append(
            {
                "id": _slug(row.get("dimension", "")),
                "number": int(_as_float(row.get("", "")) or len(dimensions) + 1),
                "dimension": row.get("dimension", ""),
                "coverage": coverage,
                "coverage_max": coverage_max,
                "current_evidence": row.get("current_evidence", ""),
                "gap_to_close": row.get("gap_to_close", ""),
                "strength": _coverage_strength(coverage, coverage_max),
            }
        )
    return dimensions


def _coverage_strength(coverage: int | None, coverage_max: int | None) -> str:
    if coverage is None or not coverage_max:
        return "unknown"
    ratio = coverage / coverage_max
    if ratio >= 0.8:
        return "strong"
    if ratio >= 0.6:
        return "medium"
    return "weak"


def parse_metric_status(md_text: str) -> list[dict[str, str]]:
    table = _table_by_header(parse_markdown_tables(md_text), ("Metric", "Current status"))
    return [
        {
            "metric": row.get("metric", ""),
            "current_status": row.get("current_status", ""),
        }
        for row in _rows_from_table(table)
    ]


def parse_residual_risks(md_text: str) -> list[dict[str, str]]:
    table = _table_by_header(
        parse_markdown_tables(md_text),
        ("Family", "Current strength", "Residual risk"),
    )
    return [
        {
            "family": row.get("family", ""),
            "current_strength": row.get("current_strength", ""),
            "residual_risk": row.get("residual_risk", ""),
        }
        for row in _rows_from_table(table)
    ]


def parse_upgrade_plan(md_text: str) -> list[dict[str, str]]:
    table = _table_by_header(parse_markdown_tables(md_text), ("Dimension", "Next metric needed"))
    return [
        {
            "dimension": row.get("dimension", ""),
            "next_metric_needed": row.get("next_metric_needed", ""),
        }
        for row in _rows_from_table(table)
    ]


def parse_comparison_rows(md_text: str) -> list[dict[str, Any]]:
    table = _table_by_header(
        parse_markdown_tables(md_text),
        ("Candidate", "Model", "Overall F1", "Decision"),
    )
    rows = []
    for row in _rows_from_table(table):
        rows.append(
            {
                "candidate": row.get("candidate", ""),
                "model": row.get("model", ""),
                "architecture_family": row.get("architecture_family", ""),
                "split_stage": row.get("split_stage", ""),
                "call_failures": _as_float(row.get("call_failures", "")),
                "parse_schema_failures": _as_float(row.get("parse_schema_failures", "")),
                "exact_evidence_rate": _as_float(row.get("exact_evidence_rate", "")),
                "overall_f1": _as_float(row.get("overall_f1", "")),
                "diagnosis_f1": _as_float(row.get("dx", "")),
                "seizure_frequency_f1": _as_float(row.get("sf", "")),
                "prescription_f1": _as_float(row.get("rx", "")),
                "investigations_f1": _as_float(row.get("inv", "")),
                "companion_surface": row.get("companion_surface", ""),
                "decision": row.get("decision", ""),
                "claim_boundary": row.get("claim_boundary", ""),
            }
        )
    return rows


def build_reliability_scorecard_payload(
    *,
    scorecard_path: Path = RELIABILITY_SCORECARD_PATH,
    cross_model_path: Path = CROSS_MODEL_REPORT_PATH,
) -> dict[str, Any]:
    from . import cross_model_reliability_analysis as reliability_analysis

    scorecard_md = load_markdown(scorecard_path)
    cross_model_md = load_markdown(cross_model_path)
    dimensions = parse_scorecard_dimensions(scorecard_md)
    return {
        "dataset": "exectv2",
        "generated_on": date.today().isoformat(),
        "source_scorecard": scorecard_path.as_posix(),
        "source_cross_model_report": cross_model_path.as_posix(),
        "evidence_set": parse_evidence_set(scorecard_md),
        "dimensions": dimensions,
        "weak_dimensions": [
            dimension for dimension in dimensions if dimension.get("strength") == "weak"
        ],
        "metrics_available_now": parse_metric_status(scorecard_md),
        "residual_risks": parse_residual_risks(scorecard_md),
        "upgrade_plan": parse_upgrade_plan(scorecard_md),
        "comparison_rows": parse_comparison_rows(cross_model_md),
        "computed_reliability": reliability_analysis.build_cross_model_reliability_analysis(),
    }


def parse_gan_scorecard_dimensions(md_text: str) -> list[dict[str, Any]]:
    table = _table_by_header(
        parse_markdown_tables(md_text),
        ("#", "Dimension", "Cov.", "Computed metric (Phase 0)"),
    )
    dimensions = []
    for row in _rows_from_table(table):
        coverage, coverage_max = _parse_fraction(row.get("cov", ""))
        dimension = row.get("dimension", "")
        dimensions.append(
            {
                "id": _slug(dimension),
                "number": int(_as_float(row.get("", "")) or len(dimensions) + 1),
                "dimension": dimension,
                "coverage": coverage,
                "coverage_max": coverage_max,
                "current_evidence": row.get("computed_metric_phase_0", ""),
                "gap_to_close": _gan_gap_to_close(dimension),
                "strength": _coverage_strength(coverage, coverage_max),
            }
        )
    return dimensions


def _gan_gap_to_close(dimension: str) -> str:
    gaps = {
        "Task correctness": (
            "Keep validation/test distinction visible; do not turn reliability "
            "evidence into new tuning."
        ),
        "Factuality (over-inference)": (
            "Normalize over-read residuals by hidden family and selected-evidence pattern."
        ),
        "Faithfulness": "Preserve exact-evidence reporting beside faithful-but-wrong analysis.",
        "Calibration": "Keep external confidence separate from degenerate self-confidence signals.",
        "Abstention": "Choose operating points by review burden, not only by curve quality.",
        "Robustness": (
            "Keep overfit-gap and perturbation panels separate from primary accuracy claims."
        ),
        "Consistency": "Add only predeclared resampling panels if paper claims require them.",
        "Safety & compliance": (
            "Maintain aggregate-only locked-test readout and no row-level test inspection."
        ),
        "Fairness (clinical family)": (
            "Convert family spread into review-routing burden and residual subtype metrics."
        ),
        "Operational reliability": (
            "Complete latency/retry measurement if operational deployment is claimed."
        ),
    }
    return gaps.get(dimension, "Name the next frozen metric before upgrading this dimension.")


def build_gan_reliability_scorecard_payload(
    *,
    scorecard_path: Path = GAN_RELIABILITY_SCORECARD_PATH,
) -> dict[str, Any]:
    scorecard_md = load_markdown(scorecard_path)
    dimensions = parse_gan_scorecard_dimensions(scorecard_md)
    return {
        "dataset": "gan2026",
        "generated_on": date.today().isoformat(),
        "source_scorecard": scorecard_path.as_posix(),
        "source_cross_model_report": "",
        "evidence_set": [
            {
                "role": "Canonical reliability subject",
                "candidate": "single GPT structured-event pass v0_reference",
                "surface": "validation + locked-test aggregate reliability package",
                "overall_f1": None,
                "decision": "Reliability subject",
            }
        ],
        "dimensions": dimensions,
        "weak_dimensions": [
            dimension for dimension in dimensions if dimension.get("strength") == "weak"
        ],
        "metrics_available_now": [
            {
                "metric": dimension["dimension"],
                "current_status": dimension["current_evidence"],
            }
            for dimension in dimensions
        ],
        "residual_risks": [
            {
                "family": "SeizureFrequency",
                "current_strength": "Faithfulness, abstention, and consistency are well populated.",
                "residual_risk": (
                    "Confident over-reading remains the central residual; self-confidence "
                    "is not useful as a guardrail without external corroboration."
                ),
            }
        ],
        "upgrade_plan": [
            {
                "dimension": dimension["dimension"],
                "next_metric_needed": dimension["gap_to_close"],
            }
            for dimension in dimensions
            if dimension.get("strength") != "strong"
        ],
        "comparison_rows": [],
    }


@lru_cache(maxsize=1)
def cached_reliability_scorecard_payload() -> dict[str, Any]:
    return build_reliability_scorecard_payload()


@lru_cache(maxsize=1)
def cached_reliability_scorecard_json() -> str:
    return json.dumps(cached_reliability_scorecard_payload(), ensure_ascii=False)


@lru_cache(maxsize=1)
def cached_gan_reliability_scorecard_payload() -> dict[str, Any]:
    return build_gan_reliability_scorecard_payload()


@lru_cache(maxsize=1)
def cached_gan_reliability_scorecard_json() -> str:
    return json.dumps(cached_gan_reliability_scorecard_payload(), ensure_ascii=False)
