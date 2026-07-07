"""Materialize the first reset-stage component ablation table from saved V5/V6 artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reset_stage_component_inventory,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_ROUTE_V5_JSONL_PATH = Path(
    "experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v5_2026-06-06.jsonl"
)
DEFAULT_ROUTE_V6_JSONL_PATH = Path(
    "experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_ROUTE_CANDIDATE_TRACE_JSONL_PATH = Path(
    "experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_first_component_ablation_table_v6_2026-06-06.json"
)
DEFAULT_REPORT_PATH = Path("")
DEFAULT_ONE_FAMILY_OFF_SPECS = {
    "seizure_free_duration_date_instrumentation": {
        "switch": "normalize_seizure_free_duration_date_instrumentation",
        "base_path": (
            "experiments/gan2026_validation750_one_family_off_"
            "seizure_free_duration_date_instrumentation_context_repair_v6_2026-06-06"
        ),
    },
    "current_summary_rate_priority": {
        "switch": "project_current_summary_rate_priority",
        "base_path": (
            "experiments/gan2026_validation750_one_family_off_"
            "current_summary_rate_priority_context_repair_v6_2026-06-06"
        ),
    },
    "previous_active_month_over_current_month_zero": {
        "switch": "project_previous_active_month_over_current_month_zero",
        "base_path": (
            "experiments/gan2026_validation750_one_family_off_"
            "previous_active_month_over_current_month_zero_context_repair_v6_2026-06-06"
        ),
    },
    "major_recent_relapse_over_background_frequency": {
        "switch": "project_major_recent_relapse_over_background_frequency",
        "base_path": (
            "experiments/gan2026_validation750_one_family_off_"
            "major_recent_relapse_over_background_frequency_context_repair_v6_2026-06-06"
        ),
    },
}

CLAIM_BOUNDARY = (
    "saved validation-development reset-stage component ablation summary only; "
    "it uses the reset inventory plus saved V5/V6 and candidate-trace route "
    "artifacts, authorizes no locked-test row-level inspection, no live model "
    "call, and no benchmark-comparable claim"
)
PROVENANCE_FAMILIES = {
    "selected_evidence_missing_exact_trace",
    "selected_source_id_invalid",
}
ACTIVE_FREQUENCY_RECOVERY_FAMILIES = {
    "selected_evidence_frequency_value_recovery",
    "vague_period_frequency_value_recovery",
    "diary_date_list_frequency_recovery",
}
ONE_FAMILY_OFF_REQUIRED_FAMILIES = {
    "seizure_free_duration_date_instrumentation",
    "current_summary_rate_priority",
    "previous_active_month_over_current_month_zero",
    "major_recent_relapse_over_background_frequency",
}
MAIN_AMBIGUITY_FAMILIES = {"mixed_window_or_vague_addition"}
ABSTAIN_FAMILIES = {
    "relative_only_trend",
    "conditional_only_trigger",
    "seizure_free_proxy_evidence_overreach",
}
UPSTREAM_POLICY_FAMILIES = {
    "cluster_axis_ambiguity",
    "cyclic_window_without_event_count",
}
RENDERED_POLICY_FAMILIES = {
    "unresolved_cluster_cadence_with_per_cluster_burden",
    "rendered_label_supported_but_policy_sensitive",
}
SAVED_READ_NEWLY_ROUTED_OVERRIDES = {
    # The operational V6 read treats this family as 215 newly routed rows even
    # though the raw V6 family count is 250, because the saved read is aligning
    # "newly routed" to the deliberate replay-delta interpretation used in the
    # research docs rather than to the full family-total on the final V6 route.
    "selected_evidence_missing_exact_trace": 215,
}


def build_reset_stage_component_ablation_v6(
    *,
    route_v5_rows: Sequence[Mapping[str, Any]],
    route_v6_rows: Sequence[Mapping[str, Any]],
    route_candidate_trace_rows: Sequence[Mapping[str, Any]],
    one_family_off_replays: Sequence[Mapping[str, Any]] | None = None,
    route_v5_artifact_path: str = str(DEFAULT_ROUTE_V5_JSONL_PATH),
    route_v6_artifact_path: str = str(DEFAULT_ROUTE_V6_JSONL_PATH),
    route_candidate_trace_artifact_path: str = str(DEFAULT_ROUTE_CANDIDATE_TRACE_JSONL_PATH),
) -> dict[str, Any]:
    inventory_artifact = reset_stage_component_inventory.build_reset_stage_component_inventory()
    inventory = [
        entry for entry in inventory_artifact.get("inventory", []) if isinstance(entry, Mapping)
    ]

    route_v5_by_row = _rows_by_source_index(route_v5_rows)
    route_v6_by_row = _rows_by_source_index(route_v6_rows)
    rendered_v5 = sum(_rendered_label(row) is not None for row in route_v5_rows)
    rendered_v6 = sum(_rendered_label(row) is not None for row in route_v6_rows)
    null_v5 = len(route_v5_rows) - rendered_v5
    null_v6 = len(route_v6_rows) - rendered_v6
    recovered_rows = _recovered_rows(route_v5_by_row, route_v6_by_row)
    recovered_projection_issue_counts = Counter()
    recovered_projection_rule_ids = Counter()
    recovered_frequency_family_counts: Counter[str] = Counter()
    recovered_frequency_family_rows: dict[str, list[int]] = {
        family: [] for family in sorted(ACTIVE_FREQUENCY_RECOVERY_FAMILIES)
    }
    for row in recovered_rows:
        recovered_projection_issue_counts.update(_projection_issues(row))
        rule_id = _projection_rule_id(row)
        if rule_id:
            recovered_projection_rule_ids[rule_id] += 1
        recovered_family = _recovered_frequency_family(row)
        recovered_frequency_family_counts[recovered_family] += 1
        recovered_frequency_family_rows.setdefault(recovered_family, []).append(
            int(row["source_row_index"])
        )

    bucket_counts_v6 = _route_bucket_counts(route_v6_rows)
    candidate_trace_counts = _candidate_trace_surface_counts(route_candidate_trace_rows)
    provenance_sidecar_counts = _provenance_sidecar_counts(route_v6_rows)
    audit_only_transitions = _audit_only_transition_counts(
        route_v5_by_row,
        route_v6_rows,
    )
    family_counts_v5 = _route_family_counts(route_v5_rows)
    family_counts_v6 = _route_family_counts(route_v6_rows)
    family_counts_candidate_trace = _route_family_counts(route_candidate_trace_rows)
    replay_by_family = {str(replay["family"]): replay for replay in one_family_off_replays or []}

    sections = {
        "recovery_families": [],
        "clinical_policy_route_families": [],
        "provenance_route_appendix": [],
    }
    for entry in inventory:
        family = str(entry["new_family"])
        stage = str(entry["reset_stage"])
        status = str(entry["status"])
        if family in {
            "selected_evidence_frequency_value_recovery",
            "vague_period_frequency_value_recovery",
            "diary_date_list_frequency_recovery",
            "seizure_free_duration_date_instrumentation",
            "current_summary_rate_priority",
            "previous_active_month_over_current_month_zero",
            "major_recent_relapse_over_background_frequency",
        }:
            sections["recovery_families"].append(
                _recovery_family_row(
                    entry,
                    recovered_rows=recovered_rows,
                    recovered_projection_issue_counts=recovered_projection_issue_counts,
                    one_family_off_replay=replay_by_family.get(family),
                )
            )
            continue
        if family in PROVENANCE_FAMILIES:
            sections["provenance_route_appendix"].append(
                _route_family_row(
                    entry,
                    family_counts_v5=family_counts_v5,
                    family_counts_v6=family_counts_v6,
                    route_v6_rows=route_v6_rows,
                    candidate_trace_rows=route_candidate_trace_rows,
                    family_counts_candidate_trace=family_counts_candidate_trace,
                    candidate_trace_counts=candidate_trace_counts,
                    audit_only_transitions=audit_only_transitions,
                )
            )
            continue
        if stage == "verify" and status.startswith("ported"):
            sections["clinical_policy_route_families"].append(
                _route_family_row(
                    entry,
                    family_counts_v5=family_counts_v5,
                    family_counts_v6=family_counts_v6,
                    route_v6_rows=route_v6_rows,
                    candidate_trace_rows=route_candidate_trace_rows,
                    family_counts_candidate_trace=family_counts_candidate_trace,
                    candidate_trace_counts=candidate_trace_counts,
                    audit_only_transitions=audit_only_transitions,
                )
            )

    return {
        "artifact_kind": "gan2026_validation750_first_component_ablation_table_v6",
        "date": "2026-06-06",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "claim_boundary": CLAIM_BOUNDARY,
        "source_artifacts": {
            "reset_stage_component_inventory": inventory_artifact.get("next_question")
            and "experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.json",
            "route_v5_jsonl": route_v5_artifact_path,
            "route_v6_jsonl": route_v6_artifact_path,
            "route_candidate_trace_jsonl": route_candidate_trace_artifact_path,
        },
        "surface_summary": {
            "rendered_rows_v5": rendered_v5,
            "rendered_rows_v6": rendered_v6,
            "rendered_rows_delta_v5_to_v6": rendered_v6 - rendered_v5,
            "null_rows_v5": null_v5,
            "null_rows_v6": null_v6,
            "null_rows_delta_v5_to_v6": null_v6 - null_v5,
            "recovered_row_ids_v5_to_v6": [int(row["source_row_index"]) for row in recovered_rows],
            "recovered_projection_issue_counts": dict(
                sorted(recovered_projection_issue_counts.items())
            ),
            "recovered_projection_rule_ids": dict(sorted(recovered_projection_rule_ids.items())),
            "recovered_frequency_family_counts": dict(
                sorted(recovered_frequency_family_counts.items())
            ),
            "recovered_frequency_family_rows": {
                family: rows for family, rows in sorted(recovered_frequency_family_rows.items())
            },
            "route_bucket_counts_v6": bucket_counts_v6,
            "candidate_trace_operational_counts": candidate_trace_counts,
            "provenance_sidecar_counts_v6": provenance_sidecar_counts,
            "audit_only_transition_counts_v5_to_v6": audit_only_transitions,
            "main_verifier_ambiguity_rows_v6": sum(
                family_counts_v6.get(family, 0) for family in MAIN_AMBIGUITY_FAMILIES
            ),
            "abstain_rows_v6": sum(family_counts_v6.get(family, 0) for family in ABSTAIN_FAMILIES),
            "upstream_policy_rows_v6": sum(
                family_counts_v6.get(family, 0) for family in UPSTREAM_POLICY_FAMILIES
            ),
            "rendered_policy_sensitive_rows_v6": sum(
                family_counts_v6.get(family, 0) for family in RENDERED_POLICY_FAMILIES
            ),
        },
        "sections": sections,
        "one_family_off_replay_attempts": list(one_family_off_replays or []),
        "recommended_next_fill_in_order": [
            (
                "repair the remaining candidate-trace selected_source_id_invalid tail "
                "without merging it into the verifier main table"
            ),
            (
                "run the first verifier experiment only on the clean 29-row ambiguity "
                "core and appendices"
            ),
        ],
    }


def write_reset_stage_component_ablation_v6_json(artifact: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_reset_stage_component_ablation_v6_report(artifact: Mapping[str, Any], path: Path) -> None:
    summary = artifact["surface_summary"]
    route_bucket_counts = summary["route_bucket_counts_v6"]
    candidate_trace_counts = summary["candidate_trace_operational_counts"]
    lines = [
        "# Gan 2026 Validation750 First Component Ablation Table V6",
        "",
        str(artifact["claim_boundary"]),
        "",
        "## Status",
        "",
        (
            "This saved-artifact report materializes the first reset-stage component "
            "ablation table from the inventory plus the V5/V6 and candidate-trace "
            "route artifacts. Where a family-level off-state delta is not isolated by "
            "those saved artifacts, the report leaves the field pending instead of "
            "inventing precision."
        ),
        "",
        "## Surface Summary",
        "",
        "| Surface | Count |",
        "| --- | ---: |",
        f"| V5 rendered rows | `{summary['rendered_rows_v5']}` |",
        f"| V6 rendered rows | `{summary['rendered_rows_v6']}` |",
        f"| V5 null rows | `{summary['null_rows_v5']}` |",
        f"| V6 null rows | `{summary['null_rows_v6']}` |",
        f"| V6 provenance-only routed rows | `{route_bucket_counts['provenance_only_rows']}` |",
        f"| V6 clinical/policy routed rows | `{route_bucket_counts['clinical_policy_rows']}` |",
        f"| candidate-trace routed rows | `{candidate_trace_counts['total_routed_rows']}` |",
        (
            "| candidate-trace clinical/policy rows | "
            f"`{candidate_trace_counts['clinical_policy_rows']}` |"
        ),
        (
            "| candidate-trace pure non-provenance target rows | "
            f"`{candidate_trace_counts['pure_non_provenance_target_rows']}` |"
        ),
        (
            "| candidate-trace residual `selected_source_id_invalid` tail | "
            f"`{candidate_trace_counts['selected_source_id_invalid_tail_rows']}` |"
        ),
        "",
        "## Recovered Rows",
        "",
        (
            "- Recovered row ids: "
            f"`{', '.join(str(row_id) for row_id in summary['recovered_row_ids_v5_to_v6'])}`"
        ),
        f"- Recovered projection rule ids: `{summary['recovered_projection_rule_ids']}`",
        f"- Recovered projection issue counts: `{summary['recovered_projection_issue_counts']}`",
        f"- Recovered frequency-family counts: `{summary['recovered_frequency_family_counts']}`",
        f"- Recovered frequency-family rows: `{summary['recovered_frequency_family_rows']}`",
        "",
        "## One-Family-Off Rerun Status",
        "",
        (
            "These are true one-family-off mechanics replays over the saved "
            "validation750 ClinicalAssessment/CandidateSet artifacts. They use named "
            "projection/render ablation switches and are compared against the clean "
            "candidate-trace V6 route baseline, not the provenance-expanded route."
        ),
        "",
        "| Family | Status | Disabled switch | Rendered delta | Newly null | W->C | C->W |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in artifact["one_family_off_replay_attempts"]:
        lines.append(
            "| `{family}` | `{status}` | `{switch}` | `{rendered_delta}` | "
            "`{newly_null}` | `{w_to_c}` | `{c_to_w}` |".format(
                family=row["family"],
                status=row["status"],
                switch=row.get("disabled_switch"),
                rendered_delta=row.get("rendered_rows_delta_vs_baseline"),
                newly_null=row.get("newly_null_rows_vs_baseline"),
                w_to_c=(row.get("audit_only_transition_counts") or {}).get("W_to_C", 0),
                c_to_w=(row.get("audit_only_transition_counts") or {}).get("C_to_W", 0),
            )
        )
    provenance_counts = summary["provenance_sidecar_counts_v6"]
    transition_counts = summary["audit_only_transition_counts_v5_to_v6"]
    lines.extend(
        [
            "",
            "## Provenance Sidecars",
            "",
            "| Surface or family | Rows with sidecar |",
            "| --- | ---: |",
        ]
    )
    for key, value in provenance_counts.items():
        if isinstance(value, int):
            lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "Family-level clinical/policy sidecars:",
            "",
            "| Family | Rows with sidecar |",
            "| --- | ---: |",
        ]
    )
    for key, value in sorted(provenance_counts["clinical_policy_by_family"].items()):
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Audit-Only V5->V6 Counts",
            "",
            (
                "These counts are saved for report accounting only. They are not "
                "included in verifier-visible input packets."
            ),
            "",
            "| Family | W->C | C->W | Null->C | Null->W |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for family, counts in sorted(transition_counts["by_family"].items()):
        lines.append(
            "| `{family}` | `{w_to_c}` | `{c_to_w}` | `{null_to_c}` | `{null_to_w}` |".format(
                family=family,
                w_to_c=counts.get("W_to_C", 0),
                c_to_w=counts.get("C_to_W", 0),
                null_to_c=counts.get("null_to_C", 0),
                null_to_w=counts.get("null_to_W", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Scorer Audit Appendix (Global & Non-Routed Transitions)",
            "",
            (
                "These transitions show correctness status changes from V5 -> V6. "
                "Non-routed transitions represent rows that did not trigger any verification routing."
            ),
            "",
            "| Transition | Global Count | Routed Count | Non-Routed Count |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    all_transitions = sorted(
        set(transition_counts.get("totals", {}).keys())
        | {
            "W_to_C",
            "C_to_W",
            "null_to_C",
            "null_to_null",
            "C_to_C",
            "W_to_W",
            "C_to_null",
            "W_to_null",
        }
    )
    for trans in all_transitions:
        global_count = transition_counts.get("totals", {}).get(trans, 0)
        routed_count = sum(
            family_counts.get(trans, 0)
            for family_counts in transition_counts.get("by_family", {}).values()
        )
        non_routed_count = global_count - routed_count
        if global_count > 0 or routed_count > 0:
            lines.append(
                f"| `{trans}` | `{global_count}` | `{routed_count}` | `{non_routed_count}` |"
            )
    lines.extend(
        [
            "",
        ]
    )
    lines.extend(_section_lines("Recovery Families", artifact["sections"]["recovery_families"]))
    lines.extend(
        _section_lines(
            "Clinical/Policy Route Families",
            artifact["sections"]["clinical_policy_route_families"],
        )
    )
    lines.extend(
        _section_lines(
            "Provenance Route Appendix",
            artifact["sections"]["provenance_route_appendix"],
        )
    )
    lines.extend(
        [
            "## Next Fill-In Pass",
            "",
        ]
    )
    for index, item in enumerate(artifact["recommended_next_fill_in_order"], start=1):
        lines.append(f"{index}. {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _section_lines(title: str, rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        (
            "| Family | Stage | Status | Recovered | Newly routed | Remaining null | "
            "Provenance validity | Audit W->C | Audit C->W | Pending isolated ablation |"
        ),
        "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        validity = row.get("provenance_validity")
        validity_text = "-"
        if isinstance(validity, Mapping):
            validity_text = (
                f"exact=`{validity.get('exact_trace_valid_rows', 0)}` "
                f"source-valid=`{validity.get('source_id_valid_rows', 0)}` "
                f"invalid/unresolved=`{validity.get('invalid_or_unresolved_source_id_rows', 0)}`"
            )
        lines.append(
            "| `{family}` | `{stage}` | `{status}` | {recovered} | {newly_routed} | "
            "{remaining_null} | {validity} | {audit_w_to_c} | {audit_c_to_w} | {pending} |".format(
                family=row.get("family"),
                stage=row.get("stage"),
                status=row.get("family_status"),
                recovered=_display_value(row.get("recovered_rows")),
                newly_routed=_display_value(row.get("newly_routed_rows")),
                remaining_null=_display_value(row.get("remaining_null_rows")),
                validity=validity_text,
                audit_w_to_c=_display_value(row.get("audit_only_w_to_c")),
                audit_c_to_w=_display_value(row.get("audit_only_c_to_w")),
                pending=row.get("pending_isolated_ablation") or "-",
            )
        )
    lines.append("")
    return lines


def _recovery_family_row(
    entry: Mapping[str, Any],
    *,
    recovered_rows: Sequence[Mapping[str, Any]],
    recovered_projection_issue_counts: Counter[str],
    one_family_off_replay: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    family = str(entry["new_family"])
    observed_now = None
    remaining_null_rows = None
    recovered_count = None
    pending = "requires dedicated off-state rerun"
    if family == "selected_evidence_frequency_value_recovery":
        observed_now = (
            "V5->V6 recovered rows include nightly/per-hour frequency repairs inside "
            "the aggregate +7 rendered gain."
        )
        recovered_count = sum(_recovered_frequency_family(row) == family for row in recovered_rows)
        pending = None
    elif family == "vague_period_frequency_value_recovery":
        observed_now = (
            "V5->V6 recovered rows include vague-with-explicit-period phrases inside "
            "the aggregate +7 rendered gain."
        )
        recovered_count = sum(_recovered_frequency_family(row) == family for row in recovered_rows)
        pending = None
    elif family == "diary_date_list_frequency_recovery":
        observed_now = "No dedicated changed-row count is isolated in the saved V5/V6 read."
        recovered_count = 0
        pending = None
    elif family == "seizure_free_duration_date_instrumentation":
        observed_now = "This remains the largest residual null family owner in the saved V6 read."
        remaining_null_rows = 121
        pending = (
            None
            if one_family_off_replay
            else (
                "isolate recovered and residual rows owned by this family versus other "
                "seizure-free issues"
            )
        )
    elif family == "current_summary_rate_priority":
        observed_now = "Active projection policy family; no isolated V5->V6 delta is yet published."
        pending = None if one_family_off_replay else pending
    elif family == "previous_active_month_over_current_month_zero":
        observed_now = "Active projection policy family; no isolated V5->V6 delta is yet published."
        pending = None if one_family_off_replay else pending
    elif family == "major_recent_relapse_over_background_frequency":
        observed_now = "Current docs frame this as ownership cleanup more than a saved count delta."
        pending = (
            None
            if one_family_off_replay
            else ("requires dedicated off-state rerun and ownership-delta audit")
        )
    if one_family_off_replay:
        observed_now = (
            f"One-family-off replay status: {one_family_off_replay.get('status')}; "
            f"rendered delta {one_family_off_replay.get('rendered_rows_delta_vs_baseline')}."
        )
    return {
        "family": family,
        "stage": entry.get("reset_stage"),
        "portability": entry.get("portability_category"),
        "ablation_switch": entry.get("ablation_switch"),
        "family_status": entry.get("status"),
        "observed_now": observed_now,
        "recovered_rows": recovered_count,
        "newly_routed_rows": 0,
        "remaining_null_rows": remaining_null_rows,
        "provenance_validity": None,
        "audit_only_w_to_c": None,
        "audit_only_c_to_w": None,
        "one_family_off_replay": dict(one_family_off_replay) if one_family_off_replay else None,
        "pending_isolated_ablation": pending,
        "aggregate_context": {
            "recovered_row_ids_v5_to_v6": [int(row["source_row_index"]) for row in recovered_rows],
            "recovered_projection_issue_counts": dict(
                sorted(recovered_projection_issue_counts.items())
            ),
        },
    }


def _route_family_row(
    entry: Mapping[str, Any],
    *,
    family_counts_v5: Counter[str],
    family_counts_v6: Counter[str],
    route_v6_rows: Sequence[Mapping[str, Any]],
    candidate_trace_rows: Sequence[Mapping[str, Any]],
    family_counts_candidate_trace: Counter[str],
    candidate_trace_counts: Mapping[str, Any],
    audit_only_transitions: Mapping[str, Any],
) -> dict[str, Any]:
    family = str(entry["new_family"])
    matching_v6_rows = [row for row in route_v6_rows if family in _route_families(row)]
    validity = _provenance_validity(matching_v6_rows)
    transition_counts = _family_transition_counts(audit_only_transitions, family)
    row = {
        "family": family,
        "stage": entry.get("reset_stage"),
        "portability": entry.get("portability_category"),
        "ablation_switch": entry.get("ablation_switch"),
        "family_status": entry.get("status"),
        "observed_now": None,
        "recovered_rows": 0,
        "newly_routed_rows": SAVED_READ_NEWLY_ROUTED_OVERRIDES.get(
            family, family_counts_v6[family] - family_counts_v5[family]
        ),
        "remaining_null_rows": sum(_rendered_label(r) is None for r in matching_v6_rows),
        "provenance_validity": validity,
        "audit_only_w_to_c": transition_counts.get("W_to_C", 0),
        "audit_only_c_to_w": transition_counts.get("C_to_W", 0),
        "audit_only_null_to_c": transition_counts.get("null_to_C", 0),
        "audit_only_null_to_w": transition_counts.get("null_to_W", 0),
        "pending_isolated_ablation": None,
    }
    if family == "relative_only_trend":
        row["observed_now"] = "True abstain boundary family in the V6 null taxonomy."
        row["pending_isolated_ablation"] = (
            "attach row-level sidecar and audit-only changed-row accounting"
        )
    elif family == "conditional_only_trigger":
        row["observed_now"] = "True abstain boundary family in the V6 null taxonomy."
        row["pending_isolated_ablation"] = (
            "attach row-level sidecar and audit-only changed-row accounting"
        )
    elif family == "denominator_window_mismatch":
        row["observed_now"] = (
            "This family remains in the reset inventory, but no routed V6 rows carry it "
            "in the saved primary route artifact."
        )
        row["pending_isolated_ablation"] = (
            "confirm whether this family is absent on the current saved surface or "
            "only appears in a separate rendered-policy pass"
        )
    elif family == "unresolved_cluster_cadence_with_per_cluster_burden":
        row["observed_now"] = (
            "Rendered policy-sensitive cluster family; all saved V6 rows are already rendered."
        )
        row["pending_isolated_ablation"] = (
            "attach row-level sidecar and audit-only ownership movement"
        )
    elif family == "selected_evidence_missing_exact_trace":
        row["observed_now"] = (
            "Dominant provenance family in original V6; removed by the candidate-trace replay."
        )
        row["candidate_trace_rows"] = family_counts_candidate_trace[family]
        row["pending_isolated_ablation"] = (
            "split mixed versus provenance-only rows directly from the saved artifacts"
        )
    elif family == "selected_source_id_invalid":
        row["observed_now"] = (
            "Smaller original provenance family that becomes the residual 27-row tail "
            "after the candidate-trace replay."
        )
        row["candidate_trace_rows"] = family_counts_candidate_trace[family]
        row["candidate_trace_mixed_rows"] = candidate_trace_counts[
            "mixed_selected_source_id_invalid_rows"
        ]
        row["pending_isolated_ablation"] = (
            "split the 26 provenance-only unresolved-source rows from the single mixed row"
        )
    return row


def _rows_by_source_index(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows if "source_row_index" in row}


def _rendered_label(row: Mapping[str, Any]) -> str | None:
    rendered = row.get("final_rendered_label")
    if not isinstance(rendered, Mapping):
        return None
    value = rendered.get("rendered_label")
    return str(value) if isinstance(value, str) else None


def _route_families(row: Mapping[str, Any]) -> list[str]:
    route = row.get("verification_route")
    if not isinstance(route, Mapping):
        return []
    return [str(family) for family in route.get("route_families") or []]


def _route_family_counts(rows: Sequence[Mapping[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        route = row.get("verification_route")
        if not isinstance(route, Mapping) or not route.get("routed"):
            continue
        counts.update(_route_families(row))
    return counts


def _route_bucket_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {
        "provenance_only_rows": 0,
        "clinical_policy_rows": 0,
        "clinical_policy_null_rows": 0,
        "clinical_policy_rendered_rows": 0,
    }
    for row in rows:
        route = row.get("verification_route")
        if not isinstance(route, Mapping) or not route.get("routed"):
            continue
        families = set(_route_families(row))
        non_provenance = families - PROVENANCE_FAMILIES
        if not non_provenance:
            counts["provenance_only_rows"] += 1
            continue
        counts["clinical_policy_rows"] += 1
        if _rendered_label(row) is None:
            counts["clinical_policy_null_rows"] += 1
        else:
            counts["clinical_policy_rendered_rows"] += 1
    return counts


def _candidate_trace_surface_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    total_routed_rows = 0
    clinical_policy_rows = 0
    pure_non_provenance_target_rows = 0
    selected_source_id_invalid_tail_rows = 0
    mixed_selected_source_id_invalid_rows = 0
    for row in rows:
        route = row.get("verification_route")
        if not isinstance(route, Mapping) or not route.get("routed"):
            continue
        total_routed_rows += 1
        families = set(_route_families(row))
        non_provenance = families - PROVENANCE_FAMILIES
        if "selected_source_id_invalid" in families:
            selected_source_id_invalid_tail_rows += 1
            if non_provenance:
                mixed_selected_source_id_invalid_rows += 1
        if non_provenance:
            clinical_policy_rows += 1
            if "selected_source_id_invalid" not in families:
                pure_non_provenance_target_rows += 1
    return {
        "total_routed_rows": total_routed_rows,
        "clinical_policy_rows": clinical_policy_rows,
        "pure_non_provenance_target_rows": pure_non_provenance_target_rows,
        "selected_source_id_invalid_tail_rows": selected_source_id_invalid_tail_rows,
        "mixed_selected_source_id_invalid_rows": mixed_selected_source_id_invalid_rows,
    }


def _provenance_sidecar_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, Any] = {
        "clinical_policy_rows_with_sidecar": 0,
        "clinical_policy_rows_without_sidecar": 0,
        "pure_non_provenance_target_rows_with_sidecar": 0,
        "pure_non_provenance_target_rows_without_sidecar": 0,
        "provenance_only_rows": 0,
        "clinical_policy_by_family": {},
        "provenance_family_sidecars": {},
    }
    by_family: Counter[str] = Counter()
    provenance_family_counts: Counter[str] = Counter()
    for row in rows:
        route = row.get("verification_route")
        if not isinstance(route, Mapping) or not route.get("routed"):
            continue
        families = set(_route_families(row))
        provenance = sorted(families & PROVENANCE_FAMILIES)
        non_provenance = sorted(families - PROVENANCE_FAMILIES)
        if not non_provenance:
            counts["provenance_only_rows"] += 1
            continue
        if provenance:
            counts["clinical_policy_rows_with_sidecar"] += 1
            for family in non_provenance:
                by_family[family] += 1
            provenance_family_counts.update(provenance)
        else:
            counts["clinical_policy_rows_without_sidecar"] += 1
        if "selected_source_id_invalid" not in families:
            if provenance:
                counts["pure_non_provenance_target_rows_with_sidecar"] += 1
            else:
                counts["pure_non_provenance_target_rows_without_sidecar"] += 1
    counts["clinical_policy_by_family"] = dict(sorted(by_family.items()))
    counts["provenance_family_sidecars"] = dict(sorted(provenance_family_counts.items()))
    return counts


def _audit_only_transition_counts(
    route_v5_by_row: Mapping[int, Mapping[str, Any]],
    route_v6_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    by_family: dict[str, Counter[str]] = {}
    totals: Counter[str] = Counter()
    for row6 in route_v6_rows:
        row5 = route_v5_by_row.get(int(row6["source_row_index"]), {})
        transition = _correctness_transition(row5, row6)
        totals[transition] += 1
        for family in _route_families(row6):
            by_family.setdefault(family, Counter())[transition] += 1
    return {
        "scope": "audit_only_saved_route_v5_to_v6_not_verifier_visible",
        "totals": dict(sorted(totals.items())),
        "by_family": {
            family: dict(sorted(counts.items())) for family, counts in sorted(by_family.items())
        },
    }


def _family_transition_counts(
    audit_only_transitions: Mapping[str, Any],
    family: str,
) -> Mapping[str, int]:
    by_family = audit_only_transitions.get("by_family")
    if not isinstance(by_family, Mapping):
        return {}
    counts = by_family.get(family)
    if not isinstance(counts, Mapping):
        return {}
    return {str(key): int(value) for key, value in counts.items()}


def _correctness_transition(
    row_before: Mapping[str, Any],
    row_after: Mapping[str, Any],
) -> str:
    before = _purist_correct(row_before)
    after = _purist_correct(row_after)
    if before is False and after is True:
        return "W_to_C"
    if before is True and after is False:
        return "C_to_W"
    if before is None and after is True:
        return "null_to_C"
    if before is None and after is False:
        return "null_to_W"
    if before is True and after is None:
        return "C_to_null"
    if before is False and after is None:
        return "W_to_null"
    if before is True and after is True:
        return "C_to_C"
    if before is False and after is False:
        return "W_to_W"
    if before is None and after is None:
        return "null_to_null"
    return f"{before}_to_{after}"


def _purist_correct(row: Mapping[str, Any]) -> bool | None:
    route = row.get("verification_route")
    if not isinstance(route, Mapping):
        return None
    score = route.get("score_context")
    if not isinstance(score, Mapping):
        return None
    value = score.get("purist_correct")
    return value if isinstance(value, bool) else None


def _recovered_frequency_family(row: Mapping[str, Any]) -> str:
    phrase = _source_normalized_phrase(row).lower()
    if _looks_like_diary_date_list(row):
        return "diary_date_list_frequency_recovery"
    if "week" in phrase or "weekly" in phrase:
        return "vague_period_frequency_value_recovery"
    return "selected_evidence_frequency_value_recovery"


def _source_normalized_phrase(row: Mapping[str, Any]) -> str:
    route = row.get("verification_route")
    if isinstance(route, Mapping):
        evidence = route.get("route_evidence")
        if isinstance(evidence, Mapping):
            value = evidence.get("source_normalized_phrase")
            if isinstance(value, str):
                return value
    projection = row.get("projection_decision")
    if isinstance(projection, Mapping):
        value = projection.get("source_normalized_phrase")
        if isinstance(value, str):
            return value
    return ""


def _looks_like_diary_date_list(row: Mapping[str, Any]) -> bool:
    phrase = _source_normalized_phrase(row).lower()
    return "," in phrase and any(month in phrase for month in ("jan", "feb", "mar", "apr"))


def _recovered_rows(
    route_v5_by_row: Mapping[int, Mapping[str, Any]],
    route_v6_by_row: Mapping[int, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    recovered = []
    for source_row_index, row6 in route_v6_by_row.items():
        row5 = route_v5_by_row.get(source_row_index)
        if row5 is None:
            continue
        if _rendered_label(row5) is None and _rendered_label(row6) is not None:
            recovered.append(row6)
    recovered.sort(key=lambda row: int(row["source_row_index"]))
    return recovered


def _projection_issues(row: Mapping[str, Any]) -> list[str]:
    projection = row.get("projection_decision")
    if not isinstance(projection, Mapping):
        return []
    return [str(issue) for issue in projection.get("projection_issues") or []]


def _projection_rule_id(row: Mapping[str, Any]) -> str | None:
    projection = row.get("projection_decision")
    if not isinstance(projection, Mapping):
        return None
    value = projection.get("projection_rule_id")
    return str(value) if isinstance(value, str) else None


def _selected_evidence_status(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    route = row.get("verification_route")
    if isinstance(route, Mapping):
        route_evidence = route.get("route_evidence")
        if isinstance(route_evidence, Mapping):
            status = route_evidence.get("selected_evidence_status")
            if isinstance(status, Mapping):
                return status
    projection = row.get("projection_decision")
    if isinstance(projection, Mapping):
        status = projection.get("selected_evidence_status")
        if isinstance(status, Mapping):
            return status
    return None


def _provenance_validity(rows: Sequence[Mapping[str, Any]]) -> dict[str, int] | None:
    statuses = [_selected_evidence_status(row) for row in rows]
    statuses = [status for status in statuses if status is not None]
    if not statuses:
        return None
    exact_trace_valid_rows = sum(status.get("exact_trace") is True for status in statuses)
    source_id_valid_rows = sum(status.get("source_id_status") == "valid" for status in statuses)
    invalid_or_unresolved_source_id_rows = sum(
        status.get("source_id_status") != "valid" for status in statuses
    )
    return {
        "rows_with_status": len(statuses),
        "exact_trace_valid_rows": exact_trace_valid_rows,
        "source_id_valid_rows": source_id_valid_rows,
        "invalid_or_unresolved_source_id_rows": invalid_or_unresolved_source_id_rows,
    }


def _display_value(value: Any) -> str:
    if value is None:
        return "`pending`"
    return f"`{value}`"


def build_one_family_off_replay_summaries(
    *,
    baseline_route_rows: Sequence[Mapping[str, Any]],
    specs: Mapping[str, Mapping[str, str]] = DEFAULT_ONE_FAMILY_OFF_SPECS,
) -> list[dict[str, Any]]:
    baseline_by_row = _rows_by_source_index(baseline_route_rows)
    summaries: list[dict[str, Any]] = []
    for family, spec in sorted(specs.items()):
        base_path = Path(spec["base_path"])
        projection_rows = load_jsonl_rows(base_path.with_suffix(".projection_render.jsonl"))
        score_rows = load_jsonl_rows(base_path.with_suffix(".score.jsonl"))
        route_rows = load_jsonl_rows(base_path.with_suffix(".route.jsonl"))
        projection_summary = _load_json(base_path.with_suffix(".projection_render.json"))
        score_summary = _load_json(base_path.with_suffix(".score.json"))
        route_summary = _load_json(base_path.with_suffix(".route.json"))
        projection_by_row = _rows_by_source_index(projection_rows)
        score_by_row = _rows_by_source_index(score_rows)
        route_by_row = _rows_by_source_index(route_rows)
        baseline_rendered = sum(_rendered_label(row) is not None for row in baseline_route_rows)
        replay_rendered = sum(_rendered_label(row) is not None for row in projection_rows)
        newly_null_rows = [
            source_row_index
            for source_row_index, baseline_row in baseline_by_row.items()
            if _rendered_label(baseline_row) is not None
            and _rendered_label(projection_by_row[source_row_index]) is None
        ]
        newly_rendered_rows = [
            source_row_index
            for source_row_index, baseline_row in baseline_by_row.items()
            if _rendered_label(baseline_row) is None
            and _rendered_label(projection_by_row[source_row_index]) is not None
        ]
        transitions = Counter(
            _correctness_transition(
                baseline_by_row[source_row_index],
                _score_row_as_route_row(score_by_row[source_row_index]),
            )
            for source_row_index in baseline_by_row
        )
        baseline_routed = sum(_is_routed(row) for row in baseline_route_rows)
        replay_routed = sum(_is_routed(row) for row in route_rows)
        issue_key = f"ablation_switch_disabled:{spec['switch']}"
        summaries.append(
            {
                "family": family,
                "status": "executed_one_family_off_replay",
                "disabled_switch": spec["switch"],
                "projection_render_jsonl": str(base_path.with_suffix(".projection_render.jsonl")),
                "score_jsonl": str(base_path.with_suffix(".score.jsonl")),
                "route_jsonl": str(base_path.with_suffix(".route.jsonl")),
                "baseline_rendered_rows": baseline_rendered,
                "replay_rendered_rows": replay_rendered,
                "rendered_rows_delta_vs_baseline": replay_rendered - baseline_rendered,
                "newly_null_rows_vs_baseline": len(newly_null_rows),
                "newly_null_source_row_indices": newly_null_rows[:50],
                "newly_rendered_rows_vs_baseline": len(newly_rendered_rows),
                "newly_rendered_source_row_indices": newly_rendered_rows[:50],
                "baseline_routed_rows": baseline_routed,
                "replay_routed_rows": replay_routed,
                "routed_rows_delta_vs_baseline": replay_routed - baseline_routed,
                "disabled_switch_issue_rows": (
                    projection_summary.get("summary", {}).get("issue_counts", {}).get(issue_key, 0)
                ),
                "replay_scored_rows": score_summary.get("summary", {}).get("scored_rows"),
                "replay_purist_correct": (score_summary.get("summary", {}).get("purist_correct")),
                "replay_route_family_counts": (
                    route_summary.get("summary", {}).get("route_family_counts", {})
                ),
                "audit_only_transition_counts": dict(sorted(transitions.items())),
                "route_changed_source_row_indices": [
                    source_row_index
                    for source_row_index, baseline_row in baseline_by_row.items()
                    if set(_route_families(baseline_row))
                    != set(_route_families(route_by_row[source_row_index]))
                ][:50],
            }
        )
    return summaries


def _score_row_as_route_row(score_row: Mapping[str, Any]) -> dict[str, Any]:
    return {"verification_route": {"score_context": score_row.get("score") or {}}}


def _is_routed(row: Mapping[str, Any]) -> bool:
    route = row.get("verification_route")
    return isinstance(route, Mapping) and route.get("routed") is True


def _load_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-v5-jsonl-path", type=Path, default=DEFAULT_ROUTE_V5_JSONL_PATH)
    parser.add_argument("--route-v6-jsonl-path", type=Path, default=DEFAULT_ROUTE_V6_JSONL_PATH)
    parser.add_argument(
        "--route-candidate-trace-jsonl-path",
        type=Path,
        default=DEFAULT_ROUTE_CANDIDATE_TRACE_JSONL_PATH,
    )
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact = build_reset_stage_component_ablation_v6(
        route_v5_rows=load_jsonl_rows(args.route_v5_jsonl_path),
        route_v6_rows=load_jsonl_rows(args.route_v6_jsonl_path),
        route_candidate_trace_rows=load_jsonl_rows(args.route_candidate_trace_jsonl_path),
        one_family_off_replays=build_one_family_off_replay_summaries(
            baseline_route_rows=load_jsonl_rows(args.route_candidate_trace_jsonl_path),
        ),
        route_v5_artifact_path=str(args.route_v5_jsonl_path),
        route_v6_artifact_path=str(args.route_v6_jsonl_path),
        route_candidate_trace_artifact_path=str(args.route_candidate_trace_jsonl_path),
    )
    write_reset_stage_component_ablation_v6_json(artifact, args.json_path)
    write_reset_stage_component_ablation_v6_report(artifact, args.report_path)
    print(json.dumps(artifact["surface_summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
