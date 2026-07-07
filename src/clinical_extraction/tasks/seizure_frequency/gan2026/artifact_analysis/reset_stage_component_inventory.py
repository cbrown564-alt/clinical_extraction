"""Record the reset-stage crosswalk from old Gan 2026 families to current owners."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_JSON_PATH = Path("experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.md")


@dataclass(frozen=True)
class ResetComponentEntry:
    old_name: str
    reset_stage: str
    new_family: str
    portability_category: str
    ablation_switch: str
    issue_or_rule_ids: tuple[str, ...]
    status: str
    notes: str


RESET_COMPONENT_ENTRIES = (
    ResetComponentEntry(
        old_name="selected-evidence frequency repair",
        reset_stage="normalize",
        new_family="selected_evidence_frequency_value_recovery",
        portability_category="seizure_frequency",
        ablation_switch="normalize_selected_evidence_frequency_value_recovery",
        issue_or_rule_ids=(
            "frequency_rate_values_repaired_from_primary_candidate",
            "frequency_rate_values_repaired_from_selected_evidence",
        ),
        status="ported_v6",
        notes=("Ported as explicit reset normalization instead of hidden scorer-facing repair."),
    ),
    ResetComponentEntry(
        old_name="vague period rates",
        reset_stage="normalize",
        new_family="vague_period_frequency_value_recovery",
        portability_category="seizure_frequency",
        ablation_switch="normalize_vague_period_frequency_value_recovery",
        issue_or_rule_ids=(
            "frequency_label_values_unparsed",
            "frequency_rate_values_incomplete",
        ),
        status="ported_v6",
        notes=(
            "Covers vague weekly/monthly/yearly burden only when an explicit period "
            "exists in source-backed evidence."
        ),
    ),
    ResetComponentEntry(
        old_name="diary date lists",
        reset_stage="normalize",
        new_family="diary_date_list_frequency_recovery",
        portability_category="gan2026_specific",
        ablation_switch="normalize_diary_date_list_frequency_recovery",
        issue_or_rule_ids=("frequency_rate_values_repaired_from_diary_dates",),
        status="ported_v6",
        notes=(
            "Kept separate because diary-style aggregation is useful on Gan letters but "
            "needs explicit portability discipline."
        ),
    ),
    ResetComponentEntry(
        old_name="anchor-window frequency value recovery",
        reset_stage="normalize",
        new_family="anchor_window_frequency_value_recovery",
        portability_category="general",
        ablation_switch="normalize_frequency_anchor_window_value_recovery",
        issue_or_rule_ids=(
            "frequency_rate_values_repaired_from_anchor_window",
            "frequency_rate_anchor_from_last_event_phrase",
            "frequency_rate_anchor_year_inferred_from_reference_date",
        ),
        status="ported_v7",
        notes=(
            "Recovers explicit count-plus-anchor frequency statements by deriving a "
            "bounded month window from source-backed since-date or last-event anchors."
        ),
    ),
    ResetComponentEntry(
        old_name="multi-month bucket frequency value recovery",
        reset_stage="normalize",
        new_family="multi_month_bucket_frequency_value_recovery",
        portability_category="general",
        ablation_switch="normalize_frequency_multi_month_bucket_value_recovery",
        issue_or_rule_ids=(
            "frequency_rate_values_repaired_from_multi_month_bucket",
            "frequency_rate_multi_month_window_from_named_buckets",
            "frequency_rate_multi_month_window_from_source_phrase",
            "frequency_rate_bucket_year_inferred_from_reference_date",
        ),
        status="ported_v7",
        notes=(
            "Recovers explicit multi-month count-bearing month-bucket summaries "
            "without broad single-month rescue or per-cluster flattening."
        ),
    ),
    ResetComponentEntry(
        old_name="seizure-free duration/date handling",
        reset_stage="normalize",
        new_family="seizure_free_duration_date_instrumentation",
        portability_category="seizure_frequency",
        ablation_switch="normalize_seizure_free_duration_date_instrumentation",
        issue_or_rule_ids=(
            "seizure_free_duration_repaired_from_since_date",
            "seizure_free_duration_repaired_from_last_event_date",
        ),
        status="ported_v6",
        notes=(
            "Owns durations, since-dates, last-event anchors, and same-note temporal "
            "carry-forward before projection."
        ),
    ),
    ResetComponentEntry(
        old_name="summary-rate priority",
        reset_stage="project",
        new_family="current_summary_rate_priority",
        portability_category="seizure_frequency",
        ablation_switch="project_current_summary_rate_priority",
        issue_or_rule_ids=("current_summary_rate_priority",),
        status="ported_v6",
        notes=(
            "Allows explicit current summary burden to own projection when it cleanly "
            "outranks long-window background evidence."
        ),
    ),
    ResetComponentEntry(
        old_name="previous-month/current-month aggregation",
        reset_stage="project",
        new_family="previous_active_month_over_current_month_zero",
        portability_category="seizure_frequency",
        ablation_switch="project_previous_active_month_over_current_month_zero",
        issue_or_rule_ids=("previous_active_month_over_current_month_zero",),
        status="ported_v6",
        notes=(
            "Restores the narrow current-vs-historical policy family without reopening "
            "broad additive rendering."
        ),
    ),
    ResetComponentEntry(
        old_name="major-semiology recent relapse priority",
        reset_stage="project",
        new_family="major_recent_relapse_over_background_frequency",
        portability_category="clinical_epilepsy",
        ablation_switch="project_major_recent_relapse_over_background_frequency",
        issue_or_rule_ids=("major_recent_relapse_over_background_frequency",),
        status="ported_v6",
        notes=(
            "A dominant recent convulsive relapse can own the projected current burden "
            "when source-backed and policy-named."
        ),
    ),
    ResetComponentEntry(
        old_name="relative-only trend guard",
        reset_stage="verify",
        new_family="relative_only_trend",
        portability_category="clinical_epilepsy",
        ablation_switch="route_relative_only_trend",
        issue_or_rule_ids=("relative_change_without_current_baseline",),
        status="ported_route_family_v6",
        notes=(
            "Moved out of anonymous parse failure and into an explicit route family for "
            "non-renderable trend-only evidence."
        ),
    ),
    ResetComponentEntry(
        old_name="conditional-only trigger guard",
        reset_stage="verify",
        new_family="conditional_only_trigger",
        portability_category="clinical_epilepsy",
        ablation_switch="route_conditional_only_trigger",
        issue_or_rule_ids=("conditional_only_trigger_without_baseline",),
        status="ported_route_family_v6",
        notes=(
            "Conditional event triggers are now explicit verification debt rather than "
            "silent unknown/null drift."
        ),
    ),
    ResetComponentEntry(
        old_name="selected-evidence missing exact trace",
        reset_stage="verify",
        new_family="selected_evidence_missing_exact_trace",
        portability_category="general",
        ablation_switch="route_selected_evidence_missing_exact_trace",
        issue_or_rule_ids=("selected_evidence_missing_exact_trace",),
        status="ported_route_family_v6",
        notes=(
            "Ported only after the reset gained explicit provenance fields with "
            "exact-trace and source-id status."
        ),
    ),
    ResetComponentEntry(
        old_name="selected source id invalid",
        reset_stage="verify",
        new_family="selected_source_id_invalid",
        portability_category="general",
        ablation_switch="route_selected_source_id_invalid",
        issue_or_rule_ids=("selected_source_id_invalid",),
        status="ported_route_family_v6",
        notes=(
            "Separated from missing exact trace so provenance review can distinguish "
            "invalid ids from non-exact evidence."
        ),
    ),
    ResetComponentEntry(
        old_name="denominator-window mismatch",
        reset_stage="verify",
        new_family="denominator_window_mismatch",
        portability_category="benchmark_format",
        ablation_switch="route_denominator_window_mismatch",
        issue_or_rule_ids=("denominator_window_mismatch",),
        status="ported_route_family_v6",
        notes=(
            "Kept as route/report ownership because the Gan-compatible label can be "
            "rendered while the denominator semantics remain review-sensitive."
        ),
    ),
    ResetComponentEntry(
        old_name="cluster cadence versus per-cluster burden ambiguity",
        reset_stage="verify",
        new_family="unresolved_cluster_cadence_with_per_cluster_burden",
        portability_category="seizure_frequency",
        ablation_switch=("route_unresolved_cluster_cadence_with_per_cluster_burden"),
        issue_or_rule_ids=("cluster_cadence_unknown_with_per_cluster_burden",),
        status="ported_route_contract_v6",
        notes=(
            "Reset now allows a convention-compatible rendered label while routing the "
            "remaining cadence/axis ambiguity for review."
        ),
    ),
    ResetComponentEntry(
        old_name="comparator-label preservation",
        reset_stage="verify",
        new_family="named_comparator_preservation_action_policy",
        portability_category="benchmark_format",
        ablation_switch="verify_named_comparator_preservation_action_policy",
        issue_or_rule_ids=("comparator_preservation_policy_pending",),
        status="pending_policy_decision",
        notes=(
            "Explicitly deferred. If it returns, it must be a named action policy "
            "rather than hidden fallback."
        ),
    ),
    ResetComponentEntry(
        old_name="H6/H9/H10 sidecars",
        reset_stage="report",
        new_family="audit_sidecars_only",
        portability_category="general",
        ablation_switch="report_audit_sidecars_only",
        issue_or_rule_ids=("h6_h9_h10_audit_only",),
        status="retained_audit_only",
        notes=(
            "Useful instrumentation remains available, but these no longer count as "
            "core reset pipeline stages."
        ),
    ),
    ResetComponentEntry(
        old_name="component evidence matrix",
        reset_stage="report",
        new_family="stage_owned_component_evidence_matrix",
        portability_category="general",
        ablation_switch="report_stage_owned_component_evidence_matrix",
        issue_or_rule_ids=("component_evidence_matrix_audit_only",),
        status="retained_audit_only",
        notes=(
            "Retained as audit/reporting debt until it is fully redesigned around the "
            "reset-stage schemas."
        ),
    ),
    ResetComponentEntry(
        old_name="broad hybrid adjudicator fallback",
        reset_stage="retired",
        new_family="do_not_port_broad_hybrid_fallback",
        portability_category="gan2026_specific",
        ablation_switch="retired_do_not_port_broad_hybrid_fallback",
        issue_or_rule_ids=("broad_hybrid_fallback_retired",),
        status="retired_do_not_port",
        notes=(
            "Explicitly rejected because it blurred selection, projection, and fallback ownership."
        ),
    ),
    ResetComponentEntry(
        old_name="broad state-graph projection",
        reset_stage="retired",
        new_family="do_not_port_broad_state_graph_projection",
        portability_category="seizure_frequency",
        ablation_switch="retired_do_not_port_broad_state_graph_projection",
        issue_or_rule_ids=("broad_state_graph_projection_retired",),
        status="retired_do_not_port",
        notes=(
            "Historical evidence is preserved, but broad projection replacement stays "
            "out of the reset path."
        ),
    ),
)


def build_reset_stage_component_inventory() -> dict[str, Any]:
    """Build the static reset-stage component crosswalk artifact."""

    entries = [asdict(entry) for entry in RESET_COMPONENT_ENTRIES]
    stage_counts = Counter(entry["reset_stage"] for entry in entries)
    portability_counts = Counter(entry["portability_category"] for entry in entries)
    status_counts = Counter(entry["status"] for entry in entries)

    return {
        "artifact_kind": "gan2026_reset_stage_component_inventory_v0",
        "date": "2026-06-06",
        "split_manifest": "gan2026_split_v1",
        "claim_boundary": (
            "Validation-development component inventory only. This artifact records "
            "how old Gan 2026 component families map into reset-stage owners, "
            "portability categories, and ablation switches. It authorizes no locked-test "
            "row-level inspection, no benchmark-comparable claim, and no whole-pipeline "
            "promotion."
        ),
        "source_artifacts": [
            "PROJECT_STATUS.md",
            "docs/research/contribution_thesis.md",
            "",
            "",
            "",
        ],
        "summary": {
            "component_families": len(entries),
            "by_stage": dict(sorted(stage_counts.items())),
            "by_portability_category": dict(sorted(portability_counts.items())),
            "by_status": dict(sorted(status_counts.items())),
            "ported_or_retained_families": sum(
                1 for entry in entries if str(entry["status"]).startswith(("ported", "retained"))
            ),
            "pending_policy_families": sum(
                1 for entry in entries if entry["status"] == "pending_policy_decision"
            ),
        },
        "inventory": entries,
        "next_question": (
            "Use this crosswalk to drive component-level ablation reporting and to keep "
            "future ports stage-owned instead of reviving broad fallback."
        ),
    }


def write_reset_stage_component_inventory_outputs(
    artifact: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    """Write JSON and Markdown outputs for the reset-stage inventory."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_reset_stage_component_inventory_report(artifact, markdown_path)


def write_reset_stage_component_inventory_report(artifact: Mapping[str, Any], path: Path) -> None:
    """Write a Markdown report for the reset-stage component inventory."""

    summary = artifact.get("summary", {})
    lines = [
        "# Gan 2026 Reset-Stage Component Inventory",
        "",
        str(artifact.get("claim_boundary")),
        "",
        f"- Split manifest: `{artifact.get('split_manifest')}`",
        f"- Component families: `{summary.get('component_families')}`",
        f"- Ported or retained families: `{summary.get('ported_or_retained_families')}`",
        f"- Pending policy families: `{summary.get('pending_policy_families')}`",
        "",
        "## Inventory",
        "",
        "| Old family | Reset stage | New family | Portability | Ablation switch | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in artifact.get("inventory", []):
        if not isinstance(entry, Mapping):
            continue
        lines.append(
            "| `{old_name}` | `{reset_stage}` | `{new_family}` | `{portability}` | "
            "`{switch}` | `{status}` |".format(
                old_name=entry.get("old_name"),
                reset_stage=entry.get("reset_stage"),
                new_family=entry.get("new_family"),
                portability=entry.get("portability_category"),
                switch=entry.get("ablation_switch"),
                status=entry.get("status"),
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "| New family | Issue or rule ids | Notes |",
            "| --- | --- | --- |",
        ]
    )
    for entry in artifact.get("inventory", []):
        if not isinstance(entry, Mapping):
            continue
        issue_ids = ", ".join(f"`{issue_id}`" for issue_id in entry.get("issue_or_rule_ids", ()))
        lines.append(f"| `{entry.get('new_family')}` | {issue_ids} | {entry.get('notes')} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The reset now has a durable crosswalk for what was ported, what remains "
            "audit-only, and what is explicitly retired. New deterministic behavior "
            "should add a portability category and named ablation switch before it is "
            "described as part of the reset architecture.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact = build_reset_stage_component_inventory()
    write_reset_stage_component_inventory_outputs(
        artifact,
        json_path=args.json,
        markdown_path=args.markdown,
    )
    print(
        json.dumps(
            {
                "json": str(args.json),
                "markdown": str(args.markdown),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
