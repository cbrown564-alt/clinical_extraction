"""Reliability cell iteration for calibration and review routing."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import FAMILIES, RICH_SCHEMA_RUNS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    risk_features,
    risk_score as compute_risk_score,
    row_family_score,
)

def iter_reliability_cells(
    rich_rows: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for run in RICH_SCHEMA_RUNS:
        for row in rich_rows[run.candidate]:
            for family in FAMILIES:
                score = row_family_score(row, family)
                if score.pred_count == 0 and score.gold_count == 0:
                    continue
                features = risk_features(row, family)
                cell_risk_score = compute_risk_score(family, features)
                cells.append(
                    {
                        "candidate": run.candidate,
                        "model_label": run.model_label,
                        "letter_id": row["letter_id"],
                        "family": family,
                        "f1": score.f1,
                        "correct": score.fp == 0 and score.fn == 0,
                        "risk_score": cell_risk_score,
                        "confidence_proxy": round(1.0 - cell_risk_score, 4),
                        "features": features,
                    }
                )
    return cells
