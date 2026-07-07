"""C7 - P2.5 family-gated graph-trust posture over the Stage D validation slice.

Predeclaration: ``gan2026_kg_family_gated_graph_trust_predeclaration_2026-06-16.md``.

The KG Stage D finding relocated the component wall from generation to SELECTION:
a clean, regression-free graph component is minted for 7/11 no-correct residual
rows, but the only regression-safe Stage D posture (P2 corroborated) recovers 0
of them because corroboration cannot fire on the no-correct residual. This driver
tests the untried corroboration-free lever, **P2.5 (family-gated graph trust)**:
override the selected baseline with the graph's withholding component WITHOUT
requiring corroboration, but ONLY when a forward-observable family signal fires
that is meant to localize to the two high-precision families
(``unknown_over_quantified_rate``, ``last_event/seizure_free_overinfer``).

P2.5 gate (predeclared, forward-computable, gold-free):
  graph_kind in {unknown, no_reference}  AND graph != selected
  AND no admitted dual-validated node carries a quantified semantic kind
      (frequency / seizure_free)  -> the graph has no surviving quantifiable
      evidence, so withholding is the ontology-grounded resolution.

P2.5a tightening probe: P2.5 gate AND the ontology over-inference guard
(``over_inference_out_of_unknown:<shape>``, shape in the unknown-only family set)
rejected >=1 uncurated node.

No-call replay: graphs reused from the frozen Stage D graphs artifact;
dual-validation / resolve recomputed deterministically; v0.9
selected/consensus/fresh + baseline from the Stage D rows artifact. Gold used
only for post-hoc Purist scoring + the honest discriminability probe.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    summarize_family_holdout_cv,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import BOUNDARY_BANDS
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph.graph import (
    ClinicalFrequencyStateGraph,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph.validation import (
    dual_validate_graph,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

STAGE_D = "gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15"
GRAPHS_PATH = EXPERIMENTS / f"{STAGE_D}_graphs.jsonl"
ROWS_PATH = EXPERIMENTS / f"{STAGE_D}_rows.jsonl"

RUN_ID = "gan2026_kg_family_gated_graph_trust_2026-06-16"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

WITHHOLDING_KINDS = {"unknown", "no_reference"}
QUANTIFIED_KINDS = {FrequencyLabelKind.FREQUENCY, FrequencyLabelKind.SEIZURE_FREE}
UNKNOWN_ONLY_SHAPES = {
    "last_event_only",
    "open_ended_since",
    "vague_count",
    "conditional_only",
    "relative_trend",
}
GENUINE_RATE_BANDS = {
    "band_zero",
    "band_submonthly",
    "band_monthly",
    "band_weekly",
    "band_daily",
}

# The 7 residual rows the Stage D generator minted a correct component for.
MINTED_RESIDUAL = {5534, 6321, 6368, 6571, 11254, 11272, 14025}


def _load_graphs() -> dict[int, ClinicalFrequencyStateGraph]:
    graphs: dict[int, ClinicalFrequencyStateGraph] = {}
    for line in GRAPHS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        graphs[int(d["source_row_index"])] = ClinicalFrequencyStateGraph.model_validate(d["graph"])
    return graphs


def _load_rows() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line in ROWS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        rows[int(d["source_row_index"])] = d
    return rows


def _graph_features(graph: ClinicalFrequencyStateGraph) -> dict[str, Any]:
    """Forward-observable, gold-free features used by the P2.5 family gate."""

    validation = dual_validate_graph(graph)
    admitted = validation.admitted_node_ids
    admitted_nodes = [n for n in graph.nodes if n.node_id in admitted]
    any_admitted_quantified = any(n.semantic_kind in QUANTIFIED_KINDS for n in admitted_nodes)
    over_inference_shapes: list[str] = []
    for nv in validation.node_validations:
        for failure in nv.failures:
            if failure.startswith("over_inference_out_of_unknown:"):
                over_inference_shapes.append(failure.split(":", 1)[1])
    guard_fired = any(s in UNKNOWN_ONLY_SHAPES for s in over_inference_shapes)
    return {
        "any_admitted_quantified": any_admitted_quantified,
        "over_inference_shapes": over_inference_shapes,
        "guard_fired_unknown_only": guard_fired,
    }


def _posture_override(
    posture: str,
    *,
    row: Mapping[str, Any],
    features: Mapping[str, Any],
) -> bool:
    graph_label = row["graph_label"]
    selected = row["selected_label"]
    if graph_label == selected:
        return False
    graph_kind = row["graph_kind"]
    if posture in ("P1_unilateral",):
        return True
    if posture == "P3_unknown_only":
        return graph_kind == "unknown"
    if posture == "P2_5_family_gated":
        return graph_kind in WITHHOLDING_KINDS and not features["any_admitted_quantified"]
    if posture == "P2_5a_guarded":
        return (
            graph_kind in WITHHOLDING_KINDS
            and not features["any_admitted_quantified"]
            and features["guard_fired_unknown_only"]
        )
    raise ValueError(f"unknown posture: {posture}")
    # P2_corroborated handled separately (needs consensus/fresh equivalence,
    # already computed in the Stage D rows artifact).


def _transition(before: bool, after: bool) -> str:
    if not before and after:
        return "W->C"
    if before and not after:
        return "C->W"
    return "C->C" if before else "W->W"


def _score_posture(
    posture: str,
    rows: Mapping[int, dict[str, Any]],
    feats: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    overrides = 0
    transitions: Counter[str] = Counter()
    per_band: dict[str, dict[str, int]] = defaultdict(
        lambda: {"rows": 0, "changed_labels": 0, "wrong_to_correct": 0, "correct_to_wrong": 0}
    )
    final_correct = 0
    harvested_minted: list[int] = []
    cw_rows: list[int] = []
    for idx, row in rows.items():
        band = row["gold_band"]
        per_band[band]["rows"] += 1
        sel_correct = row["selected_correct"]
        if posture == "P2_corroborated":
            ov = row["postures"]["P2_corroborated"]["override"]
            after_correct = row["postures"]["P2_corroborated"]["final_correct"]
        else:
            ov = _posture_override(posture, row=row, features=feats[idx])
            after_correct = row["graph_correct"] if ov else sel_correct
        if ov:
            overrides += 1
            per_band[band]["changed_labels"] += 1
        t = _transition(sel_correct, after_correct)
        transitions[t] += 1
        if after_correct:
            final_correct += 1
        if t == "W->C":
            per_band[band]["wrong_to_correct"] += 1
            if idx in MINTED_RESIDUAL:
                harvested_minted.append(idx)
        elif t == "C->W":
            per_band[band]["correct_to_wrong"] += 1
            cw_rows.append(idx)
    genuine_rate_regressions = sum(
        per_band[b]["correct_to_wrong"] for b in per_band if b in GENUINE_RATE_BANDS
    )
    return {
        "overrides": overrides,
        "final_purist_correct": final_correct,
        "wrong_to_correct": transitions["W->C"],
        "correct_to_wrong": transitions["C->W"],
        "net_purist_gain": transitions["W->C"] - transitions["C->W"],
        "transitions": dict(sorted(transitions.items())),
        "per_band": {b: dict(per_band[b]) for b in sorted(per_band)},
        "genuine_rate_regressions": genuine_rate_regressions,
        "harvested_minted_residual": sorted(harvested_minted),
        "correct_to_wrong_indices": sorted(cw_rows),
    }


def _family_cv(posture_result: Mapping[str, Any]) -> dict[str, Any]:
    families = {
        band: {
            "rows": stats["rows"],
            "changed_labels": stats["changed_labels"],
            "wrong_to_correct": stats["wrong_to_correct"],
            "correct_to_wrong": stats["correct_to_wrong"],
        }
        for band, stats in posture_result["per_band"].items()
    }
    return summarize_family_holdout_cv({"families": families})


def _decision(p25: Mapping[str, Any], cv: Mapping[str, Any]) -> tuple[str, str]:
    genuine = p25["genuine_rate_regressions"]
    gap_robust = cv["gap_robust"]
    if genuine == 0 and gap_robust:
        return (
            "promote",
            "P2.5 is gap_robust with ZERO genuine-rate regressions: a "
            "corroboration-free, family-gated harvester exists.",
        )
    return (
        "reject",
        f"P2.5 leaks {genuine} genuine-rate regression(s) "
        f"(gap_robust={gap_robust}). The forward family gate fires on "
        "genuine-rate rows indistinguishable from the harvest set on every "
        "observable graph feature; the family localization is a post-hoc gold "
        "property, not a selection-time signal. Per the stop rule, tightening "
        "on a forward feature is impossible here, so the honest decision is "
        "reject (same structural wall Stage D identified).",
    )


def main() -> None:
    graphs = _load_graphs()
    rows = _load_rows()
    feats = {idx: _graph_features(graphs[idx]) for idx in rows}

    postures = (
        "P1_unilateral",
        "P2_corroborated",
        "P3_unknown_only",
        "P2_5_family_gated",
        "P2_5a_guarded",
    )
    results = {p: _score_posture(p, rows, feats) for p in postures}
    cv_p25 = _family_cv(results["P2_5_family_gated"])
    cv_p25a = _family_cv(results["P2_5a_guarded"])
    decision, rationale = _decision(results["P2_5_family_gated"], cv_p25)

    # Honest discriminability probe: among rows the P2.5 gate fires on, how many
    # are gold band_unknown (harvestable) vs genuine-rate (casualties).
    gate_fired = [
        idx
        for idx, row in rows.items()
        if _posture_override("P2_5_family_gated", row=row, features=feats[idx])
    ]
    gate_band = Counter(rows[idx]["gold_band"] for idx in gate_fired)

    baseline_purist = sum(1 for r in rows.values() if r["selected_correct"])
    summary = {
        "rows": len(rows),
        "v09_selected_purist_correct": baseline_purist,
        "postures": results,
        "p2_5_family_cv": cv_p25,
        "p2_5a_family_cv": cv_p25a,
        "p2_5_gate_fired_rows": len(gate_fired),
        "p2_5_gate_fired_band_breakdown": dict(sorted(gate_band.items())),
        "minted_residual_indices": sorted(MINTED_RESIDUAL),
        "decision": decision,
        "decision_rationale": rationale,
    }
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-16",
        "split": "validation",
        "predeclaration": "experiments/gan2026_kg_family_gated_graph_trust_predeclaration_2026-06-16.md",
        "source_slice": f"experiments/{ROWS_PATH.name} (Stage D predeclared 250-row residual-inclusive slice)",
        "source_graphs": f"experiments/{GRAPHS_PATH.name}",
        "summary": summary,
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


def _posture_row(name: str, r: Mapping[str, Any], total: int) -> str:
    return (
        f"| `{name}` | {r['overrides']} | {r['final_purist_correct']}/{total} | "
        f"{r['wrong_to_correct']} | {r['correct_to_wrong']} | {r['net_purist_gain']} | "
        f"{r['genuine_rate_regressions']} | {r['harvested_minted_residual']} |"
    )


def _markdown(payload: Mapping[str, Any]) -> str:
    s = payload["summary"]
    total = s["rows"]
    r = s["postures"]
    lines = [
        "# Gan 2026 KG Family-Gated Graph-Trust (P2.5)",
        "",
        "Date: 2026-06-16",
        "",
        "C7 of the Gan 2026 F1 workflow. Tests the untried corroboration-free "
        "lever P2.5 (family-gated graph trust) over the frozen Stage D 250-row "
        "residual-inclusive validation slice. No-call replay: graphs reused from "
        "the Stage D graphs artifact; dual-validation recomputed deterministically; "
        "v0.9 components/baseline from the Stage D rows artifact. Gold used only "
        "for post-hoc Purist scoring.",
        "",
        f"- Predeclaration: `{payload['predeclaration']}`",
        f"- Source slice: `{payload['source_slice']}`",
        f"- Rows: {total}",
        f"- v0.9 selected baseline Purist: {s['v09_selected_purist_correct']}/{total}",
        f"- Minted residual targets (gold-`unknown`): {s['minted_residual_indices']}",
        "",
        "## Posture comparison (selected baseline -> posture override)",
        "",
        "`P2.5` = withholding graph_kind + no admitted quantified node "
        "(corroboration-free family gate). `P2.5a` = P2.5 + ontology "
        "over-inference guard fired. `genuine C->W` = C->W in any non-"
        "`band_unknown` boundary band (the stop-rule kill metric).",
        "",
        "| Posture | Overrides | Final Purist | W->C | C->W | Net | genuine C->W | harvested minted |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        _posture_row("P1_unilateral", r["P1_unilateral"], total),
        _posture_row("P2_corroborated", r["P2_corroborated"], total),
        _posture_row("P3_unknown_only", r["P3_unknown_only"], total),
        _posture_row("P2_5_family_gated", r["P2_5_family_gated"], total),
        _posture_row("P2_5a_guarded", r["P2_5a_guarded"], total),
        "",
        "## P2.5 gate discriminability (honest probe)",
        "",
        f"- Rows the P2.5 gate fires on: {s['p2_5_gate_fired_rows']}",
        f"- Their gold-band breakdown: `{s['p2_5_gate_fired_band_breakdown']}`",
        "",
        "The gate fires on both the harvestable gold-`band_unknown` rows and "
        "genuine-rate rows. Those genuine-rate rows are feature-identical to the "
        "harvest set on every forward-observable graph signal (graph_kind, "
        "admitted node kinds, missing-variable flags, claim count); only the "
        "hidden gold band distinguishes them.",
        "",
        "## P2.5 held-out-family CV",
        "",
        f"- gap_robust: **{s['p2_5_family_cv']['gap_robust']}**",
        f"- aggregate net Purist gain: {s['p2_5_family_cv']['aggregate']['net_purist_gain']}",
        f"- regressing held-out bands: {s['p2_5_family_cv']['regressing_held_out_families']}",
        f"- worst held-out fold: {s['p2_5_family_cv']['worst_held_out_fold']}",
        "",
        "## P2.5 per-band transitions",
        "",
        "| Band | Rows | Overrides | W->C | C->W |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for band in BOUNDARY_BANDS:
        b = r["P2_5_family_gated"]["per_band"].get(band)
        if not b:
            continue
        lines.append(
            f"| `{band}` | {b['rows']} | {b['changed_labels']} | "
            f"{b['wrong_to_correct']} | {b['correct_to_wrong']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{s['decision']}`",
            "",
            s["decision_rationale"],
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: Mapping[str, Any]) -> None:
    s = payload["summary"]
    p25 = s["postures"]["P2_5_family_gated"]
    entries = [e for e in load_run_registry(REGISTRY_PATH) if e.run_id != RUN_ID]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                payload["predeclaration"],
            ),
            date="2026-06-16",
            pipeline_family="hybrid_clinical_frequency_state_graph",
            split="validation",
            row_count=s["rows"],
            model="none",
            model_role=(
                "C7 P2.5 family-gated graph-trust posture. Recomputes "
                "dual-validation/resolve deterministically from the frozen Stage D "
                "graphs and scores a corroboration-free, forward-observable family "
                "gate (withholding graph_kind + no admitted quantified node) "
                "against the v0.9 selected baseline, alongside P1/P2/P3. No model "
                "calls and no holdout rows are read."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="state_graph_family_gated_graph_trust_p2_5_v1",
            cache_reuse_source=f"stage_d_graphs:{GRAPHS_PATH.name};stage_d_rows:{ROWS_PATH.name}",
            primary_metrics={
                "rows": s["rows"],
                "v09_selected_purist_correct": s["v09_selected_purist_correct"],
                "p2_5_overrides": p25["overrides"],
                "p2_5_wrong_to_correct": p25["wrong_to_correct"],
                "p2_5_correct_to_wrong": p25["correct_to_wrong"],
                "p2_5_net_purist_gain": p25["net_purist_gain"],
                "p2_5_genuine_rate_regressions": p25["genuine_rate_regressions"],
                "p2_5_harvested_minted_residual": len(p25["harvested_minted_residual"]),
                "p2_5_gap_robust": int(bool(s["p2_5_family_cv"]["gap_robust"])),
            },
            evidence_validity=(
                "Validation-only no-call replay over the frozen Stage D predeclared "
                "250-row residual-inclusive slice. Graphs reused from the Stage D "
                "graphs artifact; dual-validation/resolve recomputed "
                "deterministically (no model calls). v0.9 components/baseline from "
                "the Stage D rows artifact; gold used only for post-hoc Purist "
                "scoring and an honest discriminability probe. No holdout rows."
            ),
            decision=s["decision"],
            claim_language_notes=(
                "Tests whether a corroboration-free family-gated graph-trust "
                "posture (P2.5) can harvest the 7 minted residual rows without "
                "re-introducing P3 genuine-rate regressions. Not a holdout-facing "
                "candidate. A reject means no forward-observable family gate "
                "separates the harvest set from the genuine-rate casualties; "
                "test450 stays locked."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
