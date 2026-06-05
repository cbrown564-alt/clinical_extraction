"""Validation hard/control panel for structured seed event extraction."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_seed_validation_panel_v0"
DEFAULT_CURRENT_JSONL_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.md"
)

SEED_HARD_PAIRS = {
    ("seizure_free", "unknown"): "seizure_free_to_unknown",
    ("yearly", "daily"): "yearly_to_daily",
    ("monthly", "cluster"): "cluster_completion",
    ("other", "cluster"): "cluster_completion",
}
CONTROL_FAMILIES = {
    "seizure_free": "seizure_free_to_unknown",
    "yearly": "yearly_to_daily",
    "monthly": "cluster_completion",
    "cluster": "cluster_completion",
}


def build_validation_panel_rows(
    current_rows: Sequence[Mapping[str, Any]],
    records_by_source: Mapping[int, Any],
) -> list[dict[str, Any]]:
    """Build validation hard/control rows for structured seed families."""

    rows = []
    hard_counts: Counter[str] = Counter()
    for row in current_rows:
        current_family = _label_family(row.get("final_label"))
        gold_family = _label_family(row.get("gold_label"))
        family = SEED_HARD_PAIRS.get((current_family, gold_family))
        if family is None or _as_bool(row.get("final_purist_correct")):
            continue
        rows.append(_panel_row(row, records_by_source, seed_family=family, hard=True))
        hard_counts[family] += 1
    control_limits = hard_counts or Counter({"seizure_free_to_unknown": 0})
    control_counts: Counter[str] = Counter()
    for row in current_rows:
        if not _as_bool(row.get("final_purist_correct")):
            continue
        current_family = _label_family(row.get("final_label"))
        gold_family = _label_family(row.get("gold_label"))
        if current_family != gold_family:
            continue
        family = CONTROL_FAMILIES.get(current_family)
        if family is None or control_counts[family] >= max(control_limits[family], 1):
            continue
        rows.append(_panel_row(row, records_by_source, seed_family=family, hard=False))
        control_counts[family] += 1
    rows.sort(key=lambda item: (item["seed_family"], item["panel_role"], item["source_row_index"]))
    return rows


def summarize_validation_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the selected validation hard/control design panel."""

    family_counts = Counter(str(row["seed_family"]) for row in rows)
    hard_family_counts = Counter(
        str(row["seed_family"]) for row in rows if row["panel_role"] == "hard"
    )
    control_family_counts = Counter(
        str(row["seed_family"]) for row in rows if row["panel_role"] == "control"
    )
    exact_reference_rows = sum(bool(row["expected_evidence_substring"]) for row in rows)
    return {
        "artifact_kind": "gan2026_structured_seed_validation_panel_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "family_counts": dict(sorted(family_counts.items())),
        "hard_family_counts": dict(sorted(hard_family_counts.items())),
        "control_family_counts": dict(sorted(control_family_counts.items())),
        "exact_reference_rows": exact_reference_rows,
        "claim_boundary": (
            "Validation-development hard/control design panel for structured seed "
            "event extraction. It reads validation rows only, omits note text from "
            "artifacts, and does not authorize holdout use."
        ),
        "decision": (
            "ready_for_validation_extractor_smoke"
            if rows and exact_reference_rows == len(rows)
            else "validation_panel_contract_failed"
        ),
        "recommended_next_step": (
            "Run a validation extractor smoke that loads note text in memory, emits "
            "typed candidates for hard rows, suppresses matched controls, and writes "
            "only bounded row metadata plus exact evidence strings."
        ),
    }


def materialize_validation_panel(
    *,
    current_jsonl_path: Path = DEFAULT_CURRENT_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    current_rows = load_jsonl_rows(current_jsonl_path)
    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows = build_validation_panel_rows(current_rows, records_by_source)
    summary = summarize_validation_panel_rows(rows)
    summary = {
        **summary,
        "source_current_artifact": str(current_jsonl_path),
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
    lines = [
        "# Gan 2026 Structured Seed Validation Panel",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| exact reference rows | {summary['exact_reference_rows']} |",
        "",
        "## Families",
        "",
        "| Family | Total | Hard | Control |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, count in summary["family_counts"].items():
        lines.append(
            f"| `{family}` | {count} | "
            f"{summary['hard_family_counts'].get(family, 0)} | "
            f"{summary['control_family_counts'].get(family, 0)} |"
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source current artifact: `{summary['source_current_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _panel_row(
    row: Mapping[str, Any],
    records_by_source: Mapping[int, Any],
    *,
    seed_family: str,
    hard: bool,
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    record = records_by_source[source_row_index]
    return {
        "artifact_kind": "gan2026_structured_seed_validation_panel_row",
        "policy_name": POLICY_NAME,
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "panel_role": "hard" if hard else "control",
        "seed_family": seed_family,
        "expected_generator_action": "emit_candidate" if hard else "suppress_candidate",
        "current_label": row.get("final_label"),
        "gold_label": row.get("gold_label"),
        "expected_candidate_label": row.get("gold_label") if hard else None,
        "unsafe_candidate_label": row.get("gold_label") if not hard else None,
        "expected_evidence_substring": _record_value(record, "gold_reference"),
        "source_note_text": None,
        "claim_boundary": "validation_development_only_no_holdout_use",
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


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-jsonl-path", type=Path, default=DEFAULT_CURRENT_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_validation_panel(
        current_jsonl_path=args.current_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {"decision": summary["decision"], "row_count": summary["row_count"]},
            sort_keys=True,
        )
    )


def _record_value(record: Any, field: str) -> str:
    if isinstance(record, Mapping):
        return str(record[field])
    return str(getattr(record, field))


if __name__ == "__main__":
    main()
