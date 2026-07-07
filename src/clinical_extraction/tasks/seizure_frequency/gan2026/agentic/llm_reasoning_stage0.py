"""Stage 0 manifests and V0 comparators for Gan 2026 LLM-reasoning work.

The test-0.85 plan starts with validation-only family hard slices and pure
structured-event V0 comparators. This module is a no-call artifact builder: it
uses saved validation structured-event outputs, validation records, and the
locked split order. It does not read or score test rows.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_DATE = "2026-06-13"
DEFAULT_SPLIT = "validation"
DEFAULT_SPLIT_MANIFEST = "gan2026_split_v1"
DEFAULT_OUTPUT_JSON = Path(
    "experiments/gan2026_llm_reasoning_stage0_v0_comparators_2026-06-13.json"
)
DEFAULT_OUTPUT_MARKDOWN = Path(
    "experiments/gan2026_llm_reasoning_stage0_v0_comparators_2026-06-13.md"
)
DEFAULT_FIXED_HARD50_MANIFEST = Path(
    "experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json"
)
DEFAULT_V0_ARTIFACTS: dict[str, Path] = {
    "gpt41mini_hybrid_structured_events_v0_5": Path(
        "experiments/"
        "gan2026_three_way_comparison_validation750_hybrid_structured_events_"
        "gpt41mini_2026-06-07.jsonl"
    ),
    "qwen3635b_hybrid_structured_events_v0_6": Path(
        "experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl"
    ),
    "deepseek_hybrid_structured_events_v0_6": Path(
        "experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl"
    ),
}

FAMILY_SLICE_NAMES = (
    "unknown_no_reference_validation50",
    "seizure_free_last_event_validation50",
    "frequency_denominator_validation50",
    "cluster_axis_validation50",
    "multi_semiology_burden_validation50",
)

_BOUNDARY_KINDS = {"unknown", "no_reference"}
_FREQUENCY_KINDS = {"frequency", "unresolved_multiple"}
_SEIZURE_FREE_TEXT = re.compile(
    r"\b(seizure[- ]free|no seizures since|last seizure|free since|well controlled since)\b",
    re.IGNORECASE,
)
_DENOMINATOR_TEXT = re.compile(
    r"\b(per day|per week|per month|per year|daily|weekly|monthly|yearly|"
    r"times a|several|multiple|every \d+|once|twice|thrice)\b",
    re.IGNORECASE,
)
_RANGE_TEXT = re.compile(r"\b\d+\s*(?:-|to)\s*\d+\b", re.IGNORECASE)
_CLUSTER_TEXT = re.compile(r"\bcluster(?:s|ed|ing)?\b", re.IGNORECASE)
_SEMIOLOGY_TERMS = (
    "focal",
    "tonic-clonic",
    "tonic clonic",
    "generalised",
    "generalized",
    "absence",
    "myoclonic",
    "atonic",
    "aura",
    "convulsive",
    "convulsion",
    "impaired awareness",
    "behavioural arrest",
    "behavioral arrest",
    "jerk",
    "drop attack",
)


def run_stage0(
    *,
    validation_records: Sequence[GanFrequencyRecord],
    v0_artifact_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    source_artifacts: Mapping[str, Path | str],
    fixed_hard50_manifest: Mapping[str, Any],
    date: str = DEFAULT_DATE,
    split: str = DEFAULT_SPLIT,
    split_manifest: str = DEFAULT_SPLIT_MANIFEST,
) -> dict[str, Any]:
    """Build family manifests and V0 saved-artifact scores."""

    family_manifests = build_family_slice_manifests(
        validation_records=validation_records,
        v0_artifact_rows=v0_artifact_rows,
        source_artifacts=source_artifacts,
        date=date,
        split=split,
        split_manifest=split_manifest,
    )
    surfaces = build_stage0_surfaces(
        validation_records=validation_records,
        fixed_hard50_manifest=fixed_hard50_manifest,
        family_manifests=family_manifests,
    )
    return {
        "artifact_kind": "gan2026_llm_reasoning_stage0_v0_comparator_report",
        "date": date,
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "split": split,
        "split_manifest": split_manifest,
        "mode": "no_call_saved_validation_artifact_replay",
        "claim_boundary": (
            "Stage 0 validation-development artifact only. It builds validation hard "
            "slice manifests and scores saved pure structured-event V0 artifacts. "
            "No test rows are inspected or used."
        ),
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "family_manifests": family_manifests,
        "surfaces": surfaces,
        "v0_scores": score_v0_artifacts(v0_artifact_rows, surfaces),
    }


def build_family_slice_manifests(
    *,
    validation_records: Sequence[GanFrequencyRecord],
    v0_artifact_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    source_artifacts: Mapping[str, Path | str],
    date: str = DEFAULT_DATE,
    split: str = DEFAULT_SPLIT,
    split_manifest: str = DEFAULT_SPLIT_MANIFEST,
    max_rows: int = 50,
) -> dict[str, dict[str, Any]]:
    """Create validation-only family-slice manifests for the plan's Stage 0 gate."""

    rows_by_artifact = {
        artifact_id: _rows_by_source_index(rows) for artifact_id, rows in v0_artifact_rows.items()
    }
    validation_order = {
        int(record.source_row_index): index for index, record in enumerate(validation_records)
    }
    manifests: dict[str, dict[str, Any]] = {}
    for slice_name in FAMILY_SLICE_NAMES:
        candidates: list[tuple[tuple[int, int, int, int], dict[str, Any]]] = []
        for record in validation_records:
            source_row_index = int(record.source_row_index)
            artifact_rows = {
                artifact_id: row_by_index.get(source_row_index)
                for artifact_id, row_by_index in rows_by_artifact.items()
            }
            reasons = _trigger_reasons(slice_name, record, artifact_rows)
            if not reasons:
                continue
            score = _slice_hardness_score(
                record,
                artifact_rows,
                reasons,
                validation_order=validation_order[source_row_index],
            )
            candidates.append((score, _slice_record(record, artifact_rows, reasons)))

        selected = [
            row for _, row in sorted(candidates, key=lambda item: item[0], reverse=True)[:max_rows]
        ]
        for rank, row in enumerate(selected, start=1):
            row["selection_rank"] = rank

        manifests[slice_name] = {
            "artifact_kind": "gan2026_llm_reasoning_family_hard_slice_manifest",
            "date": date,
            "slice_name": slice_name,
            "split": split,
            "split_manifest": split_manifest,
            "source_policy": (
                "Validation-only family hard slice. Membership is selected from "
                "validation gold labels, validation note text triggers, and saved "
                "pure structured-event validation artifacts before any new agent run."
            ),
            "inspection_policy": (
                "Validation row-level review is allowed. Do not use locked test row-level "
                "failures, labels, or text to tune prompts, tools, thresholds, or repair."
            ),
            "trigger_rule": _trigger_rule_description(slice_name),
            "selection_policy": (
                "Select up to 50 triggered validation rows, prioritizing rows missed by at "
                "least one V0 artifact, cross-model V0 final-kind disagreement, and more "
                "specific trigger evidence; validation split order breaks ties."
            ),
            "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
            "row_count": len(selected),
            "source_row_indices": [row["source_row_index"] for row in selected],
            "records": selected,
        }
    return manifests


def build_stage0_surfaces(
    *,
    validation_records: Sequence[GanFrequencyRecord],
    fixed_hard50_manifest: Mapping[str, Any],
    family_manifests: Mapping[str, Mapping[str, Any]],
) -> dict[str, list[int]]:
    """Return ordered source-row surfaces used for V0 comparator reporting."""

    validation_indices = [int(record.source_row_index) for record in validation_records]
    surfaces: dict[str, list[int]] = {
        "validation25_prefix": validation_indices[:25],
        "fixed_agentic_hard50": _manifest_source_indices(fixed_hard50_manifest),
    }
    for slice_name in FAMILY_SLICE_NAMES:
        manifest = family_manifests[slice_name]
        surfaces[slice_name] = [int(value) for value in manifest["source_row_indices"]]
    surfaces["validation250_prefix"] = validation_indices[:250]
    return surfaces


def score_v0_artifacts(
    v0_artifact_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    surfaces: Mapping[str, Sequence[int]],
) -> dict[str, dict[str, Any]]:
    """Score each saved pure structured-event artifact on each Stage 0 surface."""

    rows_by_artifact = {
        artifact_id: _rows_by_source_index(rows) for artifact_id, rows in v0_artifact_rows.items()
    }
    scored: dict[str, dict[str, Any]] = {}
    for surface_name, source_indices in surfaces.items():
        scored[surface_name] = {}
        for artifact_id, rows_by_index in rows_by_artifact.items():
            rows = [rows_by_index.get(int(source_index)) for source_index in source_indices]
            scored[surface_name][artifact_id] = summarize_saved_structured_rows(rows)
    return scored


def summarize_saved_structured_rows(
    rows: Sequence[Mapping[str, Any] | None],
) -> dict[str, Any]:
    """Summarize saved structured-event rows, counting missing rows as incorrect."""

    row_count = len(rows)
    loaded_rows = [row for row in rows if row is not None]
    purist_correct = sum(_comparison_bool(row, "purist_correct") for row in loaded_rows)
    pragmatic_correct = sum(_comparison_bool(row, "pragmatic_correct") for row in loaded_rows)
    evidence_valid = sum(bool(row.get("evidence_valid")) for row in loaded_rows)
    structured_records = sum(bool(row.get("structured_record")) for row in loaded_rows)
    call_failures = sum(bool(row.get("call_error")) for row in loaded_rows)
    parse_error_rows = sum(bool(row.get("parse_errors")) for row in loaded_rows)
    rendered_rows = sum(_has_final_label(row) for row in loaded_rows)
    missing_rows = row_count - len(loaded_rows)
    return {
        "rows": row_count,
        "loaded_rows": len(loaded_rows),
        "missing_rows": missing_rows,
        "structured_records": structured_records,
        "rendered_rows": rendered_rows,
        "call_failures": call_failures,
        "parse_error_rows": parse_error_rows,
        "evidence_valid": evidence_valid,
        "evidence_valid_rate": round(evidence_valid / row_count, 4) if row_count else 0.0,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / row_count, 4) if row_count else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / row_count, 4) if row_count else 0.0,
        "final_kind_counts": dict(
            sorted(Counter(_final_kind(row) or "missing_final_kind" for row in loaded_rows).items())
        ),
    }


def write_stage0_outputs(
    stage0: Mapping[str, Any],
    *,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_markdown: Path = DEFAULT_OUTPUT_MARKDOWN,
    write_slice_files: bool = True,
) -> None:
    """Write the combined Stage 0 artifact, per-slice manifests, and report."""

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(stage0, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if write_slice_files:
        for slice_name, manifest in stage0["family_manifests"].items():
            manifest_path = output_json.parent / (
                f"gan2026_llm_reasoning_{slice_name}_manifest_{stage0['date']}.json"
            )
            txt_path = manifest_path.with_suffix(".txt")
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            txt_path.write_text(
                "\n".join(str(index) for index in manifest["source_row_indices"]) + "\n",
                encoding="utf-8",
            )
    write_stage0_report(stage0, output_markdown, json_path=output_json)


def write_stage0_report(
    stage0: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    """Write a concise markdown report for human scan and runbook use."""

    lines = [
        "# Gan 2026 LLM-Reasoning Stage 0 V0 Comparators",
        "",
        f"Date: {stage0['date']}",
        "",
        "This is a validation-development no-call artifact. It builds family hard-slice "
        "manifests and scores saved pure structured-event V0 artifacts before any new "
        "agentic reasoning runs. It does not inspect locked `test450` row-level data.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: Stage 0 data/scoring parity and reporting.",
        "- Hypothesis: saved pure structured-event artifacts can define reproducible "
        "validation hard slices and V0 baselines before V1/V2 agent calls.",
        "- Data surface: validation split only, `gan2026_split_v1`.",
        "- Scorer: saved Gan-compatible Purist and Pragmatic comparisons from each "
        "structured-event artifact.",
        "- Stop rule: do not run agents until the V0 rows, slices, and source-index "
        "files are reproducible.",
        "",
        "## Generated Slice Manifests",
        "",
        "| Slice | Rows | Primary trigger |",
        "| --- | ---: | --- |",
    ]
    for slice_name in FAMILY_SLICE_NAMES:
        manifest = stage0["family_manifests"][slice_name]
        lines.append(f"| `{slice_name}` | {manifest['row_count']} | {manifest['trigger_rule']} |")

    lines.extend(
        [
            "",
            "## V0 Comparator Scores",
            "",
            "| Surface | Artifact | Purist | Pragmatic | Evidence exact | Missing |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for surface_name, artifact_scores in stage0["v0_scores"].items():
        for artifact_id, score in artifact_scores.items():
            lines.append(
                f"| `{surface_name}` | `{artifact_id}` | "
                f"{score['purist_correct']}/{score['rows']} "
                f"({score['purist_accuracy']:.4f}) | "
                f"{score['pragmatic_correct']}/{score['rows']} "
                f"({score['pragmatic_accuracy']:.4f}) | "
                f"{score['evidence_valid']}/{score['rows']} | "
                f"{score['missing_rows']} |"
            )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Combined JSON: `{json_path}`",
            "- Runner-facing source-row files: "
            "`experiments/gan2026_llm_reasoning_*_validation50_manifest_"
            f"{stage0['date']}.txt`",
            "",
            "## Interpretation",
            "",
            "This artifact creates the Stage 0 substrate for the test-0.85 plan. "
            "The next implementation step is a V1/V2 reasoner runner that consumes "
            "these source-row files and reports changed-label precision against the "
            "best V0 pure structured-event comparator on each slice.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_default_stage0_inputs() -> tuple[
    list[GanFrequencyRecord],
    dict[str, list[dict[str, Any]]],
    dict[str, Path],
    dict[str, Any],
    str,
]:
    """Load default validation rows, V0 artifacts, fixed hard50, and manifest version."""

    validation_records = load_records_for_split(DEFAULT_SPLIT)
    v0_rows = {
        artifact_id: load_jsonl_rows(path) for artifact_id, path in DEFAULT_V0_ARTIFACTS.items()
    }
    split_manifest = load_split_manifest()
    split_manifest_version = str(split_manifest.get("manifest_version", DEFAULT_SPLIT_MANIFEST))
    fixed_hard50_manifest = json.loads(DEFAULT_FIXED_HARD50_MANIFEST.read_text(encoding="utf-8"))
    return (
        validation_records,
        v0_rows,
        dict(DEFAULT_V0_ARTIFACTS),
        fixed_hard50_manifest,
        split_manifest_version,
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build Gan 2026 LLM-reasoning Stage 0 hard slices and V0 scores."
    )
    parser.add_argument("--json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument(
        "--no-slice-files",
        action="store_true",
        help="Write only the combined JSON and markdown report.",
    )
    args = parser.parse_args(argv)

    (
        validation_records,
        v0_rows,
        source_artifacts,
        fixed_hard50_manifest,
        split_manifest_version,
    ) = load_default_stage0_inputs()
    stage0 = run_stage0(
        validation_records=validation_records,
        v0_artifact_rows=v0_rows,
        source_artifacts=source_artifacts,
        fixed_hard50_manifest=fixed_hard50_manifest,
        date=args.date,
        split_manifest=split_manifest_version,
    )
    write_stage0_outputs(
        stage0,
        output_json=args.json,
        output_markdown=args.markdown,
        write_slice_files=not args.no_slice_files,
    )
    print(json.dumps(_console_summary(stage0), sort_keys=True))


def _trigger_reasons(
    slice_name: str,
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    if slice_name == "unknown_no_reference_validation50":
        return _unknown_no_reference_reasons(record, artifact_rows)
    if slice_name == "seizure_free_last_event_validation50":
        return _seizure_free_last_event_reasons(record, artifact_rows)
    if slice_name == "frequency_denominator_validation50":
        return _frequency_denominator_reasons(record, artifact_rows)
    if slice_name == "cluster_axis_validation50":
        return _cluster_axis_reasons(record, artifact_rows)
    if slice_name == "multi_semiology_burden_validation50":
        return _multi_semiology_reasons(record, artifact_rows)
    raise ValueError(f"Unknown slice name: {slice_name}")


def _unknown_no_reference_reasons(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    reasons: list[str] = []
    gold_kind = str(record.gold_label_kind)
    if gold_kind in _BOUNDARY_KINDS:
        reasons.append(f"gold_kind:{gold_kind}")
    selected_kinds = _selected_kinds(artifact_rows)
    if any(kind in _BOUNDARY_KINDS for kind in selected_kinds.values()):
        reasons.append("v0_boundary_selection")
    if len({kind for kind in selected_kinds.values() if kind in _BOUNDARY_KINDS}) > 1:
        reasons.append("v0_unknown_no_reference_disagreement")
    if gold_kind in _BOUNDARY_KINDS and any(
        kind and kind != gold_kind for kind in selected_kinds.values()
    ):
        reasons.append("v0_disagrees_with_boundary_gold_kind")
    return sorted(set(reasons))


def _seizure_free_last_event_reasons(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    reasons: list[str] = []
    if str(record.gold_label_kind) == "seizure_free":
        reasons.append("gold_kind:seizure_free")
    if _SEIZURE_FREE_TEXT.search(record.note_text):
        reasons.append("note_seizure_free_or_last_event_text")
    for artifact_id, row in artifact_rows.items():
        final_kind = _final_kind(row)
        if final_kind == "seizure_free":
            reasons.append(f"{artifact_id}:v0_selected_seizure_free")
        event_kinds = set(_event_field_values(row, "kind"))
        if {"seizure_free", "last_event_only"} & event_kinds:
            reasons.append(f"{artifact_id}:v0_event_seizure_free_or_last_event")
    return sorted(set(reasons))


def _frequency_denominator_reasons(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    reasons: list[str] = []
    has_frequency_anchor = False
    label_text = record.gold_label.lower()
    if str(record.gold_label_kind) in _FREQUENCY_KINDS:
        has_frequency_anchor = True
        reasons.append("gold_frequency_or_unresolved_multiple")
    if " per " in label_text or "multiple" in label_text or " to " in label_text:
        reasons.append("gold_denominator_or_range_label")
    if _DENOMINATOR_TEXT.search(record.note_text) or _RANGE_TEXT.search(record.note_text):
        reasons.append("note_denominator_or_range_text")
    for artifact_id, row in artifact_rows.items():
        if _final_kind(row) in _FREQUENCY_KINDS:
            has_frequency_anchor = True
        final_label = (_final_label(row) or "").lower()
        if " per " in final_label or "multiple" in final_label or " to " in final_label:
            reasons.append(f"{artifact_id}:v0_frequency_label")
        if "frequency_rate" in set(_event_field_values(row, "kind")):
            has_frequency_anchor = True
            reasons.append(f"{artifact_id}:v0_frequency_event")
    return sorted(set(reasons)) if has_frequency_anchor else []


def _cluster_axis_reasons(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    reasons: list[str] = []
    if _CLUSTER_TEXT.search(record.gold_label):
        reasons.append("gold_cluster_label")
    if _CLUSTER_TEXT.search(record.note_text):
        reasons.append("note_cluster_text")
    for artifact_id, row in artifact_rows.items():
        if _CLUSTER_TEXT.search(_final_label(row) or ""):
            reasons.append(f"{artifact_id}:v0_cluster_label")
        event_text = " ".join(_event_field_values(row, "kind", "raw_value", "evidence"))
        if _CLUSTER_TEXT.search(event_text):
            reasons.append(f"{artifact_id}:v0_cluster_event")
    return sorted(set(reasons))


def _multi_semiology_reasons(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[str]:
    reasons: list[str] = []
    if _semiology_term_count(record.note_text) >= 2:
        reasons.append("note_multiple_semiology_terms")
    if re.search(r"\b(overall|total|combined)\b", record.note_text, flags=re.IGNORECASE):
        reasons.append("note_overall_or_total_burden_text")
    for artifact_id, row in artifact_rows.items():
        applies_to = {
            value.lower()
            for value in _event_field_values(row, "applies_to")
            if value and value.lower() not in {"none", "null", "seizures", "seizure"}
        }
        if len(applies_to) >= 2:
            reasons.append(f"{artifact_id}:v0_multiple_applies_to")
        event_text = " ".join(
            _event_field_values(row, "applies_to", "evidence", "raw_value", "notes")
        )
        if _semiology_term_count(event_text) >= 2:
            reasons.append(f"{artifact_id}:v0_multiple_event_semiology_terms")
    return sorted(set(reasons))


def _slice_hardness_score(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
    reasons: Sequence[str],
    *,
    validation_order: int,
) -> tuple[int, int, int, int]:
    missed_by_any_v0 = int(
        any(not _comparison_bool(row, "purist_correct") for row in artifact_rows.values())
    )
    wrong_count = sum(not _comparison_bool(row, "purist_correct") for row in artifact_rows.values())
    final_kind_count = len(set(_selected_kinds(artifact_rows).values()))
    reason_count = len(reasons)
    del record
    return (
        missed_by_any_v0,
        wrong_count + final_kind_count,
        reason_count,
        -validation_order,
    )


def _slice_record(
    record: GanFrequencyRecord,
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
    reasons: Sequence[str],
) -> dict[str, Any]:
    return {
        "source_row_index": int(record.source_row_index),
        "gold_label": record.gold_label,
        "gold_label_kind": str(record.gold_label_kind),
        "trigger_reasons": list(reasons),
        "v0_purist_miss_artifacts": [
            artifact_id
            for artifact_id, row in artifact_rows.items()
            if not _comparison_bool(row, "purist_correct")
        ],
        "v0_selected_kinds": _selected_kinds(artifact_rows),
        "v0_final_labels": {
            artifact_id: _final_label(row) for artifact_id, row in artifact_rows.items()
        },
    }


def _trigger_rule_description(slice_name: str) -> str:
    descriptions = {
        "unknown_no_reference_validation50": (
            "Boundary-state rows where validation gold or V0 selection involves unknown "
            "or no-reference, prioritizing V0 boundary disagreements."
        ),
        "seizure_free_last_event_validation50": (
            "Rows with seizure-free or last-event-only gold, note text, or V0 events."
        ),
        "frequency_denominator_validation50": (
            "Rows with frequency denominators, ranges, vague multiple terms, or "
            "frequency_rate events."
        ),
        "cluster_axis_validation50": (
            "Rows where gold labels, note text, V0 final labels, or V0 events mention clusters."
        ),
        "multi_semiology_burden_validation50": (
            "Rows with multiple semiology terms or V0 events applying to multiple seizure types."
        ),
    }
    return descriptions[slice_name]


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row for row in rows if row.get("source_row_index") is not None
    }


def _manifest_source_indices(manifest: Mapping[str, Any]) -> list[int]:
    values = manifest.get("source_row_indices") or []
    return [int(value) for value in values]


def _selected_kinds(
    artifact_rows: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, str | None]:
    return {artifact_id: _final_kind(row) for artifact_id, row in artifact_rows.items()}


def _final_kind(row: Mapping[str, Any] | None) -> str | None:
    selection = _selection(row)
    value = selection.get("final_kind")
    return str(value) if value is not None else None


def _final_label(row: Mapping[str, Any] | None) -> str | None:
    if row is None:
        return None
    patched_label = row.get("patched_final_label")
    if patched_label is not None:
        return str(patched_label)
    selection = _selection(row)
    value = selection.get("final_label")
    return str(value) if value is not None else None


def _selection(row: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if row is None:
        return {}
    structured_record = row.get("structured_record") or {}
    if not isinstance(structured_record, Mapping):
        return {}
    selection = structured_record.get("selection") or {}
    return selection if isinstance(selection, Mapping) else {}


def _events(row: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if row is None:
        return []
    structured_record = row.get("structured_record") or {}
    if not isinstance(structured_record, Mapping):
        return []
    events = structured_record.get("events") or []
    return [event for event in events if isinstance(event, Mapping)]


def _event_field_values(row: Mapping[str, Any] | None, *field_names: str) -> list[str]:
    values: list[str] = []
    for event in _events(row):
        for field_name in field_names:
            value = event.get(field_name)
            if value is not None:
                values.append(str(value))
    return values


def _comparison_bool(row: Mapping[str, Any] | None, key: str) -> bool:
    if row is None:
        return False
    comparison = row.get("comparison") or {}
    return bool(isinstance(comparison, Mapping) and comparison.get(key) is True)


def _has_final_label(row: Mapping[str, Any] | None) -> bool:
    return _final_label(row) is not None


def _semiology_term_count(text: str) -> int:
    lowered = text.lower()
    return sum(1 for term in _SEMIOLOGY_TERMS if term in lowered)


def _console_summary(stage0: Mapping[str, Any]) -> dict[str, Any]:
    slice_counts = {
        slice_name: manifest["row_count"]
        for slice_name, manifest in stage0["family_manifests"].items()
    }
    best_by_surface = {}
    for surface_name, artifact_scores in stage0["v0_scores"].items():
        best_artifact, best_score = max(
            artifact_scores.items(),
            key=lambda item: (item[1]["purist_correct"], item[1]["pragmatic_correct"]),
        )
        best_by_surface[surface_name] = {
            "artifact": best_artifact,
            "purist_correct": best_score["purist_correct"],
            "rows": best_score["rows"],
            "purist_accuracy": best_score["purist_accuracy"],
        }
    return {"slice_counts": slice_counts, "best_v0_by_surface": best_by_surface}


if __name__ == "__main__":
    main()
