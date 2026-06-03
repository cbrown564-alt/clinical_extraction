"""Build the frozen Gan 2026 component-projection follow-up panel."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_RQ2_MATRIX_PATH = Path(
    "experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl"
)
DEFAULT_RQ4_MATRIX_PATH = Path(
    "experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl"
)
DEFAULT_ATLAS_CSV_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv"
)
DEFAULT_HARD_SLICE_MANIFEST_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_component_projection_followup_panel_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_component_projection_followup_panel_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_component_projection_followup_panel_2026-06-04.md"
)

PANEL_RQ2_COMPONENTS = {
    "hybrid_adjudicator_raw",
    "llm_candidate_selector_raw",
    "llm_heavy_selected_fact",
    "claim_table_final_query",
    "state_graph_projection",
}
PANEL_RQ4_COMPONENTS = {
    "boundary_state_priority",
    "competing_frequency_uncertainty",
    "graph_gated_month_bucket_duration",
    "hybrid_adjudicator_raw",
    "llm_heavy_selected_fact",
    "claim_table_final_query",
    "state_graph_projection",
}


def build_component_projection_panel(
    *,
    rq2_matrix_path: Path = DEFAULT_RQ2_MATRIX_PATH,
    rq4_matrix_path: Path = DEFAULT_RQ4_MATRIX_PATH,
    atlas_csv_path: Path = DEFAULT_ATLAS_CSV_PATH,
    hard_slice_manifest_path: Path = DEFAULT_HARD_SLICE_MANIFEST_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build frozen RQ2/RQ4 panel rows with policy labels and predeclared slices."""

    atlas = _load_atlas_by_source(atlas_csv_path)
    manifest = _load_hard_slice_manifest(hard_slice_manifest_path)
    slice_membership = _slice_membership(manifest)

    rows: list[dict[str, Any]] = []
    for row in load_jsonl_rows(rq2_matrix_path):
        component = str(row.get("candidate_name") or "")
        if component in PANEL_RQ2_COMPONENTS and _is_panel_relevant(row, subproblem="rq2"):
            rows.append(_panel_row(row, subproblem="rq2", atlas=atlas, slices=slice_membership))
    for row in load_jsonl_rows(rq4_matrix_path):
        component = str(row.get("component_name") or "")
        if component in PANEL_RQ4_COMPONENTS and _is_panel_relevant(row, subproblem="rq4"):
            rows.append(_panel_row(row, subproblem="rq4", atlas=atlas, slices=slice_membership))

    rows.sort(
        key=lambda row: (
            row["clinical_subproblem"],
            row["component_name"],
            row["panel_role"],
            int(row["source_row_index"]),
        )
    )
    return rows, summarize_panel_rows(rows, manifest=manifest)


def summarize_panel_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    by_role = Counter(str(row["panel_role"]) for row in rows)
    by_owner = Counter(str(row["first_failure_owner"]) for row in rows)
    by_component = Counter(str(row["component_name"]) for row in rows)
    by_family: Counter[str] = Counter()
    by_family_owner: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        owner = str(row["first_failure_owner"])
        for family in row.get("hidden_families") or ["unmapped"]:
            by_family[str(family)] += 1
            by_family_owner[str(family)][owner] += 1

    return {
        "artifact_kind": "gan2026_component_projection_followup_panel",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "claim_boundary": (
            "Frozen validation-development follow-up panel over saved RQ2/RQ4 artifacts; "
            "no scorer, prompt, model, projection-policy, or holdout change."
        ),
        "panel_row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_panel_role": dict(sorted(by_role.items())),
        "by_component": dict(sorted(by_component.items())),
        "by_first_failure_owner": dict(sorted(by_owner.items())),
        "by_hidden_family": dict(sorted(by_family.items())),
        "by_hidden_family_first_failure_owner": {
            family: dict(sorted(counter.items()))
            for family, counter in sorted(by_family_owner.items())
        },
        "component_outcomes": _component_outcomes(rows),
        "gated_projection_panels": _gated_projection_panels(rows),
        "predeclared_slices": _predeclared_slices(manifest or {}),
    }


def write_panel_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_panel_json(metadata: Mapping[str, Any], path: Path) -> None:
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
        "# Gan 2026 Frozen Component-Projection Follow-Up Panel",
        "",
        "Frozen validation-development replay over saved RQ2/RQ4 artifacts. The panel "
        "applies the interpretation policy by propagating hidden-family tags, assigning "
        "first-failure owner labels, and separating gated projection targets from regression "
        "panels. It is not a benchmark or locked-holdout claim.",
        "",
        f"- Date: `{metadata['date']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Panel rows: {metadata['panel_row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Panel Roles",
        "",
        "| Role | Rows |",
        "| --- | ---: |",
    ]
    for role, count in metadata["by_panel_role"].items():
        lines.append(f"| `{role}` | {count} |")

    lines.extend(["", "## First-Failure Owners", "", "| Owner | Rows |", "| --- | ---: |"])
    for owner, count in metadata["by_first_failure_owner"].items():
        lines.append(f"| `{owner}` | {count} |")

    lines.extend(
        [
            "",
            "## Component Outcomes",
            "",
            "| Component | Rows | W->C | C->W | Exact evidence |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for component, summary in metadata["component_outcomes"].items():
        lines.append(
            f"| `{component}` | {summary['rows']} | {summary['wrong_to_correct']} | "
            f"{summary['correct_to_wrong']} | {summary['exact_evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Gated Projection Panels",
            "",
            "| Gate | Target rows | Regression rows | W->C | C->W | Changed regression rows |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for gate, summary in metadata["gated_projection_panels"].items():
        lines.append(
            f"| `{gate}` | {summary['target_rows']} | {summary['regression_rows']} | "
            f"{summary['wrong_to_correct']} | {summary['correct_to_wrong']} | "
            f"{summary['changed_regression_rows']} |"
        )

    lines.extend(
        [
            "",
            "## Predeclared Projection Slices",
            "",
            "| Slice | Rows | Component focus | Primary metric |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for slice_name, summary in metadata["predeclared_slices"].items():
        lines.append(
            f"| `{slice_name}` | {summary['row_count']} | "
            f"{_md(summary['component_focus'])} | {_md(summary['primary_metric'])} |"
        )

    lines.extend(
        [
            "",
            "## Hidden Family By First-Failure Owner",
            "",
            "| Hidden family | First-failure owner | Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for family, owners in metadata["by_hidden_family_first_failure_owner"].items():
        for owner, count in owners.items():
            lines.append(f"| `{family}` | `{owner}` | {count} |")

    changed_rows = [
        row
        for row in rows
        if (
            row.get("wrong_to_correct")
            or row.get("correct_to_wrong")
            or row["panel_role"] != "context"
        )
    ][:100]
    lines.extend(
        [
            "",
            "## Highest-Signal Rows",
            "",
            "| Subproblem | Role | Component | Source row | Gold | Candidate | Owner | Families |",
            "| --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in changed_rows:
        lines.append(
            f"| `{row['clinical_subproblem']}` | `{row['panel_role']}` | "
            f"`{row['component_name']}` | {row['source_row_index']} | "
            f"`{_md(row['gold_label'])}` | `{_md(row['candidate_label'])}` | "
            f"`{row['first_failure_owner']}` | `{';'.join(row.get('hidden_families') or [])}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This panel keeps deterministic outputs as comparators and safety floors, not as "
            "eligible RQ1-RQ4 answers. Projection-compatible clinical phrases are assigned "
            "to projection/rendering policy rather than counted as LLM component failures; "
            "faithful ambiguous facts are kept visible for later policy-mediated projection.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _panel_row(
    row: Mapping[str, Any],
    *,
    subproblem: str,
    atlas: Mapping[int, Mapping[str, Any]],
    slices: Mapping[int, Sequence[str]],
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    atlas_row = atlas.get(source_row_index, {})
    component = str(row.get("candidate_name" if subproblem == "rq2" else "component_name") or "")
    families = _merged_families(row.get("hidden_families"), atlas_row.get("hidden_families"))
    owner, reason, policy = _first_failure_owner(row, subproblem=subproblem, atlas_row=atlas_row)
    return {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": row.get("split") or "validation",
        "split_manifest": row.get("split_manifest") or "gan2026_split_v1",
        "clinical_subproblem": "evidence_selection" if subproblem == "rq2" else "projection",
        "source_row_index": source_row_index,
        "component_name": component,
        "panel_role": _panel_role(row, subproblem=subproblem),
        "surface": row.get("surface") or row.get("distribution") or "",
        "gold_label": row.get("gold_label") or row.get("gold_normalized_label") or "",
        "candidate_label": _clean_text(row.get("candidate_label")),
        "baseline_label": row.get("baseline_label") or "",
        "hidden_families": families,
        "first_failure_owner": owner,
        "first_failure_reason": reason,
        "interpretation_policy": policy,
        "predeclared_slices": list(slices.get(source_row_index, [])),
        "wrong_to_correct": bool(row.get("wrong_to_correct")),
        "correct_to_wrong": bool(row.get("correct_to_wrong")),
        "changed_from_baseline": bool(row.get("changed_from_baseline"))
        or bool(row.get("changed_from_deterministic")),
        "evidence_status": row.get("evidence_status") or "",
        "source_id_status": row.get("source_id_status") or "",
        "operand_complete": _optional_bool(row.get("operand_complete")),
        "projection_correct": _optional_bool(
            row.get("projection_correct", row.get("purist_correct"))
        ),
        "claim_boundary": "validation_development_frozen_component_projection_panel",
    }


def _is_panel_relevant(row: Mapping[str, Any], *, subproblem: str) -> bool:
    if row.get("wrong_to_correct") or row.get("correct_to_wrong"):
        return True
    if subproblem == "rq2":
        return (
            row.get("evidence_status") == "exact"
            and row.get("purist_correct") is False
            or row.get("operand_complete") is False
        )
    if row.get("surface") in {"target_duration_enriched", "regression_validation_hard_slice"}:
        return True
    if row.get("projection_correct") is False and row.get("component_name") in {
        "llm_heavy_selected_fact",
        "claim_table_final_query",
    }:
        return True
    return False


def _panel_role(row: Mapping[str, Any], *, subproblem: str) -> str:
    if subproblem == "rq4" and row.get("component_name") == "graph_gated_month_bucket_duration":
        if row.get("surface") == "target_duration_enriched":
            return "gated_projection_target"
        if row.get("surface") == "regression_validation_hard_slice":
            return "gated_projection_regression"
    if row.get("wrong_to_correct") or row.get("correct_to_wrong"):
        return "changed_row"
    if (
        subproblem == "rq2"
        and row.get("evidence_status") == "exact"
        and row.get("purist_correct") is False
    ):
        return "schema_near_or_projection_miss"
    if row.get("operand_complete") is False:
        return "typed_operand_incomplete"
    return "context"


def _first_failure_owner(
    row: Mapping[str, Any],
    *,
    subproblem: str,
    atlas_row: Mapping[str, Any],
) -> tuple[str, str, str]:
    if _row_correct(row, subproblem=subproblem):
        return "none", "component row is correct on its scored surface", "standard"

    gold = str(row.get("gold_label") or row.get("gold_normalized_label") or "")
    candidate = str(row.get("candidate_label") or "")
    if _projection_compatible_phrase(gold, candidate):
        return (
            "projection_rendering_policy",
            "candidate preserves a projection-compatible clinical phrase",
            "projection_compatible_phrase",
        )
    if _faithful_ambiguous_phrase(candidate):
        return (
            "projection_rendering_policy",
            "candidate preserves a faithful denominator-ambiguous clinical fact",
            "faithful_ambiguous_fact",
        )

    existing = str(row.get("first_failure_owner") or "")
    if existing and existing != "none":
        return (
            existing,
            str(row.get("first_failure_reason") or "row carried owner label"),
            "standard",
        )

    if str(row.get("evidence_status") or "") not in {"", "exact", "source_near", "valid"}:
        return "evidence_selection", "selected evidence was not exact/source-near", "standard"
    if str(row.get("source_id_status") or "") not in {"", "valid", "not_instrumented"}:
        return "evidence_selection", "selected source ids were invalid", "standard"
    if row.get("operand_complete") is False:
        return "typed_state_representation", "typed operands were incomplete", "standard"
    if subproblem == "rq4":
        return "projection_policy", "projection row missed or regressed final label", "standard"
    if candidate.strip().lower() in {"", "frequency", "seizure_frequency"}:
        return (
            "typed_state_representation",
            "selected fact lacks a renderable typed state",
            "standard",
        )

    atlas_owner = str(atlas_row.get("first_failure_owner") or "")
    if atlas_owner and atlas_owner != "none":
        return atlas_owner, str(atlas_row.get("first_failure_reason") or "atlas owner"), "atlas"
    return (
        "typed_state_representation",
        "exact evidence selected but state/projection remains wrong",
        "standard",
    )


def _row_correct(row: Mapping[str, Any], *, subproblem: str) -> bool:
    if subproblem == "rq4" and "projection_correct" in row:
        return bool(row.get("projection_correct"))
    if "purist_correct" in row:
        return bool(row.get("purist_correct"))
    return False


def _projection_compatible_phrase(gold: str, candidate: str) -> bool:
    normalized_gold = _normalize_label_phrase(gold)
    normalized_candidate = _normalize_label_phrase(candidate)
    if normalized_gold and normalized_gold == normalized_candidate:
        return True
    if normalized_gold == "multiple per week" and (
        "several" in candidate.lower() and "per week" in candidate.lower()
    ):
        return True
    if normalized_gold == "2 per 2 week" and "twice every two weeks" in candidate.lower():
        return True
    return False


def _faithful_ambiguous_phrase(candidate: str) -> bool:
    text = candidate.lower()
    return "multiple per shift" in text or "per shift" in text


def _normalize_label_phrase(value: str) -> str:
    text = " ".join(value.lower().replace("times", "").split())
    text = text.replace("several", "multiple")
    return text


def _component_outcomes(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        component = str(row["component_name"])
        counters[component]["rows"] += 1
        counters[component]["wrong_to_correct"] += int(bool(row.get("wrong_to_correct")))
        counters[component]["correct_to_wrong"] += int(bool(row.get("correct_to_wrong")))
        counters[component]["exact_evidence"] += int(row.get("evidence_status") == "exact")
    return {component: dict(counter) for component, counter in sorted(counters.items())}


def _gated_projection_panels(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row.get("panel_role") not in {
            "gated_projection_target",
            "gated_projection_regression",
        }:
            continue
        component = str(row["component_name"])
        if row["panel_role"] == "gated_projection_target":
            counters[component]["target_rows"] += 1
        else:
            counters[component]["regression_rows"] += 1
            counters[component]["changed_regression_rows"] += int(
                bool(row.get("changed_from_baseline"))
            )
        counters[component]["wrong_to_correct"] += int(bool(row.get("wrong_to_correct")))
        counters[component]["correct_to_wrong"] += int(bool(row.get("correct_to_wrong")))
    return {component: dict(counter) for component, counter in sorted(counters.items())}


def _predeclared_slices(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    slices = {}
    for slice_record in manifest.get("slices") or []:
        name = str(slice_record.get("slice_name") or "")
        if not name:
            continue
        slices[name] = {
            "row_count": len(slice_record.get("members") or []),
            "component_focus": slice_record.get("component_focus") or "",
            "membership_rule": slice_record.get("membership_rule") or "",
            "primary_metric": slice_record.get("primary_metric") or "",
        }
    return slices


def _slice_membership(manifest: Mapping[str, Any]) -> dict[int, list[str]]:
    memberships: dict[int, list[str]] = defaultdict(list)
    for slice_record in manifest.get("slices") or []:
        name = str(slice_record.get("slice_name") or "")
        for member in slice_record.get("members") or []:
            memberships[int(member["source_row_index"])].append(name)
    return dict(memberships)


def _load_atlas_by_source(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    by_source: dict[int, dict[str, Any]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source = int(row["source_row_index"])
            current = by_source.setdefault(
                source,
                {
                    "hidden_families": [],
                    "first_failure_owner": "",
                    "first_failure_reason": "",
                },
            )
            current["hidden_families"] = _merged_families(
                current.get("hidden_families"), row.get("hidden_families")
            )
            if not current.get("first_failure_owner") and row.get("first_failure_owner"):
                current["first_failure_owner"] = row["first_failure_owner"]
                current["first_failure_reason"] = row.get("first_failure_reason") or ""
    return by_source


def _load_hard_slice_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"slices": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _merged_families(*values: Any) -> list[str]:
    families: list[str] = []
    for value in values:
        if not value:
            continue
        if isinstance(value, str):
            parts = value.replace(",", ";").split(";")
        else:
            parts = [str(part) for part in value]
        for part in parts:
            family = part.strip()
            if family and family not in families:
                families.append(family)
    return families or ["unmapped"]


def _optional_bool(value: Any) -> bool | str:
    if value in {None, ""}:
        return ""
    return bool(value)


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rq2-matrix-path", type=Path, default=DEFAULT_RQ2_MATRIX_PATH)
    parser.add_argument("--rq4-matrix-path", type=Path, default=DEFAULT_RQ4_MATRIX_PATH)
    parser.add_argument("--atlas-csv-path", type=Path, default=DEFAULT_ATLAS_CSV_PATH)
    parser.add_argument(
        "--hard-slice-manifest-path", type=Path, default=DEFAULT_HARD_SLICE_MANIFEST_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    rows, metadata = build_component_projection_panel(
        rq2_matrix_path=args.rq2_matrix_path,
        rq4_matrix_path=args.rq4_matrix_path,
        atlas_csv_path=args.atlas_csv_path,
        hard_slice_manifest_path=args.hard_slice_manifest_path,
    )
    write_panel_jsonl(rows, args.jsonl_path)
    write_panel_json(metadata, args.json_path)
    write_panel_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
