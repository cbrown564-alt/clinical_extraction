"""Materialize Stage 4 H6/H9 action-policy sidecars.

These sidecars are instrumentation only. They summarize saved validation
artifacts and do not change labels, call models, or inspect locked-test rows.
"""

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

DEFAULT_ASSEMBLED_JSONL_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.jsonl"
)
DEFAULT_ASSEMBLED_JSON_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.json"
)
DEFAULT_BOUNDARY_REVISION_JSON_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json"
)
DEFAULT_ACTION_SUMMARY_JSON_PATH = Path(
    "experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json"
)
DEFAULT_ACTION_SUMMARY_REPORT_PATH = Path(
    "experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.md"
)
DEFAULT_RELEASE_ABLATION_JSON_PATH = Path(
    "experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json"
)
DEFAULT_RELEASE_ABLATION_REPORT_PATH = Path(
    "experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.md"
)
DEFAULT_H6_REPLAY_JSON_PATH = Path("experiments/gan2026_h6_control_replay_v1_2026-06-05.json")
DEFAULT_H6_REPLAY_REPORT_PATH = Path("experiments/gan2026_h6_control_replay_v1_2026-06-05.md")

NONPREDICTION_ACTIONS = {"abstain", "human_review"}


def build_action_summary_sidecar(
    candidate_rows_by_name: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Summarize prediction coverage and action burden for saved candidates."""

    candidates = [
        _candidate_action_summary(name, rows)
        for name, rows in sorted(candidate_rows_by_name.items())
    ]
    return {
        "artifact_kind": "gan2026_h9_action_summary_sidecar_v1",
        "date": "2026-06-05",
        "hypothesis_ids": ["H9"],
        "split_manifest": _first_nonempty(candidate["split_manifest"] for candidate in candidates),
        "inspection_policy": "validation_artifact_sidecar_no_prediction_change",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "locked_test_row_level_artifacts_used": 0,
        "model_calls": 0,
        "prediction_changes": 0,
        "decision": (
            "h9_action_summary_sidecar_v1_complete"
            if candidates
            else "h9_action_summary_sidecar_v1_missing_candidates"
        ),
        "claim_boundary": (
            "Stage 4 action-policy sidecar over saved validation artifacts. It "
            "reports coverage, abstain/review burden, release lane, fallback "
            "owner, and family-specific action rates without changing candidate "
            "predictions or using locked-test row-level information."
        ),
    }


def build_release_lane_ablation(
    assembled_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Release one action lane at a time over the current validation control."""

    lanes = []
    for lane in ("abstain", "human_review"):
        release_rows = [
            row
            for row in assembled_rows
            if row.get("release_eligible") is True and row.get("original_staged_action") == lane
        ]
        lanes.append(_release_lane_summary(lane, release_rows))

    h6_regressions = sum(row["h6_regression_rows"] for row in lanes)
    c_to_w_rows = sum(row["c_to_w_rows"] for row in lanes)
    w_to_c_rows = sum(row["w_to_c_rows"] for row in lanes)
    release_rows_count = sum(row["release_rows"] for row in lanes)
    return {
        "artifact_kind": "gan2026_h9_release_lane_ablation_v1",
        "date": "2026-06-05",
        "hypothesis_ids": ["H6", "H9"],
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in assembled_rows),
        "source_candidate": _first_nonempty(row.get("candidate_version") for row in assembled_rows),
        "surface": "validation_hard_control_rows_from_current_assembled_control",
        "one_change": "release_one_existing_nonprediction_lane_at_a_time",
        "lanes": lanes,
        "release_rows": release_rows_count,
        "release_correct_rows": w_to_c_rows,
        "release_wrong_rows": c_to_w_rows,
        "changed_label_precision": _rate(w_to_c_rows, w_to_c_rows + c_to_w_rows),
        "h6_regression_rows": h6_regressions,
        "c_to_w_rows": c_to_w_rows,
        "w_to_c_rows": w_to_c_rows,
        "locked_test_row_level_artifacts_used": 0,
        "model_calls": 0,
        "prediction_changes": 0,
        "decision": (
            "h9_release_lane_ablation_v1_passed_guardrail"
            if release_rows_count and h6_regressions == 0 and c_to_w_rows == 0
            else "h9_release_lane_ablation_v1_rejected_or_narrow"
        ),
        "claim_boundary": (
            "Validation-development release-lane ablation. Each lane replays an "
            "already saved deterministic fallback release independently; no "
            "semantic repair, boundary/renderer, prompt, model, parser, scorer, "
            "or locked-test policy changes are made."
        ),
    }


def build_h6_control_replay(
    candidate_summaries_by_name: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Check H6 no-regression accounting across Stage 4 candidate summaries."""

    candidates = []
    for name, summary in sorted(candidate_summaries_by_name.items()):
        correct = _int(summary.get("release_correct_rows") or summary.get("w_to_c_rows"))
        wrong = _int(summary.get("release_wrong_rows") or summary.get("c_to_w_rows"))
        changed = correct + wrong
        candidates.append(
            {
                "candidate": name,
                "h6_control_rows": _int(summary.get("h6_control_rows")),
                "h6_regression_rows": _int(
                    summary.get("h6_control_regression_rows") or summary.get("h6_regression_rows")
                ),
                "changed_correct_rows": correct,
                "changed_wrong_rows": wrong,
                "changed_label_precision": _rate(correct, changed),
                "source_decision": summary.get("decision", ""),
            }
        )

    failed = [row for row in candidates if row["h6_regression_rows"] > 0]
    return {
        "artifact_kind": "gan2026_h6_control_replay_v1",
        "date": "2026-06-05",
        "hypothesis_ids": ["H6", "H9"],
        "split_manifest": "gan2026_split_v1",
        "inspection_policy": "validation_sidecar_no_candidate_change",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "h6_regression_candidates": [row["candidate"] for row in failed],
        "locked_test_row_level_artifacts_used": 0,
        "model_calls": 0,
        "prediction_changes": 0,
        "decision": (
            "h6_control_replay_v1_passed"
            if candidates and not failed
            else "h6_control_replay_v1_failed"
        ),
        "claim_boundary": (
            "Stage 4 H6 replay sidecar. It verifies no H6 control regression "
            "from saved validation summaries and reports changed-label precision "
            "where summary-level changed-row counts are available."
        ),
    }


def materialize_stage4_sidecars(
    *,
    assembled_jsonl_path: Path = DEFAULT_ASSEMBLED_JSONL_PATH,
    assembled_json_path: Path = DEFAULT_ASSEMBLED_JSON_PATH,
    boundary_revision_json_path: Path = DEFAULT_BOUNDARY_REVISION_JSON_PATH,
    action_summary_json_path: Path = DEFAULT_ACTION_SUMMARY_JSON_PATH,
    action_summary_report_path: Path = DEFAULT_ACTION_SUMMARY_REPORT_PATH,
    release_ablation_json_path: Path = DEFAULT_RELEASE_ABLATION_JSON_PATH,
    release_ablation_report_path: Path = DEFAULT_RELEASE_ABLATION_REPORT_PATH,
    h6_replay_json_path: Path = DEFAULT_H6_REPLAY_JSON_PATH,
    h6_replay_report_path: Path = DEFAULT_H6_REPLAY_REPORT_PATH,
) -> dict[str, Any]:
    assembled_rows = load_jsonl_rows(assembled_jsonl_path)
    assembled_summary = _load_json(assembled_json_path)
    boundary_revision_summary = _load_json(boundary_revision_json_path)

    action_summary = build_action_summary_sidecar(
        {"untagged_nonprediction_release_candidate_v0_assembled_candidate": (assembled_rows)}
    )
    action_summary = {
        **action_summary,
        "source_artifacts": {"assembled_candidate_jsonl": str(assembled_jsonl_path)},
        "json_artifact": str(action_summary_json_path),
        "report_artifact": str(action_summary_report_path),
    }

    release_ablation = build_release_lane_ablation(assembled_rows)
    release_ablation = {
        **release_ablation,
        "source_artifacts": {"assembled_candidate_jsonl": str(assembled_jsonl_path)},
        "json_artifact": str(release_ablation_json_path),
        "report_artifact": str(release_ablation_report_path),
    }

    h6_replay = build_h6_control_replay(
        {
            "untagged_nonprediction_release_candidate_v0_assembled_candidate": (assembled_summary),
            "boundary_selector_precision_revision_v1": boundary_revision_summary,
            "h9_release_lane_ablation_v1": release_ablation,
        }
    )
    h6_replay = {
        **h6_replay,
        "source_artifacts": {
            "assembled_candidate_summary": str(assembled_json_path),
            "boundary_selector_precision_revision_summary": str(boundary_revision_json_path),
            "release_lane_ablation_summary": str(release_ablation_json_path),
        },
        "json_artifact": str(h6_replay_json_path),
        "report_artifact": str(h6_replay_report_path),
    }

    _write_json(action_summary, action_summary_json_path)
    _write_action_summary_report(action_summary, action_summary_report_path)
    _write_json(release_ablation, release_ablation_json_path)
    _write_release_ablation_report(release_ablation, release_ablation_report_path)
    _write_json(h6_replay, h6_replay_json_path)
    _write_h6_replay_report(h6_replay, h6_replay_report_path)

    return {
        "action_summary": action_summary,
        "release_lane_ablation": release_ablation,
        "h6_control_replay": h6_replay,
    }


def _candidate_action_summary(
    name: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    total = len(rows)
    prediction_rows = [row for row in rows if row.get("candidate_action") == "predict"]
    abstain_rows = [row for row in rows if row.get("candidate_action") == "abstain"]
    review_rows = [row for row in rows if row.get("candidate_action") == "human_review"]
    release_rows = [row for row in rows if row.get("release_applied") is True]
    return {
        "candidate": name,
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in rows),
        "rows": total,
        "prediction_bearing_rows": len(prediction_rows),
        "prediction_bearing_coverage": _rate(len(prediction_rows), total),
        "correct_prediction_rows": sum(
            row.get("candidate_purist_correct") is True for row in prediction_rows
        ),
        "abstain_rows": len(abstain_rows),
        "review_rows": len(review_rows),
        "nonprediction_rows": len(abstain_rows) + len(review_rows),
        "release_rows": len(release_rows),
        "release_lane_counts": dict(
            Counter(str(row.get("original_staged_action")) for row in release_rows)
        ),
        "fallback_owner_counts": dict(
            Counter(str(row.get("component_owner")) for row in release_rows)
        ),
        "owner_action_rates": _owner_action_rates(rows),
        "family_action_rates": _family_action_rates(rows),
    }


def _owner_action_rates(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("component_owner") or "unknown")].append(row)
    return [
        _action_rate_row("owner", owner, owner_rows)
        for owner, owner_rows in sorted(grouped.items())
    ]


def _family_action_rates(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        families = [str(family) for family in row.get("hidden_families", []) if family]
        for family in families or ["unclassified"]:
            grouped[family].append(row)
    return [
        _action_rate_row("family", family, family_rows)
        for family, family_rows in sorted(grouped.items())
    ]


def _action_rate_row(
    key: str,
    value: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    total = len(rows)
    nonprediction = [row for row in rows if row.get("candidate_action") in NONPREDICTION_ACTIONS]
    return {
        key: value,
        "rows": total,
        "prediction_bearing_rows": sum(row.get("candidate_action") == "predict" for row in rows),
        "nonprediction_rows": len(nonprediction),
        "nonprediction_rate": _rate(len(nonprediction), total),
        "abstain_rows": sum(row.get("candidate_action") == "abstain" for row in rows),
        "review_rows": sum(row.get("candidate_action") == "human_review" for row in rows),
    }


def _release_lane_summary(
    lane: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    h6_controls = [
        row
        for row in rows
        if row.get("h6_member") is True and row.get("h6_panel_role") == "control"
    ]
    transition_counts = Counter(str(row.get("baseline_transition")) for row in rows)
    correct = sum(row.get("candidate_purist_correct") is True for row in rows)
    wrong = sum(row.get("candidate_purist_correct") is False for row in rows)
    return {
        "release_lane": lane,
        "release_rows": len(rows),
        "fallback_owner_counts": dict(
            Counter(str(row.get("component_owner") or "unknown") for row in rows)
        ),
        "transition_counts": dict(transition_counts),
        "w_to_c_rows": correct,
        "c_to_w_rows": wrong,
        "changed_label_precision": _rate(correct, correct + wrong),
        "h6_control_rows": len(h6_controls),
        "h6_regression_rows": sum(
            row.get("candidate_purist_correct") is not True for row in h6_controls
        ),
        "gate": (
            "passed_no_c_to_w_no_h6_regression"
            if wrong == 0
            and all(row.get("candidate_purist_correct") is True for row in h6_controls)
            else "failed_or_needs_narrowing"
        ),
    }


def _write_action_summary_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H9 Action Summary Sidecar v1",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Candidates",
        "",
        "| Candidate | Rows | Prediction-bearing | Coverage | Abstain | Review | Released |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in summary["candidates"]:
        lines.append(
            "| `{candidate}` | {rows} | {pb} | {coverage} | {abstain} | "
            "{review} | {released} |".format(
                candidate=candidate["candidate"],
                rows=candidate["rows"],
                pb=candidate["prediction_bearing_rows"],
                coverage=_format_rate(candidate["prediction_bearing_coverage"]),
                abstain=candidate["abstain_rows"],
                review=candidate["review_rows"],
                released=candidate["release_rows"],
            )
        )
    lines.extend(["", "## Inspection Boundary", "", str(summary["inspection_policy"]), ""])
    _write_text(lines, path)


def _write_release_ablation_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H9 Release Lane Ablation v1",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Lanes",
        "",
        "| Lane | Released | W->C | C->W | Precision | H6 controls | H6 regressions | Gate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for lane in summary["lanes"]:
        lines.append(
            "| `{lane}` | {released} | {wtoc} | {ctow} | {precision} | "
            "{h6} | {h6_reg} | `{gate}` |".format(
                lane=lane["release_lane"],
                released=lane["release_rows"],
                wtoc=lane["w_to_c_rows"],
                ctow=lane["c_to_w_rows"],
                precision=_format_rate(lane["changed_label_precision"]),
                h6=lane["h6_control_rows"],
                h6_reg=lane["h6_regression_rows"],
                gate=lane["gate"],
            )
        )
    lines.extend(["", "## Surface", "", str(summary["surface"]), ""])
    _write_text(lines, path)


def _write_h6_replay_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H6 Control Replay v1",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Candidates",
        "",
        "| Candidate | H6 controls | H6 regressions | Changed precision | Source decision |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for candidate in summary["candidates"]:
        lines.append(
            "| `{candidate}` | {h6} | {h6_reg} | {precision} | `{decision}` |".format(
                candidate=candidate["candidate"],
                h6=candidate["h6_control_rows"],
                h6_reg=candidate["h6_regression_rows"],
                precision=_format_rate(candidate["changed_label_precision"]),
                decision=candidate["source_decision"],
            )
        )
    _write_text(lines + [""], path)


def _write_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(lines: Sequence[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def _int(value: Any) -> int:
    return int(value or 0)


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembled-jsonl-path", type=Path, default=DEFAULT_ASSEMBLED_JSONL_PATH)
    parser.add_argument("--assembled-json-path", type=Path, default=DEFAULT_ASSEMBLED_JSON_PATH)
    parser.add_argument(
        "--boundary-revision-json-path",
        type=Path,
        default=DEFAULT_BOUNDARY_REVISION_JSON_PATH,
    )
    args = parser.parse_args(argv)
    materialize_stage4_sidecars(
        assembled_jsonl_path=args.assembled_jsonl_path,
        assembled_json_path=args.assembled_json_path,
        boundary_revision_json_path=args.boundary_revision_json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
