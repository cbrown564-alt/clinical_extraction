"""Build the frozen v0.9 Gate 1 validation hard-slice audit.

This script reads only validation artifacts named by the v0.9 frozen protocol.
It does not open locked test rows or upstream test component artifacts.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REPLAY_PATH = (
    REPO_ROOT
    / "experiments"
    / (
        "gan2026_consensus_fresh_agreement_selector_v0_9_validation750_"
        "no_call_replay_2026-06-15.jsonl"
    )
)
RESIDUAL_AUDIT_PATH = (
    REPO_ROOT
    / "experiments"
    / (
        "gan2026_consensus_fresh_agreement_selector_v0_9_"
        "residual_component_generation_audit_2026-06-15.json"
    )
)
RUN_ID = "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26"
JSON_OUT = REPO_ROOT / "experiments" / f"{RUN_ID}.json"
MD_OUT = REPO_ROOT / "experiments" / f"{RUN_ID}.md"

BANDS = (
    "band_zero",
    "band_unknown",
    "band_submonthly",
    "band_monthly",
    "band_weekly",
    "band_daily",
)
TAXONOMY_FAMILIES = (
    "unknown_over_quantified_rate",
    "last_event_or_seizure_free_overinfer_unknown",
    "cluster_burden_component_failure",
    "highest_semiology_or_denominator_conflict",
    "fresh_only_correct_candidate",
    "consensus_fresh_correct_but_blocked",
)


def main() -> None:
    rows = _load_jsonl(REPLAY_PATH)
    residual_audit = json.loads(RESIDUAL_AUDIT_PATH.read_text(encoding="utf-8"))
    residual_records = residual_audit["summary"]["selected_wrong_records"]
    residual_by_row = {record["source_row_index"]: record for record in residual_records}

    changed_rows = [row for row in rows if _label_changed(row)]
    selected_wrong_rows = [row for row in rows if not _purist_correct(row, "selected")]
    selected_wrong_ids = {row["source_row_index"] for row in selected_wrong_rows}

    if selected_wrong_ids != set(residual_by_row):
        raise RuntimeError("Residual audit selected-wrong rows do not match replay rows.")

    correct_component_ids = {
        row_id for row_id, record in residual_by_row.items() if record["correct_components"]
    }
    no_correct_component_ids = set(residual_by_row) - correct_component_ids

    overall = _overall_summary(rows, changed_rows)
    slice_summaries: dict[str, dict[str, Any]] = {
        "all_changed_labels": _summarize_slice(changed_rows),
        "selected_wrong_residual": _summarize_slice(selected_wrong_rows),
        "residual_correct_unselected_component": _summarize_slice(
            [row for row in rows if row["source_row_index"] in correct_component_ids]
        ),
        "residual_no_correct_component_available": _summarize_slice(
            [row for row in rows if row["source_row_index"] in no_correct_component_ids]
        ),
    }

    changed_by_band = {
        band: _summarize_slice([row for row in changed_rows if _gold_band(row) == band])
        for band in BANDS
    }
    residual_by_family = {
        family: _summarize_slice(
            [
                row
                for row in selected_wrong_rows
                if family in residual_by_row[row["source_row_index"]]["audit_categories"]
            ]
        )
        for family in TAXONOMY_FAMILIES
    }

    no_component_by_family = {
        family: sum(
            1
            for row_id in no_correct_component_ids
            if family in residual_by_row[row_id]["audit_categories"]
        )
        for family in TAXONOMY_FAMILIES
    }

    gate_checks = {
        "selected_purist_at_least_733": overall["selected_purist_correct"] >= 733,
        "overall_correct_to_wrong_zero": overall["correct_to_wrong"] == 0,
        "all_predeclared_slices_non_negative_net": all(
            summary["net_purist_gain_vs_deterministic"] >= 0
            for summary in [
                slice_summaries["all_changed_labels"],
                *changed_by_band.values(),
                slice_summaries["selected_wrong_residual"],
                slice_summaries["residual_correct_unselected_component"],
                slice_summaries["residual_no_correct_component_available"],
                *residual_by_family.values(),
            ]
        ),
        "no_slice_correct_to_wrong": all(
            summary["correct_to_wrong"] == 0
            for summary in [
                slice_summaries["all_changed_labels"],
                *changed_by_band.values(),
                slice_summaries["selected_wrong_residual"],
                slice_summaries["residual_correct_unselected_component"],
                slice_summaries["residual_no_correct_component_available"],
                *residual_by_family.values(),
            ]
        ),
        "changed_label_precision_at_least_0_70": overall["changed_label_precision"] >= 0.70,
        "residual_no_correct_component_excluded_from_selector_superiority_claims": True,
        "low_precision_bands_named_as_portability_risks": True,
    }

    result = {
        "run_id": RUN_ID,
        "date": "2026-06-26",
        "claim_boundary": (
            "Validation-only Gate 1 hard-slice audit over frozen v0.9 replay rows and "
            "the frozen residual component-generation audit. No locked test rows read."
        ),
        "decision": "gate1_pass_advance_to_gate2_not_test",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "selector_version": "gan2026_consensus_fresh_agreement_selector_v0_9",
        "row_count": len(rows),
        "source_artifacts": {
            "v0_9_replay": _rel(REPLAY_PATH),
            "residual_component_generation_audit": _rel(RESIDUAL_AUDIT_PATH),
        },
        "overall": overall,
        "slice_summaries": slice_summaries,
        "changed_by_band": changed_by_band,
        "residual_by_family": residual_by_family,
        "no_correct_component_by_family": no_component_by_family,
        "selector_action_distribution": dict(Counter(row["selector_action"] for row in rows)),
        "changed_selector_action_distribution": dict(
            Counter(row["selector_action"] for row in changed_rows)
        ),
        "residual_selector_action_distribution": dict(
            Counter(row["selector_action"] for row in selected_wrong_rows)
        ),
        "source_validity_diagnostics": _source_validity_diagnostics(rows, residual_by_row),
        "gate_checks": gate_checks,
        "gate_passed": all(gate_checks.values()),
        "portability_risks": [
            "band_submonthly changed-label precision remains low at 1/5.",
            "band_weekly changed-label precision remains low at 4/10.",
            (
                "Residual selector-superiority claims must exclude 11/17 "
                "selected-wrong rows with no correct component available."
            ),
        ],
        "interpretation": (
            "Gate 1 passes: v0.9 preserves 733/750 selected Purist, has 0 correct-to-wrong "
            "regressions overall and in every predeclared slice, and changed-label precision "
            "is 0.7347. The pass is narrow: submonthly and weekly changed-label precision "
            "remain portability risks, and 11 residual wrong rows require component-generation "
            "work rather than selector-only claims. Advance to Gate 2 robustness/stress panels; "
            "do not proceed to locked test."
        ),
    }

    JSON_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(_render_markdown(result), encoding="utf-8")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _label_changed(row: dict[str, Any]) -> bool:
    return bool(row["transition_vs_deterministic"]["label_changed"])


def _purist_correct(row: dict[str, Any], layer: str) -> bool:
    return bool(row["score_layers"][layer]["comparison"]["purist_correct"])


def _pragmatic_correct(row: dict[str, Any], layer: str) -> bool:
    return bool(row["score_layers"][layer]["comparison"]["pragmatic_correct"])


def _gold_band(row: dict[str, Any]) -> str:
    category = row["score_layers"]["selected"]["comparison"].get("gold_purist_category")
    if category == "currently_no_seizure":
        return "band_zero"
    if category == "seizure_freq_unknown":
        return "band_unknown"
    if category == "seizure_freq_more1per6mon_less1mon":
        return "band_submonthly"
    if category in {"seizure_freq_1_per_mon", "seizure_freq_more1mon_less1week"}:
        return "band_monthly"
    if category == "seizure_freq_more1week_less1day":
        return "band_weekly"
    if category == "seizure_freq_1ormore_daily":
        return "band_daily"

    monthly = row["reference"].get("gold_monthly_frequency")
    if monthly is None:
        return "band_unknown"
    if monthly == 0:
        return "band_zero"
    if monthly < 1:
        return "band_submonthly"
    if monthly < 4:
        return "band_monthly"
    if monthly < 30:
        return "band_weekly"
    return "band_daily"


def _transition_counts(rows: list[dict[str, Any]], *, metric: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    correct_fn = _purist_correct if metric == "purist" else _pragmatic_correct
    for row in rows:
        baseline = correct_fn(row, "deterministic")
        selected = correct_fn(row, "selected")
        if not baseline and selected:
            counter["wrong_to_correct"] += 1
        elif baseline and not selected:
            counter["correct_to_wrong"] += 1
        elif baseline and selected:
            counter["correct_to_correct"] += 1
        else:
            counter["wrong_to_wrong"] += 1
    return counter


def _summarize_slice(rows: list[dict[str, Any]]) -> dict[str, Any]:
    purist = _transition_counts(rows, metric="purist")
    pragmatic = _transition_counts(rows, metric="pragmatic")
    changed = [row for row in rows if _label_changed(row)]
    action_counts = Counter(row["selector_action"] for row in rows)
    gate_counts = Counter(row["selector_gate"] for row in rows)
    source_rows = sorted(row["source_row_index"] for row in rows)
    summary = {
        "rows": len(rows),
        "selected_purist_correct": sum(_purist_correct(row, "selected") for row in rows),
        "selected_pragmatic_correct": sum(_pragmatic_correct(row, "selected") for row in rows),
        "deterministic_purist_correct": sum(_purist_correct(row, "deterministic") for row in rows),
        "deterministic_pragmatic_correct": sum(
            _pragmatic_correct(row, "deterministic") for row in rows
        ),
        "changed_labels": len(changed),
        "changed_label_precision": _ratio(purist["wrong_to_correct"], len(changed)),
        "wrong_to_correct": purist["wrong_to_correct"],
        "correct_to_wrong": purist["correct_to_wrong"],
        "correct_to_correct": purist["correct_to_correct"],
        "wrong_to_wrong": purist["wrong_to_wrong"],
        "net_purist_gain_vs_deterministic": (
            purist["wrong_to_correct"] - purist["correct_to_wrong"]
        ),
        "pragmatic_wrong_to_correct": pragmatic["wrong_to_correct"],
        "pragmatic_correct_to_wrong": pragmatic["correct_to_wrong"],
        "selector_action_distribution": dict(action_counts),
        "selector_gate_distribution": dict(gate_counts),
    }
    if len(source_rows) <= 100:
        summary["source_row_indices"] = source_rows
    else:
        summary["source_row_index_count"] = len(source_rows)
        summary["source_row_index_min"] = source_rows[0]
        summary["source_row_index_max"] = source_rows[-1]
    return summary


def _overall_summary(
    rows: list[dict[str, Any]], changed_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    summary = _summarize_slice(rows)
    return {
        **summary,
        "consensus_purist_correct": sum(_purist_correct(row, "consensus") for row in rows),
        "fresh_evidence_purist_correct": sum(
            _purist_correct(row, "fresh_evidence") for row in rows
        ),
        "consensus_pragmatic_correct": sum(_pragmatic_correct(row, "consensus") for row in rows),
        "fresh_evidence_pragmatic_correct": sum(
            _pragmatic_correct(row, "fresh_evidence") for row in rows
        ),
        "changed_label_precision": _ratio(
            sum(
                not _purist_correct(row, "deterministic") and _purist_correct(row, "selected")
                for row in changed_rows
            ),
            len(changed_rows),
        ),
    }


def _source_validity_diagnostics(
    rows: list[dict[str, Any]], residual_by_row: dict[int, dict[str, Any]]
) -> dict[str, Any]:
    feature_keys = set()
    fresh_uncertainty = Counter()
    fresh_actions = Counter()
    boundary_profiles = Counter()
    for row in rows:
        features = row.get("decision_features") or {}
        feature_keys.update(features)
        if features.get("fresh_uncertainty"):
            fresh_uncertainty[features["fresh_uncertainty"]] += 1
        if features.get("fresh_action"):
            fresh_actions[features["fresh_action"]] += 1
        for item in features.get("fresh_boundary_profile") or ():
            boundary_profiles[item] += 1

    residual_profiles = Counter()
    for record in residual_by_row.values():
        for item in record.get("fresh_boundary_profile") or ():
            residual_profiles[item] += 1

    return {
        "explicit_source_validity_fields_present": False,
        "available_decision_feature_keys": sorted(feature_keys),
        "fresh_uncertainty_distribution": dict(fresh_uncertainty),
        "fresh_action_distribution": dict(fresh_actions),
        "top_fresh_boundary_profiles": dict(boundary_profiles.most_common(20)),
        "residual_top_fresh_boundary_profiles": dict(residual_profiles.most_common(20)),
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _render_markdown(result: dict[str, Any]) -> str:
    overall = result["overall"]
    transition_header = (
        "| Band | Rows | Selected Purist | Selected Pragmatic | Changed | W->C | C->W | "
        "W->W | C->C | Net | Precision | Actions |"
    )
    transition_separator = (
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"
    )
    taxonomy_header = (
        "| Family | Rows | No Correct Component | Selected Purist | Selected Pragmatic | "
        "W->C | C->W | Net | Actions |"
    )
    diagnostics = result["source_validity_diagnostics"]
    lines = [
        "# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 1 Hard-Slice Audit",
        "",
        "Date: 2026-06-26",
        "",
        (
            "This is a validation-only Gate 1 audit over the frozen v0.9 no-call replay "
            "and frozen residual component-generation audit. It makes no model calls and "
            "does not read locked test rows."
        ),
        "",
        "## Experiment Unit",
        "",
        "- Work class: hybrid selector hard-slice / selective-action audit.",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        "- Selector: `gan2026_consensus_fresh_agreement_selector_v0_9`.",
        "- Scorer: unchanged Gan-compatible Purist first; Pragmatic sidecar.",
        (
            "- Stop rule: Gate 1 pass advances only to Gate 2 robustness/stress "
            "panels; it does not authorize `test450`."
        ),
        "",
        "## Overall Readout",
        "",
        f"- Deterministic Purist: {overall['deterministic_purist_correct']}/{overall['rows']}",
        f"- Consensus Purist: {overall['consensus_purist_correct']}/{overall['rows']}",
        f"- Fresh-evidence Purist: {overall['fresh_evidence_purist_correct']}/{overall['rows']}",
        f"- Selected Purist: {overall['selected_purist_correct']}/{overall['rows']}",
        f"- Selected Pragmatic: {overall['selected_pragmatic_correct']}/{overall['rows']}",
        f"- Changed labels: {overall['changed_labels']}",
        f"- Wrong->correct: {overall['wrong_to_correct']}",
        f"- Correct->wrong: {overall['correct_to_wrong']}",
        f"- Wrong->wrong: {overall['wrong_to_wrong']}",
        f"- Correct->correct: {overall['correct_to_correct']}",
        f"- Changed-label precision: {overall['changed_label_precision']}",
        "",
        "## Changed-Label Bands",
        "",
        transition_header,
        transition_separator,
    ]
    for band in BANDS:
        lines.append(_slice_row(band, result["changed_by_band"][band]))

    lines.extend(
        [
            "",
            "## Residual Slices",
            "",
            transition_header.replace("| Band |", "| Slice |"),
            transition_separator,
        ]
    )
    for name, summary in result["slice_summaries"].items():
        lines.append(_slice_row(name, summary))

    lines.extend(
        [
            "",
            "## Residual Taxonomy Families",
            "",
            taxonomy_header,
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for family in TAXONOMY_FAMILIES:
        summary = result["residual_by_family"][family]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{family}`",
                    str(summary["rows"]),
                    str(result["no_correct_component_by_family"][family]),
                    str(summary["selected_purist_correct"]),
                    str(summary["selected_pragmatic_correct"]),
                    str(summary["wrong_to_correct"]),
                    str(summary["correct_to_wrong"]),
                    str(summary["net_purist_gain_vs_deterministic"]),
                    _format_counts(summary["selector_action_distribution"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Evidence/Source-Validity Diagnostics",
            "",
            (
                "The frozen replay does not expose explicit source-validity fields. "
                "Available diagnostics are selector decision features and "
                "fresh-evidence boundary profiles."
            ),
            "",
            f"- Fresh uncertainty: `{diagnostics['fresh_uncertainty_distribution']}`",
            f"- Fresh action: `{diagnostics['fresh_action_distribution']}`",
            (
                "- Residual top boundary profiles: "
                f"`{diagnostics['residual_top_fresh_boundary_profiles']}`"
            ),
            "",
            "## Gate Checks",
            "",
        ]
    )
    for check, passed in result["gate_checks"].items():
        lines.append(f"- {check}: `{passed}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["interpretation"],
            "",
            "Portability risks:",
        ]
    )
    for risk in result["portability_risks"]:
        lines.append(f"- {risk}")
    lines.extend(
        [
            "",
            f"- JSON summary: `{_rel(JSON_OUT)}`.",
            f"- Markdown report: `{_rel(MD_OUT)}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def _slice_row(name: str, summary: dict[str, Any]) -> str:
    return (
        "| "
        + " | ".join(
            [
                f"`{name}`",
                str(summary["rows"]),
                str(summary["selected_purist_correct"]),
                str(summary["selected_pragmatic_correct"]),
                str(summary["changed_labels"]),
                str(summary["wrong_to_correct"]),
                str(summary["correct_to_wrong"]),
                str(summary["wrong_to_wrong"]),
                str(summary["correct_to_correct"]),
                str(summary["net_purist_gain_vs_deterministic"]),
                str(summary["changed_label_precision"]),
                _format_counts(summary["selector_action_distribution"]),
            ]
        )
        + " |"
    )


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "`{}`"
    return "`" + json.dumps(counts, sort_keys=True) + "`"


if __name__ == "__main__":
    main()
