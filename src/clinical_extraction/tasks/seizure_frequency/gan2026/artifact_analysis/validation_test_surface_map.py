"""Build aggregate validation-test surface maps from predeclared artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def build_surface_map(
    inventory: Mapping[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    """Summarize inventory artifacts without exposing locked-test row details."""

    artifact_summaries = [
        _summarize_inventory_artifact(artifact, root=root)
        for artifact in inventory.get("artifacts", [])
    ]

    return {
        "artifact_kind": "gan2026_validation_test_surface_map_v0",
        "inventory_id": inventory.get("inventory_id", ""),
        "split_manifest": inventory.get("split_manifest", ""),
        "protocol": inventory.get("protocol", ""),
        "inspection_policy": inventory.get("inspection_policy", {}),
        "surface_count": len(artifact_summaries),
        "surface_summaries": artifact_summaries,
        "candidate_gap_summary": _candidate_gap_summary(artifact_summaries),
        "distribution_summary": _distribution_summary(artifact_summaries),
        "known_gaps": [
            "Metrics are aggregate-only and depend on fields present in saved artifacts.",
            "Locked-test summaries intentionally omit row-level records.",
            "Candidate gaps are computed only when comparable validation and locked-test "
            "final Purist proxies are available.",
        ],
    }


def write_surface_map_json(surface_map: Mapping[str, Any], path: Path) -> None:
    path.write_text(json.dumps(surface_map, indent=2, sort_keys=True) + "\n")


def write_surface_map_report(surface_map: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Validation-Test Surface Map v0",
        "",
        f"Split manifest: `{surface_map.get('split_manifest', '')}`",
        "",
        "This report is aggregate-only for locked test surfaces. It does not expose "
        "locked-test row-level failures.",
        "",
        "## Candidate Gap Summary",
        "",
    ]

    gaps = surface_map.get("candidate_gap_summary", [])
    if gaps:
        lines.extend(
            [
                "| Candidate | Validation proxy | Test proxy | Gap | Validation rows | Test rows |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for gap in gaps:
            lines.append(
                "| {candidate} | {validation_final_purist_proxy} | "
                "{test_final_purist_proxy} | {validation_minus_test_gap} | "
                "{validation_rows} | {test_rows} |".format(
                    candidate=_md(gap["candidate_name"]),
                    validation_final_purist_proxy=_format_metric(
                        gap.get("validation_final_purist_proxy")
                    ),
                    test_final_purist_proxy=_format_metric(
                        gap.get("test_final_purist_proxy")
                    ),
                    validation_minus_test_gap=_format_metric(
                        gap.get("validation_minus_test_gap")
                    ),
                    validation_rows=_md(gap.get("validation_rows")),
                    test_rows=_md(gap.get("test_rows")),
                )
            )
    else:
        lines.append("No comparable validation/test proxy pairs were available.")

    lines.extend(["", "## Surface Summaries", ""])
    lines.extend(
        [
            "| Artifact | Distribution | Rows | Final proxy | Changed | W->C | C->W | Inspection |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for summary in surface_map.get("surface_summaries", []):
        lines.append(
            "| {artifact_id} | {distribution} | {rows} | {proxy} | {changed} | "
            "{wtc} | {ctw} | {inspection} |".format(
                artifact_id=_md(summary.get("artifact_id")),
                distribution=_md(summary.get("distribution")),
                rows=_md(summary.get("total_rows")),
                proxy=_format_metric(summary.get("final_purist_proxy")),
                changed=_md(summary.get("changed_rows")),
                wtc=_md(summary.get("wrong_to_correct")),
                ctw=_md(summary.get("correct_to_wrong")),
                inspection=_md(summary.get("allowed_inspection")),
            )
        )

    lines.extend(["", "## Known Gaps", ""])
    for gap in surface_map.get("known_gaps", []):
        lines.append(f"- {gap}")

    path.write_text("\n".join(lines) + "\n")


def _summarize_inventory_artifact(
    artifact: Mapping[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    json_path = _first_existing_json_path(artifact.get("paths", []), root=root)
    payload = _load_json(json_path) if json_path is not None else {}
    metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}

    total_rows = _first_number(
        payload,
        metrics,
        [
            "base_total_rows",
            "row_count",
            "total_rows",
            "test_rows",
        ],
    )
    final_correct = _first_number(
        payload,
        metrics,
        [
            "final_correct_rows",
            "projected_correct_rows",
            "contract_projected_correct_rows",
            "combined_current_correct_rows",
            "current_correct_rows",
            "prediction_bearing_rows",
        ],
    )
    baseline_correct = _first_number(
        payload,
        metrics,
        [
            "base_correct_rows",
            "raw_base_correct_rows",
            "current_correct_rows",
        ],
    )
    final_proxy = _first_number(
        payload,
        metrics,
        [
            "final_purist_proxy",
            "projected_purist_proxy",
            "projected_full_row_purist_proxy",
            "contract_projected_purist_proxy",
            "combined_current_purist_proxy",
            "current_purist_proxy",
        ],
    )
    baseline_proxy = _first_number(
        payload,
        metrics,
        [
            "base_purist_proxy",
            "base_full_row_purist_proxy",
            "raw_base_purist_proxy",
            "current_purist_proxy",
        ],
    )
    transition_counts = _transition_counts(payload)

    return {
        "artifact_id": artifact.get("artifact_id", ""),
        "candidate_name": artifact.get("candidate_name", ""),
        "pipeline_family": artifact.get("pipeline_family", ""),
        "distribution": artifact.get("distribution", ""),
        "artifact_role": artifact.get("artifact_role", ""),
        "replay_status": artifact.get("replay_status", ""),
        "allowed_inspection": artifact.get("allowed_inspection", ""),
        "hypothesis_ids": artifact.get("hypothesis_ids", []),
        "loaded_json_path": str(json_path.relative_to(root)) if json_path else None,
        "total_rows": total_rows,
        "baseline_correct_rows": baseline_correct,
        "baseline_purist_proxy": baseline_proxy,
        "final_correct_rows": final_correct,
        "final_purist_proxy": final_proxy,
        "selected_rows": _first_number(
            payload,
            metrics,
            [
                "selected_rows",
                "selected_candidate_rows",
                "contract_selected_rows",
                "targeted_selected_rows",
            ],
        ),
        "changed_rows": _first_number(
            transition_counts,
            metrics,
            [
                "changed",
                "changed_rows",
                "combined_changed_rows",
            ],
        ),
        "wrong_to_correct": _first_number(
            transition_counts,
            metrics,
            [
                "wrong_to_correct",
                "w_to_c",
            ],
        ),
        "correct_to_wrong": _first_number(
            transition_counts,
            metrics,
            [
                "correct_to_wrong",
                "c_to_w",
            ],
        ),
        "changed_label_precision": _first_number(
            payload,
            metrics,
            [
                "changed_label_precision",
                "contract_changed_label_precision",
                "targeted_changed_label_precision",
            ],
        ),
        "decision": payload.get("decision") if isinstance(payload, dict) else None,
        "score_layers_available": artifact.get("score_layers_available", []),
    }


def _candidate_gap_summary(summaries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_candidate: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for summary in summaries:
        by_candidate[str(summary.get("candidate_name", ""))].append(summary)

    gaps = []
    for candidate, candidate_summaries in sorted(by_candidate.items()):
        validation = _best_surface(candidate_summaries, distribution_prefix="validation")
        test = _best_surface(candidate_summaries, distribution_prefix="locked_test")
        if not validation or not test:
            continue
        validation_proxy = validation.get("final_purist_proxy")
        test_proxy = test.get("final_purist_proxy")
        if not isinstance(validation_proxy, int | float) or not isinstance(
            test_proxy, int | float
        ):
            continue
        gaps.append(
            {
                "candidate_name": candidate,
                "validation_artifact_id": validation.get("artifact_id"),
                "test_artifact_id": test.get("artifact_id"),
                "validation_final_purist_proxy": validation_proxy,
                "test_final_purist_proxy": test_proxy,
                "validation_minus_test_gap": validation_proxy - test_proxy,
                "validation_rows": validation.get("total_rows"),
                "test_rows": test.get("total_rows"),
            }
        )
    return gaps


def _distribution_summary(
    summaries: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for summary in summaries:
        distribution = str(summary.get("distribution", "unknown"))
        bucket = result.setdefault(
            distribution,
            {
                "surface_count": 0,
                "artifacts_with_final_proxy": 0,
                "mean_final_purist_proxy": None,
            },
        )
        bucket["surface_count"] += 1
        if isinstance(summary.get("final_purist_proxy"), int | float):
            bucket["artifacts_with_final_proxy"] += 1

    for distribution, bucket in result.items():
        values = [
            summary["final_purist_proxy"]
            for summary in summaries
            if summary.get("distribution") == distribution
            and isinstance(summary.get("final_purist_proxy"), int | float)
        ]
        if values:
            bucket["mean_final_purist_proxy"] = sum(values) / len(values)
    return result


def _best_surface(
    summaries: Sequence[Mapping[str, Any]],
    *,
    distribution_prefix: str,
) -> Mapping[str, Any] | None:
    eligible = [
        summary
        for summary in summaries
        if str(summary.get("distribution", "")).startswith(distribution_prefix)
        and isinstance(summary.get("final_purist_proxy"), int | float)
    ]
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda summary: (
            int(summary.get("total_rows") or 0),
            str(summary.get("artifact_id", "")),
        ),
        reverse=True,
    )[0]


def _first_existing_json_path(paths: Sequence[str], *, root: Path) -> Path | None:
    for raw_path in paths:
        path = root / raw_path
        if path.suffix == ".json" and path.exists():
            return path
    return None


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    data = json.loads(path.read_text())
    return data if isinstance(data, dict) else {}


def _first_number(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    keys: Sequence[str],
) -> int | float | None:
    for key in keys:
        for mapping in (first, second):
            value = mapping.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int | float):
                return value
    return None


def _transition_counts(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in [
        "transition_counts",
        "selected_transition_counts",
        "contract_transition_counts",
        "targeted_transition_counts",
        "combined_transition_counts",
    ]:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, int):
        return str(value)
    return ""


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json"),
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path("experiments/gan2026_validation_test_surface_map_v0_2026-06-05.md"),
    )
    args = parser.parse_args(argv)

    root = Path.cwd()
    inventory = json.loads(args.inventory.read_text())
    surface_map = build_surface_map(inventory, root=root)
    write_surface_map_json(surface_map, args.json_output)
    write_surface_map_report(surface_map, args.report_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
