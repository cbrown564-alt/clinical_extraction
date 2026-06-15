"""Validation-only selector that requires fresh-evidence agreement.

The 2026-06-14 next-phase brief showed that exact multi-agent consensus was a
weak action trigger by itself: it improved validation but had low changed-label
precision and inherited the deterministic floor's distribution-shift risk. This
module tests a narrower selector over saved validation artifacts:

* keep the deterministic/rules-tool baseline by default;
* accept a consensus switch only when V12 fresh-evidence reasoning independently
  emits the same final label as the consensus candidate.

The selector is a no-call replay instrument. Gold labels are used only after the
decision, for scoring and validation-band reporting.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    BOUNDARY_BANDS,
    boundary_band,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PIPELINE_FAMILY = "consensus_fresh_agreement_selector"
SELECTOR_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_1"
SELECTOR_V0_2_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_2"
SELECTOR_V0_3_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_3"
SELECTOR_V0_4_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_4"
SELECTOR_V0_5_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_5"
SELECTOR_V0_6_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_6"
SELECTOR_V0_7_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_7"
SELECTOR_V0_8_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_8"
SELECTOR_V0_9_VERSION = "gan2026_consensus_fresh_agreement_selector_v0_9"
SelectorPolicy = Literal[
    "fresh_agreement_v0_1",
    "nonboundary_precision_v0_2",
    "specific_label_precision_v0_3",
    "cluster_cadence_precision_v0_4",
    "fresh_boundary_rescue_v0_5",
    "profile_guard_boundary_rescue_v0_6",
    "unknown_count_window_rescue_v0_7",
    "parseable_denominator_window_refinement_v0_8",
    "semantic_equiv_unknown_uncertainty_v0_9",
]


def build_selector_rows(
    *,
    deterministic_rows: Sequence[Mapping[str, Any]],
    consensus_rows: Sequence[Mapping[str, Any]],
    fresh_evidence_rows: Sequence[Mapping[str, Any]],
    policy: SelectorPolicy = "fresh_agreement_v0_1",
) -> list[dict[str, Any]]:
    """Build selector replay rows aligned by ``source_row_index``."""

    deterministic_by_id = _rows_by_source_index(deterministic_rows)
    consensus_by_id = _rows_by_source_index(consensus_rows)
    fresh_by_id = _rows_by_source_index(fresh_evidence_rows)
    common_ids = sorted(
        set(deterministic_by_id) & set(consensus_by_id) & set(fresh_by_id)
    )
    return [
        _build_selector_row(
            source_row_index=source_row_index,
            deterministic_row=deterministic_by_id[source_row_index],
            consensus_row=consensus_by_id[source_row_index],
            fresh_evidence_row=fresh_by_id[source_row_index],
            policy=policy,
        )
        for source_row_index in common_ids
    ]


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize selector performance and changed-label precision."""

    transitions = Counter(_dig(row, ("transition_vs_deterministic", "purist"))
                          for row in rows)
    changed_rows = sum(
        1
        for row in rows
        if _dig(row, ("transition_vs_deterministic", "label_changed")) is True
    )
    wrong_to_correct = transitions["wrong_to_correct"]
    correct_to_wrong = transitions["correct_to_wrong"]
    return {
        "selector": _selector_version(rows),
        "rows": len(rows),
        "deterministic_purist_correct": sum(
            _dig(row, ("score_layers", "deterministic", "comparison", "purist_correct"))
            is True
            for row in rows
        ),
        "consensus_purist_correct": sum(
            _dig(row, ("score_layers", "consensus", "comparison", "purist_correct"))
            is True
            for row in rows
        ),
        "fresh_evidence_purist_correct": sum(
            _dig(row, ("score_layers", "fresh_evidence", "comparison", "purist_correct"))
            is True
            for row in rows
        ),
        "selected_purist_correct": sum(
            _dig(row, ("score_layers", "selected", "comparison", "purist_correct"))
            is True
            for row in rows
        ),
        "changed_labels": changed_rows,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "correct_to_correct": transitions["correct_to_correct"],
        "wrong_to_wrong": transitions["wrong_to_wrong"],
        "changed_label_precision": (
            round(wrong_to_correct / changed_rows, 4) if changed_rows else None
        ),
        "net_purist_gain_vs_deterministic": wrong_to_correct - correct_to_wrong,
        "actions": dict(Counter(str(row.get("selector_action")) for row in rows)),
        "summary_by_band": summarize_by_band(rows),
        "claim_boundary": (
            "Validation-only no-call selector over saved deterministic, consensus, "
            "and V12 fresh-evidence artifacts. Gold labels are used only for "
            "post-hoc scoring and band summaries; this is not a holdout result."
        ),
    }


def summarize_by_band(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Report canonical validation boundary-band transitions."""

    bands: dict[str, dict[str, Any]] = {}
    for band in BOUNDARY_BANDS:
        band_rows = [
            row
            for row in rows
            if boundary_band(
                _dig(row, ("reference", "gold_monthly_frequency"))
            )
            == band
        ]
        changed = [
            row
            for row in band_rows
            if _dig(row, ("transition_vs_deterministic", "label_changed")) is True
        ]
        wrong_to_correct = sum(
            _dig(row, ("transition_vs_deterministic", "purist"))
            == "wrong_to_correct"
            for row in changed
        )
        correct_to_wrong = sum(
            _dig(row, ("transition_vs_deterministic", "purist"))
            == "correct_to_wrong"
            for row in changed
        )
        bands[band] = {
            "rows": len(band_rows),
            "deterministic_purist_correct": sum(
                _dig(row, ("score_layers", "deterministic", "comparison", "purist_correct"))
                is True
                for row in band_rows
            ),
            "selected_purist_correct": sum(
                _dig(row, ("score_layers", "selected", "comparison", "purist_correct"))
                is True
                for row in band_rows
            ),
            "changed_labels": len(changed),
            "wrong_to_correct": wrong_to_correct,
            "correct_to_wrong": correct_to_wrong,
            "net_purist_gain": wrong_to_correct - correct_to_wrong,
            "changed_label_precision": (
                round(wrong_to_correct / len(changed), 4) if changed else None
            ),
        }
    return bands


def write_report(
    rows: Sequence[Mapping[str, Any]],
    path: Path,
    *,
    jsonl_path: Path,
    source_artifacts: Mapping[str, str],
) -> None:
    """Write a compact Markdown report for the selector replay."""

    summary = summarize_rows(rows)
    bands = dict(summary["summary_by_band"])
    selector_description = _description_text_for_selector(str(summary["selector"]))
    lines = [
        "# Gan 2026 Consensus + Fresh Agreement Selector",
        "",
        "Date: 2026-06-15",
        "",
        selector_description,
        "",
        "## Experiment Unit",
        "",
        f"- Selector: `{summary['selector']}`.",
        "- Work class: hybrid selector / saved-output replay.",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        "- Row policy: aligned source rows present in all three source artifacts.",
        "- Scorer: Gan-compatible Purist, unchanged.",
        "- Inspection policy: validation aggregate and validation-band summaries.",
        "- Stop rule: promote only if gains are robust by band and changed-label "
        "precision is high enough for a holdout-facing freeze; otherwise revise.",
        "",
        "## Source Artifacts",
        "",
    ]
    for name, artifact_path in sorted(source_artifacts.items()):
        lines.append(f"- `{name}`: `{artifact_path}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            (
                f"- Deterministic Purist: "
                f"{summary['deterministic_purist_correct']}/{summary['rows']}"
            ),
            (
                f"- Consensus Purist: "
                f"{summary['consensus_purist_correct']}/{summary['rows']}"
            ),
            (
                f"- V12 fresh-evidence Purist: "
                f"{summary['fresh_evidence_purist_correct']}/{summary['rows']}"
            ),
            (
                f"- Selected Purist: "
                f"{summary['selected_purist_correct']}/{summary['rows']}"
            ),
            (
                f"- Net Purist gain vs deterministic: "
                f"{summary['net_purist_gain_vs_deterministic']}"
            ),
            f"- Changed labels: {summary['changed_labels']}",
            f"- Wrong->correct: {summary['wrong_to_correct']}",
            f"- Correct->wrong: {summary['correct_to_wrong']}",
            (
                f"- Changed-label precision: "
                f"{summary['changed_label_precision']}"
            ),
            f"- Actions: `{summary['actions']}`",
            f"- JSONL artifact: `{jsonl_path}`",
            "",
            "## Boundary Bands",
            "",
            (
                "| Band | Rows | Deterministic | Selected | Net | Changed | "
                "W->C | C->W | Precision |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for band in BOUNDARY_BANDS:
        info = bands[band]
        lines.append(
            f"| `{band}` | {info['rows']} | "
            f"{info['deterministic_purist_correct']} | "
            f"{info['selected_purist_correct']} | "
            f"{info['net_purist_gain']} | "
            f"{info['changed_labels']} | "
            f"{info['wrong_to_correct']} | "
            f"{info['correct_to_wrong']} | "
            f"{info['changed_label_precision']} |"
        )
    decision = _decision_text_for_selector(str(summary["selector"]))
    lines.extend(
        [
            "",
            "## Decision",
            "",
            decision,
        ]
    )
    write_markdown_report(path, lines)


def _decision_text_for_selector(selector_version: str) -> str:
    if selector_version == SELECTOR_V0_5_VERSION:
        return (
            "Revise, not freeze. v0.5 adds a narrow fresh-evidence boundary "
            "rescue on top of v0.4 for deterministic seizure-free/no-reference "
            "overreach. It needs targeted robustness evidence before any "
            "holdout-facing claim."
        )
    if selector_version == SELECTOR_V0_6_VERSION:
        return (
            "Revise, not freeze. v0.6 keeps the v0.5 boundary rescue but "
            "requires the fresh-evidence boundary profile to support the "
            "specific rescue. It remains validation-only replay evidence."
        )
    if selector_version == SELECTOR_V0_7_VERSION:
        return (
            "Revise, not freeze. v0.7 keeps the v0.6 profile-guard boundary "
            "rescue and adds a narrow deterministic-unknown rescue for "
            "explicit count plus usable window profiles. It remains "
            "validation-only replay evidence."
        )
    if selector_version == SELECTOR_V0_8_VERSION:
        return (
            "Revise, not freeze. v0.8 keeps the v0.7 boundary and unknown "
            "guards, then adds a narrow parseable denominator/window refinement "
            "for consensus+fresh labels previously gated as ambiguous `other`. "
            "It remains validation-only replay evidence."
        )
    if selector_version == SELECTOR_V0_9_VERSION:
        return (
            "Revise, not freeze. v0.9 keeps the v0.8 selector and adds two "
            "narrow rescues: normalized-equivalent consensus/fresh disagreement "
            "and specific-rate-to-unknown uncertainty. It remains validation-only "
            "replay evidence."
        )
    if selector_version == SELECTOR_V0_4_VERSION:
        return (
            "Revise, not freeze. v0.4 removes the remaining validation "
            "correct-to-wrong regressions from v0.3 and improves weekly-band "
            "net gain, but it is still a validation-only saved-output replay "
            "and needs a predeclared hard-slice or frozen protocol before any "
            "holdout-facing claim."
        )
    if selector_version == SELECTOR_V0_3_VERSION:
        return (
            "Revise, not freeze. v0.3 restores the v0.1 aggregate gain while "
            "substantially improving changed-label precision, but weekly-band "
            "precision remains weak and this is still validation-only saved-output "
            "replay evidence, not a holdout-facing frozen candidate."
        )
    return (
        "Revise, not freeze. The selector improves validation aggregate "
        "performance, but changed-label precision remains low outside "
        "`band_daily`, so it does not satisfy the precision-first promotion "
        "rule from the next-phase brief."
    )


def _description_text_for_selector(selector_version: str) -> str:
    if selector_version == SELECTOR_V0_5_VERSION:
        return (
            "This is a validation-only no-call selector replay. It starts from "
            "v0.4 consensus+fresh agreement and adds a narrow V12 fresh-evidence "
            "boundary rescue for deterministic seizure-free/no-reference "
            "overreach."
        )
    if selector_version == SELECTOR_V0_6_VERSION:
        return (
            "This is a validation-only no-call selector replay. It starts from "
            "v0.5 fresh boundary rescue and adds a gold-free boundary-profile "
            "guard before accepting fresh seizure-free/no-reference rescues."
        )
    if selector_version == SELECTOR_V0_7_VERSION:
        return (
            "This is a validation-only no-call selector replay. It starts from "
            "v0.6 profile-guard boundary rescue and adds a narrow unknown-origin "
            "rescue for fresh profiles with explicit count plus usable window."
        )
    if selector_version == SELECTOR_V0_8_VERSION:
        return (
            "This is a validation-only no-call selector replay. It starts from "
            "v0.7 and adds a narrow parseable denominator/window refinement for "
            "fresh profiles that support current count/window labels."
        )
    if selector_version == SELECTOR_V0_9_VERSION:
        return (
            "This is a validation-only no-call selector replay. It starts from "
            "v0.8 and adds normalized-equivalent agreement plus explicit "
            "unknown-uncertainty rescues."
        )
    return (
        "This is a validation-only no-call selector replay. It keeps the "
        "deterministic baseline unless exact structured-event consensus proposes "
        "a different label and V12 fresh-evidence reasoning independently emits "
        "that same label."
    )


def _accept_specific_label_precision_v0_3(
    *,
    deterministic_label: str,
    consensus_label: str,
) -> tuple[bool, str]:
    deterministic_unit = _label_unit(deterministic_label)
    consensus_unit = _label_unit(consensus_label)
    if deterministic_unit in {"no_reference", "unknown"}:
        return False, (
            "specific_label_precision_v0_3:"
            f"deterministic_boundary_origin:{deterministic_unit}"
        )
    if consensus_unit in {"unknown", "seizure_free", "other"}:
        return False, (
            "specific_label_precision_v0_3:"
            f"uncertain_or_ambiguous_replacement:{consensus_unit}"
        )
    return True, "specific_label_precision_v0_3"


def _accept_cluster_cadence_precision_v0_4(
    *,
    deterministic_label: str,
    consensus_label: str,
) -> tuple[bool, str]:
    accept_v03, gate = _accept_specific_label_precision_v0_3(
        deterministic_label=deterministic_label,
        consensus_label=consensus_label,
    )
    if not accept_v03:
        return False, gate.replace(
            "specific_label_precision_v0_3", "cluster_cadence_precision_v0_4"
        )
    deterministic_has_cluster = _has_cluster_label(deterministic_label)
    consensus_has_cluster = _has_cluster_label(consensus_label)
    if deterministic_has_cluster and not consensus_has_cluster:
        return False, "cluster_cadence_precision_v0_4:cluster_label_demoted"
    if deterministic_has_cluster and consensus_has_cluster:
        deterministic_cadence = _cluster_cadence(deterministic_label)
        consensus_cadence = _cluster_cadence(consensus_label)
        if deterministic_cadence != consensus_cadence:
            return False, "cluster_cadence_precision_v0_4:cluster_cadence_changed"
    return True, "cluster_cadence_precision_v0_4"


def _accept_base_consensus_v0_8(
    *,
    deterministic_label: str,
    consensus_label: str,
) -> tuple[bool, str]:
    accept_v04, gate = _accept_cluster_cadence_precision_v0_4(
        deterministic_label=deterministic_label,
        consensus_label=consensus_label,
    )
    if not accept_v04:
        return False, gate.replace(
            "cluster_cadence_precision_v0_4",
            "parseable_denominator_window_refinement_v0_8",
            1,
        )
    replacement_unit = _label_unit(consensus_label)
    if replacement_unit in {"day", "week", "month", "year"} and not (
        _parseable_frequency_label(consensus_label)
    ):
        return False, (
            "parseable_denominator_window_refinement_v0_8:"
            "replacement_not_parseable_specific_rate"
        )
    return True, "parseable_denominator_window_refinement_v0_8:base_consensus"


def _has_cluster_label(label: str) -> bool:
    return "cluster" in label.strip().lower()


def _cluster_cadence(label: str) -> tuple[str, str, str] | None:
    match = re.search(
        r"(?P<count>\d+(?:\s+to\s+\d+)?)\s+clusters?\s+per\s+"
        r"(?:(?P<denominator>\d+)\s+)?(?P<unit>day|week|month|year)",
        label.strip().lower(),
    )
    if match is None:
        return None
    return (
        match.group("count"),
        match.group("denominator") or "1",
        match.group("unit"),
    )


def _build_selector_row(
    *,
    source_row_index: int,
    deterministic_row: Mapping[str, Any],
    consensus_row: Mapping[str, Any],
    fresh_evidence_row: Mapping[str, Any],
    policy: SelectorPolicy,
) -> dict[str, Any]:
    deterministic_label = str(deterministic_row.get("final_label") or "")
    consensus_label = str(consensus_row.get("consensus_final_label") or "")
    fresh_label = str(
        _dig(fresh_evidence_row, ("decision_record", "final_label")) or ""
    )
    consensus_policy = _consensus_policy_for(policy)
    accept_consensus, selector_gate = _accept_consensus_switch(
        policy=consensus_policy,
        deterministic_label=deterministic_label,
        consensus_label=consensus_label,
        fresh_label=fresh_label,
    )
    accept_fresh_rescue = False
    rescue_action = "accept_fresh_boundary_rescue"
    fresh_boundary_profile = (
        _dig(
            fresh_evidence_row,
            ("fresh_evidence_decision_record", "boundary_profile"),
        )
        or []
    )
    if not accept_consensus and policy == "fresh_boundary_rescue_v0_5":
        accept_fresh_rescue, selector_gate = _accept_fresh_boundary_rescue_v0_5(
            deterministic_label=deterministic_label,
            fresh_label=fresh_label,
            prior_gate=selector_gate,
        )
    if not accept_consensus and policy in {
        "profile_guard_boundary_rescue_v0_6",
        "unknown_count_window_rescue_v0_7",
        "parseable_denominator_window_refinement_v0_8",
        "semantic_equiv_unknown_uncertainty_v0_9",
    }:
        accept_fresh_rescue, selector_gate = _accept_fresh_boundary_rescue_v0_6(
            deterministic_label=deterministic_label,
            fresh_label=fresh_label,
            fresh_boundary_profile=fresh_boundary_profile,
            prior_gate=selector_gate,
        )
    if (
        not accept_consensus
        and not accept_fresh_rescue
        and policy in {
            "unknown_count_window_rescue_v0_7",
            "parseable_denominator_window_refinement_v0_8",
            "semantic_equiv_unknown_uncertainty_v0_9",
        }
    ):
        accept_fresh_rescue, selector_gate = _accept_unknown_count_window_rescue_v0_7(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
            fresh_label=fresh_label,
            fresh_boundary_profile=fresh_boundary_profile,
            prior_gate=selector_gate,
        )
        rescue_action = "accept_unknown_count_window_rescue"
    if (
        not accept_consensus
        and not accept_fresh_rescue
        and policy in {
            "parseable_denominator_window_refinement_v0_8",
            "semantic_equiv_unknown_uncertainty_v0_9",
        }
    ):
        accept_fresh_rescue, selector_gate = (
            _accept_parseable_denominator_window_refinement_v0_8(
                deterministic_label=deterministic_label,
                consensus_label=consensus_label,
                fresh_label=fresh_label,
                fresh_boundary_profile=fresh_boundary_profile,
                prior_gate=selector_gate,
            )
        )
        rescue_action = "accept_parseable_denominator_window_refinement"
    if (
        not accept_consensus
        and not accept_fresh_rescue
        and policy == "semantic_equiv_unknown_uncertainty_v0_9"
    ):
        accept_fresh_rescue, selector_gate, rescue_action = (
            _accept_semantic_equiv_unknown_uncertainty_v0_9(
                deterministic_label=deterministic_label,
                consensus_label=consensus_label,
                fresh_label=fresh_label,
                fresh_boundary_profile=fresh_boundary_profile,
                prior_gate=selector_gate,
            )
        )
    if accept_consensus:
        selected_label = consensus_label
        selected_layer = _score_layer(
            "consensus", consensus_label, consensus_row.get("consensus_comparison")
        )
        selector_action = "accept_consensus_fresh_agreement"
    elif accept_fresh_rescue:
        selected_label = fresh_label
        selected_layer = _score_layer(
            "fresh_evidence",
            fresh_label,
            _dig(fresh_evidence_row, ("score_layers", "final", "comparison")),
        )
        selector_action = rescue_action
    else:
        selected_label = deterministic_label
        selected_layer = _score_layer(
            "deterministic",
            deterministic_label,
            deterministic_row.get("comparison"),
        )
        selector_action = "keep_deterministic_baseline"
    deterministic_correct = _dig(
        deterministic_row, ("comparison", "purist_correct")
    ) is True
    selected_correct = _dig(selected_layer, ("comparison", "purist_correct")) is True
    label_changed = selected_label != deterministic_label
    return {
        "source_row_index": source_row_index,
        "pipeline_family": PIPELINE_FAMILY,
        "selector_version": _policy_version(policy),
        "selector_action": selector_action,
        "selector_gate": selector_gate,
        "deterministic_label": deterministic_label,
        "consensus_label": consensus_label,
        "fresh_evidence_label": fresh_label,
        "selected_label": selected_label,
        "score_layers": {
            "deterministic": _score_layer(
                "deterministic",
                deterministic_label,
                deterministic_row.get("comparison"),
            ),
            "consensus": _score_layer(
                "consensus",
                consensus_label,
                consensus_row.get("consensus_comparison"),
            ),
            "fresh_evidence": _score_layer(
                "fresh_evidence",
                fresh_label,
                _dig(fresh_evidence_row, ("score_layers", "final", "comparison")),
            ),
            "selected": selected_layer,
        },
        "transition_vs_deterministic": {
            "label_changed": label_changed,
            "purist": _purist_transition(
                baseline_correct=deterministic_correct,
                selected_correct=selected_correct,
                label_changed=label_changed,
            ),
        },
        "reference": {
            "gold_label": _dig(deterministic_row, ("reference", "gold_label")),
            "gold_monthly_frequency": _dig(
                deterministic_row, ("reference", "gold_monthly_frequency")
            ),
            "row_ok": _dig(deterministic_row, ("reference", "row_ok")),
        },
        "decision_features": {
            "consensus_reason": _dig(
                consensus_row, ("consensus_decision", "reason")
            ),
            "fresh_action": _dig(
                fresh_evidence_row, ("fresh_evidence_decision_record", "action")
            ),
            "fresh_uncertainty": _dig(
                fresh_evidence_row,
                ("fresh_evidence_decision_record", "uncertainty"),
            ),
            "fresh_boundary_profile": _dig(
                fresh_evidence_row,
                ("fresh_evidence_decision_record", "boundary_profile"),
            )
            or [],
        },
    }


def _accept_consensus_switch(
    *,
    policy: SelectorPolicy,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
) -> tuple[bool, str]:
    if not consensus_label:
        return False, "missing_consensus_label"
    if consensus_label == deterministic_label:
        return False, "consensus_matches_deterministic"
    if fresh_label != consensus_label:
        return False, "fresh_evidence_disagrees_with_consensus"
    if policy == "fresh_agreement_v0_1":
        return True, "fresh_agreement_v0_1"
    if policy == "nonboundary_precision_v0_2":
        deterministic_unit = _label_unit(deterministic_label)
        consensus_unit = _label_unit(consensus_label)
        if deterministic_unit == "no_reference":
            return False, "nonboundary_precision_v0_2:deterministic_no_reference_origin"
        if consensus_unit in {"unknown", "seizure_free"}:
            return False, f"nonboundary_precision_v0_2:boundary_replacement:{consensus_unit}"
        return True, "nonboundary_precision_v0_2"
    if policy == "specific_label_precision_v0_3":
        return _accept_specific_label_precision_v0_3(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
        )
    if policy == "cluster_cadence_precision_v0_4":
        return _accept_cluster_cadence_precision_v0_4(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
        )
    if policy in {
        "fresh_boundary_rescue_v0_5",
        "profile_guard_boundary_rescue_v0_6",
        "unknown_count_window_rescue_v0_7",
    }:
        return _accept_cluster_cadence_precision_v0_4(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
        )
    if policy == "parseable_denominator_window_refinement_v0_8":
        return _accept_base_consensus_v0_8(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
        )
    if policy == "semantic_equiv_unknown_uncertainty_v0_9":
        accept_v08, gate = _accept_base_consensus_v0_8(
            deterministic_label=deterministic_label,
            consensus_label=consensus_label,
        )
        return accept_v08, gate.replace(
            "parseable_denominator_window_refinement_v0_8",
            "semantic_equiv_unknown_uncertainty_v0_9",
            1,
        )
    raise ValueError(f"unknown selector policy: {policy}")


def _accept_fresh_boundary_rescue_v0_5(
    *,
    deterministic_label: str,
    fresh_label: str,
    prior_gate: str,
) -> tuple[bool, str]:
    deterministic_unit = _label_unit(deterministic_label)
    fresh_unit = _label_unit(fresh_label)
    if deterministic_unit == "seizure_free" and fresh_unit in {
        "unknown",
        "no_reference",
    }:
        return (
            True,
            (
                "fresh_boundary_rescue_v0_5:"
                "deterministic_seizure_free_to_fresh_uncertain_boundary"
            ),
        )
    if deterministic_unit == "no_reference" and fresh_unit == "seizure_free":
        return (
            True,
            "fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free",
        )
    return False, prior_gate.replace(
        "cluster_cadence_precision_v0_4", "fresh_boundary_rescue_v0_5", 1
    )


def _accept_fresh_boundary_rescue_v0_6(
    *,
    deterministic_label: str,
    fresh_label: str,
    fresh_boundary_profile: Sequence[Any],
    prior_gate: str,
) -> tuple[bool, str]:
    accept_v05, gate = _accept_fresh_boundary_rescue_v0_5(
        deterministic_label=deterministic_label,
        fresh_label=fresh_label,
        prior_gate=prior_gate,
    )
    if not accept_v05:
        return False, gate.replace(
            "fresh_boundary_rescue_v0_5",
            "profile_guard_boundary_rescue_v0_6",
            1,
        )
    deterministic_unit = _label_unit(deterministic_label)
    fresh_unit = _label_unit(fresh_label)
    profile_text = _profile_text(fresh_boundary_profile)
    if deterministic_unit == "seizure_free" and fresh_unit in {
        "unknown",
        "no_reference",
    }:
        if _profile_affirms_seizure_free(profile_text):
            return (
                False,
                "profile_guard_boundary_rescue_v0_6:profile_affirms_seizure_free",
            )
        if _profile_supports_seizure_free_overreach(profile_text):
            return (
                True,
                (
                    "profile_guard_boundary_rescue_v0_6:"
                    "seizure_free_to_uncertain_supported"
                ),
            )
        return (
            False,
            "profile_guard_boundary_rescue_v0_6:missing_seizure_free_overreach_profile",
        )
    if deterministic_unit == "no_reference" and fresh_unit == "seizure_free":
        if _profile_is_only_no_reference_absence(profile_text):
            return (
                False,
                "profile_guard_boundary_rescue_v0_6:profile_only_no_reference_absence",
            )
        if _profile_supports_no_reference_to_seizure_free(profile_text):
            return (
                True,
                (
                    "profile_guard_boundary_rescue_v0_6:"
                    "no_reference_to_seizure_free_supported"
                ),
            )
        return (
            False,
            "profile_guard_boundary_rescue_v0_6:missing_no_reference_rescue_profile",
        )
    return False, prior_gate.replace(
        "cluster_cadence_precision_v0_4",
        "profile_guard_boundary_rescue_v0_6",
        1,
    )


def _accept_unknown_count_window_rescue_v0_7(
    *,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
    fresh_boundary_profile: Sequence[Any],
    prior_gate: str,
) -> tuple[bool, str]:
    deterministic_unit = _label_unit(deterministic_label)
    consensus_unit = _count_window_replacement_unit(consensus_label)
    fresh_unit = _count_window_replacement_unit(fresh_label)
    if deterministic_unit != "unknown":
        return False, prior_gate.replace(
            "profile_guard_boundary_rescue_v0_6",
            "unknown_count_window_rescue_v0_7",
            1,
        )
    if not consensus_label or consensus_label != fresh_label:
        return False, "unknown_count_window_rescue_v0_7:fresh_consensus_disagree"
    if fresh_unit in {"unknown", "no_reference", "seizure_free", "other"}:
        return False, (
            "unknown_count_window_rescue_v0_7:"
            f"unsupported_replacement_unit:{fresh_unit}"
        )
    if consensus_unit != fresh_unit:
        return False, "unknown_count_window_rescue_v0_7:unit_mismatch"
    profile_text = _profile_text(fresh_boundary_profile)
    if _profile_blocks_unknown_count_window_rescue(profile_text):
        return (
            False,
            "unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile",
        )
    if _profile_supports_explicit_count_window(profile_text):
        return (
            True,
            "unknown_count_window_rescue_v0_7:explicit_count_window_supported",
        )
    return (
        False,
        "unknown_count_window_rescue_v0_7:missing_explicit_count_window_profile",
    )


def _accept_parseable_denominator_window_refinement_v0_8(
    *,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
    fresh_boundary_profile: Sequence[Any],
    prior_gate: str,
) -> tuple[bool, str]:
    if "uncertain_or_ambiguous_replacement:other" not in prior_gate:
        return False, prior_gate.replace(
            "unknown_count_window_rescue_v0_7",
            "parseable_denominator_window_refinement_v0_8",
            1,
        )
    if not consensus_label or consensus_label != fresh_label:
        return False, (
            "parseable_denominator_window_refinement_v0_8:"
            "fresh_consensus_disagree"
        )
    if _label_unit(deterministic_label) in {
        "unknown",
        "no_reference",
        "seizure_free",
    }:
        return False, (
            "parseable_denominator_window_refinement_v0_8:"
            "boundary_origin_not_relaxed"
        )
    if not _parseable_specific_rate(fresh_label):
        return False, (
            "parseable_denominator_window_refinement_v0_8:"
            "replacement_not_parseable_specific_rate"
        )
    profile_text = _profile_text(fresh_boundary_profile)
    if _profile_blocks_parseable_refinement_v0_8(profile_text):
        return False, (
            "parseable_denominator_window_refinement_v0_8:"
            "unsafe_parseable_refinement_profile"
        )
    if _profile_supports_parseable_refinement_v0_8(profile_text):
        return (
            True,
            (
                "parseable_denominator_window_refinement_v0_8:"
                "profile_supported_parseable_refinement"
            ),
        )
    return False, (
        "parseable_denominator_window_refinement_v0_8:"
        "missing_parseable_refinement_profile"
    )


def _accept_semantic_equiv_unknown_uncertainty_v0_9(
    *,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
    fresh_boundary_profile: Sequence[Any],
    prior_gate: str,
) -> tuple[bool, str, str]:
    accept_equiv, gate = _accept_normalized_equivalent_agreement_v0_9(
        deterministic_label=deterministic_label,
        consensus_label=consensus_label,
        fresh_label=fresh_label,
        prior_gate=prior_gate,
    )
    if accept_equiv:
        return True, gate, "accept_normalized_equivalent_agreement"
    accept_unknown, gate = _accept_unknown_uncertainty_rescue_v0_9(
        deterministic_label=deterministic_label,
        consensus_label=consensus_label,
        fresh_label=fresh_label,
        fresh_boundary_profile=fresh_boundary_profile,
        prior_gate=gate,
    )
    if accept_unknown:
        return True, gate, "accept_unknown_uncertainty_rescue"
    return False, gate, "keep_deterministic_baseline"


def _accept_normalized_equivalent_agreement_v0_9(
    *,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
    prior_gate: str,
) -> tuple[bool, str]:
    if prior_gate != "fresh_evidence_disagrees_with_consensus":
        return False, prior_gate
    deterministic_monthly = _monthly_frequency_or_none(deterministic_label)
    consensus_monthly = _monthly_frequency_or_none(consensus_label)
    fresh_monthly = _monthly_frequency_or_none(fresh_label)
    if consensus_monthly is None or fresh_monthly is None:
        return False, prior_gate
    if consensus_monthly != fresh_monthly:
        return False, prior_gate
    if deterministic_monthly == fresh_monthly:
        return False, prior_gate
    return (
        True,
        (
            "semantic_equiv_unknown_uncertainty_v0_9:"
            "normalized_equivalent_consensus_fresh"
        ),
    )


def _accept_unknown_uncertainty_rescue_v0_9(
    *,
    deterministic_label: str,
    consensus_label: str,
    fresh_label: str,
    fresh_boundary_profile: Sequence[Any],
    prior_gate: str,
) -> tuple[bool, str]:
    if consensus_label != "unknown" or fresh_label != "unknown":
        return False, prior_gate
    deterministic_unit = _label_unit(deterministic_label)
    if deterministic_unit in {"unknown", "no_reference", "seizure_free"}:
        return False, prior_gate
    if deterministic_unit == "other" and not _parseable_specific_rate(
        deterministic_label
    ):
        return False, prior_gate
    profile_text = _profile_text(fresh_boundary_profile)
    if _profile_blocks_unknown_uncertainty_v0_9(profile_text):
        return (
            False,
            (
                "semantic_equiv_unknown_uncertainty_v0_9:"
                "unknown_uncertainty_profile_blocked"
            ),
        )
    if _profile_supports_unknown_uncertainty_v0_9(profile_text):
        return (
            True,
            (
                "semantic_equiv_unknown_uncertainty_v0_9:"
                "specific_rate_to_unknown_uncertainty_supported"
            ),
        )
    return (
        False,
        (
            "semantic_equiv_unknown_uncertainty_v0_9:"
            "missing_unknown_uncertainty_profile"
        ),
    )


def _profile_text(profile: Sequence[Any]) -> str:
    return " | ".join(str(item).lower() for item in profile)


def _profile_affirms_seizure_free(profile_text: str) -> bool:
    affirming_markers = (
        "explicit seizure-free duration",
        "zero-event interval",
        "no current seizures",
    )
    refuting_markers = (
        "no explicit seizure-free",
        "not seizure_free",
        "not seizure free",
    )
    return any(marker in profile_text for marker in affirming_markers) and not any(
        marker in profile_text for marker in refuting_markers
    )


def _profile_supports_seizure_free_overreach(profile_text: str) -> bool:
    markers = (
        "last_event",
        "last event",
        "not seizure_free",
        "not seizure free",
        "no explicit seizure-free",
        "frequency_vs_seizure_free",
        "frequency vs seizure",
        "current/recent frequency",
        "unknown/no-reference",
        "denominator/window",
        "no explicit numeric",
        "qualitative",
        "cluster pattern",
        "unknown_frequency",
        "unknown frequency",
        "no clear current recurring rate",
        "no explicit count or rate",
    )
    return any(marker in profile_text for marker in markers)


def _profile_is_only_no_reference_absence(profile_text: str) -> bool:
    absence_markers = (
        "no positive seizure-frequency evidence",
        "no seizure-frequency",
        "no seizure frequency",
    )
    support_markers = (
        "no current",
        "non-epileptic",
        "unknown/no-reference",
        "not absent",
        "no evidence that frequency is truly unknown",
        "no positive absence",
        "explicit seizure-free",
        "seizure free",
    )
    return any(marker in profile_text for marker in absence_markers) and not any(
        marker in profile_text for marker in support_markers
    )


def _profile_supports_no_reference_to_seizure_free(profile_text: str) -> bool:
    markers = (
        "no_reference",
        "no reference",
        "no current or recent epileptic",
        "non-epileptic",
        "not absent",
        "no evidence that frequency is truly unknown",
        "no positive absence",
        "unknown/no-reference boundary",
        "current/recent frequency",
        "explicit seizure-free",
        "seizure free",
    )
    return any(marker in profile_text for marker in markers)


def _profile_blocks_unknown_count_window_rescue(profile_text: str) -> bool:
    blockers = (
        "last_event",
        "last event",
        "last seizure date",
        "none since",
        "open-ended",
        "since starting",
        "since beginning",
        "start date unclear",
        "unclear window",
        "window unclear",
        "denominator unclear",
        "vague",
        "several",
        "qualitative",
        "no explicit count",
        "no explicit numeric",
        "no explicit numeric/range",
    )
    return any(blocker in profile_text for blocker in blockers)


def _profile_supports_explicit_count_window(profile_text: str) -> bool:
    count_markers = (
        "explicit count",
        "explicit numeric count",
        "number of seizures explicitly given",
        "count-plus-window",
        "count plus window",
    )
    window_markers = (
        "usable follow-up",
        "usable observation period",
        "usable window",
        "defined period",
        "defined observation period",
        "explicit interval",
        "follow-up period",
    )
    return any(marker in profile_text for marker in count_markers) and any(
        marker in profile_text for marker in window_markers
    )


def _profile_blocks_parseable_refinement_v0_8(profile_text: str) -> bool:
    blockers = (
        "seizure-free interval",
        "last_event_only",
        "last event",
        "highest active semiology",
        "highest-burden seizure type",
        "highest current clinically active semiology",
        "multiple active semiologies",
        "highest burden selected",
        "seizure-day counts",
    )
    return any(blocker in profile_text for blocker in blockers)


def _profile_supports_parseable_refinement_v0_8(profile_text: str) -> bool:
    if "denominator/window" in profile_text:
        return True
    if "explicit current frequency" in profile_text and "clearly stated" in profile_text:
        return True
    count_marker = "explicit count" in profile_text
    window_marker = any(
        marker in profile_text for marker in (" over ", "window", "period", "~")
    )
    boundary_negated = (
        "no evidence for seizure-free, unknown, or no_reference" in profile_text
    )
    return count_marker and window_marker and boundary_negated


def _parseable_specific_rate(label: str) -> bool:
    try:
        monthly = label_to_monthly_frequency(label)
    except Exception:
        return False
    return monthly not in (0.0, 1000.0)


def _parseable_frequency_label(label: str) -> bool:
    try:
        label_to_monthly_frequency(label)
    except Exception:
        return False
    return True


def _monthly_frequency_or_none(label: str) -> float | None:
    try:
        return label_to_monthly_frequency(label)
    except Exception:
        return None


def _profile_blocks_unknown_uncertainty_v0_9(profile_text: str) -> bool:
    blockers = (
        "cluster frequency and events per cluster both specified",
        "events per cluster both specified",
        "cluster burden present",
        "cluster frequency with explicit cadence",
    )
    return any(blocker in profile_text for blocker in blockers)


def _profile_supports_unknown_uncertainty_v0_9(profile_text: str) -> bool:
    uncertainty_marker = (
        "unknown_frequency" in profile_text or "unknown frequency" in profile_text
    )
    missing_count_marker = any(
        marker in profile_text
        for marker in (
            "no explicit count or rate",
            "no explicit recurring rate",
            "device logs suggest clusters but no counts",
            "patient unsure",
        )
    )
    return uncertainty_marker and missing_count_marker


def _count_window_replacement_unit(label: str) -> str:
    lowered = label.strip().lower()
    if lowered in {"unknown", "no seizure frequency reference"}:
        return _label_unit(lowered)
    if lowered.startswith("seizure free"):
        return "seizure_free"
    match = re.search(
        r"\b(?:\d+|multiple)\s+per\s+(?:\d+\s+)?"
        r"(?P<unit>day|week|month|year)s?\b",
        lowered,
    )
    if match is None:
        return "other"
    return match.group("unit")


def _label_unit(label: str) -> str:
    lowered = label.strip().lower()
    for unit in ("day", "week", "month", "year"):
        if f" per {unit}" in lowered:
            return unit
    if lowered == "unknown":
        return "unknown"
    if lowered == "no seizure frequency reference":
        return "no_reference"
    if lowered.startswith("seizure free"):
        return "seizure_free"
    if "cluster" in lowered:
        return "cluster"
    return "other"


def _policy_version(policy: SelectorPolicy) -> str:
    if policy == "fresh_agreement_v0_1":
        return SELECTOR_VERSION
    if policy == "nonboundary_precision_v0_2":
        return SELECTOR_V0_2_VERSION
    if policy == "specific_label_precision_v0_3":
        return SELECTOR_V0_3_VERSION
    if policy == "cluster_cadence_precision_v0_4":
        return SELECTOR_V0_4_VERSION
    if policy == "fresh_boundary_rescue_v0_5":
        return SELECTOR_V0_5_VERSION
    if policy == "profile_guard_boundary_rescue_v0_6":
        return SELECTOR_V0_6_VERSION
    if policy == "unknown_count_window_rescue_v0_7":
        return SELECTOR_V0_7_VERSION
    if policy == "parseable_denominator_window_refinement_v0_8":
        return SELECTOR_V0_8_VERSION
    if policy == "semantic_equiv_unknown_uncertainty_v0_9":
        return SELECTOR_V0_9_VERSION
    raise ValueError(f"unknown selector policy: {policy}")


def _consensus_policy_for(policy: SelectorPolicy) -> SelectorPolicy:
    if policy in {
        "fresh_boundary_rescue_v0_5",
        "profile_guard_boundary_rescue_v0_6",
        "unknown_count_window_rescue_v0_7",
    }:
        return "cluster_cadence_precision_v0_4"
    if policy == "parseable_denominator_window_refinement_v0_8":
        return policy
    if policy == "semantic_equiv_unknown_uncertainty_v0_9":
        return policy
    return policy


def _selector_version(rows: Sequence[Mapping[str, Any]]) -> str:
    versions = {
        str(row.get("selector_version") or "")
        for row in rows
        if row.get("selector_version")
    }
    if len(versions) == 1:
        return next(iter(versions))
    if not versions:
        return SELECTOR_VERSION
    return "mixed:" + ",".join(sorted(versions))


def _score_layer(
    source: str,
    final_label: str,
    comparison: Any,
) -> dict[str, Any]:
    return {
        "source": source,
        "final_label": final_label,
        "comparison": dict(comparison or {}),
    }


def _purist_transition(
    *,
    baseline_correct: bool,
    selected_correct: bool,
    label_changed: bool,
) -> str:
    if not label_changed:
        return "unchanged_correct" if baseline_correct else "unchanged_wrong"
    if not baseline_correct and selected_correct:
        return "wrong_to_correct"
    if baseline_correct and not selected_correct:
        return "correct_to_wrong"
    if baseline_correct and selected_correct:
        return "correct_to_correct"
    return "wrong_to_wrong"


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row
        for row in rows
        if row.get("source_row_index") is not None
    }


def _dig(row: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = row
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current
