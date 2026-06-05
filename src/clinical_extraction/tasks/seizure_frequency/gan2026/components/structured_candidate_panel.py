"""Materialize structured candidate/event validation panels."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_candidate_contract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_candidate_event_contract_v0"
SOURCE_ARTIFACT_KIND = "direct_labeler_full_validation750"
DEFAULT_SOURCE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_"
    "2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_validation750_panel_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_validation750_panel_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_validation750_panel_2026-06-05.md"
)


def build_direct_labeler_panel_rows(
    saved_rows: Sequence[Mapping[str, Any]],
    note_text_by_source: Mapping[int, str],
) -> list[dict[str, Any]]:
    """Adapt saved direct-labeler validation rows to the structured contract."""

    rows = []
    for saved in saved_rows:
        source_row_index = int(saved["source_row_index"])
        decision = saved.get("decision_record") or {}
        candidate_input = {
            "source_row_index": source_row_index,
            "split": saved.get("split") or "validation",
            "current_label": saved.get("current_label"),
            "proposed_label": saved.get("direct_label"),
            "gold_label": saved.get("gold_label"),
            "candidate_id": f"direct_labeler:{source_row_index}",
            "candidate_source": "llm_candidate",
            "event_kind": _event_kind(decision.get("answer_kind"), saved.get("direct_label")),
            "event_target": decision.get("selected_seizure_type") or "seizure",
            "temporality": _temporality(decision.get("time_window")),
            "assertion_status": "asserted",
            "evidence": decision.get("evidence") or "",
            "note_text": note_text_by_source.get(source_row_index, ""),
            "parse_ok": not saved.get("parse_errors"),
            "selected_for_ablation": True,
            "panel_role": (
                "control" if _as_bool(saved.get("current_purist_correct")) else "hard"
            ),
        }
        event = structured_candidate_contract.build_candidate_event(candidate_input)
        row = asdict(event)
        row.update(
            {
                "artifact_kind": "gan2026_structured_candidate_event_contract_row",
                "policy_name": POLICY_NAME,
                "source_artifact_kind": SOURCE_ARTIFACT_KIND,
                "source_policy_name": saved.get("policy_name"),
                "split_manifest": saved.get("split_manifest") or "gan2026_split_v1",
                "source_transition": saved.get("transition"),
                "source_parse_errors": saved.get("parse_errors") or [],
                "source_evidence_valid": bool(saved.get("evidence_valid")),
                "note_text": None,
            }
        )
        row["contract_issues"] = list(event.contract_issues)
        rows.append(row)
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows


def summarize_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize structured candidate panel rows and pre-holdout gates."""

    events = [
        structured_candidate_contract.StructuredCandidateEvent(
            source_row_index=int(row["source_row_index"]),
            split=str(row["split"]),
            candidate_id=str(row["candidate_id"]),
            candidate_source=row["candidate_source"],
            event_kind=row["event_kind"],
            event_target=str(row["event_target"]),
            temporality=row["temporality"],
            assertion_status=row["assertion_status"],
            evidence=str(row["evidence"]),
            current_label=str(row["current_label"]),
            proposed_label=str(row["proposed_label"]),
            gold_label=str(row["gold_label"]),
            parse_ok=bool(row["parse_ok"]),
            exact_evidence=bool(row["exact_evidence"]),
            selected_for_ablation=bool(row["selected_for_ablation"]),
            panel_role=row["panel_role"],
            prediction_bearing=bool(row["prediction_bearing"]),
            transition=row["transition"],
            contract_issues=tuple(row.get("contract_issues") or []),
        )
        for row in rows
    ]
    gate = structured_candidate_contract.summarize_validation_gate(events)
    transitions = Counter(str(row["transition"]) for row in rows)
    source_transitions = Counter(str(row.get("source_transition")) for row in rows)
    panel_roles = Counter(str(row["panel_role"]) for row in rows)
    return {
        "artifact_kind": "gan2026_structured_candidate_event_contract_summary",
        "policy_name": POLICY_NAME,
        "source_artifact_kind": SOURCE_ARTIFACT_KIND,
        "row_count": len(rows),
        "panel_role_counts": dict(sorted(panel_roles.items())),
        "transition_counts": dict(sorted(transitions.items())),
        "source_transition_counts": dict(sorted(source_transitions.items())),
        "parse_ok_rows": sum(bool(row["parse_ok"]) for row in rows),
        "exact_evidence_rows": sum(bool(row["exact_evidence"]) for row in rows),
        "contract_issue_rows": sum(bool(row.get("contract_issues")) for row in rows),
        "validation_gate": gate,
        "claim_boundary": (
            "Validation-development structured candidate/event panel adapted from "
            "saved direct-labeler full-validation rows. This is a no-call analysis "
            "and does not inspect locked-test rows or authorize a frozen test audit."
        ),
        "decision": (
            "eligible_for_frozen_test_protocol_addendum"
            if gate["frozen_test_audit_ready"]
            else "blocked_before_holdout"
        ),
    }


def materialize_direct_labeler_panel(
    *,
    source_jsonl_path: Path = DEFAULT_SOURCE_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    """Materialize the saved direct-labeler surface under the structured contract."""

    saved_rows = load_jsonl_rows(source_jsonl_path)
    note_text_by_source = {
        record.source_row_index: record.note_text for record in load_records_for_split("validation")
    }
    rows = build_direct_labeler_panel_rows(saved_rows, note_text_by_source)
    summary = summarize_panel_rows(rows)
    summary = {
        **summary,
        "source_artifact": str(source_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(
        summary,
        output_report_path,
        jsonl_path=output_jsonl_path,
        json_path=output_json_path,
    )
    return summary


def write_report(
    summary: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    """Write a compact Markdown report for the structured candidate panel."""

    gate = summary["validation_gate"]
    lines = [
        "# Gan 2026 Structured Candidate Event Contract Panel",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Gate",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| selected prediction-bearing rows | {gate['selected_prediction_bearing_rows']} |",
        f"| W->C rows | {gate['w_to_c_rows']} |",
        f"| C->W rows | {gate['c_to_w_rows']} |",
        f"| C->W rate | {_format_rate(gate['c_to_w_rate'])} |",
        (
            "| parse-ok plus exact-evidence rate | "
            f"{_format_rate(gate['parse_ok_exact_evidence_rate'])} |"
        ),
        f"| frozen test audit ready | {gate['frozen_test_audit_ready']} |",
        "",
        "Gate failures: "
        + (", ".join(f"`{failure}`" for failure in gate["gate_failures"]) or "none"),
        "",
        "## Panel",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| parse-ok rows | {summary['parse_ok_rows']} |",
        f"| exact-evidence rows | {summary['exact_evidence_rows']} |",
        f"| contract-issue rows | {summary['contract_issue_rows']} |",
        "",
        "## Gate Transitions",
        "",
        "| Transition | Prediction-Bearing Rows |",
        "| --- | ---: |",
    ]
    for transition, count in gate["transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Source Transitions",
            "",
            "These counts cover all 750 adapted source rows, including rows that were "
            "not prediction-bearing under the structured contract.",
            "",
            "| Transition | Rows |",
            "| --- | ---: |",
        ]
    )
    for transition, count in summary["transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
        "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source JSONL: `{summary['source_artifact']}`",
            "",
            "## Inspection Boundary",
            "",
            "No locked-test rows are read. Panel rows omit clinical note text.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _event_kind(answer_kind: Any, label: Any) -> str:
    text = str(answer_kind or "").lower()
    label_text = str(label or "").lower()
    if "cluster" in text or "cluster" in label_text:
        return "cluster_frequency"
    if "seizure free" in text or label_text.startswith("seizure free"):
        return "seizure_free"
    if "no_reference" in text or "no seizure frequency reference" in label_text:
        return "no_reference"
    if "unknown" in text or label_text == "unknown":
        return "unknown_frequency"
    if "last" in text and "event" in text:
        return "last_event_only"
    return "frequency_rate"


def _temporality(time_window: Any) -> str:
    text = str(time_window or "").lower()
    if any(token in text for token in ("historical", "past history", "remote")):
        return "historical"
    if any(token in text for token in ("current", "recent", "past", "month", "week")):
        return "current"
    return "unclear"


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _format_rate(value: Any) -> str:
    return f"{float(value):.4f}"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-jsonl-path", type=Path, default=DEFAULT_SOURCE_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_direct_labeler_panel(
        source_jsonl_path=args.source_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(json.dumps(summary["validation_gate"], sort_keys=True))


if __name__ == "__main__":
    main()
