"""Hidden-family and first-failure atlas for saved Gan 2026 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_OUTPUT_CSV_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_hidden_family_first_failure_atlas_2026-06-03.md"
)
DEFAULT_HARD_SLICE_JSON_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json"
)
DEFAULT_HARD_SLICE_REPORT_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.md"
)

ATLAS_FIELDNAMES = (
    "artifact_name",
    "source_row_index",
    "split",
    "primary_layer",
    "gold_label",
    "predicted_label",
    "purist_correct",
    "pragmatic_correct",
    "hidden_families",
    "first_failure_owner",
    "first_failure_reason",
    "evidence_exact",
    "selected_operand_complete",
    "deterministic_correct",
    "oracle_candidate_presence",
    "oracle_graph_representability",
)

ATLAS_HARD_SLICE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "slice_name": "candidate_generation_rescue",
        "component_focus": "candidate generation",
        "membership_rule": (
            "Atlas row is Purist-wrong and first_failure_owner is candidate_generation."
        ),
        "primary_metric": (
            "Candidate-recall rescue rate before final-label promotion; final policy keeps the "
            "deterministic safety floor unless a rescue is predeclared and ablated."
        ),
    },
    {
        "slice_name": "candidate_generation_unknown_seizure_free_boundary",
        "component_focus": "candidate generation",
        "membership_rule": (
            "Atlas row is Purist-wrong, first_failure_owner is candidate_generation, and "
            "hidden_families includes unknown_boundary or seizure_free_duration."
        ),
        "primary_metric": (
            "Boundary-state recall without converting uncertain seizure-free language into a "
            "prediction-bearing deterministic repair."
        ),
    },
    {
        "slice_name": "projection_arbitration",
        "component_focus": "graph/final projection",
        "membership_rule": (
            "Atlas row is Purist-wrong and first_failure_owner is projection or "
            "final_projection."
        ),
        "primary_metric": (
            "Projection-variant correction precision, mechanical-correct to projected-wrong "
            "regressions, and selected-evidence/source trace validity."
        ),
    },
    {
        "slice_name": "projection_unknown_seizure_free_arbitration",
        "component_focus": "graph/final projection",
        "membership_rule": (
            "Atlas row is Purist-wrong, first_failure_owner is projection or final_projection, "
            "and hidden_families includes unknown_boundary, seizure_free_duration, or "
            "current_vs_historical."
        ),
        "primary_metric": (
            "Unknown/seizure-free/current-vs-historical arbitration precision with no broad "
            "validation retuning."
        ),
    },
)


def build_atlas_rows(
    artifact_paths: Sequence[Path],
    *,
    primary_layer: str | None = None,
    data_path: Path = DEFAULT_DATA_PATH,
) -> list[dict[str, Any]]:
    records = {
        record.source_row_index: record for record in load_records_with_monthly_frequency(data_path)
    }
    atlas_rows: list[dict[str, Any]] = []
    for artifact_path in artifact_paths:
        artifact_rows = load_jsonl_rows(artifact_path)
        for row in artifact_rows:
            source_row_index = int(row["source_row_index"])
            record = records[source_row_index]
            layer_name = primary_layer or _default_primary_layer(row)
            score_layer = (row.get("score_layers") or {}).get(layer_name) or {}
            predicted_label = _text(score_layer.get("final_label"))
            diagnostic_text = " ".join(
                [
                    record.gold_reference,
                    _selected_evidence_text(row),
                    record.gold_normalized_label,
                    predicted_label,
                ]
            )
            families = classify_hidden_families(
                note_text=diagnostic_text,
                gold_label=record.gold_normalized_label,
                predicted_label=predicted_label,
            )
            first_failure_owner, first_failure_reason = classify_first_failure(
                row,
                layer_name=layer_name,
            )
            atlas_rows.append(
                {
                    "artifact_name": artifact_path.name,
                    "source_row_index": source_row_index,
                    "split": row.get("split") or "",
                    "primary_layer": layer_name,
                    "gold_label": record.gold_normalized_label,
                    "predicted_label": predicted_label,
                    "purist_correct": bool(score_layer.get("purist_correct")),
                    "pragmatic_correct": bool(score_layer.get("pragmatic_correct")),
                    "hidden_families": ";".join(families),
                    "first_failure_owner": first_failure_owner,
                    "first_failure_reason": first_failure_reason,
                    "evidence_exact": _evidence_exact(row),
                    "selected_operand_complete": _selected_operand_complete(row),
                    "deterministic_correct": _diagnostic_bool(row, "deterministic_correct"),
                    "oracle_candidate_presence": _diagnostic_bool(row, "oracle_candidate_presence"),
                    "oracle_graph_representability": _diagnostic_bool(
                        row, "oracle_graph_representability"
                    ),
                }
            )
    return atlas_rows


def classify_hidden_families(
    *,
    note_text: str,
    gold_label: str,
    predicted_label: str,
) -> tuple[str, ...]:
    text = " ".join([note_text, gold_label, predicted_label]).lower()
    families: list[str] = []

    if gold_label == "unknown" or predicted_label == "unknown":
        families.append("unknown_boundary")
    if "seizure free" in gold_label or "seizure free" in predicted_label or _has_any(
        text, "seizure-free", "seizure free", "no seizures", "no further events", "last seizure"
    ):
        families.append("seizure_free_duration")
    if _has_any(text, "cluster", "clusters", "per cluster"):
        families.append("cluster_burden")
    if _has_any(text, "diary", "calendar", "log", "entries"):
        families.append("diary_or_log_aggregation")
    if _has_any(text, "nightly", "daily", "weekly", "monthly", "yearly", "per day", "per week"):
        families.append("rate_bucket_or_denominator")
    if _has_any(text, "past ", "since ", "last ", "previous", "histor", "currently", "current"):
        families.append("current_vs_historical")
    if _has_any(
        text,
        "focal",
        "generalised",
        "generalized",
        "absence",
        "tonic",
        "clonic",
        "aura",
        "semiology",
    ):
        families.append("competing_semiologies")
    if _has_any(text, "uncertain", "unclear", "possible", "suspected", "may represent", "unknown"):
        families.append("uncertainty_or_ambiguity")
    if _has_any(text, "bimonthly", "biweekly", "every other", "multiple per", "most weekdays"):
        families.append("benchmark_format_convention")

    if not families:
        families.append("unclassified")
    return tuple(dict.fromkeys(families))


def classify_first_failure(row: Mapping[str, Any], *, layer_name: str) -> tuple[str, str]:
    score_layers = row.get("score_layers") or {}
    layer = score_layers.get(layer_name) or {}
    if layer.get("purist_correct"):
        return "none", "primary layer is Purist-correct"
    status = row.get("component_status") or {}
    diagnostics = row.get("diagnostics") or {}

    if layer_name == "final_projected_label":
        if row.get("call_error"):
            return "call", "model call failed before scoring"
        if row.get("parse_errors"):
            return "schema_or_parse", "blocking parse/schema errors are recorded"
        raw = score_layers.get("raw_model_clinical_selection") or {}
        mechanical = score_layers.get("mechanical_adapter_label") or {}
        if status.get("evidence_exactness") != "ok":
            return "evidence_selection", "selected evidence was not exact/source-near"
        if status.get("selected_fact_trace") not in {None, "ok"}:
            return "selected_fact_trace", "selected fact trace mismatch was recorded"
        if status.get("selected_operand_completeness") != "ok":
            return "operand_exposure", "model did not expose complete adapter operands"
        if raw.get("purist_correct") and not mechanical.get("purist_correct"):
            return "deterministic_adapter", "adapter regressed a raw-correct clinical selection"
        if mechanical.get("purist_correct") and not layer.get("purist_correct"):
            return "final_projection", "final projection regressed a mechanical-correct row"
        if not raw.get("purist_correct"):
            return "llm_clinical_selection", "raw model clinical selection was already wrong"
        return (
            "uncertain_layer_interaction",
            "row is wrong but recorded layer ownership is ambiguous",
        )

    if layer_name == "hybrid_adjudicator_with_adapters":
        if row.get("call_error"):
            return "call", "model call failed before scoring"
        if diagnostics.get("deterministic_correct_regression"):
            return "safety_floor_regression", "final policy regressed a deterministic-correct row"
        if diagnostics.get("deterministic_correct") is False:
            if diagnostics.get("oracle_candidate_presence") is False:
                return "candidate_generation", "gold state absent from candidate set"
            if diagnostics.get("oracle_graph_representability") is False:
                return "state_representation", "gold state absent from graph nodes"
            if diagnostics.get("graph_projection_correct") is False:
                return "projection", "gold appears representable but projection is wrong"
            return "deterministic_safety_floor", "safety-floor candidate is wrong"
        if diagnostics.get("adjudicator_adapted_correct") is False:
            return (
                "llm_sidecar_adjudication",
                "LLM sidecar/adjudicator is wrong but safety floor protects",
            )
        if row.get("parse_errors"):
            return "schema_or_parse", "blocking prediction-layer parse/schema errors are recorded"
        return (
            "uncertain_layer_interaction",
            "row is wrong but diagnostics do not isolate ownership",
        )

    return "unknown_layer", f"no first-failure policy is defined for {layer_name}"


def summarize_atlas_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    incorrect = [row for row in rows if not row["purist_correct"]]
    return {
        "row_count": len(rows),
        "purist_correct": sum(bool(row["purist_correct"]) for row in rows),
        "pragmatic_correct": sum(bool(row["pragmatic_correct"]) for row in rows),
        "incorrect_count": len(incorrect),
        "artifacts": dict(Counter(str(row["artifact_name"]) for row in rows)),
        "primary_layers": dict(Counter(str(row["primary_layer"]) for row in rows)),
        "first_failure_owners": dict(Counter(str(row["first_failure_owner"]) for row in incorrect)),
        "hidden_families": dict(
            Counter(
                family
                for row in rows
                for family in str(row["hidden_families"]).split(";")
                if family
            )
        ),
        "incorrect_hidden_families": dict(
            Counter(
                family
                for row in incorrect
                for family in str(row["hidden_families"]).split(";")
                if family
            )
        ),
        "family_by_first_failure": _family_by_first_failure(incorrect),
    }


def write_atlas_csv(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ATLAS_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in ATLAS_FIELDNAMES})


def write_atlas_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_atlas_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def build_atlas_hard_slice_manifest(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_atlas_csv: str | None = None,
) -> dict[str, Any]:
    """Build reproducible atlas-derived hard slices for the next diagnostic experiment."""

    slices = []
    for definition in ATLAS_HARD_SLICE_DEFINITIONS:
        members = [
            _hard_slice_member(row)
            for row in rows
            if _belongs_to_atlas_hard_slice(row, definition["slice_name"])
        ]
        slices.append(
            {
                **definition,
                "row_count": len(members),
                "members": sorted(members, key=lambda row: row["source_row_index"]),
            }
        )

    return {
        "artifact_kind": "gan2026_atlas_candidate_generation_projection_hard_slices",
        "date": "2026-06-03",
        "source_atlas_csv": source_atlas_csv,
        "source_policy": (
            "Validation-development atlas rows only; no locked-test row-level inspection and "
            "no hosted model calls."
        ),
        "split_manifest": "gan2026_split_v1",
        "candidate_context": "hybrid_parallel_state_candidate_reasoner deterministic safety floor",
        "claim_language": (
            "Diagnostic validation-cycle hard-slice manifest, not a benchmark or holdout claim."
        ),
        "stop_rule": (
            "Promote only if candidate-generation rescues or projection-arbitration changes are "
            "high precision on these fixed slices, preserve evidence/source traces, and introduce "
            "no deterministic-correct regressions under the safety-floor final policy."
        ),
        "slices": slices,
    }


def write_atlas_hard_slice_manifest(manifest: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_atlas_hard_slice_report(manifest: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Atlas Candidate-Generation And Projection Hard-Slice Predeclaration",
        "",
        "This is a validation-development predeclaration derived from the hidden-family and "
        "first-failure atlas. It fixes slice membership before any candidate-generation rescue "
        "or projection-arbitration change is run.",
        "",
        f"- Date: `{manifest['date']}`",
        f"- Split manifest: `{manifest['split_manifest']}`",
        f"- Source atlas CSV: `{manifest.get('source_atlas_csv') or 'in-memory rows'}`",
        f"- Candidate context: `{manifest['candidate_context']}`",
        f"- Claim language: {manifest['claim_language']}",
        "",
        "## Hypothesis",
        "",
        "The remaining validation misses are dominated by two separable mechanisms: absent or "
        "weak candidate generation, and projection/arbitration over already representable "
        "clinical states. A useful next experiment should improve one named mechanism on fixed "
        "validation hard slices while keeping the deterministic safety-floor final policy.",
        "",
        "## Slice Manifest",
        "",
        "| Slice | Focus | Rows | Primary metric |",
        "| --- | --- | ---: | --- |",
    ]
    for slice_record in manifest["slices"]:
        lines.append(
            f"| `{slice_record['slice_name']}` | {slice_record['component_focus']} | "
            f"{slice_record['row_count']} | {slice_record['primary_metric']} |"
        )

    lines.extend(
        [
            "",
            "## Experiment Unit",
            "",
            "- Minimal change: add only candidate-generation rescue or projection-arbitration "
            "variants, not a broad prompt/schema/scorer rewrite.",
            "- Surface: fixed validation hard slices in this manifest; no train or locked-test "
            "inspection.",
            "- Comparator: current `hybrid_parallel_state_candidate_reasoner` deterministic "
            "safety-floor replay.",
            "- Required ablations: deterministic top, candidate-generation rescue sidecar, "
            "baseline graph projection, projection-arbitration variant, and final safety-floor "
            "policy.",
            "- Required counts: slice-level Purist/Pragmatic, wrong-to-correct, "
            "correct-to-wrong, deterministic-correct regressions, evidence exactness, source-id "
            "validity, fallback rate, and changed-label precision.",
            "",
            "## Stop Rule",
            "",
            str(manifest["stop_rule"]),
            "",
            "## Slice Definitions",
            "",
        ]
    )
    for slice_record in manifest["slices"]:
        lines.extend(
            [
                f"### {slice_record['slice_name']}",
                "",
                f"- Rows: {slice_record['row_count']}",
                f"- Membership: {slice_record['membership_rule']}",
                f"- Component focus: {slice_record['component_focus']}",
                f"- Primary metric: {slice_record['primary_metric']}",
                "",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_atlas_report(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    csv_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Hidden-Family And First-Failure Atlas",
        "",
        "Diagnostic validation-cycle artifact. This summarizes saved experiment rows; it "
        "does not change scoring, prompts, rules, projection policy, or holdout claims.",
        "",
        f"- Rows: {summary['row_count']}",
        f"- Purist correct: {summary['purist_correct']}/{summary['row_count']}",
        f"- Pragmatic correct: {summary['pragmatic_correct']}/{summary['row_count']}",
        f"- CSV: `{csv_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Artifacts",
        "",
        "| Artifact | Rows |",
        "| --- | ---: |",
    ]
    for artifact, count in sorted(summary["artifacts"].items()):
        lines.append(f"| `{artifact}` | {count} |")

    lines.extend(
        ["", "## First Failure Owners", "", "| Owner | Incorrect rows |", "| --- | ---: |"]
    )
    for owner, count in sorted(
        summary["first_failure_owners"].items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{owner}` | {count} |")

    lines.extend(
        ["", "## Hidden Families On Incorrect Rows", "", "| Family | Rows |", "| --- | ---: |"]
    )
    for family, count in sorted(
        summary["incorrect_hidden_families"].items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{family}` | {count} |")

    lines.extend(
        [
            "",
            "## Family By First Failure",
            "",
            "| Family | First failure owner | Incorrect rows |",
            "| --- | --- | ---: |",
        ]
    )
    for family, owners in sorted(summary["family_by_first_failure"].items()):
        for owner, count in sorted(owners.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| `{family}` | `{owner}` | {count} |")

    lines.extend(
        [
            "",
            "## Highest-Signal Incorrect Rows",
            "",
            "| Artifact | Row | Gold | Prediction | Families | First failure |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in [row for row in rows if not row["purist_correct"]][:80]:
        lines.append(
            f"| `{row['artifact_name']}` | {row['source_row_index']} | "
            f"`{row['gold_label']}` | `{row['predicted_label']}` | "
            f"{row['hidden_families']} | `{row['first_failure_owner']}` |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _default_primary_layer(row: Mapping[str, Any]) -> str:
    score_layers = row.get("score_layers") or {}
    if "final_projected_label" in score_layers:
        return "final_projected_label"
    if "hybrid_adjudicator_with_adapters" in score_layers:
        return "hybrid_adjudicator_with_adapters"
    raise ValueError("Could not infer primary score layer from artifact row")


def _family_by_first_failure(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = {}
    for row in rows:
        owner = str(row["first_failure_owner"])
        for family in str(row["hidden_families"]).split(";"):
            counters.setdefault(family, Counter())[owner] += 1
    return {family: dict(counter) for family, counter in sorted(counters.items())}


def _belongs_to_atlas_hard_slice(row: Mapping[str, Any], slice_name: str) -> bool:
    if _bool_value(row.get("purist_correct")):
        return False
    owner = str(row.get("first_failure_owner") or "")
    families = set(_families(row))
    if slice_name == "candidate_generation_rescue":
        return owner == "candidate_generation"
    if slice_name == "candidate_generation_unknown_seizure_free_boundary":
        return owner == "candidate_generation" and bool(
            families & {"unknown_boundary", "seizure_free_duration"}
        )
    if slice_name == "projection_arbitration":
        return owner in {"projection", "final_projection"}
    if slice_name == "projection_unknown_seizure_free_arbitration":
        return owner in {"projection", "final_projection"} and bool(
            families & {"unknown_boundary", "seizure_free_duration", "current_vs_historical"}
        )
    raise ValueError(f"Unknown atlas hard slice: {slice_name}")


def _hard_slice_member(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_row_index": int(row["source_row_index"]),
        "artifact_name": row.get("artifact_name") or "",
        "split": row.get("split") or "",
        "primary_layer": row.get("primary_layer") or "",
        "gold_label": row.get("gold_label") or "",
        "predicted_label": row.get("predicted_label") or "",
        "hidden_families": _families(row),
        "first_failure_owner": row.get("first_failure_owner") or "",
        "first_failure_reason": row.get("first_failure_reason") or "",
        "evidence_exact": _optional_bool(row.get("evidence_exact")),
        "selected_operand_complete": _optional_bool(row.get("selected_operand_complete")),
        "deterministic_correct": _optional_bool(row.get("deterministic_correct")),
        "oracle_candidate_presence": _optional_bool(row.get("oracle_candidate_presence")),
        "oracle_graph_representability": _optional_bool(row.get("oracle_graph_representability")),
    }


def _families(row: Mapping[str, Any]) -> list[str]:
    value = row.get("hidden_families") or ""
    if isinstance(value, str):
        return [family for family in value.split(";") if family]
    return [str(family) for family in value if family]


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _optional_bool(value: Any) -> bool | str:
    if value in {None, ""}:
        return ""
    return _bool_value(value)


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _evidence_exact(row: Mapping[str, Any]) -> bool | str:
    diagnostics = row.get("diagnostics") or {}
    if "selected_evidence_exact" in diagnostics:
        return bool(diagnostics["selected_evidence_exact"])
    status = row.get("component_status") or {}
    if "evidence_exactness" in status:
        return status["evidence_exactness"] == "ok"
    return ""


def _selected_operand_complete(row: Mapping[str, Any]) -> bool | str:
    status = row.get("component_status") or {}
    if "selected_operand_completeness" in status:
        return status["selected_operand_completeness"] == "ok"
    return ""


def _diagnostic_bool(row: Mapping[str, Any], key: str) -> bool | str:
    diagnostics = row.get("diagnostics") or {}
    if key in diagnostics:
        return bool(diagnostics[key])
    return ""


def _selected_evidence_text(row: Mapping[str, Any]) -> str:
    evidence_summary = row.get("evidence_summary") or {}
    for key in ("selected_fact_evidence", "raw_model_selected_evidence"):
        if evidence_summary.get(key):
            return _text(evidence_summary[key])
    structured_record = row.get("structured_record") or {}
    selected_fact = structured_record.get("selected_fact") or {}
    if selected_fact.get("evidence"):
        return _text(selected_fact["evidence"])
    raw_answer = structured_record.get("raw_model_answer") or {}
    if raw_answer.get("selected_evidence"):
        return _text(raw_answer["selected_evidence"])
    structured_adjudicator = row.get("structured_adjudicator_record") or {}
    if structured_adjudicator.get("selected_evidence"):
        return _text(structured_adjudicator["selected_evidence"])
    component_inputs = row.get("component_inputs") or {}
    deterministic_top = component_inputs.get("deterministic_top") or {}
    return _text(deterministic_top.get("evidence"))


def _text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--primary-layer", default=None)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--csv", type=Path, default=DEFAULT_OUTPUT_CSV_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--hard-slice-json", type=Path, default=None)
    parser.add_argument("--hard-slice-report", type=Path, default=None)
    args = parser.parse_args(argv)

    rows = build_atlas_rows(args.artifacts, primary_layer=args.primary_layer, data_path=args.data)
    summary = summarize_atlas_rows(rows)
    write_atlas_csv(rows, args.csv)
    write_atlas_json(summary, args.json)
    write_atlas_report(rows, summary, args.report, csv_path=args.csv, json_path=args.json)
    if args.hard_slice_json or args.hard_slice_report:
        manifest = build_atlas_hard_slice_manifest(rows, source_atlas_csv=str(args.csv))
        if args.hard_slice_json:
            write_atlas_hard_slice_manifest(manifest, args.hard_slice_json)
        if args.hard_slice_report:
            write_atlas_hard_slice_report(manifest, args.hard_slice_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
