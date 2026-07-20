"""Replay and attribute the frozen Gan six-model validation panel without calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import convert_to_categories
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_canonical_pipeline import (
    parse_decision_json_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)

BLOCKING_PREFIXES = (
    "invalid_json:",
    "json_parse_error:",
    "schema_validation_error:",
    "unscorable_final_label:",
    "not_run",
)


def classify_first_failure(
    *,
    call_error: str | None,
    parse_errors: Sequence[str],
    evidence_valid: bool,
    model_correct: bool,
    final_correct: bool,
) -> str:
    if call_error:
        return "model_transport"
    if any(str(error).startswith(BLOCKING_PREFIXES) for error in parse_errors):
        return "format_or_schema"
    if not evidence_valid:
        return "evidence_selection"
    if model_correct and not final_correct:
        return "deterministic_semantic"
    if not model_correct and not final_correct:
        return "llm_clinical_selection"
    return "none"


def classify_subproblem(evidence: str, label: str, events: Sequence[str]) -> str:
    text = " ".join([evidence, label, *events]).lower()
    if "cluster" in text or "diary" in text:
        return "cluster_or_diary_aggregation"
    if "seizure free" in text or "seizure-free" in text or "no seizures" in text:
        return "seizure_free_boundary"
    if "unknown" in text or "uncertain" in text or "no reference" in text:
        return "uncertainty_boundary"
    if any(token in text for token in ("historical", "recent", "current", "since ")):
        return "temporal_selection"
    if any(token in text for token in (" per ", "daily", "weekly", "monthly", "yearly")):
        return "rate_denominator"
    return "competing_event_selection"


def build_analysis(
    repo_root: Path,
    config_path: Path,
    *,
    retained_artifact_root: Path | None = None,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rules_path = repo_root / (
        "experiments/gan2026_three_way_comparison_validation750_"
        "deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
    )
    rules_rows = {int(row["source_row_index"]): row for row in load_jsonl_rows(rules_path)}
    detail_rows: list[dict[str, Any]] = []
    conditions: list[dict[str, Any]] = []
    rows_by_pair: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}

    for model in config["conditions"]:
        for method in config["methods"]:
            slug = str(model["slug"])
            method_name = str(method["method"])
            relative = (
                retained_artifact_root / f"{slug}--{method_name}.jsonl"
                if retained_artifact_root is not None
                else Path(str(config["artifact_root"]))
                / slug
                / method_name
                / "validation750.rows.jsonl"
            )
            path = repo_root / relative
            source_rows = load_jsonl_rows(path)
            if len(source_rows) != 750:
                raise ValueError(f"{relative} has {len(source_rows)} rows, expected 750")
            condition_details: dict[int, dict[str, Any]] = {}
            original_success = replay_success = recovered = 0
            selected_answer_changes = 0
            repair_counts: Counter[str] = Counter()
            failures: Counter[str] = Counter()
            subproblems: Counter[str] = Counter()
            rules_correct_regressions = 0
            model_boundary_correct = 0
            final_correct_count = 0
            evidence_valid_count = 0
            model_to_final_changed = 0

            for row in source_rows:
                index = int(row["source_row_index"])
                current_label = _final_label(row, method_name)
                raw_field = ((row.get("row_trace") or {}).get("model_prediction") or {}).get(
                    "raw_output_field"
                ) or "raw_output"
                raw_output = str(row.get(raw_field) or row.get("raw_output") or "")
                prompt = _json_mapping(row.get("prompt_input_json"))
                if method_name == "llm_with_rules":
                    extraction, _, replay_errors, replay_trace = parse_structured_json_with_trace(
                        raw_output,
                        note_text=str(prompt.get("note_text") or ""),
                        repair_config=StructuredRepairConfig.for_mode("hybrid_full_stack"),
                    )
                    replay_label = extraction.selection.final_label if extraction else None
                    evidence = extraction.selection.evidence if extraction else ""
                else:
                    decision, replay_errors, replay_trace = parse_decision_json_with_trace(
                        raw_output
                    )
                    replay_label = decision.final_label if decision else None
                    evidence = decision.evidence if decision else ""

                original_ok = current_label is not None
                replay_ok = replay_label is not None
                original_success += int(original_ok)
                replay_success += int(replay_ok)
                recovered += int(not original_ok and replay_ok)
                if original_ok and replay_label != current_label:
                    selected_answer_changes += 1

                format_events = list((replay_trace.get("format_repair") or {}).get("events") or [])
                semantic_events = list(
                    (replay_trace.get("deterministic_semantic") or {}).get("events") or []
                )
                for event in format_events:
                    repair_counts[_repair_class(str(event))] += 1

                final_correct = bool((row.get("comparison") or {}).get("purist_correct"))
                model_label = _model_boundary_label(row, method_name)
                gold_monthly = float((row.get("reference") or {})["gold_monthly_frequency"])
                model_correct = _purist_correct(model_label, gold_monthly)
                evidence_valid = bool(
                    row.get("evidence_valid")
                    if method_name == "llm_with_rules"
                    else row.get("evidence_text_contained")
                )
                model_boundary_correct += int(model_correct)
                final_correct_count += int(final_correct)
                evidence_valid_count += int(evidence_valid)
                model_to_final_changed += int(
                    model_label is not None
                    and current_label is not None
                    and model_label != current_label
                )
                failure_owner = classify_first_failure(
                    call_error=str(row.get("call_error")) if row.get("call_error") else None,
                    parse_errors=[str(value) for value in row.get("parse_errors") or []],
                    evidence_valid=evidence_valid,
                    model_correct=model_correct,
                    final_correct=final_correct,
                )
                failures[failure_owner] += 1
                subproblem = classify_subproblem(
                    evidence, replay_label or current_label or "", semantic_events
                )
                subproblems[subproblem] += 1
                rules_row = rules_rows.get(index) or {}
                rules_correct = bool((rules_row.get("comparison") or {}).get("purist_correct"))
                rules_regression = rules_correct and not final_correct
                rules_correct_regressions += int(rules_regression)

                detail = {
                    "model_slug": slug,
                    "model": model["model"],
                    "method": method_name,
                    "source_row_index": index,
                    "artifact_sha256": _sha256(path),
                    "original_parse_success": original_ok,
                    "replay_parse_success": replay_ok,
                    "recovered_by_replay": not original_ok and replay_ok,
                    "selected_answer_changed": original_ok and replay_label != current_label,
                    "original_final_label": current_label,
                    "replay_final_label": replay_label,
                    "model_boundary_label": model_label,
                    "purist_correct": final_correct,
                    "model_boundary_purist_correct": model_correct,
                    "rules_purist_correct": rules_correct,
                    "rules_correct_regression": rules_regression,
                    "evidence_valid": evidence_valid,
                    "format_events": format_events,
                    "semantic_events": semantic_events,
                    "first_failure_owner": failure_owner,
                    "clinical_subproblem": subproblem,
                }
                detail_rows.append(detail)
                condition_details[index] = detail

            if selected_answer_changes:
                raise ValueError(f"{slug}/{method_name} changed {selected_answer_changes} answers")
            rows_by_pair[(slug, method_name)] = condition_details
            conditions.append(
                {
                    "model_slug": slug,
                    "model": model["model"],
                    "method": method_name,
                    "artifact": relative.as_posix(),
                    "artifact_sha256": _sha256(path),
                    "rows": len(source_rows),
                    "original_parse_success": original_success,
                    "replay_parse_success": replay_success,
                    "recovered_by_replay": recovered,
                    "selected_answer_changes": selected_answer_changes,
                    "repair_events": dict(sorted(repair_counts.items())),
                    "model_boundary_purist_correct": model_boundary_correct,
                    "final_purist_correct": final_correct_count,
                    "evidence_valid": evidence_valid_count,
                    "model_to_final_changed": model_to_final_changed,
                    "first_failure_owner": dict(sorted(failures.items())),
                    "clinical_subproblem": dict(sorted(subproblems.items())),
                    "rules_correct_regressions": rules_correct_regressions,
                }
            )

    comparisons = []
    for model in config["conditions"]:
        slug = str(model["slug"])
        llm = rows_by_pair[(slug, "llm_only")]
        rules = rows_by_pair[(slug, "llm_with_rules")]
        transitions = Counter()
        owner = Counter()
        evidence = Counter()
        regressions = Counter()
        examples: dict[str, list[int]] = defaultdict(list)
        for index in sorted(llm):
            left = llm[index]
            right = rules[index]
            if not left["purist_correct"] and right["purist_correct"]:
                direction = "llm_only_wrong_to_rules_correct"
            elif left["purist_correct"] and not right["purist_correct"]:
                direction = "llm_only_correct_to_rules_wrong"
            elif left["purist_correct"] and right["purist_correct"]:
                direction = "both_correct"
            else:
                direction = "both_wrong"
            transitions[direction] += 1
            if direction in {"llm_only_wrong_to_rules_correct", "llm_only_correct_to_rules_wrong"}:
                changed_by_deterministic = (
                    right["model_boundary_label"] is not None
                    and right["model_boundary_label"] != right["original_final_label"]
                )
                owner[
                    "deterministic_semantic"
                    if changed_by_deterministic
                    else "llm_clinical_selection"
                ] += 1
                evidence["both_valid"] += int(left["evidence_valid"] and right["evidence_valid"])
                regressions[right["clinical_subproblem"]] += int(
                    direction == "llm_only_correct_to_rules_wrong"
                )
                if len(examples[direction]) < 8:
                    examples[direction].append(index)
        comparisons.append(
            {
                "model_slug": slug,
                "model": model["model"],
                "transitions": dict(sorted(transitions.items())),
                "changed_row_owner": dict(sorted(owner.items())),
                "changed_rows_both_evidence_valid": evidence["both_valid"],
                "regressions_by_subproblem": dict(sorted(regressions.items())),
                "representative_source_rows": dict(examples),
            }
        )

    return {
        "schema_version": "gan2026.six_model_post_panel_attribution.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": (
            "docs/experiments/gan2026/gan2026_six_model_post_panel_replay_protocol_2026-07-20.md"
        ),
        "dataset": "Gan 2026",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "development_row_level",
        "replay_mode": "saved_raw_output_no_call",
        "scorer": "Gan Purist primary; Pragmatic secondary",
        "repair_policy": (
            "selected_answer_preserving_schema_replay_v1 + frozen downstream hybrid_full_stack"
        ),
        "rules_comparator": {
            "artifact": rules_path.relative_to(repo_root).as_posix(),
            "artifact_sha256": _sha256(rules_path),
            "rows": len(rules_rows),
        },
        "conditions": conditions,
        "method_comparisons": comparisons,
        "rows": detail_rows,
        "claim_boundary": (
            "Development component evidence for the named validation split and frozen routes; "
            "not holdout evidence, clinical validation, or a model-neutral ranking."
        ),
    }


def write_report(analysis: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 six-model post-panel replay and component audit",
        "",
        f"Generated: {analysis['generated_at_utc']}",
        "",
        "Development evidence on `validation750`; no model calls or test rows were used.",
        "",
        "## Replay result",
        "",
        (
            "| Model | Method | Original valid | Replay valid | Recovered | "
            "Answer changes | Rules-correct regressions |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in analysis["conditions"]:
        lines.append(
            f"| {item['model_slug']} | `{item['method']}` | {item['original_parse_success']}/750 | "
            f"{item['replay_parse_success']}/750 | {item['recovered_by_replay']} | "
            f"{item['selected_answer_changes']} | {item['rules_correct_regressions']} |"
        )
    lines.extend(
        [
            "",
            "## Score-layer and evidence ladder",
            "",
            (
                "| Model | Method | Model boundary correct | Final correct | "
                "Model → final changes | Exact evidence |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in analysis["conditions"]:
        lines.append(
            f"| {item['model_slug']} | `{item['method']}` | "
            f"{item['model_boundary_purist_correct']}/750 | {item['final_purist_correct']}/750 | "
            f"{item['model_to_final_changed']} | {item['evidence_valid']}/750 |"
        )
    lines.extend(
        [
            "",
            "## Matched method transitions",
            "",
            (
                "| Model | Rules rescue | Rules regression | Both correct | Both wrong | "
                "Changed rows with valid evidence |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in analysis["method_comparisons"]:
        t = item["transitions"]
        lines.append(
            f"| {item['model_slug']} | {t.get('llm_only_wrong_to_rules_correct', 0)} | "
            f"{t.get('llm_only_correct_to_rules_wrong', 0)} | {t.get('both_correct', 0)} | "
            f"{t.get('both_wrong', 0)} | {item['changed_rows_both_evidence_valid']} |"
        )
    owner = Counter()
    subproblems = Counter()
    for item in analysis["conditions"]:
        owner.update(item["first_failure_owner"])
        subproblems.update(item["clinical_subproblem"])
    lines.extend(["", "## First failure owner", ""])
    for key, count in owner.most_common():
        lines.append(f"- `{key}`: {count}")
    lines.extend(["", "## Clinical subproblem distribution", ""])
    for key, count in subproblems.most_common():
        lines.append(f"- `{key}`: {count}")
    lines.extend(
        [
            "",
            "## Changed-row ownership",
            "",
            "| Model | Model clinical selection | Deterministic semantic |",
            "| --- | ---: | ---: |",
        ]
    )
    for item in analysis["method_comparisons"]:
        changed_owner = item["changed_row_owner"]
        lines.append(
            f"| {item['model_slug']} | {changed_owner.get('llm_clinical_selection', 0)} | "
            f"{changed_owner.get('deterministic_semantic', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The replay is accepted only if selected-answer changes remain zero. "
                "Recovered records are attributed to bounded format/schema repair, not "
                "clinical reasoning. Matched method gains are development evidence and "
                "retain every deterministic regression and evidence failure in the machine "
                "artifact."
            ),
            "",
            "## Claim boundary",
            "",
            str(analysis["claim_boundary"]),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _repair_class(event: str) -> str:
    if event.startswith("json_dialect_repaired:"):
        return "syntax_only"
    if event.startswith("container_shape_repaired:"):
        return "container_shape"
    if event.startswith("unselected_event_quarantined:"):
        return "quarantined_unselected_event"
    return "other_format"


def _json_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, Mapping) else {}


def _final_label(row: Mapping[str, Any], method: str) -> str | None:
    if method == "llm_only":
        record = row.get("decision_record") or {}
        value = record.get("final_label") if isinstance(record, Mapping) else None
    else:
        record = row.get("structured_record") or {}
        selection = record.get("selection") if isinstance(record, Mapping) else None
        value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _model_boundary_label(row: Mapping[str, Any], method: str) -> str | None:
    record = ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
    if not isinstance(record, Mapping):
        return None
    value = record.get("final_label")
    if method == "llm_with_rules":
        selection = record.get("selection")
        value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _purist_correct(label: str | None, gold_monthly: float) -> bool:
    if not label:
        return False
    try:
        predicted = float(label_to_frequency_record(label).monthly_frequency)
    except (TypeError, ValueError):
        return False
    return (
        convert_to_categories([predicted], method="purist")[0]
        == convert_to_categories([gold_monthly], method="purist")[0]
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def comparable_analysis(analysis: Mapping[str, Any]) -> dict[str, Any]:
    """Remove only volatile generation metadata for retained-output checks."""

    return {key: value for key, value in analysis.items() if key != "generated_at_utc"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/gan2026/six_model_validation_comparison_20260718.json"),
    )
    parser.add_argument("--retained-artifact-root", type=Path)
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("experiments/gan2026_six_model_post_panel_attribution_20260720.json"),
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path(
            "docs/experiments/gan2026/gan2026_six_model_post_panel_attribution_2026-07-20.md"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild in memory and compare with the retained JSON without writing files.",
    )
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    config = args.config if args.config.is_absolute() else root / args.config
    output = args.json if args.json.is_absolute() else root / args.json
    report = args.markdown if args.markdown.is_absolute() else root / args.markdown
    analysis = build_analysis(
        root,
        config,
        retained_artifact_root=args.retained_artifact_root,
    )
    if args.check:
        if not output.is_file():
            raise SystemExit(f"retained analysis is missing: {output}")
        expected = json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(expected, Mapping):
            raise SystemExit(f"retained analysis must be an object: {output}")
        if comparable_analysis(analysis) != comparable_analysis(expected):
            raise SystemExit(f"retained analysis drift: {output}")
        print(f"Gan post-panel analysis valid: {output.relative_to(root)}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(analysis, report)
    print(
        json.dumps(
            {
                "conditions": len(analysis["conditions"]),
                "rows": len(analysis["rows"]),
                "json": str(output),
                "markdown": str(report),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
