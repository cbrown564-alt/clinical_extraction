"""Family-slice audit for structured candidate/event panels."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_validation750_panel_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_family_audit_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_family_audit_2026-06-05.md"
)
POLICY_NAME = "gan2026_structured_candidate_family_audit_v0"

SliceFn = Callable[[Mapping[str, Any]], str]


def summarize_family_audit(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize precision and coverage for structured candidate family slices."""

    selected = [row for row in rows if row.get("prediction_bearing")]
    slice_summaries = []
    for slice_name, slice_fn in _slice_fns().items():
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        for row in selected:
            grouped[slice_fn(row)][str(row["transition"])] += 1
        for slice_value, transitions in grouped.items():
            summary = _summarize_slice(slice_name, slice_value, transitions)
            slice_summaries.append(summary)
    slice_summaries.sort(
        key=lambda row: (
            -int(row["w_to_c_rows"]),
            int(row["c_to_w_rows"]),
            str(row["slice_name"]),
            str(row["slice_value"]),
        )
    )
    clean_seed_slices = [
        row
        for row in slice_summaries
        if row["w_to_c_rows"] > 0
        and row["c_to_w_rows"] == 0
        and row["changed_label_precision"] == 1.0
    ]
    clean_seed_slices.sort(
        key=lambda row: (
            -int(row["w_to_c_rows"]),
            _slice_priority(str(row["slice_name"])),
            str(row["slice_value"]),
        )
    )
    transition_counts = Counter(str(row["transition"]) for row in selected)
    return {
        "artifact_kind": "gan2026_structured_candidate_family_audit_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "prediction_bearing_rows": len(selected),
        "transition_counts": dict(sorted(transition_counts.items())),
        "slice_summaries": slice_summaries,
        "clean_seed_slices": clean_seed_slices,
        "decision": _decision(clean_seed_slices),
        "claim_boundary": (
            "Validation-development family audit over the structured candidate "
            "panel. Gold labels are used only for validation W->C/C->W accounting. "
            "No locked-test rows are read and no holdout-facing use is authorized."
        ),
        "recommended_next_step": _recommended_next_step(clean_seed_slices),
    }


def materialize_family_audit(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    rows = load_jsonl_rows(panel_jsonl_path)
    summary = summarize_family_audit(rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path, json_path=output_json_path)
    return summary


def write_report(
    summary: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    clean = summary["clean_seed_slices"][:12]
    lines = [
        "# Gan 2026 Structured Candidate Family Audit",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Clean Seed Slices",
        "",
        "| Slice | Value | Rows | W->C | C->W | Precision |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in clean:
        lines.append(
            f"| `{row['slice_name']}` | `{row['slice_value']}` | "
            f"{row['selected_rows']} | {row['w_to_c_rows']} | "
            f"{row['c_to_w_rows']} | {_format_rate(row['changed_label_precision'])} |"
        )
    if not clean:
        lines.append("| none | none | 0 | 0 | 0 | 0.0000 |")
    lines.extend(
        [
            "",
            "## Top Slices By W->C",
            "",
            "| Slice | Value | Rows | W->C | C->W | Net | Precision |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary["slice_summaries"][:20]:
        lines.append(
            f"| `{row['slice_name']}` | `{row['slice_value']}` | "
            f"{row['selected_rows']} | {row['w_to_c_rows']} | "
            f"{row['c_to_w_rows']} | {row['net_w_to_c']} | "
            f"{_format_rate(row['changed_label_precision'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Summary JSON: `{json_path}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _summarize_slice(
    slice_name: str,
    slice_value: str,
    transitions: Counter[str],
) -> dict[str, Any]:
    w_to_c = transitions["W_to_C"]
    c_to_w = transitions["C_to_W"]
    changed = w_to_c + c_to_w
    selected_rows = sum(transitions.values())
    return {
        "slice_name": slice_name,
        "slice_value": slice_value,
        "selected_rows": selected_rows,
        "transition_counts": dict(sorted(transitions.items())),
        "w_to_c_rows": w_to_c,
        "c_to_w_rows": c_to_w,
        "net_w_to_c": w_to_c - c_to_w,
        "c_to_w_rate": _rate(c_to_w, selected_rows),
        "changed_label_precision": _rate(w_to_c, changed),
    }


def _slice_fns() -> dict[str, SliceFn]:
    return {
        "event_kind": lambda row: str(row.get("event_kind") or "unknown"),
        "current_family": lambda row: _label_family(row.get("current_label")),
        "proposed_family": lambda row: _label_family(row.get("proposed_label")),
        "current_to_proposed_family": (
            lambda row: (
                f"{_label_family(row.get('current_label'))}->"
                f"{_label_family(row.get('proposed_label'))}"
            )
        ),
    }


def _label_family(label: Any) -> str:
    text = str(label or "").lower()
    if text == "unknown":
        return "unknown"
    if text == "no seizure frequency reference":
        return "no_reference"
    if text.startswith("seizure free"):
        return "seizure_free"
    if "cluster" in text:
        return "cluster"
    if "per day" in text:
        return "daily"
    if "per week" in text:
        return "weekly"
    if "per month" in text:
        return "monthly"
    if "per year" in text:
        return "yearly"
    return "other"


def _decision(clean_seed_slices: Sequence[Mapping[str, Any]]) -> str:
    if not clean_seed_slices:
        return "no_clean_structured_seed_slice"
    if max(int(row["w_to_c_rows"]) for row in clean_seed_slices) >= 60:
        return "candidate_family_meets_w_to_c_gate"
    return "seed_slices_only_undercoverage"


def _slice_priority(slice_name: str) -> int:
    priorities = {
        "current_to_proposed_family": 0,
        "current_family": 1,
        "proposed_family": 2,
        "event_kind": 3,
    }
    return priorities.get(slice_name, 99)


def _recommended_next_step(clean_seed_slices: Sequence[Mapping[str, Any]]) -> str:
    if not clean_seed_slices:
        return (
            "Do not promote any broad direct-labeler family. Build a new structured "
            "event generator with stricter parse and evidence ownership."
        )
    top = clean_seed_slices[0]
    return (
        "Use the clean seed slices only as mechanism probes, not holdout-ready "
        "policy. The largest clean slice is "
        f"`{top['slice_name']}={top['slice_value']}` with {top['w_to_c_rows']} "
        "W->C and 0 C->W, far below the 60 W->C gate; expand through structured "
        "event generation and matched controls before any frozen test audit."
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: Any) -> str:
    return f"{float(value):.4f}"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_family_audit(
        panel_jsonl_path=args.panel_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "clean_seed_slices": summary["clean_seed_slices"][:5],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
