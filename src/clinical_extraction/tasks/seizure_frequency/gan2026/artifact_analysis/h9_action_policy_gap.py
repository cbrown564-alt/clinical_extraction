"""Test H9 action-policy pressure across validation and aggregate test surfaces."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_MATRIX_PATH = Path(
    "experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl"
)
DEFAULT_H1_PATH = Path("experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.json")
DEFAULT_TEST_NONPREDICTION_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v0_"
    "test450_nonprediction_selector_aggregate_audit_2026-06-05.json"
)
DEFAULT_JSON_PATH = Path("experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.md")

POLICY_NAME = "gan2026_h9_action_policy_gap_v0"
PREDICTION_ACTION = ""


def build_h9_action_policy_gap(
    matrix_rows: Sequence[Mapping[str, Any]],
    *,
    h1_summary: Mapping[str, Any] | None = None,
    test_nonprediction_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an H9 readout without writing locked-test row-level details."""

    final_rows = [row for row in matrix_rows if row.get("score_layer") == "final_policy"]
    monitor_rows = [
        row for row in matrix_rows if row.get("score_layer") == "abstain_review_monitor"
    ]
    validation = _validation_summary(final_rows, monitor_rows)
    locked_test = _locked_test_summary(
        h1_summary=h1_summary or {},
        test_nonprediction_summary=test_nonprediction_summary or {},
    )
    decision = _decision(validation, locked_test)
    return {
        "artifact_kind": POLICY_NAME,
        "date": "2026-06-05",
        "hypothesis_id": "H9",
        "hypothesis": "Abstention/review policy hides different failure modes by split.",
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in matrix_rows),
        "inspection_policy": {
            "validation": "row_level_allowed",
            "locked_test": "aggregate_only_no_row_level_failure_records_written",
        },
        "source_artifacts": {
            "validation_gap_matrix": str(DEFAULT_MATRIX_PATH),
            "h1_family_aggregate": str(DEFAULT_H1_PATH),
            "locked_test_nonprediction_aggregate": str(DEFAULT_TEST_NONPREDICTION_PATH),
        },
        "validation": validation,
        "locked_test": locked_test,
        "support_signal": {
            "action_rate_shift": (
                (locked_test.get("router_metrics", {}).get("nonprediction_rate") or 0.0)
                - validation["overall"]["nonprediction_rate"]
            ),
            "validation_actions_related_to_blocked_baseline_misses": (
                validation["overall"]["blocked_baseline_wrong_rows"] > 0
            ),
            "validation_actions_related_to_overblocking": (
                validation["overall"]["blocked_baseline_correct_rows"] > 0
            ),
            "test_owner_family_resolution_available": False,
        },
        "decision": decision,
        "interpretation": _interpretation(decision),
        "recommended_next_step": _recommended_next_step(decision),
        "locked_test_row_level_artifacts_written": 0,
        "claim_boundary": (
            "H9 no-call validation plus aggregate-only locked-test readout. "
            "Validation action rows may be inspected, but locked-test output is "
            "limited to predeclared aggregate action/family summaries and writes "
            "no test row ids, note text, raw model outputs, or row-level failures."
        ),
    }


def write_h9_report(summary: Mapping[str, Any], path: Path) -> None:
    """Write a compact Markdown H9 artifact report."""

    validation = summary["validation"]
    locked_test = summary["locked_test"]
    lines = [
        "# Gan 2026 H9 Action-Policy Gap v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Interpretation",
        "",
        str(summary["interpretation"]),
        "",
        "## Overall Action Pressure",
        "",
        "| Split | Rows | Nonprediction rows | Nonprediction rate | Abstain | Review | "
        "Blocked baseline-correct | Blocked baseline-wrong |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    overall = validation["overall"]
    test_router = locked_test.get("router_metrics", {})
    lines.append(
        "| validation750 | {rows} | {nonprediction_rows} | {rate} | {abstain} | "
        "{review} | {blocked_correct} | {blocked_wrong} |".format(
            rows=overall["rows"],
            nonprediction_rows=overall["nonprediction_rows"],
            rate=_format_rate(overall["nonprediction_rate"]),
            abstain=overall["abstain_rows"],
            review=overall["human_review_rows"],
            blocked_correct=overall["blocked_baseline_correct_rows"],
            blocked_wrong=overall["blocked_baseline_wrong_rows"],
        )
    )
    lines.append(
        "| locked_test450 | {rows} | {nonprediction_rows} | {rate} | {abstain} | "
        "{review} |  |  |".format(
            rows=test_router.get("rows", ""),
            nonprediction_rows=test_router.get("nonprediction_rows", ""),
            rate=_format_rate(test_router.get("nonprediction_rate")),
            abstain=test_router.get("abstain_rows", ""),
            review=test_router.get("human_review_rows", ""),
        )
    )

    lines.extend(
        [
            "",
            "## Validation By Action Reason",
            "",
            "| Reason | Rows | Abstain | Review | Rate | Blocked C | Blocked W |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in validation["by_reason"]:
        lines.append(
            "| `{reason}` | {rows} | {abstain} | {review} | {rate} | "
            "{blocked_correct} | {blocked_wrong} |".format(
                reason=row["reason"],
                rows=row["rows"],
                abstain=row["abstain_rows"],
                review=row["human_review_rows"],
                rate=_format_rate(row["nonprediction_rate"]),
                blocked_correct=row["blocked_baseline_correct_rows"],
                blocked_wrong=row["blocked_baseline_wrong_rows"],
            )
        )

    lines.extend(
        [
            "",
            "## Validation By Hidden Family",
            "",
            "| Family | Rows | Nonprediction rows | Nonprediction rate | Blocked C | "
            "Blocked W |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in validation["by_hidden_family"]:
        lines.append(
            "| `{family}` | {rows} | {nonprediction_rows} | {rate} | "
            "{blocked_correct} | {blocked_wrong} |".format(
                family=row["family"],
                rows=row["rows"],
                nonprediction_rows=row["nonprediction_rows"],
                rate=_format_rate(row["nonprediction_rate"]),
                blocked_correct=row["blocked_baseline_correct_rows"],
                blocked_wrong=row["blocked_baseline_wrong_rows"],
            )
        )

    lines.extend(
        [
            "",
            "## Test Aggregate Family Context",
            "",
            "| Family | Test rows | Test proxy | Test changed rate | Validation-test proxy gap |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in locked_test.get("family_aggregate_context", []):
        lines.append(
            "| `{family}` | {rows} | {proxy} | {changed_rate} | {gap} |".format(
                family=row["family"],
                rows=row["test_rows"],
                proxy=_format_rate(row["test_purist_proxy"]),
                changed_rate=_format_rate(row["test_changed_rate"]),
                gap=_format_rate(row["validation_minus_test_gap"]),
            )
        )

    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "Locked-test family rows above are aggregate-only and come from predeclared "
            "H1/frozen selector summaries. This artifact does not resolve test "
            "row-level owner/failure mechanisms.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def materialize_h9_action_policy_gap(
    *,
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    h1_path: Path = DEFAULT_H1_PATH,
    test_nonprediction_path: Path = DEFAULT_TEST_NONPREDICTION_PATH,
    output_json_path: Path = DEFAULT_JSON_PATH,
    output_report_path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    h1_summary = _load_json(h1_path)
    test_nonprediction_summary = _load_json(test_nonprediction_path)
    summary = build_h9_action_policy_gap(
        load_jsonl_rows(matrix_path),
        h1_summary=h1_summary,
        test_nonprediction_summary=test_nonprediction_summary,
    )
    summary = {
        **summary,
        "source_artifacts": {
            "validation_gap_matrix": str(matrix_path),
            "h1_family_aggregate": str(h1_path),
            "locked_test_nonprediction_aggregate": str(test_nonprediction_path),
        },
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_h9_report(summary, output_report_path)
    return summary


def _validation_summary(
    final_rows: Sequence[Mapping[str, Any]],
    monitor_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    total_rows = len(final_rows)
    return {
        "overall": _summarize_action_group(monitor_rows, denominator=total_rows),
        "by_reason": _by_reason(monitor_rows, denominator=total_rows),
        "by_hidden_family": _by_hidden_family(final_rows, monitor_rows),
        "by_component_owner": _by_component_owner(final_rows, monitor_rows),
    }


def _locked_test_summary(
    *,
    h1_summary: Mapping[str, Any],
    test_nonprediction_summary: Mapping[str, Any],
) -> dict[str, Any]:
    router_metrics = test_nonprediction_summary.get("router_metrics", {})
    rows = int(
        router_metrics.get("eligible_rows")
        or test_nonprediction_summary.get("base_total_rows")
        or test_nonprediction_summary.get("row_count")
        or 0
    )
    abstain_rows = int(router_metrics.get("abstained_rows") or 0)
    human_review_rows = int(router_metrics.get("human_review_rows") or 0)
    nonprediction_rows = abstain_rows + human_review_rows
    return {
        "source_artifact": test_nonprediction_summary.get("source_artifact", ""),
        "inspection_policy": test_nonprediction_summary.get("inspection_policy", ""),
        "router_metrics": {
            "rows": rows,
            "nonprediction_rows": nonprediction_rows,
            "nonprediction_rate": _rate(nonprediction_rows, rows),
            "abstain_rows": abstain_rows,
            "human_review_rows": human_review_rows,
            "coverage": router_metrics.get("coverage"),
            "selective_accuracy": router_metrics.get("selective_accuracy"),
        },
        "family_aggregate_context": _test_family_context(h1_summary),
        "known_gap": (
            "Locked-test aggregate artifacts expose action counts and predeclared "
            "family correctness, but not component-owner-by-family nonprediction "
            "failure rows."
        ),
    }


def _by_reason(
    monitor_rows: Sequence[Mapping[str, Any]], *, denominator: int
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in monitor_rows:
        grouped[str(row.get("abstain_review_monitor_reason") or "unknown")].append(row)
    return [
        {"reason": reason, **_summarize_action_group(rows, denominator=denominator)}
        for reason, rows in sorted(grouped.items())
    ]


def _by_hidden_family(
    final_rows: Sequence[Mapping[str, Any]],
    monitor_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    denominator: Counter[str] = Counter()
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in final_rows:
        for family in _families(row):
            denominator[family] += 1
    for row in monitor_rows:
        for family in _families(row):
            grouped[family].append(row)
    return [
        {
            "family": family,
            **_summarize_action_group(grouped.get(family, []), denominator=rows),
        }
        for family, rows in sorted(denominator.items())
        if family != "all_rows"
    ]


def _by_component_owner(
    final_rows: Sequence[Mapping[str, Any]],
    monitor_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    denominator = Counter(str(row.get("component_owner") or "unknown") for row in final_rows)
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in monitor_rows:
        grouped[str(row.get("component_owner") or "unknown")].append(row)
    return [
        {
            "component_owner": owner,
            **_summarize_action_group(grouped.get(owner, []), denominator=rows),
        }
        for owner, rows in sorted(denominator.items())
    ]


def _summarize_action_group(
    rows: Sequence[Mapping[str, Any]], *, denominator: int
) -> dict[str, Any]:
    action_counts = Counter(str(row.get("abstain_review_monitor_action") or "") for row in rows)
    blocked_correct = sum(row.get("baseline_purist_correct") is True for row in rows)
    blocked_wrong = sum(row.get("baseline_purist_correct") is False for row in rows)
    return {
        "rows": denominator,
        "nonprediction_rows": len(rows),
        "nonprediction_rate": _rate(len(rows), denominator),
        "abstain_rows": action_counts["abstain"],
        "human_review_rows": action_counts["human_review"],
        "blocked_baseline_correct_rows": blocked_correct,
        "blocked_baseline_wrong_rows": blocked_wrong,
        "blocked_baseline_correct_rate": _rate(blocked_correct, len(rows)),
        "blocked_baseline_wrong_rate": _rate(blocked_wrong, len(rows)),
    }


def _test_family_context(h1_summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in h1_summary.get("family_gaps", []):
        rows.append(
            {
                "family": row.get("family", ""),
                "test_rows": row.get("test_rows", 0),
                "test_purist_proxy": row.get("test_purist_proxy"),
                "test_changed_rate": row.get("test_changed_rate"),
                "validation_minus_test_gap": row.get("validation_minus_test_gap"),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -(row.get("test_changed_rate") or 0.0),
            -(row.get("validation_minus_test_gap") or 0.0),
        ),
    )


def _families(row: Mapping[str, Any]) -> list[str]:
    families = [str(family) for family in row.get("hidden_families", []) if family]
    return families or ["unclassified"]


def _decision(validation: Mapping[str, Any], locked_test: Mapping[str, Any]) -> str:
    validation_rate = validation["overall"]["nonprediction_rate"]
    test_rate = locked_test.get("router_metrics", {}).get("nonprediction_rate") or 0.0
    blocked_correct = validation["overall"]["blocked_baseline_correct_rows"]
    if validation_rate > 0.03 and test_rate < 0.01 and blocked_correct:
        return "h9_partially_supported_action_policy_shift_not_primary_gap_explanation"
    if abs(validation_rate - test_rate) <= 0.01:
        return "h9_rejected_action_rates_stable"
    return "h9_inconclusive_instrumentation_gap"


def _interpretation(decision: str) -> str:
    if decision == "h9_partially_supported_action_policy_shift_not_primary_gap_explanation":
        return (
            "Validation action policy is not neutral: nonprediction/review rows are "
            "safety-floor-owned and frequently block deterministic-correct labels. "
            "The locked-test aggregate selector surface has much lower nonprediction "
            "burden, while the test accuracy gap remains large, so H9 is supported "
            "as an action-policy shift but not as the primary explanation for the "
            "validation-test generalisation gap."
        )
    if decision == "h9_rejected_action_rates_stable":
        return (
            "Action rates appear stable across the available aggregate surfaces, so "
            "H9 should not lead the next mechanism work."
        )
    return (
        "The available artifacts are insufficient to decide H9 because the locked "
        "test side lacks owner-by-family action/failure summaries."
    )


def _recommended_next_step(decision: str) -> str:
    if decision == "h9_partially_supported_action_policy_shift_not_primary_gap_explanation":
        return (
            "Keep action policy as a guardrail and report validation overblocking, "
            "but prioritize H3/H7 candidate exposure and template-brittleness work. "
            "Before any frozen test audit, predeclare aggregate owner/family action "
            "summaries so H9 can be tested without row-level holdout inspection."
        )
    return (
        "Add aggregate owner/family action fields to the next frozen audit protocol "
        "before using H9 for architecture decisions."
    )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _format_rate(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _first_nonempty(values: Sequence[Any]) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX_PATH)
    parser.add_argument("--h1", type=Path, default=DEFAULT_H1_PATH)
    parser.add_argument(
        "--test-nonprediction",
        type=Path,
        default=DEFAULT_TEST_NONPREDICTION_PATH,
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--output-report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_h9_action_policy_gap(
        matrix_path=args.matrix,
        h1_path=args.h1,
        test_nonprediction_path=args.test_nonprediction,
        output_json_path=args.output_json,
        output_report_path=args.output_report,
    )


if __name__ == "__main__":
    main()
