"""Materialize RQ1/RQ2 single-task control panels and condition matrices."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    hidden_family_atlas,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ATLAS_CSV_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv"
)
DEFAULT_HARD_SLICE_MANIFEST_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json"
)
DEFAULT_FOLLOWUP_PANEL_PATH = Path(
    "experiments/gan2026_component_projection_followup_panel_2026-06-04.jsonl"
)
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.jsonl"
)
DEFAULT_PANEL_JSON_PATH = Path(
    "experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.json"
)
DEFAULT_PANEL_REPORT_PATH = Path(
    "experiments/gan2026_rq1_rq2_single_task_control_panels_2026-06-04.md"
)
DEFAULT_MATRIX_JSONL_PATH = Path(
    "experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl"
)
DEFAULT_MATRIX_JSON_PATH = Path(
    "experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.json"
)
DEFAULT_MATRIX_REPORT_PATH = Path(
    "experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.md"
)

BALANCED_KIND_TARGETS = {
    "frequency": 20,
    "seizure_free": 8,
    "unknown": 8,
    "no_reference": 6,
    "unresolved_multiple": 8,
}
BALANCED_FAMILY_TARGETS = {
    "cluster_burden": 4,
    "diary_or_log_aggregation": 4,
    "current_vs_historical": 8,
    "rate_bucket_or_denominator": 8,
    "competing_semiologies": 6,
    "seizure_free_duration": 6,
    "unknown_boundary": 6,
    "benchmark_format_convention": 4,
}
CONTROL_CONDITIONS: tuple[dict[str, Any], ...] = (
    {
        "condition_id": "candidate_only",
        "prompt_name": "candidate_only",
        "component_task": "candidate_generation",
        "representation_type": "free_text_candidate_list",
        "input_contract": "note_text_and_source_ids_only",
        "overload_condition": False,
    },
    {
        "condition_id": "gold_query_evidence_only",
        "prompt_name": "gold_query_evidence_only",
        "component_task": "evidence_selection",
        "representation_type": "minimal_evidence_tuple",
        "input_contract": "note_text_source_ids_and_gold_frequency_query",
        "overload_condition": False,
    },
    {
        "condition_id": "candidate_conditioned_evidence_only",
        "prompt_name": "candidate_conditioned_evidence_only",
        "component_task": "evidence_selection",
        "representation_type": "candidate_conditioned_evidence_tuple",
        "input_contract": "note_text_source_ids_and_fixed_candidate_state",
        "overload_condition": False,
    },
    {
        "condition_id": "projection_only",
        "prompt_name": "projection_only",
        "component_task": "projection",
        "representation_type": "selected_fact_or_typed_state",
        "input_contract": "fixed_candidate_facts_and_exact_evidence",
        "overload_condition": False,
    },
    {
        "condition_id": "projection_only_instruction_heavy",
        "prompt_name": "projection_only_instruction_heavy",
        "component_task": "projection",
        "representation_type": "selected_fact_or_typed_state_with_policy_principles",
        "input_contract": "fixed_candidate_facts_exact_evidence_and_projection_policy",
        "overload_condition": False,
    },
    {
        "condition_id": "candidate_plus_evidence",
        "prompt_name": "candidate_plus_evidence",
        "component_task": "candidate_generation+evidence_selection",
        "representation_type": "candidate_list_with_evidence_tuple",
        "input_contract": "note_text_source_ids_no_final_label",
        "overload_condition": True,
    },
    {
        "condition_id": "evidence_plus_projection",
        "prompt_name": "evidence_plus_projection",
        "component_task": "evidence_selection+projection",
        "representation_type": "selected_fact_with_final_projection",
        "input_contract": "note_text_source_ids_and_fixed_candidate_state",
        "overload_condition": True,
    },
    {
        "condition_id": "candidate_plus_evidence_plus_projection",
        "prompt_name": "candidate_plus_evidence_plus_projection",
        "component_task": "candidate_generation+evidence_selection+projection",
        "representation_type": "end_to_end_component_bundle",
        "input_contract": "note_text_and_source_ids",
        "overload_condition": True,
    },
)


def build_control_panels(
    *,
    data_path: Path = DEFAULT_DATA_PATH,
    split_manifest_path: Path = DEFAULT_SPLIT_MANIFEST_PATH,
    atlas_csv_path: Path = DEFAULT_ATLAS_CSV_PATH,
    hard_slice_manifest_path: Path = DEFAULT_HARD_SLICE_MANIFEST_PATH,
    followup_panel_path: Path = DEFAULT_FOLLOWUP_PANEL_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = _validation_records(data_path=data_path, split_manifest_path=split_manifest_path)
    balanced = build_balanced_validation_panel(records)
    hard = build_hidden_family_hard_panel(
        hard_slice_manifest_path=hard_slice_manifest_path,
        followup_panel_path=followup_panel_path,
        atlas_csv_path=atlas_csv_path,
    )
    rows = sorted(
        [*balanced, *hard],
        key=lambda row: (str(row["panel_id"]), int(row["source_row_index"])),
    )
    return rows, summarize_panel_rows(rows)


def build_balanced_validation_panel(
    records: Sequence[Mapping[str, Any]],
    *,
    target_size: int = 50,
    kind_targets: Mapping[str, int] = BALANCED_KIND_TARGETS,
    family_targets: Mapping[str, int] = BALANCED_FAMILY_TARGETS,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_indices: set[int] = set()
    kind_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    candidates = sorted((_normalized_record(record) for record in records), key=_balanced_sort_key)

    def add(record: Mapping[str, Any], reason: str) -> None:
        source = int(record["source_row_index"])
        if source in selected_indices or len(selected) >= target_size:
            return
        selected_indices.add(source)
        row = _panel_row(record, panel_id="balanced_validation50", selection_reason=reason)
        selected.append(row)
        kind_counts[str(row["gold_kind"])] += 1
        family_counts.update(row["hidden_families"])

    for kind, target in kind_targets.items():
        for record in candidates:
            if kind_counts[kind] >= target:
                break
            if str(record["gold_kind"]) == kind:
                add(record, f"gold_kind_quota:{kind}")

    made_progress = True
    while len(selected) < target_size and made_progress:
        made_progress = False
        for family, target in family_targets.items():
            if len(selected) >= target_size:
                break
            if family_counts[family] >= target:
                continue
            for record in candidates:
                if family in record["hidden_families"]:
                    before = len(selected)
                    add(record, f"hidden_family_quota:{family}")
                    made_progress = len(selected) > before
                    if made_progress:
                        break

    for record in candidates:
        if len(selected) >= target_size:
            break
        add(record, "deterministic_validation_order_fill")

    return sorted(selected, key=lambda row: int(row["source_row_index"]))


def build_hidden_family_hard_panel(
    *,
    hard_slice_manifest_path: Path = DEFAULT_HARD_SLICE_MANIFEST_PATH,
    followup_panel_path: Path = DEFAULT_FOLLOWUP_PANEL_PATH,
    atlas_csv_path: Path = DEFAULT_ATLAS_CSV_PATH,
    target_size: int = 75,
) -> list[dict[str, Any]]:
    atlas = _load_atlas_by_source(atlas_csv_path)
    rows_by_source: dict[int, dict[str, Any]] = {}

    manifest = _load_json(hard_slice_manifest_path, default={"slices": []})
    for slice_record in manifest.get("slices") or []:
        slice_name = str(slice_record.get("slice_name") or "")
        for member in slice_record.get("members") or []:
            source = int(member["source_row_index"])
            row = rows_by_source.setdefault(source, _hard_panel_seed(member, atlas=atlas))
            _append_unique(row["selection_sources"], "atlas_hard_slice_manifest")
            _append_unique(row["predeclared_slices"], slice_name)

    if followup_panel_path.exists():
        for followup in load_jsonl_rows(followup_panel_path):
            if not _followup_hard_panel_relevant(followup):
                continue
            source = int(followup["source_row_index"])
            row = rows_by_source.setdefault(source, _hard_panel_seed(followup, atlas=atlas))
            _append_unique(row["selection_sources"], "component_projection_followup_panel")
            _append_unique(row["component_names"], str(followup.get("component_name") or ""))
            _append_unique(row["panel_roles"], str(followup.get("panel_role") or ""))
            row["hidden_families"] = _merged_families(
                row.get("hidden_families"),
                followup.get("hidden_families"),
                atlas.get(source, {}).get("hidden_families"),
            )
            if not row.get("first_failure_owner") or row["first_failure_owner"] == "none":
                row["first_failure_owner"] = str(followup.get("first_failure_owner") or "")

    rows = [
        _finalize_hard_panel_row(row)
        for row in sorted(rows_by_source.values(), key=_hard_panel_sort_key)[:target_size]
    ]
    return rows


def summarize_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_panel: dict[str, dict[str, Any]] = {}
    for panel_id in sorted({str(row["panel_id"]) for row in rows}):
        panel_rows = [row for row in rows if row["panel_id"] == panel_id]
        family_counts: Counter[str] = Counter()
        for row in panel_rows:
            family_counts.update(row.get("hidden_families") or [])
        by_panel[panel_id] = {
            "source_rows": len({int(row["source_row_index"]) for row in panel_rows}),
            "rows": len(panel_rows),
            "gold_kind_counts": dict(
                sorted(Counter(str(row.get("gold_kind") or "") for row in panel_rows).items())
            ),
            "hidden_family_counts": dict(sorted(family_counts.items())),
            "first_failure_owner_counts": _first_failure_counts(panel_rows),
        }
    return {
        "artifact_kind": "gan2026_rq1_rq2_single_task_control_panels",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "claim_boundary": (
            "Frozen validation-development panels for RQ1/RQ2 single-task controls; "
            "no locked-test row-level use and no model-performance claim."
        ),
        "panel_row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_panel_id": by_panel,
    }


def build_component_control_matrix(
    panel_rows: Sequence[Mapping[str, Any]],
    *,
    conditions: Sequence[Mapping[str, Any]] = CONTROL_CONDITIONS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for panel_row in sorted(
        panel_rows,
        key=lambda row: (str(row["panel_id"]), int(row["source_row_index"])),
    ):
        for condition in conditions:
            rows.append(_matrix_row(panel_row, condition))
    return rows, summarize_component_control_matrix(rows)


def summarize_component_control_matrix(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_condition: dict[str, dict[str, Any]] = {}
    for condition_id in sorted({str(row["condition_id"]) for row in rows}):
        condition_rows = [row for row in rows if row["condition_id"] == condition_id]
        by_condition[condition_id] = {
            "rows": len(condition_rows),
            "source_rows": len({int(row["source_row_index"]) for row in condition_rows}),
            "component_task": condition_rows[0]["component_task"] if condition_rows else "",
            "overload_condition": bool(condition_rows[0]["overload_condition"])
            if condition_rows
            else False,
        }
    return {
        "artifact_kind": "gan2026_rq1_rq2_component_control_matrix",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "claim_boundary": (
            "Pre-call matrix for isolated and paired-task overload controls. Rows record "
            "prompt/schema obligations but do not contain fresh model outputs."
        ),
        "matrix_row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "condition_count": len(by_condition),
        "by_condition": by_condition,
    }


def write_json_summary(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_panel_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 RQ1/RQ2 Single-Task Control Panels",
        "",
        "Frozen validation-development row panels for the isolated candidate, evidence, "
        "projection, and paired-task overload controls. These panels materialize row "
        "membership only; they do not run or score fresh model calls.",
        "",
        f"- Date: `{metadata['date']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Panel rows: {metadata['panel_row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Panels",
        "",
        "| Panel | Rows | Source rows | Gold kinds |",
        "| --- | ---: | ---: | --- |",
    ]
    for panel_id, summary in metadata["by_panel_id"].items():
        lines.append(
            f"| `{panel_id}` | {summary['rows']} | {summary['source_rows']} | "
            f"{_compact_counts(summary['gold_kind_counts'])} |"
        )
    lines.extend(
        [
            "",
            "## Hidden Family Coverage",
            "",
            "| Panel | Family | Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for panel_id, summary in metadata["by_panel_id"].items():
        for family, count in summary["hidden_family_counts"].items():
            lines.append(f"| `{panel_id}` | `{family}` | {count} |")
    lines.extend(
        [
            "",
            "## Row Manifest",
            "",
            "| Panel | Row | Gold | Kind | Families | Selection |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['panel_id']}` | {row['source_row_index']} | `{_md(row['gold_label'])}` | "
            f"`{row['gold_kind']}` | `{';'.join(row.get('hidden_families') or [])}` | "
            f"`{_panel_selection_text(row)}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            metadata["claim_boundary"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_matrix_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 RQ1/RQ2 Component-Control Matrix",
        "",
        "Pre-call condition matrix for isolated single-task controls and paired-task "
        "overload controls. The JSONL row grain is one source row by panel by condition.",
        "",
        f"- Date: `{metadata['date']}`",
        f"- Matrix rows: {metadata['matrix_row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        f"- Conditions: {metadata['condition_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Conditions",
        "",
        "| Condition | Task | Rows | Source rows | Overload |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for condition_id, summary in metadata["by_condition"].items():
        lines.append(
            f"| `{condition_id}` | `{summary['component_task']}` | {summary['rows']} | "
            f"{summary['source_rows']} | `{summary['overload_condition']}` |"
        )
    lines.extend(
        [
            "",
            "## Required Empty Output Slots",
            "",
            "Each JSONL row reserves fields for component output, exact evidence/source-id "
            "status, deterministic comparator label, gold label, hidden-family tags, metric "
            "fields, first-failure owner, and row-level notes. Fresh model-call runners should "
            "fill those fields without changing row membership.",
            "",
            "## Claim Boundary",
            "",
            metadata["claim_boundary"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _validation_records(*, data_path: Path, split_manifest_path: Path) -> list[dict[str, Any]]:
    records = []
    for record in load_records_for_split(
        "validation",
        data_path=data_path,
        manifest_path=split_manifest_path,
    ):
        families = hidden_family_atlas.classify_hidden_families(
            note_text=f"{record.note_text} {record.gold_reference}",
            gold_label=record.gold_normalized_label,
            predicted_label="",
        )
        records.append(
            {
                "source_row_index": record.source_row_index,
                "split": "validation",
                "gold_label": record.gold_normalized_label,
                "gold_kind": str(record.gold_label_kind),
                "gold_reference": record.gold_reference,
                "row_ok": record.row_ok,
                "hidden_families": list(families),
            }
        )
    return records


def _normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_row_index": int(record["source_row_index"]),
        "split": record.get("split") or "validation",
        "gold_label": str(record.get("gold_label") or ""),
        "gold_kind": str(record.get("gold_kind") or ""),
        "gold_reference": str(record.get("gold_reference") or ""),
        "row_ok": bool(record.get("row_ok", True)),
        "hidden_families": _merged_families(record.get("hidden_families")),
    }


def _panel_row(
    record: Mapping[str, Any],
    *,
    panel_id: str,
    selection_reason: str,
) -> dict[str, Any]:
    return {
        "artifact_kind": "gan2026_rq1_rq2_single_task_control_panel_row",
        "panel_id": panel_id,
        "panel_role": "balanced_control" if panel_id == "balanced_validation50" else "hard_control",
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": record.get("split") or "validation",
        "split_manifest": "gan2026_split_v1",
        "source_row_index": int(record["source_row_index"]),
        "gold_label": str(record.get("gold_label") or ""),
        "gold_kind": str(record.get("gold_kind") or ""),
        "gold_reference": str(record.get("gold_reference") or ""),
        "row_ok": bool(record.get("row_ok", True)),
        "hidden_families": _merged_families(record.get("hidden_families")),
        "first_failure_owner": str(record.get("first_failure_owner") or ""),
        "selection_reason": selection_reason,
        "selection_sources": list(record.get("selection_sources") or []),
        "predeclared_slices": list(record.get("predeclared_slices") or []),
        "component_names": list(record.get("component_names") or []),
        "panel_roles": list(record.get("panel_roles") or []),
        "claim_boundary": "validation_development_panel_membership_only",
    }


def _hard_panel_seed(
    source: Mapping[str, Any],
    *,
    atlas: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    source_row_index = int(source["source_row_index"])
    atlas_row = atlas.get(source_row_index, {})
    families = _merged_families(source.get("hidden_families"), atlas_row.get("hidden_families"))
    return {
        "source_row_index": source_row_index,
        "split": source.get("split") or "validation",
        "gold_label": source.get("gold_label") or atlas_row.get("gold_label") or "",
        "gold_kind": _gold_kind(source.get("gold_label") or atlas_row.get("gold_label") or ""),
        "gold_reference": "",
        "row_ok": True,
        "hidden_families": families,
        "first_failure_owner": (
            source.get("first_failure_owner") or atlas_row.get("first_failure_owner") or ""
        ),
        "selection_sources": [],
        "predeclared_slices": [],
        "component_names": [],
        "panel_roles": [],
    }


def _finalize_hard_panel_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return _panel_row(
        row,
        panel_id="hidden_family_hard_panel",
        selection_reason=";".join(row.get("selection_sources") or []),
    )


def _matrix_row(panel_row: Mapping[str, Any], condition: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_kind": "gan2026_rq1_rq2_component_control_matrix_row",
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": panel_row.get("split") or "validation",
        "split_manifest": panel_row.get("split_manifest") or "gan2026_split_v1",
        "source_row_index": int(panel_row["source_row_index"]),
        "row_panel_id": panel_row["panel_id"],
        "panel_role": panel_row.get("panel_role") or "",
        "condition_id": condition["condition_id"],
        "prompt_name": condition["prompt_name"],
        "prompt_version": "predeclared_v0",
        "model_id": "",
        "decoding_parameters": {},
        "component_task": condition["component_task"],
        "representation_type": condition["representation_type"],
        "input_contract": condition["input_contract"],
        "overload_condition": bool(condition["overload_condition"]),
        "exact_evidence_status": "",
        "source_id_status": "",
        "component_output": {},
        "deterministic_comparator_label": "",
        "deterministic_comparator_correct": "",
        "gold_label": panel_row.get("gold_label") or "",
        "gold_kind": panel_row.get("gold_kind") or "",
        "hidden_families": list(panel_row.get("hidden_families") or []),
        "component_metrics": {},
        "first_failure_owner": "",
        "row_notes": "",
        "claim_boundary": "pre_call_validation_development_control_matrix",
    }


def _balanced_sort_key(record: Mapping[str, Any]) -> tuple[int, int]:
    return (0 if record.get("row_ok") else 1, int(record["source_row_index"]))


def _hard_panel_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int]:
    source_rank = 0 if "atlas_hard_slice_manifest" in row.get("selection_sources", []) else 1
    owner_rank = 0 if row.get("first_failure_owner") not in {"", "none"} else 1
    return (source_rank, owner_rank, int(row["source_row_index"]))


def _followup_hard_panel_relevant(row: Mapping[str, Any]) -> bool:
    if row.get("panel_role") in {
        "changed_row",
        "schema_near_or_projection_miss",
        "typed_operand_incomplete",
        "gated_projection_target",
    }:
        return True
    return str(row.get("first_failure_owner") or "") not in {"", "none"}


def _load_atlas_by_source(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    by_source: dict[int, dict[str, Any]] = defaultdict(
        lambda: {"hidden_families": [], "first_failure_owner": "", "gold_label": ""}
    )
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source = int(row["source_row_index"])
            current = by_source[source]
            current["hidden_families"] = _merged_families(
                current.get("hidden_families"), row.get("hidden_families")
            )
            if row.get("gold_label") and not current.get("gold_label"):
                current["gold_label"] = row["gold_label"]
            if row.get("first_failure_owner") and not current.get("first_failure_owner"):
                current["first_failure_owner"] = row["first_failure_owner"]
    return dict(by_source)


def _load_json(path: Path, *, default: Mapping[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    return json.loads(path.read_text(encoding="utf-8"))


def _gold_kind(label: str) -> str:
    if not str(label).strip():
        return ""
    return str(label_to_frequency_record(str(label)).kind)


def _merged_families(*values: Any) -> list[str]:
    families: list[str] = []
    for value in values:
        if not value:
            continue
        parts = value.replace(",", ";").split(";") if isinstance(value, str) else value
        for part in parts:
            family = str(part).strip()
            if family and family not in families:
                families.append(family)
    return families or ["unmapped"]


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _compact_counts(counts: Mapping[str, Any]) -> str:
    return ", ".join(f"`{key}`={value}" for key, value in counts.items())


def _first_failure_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return dict(
        sorted(Counter(str(row.get("first_failure_owner") or "") for row in rows).items())
    )


def _panel_selection_text(row: Mapping[str, Any]) -> str:
    return _md(row.get("selection_reason") or ";".join(row.get("selection_sources") or []))


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--split-manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--atlas-csv-path", type=Path, default=DEFAULT_ATLAS_CSV_PATH)
    parser.add_argument(
        "--hard-slice-manifest-path",
        type=Path,
        default=DEFAULT_HARD_SLICE_MANIFEST_PATH,
    )
    parser.add_argument("--followup-panel-path", type=Path, default=DEFAULT_FOLLOWUP_PANEL_PATH)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--panel-json-path", type=Path, default=DEFAULT_PANEL_JSON_PATH)
    parser.add_argument("--panel-report-path", type=Path, default=DEFAULT_PANEL_REPORT_PATH)
    parser.add_argument("--matrix-jsonl-path", type=Path, default=DEFAULT_MATRIX_JSONL_PATH)
    parser.add_argument("--matrix-json-path", type=Path, default=DEFAULT_MATRIX_JSON_PATH)
    parser.add_argument("--matrix-report-path", type=Path, default=DEFAULT_MATRIX_REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    panel_rows, panel_metadata = build_control_panels(
        data_path=args.data_path,
        split_manifest_path=args.split_manifest_path,
        atlas_csv_path=args.atlas_csv_path,
        hard_slice_manifest_path=args.hard_slice_manifest_path,
        followup_panel_path=args.followup_panel_path,
    )
    write_jsonl_rows(panel_rows, args.panel_jsonl_path)
    write_json_summary(panel_metadata, args.panel_json_path)
    write_panel_report(
        panel_rows,
        panel_metadata,
        args.panel_report_path,
        jsonl_path=args.panel_jsonl_path,
        json_path=args.panel_json_path,
    )

    matrix_rows, matrix_metadata = build_component_control_matrix(panel_rows)
    write_jsonl_rows(matrix_rows, args.matrix_jsonl_path)
    write_json_summary(matrix_metadata, args.matrix_json_path)
    write_matrix_report(
        matrix_rows,
        matrix_metadata,
        args.matrix_report_path,
        jsonl_path=args.matrix_jsonl_path,
        json_path=args.matrix_json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
