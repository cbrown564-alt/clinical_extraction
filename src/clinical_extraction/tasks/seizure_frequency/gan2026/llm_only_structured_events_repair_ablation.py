"""No-call repair-family ablation for structured Gan 2026 LLM artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_only_structured_events import (
    StructuredRepairConfig,
    load_reusable_raw_outputs,
    run_split,
)

DEFAULT_INPUT_JSONL = Path(
    "experiments/gan2026_llm_only_structured_events_validation750_gpt41mini_v05_completion_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation750_v05_repair_ablation_2026-06-01.md"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation750_v05_repair_ablation_2026-06-01.json"
)


def repair_ablation_ladder() -> list[tuple[str, StructuredRepairConfig]]:
    """Return the cumulative repair-family ladder from the v0.5 repair audit."""

    off: dict[str, Any] = {
        "basic_label_repair": False,
        "basic_label_repair_format_only": False,
        "selected_evidence_repair": False,
        "monthly_diary_repair": False,
        "usual_interval_repair": False,
        "breakthrough_repair": False,
        "non_epileptic_repair": False,
        "residual_jerk_repair": False,
        "post_change_burst_repair": False,
        "dated_sequence_repair": False,
        "elapsed_anchor_repair": False,
    }
    cumulative = dict(off)
    ladder = [
        (
            "A_raw_llm_final_label_only",
            StructuredRepairConfig.for_mode("raw_model"),
        )
    ]
    cumulative["basic_label_repair"] = True
    cumulative["basic_label_repair_format_only"] = True
    ladder.append(
        (
            "B_format_preserving_basic_label_repair",
            StructuredRepairConfig.for_mode("strict_format"),
        )
    )
    cumulative["basic_label_repair_format_only"] = False
    ladder.append(("C_full_basic_gan_label_repair", StructuredRepairConfig(**cumulative)))
    for name, key in [
        ("D_selected_evidence_repair", "selected_evidence_repair"),
        ("E_monthly_diary_arithmetic", "monthly_diary_repair"),
        ("F_usual_interval_override", "usual_interval_repair"),
        ("G_breakthrough_after_seizure_free", "breakthrough_repair"),
        ("H_non_epileptic_override", "non_epileptic_repair"),
        ("I_residual_jerk_date_anchor", "residual_jerk_repair"),
        ("J_post_change_burst", "post_change_burst_repair"),
        ("K_dated_sequence", "dated_sequence_repair"),
        ("L_elapsed_anchor", "elapsed_anchor_repair"),
    ]:
        cumulative[key] = True
        ladder.append((name, StructuredRepairConfig(**cumulative)))
    ladder.append(("M_full_current_stack", StructuredRepairConfig()))
    return ladder


def run_repair_ablation(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    reuse_jsonl: Path,
    model: str = "openai/gpt-4.1-mini",
) -> dict[str, Any]:
    """Replay saved raw outputs under each repair-family condition."""

    raw_outputs = load_reusable_raw_outputs(reuse_jsonl)
    records = [record for record in records if record.source_row_index in raw_outputs]
    conditions: list[dict[str, Any]] = []
    previous_rows: Sequence[Mapping[str, Any]] | None = None
    for condition_name, repair_config in repair_ablation_ladder():
        rows, metadata = run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=0.0,
            max_tokens=0,
            mode="prompt-only",
            dspy_cache=True,
            reuse_raw_outputs=raw_outputs,
            reuse_source=str(reuse_jsonl),
            escalation_reason="No-call repair-family ablation over saved raw outputs.",
            progress_every=None,
            checkpoint_jsonl_path=None,
            checkpoint_report_path=None,
            repair_config=repair_config,
        )
        conditions.append(
            {
                "name": condition_name,
                "repair_mode": repair_config.resolved_repair_mode,
                "repair_config": asdict(repair_config),
                "summary": _condition_summary(rows, previous_rows),
                "top_changed_rows": _top_changed_rows(rows, previous_rows),
                "slices": _slice_summaries(rows, previous_rows),
            }
        )
        previous_rows = rows
    return {
        "split": split,
        "split_manifest": split_manifest,
        "reuse_jsonl": str(reuse_jsonl),
        "model": model,
        "conditions": conditions,
    }


def write_ablation_json(result: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_ablation_report(result: Mapping[str, Any], path: Path, *, json_path: Path) -> None:
    lines = [
        "# Gan 2026 Structured LLM V0.5 Repair-Family Ablation",
        "",
        "This is a validation development no-call replay over saved raw model outputs. "
        "It is not a final holdout or benchmark result.",
        "",
        f"- Split: `{result['split']}`",
        f"- Split manifest: `{result['split_manifest']}`",
        f"- Raw-output source: `{result['reuse_jsonl']}`",
        f"- JSON summary: `{json_path}`",
        "",
        "## Condition Summary",
        "",
        "| Condition | Purist | Pragmatic | Exact label | Semantic kind | Evidence | "
        "Improved | Regressed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in result["conditions"]:
        summary = condition["summary"]
        lines.append(
            f"| {condition['name']} | {summary['purist_accuracy']:.4f} | "
            f"{summary['pragmatic_accuracy']:.4f} | {summary['exact_label_accuracy']:.4f} | "
            f"{summary['semantic_kind_accuracy']:.4f} | {summary['evidence_rate']:.4f} | "
            f"{summary['improved_vs_previous']} | {summary['regressed_vs_previous']} |"
        )
    condition_by_name = {condition["name"]: condition for condition in result["conditions"]}
    if "B_format_preserving_basic_label_repair" in condition_by_name:
        raw = condition_by_name["A_raw_llm_final_label_only"]["summary"]
        strict_basic = condition_by_name["B_format_preserving_basic_label_repair"]["summary"]
        full_basic = condition_by_name["C_full_basic_gan_label_repair"]["summary"]
        lines.extend(
            [
                "",
                "## Basic Repair Split Interpretation",
                "",
                "The clean LLM-only structured-events attribution baseline is raw "
                "model selection plus format-preserving basic label repair only. "
                "This condition keeps casing, "
                "plural units, compact rate syntax, event-word cleanup, and directly "
                "stated every/each-period phrasing, but excludes vague-quantity remapping, "
                "semantic fallback to unknown/no-reference, impossible-denominator fallback, "
                "and final catch-all coercion.",
                "",
                f"- Raw model selection: {raw['purist_correct']} / {raw['rows']} Purist "
                f"correct = {raw['purist_accuracy']:.4f}.",
                f"- Format-preserving basic repair: {strict_basic['purist_correct']} / "
                f"{strict_basic['rows']} Purist correct = "
                f"{strict_basic['purist_accuracy']:.4f}; "
                f"{strict_basic['improved_vs_previous']} improved and "
                f"{strict_basic['regressed_vs_previous']} regressed versus raw.",
                f"- Full basic repair: {full_basic['purist_correct']} / {full_basic['rows']} "
                f"Purist correct = {full_basic['purist_accuracy']:.4f}; this remains an "
                "upper-bound diagnostic because it includes semantic fallback and "
                "vague-quantity remapping.",
                "",
                "Use the format-preserving condition, not the full basic condition, for "
                "clean LLM-only structured-events attribution. Treat the full "
                "basic condition as a named deterministic repair module if it "
                "is retained.",
            ]
        )
    lines.extend(["", "## Top Changed Rows", ""])
    for condition in result["conditions"][1:]:
        lines.extend([f"### {condition['name']}", ""])
        changed_rows = condition["top_changed_rows"]
        if not changed_rows:
            lines.extend(["No final-label changes versus the previous condition.", ""])
            continue
        lines.extend(
            [
                "| Row | Previous | New | Gold | Purist Before | Purist After | Notes |",
                "| ---: | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in changed_rows:
            lines.append(
                f"| {row['source_row_index']} | {row['previous_label']} | {row['new_label']} | "
                f"{row['gold_label']} | {_yes_no(row['previous_purist'])} | "
                f"{_yes_no(row['new_purist'])} | {row['notes']} |"
            )
        lines.append("")
    lines.extend(["## Minimum Row-Level Slices", ""])
    for condition in result["conditions"]:
        lines.extend([f"### {condition['name']}", ""])
        lines.extend(
            [
                "| Slice | Rows | Purist | Exact label | Improved | Regressed |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for name, summary in condition["slices"].items():
            lines.append(
                f"| {name} | {summary['rows']} | {summary['purist_accuracy']:.4f} | "
                f"{summary['exact_label_accuracy']:.4f} | {summary['improved_vs_previous']} | "
                f"{summary['regressed_vs_previous']} |"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _condition_summary(
    rows: Sequence[Mapping[str, Any]],
    previous_rows: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    count = len(rows)
    purist = sum(_purist_correct(row) for row in rows)
    pragmatic = sum(_pragmatic_correct(row) for row in rows)
    exact = sum(_exact_label_match(row) for row in rows)
    semantic = sum(_semantic_kind_match(row) for row in rows)
    evidence = sum(bool(row.get("evidence_valid")) for row in rows)
    improved, regressed = _changed_correctness_counts(rows, previous_rows)
    return {
        "rows": count,
        "purist_correct": purist,
        "purist_accuracy": round(purist / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
        "exact_label_correct": exact,
        "exact_label_accuracy": round(exact / count, 4) if count else 0.0,
        "semantic_kind_correct": semantic,
        "semantic_kind_accuracy": round(semantic / count, 4) if count else 0.0,
        "evidence_exact_substring": evidence,
        "evidence_rate": round(evidence / count, 4) if count else 0.0,
        "improved_vs_previous": improved,
        "regressed_vs_previous": regressed,
    }


def _top_changed_rows(
    rows: Sequence[Mapping[str, Any]],
    previous_rows: Sequence[Mapping[str, Any]] | None,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if previous_rows is None:
        return []
    previous_by_index = {row["source_row_index"]: row for row in previous_rows}
    changed = []
    for row in rows:
        previous = previous_by_index.get(row["source_row_index"])
        if previous is None or _final_label(previous) == _final_label(row):
            continue
        changed.append(
            {
                "source_row_index": row["source_row_index"],
                "previous_label": _final_label(previous),
                "new_label": _final_label(row),
                "gold_label": row["reference"]["gold_label"],
                "previous_purist": _purist_correct(previous),
                "new_purist": _purist_correct(row),
                "notes": "; ".join(row.get("parse_errors") or []),
            }
        )
    changed.sort(key=lambda item: (not item["new_purist"], item["source_row_index"]))
    return changed[:limit]


def _slice_summaries(
    rows: Sequence[Mapping[str, Any]],
    previous_rows: Sequence[Mapping[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    previous_by_index = (
        {row["source_row_index"]: row for row in previous_rows} if previous_rows else {}
    )
    slices = {
        "seizure_free_gold": [row for row in rows if "seizure free" in _gold_label(row)],
        "unknown_or_no_reference_gold": [
            row
            for row in rows
            if _gold_label(row) in {"unknown", "no seizure frequency reference"}
        ],
        "cluster_gold": [row for row in rows if "cluster" in _gold_label(row)],
        "monthly_diary": [
            row
            for row in rows
            if _text_matches(row, r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)")
        ],
        "year_to_date_or_current_year": [
            row
            for row in rows
            if _text_matches(row, r"\b(this year|year to date|so far this year)\b")
        ],
        "dated_sequence": [
            row
            for row in rows
            if _text_matches(row, r"\b(first|second|third)\b.*\b\d{4}\b")
        ],
        "row_ok_false": [row for row in rows if row.get("reference", {}).get("row_ok") is False],
        "purist_correct_exact_label_wrong": [
            row for row in rows if _purist_correct(row) and not _exact_label_match(row)
        ],
    }
    summaries = {}
    for name, slice_rows in slices.items():
        previous_slice_rows = [
            previous_by_index[row["source_row_index"]]
            for row in slice_rows
            if row["source_row_index"] in previous_by_index
        ]
        summaries[name] = _condition_summary(slice_rows, previous_slice_rows or None)
    return summaries


def _changed_correctness_counts(
    rows: Sequence[Mapping[str, Any]],
    previous_rows: Sequence[Mapping[str, Any]] | None,
) -> tuple[int, int]:
    if previous_rows is None:
        return 0, 0
    previous_by_index = {row["source_row_index"]: row for row in previous_rows}
    improved = 0
    regressed = 0
    for row in rows:
        previous = previous_by_index.get(row["source_row_index"])
        if previous is None:
            continue
        before = _purist_correct(previous)
        after = _purist_correct(row)
        improved += int(not before and after)
        regressed += int(before and not after)
    return improved, regressed


def _final_label(row: Mapping[str, Any]) -> str | None:
    structured = row.get("structured_record") or {}
    selection = structured.get("selection") or {}
    label = selection.get("final_label")
    return label if isinstance(label, str) else None


def _final_frequency_kind(row: Mapping[str, Any]) -> str | None:
    label = _final_label(row)
    if not label:
        return None
    try:
        return str(label_to_frequency_record(label).kind)
    except ValueError:
        return None


def _gold_label(row: Mapping[str, Any]) -> str:
    reference = row.get("reference", {})
    return str(reference.get("gold_normalized_label") or reference["gold_label"])


def _purist_correct(row: Mapping[str, Any]) -> bool:
    return bool((row.get("comparison") or {}).get("purist_correct"))


def _pragmatic_correct(row: Mapping[str, Any]) -> bool:
    return bool((row.get("comparison") or {}).get("pragmatic_correct"))


def _exact_label_match(row: Mapping[str, Any]) -> bool:
    return _final_label(row) == _gold_label(row)


def _semantic_kind_match(row: Mapping[str, Any]) -> bool:
    return _final_frequency_kind(row) == row.get("reference", {}).get("gold_label_kind")


def _text_matches(row: Mapping[str, Any], pattern: str) -> bool:
    prompt = json.loads(str(row.get("prompt_input_json") or "{}"))
    note_text = str(prompt.get("note_text") or "")
    return re.search(pattern, note_text.lower(), flags=re.DOTALL) is not None


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a no-call repair-family ablation over LLM-only structured-events "
            "raw outputs."
        )
    )
    parser.add_argument("--split", choices=("train", "validation"), default="validation")
    parser.add_argument("--reuse-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    args = parser.parse_args(argv)

    records = load_records_for_split(args.split)
    if args.limit is not None:
        records = records[: args.limit]
    manifest = load_split_manifest()
    result = run_repair_ablation(
        records,
        split=args.split,
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        reuse_jsonl=args.reuse_jsonl,
        model=args.model,
    )
    write_ablation_json(result, args.json)
    write_ablation_report(result, args.markdown, json_path=args.json)
    print(json.dumps(result["conditions"][-1]["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
