"""Score rendered ClinicalAssessment project/render artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    SCORING_POLICY_ID,
    SCORING_SCHEMA_VERSION,
    RenderedLabelScore,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)

DEFAULT_PROJECT_RENDER_JSONL_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_render_validation250_v1.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_score_validation250_v0.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_score_validation250_v0.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_score_validation250_v0.md"
)


def build_scoring_artifact(
    project_render_rows: Sequence[Mapping[str, Any]],
    *,
    gold_records: Mapping[int, GanFrequencyRecord],
    project_render_artifact_path: str = str(DEFAULT_PROJECT_RENDER_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [build_scoring_row(row, gold_records=gold_records) for row in project_render_rows]
    return rows, summarize_rows(
        rows,
        project_render_artifact_path=project_render_artifact_path,
    )


def build_scoring_row(
    project_render_row: Mapping[str, Any],
    *,
    gold_records: Mapping[int, GanFrequencyRecord],
) -> dict[str, Any]:
    source_row_index = int(project_render_row["source_row_index"])
    final_rendered = project_render_row.get("final_rendered_label") or {}
    rendered_label = final_rendered.get("rendered_label")
    gold_record = gold_records.get(source_row_index)
    score = score_rendered_label(
        source_row_index=source_row_index,
        rendered_label=str(rendered_label) if rendered_label is not None else None,
        gold_record=gold_record,
    )
    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_score_row",
        "source_row_index": source_row_index,
        "split": project_render_row.get("split", "validation"),
        "split_manifest": project_render_row.get("split_manifest", "gan2026_split_v1"),
        "schema_version": SCORING_SCHEMA_VERSION,
        "scoring_policy_id": SCORING_POLICY_ID,
        "claim_boundary": (
            "score-policy artifact over saved validation250 project/render rows; "
            "uses existing Gan parser and category mappers; not a benchmark-comparable claim"
        ),
        "source_artifacts": {
            "projection_policy_id": project_render_row.get("projection_policy_id"),
            "render_policy_id": project_render_row.get("render_policy_id"),
            "projection_render_schema_version": project_render_row.get("schema_version"),
        },
        "projection_decision": project_render_row.get("projection_decision"),
        "final_rendered_label": project_render_row.get("final_rendered_label"),
        "score": score.model_dump(),
    }


def score_rendered_label(
    *,
    source_row_index: int,
    rendered_label: str | None,
    gold_record: GanFrequencyRecord | None,
) -> RenderedLabelScore:
    if gold_record is None:
        return RenderedLabelScore(
            source_row_index=source_row_index,
            component_owner="rendered_label_scorer",
            score_status="not_scored_missing_gold_record",
            rendered_label=rendered_label,
            gold_label=None,
            score_issues=["gold_record_missing"],
        )
    gold_purist = str(map_purist(gold_record.gold_monthly_frequency))
    gold_pragmatic = str(map_pragmatic(gold_record.gold_monthly_frequency))
    if rendered_label is None:
        return RenderedLabelScore(
            source_row_index=source_row_index,
            component_owner="rendered_label_scorer",
            score_status="not_scored_null_rendered_label",
            rendered_label=None,
            gold_label=gold_record.gold_label,
            gold_normalized_label=gold_record.gold_normalized_label,
            gold_monthly_frequency=gold_record.gold_monthly_frequency,
            gold_purist_category=gold_purist,
            gold_pragmatic_category=gold_pragmatic,
            score_issues=["rendered_label_null"],
        )
    try:
        predicted = label_to_frequency_record(rendered_label)
    except ValueError as exc:
        return RenderedLabelScore(
            source_row_index=source_row_index,
            component_owner="rendered_label_scorer",
            score_status="not_scored_unparseable_rendered_label",
            rendered_label=rendered_label,
            gold_label=gold_record.gold_label,
            gold_normalized_label=gold_record.gold_normalized_label,
            gold_monthly_frequency=gold_record.gold_monthly_frequency,
            gold_purist_category=gold_purist,
            gold_pragmatic_category=gold_pragmatic,
            score_issues=[f"rendered_label_unparseable:{exc}"],
        )
    predicted_purist = str(map_purist(predicted.monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
    return RenderedLabelScore(
        source_row_index=source_row_index,
        component_owner="rendered_label_scorer",
        score_status="scored",
        rendered_label=rendered_label,
        gold_label=gold_record.gold_label,
        predicted_normalized_label=predicted.normalized_label,
        gold_normalized_label=gold_record.gold_normalized_label,
        predicted_monthly_frequency=predicted.monthly_frequency,
        gold_monthly_frequency=gold_record.gold_monthly_frequency,
        predicted_purist_category=predicted_purist,
        gold_purist_category=gold_purist,
        predicted_pragmatic_category=predicted_pragmatic,
        gold_pragmatic_category=gold_pragmatic,
        exact_normalized_label_match=(
            predicted.normalized_label == gold_record.gold_normalized_label
        ),
        purist_correct=predicted_purist == gold_purist,
        pragmatic_correct=predicted_pragmatic == gold_pragmatic,
    )


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    project_render_artifact_path: str = str(DEFAULT_PROJECT_RENDER_JSONL_PATH),
) -> dict[str, Any]:
    scores = [row["score"] for row in rows]
    scored = [score for score in scores if score["score_status"] == "scored"]
    status_counts = Counter(str(score["score_status"]) for score in scores)
    issue_counts = Counter(
        issue for score in scores for issue in list(score.get("score_issues") or [])
    )
    purist_correct = sum(score.get("purist_correct") is True for score in scored)
    pragmatic_correct = sum(score.get("pragmatic_correct") is True for score in scored)
    exact = sum(score.get("exact_normalized_label_match") is True for score in scored)
    surface_label = f"validation{len(rows)}"
    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_score",
        "schema_version": SCORING_SCHEMA_VERSION,
        "scoring_policy_id": SCORING_POLICY_ID,
        "project_render_artifact_path": project_render_artifact_path,
        "row_count": len(rows),
        "claim_boundary": (
            f"{surface_label} mechanics scoring over saved project/render rows only. "
            "Scoring reuses the existing label parser plus purist/pragmatic category "
            "mappers and is not a benchmark-comparable promotion claim."
        ),
        "summary": {
            "scored_rows": len(scored),
            "non_scored_rows": len(rows) - len(scored),
            "purist_correct": purist_correct,
            "purist_accuracy_on_scored": _rate(purist_correct, len(scored)),
            "pragmatic_correct": pragmatic_correct,
            "pragmatic_accuracy_on_scored": _rate(pragmatic_correct, len(scored)),
            "exact_normalized_label_matches": exact,
            "exact_normalized_label_match_rate_on_scored": _rate(exact, len(scored)),
            "score_status_counts": dict(sorted(status_counts.items())),
            "score_issue_counts": dict(sorted(issue_counts.items())),
            "non_scored_source_row_indices": [
                int(row["source_row_index"])
                for row in rows
                if row["score"]["score_status"] != "scored"
            ][:25],
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 ClinicalAssessment Projection Score",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Scoring JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Project/render source: `{metadata['project_render_artifact_path']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Scored rows: {summary['scored_rows']}",
        f"- Non-scored rows: {summary['non_scored_rows']}",
        f"- Purist correct on scored rows: {summary['purist_correct']} "
        f"({summary['purist_accuracy_on_scored']})",
        f"- Pragmatic correct on scored rows: {summary['pragmatic_correct']} "
        f"({summary['pragmatic_accuracy_on_scored']})",
        f"- Exact normalized-label matches on scored rows: "
        f"{summary['exact_normalized_label_matches']} "
        f"({summary['exact_normalized_label_match_rate_on_scored']})",
        "",
        "## Score Statuses",
        "",
    ]
    for status, count in summary["score_status_counts"].items():
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Score Issues", ""])
    if not summary["score_issue_counts"]:
        lines.append("- None.")
    for issue, count in summary["score_issue_counts"].items():
        lines.append(f"- `{issue}`: {count}")
    lines.extend(["", "## Non-Scored Rows", ""])
    if not summary["non_scored_source_row_indices"]:
        lines.append("- None.")
    else:
        lines.append(
            "- First rows: " + ", ".join(str(i) for i in summary["non_scored_source_row_indices"])
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-render-jsonl",
        type=Path,
        default=DEFAULT_PROJECT_RENDER_JSONL_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    validation_records = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows, metadata = build_scoring_artifact(
        load_jsonl_rows(args.project_render_jsonl),
        gold_records=validation_records,
        project_render_artifact_path=str(args.project_render_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
