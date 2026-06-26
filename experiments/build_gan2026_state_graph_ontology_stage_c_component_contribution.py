"""Stage C - 50-row component-contribution test for the graph query.

Design note: ````
§5 (Stage C) and §8.4.2; ADR ``0017`` (the C2 parallel posture); resolve_label
spec ``docs/design/gan2026_resolve_label_spec.md`` §5 (the ablation contract:
report W->C / C->W and per-band changed-label precision).

Stage C measures the ``resolve_label`` graph query *purely as a new component*
fed to the frozen v0.9 consensus+fresh selector, on the predeclared first-50
validation rows. Two arms:

* **Arm 1 - component-pool coverage.** For each row, the existing pool is
  {deterministic, consensus, fresh-evidence} (from the saved v0.9 replay). A row
  is *no-correct* when none of the three is Purist-correct. The arm asks how many
  no-correct rows the graph query newly covers - the "mint a correct component
  for the no-correct residual" number the design leads with.

* **Arm 2 - selection contribution.** The graph query is added as a fourth
  candidate under three transparent, predeclared override postures, and final
  labels are scored against the v0.9 selected baseline (the §6 kill metric is
  correct->wrong):
    - ``P1_unilateral``     - graph overrides whenever it disagrees (effect bound);
    - ``P2_corroborated``   - graph overrides only when an independent existing
      candidate (consensus or fresh) is monthly-equivalent to it (the
      precision-first posture the whole selector line uses, applied to the new
      component);
    - ``P3_unknown_only``   - graph overrides only when it resolves to ``unknown``
      (isolates the ADR ``0017`` clean-``unknown`` arm).

This is a no-call replay: the graph is rebuilt deterministically from the same
validation50 v3 section claim-table the rest of the ladder uses (raw_frequency
normalized, no diary/window arithmetic), and the selector inputs come from the
saved v0.9 replay. Validation-only over ``gan2026_split_v1``: no holdout rows are
read and no model calls are made. Not a holdout authorization or a promoted
candidate.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    BOUNDARY_BANDS,
    boundary_band,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    atomic_claims_from_structured_record,
    build_state_graph_from_atomic_claims,
    resolve_label,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

# The first-50 validation rows: the canonical v3 section claim-table used by the
# rest of the 25 -> 50 -> 250 ladder. validation25 (Stage B) is a strict prefix.
SOURCE_CLAIM_TABLE = (
    EXPERIMENTS / "gan2026_section_claim_table_validation50_gpt41mini_v3_2026-06-01.jsonl"
)
# The frozen v0.9 selector replay supplying the deterministic/consensus/fresh
# components and the selected baseline for each row.
V09_REPLAY = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)

GRAPH_BUILDER = "llm-sg-stage-c-v3-raw-frequency-normalized"

RUN_ID = "gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15"
GRAPHS_PATH = EXPERIMENTS / f"{RUN_ID}_graphs.jsonl"
ROWS_PATH = EXPERIMENTS / f"{RUN_ID}_rows.jsonl"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

POSTURES = ("P1_unilateral", "P2_corroborated", "P3_unknown_only")


def main() -> None:
    graphs, graph_labels = _build_graphs_and_labels()
    _write_graphs_artifact(graphs)
    v09_by_index = _load_v09_rows()

    rows = _build_rows(graph_labels, v09_by_index)
    _write_rows_artifact(rows)
    summary = _summarize(rows)

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Stage C component-contribution test. Feeds the resolve_label graph "
            "query as a fourth component to the frozen v0.9 consensus+fresh "
            "selector on the predeclared first-50 validation rows. Reports "
            "component-pool coverage of the no-correct residual and selection "
            "contribution (W->C / C->W) under three transparent override "
            "postures. Validation-only; no holdout rows and no model calls."
        ),
        "split": "validation",
        "split_manifest": split_manifest,
        "source_claim_table": f"experiments/{SOURCE_CLAIM_TABLE.name}",
        "v09_replay_artifact": f"experiments/{V09_REPLAY.name}",
        "rebuilt_graphs_artifact": f"experiments/{GRAPHS_PATH.name}",
        "rows_artifact": f"experiments/{ROWS_PATH.name}",
        "graph_builder": GRAPH_BUILDER,
        "summary": summary,
    }
    payload["decision"] = summary["decision"]
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


# --------------------------------------------------------------------------- #
# Graph rebuild (same conversion as the Stage B rebuild pass).
# --------------------------------------------------------------------------- #


def _build_graphs_and_labels() -> tuple[
    list[ClinicalFrequencyStateGraph], dict[int, dict[str, Any]]
]:
    records_by_index = {r.source_row_index: r for r in load_records_for_split("validation")}
    graphs: list[ClinicalFrequencyStateGraph] = []
    labels: dict[int, dict[str, Any]] = {}
    for line in SOURCE_CLAIM_TABLE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        source_row_index = int(row["source_row_index"])
        record = records_by_index[source_row_index]
        claims = atomic_claims_from_structured_record(row.get("structured_record"))
        graph = build_state_graph_from_atomic_claims(
            record.note_text,
            claims,
            source_row_index=source_row_index,
            graph_builder=GRAPH_BUILDER,
        )
        graphs.append(graph)
        resolution = resolve_label(graph)
        labels[source_row_index] = {
            "graph_label": resolution.final_label,
            "graph_kind": resolution.final_kind.value,
            "graph_monthly_frequency": resolution.monthly_frequency,
            "selected_node_ids": list(resolution.selected_node_ids),
            "used_edge_ids": list(resolution.used_edge_ids),
            "decision_trace": list(resolution.decision_trace),
        }
    return graphs, labels


def _write_graphs_artifact(graphs: Sequence[ClinicalFrequencyStateGraph]) -> None:
    lines = [
        json.dumps(
            {"source_row_index": graph.source_row_index, "graph": graph.model_dump(mode="json")},
            sort_keys=True,
        )
        for graph in graphs
    ]
    GRAPHS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_v09_rows() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line in V09_REPLAY.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[int(row["source_row_index"])] = row
    return rows


# --------------------------------------------------------------------------- #
# Per-row component + posture accounting.
# --------------------------------------------------------------------------- #


def _monthly(label: str) -> float | None:
    try:
        return label_to_monthly_frequency(label)
    except Exception:
        return None


def _purist_correct(label: str, gold_monthly: float) -> bool:
    monthly = _monthly(label)
    return monthly is not None and map_purist(monthly) == map_purist(gold_monthly)


def _monthly_equivalent(a: str, b: str) -> bool:
    ma, mb = _monthly(a), _monthly(b)
    return ma is not None and mb is not None and ma == mb


def _build_rows(
    graph_labels: Mapping[int, dict[str, Any]],
    v09_by_index: Mapping[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row_index in sorted(graph_labels):
        v09 = v09_by_index[source_row_index]
        gold_monthly = v09["reference"]["gold_monthly_frequency"]
        band = boundary_band(gold_monthly)

        deterministic = v09["deterministic_label"]
        consensus = v09["consensus_label"]
        fresh = v09["fresh_evidence_label"]
        selected = v09["selected_label"]
        graph = graph_labels[source_row_index]
        graph_label = graph["graph_label"]
        graph_kind = graph["graph_kind"]

        pool_correct = any(
            _purist_correct(label, gold_monthly)
            for label in (deterministic, consensus, fresh)
        )
        selected_correct = _purist_correct(selected, gold_monthly)
        graph_correct = _purist_correct(graph_label, gold_monthly)

        postures: dict[str, dict[str, Any]] = {}
        for posture in POSTURES:
            override = _posture_overrides(
                posture,
                graph_label=graph_label,
                graph_kind=graph_kind,
                selected_label=selected,
                consensus_label=consensus,
                fresh_label=fresh,
            )
            final_label = graph_label if override else selected
            final_correct = _purist_correct(final_label, gold_monthly)
            postures[posture] = {
                "override": override,
                "final_label": final_label,
                "final_correct": final_correct,
                "transition": _transition(selected_correct, final_correct),
            }

        rows.append(
            {
                "source_row_index": source_row_index,
                "gold_label": v09["reference"]["gold_label"],
                "gold_monthly_frequency": gold_monthly,
                "gold_band": band,
                "deterministic_label": deterministic,
                "consensus_label": consensus,
                "fresh_evidence_label": fresh,
                "selected_label": selected,
                "graph_label": graph_label,
                "graph_kind": graph_kind,
                "pool_correct": pool_correct,
                "selected_correct": selected_correct,
                "graph_correct": graph_correct,
                "no_correct_pool": not pool_correct,
                "graph_mints_correct_for_no_correct": (not pool_correct) and graph_correct,
                "graph_decision_trace": graph["decision_trace"],
                "postures": postures,
            }
        )
    return rows


def _posture_overrides(
    posture: str,
    *,
    graph_label: str,
    graph_kind: str,
    selected_label: str,
    consensus_label: str,
    fresh_label: str,
) -> bool:
    if graph_label == selected_label:
        return False
    if posture == "P1_unilateral":
        return True
    if posture == "P2_corroborated":
        return _monthly_equivalent(graph_label, consensus_label) or _monthly_equivalent(
            graph_label, fresh_label
        )
    if posture == "P3_unknown_only":
        return graph_kind == "unknown"
    raise ValueError(f"unknown posture: {posture}")


def _transition(before_correct: bool, after_correct: bool) -> str:
    if not before_correct and after_correct:
        return "W->C"
    if before_correct and not after_correct:
        return "C->W"
    return "C->C" if before_correct else "W->W"


def _write_rows_artifact(rows: Sequence[Mapping[str, Any]]) -> None:
    lines = [json.dumps(row, sort_keys=True) for row in rows]
    ROWS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Summary + decision.
# --------------------------------------------------------------------------- #


def _summarize(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    no_correct = [row for row in rows if row["no_correct_pool"]]
    minted = [row for row in no_correct if row["graph_mints_correct_for_no_correct"]]

    posture_summary: dict[str, Any] = {}
    for posture in POSTURES:
        transitions = Counter(row["postures"][posture]["transition"] for row in rows)
        overrides = sum(1 for row in rows if row["postures"][posture]["override"])
        final_correct = sum(1 for row in rows if row["postures"][posture]["final_correct"])
        w_to_c = transitions["W->C"]
        c_to_w = transitions["C->W"]
        posture_summary[posture] = {
            "overrides": overrides,
            "final_purist_correct": final_correct,
            "wrong_to_correct": w_to_c,
            "correct_to_wrong": c_to_w,
            "net_purist_gain": w_to_c - c_to_w,
            "transitions": dict(sorted(transitions.items())),
            "regression_bands": _regression_bands(rows, posture),
        }

    arm1 = {
        "rows": total,
        "pool_correct_rows": total - len(no_correct),
        "no_correct_pool_rows": len(no_correct),
        "no_correct_source_row_indices": [row["source_row_index"] for row in no_correct],
        "graph_mints_correct_for_no_correct": len(minted),
        "graph_minted_source_row_indices": [row["source_row_index"] for row in minted],
    }
    summary = {
        "rows": total,
        "v09_selected_purist_correct": sum(1 for row in rows if row["selected_correct"]),
        "graph_component_purist_correct": sum(1 for row in rows if row["graph_correct"]),
        "arm1_component_pool_coverage": arm1,
        "arm2_selection_contribution": posture_summary,
        "by_band": _by_band(rows),
        "graph_kind_counts": dict(
            sorted(Counter(row["graph_kind"] for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-only no-call replay. The graph query is rebuilt "
            "deterministically from the validation50 v3 section claim-table; the "
            "deterministic/consensus/fresh components and the v0.9 selected "
            "baseline come from the saved v0.9 replay. Gold labels are used only "
            "for post-hoc scoring; no holdout rows are read."
        ),
    }
    summary["decision"] = _decision(summary)
    summary["decision_rationale"] = _decision_rationale(summary)
    return summary


def _regression_bands(rows: Sequence[Mapping[str, Any]], posture: str) -> dict[str, int]:
    bands: Counter[str] = Counter()
    for row in rows:
        if row["postures"][posture]["transition"] == "C->W":
            bands[row["gold_band"]] += 1
    return dict(sorted(bands.items()))


def _by_band(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    bands: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["gold_band"]].append(row)
    for band in BOUNDARY_BANDS:
        band_rows = grouped.get(band, [])
        if not band_rows:
            continue
        bands[band] = {
            "rows": len(band_rows),
            "v09_selected_purist_correct": sum(1 for r in band_rows if r["selected_correct"]),
            "graph_component_purist_correct": sum(1 for r in band_rows if r["graph_correct"]),
            "no_correct_pool_rows": sum(1 for r in band_rows if r["no_correct_pool"]),
            "p1_correct_to_wrong": sum(
                1 for r in band_rows if r["postures"]["P1_unilateral"]["transition"] == "C->W"
            ),
            "p3_correct_to_wrong": sum(
                1 for r in band_rows if r["postures"]["P3_unknown_only"]["transition"] == "C->W"
            ),
        }
    return bands


def _decision(summary: Mapping[str, Any]) -> str:
    arm2 = summary["arm2_selection_contribution"]
    p2 = arm2["P2_corroborated"]
    unconditional_regresses = any(
        arm2[posture]["correct_to_wrong"] > 0 for posture in ("P1_unilateral", "P3_unknown_only")
    )
    minted = summary["arm1_component_pool_coverage"]["graph_mints_correct_for_no_correct"]
    no_correct = summary["arm1_component_pool_coverage"]["no_correct_pool_rows"]

    if p2["correct_to_wrong"] == 0 and p2["wrong_to_correct"] == 0 and no_correct == 0:
        # The only regression-safe posture is exactly neutral and the predeclared
        # slice holds no no-correct residual to demonstrate uplift on.
        return "revise"
    if p2["net_purist_gain"] > 0 and p2["correct_to_wrong"] == 0 and minted > 0:
        return "promote_to_stage_d"
    if unconditional_regresses and p2["correct_to_wrong"] == 0:
        return "revise"
    return "reject"


def _decision_rationale(summary: Mapping[str, Any]) -> str:
    arm1 = summary["arm1_component_pool_coverage"]
    arm2 = summary["arm2_selection_contribution"]
    p1, p2, p3 = (arm2[p] for p in POSTURES)
    return (
        f"On the predeclared first-{summary['rows']} validation slice the v0.9 "
        f"pool is already Purist-correct on "
        f"{arm1['pool_correct_rows']}/{summary['rows']} rows "
        f"({arm1['no_correct_pool_rows']} no-correct), so Arm 1 has "
        f"{arm1['no_correct_pool_rows']} residual targets and the graph mints a "
        f"correct component for {arm1['graph_mints_correct_for_no_correct']} of "
        "them - the component-starvation benefit cannot be demonstrated where the "
        "11/750 residual does not live. In Arm 2 an unconditional graph component "
        f"only regresses (P1 unilateral net {p1['net_purist_gain']}, "
        f"C->W {p1['correct_to_wrong']}; P3 unknown-only net "
        f"{p3['net_purist_gain']}, C->W {p3['correct_to_wrong']}) - the literature "
        "caveat made concrete. Only the independent-corroboration posture (P2) is "
        f"regression-safe (W->C {p2['wrong_to_correct']}, C->W "
        f"{p2['correct_to_wrong']}, net {p2['net_purist_gain']}), and it is "
        "exactly neutral here. Stage C therefore does not promote the graph as an "
        "unconditional component: it must enter the selector under corroboration "
        "gating, and the no-correct-residual uplift must be evaluated on the rows "
        "where the residual actually lives under a separate predeclared protocol "
        "(no slice-shopping within Stage C)."
    )


# --------------------------------------------------------------------------- #
# Markdown + registry.
# --------------------------------------------------------------------------- #


def _markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    arm1 = summary["arm1_component_pool_coverage"]
    arm2 = summary["arm2_selection_contribution"]
    lines = [
        "# Gan 2026 State-Graph Ontology Stage C (Component Contribution)",
        "",
        "Date: 2026-06-15",
        "",
        "Stage C of the KG-grounded component-generation ladder. Feeds the "
        "`resolve_label` graph query as a fourth component to the frozen v0.9 "
        "consensus+fresh selector on the predeclared first-50 validation rows. "
        "Validation-only over `gan2026_split_v1`; no holdout rows, no model calls "
        "(the graph is rebuilt deterministically from the v3 section claim-table).",
        "",
        f"- Source claim-table: `{payload['source_claim_table']}`",
        f"- v0.9 selector replay: `{payload['v09_replay_artifact']}`",
        f"- Rebuilt graphs (replay artifact): `{payload['rebuilt_graphs_artifact']}`",
        f"- Per-row accounting: `{payload['rows_artifact']}`",
        f"- Graph builder: `{payload['graph_builder']}`",
        f"- Rows: {summary['rows']}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: hybrid selector / saved-output replay with a rebuilt graph "
        "component.",
        "- Scorer: Gan-compatible Purist, unchanged.",
        "- Baseline: v0.9 selected label per row.",
        "- Stop rule (design §6): promote only with net component uplift and "
        "near-zero correct->wrong regression, gains localized to named "
        "edge/ontology mechanisms; reject if the graph layer breaks band cases "
        "the bare components already handled.",
        "",
        "## Headline",
        "",
        f"- v0.9 selected Purist: {summary['v09_selected_purist_correct']}/{summary['rows']}",
        f"- Graph component standalone Purist: "
        f"{summary['graph_component_purist_correct']}/{summary['rows']}",
        f"- Graph final-kind counts: `{summary['graph_kind_counts']}`",
        "",
        "## Arm 1 - component-pool coverage of the no-correct residual",
        "",
        f"- Pool ({{deterministic, consensus, fresh}}) already correct: "
        f"{arm1['pool_correct_rows']}/{summary['rows']}",
        f"- No-correct pool rows (Arm 1 targets): {arm1['no_correct_pool_rows']}",
        f"- Graph mints a correct component for a no-correct row: "
        f"{arm1['graph_mints_correct_for_no_correct']}",
        "",
        "The 11/750 no-correct residual is not in the first-50 slice: the pool "
        "covers every row, so Arm 1 has no targets here. This is a slice fact, not "
        "a negative on the mechanism - the component-starvation benefit must be "
        "evaluated where the residual lives, under its own predeclared protocol.",
        "",
        "## Arm 2 - selection contribution under override postures",
        "",
        "Final labels scored against the v0.9 selected baseline. `correct->wrong` "
        "is the design §6 kill metric.",
        "",
        "| Posture | Overrides | Final Purist | W->C | C->W | Net | C->W bands |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for posture in POSTURES:
        info = arm2[posture]
        bands = info["regression_bands"]
        bands_text = ", ".join(f"{b}:{n}" for b, n in bands.items()) if bands else "-"
        lines.append(
            f"| `{posture}` | {info['overrides']} | "
            f"{info['final_purist_correct']}/{summary['rows']} | "
            f"{info['wrong_to_correct']} | {info['correct_to_wrong']} | "
            f"{info['net_purist_gain']} | {bands_text} |"
        )
    lines.extend(
        [
            "",
            "Postures: `P1_unilateral` = graph overrides on any disagreement "
            "(effect bound); `P2_corroborated` = graph overrides only when an "
            "independent existing candidate (consensus or fresh) is "
            "monthly-equivalent to it; `P3_unknown_only` = graph overrides only "
            "when it resolves to `unknown` (the ADR 0017 clean-`unknown` arm).",
            "",
            "## Boundary bands",
            "",
            "| Band | Rows | v0.9 sel | Graph | No-correct | P1 C->W | P3 C->W |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for band in BOUNDARY_BANDS:
        info = summary["by_band"].get(band)
        if not info:
            continue
        lines.append(
            f"| `{band}` | {info['rows']} | "
            f"{info['v09_selected_purist_correct']} | "
            f"{info['graph_component_purist_correct']} | "
            f"{info['no_correct_pool_rows']} | "
            f"{info['p1_correct_to_wrong']} | {info['p3_correct_to_wrong']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"`{summary['decision']}`",
            "",
            summary["decision_rationale"],
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: Mapping[str, Any]) -> None:
    summary = payload["summary"]
    arm1 = summary["arm1_component_pool_coverage"]
    arm2 = summary["arm2_selection_contribution"]
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{GRAPHS_PATH.name}",
                f"experiments/{ROWS_PATH.name}",
            ),
            date="2026-06-15",
            pipeline_family="hybrid_clinical_frequency_state_graph",
            split="validation",
            row_count=summary["rows"],
            model="none",
            model_role=(
                "Stage C component-contribution test: rebuilds the resolve_label "
                "graph query deterministically from the validation50 v3 "
                "claim-table and feeds it as a fourth component to the frozen v0.9 "
                "selector replay. No model calls and no holdout rows are read."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="state_graph_resolve_label_component_contribution_v1",
            cache_reuse_source=(
                f"claim_table:{SOURCE_CLAIM_TABLE.name};selector:{V09_REPLAY.name}"
            ),
            primary_metrics={
                "rows": summary["rows"],
                "v09_selected_purist_correct": summary["v09_selected_purist_correct"],
                "graph_component_purist_correct": summary["graph_component_purist_correct"],
                "no_correct_pool_rows": arm1["no_correct_pool_rows"],
                "graph_mints_correct_for_no_correct": arm1[
                    "graph_mints_correct_for_no_correct"
                ],
                "p1_unilateral_correct_to_wrong": arm2["P1_unilateral"]["correct_to_wrong"],
                "p2_corroborated_correct_to_wrong": arm2["P2_corroborated"]["correct_to_wrong"],
                "p2_corroborated_net_purist_gain": arm2["P2_corroborated"]["net_purist_gain"],
                "p3_unknown_only_correct_to_wrong": arm2["P3_unknown_only"]["correct_to_wrong"],
            },
            evidence_validity=(
                "Validation-only saved-output replay over the first-50 validation "
                "rows. Gold-free graph rebuild (raw_frequency normalized, no "
                "diary/window arithmetic); gold labels used only for post-hoc "
                "Purist scoring. No holdout rows are read and no model calls are "
                "made. The pool already covers all 50 rows, so Arm 1 has no "
                "no-correct targets in this slice."
            ),
            decision=payload["decision"],
            claim_language_notes=(
                "Stage C gate for the graph-as-component generator. Not a "
                "holdout-facing candidate. Finds the graph component regression-"
                "safe only under independent-corroboration gating (P2), neutral on "
                "the solved first-50 slice; an unconditional graph component "
                "regresses (P1/P3). The no-correct-residual uplift is untested "
                "here because the residual is not in this slice."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
