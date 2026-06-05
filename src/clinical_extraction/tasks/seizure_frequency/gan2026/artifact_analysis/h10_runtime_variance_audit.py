"""H10 runtime-variance audit over paired live and saved-output replay artifacts."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_LIVE_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_"
    "v0_conservative_live_2026-06-03.jsonl"
)
DEFAULT_REPLAY_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_"
    "v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_SURFACE_MAP_PATH = Path(
    "experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_h10_runtime_variance_audit_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_h10_runtime_variance_audit_v0_2026-06-05.md"
)

RAW_OUTPUT_FIELDS = (
    "raw_output",
    "llm_candidate_raw_output",
    "adjudicator_raw_output",
)


def _rows_by_source_index(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows}


def _identity_summary(
    live_rows: Mapping[int, Mapping[str, Any]],
    replay_rows: Mapping[int, Mapping[str, Any]],
    matched_indices: Sequence[int],
) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    denominator = len(matched_indices)
    for field in RAW_OUTPUT_FIELDS:
        identical = sum(
            live_rows[index].get(field) == replay_rows[index].get(field)
            for index in matched_indices
        )
        present = sum(
            field in live_rows[index] and field in replay_rows[index]
            for index in matched_indices
        )
        summary[field] = {
            "present_rows": present,
            "identical_rows": identical,
            "identity_rate": identical / denominator if denominator else 0.0,
        }
    return summary


def _score_layer_drift(
    live_rows: Mapping[int, Mapping[str, Any]],
    replay_rows: Mapping[int, Mapping[str, Any]],
    matched_indices: Sequence[int],
) -> dict[str, dict[str, float | int]]:
    layer_names = sorted(
        {
            layer
            for row in list(live_rows.values()) + list(replay_rows.values())
            for layer in row.get("score_layers", {})
        }
    )
    drift: dict[str, dict[str, float | int]] = {}
    for layer in layer_names:
        rows = 0
        label_changed = 0
        purist_changed = 0
        scorable_changed = 0
        live_scorable = 0
        replay_scorable = 0
        live_correct = 0
        replay_correct = 0
        for index in matched_indices:
            live_layer = live_rows[index].get("score_layers", {}).get(layer, {})
            replay_layer = replay_rows[index].get("score_layers", {}).get(layer, {})
            if not live_layer and not replay_layer:
                continue
            rows += 1
            label_changed += live_layer.get("final_label") != replay_layer.get(
                "final_label"
            )
            purist_changed += live_layer.get("purist_correct") != replay_layer.get(
                "purist_correct"
            )
            scorable_changed += live_layer.get("scorable") != replay_layer.get(
                "scorable"
            )
            if live_layer.get("scorable") is True:
                live_scorable += 1
                live_correct += live_layer.get("purist_correct") is True
            if replay_layer.get("scorable") is True:
                replay_scorable += 1
                replay_correct += replay_layer.get("purist_correct") is True

        drift[layer] = {
            "rows": rows,
            "final_label_changed_rows": label_changed,
            "purist_correct_changed_rows": purist_changed,
            "scorable_changed_rows": scorable_changed,
            "live_scorable_rows": live_scorable,
            "live_purist_correct_rows": live_correct,
            "live_purist_accuracy": live_correct / live_scorable
            if live_scorable
            else 0.0,
            "replay_scorable_rows": replay_scorable,
            "replay_purist_correct_rows": replay_correct,
            "replay_purist_accuracy": replay_correct / replay_scorable
            if replay_scorable
            else 0.0,
        }
    return drift


def _surface_gap_context(surface_map_path: Path) -> dict[str, Any]:
    data = json.loads(surface_map_path.read_text(encoding="utf-8"))
    gaps = data.get("candidate_gap_summary", [])
    numeric_gaps = [
        gap["validation_minus_test_gap"]
        for gap in gaps
        if isinstance(gap.get("validation_minus_test_gap"), int | float)
    ]
    return {
        "surface_map_path": str(surface_map_path),
        "paired_candidates_with_gap": len(numeric_gaps),
        "max_validation_minus_test_gap": max(numeric_gaps) if numeric_gaps else None,
        "mean_validation_minus_test_gap": sum(numeric_gaps) / len(numeric_gaps)
        if numeric_gaps
        else None,
        "candidate_gaps": gaps,
    }


def build_h10_runtime_variance_audit(
    *,
    live_path: Path = DEFAULT_LIVE_PATH,
    replay_path: Path = DEFAULT_REPLAY_PATH,
    surface_map_path: Path = DEFAULT_SURFACE_MAP_PATH,
) -> dict[str, Any]:
    live_rows = _rows_by_source_index(load_jsonl_rows(live_path))
    replay_rows = _rows_by_source_index(load_jsonl_rows(replay_path))
    matched_indices = sorted(set(live_rows) & set(replay_rows))
    raw_identity = _identity_summary(live_rows, replay_rows, matched_indices)
    score_drift = _score_layer_drift(live_rows, replay_rows, matched_indices)
    gap_context = _surface_gap_context(surface_map_path)
    all_raw_identical = all(
        item["identity_rate"] == 1.0 for item in raw_identity.values()
    )
    gap_persists = bool(gap_context["max_validation_minus_test_gap"])

    if all_raw_identical and gap_persists:
        decision = "h10_rejected_as_primary_gap_explanation"
        interpretation = (
            "The paired validation live/replay surface has byte-identical saved "
            "raw outputs for every matched row, while saved validation/test "
            "surface-map gaps remain large. Runtime variance may affect downstream "
            "attribution when adapters or repair code change, but it is not the "
            "primary explanation for the observed generalisation gap."
        )
    else:
        decision = "h10_inconclusive_needs_more_replay_controls"
        interpretation = (
            "The available paired artifacts do not yet separate raw-output "
            "variance from downstream replay effects well enough to decide H10."
        )

    return {
        "artifact_kind": "gan2026_h10_runtime_variance_audit_v0",
        "hypothesis_id": "H10",
        "date": "2026-06-05",
        "split_manifest": "gan2026_split_v1",
        "live_path": str(live_path),
        "replay_path": str(replay_path),
        "matched_source_rows": len(matched_indices),
        "live_only_rows": len(set(live_rows) - set(replay_rows)),
        "replay_only_rows": len(set(replay_rows) - set(live_rows)),
        "raw_output_identity": raw_identity,
        "score_layer_drift": score_drift,
        "surface_gap_context": gap_context,
        "decision": decision,
        "interpretation": interpretation,
        "claim_boundary": (
            "No live model calls were made. No locked-test row-level failures were "
            "inspected; locked-test evidence is limited to the saved aggregate "
            "surface map."
        ),
    }


def write_h10_json(audit: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_h10_report(audit: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# H10 Runtime Variance Audit",
        "",
        f"Decision: `{audit['decision']}`.",
        "",
        str(audit["claim_boundary"]),
        "",
        "## Raw Output Identity",
        "",
        f"Matched source rows: {audit['matched_source_rows']}.",
        "",
        "| Field | Identical rows | Identity rate |",
        "| --- | ---: | ---: |",
    ]
    for field, summary in audit["raw_output_identity"].items():
        lines.append(
            f"| `{field}` | {summary['identical_rows']} | "
            f"{summary['identity_rate']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Score-Layer Drift",
            "",
            "| Score layer | Final-label changed | Purist changed | "
            "Live accuracy | Replay accuracy |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for layer, summary in audit["score_layer_drift"].items():
        lines.append(
            f"| `{layer}` | {summary['final_label_changed_rows']} | "
            f"{summary['purist_correct_changed_rows']} | "
            f"{summary['live_purist_accuracy']:.4f} | "
            f"{summary['replay_purist_accuracy']:.4f} |"
        )

    gap_context = audit["surface_gap_context"]
    mean_gap = gap_context.get("mean_validation_minus_test_gap")
    lines.extend(
        [
            "",
            "## Surface Gap Context",
            "",
            f"Paired candidates with saved validation/test gap: "
            f"{gap_context['paired_candidates_with_gap']}.",
            f"Maximum saved validation-minus-test gap: "
            f"{gap_context['max_validation_minus_test_gap']:.4f}.",
            f"Mean saved validation-minus-test gap: "
            f"{mean_gap:.4f}." if mean_gap is not None else "not available.",
            "",
            "## Interpretation",
            "",
            str(audit["interpretation"]),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-path", type=Path, default=DEFAULT_LIVE_PATH)
    parser.add_argument("--replay-path", type=Path, default=DEFAULT_REPLAY_PATH)
    parser.add_argument("--surface-map-path", type=Path, default=DEFAULT_SURFACE_MAP_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    audit = build_h10_runtime_variance_audit(
        live_path=args.live_path,
        replay_path=args.replay_path,
        surface_map_path=args.surface_map_path,
    )
    write_h10_json(audit, args.json_path)
    write_h10_report(audit, args.report_path)


if __name__ == "__main__":
    main()
