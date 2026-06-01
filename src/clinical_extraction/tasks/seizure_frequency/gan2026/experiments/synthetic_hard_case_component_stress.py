"""Synthetic hard-case component stress runner for Gan 2026 hybrid adjudicators."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    architecture_component_ablation as component_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    hybrid_rules_candidates_llm_adjudicator as hybrid_adjudicator,
)

SYNTHETIC_SOURCE_INDEX_BASE = 900_000
SYNTHETIC_SPLIT_NAME = "synthetic_hard_cases"
SYNTHETIC_SPLIT_MANIFEST = "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01"
DEFAULT_HARD_CASES_JSONL_PATH = Path(
    "experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_gpt41mini_live_2026-06-01.md"
)
DEFAULT_COMPONENT_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.json"
)
DEFAULT_COMPONENT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md"
)


def load_synthetic_hard_cases(path: Path) -> list[dict[str, Any]]:
    """Load reviewed synthetic hard-case rows from JSONL."""

    return load_jsonl_rows(path)


def synthetic_records_from_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    source_index_base: int = SYNTHETIC_SOURCE_INDEX_BASE,
) -> list[GanFrequencyRecord]:
    """Convert reviewed hard cases into scored Gan-like records."""

    records = []
    for offset, case in enumerate(cases):
        label_record = label_to_frequency_record(str(case["expected_final_label"]))
        records.append(
            GanFrequencyRecord(
                source_row_index=source_index_base + offset,
                note_text=str(case["source_note_text"]),
                gold_label=str(case["expected_final_label"]),
                gold_reference=str(case["expected_evidence_substring"]),
                labels_match_all_categories=True,
                quotes_ok_all_categories=True,
                row_ok=True,
                raw=dict(case),
                gold_normalized_label=label_record.normalized_label,
                gold_label_kind=label_record.kind,
                gold_yearly_bounds=label_record.yearly_bounds,
                gold_monthly_frequency=label_record.monthly_frequency,
            )
        )
    return records


def attach_hard_case_metadata(
    rows: Sequence[dict[str, Any]],
    cases: Sequence[Mapping[str, Any]],
    *,
    source_index_base: int = SYNTHETIC_SOURCE_INDEX_BASE,
) -> list[dict[str, Any]]:
    """Attach case ids/families to saved hybrid rows without exposing gold in prompts."""

    case_by_index = {
        source_index_base + offset: case for offset, case in enumerate(cases)
    }
    enriched = []
    for row in rows:
        row_copy = dict(row)
        case = case_by_index.get(int(row["source_row_index"]))
        if case is not None:
            row_copy["hard_case"] = {
                "case_id": case["case_id"],
                "failure_family": case["failure_family"],
                "expected_answer_kind": case["expected_answer_kind"],
                "allowed_llm_action": case["allowed_llm_action"],
                "deterministic_failure_rationale": case[
                    "deterministic_failure_rationale"
                ],
            }
        enriched.append(row_copy)
    return enriched


def build_component_stress_result(
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    artifact_path: str | None,
) -> dict[str, Any]:
    """Build component condition summaries plus hard-case family summaries."""

    conditions = component_ablation.condition_from_hybrid_rules_candidates_llm_adjudicator_rows(
        rows,
        artifact_path=artifact_path,
    )
    result = component_ablation.build_component_ablation_result(
        conditions,
        split=split,
        split_manifest=split_manifest,
    )
    result.update(
        {
            "artifact_kind": "gan2026_hybrid_adjudicator_synthetic_hard_case_component_stress",
            "source_artifact": artifact_path,
            "row_policy": (
                "Reviewed synthetic hard-case development panel; not validation, not holdout, "
                "and not a benchmark claim."
            ),
            "family_summaries": _family_summaries(rows),
        }
    )
    return result


def write_component_stress_report(result: Mapping[str, Any], path: Path) -> None:
    """Write a compact hard-panel interpretation report."""

    lines = [
        "# Gan 2026 Hybrid Adjudicator V0.2 Synthetic Hard-Case Component Stress",
        "",
        "This is a reviewed synthetic development panel. It is not validation, holdout, "
        "or a benchmark claim.",
        "",
        f"- Split: `{result['split']}`",
        f"- Split manifest: `{result['split_manifest']}`",
        f"- Source artifact: `{result.get('source_artifact') or 'in-memory rows'}`",
        "",
        "## Component Summary",
        "",
        "| Condition | Rows | Purist | Pragmatic | Changed | Improved | Regressed | Issues |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    comparisons = {
        comparison["candidate"]: comparison for comparison in result.get("comparisons", [])
    }
    for condition in result.get("conditions", []):
        summary = condition["summary"]
        comparison = comparisons.get(condition["name"], {})
        lines.append(
            f"| {condition['name']} | {summary['rows']} | "
            f"{summary['purist_accuracy']:.4f} | {summary['pragmatic_accuracy']:.4f} | "
            f"{comparison.get('changed_labels', 0)} | "
            f"{comparison.get('wrong_to_correct', 0)} | "
            f"{comparison.get('correct_to_wrong', 0)} | "
            f"{summary['parse_or_validation_issues']} |"
        )
    lines.extend(
        [
            "",
            "## Failure Families",
            "",
            "| Family | Rows | Deterministic correct | Raw correct | Gated correct | "
            "Raw W->C | Raw C->W | Gated W->C | Gated C->W |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for family, summary in sorted(result.get("family_summaries", {}).items()):
        lines.append(
            f"| {family} | {summary['rows']} | {summary['deterministic_purist_correct']} | "
            f"{summary['raw_purist_correct']} | {summary['gated_purist_correct']} | "
            f"{summary['raw_wrong_to_correct']} | {summary['raw_correct_to_wrong']} | "
            f"{summary['gated_wrong_to_correct']} | {summary['gated_correct_to_wrong']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run hybrid adjudicator v0.2 over the reviewed synthetic hard-case panel "
            "and write component-stress artifacts."
        )
    )
    parser.add_argument("--hard-cases-jsonl", type=Path, default=DEFAULT_HARD_CASES_JSONL_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--component-json", type=Path, default=DEFAULT_COMPONENT_JSON_PATH)
    parser.add_argument(
        "--component-markdown",
        type=Path,
        default=DEFAULT_COMPONENT_REPORT_PATH,
    )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1100)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--disable-dspy-cache", action="store_true")
    parser.add_argument("--progress-every", type=int, default=10)
    args = parser.parse_args(argv)

    cases = load_synthetic_hard_cases(args.hard_cases_jsonl)
    records = synthetic_records_from_cases(cases)
    rows, metadata = hybrid_adjudicator.run_hybrid_rules_candidates_llm_adjudicator_split(
        records,
        split=SYNTHETIC_SPLIT_NAME,
        split_manifest=SYNTHETIC_SPLIT_MANIFEST,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.disable_dspy_cache,
        escalation_reason="component stress over approved synthetic hard-case panel",
        progress_every=args.progress_every if args.progress_every > 0 else None,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
    )
    enriched_rows = attach_hard_case_metadata(rows, cases)
    metadata["summary"] = metadata["summary"] | _hard_case_summary(enriched_rows)
    hybrid_adjudicator.write_hybrid_rules_candidates_llm_adjudicator_jsonl(
        enriched_rows,
        args.jsonl,
    )
    hybrid_adjudicator.write_hybrid_rules_candidates_llm_adjudicator_report(
        enriched_rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
    )
    result = build_component_stress_result(
        enriched_rows,
        split=SYNTHETIC_SPLIT_NAME,
        split_manifest=SYNTHETIC_SPLIT_MANIFEST,
        artifact_path=str(args.jsonl),
    )
    component_ablation.write_component_ablation_json(result, args.component_json)
    conditions = component_ablation.condition_from_hybrid_rules_candidates_llm_adjudicator_rows(
        enriched_rows,
        artifact_path=str(args.jsonl),
    )
    component_ablation.write_component_ablation_report(
        conditions,
        args.component_markdown,
        split=SYNTHETIC_SPLIT_NAME,
        split_manifest=SYNTHETIC_SPLIT_MANIFEST,
    )
    write_component_stress_report(result, args.component_markdown)
    print(
        json.dumps(
            {
                "rows": len(enriched_rows),
                "jsonl": str(args.jsonl),
                "component_json": str(args.component_json),
                "component_markdown": str(args.component_markdown),
                "summary": metadata["summary"],
            },
            sort_keys=True,
        )
    )


def _family_summaries(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        hard_case = row.get("hard_case") or {}
        grouped[str(hard_case.get("failure_family", "unknown"))].append(row)
    return {family: _summarize_family(family_rows) for family, family_rows in grouped.items()}


def _summarize_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    deterministic_correct = raw_correct = gated_correct = 0
    raw_wrong_to_correct = raw_correct_to_wrong = 0
    gated_wrong_to_correct = gated_correct_to_wrong = 0
    for row in rows:
        scores = row.get("scores") or {}
        deterministic = scores.get("deterministic_top") or {}
        raw = scores.get("raw_adjudicator") or {}
        gated = scores.get("conservative_adjudicator") or {}
        det_ok = bool(deterministic.get("purist_correct"))
        raw_ok = bool(raw.get("purist_correct"))
        gated_ok = bool(gated.get("purist_correct"))
        deterministic_correct += det_ok
        raw_correct += raw_ok
        gated_correct += gated_ok
        raw_wrong_to_correct += (not det_ok) and raw_ok
        raw_correct_to_wrong += det_ok and not raw_ok
        gated_wrong_to_correct += (not det_ok) and gated_ok
        gated_correct_to_wrong += det_ok and not gated_ok
    return {
        "rows": len(rows),
        "deterministic_purist_correct": deterministic_correct,
        "raw_purist_correct": raw_correct,
        "gated_purist_correct": gated_correct,
        "raw_wrong_to_correct": raw_wrong_to_correct,
        "raw_correct_to_wrong": raw_correct_to_wrong,
        "gated_wrong_to_correct": gated_wrong_to_correct,
        "gated_correct_to_wrong": gated_correct_to_wrong,
    }


def _hard_case_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    families = _family_summaries(rows)
    return {
        "synthetic_hard_cases": len(rows),
        "synthetic_failure_families": len(families),
    }


if __name__ == "__main__":
    main()
