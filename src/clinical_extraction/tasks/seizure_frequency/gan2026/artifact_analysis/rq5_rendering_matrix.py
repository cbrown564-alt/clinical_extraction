"""Build the Gan 2026 RQ5 fixed selected-state rendering matrix."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    StateGraphNode,
    build_state_graph,
    project_graph_to_gan,
)

DEFAULT_REPLAY_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
    "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_RQ4_MATRIX_PATH = Path(
    "experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl"
)
DEFAULT_PANEL_PATH = Path(
    "experiments/gan2026_component_projection_followup_panel_2026-06-04.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq5_deterministic_rendering_matrix_2026-06-04.md"
)

ACD_FIXTURES: tuple[dict[str, str], ...] = (
    {
        "acd_id": "ACD-003",
        "source_row_index": "1707",
        "note_text": "The diary records several focal seizures last month.",
        "expected_label": "multiple per month",
        "expectation": "vague_count_with_denominator",
    },
    {
        "acd_id": "ACD-003",
        "source_row_index": "0",
        "note_text": "Current seizure burden is occasional events.",
        "expected_label": "unknown",
        "expectation": "vague_count_without_denominator",
    },
    {
        "acd_id": "ACD-004",
        "source_row_index": "3356",
        "note_text": "Seizures happen when perimenstrual only (days -2 to +2).",
        "expected_label": "unknown",
        "expectation": "conditional_only_trigger",
    },
    {
        "acd_id": "ACD-005",
        "source_row_index": "3528",
        "note_text": "Frequency increased by about 50% after dose reduction.",
        "expected_label": "unknown",
        "expectation": "relative_only_trend",
    },
    {
        "acd_id": "ACD-006",
        "source_row_index": "4368",
        "note_text": "Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
        "expected_label": "5 per 2 month",
        "expectation": "diary_date_listing",
    },
    {
        "acd_id": "ACD-007",
        "source_row_index": "3137",
        "note_text": (
            "There have been no definite seizure events. Two recent Emergency "
            "Department presentations were primarily for light-headedness and anxiety."
        ),
        "expected_label": "seizure free for multiple month",
        "expectation": "non_epileptic_triage",
    },
    {
        "acd_id": "ACD-008",
        "source_row_index": "2748",
        "note_text": (
            "Only seven focal impaired-awareness seizures reported so far this year. "
            "At present, his typical pattern is a focal seizure monthly."
        ),
        "expected_label": "1 per month",
        "expectation": "summary_rate_over_average",
    },
    {
        "acd_id": "ACD-009",
        "source_row_index": "1695",
        "note_text": (
            "There were a handful of short focal events during the previous month. "
            "In the current month to date, no events have been recorded."
        ),
        "expected_label": "multiple per month",
        "expectation": "previous_month_over_current_zero",
    },
    {
        "acd_id": "ACD-010",
        "source_row_index": "1363",
        "note_text": (
            "Yesterday he experienced three tonic-clonic seizures yesterday. "
            "He describes interictal brief auras occurring approximately once or "
            "twice per week."
        ),
        "expected_label": "3 per day",
        "expectation": "major_relapse_priority",
    },
)


def build_rendering_matrix(
    *,
    replay_path: Path = DEFAULT_REPLAY_PATH,
    rq4_matrix_path: Path = DEFAULT_RQ4_MATRIX_PATH,
    panel_path: Path = DEFAULT_PANEL_PATH,
    include_replay_limit: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    context = _load_context(rq4_matrix_path=rq4_matrix_path, panel_path=panel_path)
    rows: list[dict[str, Any]] = []
    replay_rows = load_jsonl_rows(replay_path)
    if include_replay_limit is not None:
        replay_rows = replay_rows[:include_replay_limit]
    for source_row in replay_rows:
        rows.extend(_rows_from_replay_row(source_row, replay_path, context))
    for fixture in ACD_FIXTURES:
        rows.extend(_rows_from_acd_fixture(fixture))
    rows.sort(
        key=lambda row: (
            row["claim_boundary"],
            int(row["source_row_index"]),
            row["compiler_rendering_variant"],
            row.get("acd_id") or "",
        )
    )
    return rows, summarize_rendering_rows(rows)


def summarize_rendering_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_variant: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_boundary: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_acd: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    drift_families: Counter[str] = Counter()
    first_failure: Counter[str] = Counter()
    for row in rows:
        by_variant[str(row["compiler_rendering_variant"])].append(row)
        by_boundary[str(row["claim_boundary"])].append(row)
        by_acd[str(row.get("acd_id") or "none")].append(row)
        if row.get("semantic_drift"):
            drift_families[str(row.get("semantic_drift_family") or "unclassified")] += 1
        first_failure[str(row.get("first_failure_owner_after_rendering") or "unknown")] += 1

    return {
        "artifact_kind": "gan2026_rq5_deterministic_rendering_matrix",
        "row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_variant": {
            variant: _summary_for_rows(variant_rows)
            for variant, variant_rows in sorted(by_variant.items())
        },
        "by_claim_boundary": {
            boundary: _summary_for_rows(boundary_rows)
            for boundary, boundary_rows in sorted(by_boundary.items())
        },
        "by_acd_id": {
            acd_id: _summary_for_rows(acd_rows)
            for acd_id, acd_rows in sorted(by_acd.items())
        },
        "semantic_drift_families": dict(sorted(drift_families.items())),
        "first_failure_owner_after_rendering": dict(sorted(first_failure.items())),
    }


def write_matrix_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_matrix_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ5 Fixed Selected-State Rendering Matrix",
        "",
        (
            "Validation-development artifact for deterministic compilation/rendering "
            "over fixed selected states and explicit ACD projection-policy decisions. "
            "No model calls or locked-holdout rows are used."
        ),
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Matrix rows: {metadata['row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        "",
        "## Variant Summary",
        "",
        (
            "| Variant | Rows | Parse valid | Exact label | Purist correct | "
            "Pragmatic correct | Semantic drift | Evidence retained | Source ids retained |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, summary in metadata["by_variant"].items():
        lines.append(
            (
                "| {variant} | {rows} | {parse_valid:.3f} | {exact:.3f} | "
                "{purist:.3f} | {pragmatic:.3f} | {drift} | {evidence:.3f} | "
                "{source_ids:.3f} |"
            ).format(
                variant=variant,
                rows=summary["rows"],
                parse_valid=summary["parse_valid_rate"],
                exact=summary["exact_label_match_rate"],
                purist=summary["purist_correct_rate"],
                pragmatic=summary["pragmatic_correct_rate"],
                drift=summary["semantic_drift_count"],
                evidence=summary["exact_evidence_retained_rate"],
                source_ids=summary["source_id_retained_rate"],
            )
        )

    lines.extend(
        [
            "",
            "## ACD Summary",
            "",
            "| ACD | Rows | Exact label | Semantic drift | Evidence retained |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for acd_id, summary in metadata["by_acd_id"].items():
        lines.append(
            (
                "| {acd_id} | {rows} | {exact:.3f} | {drift} | {evidence:.3f} |"
            ).format(
                acd_id=acd_id,
                rows=summary["rows"],
                exact=summary["exact_label_match_rate"],
                drift=summary["semantic_drift_count"],
                evidence=summary["exact_evidence_retained_rate"],
            )
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "Rows marked `materialized_replay` come from saved validation replay "
                "state-graph projection metadata. Rows marked `focused_fixture` are "
                "small source-near ACD fixtures that freeze the selected state and "
                "policy decision. ACD-off rows are ablations only; they are included "
                "to measure dependence on explicit policy, not as candidate policies."
            ),
            "",
            "## Instrumentation Gaps",
            "",
        ]
    )
    gap_rows = [row for row in rows if row["claim_boundary"] == "diagnostic_only"]
    if gap_rows:
        lines.append(
            f"- {len(gap_rows)} rows lack enough selected-state metadata for a "
            "materialized compiler/rendering claim."
        )
    else:
        lines.append(
            "- No diagnostic-only rows were emitted; all rows are either materialized "
            "saved replay or focused ACD fixtures."
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _rows_from_replay_row(
    source_row: Mapping[str, Any],
    replay_path: Path,
    context: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    component_inputs = source_row.get("component_inputs") or {}
    projection = component_inputs.get("state_graph_projection") or {}
    nodes = component_inputs.get("state_graph_nodes") or []
    selected_node_ids = tuple(projection.get("selected_node_ids") or ())
    selected_nodes = [
        node for node in nodes if str(node.get("node_id")) in set(selected_node_ids)
    ]
    if not projection:
        return []

    source_row_index = int(source_row["source_row_index"])
    reference = source_row.get("reference") or {}
    baseline = (component_inputs.get("deterministic_top") or {}).get("final_label") or ""
    gold_label = reference.get("gold_normalized_label") or reference.get("gold_label") or ""
    fixed_label = projection.get("final_label") or ""
    selected_evidence = projection.get("evidence") or ""
    source_ids = [f"graph:{node_id}" for node_id in selected_node_ids]
    ctx = context.get(source_row_index, {})
    base = {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "clinical_subproblem": "deterministic_compilation_rendering",
        "source_row_index": source_row_index,
        "split": source_row.get("split") or "validation",
        "split_manifest": source_row.get("split_manifest") or "gan2026_split_v1",
        "source_artifact": replay_path.as_posix(),
        "surface": "validation750_saved_state_graph_projection",
        "row_role": ctx.get("panel_role") or "materialized_state_graph_projection",
        "hidden_families": ctx.get("hidden_families") or [],
        "gold_label": gold_label,
        "gold_label_kind": reference.get("gold_label_kind") or "",
        "deterministic_baseline_label": baseline,
        "deterministic_baseline_correct": (source_row.get("diagnostics") or {}).get(
            "deterministic_correct"
        ),
        "fixed_selected_state_ids": list(selected_node_ids),
        "fixed_selected_state_kind": _join_unique(node.get("kind") for node in selected_nodes),
        "fixed_selected_state_semantic_kind": _join_unique(
            node.get("semantic_kind") for node in selected_nodes
        ),
        "fixed_selected_state_temporality": _join_unique(
            node.get("temporality") for node in selected_nodes
        ),
        "fixed_selected_state_assertion_status": _join_unique(
            node.get("assertion_status") for node in selected_nodes
        ),
        "fixed_selected_state_certainty": _join_unique(
            node.get("certainty") for node in selected_nodes
        ),
        "fixed_selected_state_applies_to": _join_unique(
            node.get("applies_to") for node in selected_nodes
        ),
        "fixed_typed_operands": _typed_operands_from_nodes(selected_nodes),
        "selected_evidence": selected_evidence,
        "selected_source_ids": source_ids,
        "active_projection_policy": projection.get("projection_policy") or "",
        "acd_id": _acd_id_from_nodes(selected_nodes),
        "projection_rationale": projection.get("rationale") or "",
        "first_failure_owner_from_source": ctx.get("first_failure_owner") or "",
        "claim_boundary": "materialized_replay",
    }
    return [
        _rendered_row(
            base,
            variant="current_production",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=False,
        ),
        _rendered_row(
            base,
            variant="strict_format",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=False,
            require_source_ids=False,
        ),
        _rendered_row(
            base,
            variant="evidence_preserving",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=True,
        ),
    ]


def _rows_from_acd_fixture(fixture: Mapping[str, str]) -> list[dict[str, Any]]:
    graph = build_state_graph(
        fixture["note_text"],
        source_row_index=int(fixture["source_row_index"]),
    )
    projection = project_graph_to_gan(graph)
    selected_nodes = [
        node for node in graph.nodes if node.node_id in set(projection.selected_node_ids)
    ]
    base = {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "clinical_subproblem": "deterministic_compilation_rendering",
        "source_row_index": int(fixture["source_row_index"]),
        "split": "validation_fixture",
        "split_manifest": "gan2026_split_v1",
        "source_artifact": "tests/test_gan2026_state_graph.py",
        "surface": "focused_acd_policy_fixture",
        "row_role": fixture["expectation"],
        "hidden_families": [_hidden_family_for_acd(fixture["acd_id"])],
        "gold_label": fixture["expected_label"],
        "gold_label_kind": label_to_frequency_record(fixture["expected_label"]).kind.value,
        "deterministic_baseline_label": "",
        "deterministic_baseline_correct": None,
        "fixed_selected_state_ids": list(projection.selected_node_ids),
        "fixed_selected_state_kind": _join_unique(node.kind.value for node in selected_nodes),
        "fixed_selected_state_semantic_kind": _join_unique(
            node.semantic_kind.value for node in selected_nodes
        ),
        "fixed_selected_state_temporality": _join_unique(
            node.temporality for node in selected_nodes
        ),
        "fixed_selected_state_assertion_status": _join_unique(
            node.assertion_status for node in selected_nodes
        ),
        "fixed_selected_state_certainty": _join_unique(
            node.certainty for node in selected_nodes
        ),
        "fixed_selected_state_applies_to": _join_unique(
            node.applies_to for node in selected_nodes
        ),
        "fixed_typed_operands": _typed_operands_from_node_models(selected_nodes),
        "selected_evidence": projection.evidence,
        "selected_source_ids": [f"graph:{node_id}" for node_id in projection.selected_node_ids],
        "active_projection_policy": projection.projection_policy,
        "acd_id": fixture["acd_id"],
        "projection_rationale": projection.rationale,
        "first_failure_owner_from_source": "projection_policy",
        "claim_boundary": "focused_fixture",
    }
    fixed_label = projection.final_label
    gold_label = fixture["expected_label"]
    return [
        _rendered_row(
            base,
            variant="current_production",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=True,
        ),
        _rendered_row(
            base,
            variant="acd_aware",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=True,
        ),
        _rendered_row(
            base,
            variant="acd_off_ablation",
            rendered_label=_acd_off_rendered_label(
                acd_id=fixture["acd_id"],
                acd_aware_label=fixed_label,
            ),
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=True,
        ),
        _rendered_row(
            base,
            variant="strict_format",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=False,
            require_source_ids=False,
        ),
        _rendered_row(
            base,
            variant="evidence_preserving",
            rendered_label=fixed_label,
            fixed_projection_label=fixed_label,
            gold_label=gold_label,
            require_evidence=True,
            require_source_ids=True,
        ),
    ]


def _rendered_row(
    base: Mapping[str, Any],
    *,
    variant: str,
    rendered_label: str,
    fixed_projection_label: str,
    gold_label: str,
    require_evidence: bool,
    require_source_ids: bool,
) -> dict[str, Any]:
    parse = _parse_label(rendered_label)
    gold_parse = _parse_label(gold_label)
    exact_evidence_retained = bool(base.get("selected_evidence")) if require_evidence else True
    source_id_retained = bool(base.get("selected_source_ids")) if require_source_ids else True
    semantic_drift = rendered_label != fixed_projection_label
    purist_correct = None
    pragmatic_correct = None
    if parse["parse_valid"] and gold_parse["parse_valid"]:
        purist_correct = parse["purist_category"] == gold_parse["purist_category"]
        pragmatic_correct = parse["pragmatic_category"] == gold_parse["pragmatic_category"]
    row = dict(base)
    row.update(
        {
            "compiler_rendering_variant": variant,
            "fixed_projection_label": fixed_projection_label,
            "rendered_label": rendered_label,
            "rendered_label_kind": parse["label_kind"],
            "normalized_scorer_label": parse["normalized_label"],
            "parse_valid": parse["parse_valid"],
            "parse_error": parse["parse_error"],
            "exact_label_match": rendered_label == gold_label,
            "purist_correct": purist_correct,
            "pragmatic_correct": pragmatic_correct,
            "changed_from_baseline": bool(
                base.get("deterministic_baseline_label")
                and rendered_label != base.get("deterministic_baseline_label")
            ),
            "wrong_to_correct": _wrong_to_correct(base, purist_correct),
            "correct_to_wrong": _correct_to_wrong(base, purist_correct),
            "semantic_drift": semantic_drift,
            "semantic_drift_family": _semantic_drift_family(
                semantic_drift=semantic_drift,
                rendered_label=rendered_label,
                fixed_projection_label=fixed_projection_label,
                parse_valid=parse["parse_valid"],
            ),
            "benchmark_format_leakage": not parse["parse_valid"],
            "exact_evidence_retained": exact_evidence_retained,
            "source_id_retained": source_id_retained,
            "operand_loss": False,
            "operand_loss_family": "",
            "first_failure_owner_after_rendering": _first_failure_owner_after_rendering(
                parse_valid=parse["parse_valid"],
                semantic_drift=semantic_drift,
                exact_evidence_retained=exact_evidence_retained,
                source_id_retained=source_id_retained,
                source_owner=str(base.get("first_failure_owner_from_source") or ""),
            ),
        }
    )
    return row


def _load_context(
    *,
    rq4_matrix_path: Path,
    panel_path: Path,
) -> dict[int, dict[str, Any]]:
    context: dict[int, dict[str, Any]] = {}
    for path in (rq4_matrix_path, panel_path):
        if not path.exists():
            continue
        for row in load_jsonl_rows(path):
            source_index = int(row["source_row_index"])
            current = context.setdefault(source_index, {})
            if not current.get("hidden_families") and row.get("hidden_families"):
                current["hidden_families"] = row["hidden_families"]
            for key in ("panel_role", "first_failure_owner"):
                if not current.get(key) and row.get(key):
                    current[key] = row[key]
    return context


def _parse_label(label: str) -> dict[str, Any]:
    try:
        record = label_to_frequency_record(label)
    except ValueError as exc:
        return {
            "parse_valid": False,
            "parse_error": str(exc),
            "normalized_label": label,
            "label_kind": "",
            "monthly_frequency": None,
            "purist_category": "",
            "pragmatic_category": "",
        }
    return {
        "parse_valid": True,
        "parse_error": "",
        "normalized_label": record.normalized_label,
        "label_kind": record.kind.value,
        "monthly_frequency": record.monthly_frequency,
        "purist_category": str(map_purist(record.monthly_frequency)),
        "pragmatic_category": str(map_pragmatic(record.monthly_frequency)),
    }


def _acd_off_rendered_label(*, acd_id: str, acd_aware_label: str) -> str:
    if acd_id in {"ACD-003", "ACD-004", "ACD-005"} and acd_aware_label == "unknown":
        return acd_aware_label
    return "unknown"


def _typed_operands_from_nodes(nodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rule_ids = [node.get("rule_id") for node in nodes if node.get("rule_id")]
    labels = [node.get("normalized_label") for node in nodes if node.get("normalized_label")]
    evidence = [node.get("evidence") for node in nodes if node.get("evidence")]
    return {
        "rule_ids": rule_ids,
        "normalized_labels": labels,
        "evidence": evidence,
        "monthly_frequency": [
            node.get("monthly_frequency")
            for node in nodes
            if node.get("monthly_frequency") is not None
        ],
        "uncertainty_flags": [],
    }


def _typed_operands_from_node_models(nodes: Sequence[StateGraphNode]) -> dict[str, Any]:
    return {
        "rule_ids": [node.rule_id for node in nodes],
        "normalized_labels": [node.normalized_label for node in nodes],
        "evidence": [node.evidence.text for node in nodes],
        "monthly_frequency": [node.monthly_frequency for node in nodes],
        "uncertainty_flags": [
            error for node in nodes for error in tuple(node.graph_errors or ())
        ],
    }


def _acd_id_from_nodes(nodes: Sequence[Mapping[str, Any]]) -> str:
    for node in nodes:
        rule_id = str(node.get("rule_id") or "")
        acd = _acd_id_from_rule(rule_id)
        if acd:
            return acd
    return ""


def _acd_id_from_rule(rule_id: str) -> str:
    if "acd_003" in rule_id:
        return "ACD-003"
    if "acd_004" in rule_id:
        return "ACD-004"
    if "acd_005" in rule_id:
        return "ACD-005"
    if rule_id == "diary.date_list":
        return "ACD-006"
    if rule_id == "seizure_free.no_definite_events":
        return "ACD-007"
    if "acd_008" in rule_id:
        return "ACD-008"
    if "acd_009" in rule_id:
        return "ACD-009"
    return ""


def _hidden_family_for_acd(acd_id: str) -> str:
    return {
        "ACD-003": "benchmark_format_convention",
        "ACD-004": "uncertainty_or_ambiguity",
        "ACD-005": "temporal_conflict",
        "ACD-006": "diary_or_log_aggregation",
        "ACD-007": "seizure_free_duration",
        "ACD-008": "current_vs_historical",
        "ACD-009": "current_vs_historical",
        "ACD-010": "competing_semiologies",
    }.get(acd_id, "unmapped")


def _summary_for_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "parse_valid_rate": _rate(row.get("parse_valid") for row in rows),
        "exact_label_match_rate": _rate(row.get("exact_label_match") for row in rows),
        "purist_correct_rate": _rate(row.get("purist_correct") for row in rows),
        "pragmatic_correct_rate": _rate(row.get("pragmatic_correct") for row in rows),
        "semantic_drift_count": sum(bool(row.get("semantic_drift")) for row in rows),
        "benchmark_format_leakage_count": sum(
            bool(row.get("benchmark_format_leakage")) for row in rows
        ),
        "exact_evidence_retained_rate": _rate(
            row.get("exact_evidence_retained") for row in rows
        ),
        "source_id_retained_rate": _rate(row.get("source_id_retained") for row in rows),
        "wrong_to_correct": sum(bool(row.get("wrong_to_correct")) for row in rows),
        "correct_to_wrong": sum(bool(row.get("correct_to_wrong")) for row in rows),
    }


def _rate(values: Sequence[Any]) -> float:
    bools = [bool(value) for value in values if value is not None]
    if not bools:
        return 0.0
    return round(sum(bools) / len(bools), 4)


def _wrong_to_correct(base: Mapping[str, Any], purist_correct: bool | None) -> bool:
    baseline = base.get("deterministic_baseline_correct")
    return bool(baseline is False and purist_correct is True)


def _correct_to_wrong(base: Mapping[str, Any], purist_correct: bool | None) -> bool:
    baseline = base.get("deterministic_baseline_correct")
    return bool(baseline is True and purist_correct is False)


def _semantic_drift_family(
    *,
    semantic_drift: bool,
    rendered_label: str,
    fixed_projection_label: str,
    parse_valid: bool,
) -> str:
    if not parse_valid:
        return "benchmark_format_leakage"
    if not semantic_drift:
        return ""
    if rendered_label in {"unknown", "no seizure frequency reference"}:
        return "collapsed_to_uncertainty_or_no_reference"
    if fixed_projection_label in {"unknown", "no seizure frequency reference"}:
        return "invented_frequency_from_uncertain_state"
    return "changed_fixed_state_label"


def _first_failure_owner_after_rendering(
    *,
    parse_valid: bool,
    semantic_drift: bool,
    exact_evidence_retained: bool,
    source_id_retained: bool,
    source_owner: str,
) -> str:
    if not parse_valid or semantic_drift or not exact_evidence_retained or not source_id_retained:
        return "compiler_renderer"
    if source_owner:
        return source_owner
    return "none_observed"


def _join_unique(values: Any) -> str:
    unique = []
    for value in values:
        if value is None:
            continue
        text = str(value)
        if text and text not in unique:
            unique.append(text)
    return ";".join(unique)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-path", type=Path, default=DEFAULT_REPLAY_PATH)
    parser.add_argument("--rq4-matrix-path", type=Path, default=DEFAULT_RQ4_MATRIX_PATH)
    parser.add_argument("--panel-path", type=Path, default=DEFAULT_PANEL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--include-replay-limit", type=int)
    args = parser.parse_args(argv)

    rows, metadata = build_rendering_matrix(
        replay_path=args.replay_path,
        rq4_matrix_path=args.rq4_matrix_path,
        panel_path=args.panel_path,
        include_replay_limit=args.include_replay_limit,
    )
    write_matrix_jsonl(rows, args.jsonl_path)
    write_matrix_report(rows, metadata, args.report_path, jsonl_path=args.jsonl_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
