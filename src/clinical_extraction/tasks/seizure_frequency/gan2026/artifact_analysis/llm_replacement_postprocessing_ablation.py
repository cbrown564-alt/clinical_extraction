"""Saved-output replacement ablations for deterministic LLM post-processing layers."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    write_run_registry,
    write_run_registry_markdown,
)

DEFAULT_SOURCE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_"
    "2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_llm_replacement_postprocessing_ablation_validation250_v0_"
    "2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_llm_replacement_postprocessing_ablation_validation250_v0_"
    "2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_llm_replacement_postprocessing_ablation_validation250_v0_"
    "2026-06-02.md"
)
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
DEFAULT_RUN_INDEX_PATH = Path("experiments/RUN_INDEX.md")


@dataclass(frozen=True)
class ReplacementCondition:
    condition: str
    score_layer: str
    prediction_owner: str
    repair_mode: str
    replacement_target: str
    transition_reason: str
    node_source: str = "not_applicable"
    projection_owner: str = "not_applicable"


CONDITIONS: tuple[ReplacementCondition, ...] = (
    ReplacementCondition(
        condition="raw_model_selected_label",
        score_layer="raw_llm",
        prediction_owner="llm",
        repair_mode="raw_llm",
        replacement_target="strict_format",
        transition_reason="none",
    ),
    ReplacementCondition(
        condition="format_only_repair",
        score_layer="format_only",
        prediction_owner="llm",
        repair_mode="format_only",
        replacement_target="strict_format",
        transition_reason="format_preserving_label_repair",
    ),
    ReplacementCondition(
        condition="selected_evidence_arithmetic_only",
        score_layer="selected_evidence_arithmetic",
        prediction_owner="llm_selected_evidence_then_deterministic_arithmetic",
        repair_mode="selected_evidence_arithmetic",
        replacement_target="selected_evidence_arithmetic",
        transition_reason="deterministic_arithmetic_over_model_selected_evidence",
    ),
    ReplacementCondition(
        condition="benchmark_aligned_adapter",
        score_layer="benchmark_aligned",
        prediction_owner="llm_with_named_benchmark_adapter",
        repair_mode="benchmark_aligned",
        replacement_target="benchmark_aligned",
        transition_reason="benchmark_alignment_adapter",
    ),
    ReplacementCondition(
        condition="full_stack",
        score_layer="benchmark_aligned",
        prediction_owner="mixed_llm_plus_deterministic_postprocessing",
        repair_mode="full_stack",
        replacement_target="deterministic_fallback",
        transition_reason="existing_best_saved_stack",
    ),
)


def build_replacement_ablation(
    saved_rows: Sequence[Mapping[str, Any]],
    *,
    source_jsonl: str | None,
    split: str,
    split_manifest: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build condition-level rows and summary metadata from saved LLM-heavy artifacts."""

    raw_rows = [
        _condition_row(row, CONDITIONS[0], comparator=None)
        for row in saved_rows
        if _has_score_layer(row, CONDITIONS[0].score_layer)
    ]
    raw_by_index = {int(row["source_row_index"]): row for row in raw_rows}
    condition_rows: list[dict[str, Any]] = list(raw_rows)
    for condition in CONDITIONS[1:]:
        for row in saved_rows:
            if not _has_score_layer(row, condition.score_layer):
                continue
            source_row_index = int(row["source_row_index"])
            condition_rows.append(
                _condition_row(
                    row,
                    condition,
                    comparator=raw_by_index.get(source_row_index),
                )
            )

    metadata = {
        "artifact_kind": "llm_replacement_postprocessing_ablation",
        "date": "2026-06-02",
        "source_jsonl": source_jsonl,
        "pipeline_family": "llm_replacement_postprocessing_ablation",
        "source_pipeline_family": _first_text(saved_rows, "pipeline_family"),
        "split": split,
        "split_manifest": split_manifest,
        "claim_language": (
            "Diagnostic saved-output replay only. No hosted calls, prompt changes, "
            "scorer changes, production projection policy changes, or holdout behavior "
            "changes are made."
        ),
        "replacement_targets": sorted({condition.replacement_target for condition in CONDITIONS}),
        "conditions": [
            _condition_summary(condition, condition_rows)
            for condition in CONDITIONS
            if any(row["condition"] == condition.condition for row in condition_rows)
        ],
        "summary": _overall_summary(saved_rows, condition_rows),
    }
    return condition_rows, metadata


def write_replacement_ablation_outputs(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    jsonl_path: Path,
    json_path: Path,
    markdown_path: Path,
) -> None:
    write_jsonl_rows(rows, jsonl_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_replacement_ablation_report(
        rows,
        metadata,
        markdown_path,
        jsonl_path=jsonl_path,
        json_path=json_path,
    )


def write_replacement_ablation_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 LLM-Replacement Post-Processing Ablation",
        "",
        "Diagnostic saved-output replay only: no hosted calls, prompt changes, scorer "
        "changes, projection-policy promotion, or holdout behavior changes.",
        "",
        f"- Source JSONL: `{metadata.get('source_jsonl')}`",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['summary']['row_count']}",
        f"- Condition rows: {len(rows)}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Condition Summary",
        "",
        "| Condition | Target | Rows | Scorable | Purist | Pragmatic | Changed | "
        "Raw wrong -> correct | Raw correct -> wrong | Evidence exact | Trace mismatches |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in metadata["conditions"]:
        score = condition["score"]
        repair = condition["repair_attribution"]
        evidence = condition["evidence_validity"]
        lines.append(
            f"| `{condition['condition']}` | `{condition['replacement_target']}` | "
            f"{score['rows']} | {score['scorable_rows']} | "
            f"{score['purist_correct']} ({score['purist_accuracy']:.4f}) | "
            f"{score['pragmatic_correct']} ({score['pragmatic_accuracy']:.4f}) | "
            f"{repair['changed_from_raw']} | "
            f"{repair['raw_wrong_to_condition_correct']} | "
            f"{repair['raw_correct_to_condition_wrong']} | "
            f"{evidence['selected_evidence_valid_rows']} | "
            f"{evidence['selected_event_trace_mismatches']} |"
        )
    lines.extend(
        [
            "",
            "## Replay Variance",
            "",
            f"- Reused raw-output rows: "
            f"{metadata['summary']['replay_variance']['reused_raw_output_rows']}",
            f"- Non-reused raw-output rows: "
            f"{metadata['summary']['replay_variance']['non_reused_raw_output_rows']}",
            f"- Provider-call-change rows: "
            f"{metadata['summary']['replay_variance']['provider_call_change_rows']}",
            "",
            "## Hard-Slice Breakdown",
            "",
            "| Slice | Rows | Parse/schema failures | Trace mismatches |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for slice_name, stats in sorted(metadata["summary"]["hard_slice_breakdown"].items()):
        lines.append(
            f"| `{slice_name}` | {stats['rows']} | {stats['parse_or_schema_failures']} | "
            f"{stats['selected_event_trace_mismatches']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def registry_entry_for_replacement_ablation(
    metadata: Mapping[str, Any],
    *,
    artifact_paths: Sequence[str],
) -> RunRegistryEntry:
    condition_metrics = {
        f"{condition['condition']}_purist_correct": condition["score"]["purist_correct"]
        for condition in metadata["conditions"]
    }
    summary = metadata["summary"]
    return RunRegistryEntry(
        run_id=(
            "gan2026_llm_replacement_postprocessing_ablation_"
            f"{metadata['split']}{summary['row_count']}_2026-06-02"
        ),
        artifact_paths=tuple(artifact_paths),
        date="2026-06-02",
        pipeline_family="llm_replacement_postprocessing_ablation",
        split=str(metadata["split"]),
        row_count=int(summary["row_count"]),
        model="none; saved outputs only",
        model_role="analysis-only deterministic post-processing replacement replay",
        mode="saved-output no-call post-processing replacement ablation",
        replay_status="saved_output_replay",
        decision="revise",
        primary_metrics={
            "row_count": int(summary["row_count"]),
            "condition_rows": int(summary["condition_row_count"]),
            "reused_raw_output_rows": int(
                summary["replay_variance"]["reused_raw_output_rows"]
            ),
            **condition_metrics,
        },
        repair_mode="raw_llm + format_only + selected_evidence_arithmetic + benchmark_aligned",
        cache_reuse_source=_optional_str(metadata.get("source_jsonl")),
        evidence_validity=(
            "Reports selected-evidence exactness, event/node evidence validity, "
            "and selected-event trace mismatches for each replacement condition."
        ),
        supersedes=("gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02",),
        claim_language_notes=str(metadata["claim_language"]),
    )


def append_registry_entry(
    entry: RunRegistryEntry,
    *,
    registry_path: Path,
    run_index_path: Path | None = None,
) -> None:
    entries = [
        existing
        for existing in load_run_registry(registry_path)
        if existing.run_id != entry.run_id
    ]
    entries.append(entry)
    write_run_registry(entries, registry_path)
    if run_index_path is not None:
        write_run_registry_markdown(entries, run_index_path)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Replay saved LLM-heavy score layers as deterministic post-processing "
            "replacement ablations without hosted calls."
        )
    )
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--split-manifest", default="gan2026_split_v1")
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    args = parser.parse_args(argv)

    saved_rows = load_jsonl_rows(args.source_jsonl)
    rows, metadata = build_replacement_ablation(
        saved_rows,
        source_jsonl=str(args.source_jsonl),
        split=args.split,
        split_manifest=args.split_manifest,
    )
    write_replacement_ablation_outputs(
        rows,
        metadata,
        jsonl_path=args.jsonl,
        json_path=args.json,
        markdown_path=args.markdown,
    )
    registry_path = args.registry
    if registry_path is not None:
        entry = registry_entry_for_replacement_ablation(
            metadata,
            artifact_paths=(str(args.jsonl), str(args.json), str(args.markdown)),
        )
        append_registry_entry(
            entry,
            registry_path=registry_path,
            run_index_path=args.run_index,
        )
    print(
        json.dumps(
            {
                "condition_rows": len(rows),
                "json": str(args.json),
                "jsonl": str(args.jsonl),
                "markdown": str(args.markdown),
                "registry": str(registry_path) if registry_path else None,
            },
            sort_keys=True,
        )
    )


def _condition_row(
    saved_row: Mapping[str, Any],
    condition: ReplacementCondition,
    *,
    comparator: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source_row_index = int(saved_row["source_row_index"])
    score_layer = _score_layer(saved_row, condition.score_layer)
    raw_score_layer = _score_layer(saved_row, "raw_llm")
    raw_label = _optional_str(raw_score_layer.get("final_label"))
    final_label = _optional_str(score_layer.get("final_label"))
    evidence_summary = saved_row.get("evidence_summary") or {}
    repair_metadata = _repair_metadata(score_layer, condition)
    component_status = saved_row.get("component_status") or {}
    parse_errors = tuple(str(error) for error in saved_row.get("parse_errors") or ())
    purist_category_transition = _category_transition(
        raw_score_layer,
        score_layer,
        "predicted_purist_category",
    )
    pragmatic_category_transition = _category_transition(
        raw_score_layer,
        score_layer,
        "predicted_pragmatic_category",
    )
    return {
        "source_row_index": source_row_index,
        "split": _optional_str(saved_row.get("split")),
        "condition": condition.condition,
        "prediction_owner": condition.prediction_owner,
        "node_source": condition.node_source,
        "projection_owner": condition.projection_owner,
        "repair_mode": repair_metadata.get("repair_mode", condition.repair_mode),
        "replacement_target": condition.replacement_target,
        "raw_label": raw_label,
        "final_label": final_label,
        "gold_label": (saved_row.get("reference") or {}).get("gold_label"),
        "scorable": bool(score_layer.get("scorable")),
        "purist_correct": bool(score_layer.get("purist_correct")),
        "pragmatic_correct": bool(score_layer.get("pragmatic_correct")),
        "selected_evidence_valid": _optional_bool(
            evidence_summary.get("selected_evidence_valid")
        ),
        "event_or_node_evidence_valid": _event_or_node_evidence_valid(evidence_summary),
        "changed_from_raw": raw_label != final_label,
        "changed_from_comparator": (
            comparator is not None and comparator.get("final_label") != final_label
        ),
        "transition_reason": repair_metadata.get("repair_family", condition.transition_reason),
        "purist_category_transition": purist_category_transition,
        "pragmatic_category_transition": pragmatic_category_transition,
        "semantic_kind_transition": _semantic_kind_transition(
            raw_label,
            final_label,
            saved_row,
        ),
        "reused_raw_output": bool(saved_row.get("reused_raw_output")),
        "selected_event_trace_mismatch": _selected_event_trace_mismatch(
            component_status,
            parse_errors,
        ),
        "parse_or_validation_issues": parse_errors,
        "hard_slice_tags": _hard_slice_tags(saved_row, parse_errors, component_status),
    }


def _condition_summary(
    condition: ReplacementCondition,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    condition_rows = [row for row in rows if row["condition"] == condition.condition]
    raw_rows = [row for row in rows if row["condition"] == "raw_model_selected_label"]
    raw_by_index = {int(row["source_row_index"]): row for row in raw_rows}
    count = len(condition_rows)
    purist = sum(bool(row["purist_correct"]) for row in condition_rows)
    pragmatic = sum(bool(row["pragmatic_correct"]) for row in condition_rows)
    changed = [row for row in condition_rows if row["changed_from_raw"]]
    raw_wrong_to_correct = 0
    raw_correct_to_wrong = 0
    purist_transitions = 0
    pragmatic_transitions = 0
    exact_label_transitions = 0
    for row in condition_rows:
        raw = raw_by_index.get(int(row["source_row_index"]))
        if raw is None:
            continue
        if not raw["purist_correct"] and row["purist_correct"]:
            raw_wrong_to_correct += 1
        if raw["purist_correct"] and not row["purist_correct"]:
            raw_correct_to_wrong += 1
        purist_transitions += bool(row.get("purist_category_transition"))
        pragmatic_transitions += bool(row.get("pragmatic_category_transition"))
        exact_label_transitions += raw.get("final_label") != row.get("final_label")
    evidence_rows = [
        row for row in condition_rows if row.get("selected_evidence_valid") is not None
    ]
    event_evidence_rows = [
        row for row in condition_rows if row.get("event_or_node_evidence_valid") is not None
    ]
    return {
        "condition": condition.condition,
        "score_layer": condition.score_layer,
        "prediction_owner": condition.prediction_owner,
        "replacement_target": condition.replacement_target,
        "score": {
            "rows": count,
            "scorable_rows": sum(bool(row["scorable"]) for row in condition_rows),
            "purist_correct": purist,
            "purist_accuracy": round(purist / count, 4) if count else 0.0,
            "pragmatic_correct": pragmatic,
            "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
        },
        "repair_attribution": {
            "changed_from_raw": len(changed),
            "raw_wrong_to_condition_correct": raw_wrong_to_correct,
            "raw_correct_to_condition_wrong": raw_correct_to_wrong,
            "purist_category_transitions": purist_transitions,
            "pragmatic_category_transitions": pragmatic_transitions,
            "exact_normalized_label_transitions": exact_label_transitions,
            "semantic_kind_transitions": sum(
                bool(row.get("semantic_kind_transition")) for row in condition_rows
            ),
        },
        "evidence_validity": {
            "selected_evidence_valid_rows": sum(
                row["selected_evidence_valid"] is True for row in evidence_rows
            ),
            "selected_evidence_rows": len(evidence_rows),
            "event_or_node_evidence_valid_rows": sum(
                row["event_or_node_evidence_valid"] is True for row in event_evidence_rows
            ),
            "event_or_node_evidence_rows": len(event_evidence_rows),
            "selected_event_trace_mismatches": sum(
                bool(row["selected_event_trace_mismatch"]) for row in condition_rows
            ),
        },
    }


def _overall_summary(
    saved_rows: Sequence[Mapping[str, Any]],
    condition_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    hard_slices: dict[str, Counter[str]] = {}
    for row in saved_rows:
        tags = _hard_slice_tags(
            row,
            tuple(str(error) for error in row.get("parse_errors") or ()),
            row.get("component_status") or {},
        )
        for tag in tags:
            stats = hard_slices.setdefault(tag, Counter())
            stats["rows"] += 1
            stats["parse_or_schema_failures"] += _has_parse_or_schema_failure(row)
            stats["selected_event_trace_mismatches"] += _selected_event_trace_mismatch(
                row.get("component_status") or {},
                tuple(str(error) for error in row.get("parse_errors") or ()),
            )
    return {
        "row_count": len(saved_rows),
        "condition_row_count": len(condition_rows),
        "source_row_indices": [
            int(row["source_row_index"])
            for row in saved_rows
            if isinstance(row.get("source_row_index"), int)
        ],
        "replay_variance": {
            "reused_raw_output_rows": sum(bool(row.get("reused_raw_output")) for row in saved_rows),
            "non_reused_raw_output_rows": sum(
                not bool(row.get("reused_raw_output")) for row in saved_rows
            ),
            "provider_call_change_rows": sum(
                bool(row.get("provider_call_changed")) for row in saved_rows
            ),
            "run_seed_or_cache_key": _first_text(saved_rows, "cache_key") or "not_recorded",
        },
        "hard_slice_breakdown": {
            tag: dict(stats)
            for tag, stats in sorted(hard_slices.items())
        },
    }


def _score_layer(row: Mapping[str, Any], layer: str) -> Mapping[str, Any]:
    score_layers = row.get("score_layers")
    if isinstance(score_layers, Mapping):
        value = score_layers.get(layer)
        if isinstance(value, Mapping):
            return value
    return {}


def _has_score_layer(row: Mapping[str, Any], layer: str) -> bool:
    return bool(_score_layer(row, layer))


def _repair_metadata(
    score_layer: Mapping[str, Any],
    condition: ReplacementCondition,
) -> Mapping[str, Any]:
    metadata = score_layer.get("repair_mode_metadata")
    if isinstance(metadata, Mapping):
        return metadata
    return {
        "repair_mode": condition.repair_mode,
        "repair_family": condition.transition_reason,
    }


def _event_or_node_evidence_valid(evidence_summary: Mapping[str, Any]) -> bool | None:
    for key in ("selected_event_evidence_valid", "selected_node_evidence_valid"):
        value = evidence_summary.get(key)
        if isinstance(value, bool):
            return value
    valid = evidence_summary.get("event_evidence_valid")
    total = evidence_summary.get("event_evidence_total")
    if isinstance(valid, int) and isinstance(total, int) and total > 0:
        return valid == total
    return None


def _selected_event_trace_mismatch(
    component_status: Mapping[str, Any],
    parse_errors: Sequence[str],
) -> bool:
    status = component_status.get("selected_event_trace")
    if isinstance(status, str) and status not in ("ok", "not_applicable"):
        return True
    return any("selected_event_trace" in error for error in parse_errors)


def _hard_slice_tags(
    row: Mapping[str, Any],
    parse_errors: Sequence[str],
    component_status: Mapping[str, Any],
) -> tuple[str, ...]:
    explicit_tags = row.get("hard_slice_tags") or row.get("family_tags") or row.get("tags")
    tags: list[str] = []
    if isinstance(explicit_tags, Sequence) and not isinstance(explicit_tags, str):
        tags.extend(str(tag) for tag in explicit_tags)
    gold_label = str((row.get("reference") or {}).get("gold_label", "")).lower()
    raw_label = str(
        ((row.get("structured_record") or {}).get("final_answer") or {}).get(
            "raw_llm_final_label",
            "",
        )
    ).lower()
    label_text = f"{gold_label} {raw_label}"
    if "cluster" in label_text:
        tags.append("cluster")
    if "diary" in label_text:
        tags.append("diary_aggregation")
    if "seizure free" in label_text:
        tags.append("seizure_free_duration")
    if "unknown" in label_text or "no seizure frequency reference" in label_text:
        tags.append("unknown_no_reference_boundary")
    if any("parse" in error or "schema" in error for error in parse_errors):
        tags.append("schema_parse_failure")
    if _selected_event_trace_mismatch(component_status, parse_errors):
        tags.append("selected_event_trace_mismatch")
    if not tags:
        tags.append("unclassified_validation")
    return tuple(dict.fromkeys(tags))


def _has_parse_or_schema_failure(row: Mapping[str, Any]) -> bool:
    return any(
        "parse" in str(error) or "schema" in str(error)
        for error in row.get("parse_errors") or ()
    )


def _semantic_kind_transition(
    raw_label: str | None,
    final_label: str | None,
    row: Mapping[str, Any],
) -> str | None:
    if raw_label == final_label:
        return None
    raw_kind = _label_kind(raw_label)
    final_answer = (row.get("structured_record") or {}).get("final_answer")
    if raw_kind is None and isinstance(final_answer, Mapping):
        raw_kind = _optional_str(final_answer.get("raw_llm_final_kind"))
    final_kind = _label_kind(final_label)
    if raw_kind is None or final_kind is None or raw_kind == final_kind:
        return None
    return f"{raw_kind}->{final_kind}"


def _label_kind(label: str | None) -> str | None:
    if not label:
        return None
    try:
        return str(label_to_frequency_record(label).kind)
    except ValueError:
        return None


def _category_transition(
    raw_score_layer: Mapping[str, Any],
    score_layer: Mapping[str, Any],
    field: str,
) -> str | None:
    raw = raw_score_layer.get(field)
    current = score_layer.get(field)
    if raw == current:
        return None
    return f"{raw}->{current}"


def _first_text(rows: Sequence[Mapping[str, Any]], key: str) -> str | None:
    for row in rows:
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


if __name__ == "__main__":
    main()
