"""Run change-only verifier calibration for LLM-selector exact alternatives."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    change_only_det_state_family_experiment as base_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    change_only_candidate_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

DATE = "2026-06-05"
MODEL = "openai/gpt-4.1"
PROMPT_VERSION = change_only_candidate_verifier.POLICY_NAME
DEFAULT_CANDIDATE_DISCOVERY_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl"
)
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_panel_2026-06-05.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_calibration_gpt41_2026-06-05.md"
)
DEFAULT_FULL_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.jsonl"
)
DEFAULT_FULL_JSON_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.json"
)
DEFAULT_FULL_REPORT_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_2026-06-05.md"
)
DEFAULT_TEST_INPUT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_"
    "deterministic_safety_floor_live_2026-06-03.jsonl"
)
DEFAULT_TEST_JSON_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_test450_aggregate_audit_2026-06-05.md"
)
DEFAULT_RAW_REUSE_PATHS = [
    Path("experiments/gan2026_change_only_verifier_calibration_gpt41_2026-06-05.jsonl"),
    Path(
        "experiments/gan2026_change_only_verifier_expanded_calibration_gpt41_2026-06-05.jsonl"
    ),
    Path(
        "experiments/gan2026_change_only_verifier_sf_unknown_family_gpt41_2026-06-05.jsonl"
    ),
    Path(
        "experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.jsonl"
    ),
]

CANDIDATE_KINDS = {
    "frequency_rate",
    "unknown_frequency",
    "cluster_frequency",
    "last_event_only",
}
CANDIDATE_KIND_PRIORITY = {
    "frequency_rate": 0,
    "unknown_frequency": 1,
    "cluster_frequency": 2,
    "last_event_only": 3,
}


def build_ranked_llm_family(
    candidate_rows: Sequence[Mapping[str, Any]],
    current_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Select one exact LLM-selector alternative per validation row."""

    current_by_source = {int(row["source_row_index"]): row for row in current_rows}
    candidates_by_source: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidate_rows:
        if not _candidate_eligible(candidate):
            continue
        source_row_index = int(candidate["source_row_index"])
        current = current_by_source.get(source_row_index)
        if current is None:
            continue
        current_label = _normalized_label(current["prediction_label"])
        candidate_label = _normalized_label(candidate.get("candidate_label"))
        if not current_label or not candidate_label or candidate_label == current_label:
            continue
        candidates_by_source[source_row_index].append(candidate)

    rows = []
    for source_row_index, candidates in sorted(candidates_by_source.items()):
        current = current_by_source[source_row_index]
        selected = sorted(candidates, key=_candidate_rank_key)[0]
        rows.append(_family_row(current, selected))
    return rows


def build_calibration_panel(family_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Use validation gold only to construct a balanced calibration panel."""

    positives = [row for row in family_rows if _transition_without_verifier(row) == "W_to_C"]
    controls_by_kind: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in family_rows:
        if _transition_without_verifier(row) == "C_to_W":
            controls_by_kind[str(row["candidate_kind"])].append(row)
    controls = []
    for kind in sorted(controls_by_kind):
        controls.extend(controls_by_kind[kind][: min(20, len(controls_by_kind[kind]))])
    return [
        dict(row, panel_role="recoverable_positive")
        for row in sorted(positives, key=lambda item: int(item["source_row_index"]))
    ] + [
        dict(row, panel_role="regression_control")
        for row in sorted(
            controls,
            key=lambda item: (str(item["candidate_kind"]), int(item["source_row_index"])),
        )
    ]


def run_calibration(
    panel_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    raw_reuse_paths: Sequence[Path],
    progress_every: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_reuse = base_experiment.load_reusable_raw_outputs(raw_reuse_paths)
    rows = []
    for index, row in enumerate(panel_rows, 1):
        result = base_experiment._run_row(
            row,
            model=model,
            max_tokens=max_tokens,
            raw_reuse=raw_reuse,
        )
        result["artifact_kind"] = "gan2026_change_only_verifier_llm_selector_exact_row"
        result["panel_role"] = row["panel_role"]
        result["claim_boundary"] = "validation_development_llm_selector_exact_calibration"
        rows.append(result)
        if progress_every and index % progress_every == 0:
            summary = change_only_candidate_verifier.summarize_rows(rows)
            print(
                f"processed={index}/{len(panel_rows)} "
                f"transitions={summary['transition_counts']}"
            )
    return rows, summarize_rows(rows, model=model, raw_reuse_paths=raw_reuse_paths)


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    raw_reuse_paths: Sequence[Path],
) -> dict[str, Any]:
    summary = change_only_candidate_verifier.summarize_rows(rows)
    transitions = Counter(str(row["transition"]) for row in rows)
    panel_roles = Counter(str(row["panel_role"]) for row in rows)
    whole_base_correct = next(
        (
            int(row["whole_validation_base_correct_rows"])
            for row in rows
            if row.get("whole_validation_base_correct_rows") is not None
        ),
        0,
    )
    whole_projected = whole_base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_change_only_verifier_llm_selector_exact_calibration_summary",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_name": change_only_candidate_verifier.POLICY_NAME,
        "source_artifact": str(DEFAULT_CANDIDATE_DISCOVERY_PATH),
        "raw_reuse_paths": [str(path) for path in raw_reuse_paths],
        "claim_boundary": (
            "Validation-development calibration panel for LLM-selector exact alternatives. "
            "Panel positives and controls use validation gold only for development "
            "accounting and do not authorize locked-test use."
        ),
        "proposal_policy": (
            "One exact llm_candidate_selector_raw alternative per validation row, ranked "
            "frequency_rate before unknown_frequency before cluster_frequency before "
            "last_event_only, then normalized label, candidate id, evidence."
        ),
        "metrics": {
            "row_count": len(rows),
            "recoverable_positive_rows": panel_roles["recoverable_positive"],
            "regression_control_rows": panel_roles["regression_control"],
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "model_call_rows": sum(not row["raw_output_reused"] for row in rows),
            "raw_output_reused_rows": sum(row["raw_output_reused"] for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
            "all_evidence_quotes_exact_rows": sum(
                bool(row["verifier_decision"]["all_evidence_quotes_exact"])
                for row in rows
            ),
            "base_correct_rows": summary["base_correct_rows"],
            "projected_correct_rows": summary["projected_correct_rows"],
            "base_purist_proxy": summary["base_purist_proxy"],
            "projected_purist_proxy": summary["projected_purist_proxy"],
            "changed_label_precision": summary["changed_label_precision"],
            "whole_validation_base_correct_rows": whole_base_correct,
            "whole_validation_projected_correct_rows": whole_projected,
            "whole_validation_base_purist_proxy": _rate(whole_base_correct, 750),
            "whole_validation_projected_purist_proxy": _rate(whole_projected, 750),
        },
        "transition_counts": summary["transition_counts"],
        "recommendation_counts": summary["recommendation_counts"],
        "candidate_kind_counts": dict(
            sorted(Counter(str(row["candidate_kind"]) for row in rows).items())
        ),
        "regression_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["transition"] == "C_to_W"
        ],
        "improved_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["transition"] == "W_to_C"
        ],
        "interpretation": _interpretation(transitions),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Change-Only Verifier LLM-Selector Exact Calibration",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Panel JSONL: `{DEFAULT_PANEL_JSONL_PATH}`",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Changed Validation Rows",
            "",
            "| Row | Role | Kind | Transition | Current | Proposed |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["transition"] in {"C_to_C", "W_to_W"}:
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['panel_role']}` | "
            f"`{row['candidate_kind']}` | `{row['transition']}` | "
            f"`{row['current_label']}` | `{row['proposed_label']}` |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_test_family(test_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build the frozen holdout family without using gold labels for proposal selection."""

    rows = []
    for row in test_rows:
        current_label = _normalized_label(
            row["score_layers"]["hybrid_adjudicator_raw"]["final_label"]
        )
        if not current_label:
            continue
        candidates = []
        for candidate in row["component_inputs"].get("llm_candidates") or []:
            if candidate.get("kind") not in CANDIDATE_KINDS:
                continue
            proposed = _normalized_label(candidate.get("normalized_label"))
            if proposed and proposed != current_label and candidate.get("evidence"):
                candidates.append(candidate)
        if not candidates:
            continue
        selected = sorted(candidates, key=_test_candidate_rank_key)[0]
        rows.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "split": "test",
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "clinical_text": str(row["component_inputs"]["note_text"]),
                "gold_label": str(row["reference"]["gold_normalized_label"]),
                "current_label": current_label,
                "proposed_label": _normalized_label(selected["normalized_label"]),
                "proposed_evidence": str(selected.get("evidence") or ""),
                "candidate_source": "llm_candidate_selector_raw",
                "candidate_kind": str(selected.get("kind") or ""),
                "candidate_id": str(selected.get("candidate_id") or ""),
            }
        )
    return rows


def run_test_aggregate_audit(
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int,
) -> dict[str, Any]:
    family = build_test_family(test_rows)
    output_rows = []
    for index, row in enumerate(family, 1):
        output_rows.append(
            base_experiment._run_row(row, model=model, max_tokens=max_tokens, raw_reuse={})
        )
        if progress_every and index % progress_every == 0:
            summary = change_only_candidate_verifier.summarize_rows(output_rows)
            print(
                f"processed={index}/{len(family)} "
                f"transitions={summary['transition_counts']}"
            )
    return summarize_test_aggregate(output_rows, test_rows, model=model)


def summarize_test_aggregate(
    rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
) -> dict[str, Any]:
    summary = change_only_candidate_verifier.summarize_rows(rows)
    transitions = Counter(str(row["transition"]) for row in rows)
    base_correct = sum(
        bool(row["score_layers"]["hybrid_adjudicator_raw"]["purist_correct"])
        for row in test_rows
    )
    projected_correct = base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_change_only_verifier_llm_selector_exact_test450_aggregate_audit",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_name": change_only_candidate_verifier.POLICY_NAME,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "claim_boundary": (
            "Frozen locked-test aggregate-only audit over exact LLM-selector alternatives. "
            "This summary intentionally omits row ids, clinical text, raw model outputs, "
            "and row-level errors."
        ),
        "proposal_policy": (
            "One exact llm_candidate_selector_raw alternative per eligible test row, ranked "
            "frequency_rate before unknown_frequency before cluster_frequency before "
            "last_event_only, then normalized label, candidate id, evidence."
        ),
        "metrics": {
            "test_rows": len(test_rows),
            "eligible_rows": len(rows),
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
            "all_evidence_quotes_exact_rows": sum(
                bool(row["verifier_decision"]["all_evidence_quotes_exact"])
                for row in rows
            ),
            "base_correct_rows": base_correct,
            "projected_correct_rows": projected_correct,
            "base_purist_proxy": _rate(base_correct, len(test_rows)),
            "projected_purist_proxy": _rate(projected_correct, len(test_rows)),
            "changed_label_precision": summary["changed_label_precision"],
        },
        "transition_counts": summary["transition_counts"],
        "recommendation_counts": summary["recommendation_counts"],
        "candidate_kind_counts": dict(
            sorted(Counter(str(row["candidate_kind"]) for row in rows).items())
        ),
        "decision": (
            "meets_requested_test_threshold"
            if _rate(projected_correct, len(test_rows)) >= 0.9
            else "does_not_meet_goal"
        ),
        "interpretation": (
            "Aggregate-only holdout result reaches the requested threshold."
            if _rate(projected_correct, len(test_rows)) >= 0.9
            else "Aggregate-only holdout result remains below the requested Purist F1 >= 0.9."
        ),
    }


def write_test_aggregate_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Change-Only Verifier LLM-Selector Test450 Aggregate Audit",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{json_path}`",
        f"- Source artifact: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "No test row ids, clinical text, raw model outputs, or row-level failures are "
            "stored in this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _family_row(
    current: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "source_row_index": int(current["source_row_index"]),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "clinical_text": str(current["clinical_text"]),
        "gold_label": str(current["gold_label"]),
        "current_label": _normalized_label(current["prediction_label"]),
        "proposed_label": _normalized_label(candidate["candidate_label"]),
        "proposed_evidence": str(candidate.get("candidate_evidence") or ""),
        "candidate_source": "llm_candidate_selector_raw",
        "candidate_kind": str(candidate.get("candidate_kind") or ""),
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "candidate_evidence_status": str(candidate.get("evidence_status") or ""),
        "whole_validation_base_correct_rows": current.get("whole_validation_base_correct_rows"),
    }


def _candidate_eligible(candidate: Mapping[str, Any]) -> bool:
    return (
        candidate.get("split") == "validation"
        and candidate.get("generator_name") == "llm_candidate_selector_raw"
        and candidate.get("evidence_status") == "exact"
        and candidate.get("candidate_kind") in CANDIDATE_KINDS
        and _normalized_label(candidate.get("candidate_label")) is not None
    )


def _candidate_rank_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        CANDIDATE_KIND_PRIORITY.get(str(candidate.get("candidate_kind") or ""), 99),
        str(_normalized_label(candidate.get("candidate_label")) or ""),
        str(candidate.get("candidate_id") or ""),
        str(candidate.get("candidate_evidence") or ""),
    )


def _test_candidate_rank_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        CANDIDATE_KIND_PRIORITY.get(str(candidate.get("kind") or ""), 99),
        str(_normalized_label(candidate.get("normalized_label")) or ""),
        str(candidate.get("candidate_id") or ""),
        str(candidate.get("evidence") or ""),
    )


def _transition_without_verifier(row: Mapping[str, Any]) -> str:
    current_correct = _purist_correct(row["current_label"], row["gold_label"])
    proposed_correct = _purist_correct(row["proposed_label"], row["gold_label"])
    return change_only_candidate_verifier.transition(current_correct, proposed_correct)


def _normalized_label(label: Any) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return None


def _purist_correct(label: Any, gold_label: Any) -> bool:
    try:
        predicted = label_to_frequency_record(str(label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    return map_purist(predicted.monthly_frequency) == map_purist(gold.monthly_frequency)


def _interpretation(transitions: Counter[str]) -> str:
    if transitions["W_to_C"] > 0 and transitions["C_to_W"] == 0:
        return "Promote to full validation-family audit; calibration is clean and useful."
    if transitions["W_to_C"] > transitions["C_to_W"]:
        return "Diagnostic positive but not promotable; inspect validation C->W regressions."
    return "Reject or revise; calibration does not show high-precision switching."


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["calibration", "full-family", "test-aggregate"],
        default="calibration",
    )
    parser.add_argument(
        "--candidate-discovery-path",
        type=Path,
        default=DEFAULT_CANDIDATE_DISCOVERY_PATH,
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--test-json-path", type=Path, default=DEFAULT_TEST_JSON_PATH)
    parser.add_argument("--test-report-path", type=Path, default=DEFAULT_TEST_REPORT_PATH)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument(
        "--raw-reuse-path",
        type=Path,
        action="append",
        default=list(DEFAULT_RAW_REUSE_PATHS),
    )
    args = parser.parse_args(argv)

    if args.mode == "test-aggregate":
        metadata = run_test_aggregate_audit(
            load_jsonl_rows(args.test_input_path),
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
        write_summary_json(metadata, args.test_json_path)
        write_test_aggregate_report(
            metadata,
            args.test_report_path,
            json_path=args.test_json_path,
        )
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["interpretation"])
        return

    current_rows = base_experiment.load_current_validation_rows()
    family = build_ranked_llm_family(
        load_jsonl_rows(args.candidate_discovery_path),
        current_rows,
    )
    if args.mode == "full-family":
        panel = [dict(row, panel_role="full_family") for row in family]
        if args.jsonl_path == DEFAULT_JSONL_PATH:
            args.jsonl_path = DEFAULT_FULL_JSONL_PATH
        if args.json_path == DEFAULT_JSON_PATH:
            args.json_path = DEFAULT_FULL_JSON_PATH
        if args.report_path == DEFAULT_REPORT_PATH:
            args.report_path = DEFAULT_FULL_REPORT_PATH
    else:
        panel = build_calibration_panel(family)
        write_jsonl_rows(panel, args.panel_jsonl_path)
    rows, metadata = run_calibration(
        panel,
        model=args.model,
        max_tokens=args.max_tokens,
        raw_reuse_paths=args.raw_reuse_path,
        progress_every=args.progress_every,
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["interpretation"])


if __name__ == "__main__":
    main()
