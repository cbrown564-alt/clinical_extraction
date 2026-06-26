"""Predeclared review-routing analysis over reliability cells."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import review_triggers, round_rate

def review_routing(cells: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = caught = false_alarm = missed = total_errors = 0
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    trigger_counts: Counter[str] = Counter()
    for cell in cells:
        triggers = review_triggers(cell)
        is_error = not bool(cell["correct"])
        if is_error:
            total_errors += 1
        if triggers:
            reviewed += 1
            trigger_counts.update(triggers)
            by_family[str(cell["family"])]["reviewed_cells"] += 1
            if is_error:
                caught += 1
                by_family[str(cell["family"])]["caught_error_cells"] += 1
            else:
                false_alarm += 1
                by_family[str(cell["family"])]["false_alarm_cells"] += 1
        elif is_error:
            missed += 1
            by_family[str(cell["family"])]["missed_error_cells"] += 1
        by_family[str(cell["family"])]["eligible_cells"] += 1
        if is_error:
            by_family[str(cell["family"])]["total_error_cells"] += 1

    return {
        "definition": (
            "Predeclared dev-only review triggers over evidence-invalid cells, "
            "high proxy risk, source-to-final changes, and family-specific ambiguity cues."
        ),
        "eligible_cells": len(cells),
        "reviewed_cells": reviewed,
        "review_burden": round_rate(reviewed, len(cells)),
        "total_error_cells": total_errors,
        "caught_error_cells": caught,
        "catch_rate": round_rate(caught, total_errors),
        "false_alarm_cells": false_alarm,
        "missed_error_cells": missed,
        "operating_points": review_operating_points(cells),
        "trigger_counts": dict(sorted(trigger_counts.items())),
        "by_family": [
            {
                "family": family,
                **dict(counts),
                "review_burden": round_rate(
                    int(counts["reviewed_cells"]), int(counts["eligible_cells"])
                ),
                "catch_rate": round_rate(
                    int(counts["caught_error_cells"]), int(counts["total_error_cells"])
                ),
            }
            for family, counts in sorted(by_family.items())
        ],
    }


def review_operating_points(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = [
        operating_point_summary(
            cells,
            point_id="high_recall_predeclared",
            label="High-recall predeclared trigger net",
            rules=[
                "any current review trigger",
                "risk >= 0.35",
                "evidence invalid",
                "family-specific ambiguity cue",
            ],
            validation_status="dev replay only; not a promoted policy",
            review_fn=lambda cell: bool(review_triggers(cell)),
        ),
        operating_point_summary(
            cells,
            point_id="risk_ge_030",
            label="Risk proxy >= 0.30",
            rules=["risk >= 0.30"],
            validation_status="dev replay threshold scan",
            review_fn=lambda cell: float(cell["risk_score"]) >= 0.30,
        ),
        operating_point_summary(
            cells,
            point_id="balanced_dev_candidate",
            label="Balanced dev candidate",
            rules=[
                "risk >= 0.35",
                "source-to-final delta",
                "low confidence",
                "investigation result-state cue",
            ],
            validation_status="dev-tuned candidate; needs frozen validation",
            review_fn=lambda cell: (
                float(cell["risk_score"]) >= 0.35
                or bool(cell["features"]["source_final_delta"])
                or bool(cell["features"]["low_confidence"])
                or bool(cell["features"]["result_state"])
            ),
        ),
        operating_point_summary(
            cells,
            point_id="transition_focus",
            label="Transition-focused candidate",
            rules=[
                "source-to-final delta",
                "SF active-rate cue",
                "Prescription plan language",
                "Investigation result-state cue",
            ],
            validation_status="dev-tuned candidate; needs frozen validation",
            review_fn=lambda cell: (
                bool(cell["features"]["source_final_delta"])
                or (
                    cell["family"] == "SeizureFrequency"
                    and bool(cell["features"]["active_rate"])
                )
                or (
                    cell["family"] == "Prescription"
                    and bool(cell["features"]["plan_language"])
                )
                or bool(cell["features"]["result_state"])
            ),
        ),
    ]
    high_recall = points[0]
    for point in points:
        point["review_burden_delta_vs_high_recall"] = round(
            float(point["review_burden"]) - float(high_recall["review_burden"]),
            4,
        )
        point["catch_rate_delta_vs_high_recall"] = round(
            float(point["catch_rate"]) - float(high_recall["catch_rate"]),
            4,
        )
    return points


def operating_point_summary(
    cells: list[dict[str, Any]],
    *,
    point_id: str,
    label: str,
    rules: list[str],
    validation_status: str,
    review_fn: Any,
) -> dict[str, Any]:
    reviewed_cells = [cell for cell in cells if review_fn(cell)]
    total_errors = sum(1 for cell in cells if not cell["correct"])
    caught = sum(1 for cell in reviewed_cells if not cell["correct"])
    false_alarm = sum(1 for cell in reviewed_cells if cell["correct"])
    missed = total_errors - caught
    return {
        "id": point_id,
        "label": label,
        "rules": rules,
        "validation_status": validation_status,
        "eligible_cells": len(cells),
        "reviewed_cells": len(reviewed_cells),
        "review_burden": round_rate(len(reviewed_cells), len(cells)),
        "total_error_cells": total_errors,
        "caught_error_cells": caught,
        "catch_rate": round_rate(caught, total_errors),
        "false_alarm_cells": false_alarm,
        "false_alarm_rate": round_rate(false_alarm, len(reviewed_cells)),
        "missed_error_cells": missed,
    }
