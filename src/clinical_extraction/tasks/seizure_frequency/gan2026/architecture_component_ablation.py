"""Cross-architecture component ablation tooling for Gan 2026 experiments."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    RuleGroup,
)

DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_architecture_component_ablation_validation_2026-06-01.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_architecture_component_ablation_validation_2026-06-01.md"
)


class Architecture(StrEnum):
    DETERMINISTIC_ONLY = "deterministic_only"
    LLM_THEN_DETERMINISTIC = "llm_then_deterministic"
    DETERMINISTIC_THEN_LLM = "deterministic_then_llm"


@dataclass(frozen=True)
class ConditionSpec:
    architecture: Architecture
    name: str
    component_role: str
    prediction_source: str
    components_enabled: tuple[str, ...]
    components_disabled: tuple[str, ...] = ()
    artifact_path: str | None = None


@dataclass(frozen=True)
class ConditionRow:
    source_row_index: int
    prediction_label: str | None
    gold_label: str
    purist_correct: bool
    pragmatic_correct: bool
    evidence_valid: bool | None = None
    parse_or_validation_issues: tuple[str, ...] = ()
    scorable: bool = True


@dataclass(frozen=True)
class ConditionResult:
    architecture: Architecture
    name: str
    component_role: str
    prediction_source: str
    components_enabled: tuple[str, ...]
    components_disabled: tuple[str, ...]
    artifact_path: str | None
    rows: tuple[ConditionRow, ...]


def deterministic_conditions(
    records: Sequence[GanFrequencyRecord],
) -> list[ConditionResult]:
    """Build deterministic-only baseline and one-rule-group-disabled conditions."""

    specs = [
        (
            "deterministic_all_rules",
            AblationConfig(),
            (),
        )
    ]
    for disabled_group in RuleGroup:
        enabled_groups = frozenset(group for group in RuleGroup if group is not disabled_group)
        specs.append(
            (
                f"deterministic_disable_{disabled_group.value}",
                AblationConfig(enabled_groups=enabled_groups),
                (disabled_group.value,),
            )
        )

    conditions: list[ConditionResult] = []
    for name, ablation_config, disabled in specs:
        pipeline = Gan2026PipelineV1(ablation_config=ablation_config)
        rows = []
        for record in records:
            result = pipeline.run(record)
            diagnostics = result.diagnostics
            final_selection = diagnostics["final_selection"]
            prediction_label = str(final_selection["final_label"])
            rows.append(
                _condition_row_from_label(
                    record,
                    prediction_label,
                    evidence_valid=bool(diagnostics.get("evidence_valid")),
                )
            )
        conditions.append(
            ConditionResult(
                architecture=Architecture.DETERMINISTIC_ONLY,
                name=name,
                component_role="deterministic_extractor",
                prediction_source="Gan2026PipelineV1",
                components_enabled=tuple(
                    group.value for group in RuleGroup if group.value not in disabled
                ),
                components_disabled=disabled,
                artifact_path=None,
                rows=tuple(rows),
            )
        )
    return conditions


def condition_from_llm_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    spec: ConditionSpec,
) -> ConditionResult:
    """Normalize saved LLM-first or LLM-structured JSONL rows into one condition."""

    condition_rows = []
    for row in rows:
        prediction_label = _llm_prediction_label(row)
        reference = row.get("reference") or {}
        comparison = row.get("comparison") or {}
        condition_rows.append(
            ConditionRow(
                source_row_index=int(row["source_row_index"]),
                prediction_label=prediction_label,
                gold_label=str(reference.get("gold_label", "")),
                purist_correct=bool(comparison.get("purist_correct")),
                pragmatic_correct=bool(comparison.get("pragmatic_correct")),
                evidence_valid=_optional_bool(row.get("evidence_valid")),
                parse_or_validation_issues=tuple(
                    str(error) for error in row.get("parse_errors") or ()
                ),
                scorable=prediction_label is not None and not _has_unscorable_issue(row),
            )
        )
    return _condition_from_spec(spec, condition_rows)


def condition_from_architecture2_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    artifact_path: str | None = None,
) -> tuple[ConditionResult, ConditionResult]:
    """Split Architecture 2 artifacts into generator-top and LLM-adjudicated conditions."""

    deterministic_rows = []
    adjudicator_rows = []
    for row in rows:
        scores = row.get("scores") or {}
        reference = row.get("reference") or {}
        diagnostics = row.get("deterministic_diagnostics") or {}
        deterministic_rows.append(
            _condition_row_from_score(
                row,
                scores.get("deterministic_top") or {},
                reference,
                evidence_valid=_optional_bool(diagnostics.get("evidence_valid")),
            )
        )
        adjudicator_rows.append(
            _condition_row_from_score(
                row,
                scores.get("adjudicator") or {},
                reference,
                evidence_valid=None,
                parse_errors=tuple(str(error) for error in row.get("parse_errors") or ()),
            )
        )
    return (
        ConditionResult(
            architecture=Architecture.DETERMINISTIC_THEN_LLM,
            name="deterministic_candidate_generator_top",
            component_role="candidate_generator_topline",
            prediction_source="Architecture 2 deterministic diagnostics",
            components_enabled=("deterministic candidate generator",),
            components_disabled=("LLM adjudicator",),
            artifact_path=artifact_path,
            rows=tuple(deterministic_rows),
        ),
        ConditionResult(
            architecture=Architecture.DETERMINISTIC_THEN_LLM,
            name="llm_adjudicator_final",
            component_role="prediction_bearing_adjudicator",
            prediction_source="Architecture 2 saved adjudicator output",
            components_enabled=("deterministic candidate generator", "LLM adjudicator"),
            components_disabled=(),
            artifact_path=artifact_path,
            rows=tuple(adjudicator_rows),
        ),
    )


def summarize_condition(condition: ConditionResult) -> dict[str, Any]:
    rows = condition.rows
    count = len(rows)
    purist_correct = sum(row.purist_correct for row in rows)
    pragmatic_correct = sum(row.pragmatic_correct for row in rows)
    evidence_rows = [row for row in rows if row.evidence_valid is not None]
    evidence_valid = sum(row.evidence_valid is True for row in evidence_rows)
    issues = sum(bool(row.parse_or_validation_issues) for row in rows)
    scorable = sum(row.scorable for row in rows)
    return {
        "rows": count,
        "scorable_rows": scorable,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / count, 4) if count else 0.0,
        "evidence_valid": evidence_valid,
        "evidence_rows": len(evidence_rows),
        "evidence_rate": round(evidence_valid / len(evidence_rows), 4) if evidence_rows else None,
        "parse_or_validation_issues": issues,
    }


def compare_condition_rows(
    baseline: ConditionResult,
    candidate: ConditionResult,
) -> dict[str, Any]:
    baseline_by_index = {row.source_row_index: row for row in baseline.rows}
    changed_labels = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    overlap = 0
    for row in candidate.rows:
        baseline_row = baseline_by_index.get(row.source_row_index)
        if baseline_row is None:
            continue
        overlap += 1
        if baseline_row.prediction_label != row.prediction_label:
            changed_labels += 1
        if not baseline_row.purist_correct and row.purist_correct:
            wrong_to_correct += 1
        if baseline_row.purist_correct and not row.purist_correct:
            correct_to_wrong += 1
    return {
        "baseline": baseline.name,
        "candidate": candidate.name,
        "overlap": overlap,
        "changed_labels": changed_labels,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
    }


def build_component_ablation_result(
    conditions: Sequence[ConditionResult],
    *,
    split: str,
    split_manifest: str = "gan2026_split_v1",
) -> dict[str, Any]:
    baselines = _architecture_baselines(conditions)
    return {
        "split": split,
        "split_manifest": split_manifest,
        "conditions": [_condition_payload(condition) for condition in conditions],
        "comparisons": [
            compare_condition_rows(baselines[condition.architecture], condition)
            for condition in conditions
            if baselines.get(condition.architecture) is not None
            and baselines[condition.architecture] is not condition
        ],
    }


def write_component_ablation_json(result: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_component_ablation_report(
    conditions: Sequence[ConditionResult],
    path: Path,
    *,
    split: str,
    split_manifest: str = "gan2026_split_v1",
) -> None:
    baselines = _architecture_baselines(conditions)
    lines = [
        "# Gan 2026 Architecture Component Ablation",
        "",
        "This is a development attribution artifact, not a held-out benchmark claim.",
        "",
        f"- Split: `{split}`",
        f"- Split manifest: `{split_manifest}`",
        "",
        "## Condition Summary",
        "",
        "| Architecture | Condition | Role | Rows | Purist | Pragmatic | Evidence | "
        "Issues | Changed | Improved | Regressed |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in conditions:
        summary = summarize_condition(condition)
        comparison = (
            compare_condition_rows(baselines[condition.architecture], condition)
            if baselines.get(condition.architecture) is not condition
            else None
        )
        evidence = (
            ""
            if summary["evidence_rate"] is None
            else f"{summary['evidence_rate']:.4f}"
        )
        lines.append(
            f"| {condition.architecture.value} | {condition.name} | "
            f"{condition.component_role} | {summary['rows']} | "
            f"{summary['purist_accuracy']:.4f} | {summary['pragmatic_accuracy']:.4f} | "
            f"{evidence} | {summary['parse_or_validation_issues']} | "
            f"{comparison['changed_labels'] if comparison else 0} | "
            f"{comparison['wrong_to_correct'] if comparison else 0} | "
            f"{comparison['correct_to_wrong'] if comparison else 0} |"
        )
    lines.extend(["", "## Component Map", ""])
    for condition in conditions:
        enabled = ", ".join(condition.components_enabled) or "none"
        disabled = ", ".join(condition.components_disabled) or "none"
        lines.extend(
            [
                f"### {condition.name}",
                "",
                f"- Architecture: `{condition.architecture.value}`",
                f"- Prediction source: `{condition.prediction_source}`",
                f"- Enabled: {enabled}",
                f"- Disabled: {disabled}",
                f"- Artifact: `{condition.artifact_path or 'generated in-process'}`",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a unified component-ablation report for deterministic-only, "
            "LLM-then-deterministic, and deterministic-then-LLM Gan 2026 architectures."
        )
    )
    parser.add_argument("--split", choices=("train", "validation"), default="validation")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--llm-jsonl", type=Path, action="append", default=[])
    parser.add_argument("--arch2-jsonl", type=Path, action="append", default=[])
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    records = load_records_for_split(args.split, args.data_path, args.manifest_path)
    if args.limit is not None:
        records = records[: args.limit]
    manifest = load_split_manifest(args.manifest_path)
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))

    conditions: list[ConditionResult] = deterministic_conditions(records)
    for llm_jsonl in args.llm_jsonl:
        conditions.append(
            condition_from_llm_rows(
                load_jsonl(llm_jsonl),
                spec=ConditionSpec(
                    architecture=Architecture.LLM_THEN_DETERMINISTIC,
                    name=f"llm_then_deterministic_{llm_jsonl.stem}",
                    component_role="llm_selection_with_named_deterministic_postprocessing",
                    prediction_source="saved LLM JSONL",
                    components_enabled=("LLM extractor/selector", "deterministic postprocessing"),
                    artifact_path=str(llm_jsonl),
                ),
            )
        )
    for arch2_jsonl in args.arch2_jsonl:
        conditions.extend(
            condition_from_architecture2_rows(
                load_jsonl(arch2_jsonl),
                artifact_path=str(arch2_jsonl),
            )
        )

    result = build_component_ablation_result(
        conditions,
        split=args.split,
        split_manifest=split_manifest,
    )
    write_component_ablation_json(result, args.json)
    write_component_ablation_report(
        conditions,
        args.markdown,
        split=args.split,
        split_manifest=split_manifest,
    )
    print(json.dumps({"conditions": len(conditions), "json": str(args.json)}, sort_keys=True))


def _condition_row_from_label(
    record: GanFrequencyRecord,
    label: str,
    *,
    evidence_valid: bool | None,
) -> ConditionRow:
    score = _score_label(label, record.gold_monthly_frequency)
    return ConditionRow(
        source_row_index=record.source_row_index,
        prediction_label=label,
        gold_label=record.gold_label,
        purist_correct=score["purist_correct"],
        pragmatic_correct=score["pragmatic_correct"],
        evidence_valid=evidence_valid,
        parse_or_validation_issues=tuple(score["errors"]),
        scorable=score["scorable"],
    )


def _condition_row_from_score(
    source_row: Mapping[str, Any],
    score: Mapping[str, Any],
    reference: Mapping[str, Any],
    *,
    evidence_valid: bool | None,
    parse_errors: tuple[str, ...] = (),
) -> ConditionRow:
    return ConditionRow(
        source_row_index=int(source_row["source_row_index"]),
        prediction_label=_optional_str(score.get("final_label")),
        gold_label=str(reference.get("gold_label", "")),
        purist_correct=bool(score.get("purist_correct")),
        pragmatic_correct=bool(score.get("pragmatic_correct")),
        evidence_valid=evidence_valid,
        parse_or_validation_issues=parse_errors,
        scorable=bool(score.get("scorable", score.get("final_label") is not None)),
    )


def _score_label(label: str, gold_monthly_frequency: float) -> dict[str, Any]:
    try:
        predicted = label_to_frequency_record(label)
    except ValueError as exc:
        return {
            "scorable": False,
            "purist_correct": False,
            "pragmatic_correct": False,
            "errors": [f"unscorable_final_label: {exc}"],
        }
    return {
        "scorable": True,
        "purist_correct": str(map_purist(predicted.monthly_frequency))
        == str(map_purist(gold_monthly_frequency)),
        "pragmatic_correct": str(map_pragmatic(predicted.monthly_frequency))
        == str(map_pragmatic(gold_monthly_frequency)),
        "errors": [],
    }


def _llm_prediction_label(row: Mapping[str, Any]) -> str | None:
    decision = row.get("decision_record")
    if isinstance(decision, Mapping):
        return _optional_str(decision.get("final_label"))
    structured = row.get("structured_record")
    if isinstance(structured, Mapping):
        selection = structured.get("selection")
        if isinstance(selection, Mapping):
            return _optional_str(selection.get("final_label"))
    return None


def _condition_from_spec(
    spec: ConditionSpec,
    rows: Sequence[ConditionRow],
) -> ConditionResult:
    return ConditionResult(
        architecture=spec.architecture,
        name=spec.name,
        component_role=spec.component_role,
        prediction_source=spec.prediction_source,
        components_enabled=spec.components_enabled,
        components_disabled=spec.components_disabled,
        artifact_path=spec.artifact_path,
        rows=tuple(rows),
    )


def _condition_payload(condition: ConditionResult) -> dict[str, Any]:
    return {
        "architecture": condition.architecture.value,
        "name": condition.name,
        "component_role": condition.component_role,
        "prediction_source": condition.prediction_source,
        "components_enabled": condition.components_enabled,
        "components_disabled": condition.components_disabled,
        "artifact_path": condition.artifact_path,
        "summary": summarize_condition(condition),
        "rows": [asdict(row) for row in condition.rows],
    }


def _architecture_baselines(
    conditions: Sequence[ConditionResult],
) -> dict[Architecture, ConditionResult]:
    baselines: dict[Architecture, ConditionResult] = {}
    for condition in conditions:
        baselines.setdefault(condition.architecture, condition)
    return baselines


def _has_unscorable_issue(row: Mapping[str, Any]) -> bool:
    return any(
        str(error).startswith("unscorable_final_label:")
        for error in row.get("parse_errors") or ()
    )


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


if __name__ == "__main__":
    main()
