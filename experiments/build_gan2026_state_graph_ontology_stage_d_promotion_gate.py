"""Stage D - 250-row promotion gate for the graph query on the no-correct residual.

Design note: ````
§5 (Stage D), §6 (promotion contract / kill metric), and §8.5 (the Stage C
``revise`` that mandates this stage); ADR ``0017`` (the C2 parallel posture);
resolve_label spec ``docs/design/gan2026_resolve_label_spec.md`` §5 (the ablation
contract: report W->C / C->W and per-band changed-label precision, especially
``band_weekly`` and ``band_unknown``).

Stage C (§8.5) returned ``revise`` for one structural reason: the predeclared
first-50 slice contained *none* of the ``11/750`` no-correct residual, so the
component-starvation benefit - the entire reason the generator exists - could not
be demonstrated. Stage C also established that the *only* regression-safe
integration is the independent-corroboration posture (``P2``); an unconditional
graph component regresses (P1/P3). Stage D therefore does exactly what §8.5
prescribes: wire the **same P2-gated graph component** at 250-row scale on a
predeclared slice that **actually contains the 11/750 residual**.

Predeclared protocol (fixed before the run; no slice-shopping):

* **Slice.** The 250-row Stage D slice = the **11 no-correct residual rows**
  (from the frozen v0.9 residual component-generation audit) UNION the **first 239
  non-residual validation rows in ``source_row_index`` order**. This is a single
  deterministic, reproducible rule: it guarantees every residual row is present
  and is 250-row scale, and it is chosen by source order (not by outcome).

* **Claim extractor.** The graphs are rebuilt from the ``validation750`` v4
  section claim-table. This is the *only* no-call source that covers the residual:
  the v3 table the earlier ladder used (Stage A/B/C) was never run past the first
  250 validation rows, so 10 of the 11 residual rows are unreachable under v3
  without new model calls. The v3->v4 extractor change is a declared confound; it
  is held *constant across the whole Stage D slice* (residual and fill alike use
  v4), so the within-slice comparison is internally consistent, and a v3<->v4
  cross-check on the one overlap row (5534) is reported as a robustness probe.

* **Component under test.** Identical ``resolve_label`` / ontology / typed-edge
  query as Stage A/B/C - only the upstream extractor and the slice differ. ``P2``
  (corroborated) is the promotion-decision posture; ``P1``/``P3`` are reported as
  effect bounds, as in Stage C.

This is a no-call replay: the graph is rebuilt deterministically (raw_frequency
normalized, no diary/window arithmetic); the deterministic/consensus/fresh
components and the v0.9 selected baseline come from the saved v0.9 validation750
replay. Validation-only over ``gan2026_split_v1``: no holdout rows are read and no
model calls are made. A ``promote`` decision clears the **validation ladder**
only; the locked ``test450`` holdout still requires a separate frozen protocol and
explicit authorization (design §4).
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

# The only no-call section claim-table that covers the residual: v4 at full
# validation750 scale (v3 was never run past the first 250 rows).
SOURCE_CLAIM_TABLE = (
    EXPERIMENTS / "gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl"
)
# The v3 table the earlier ladder used; only row 5534 overlaps with the residual.
# Used solely for the v3<->v4 cross-check probe.
V3_OVERLAP_TABLE = (
    EXPERIMENTS / "gan2026_section_claim_table_validation250_gpt41mini_v3_2026-06-01.jsonl"
)
# The frozen v0.9 selector replay supplying the deterministic/consensus/fresh
# components and the selected baseline for each row (covers all 750).
V09_REPLAY = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "validation750_no_call_replay_2026-06-15.jsonl"
)
# The frozen audit that identifies the 11/750 no-correct residual rows + categories.
RESIDUAL_AUDIT = (
    EXPERIMENTS
    / "gan2026_consensus_fresh_agreement_selector_v0_9_"
    "residual_component_generation_audit_2026-06-15.json"
)

GRAPH_BUILDER = "llm-sg-stage-d-v4-raw-frequency-normalized"
V3_GRAPH_BUILDER = "llm-sg-stage-d-v3-overlap-crosscheck"

SLICE_SIZE = 250
RUN_ID = "gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15"
GRAPHS_PATH = EXPERIMENTS / f"{RUN_ID}_graphs.jsonl"
ROWS_PATH = EXPERIMENTS / f"{RUN_ID}_rows.jsonl"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

POSTURES = ("P1_unilateral", "P2_corroborated", "P3_unknown_only")
PROMOTION_POSTURE = "P2_corroborated"

# The Stage D gate uses a descriptive decision string in the payload/doc, but the
# shared run registry enforces a fixed decision enum. Map onto it.
REGISTRY_DECISION = {
    "promote_clears_validation_ladder": "promote",
    "revise": "revise",
    "reject": "reject",
}


def main() -> None:
    residual = _load_residual()
    residual_indices = {rec["source_row_index"] for rec in residual}
    v4_rows = _load_claim_table(SOURCE_CLAIM_TABLE)
    slice_indices = _build_predeclared_slice(v4_rows, residual_indices)

    graphs, graph_labels = _build_graphs_and_labels(v4_rows, slice_indices)
    _write_graphs_artifact(graphs)
    v09_by_index = _load_v09_rows()

    rows = _build_rows(graph_labels, v09_by_index, residual_indices)
    _write_rows_artifact(rows)
    cross_check = _v3_v4_cross_check(graph_labels)
    summary = _summarize(rows, residual, slice_indices, cross_check)

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Stage D promotion gate. Wires the P2-gated resolve_label graph query "
            "as a fourth component to the frozen v0.9 consensus+fresh selector on a "
            "predeclared 250-row slice that contains all 11/750 no-correct residual "
            "rows. Reports component-pool coverage of the residual (Arm 1) and "
            "selection contribution with per-band changed-label precision (Arm 2), "
            "the design-§6 correct->wrong kill metric, and a v3<->v4 cross-check. "
            "Validation-only; no holdout rows and no model calls."
        ),
        "split": "validation",
        "split_manifest": split_manifest,
        "predeclared_slice": (
            "11 no-correct residual rows UNION the first 239 non-residual "
            "validation rows in source_row_index order; 250 rows; deterministic, "
            "reproducible, residual-inclusive, source-ordered (no slice-shopping)."
        ),
        "source_claim_table": f"experiments/{SOURCE_CLAIM_TABLE.name}",
        "source_claim_table_note": (
            "v4 at validation750 scale - the only no-call source covering the "
            "residual; v3 (Stage A/B/C) was never run past the first 250 rows. "
            "Declared confound, held constant across the whole Stage D slice."
        ),
        "v09_replay_artifact": f"experiments/{V09_REPLAY.name}",
        "residual_audit_artifact": f"experiments/{RESIDUAL_AUDIT.name}",
        "rebuilt_graphs_artifact": f"experiments/{GRAPHS_PATH.name}",
        "rows_artifact": f"experiments/{ROWS_PATH.name}",
        "graph_builder": GRAPH_BUILDER,
        "promotion_posture": PROMOTION_POSTURE,
        "summary": summary,
    }
    payload["decision"] = summary["decision"]
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


# --------------------------------------------------------------------------- #
# Inputs: residual audit, claim table, predeclared slice.
# --------------------------------------------------------------------------- #


def _load_residual() -> list[dict[str, Any]]:
    audit = json.loads(RESIDUAL_AUDIT.read_text(encoding="utf-8"))
    records = audit["summary"]["selected_wrong_records"]
    no_correct = [rec for rec in records if not rec.get("correct_components")]
    return [
        {
            "source_row_index": int(rec["source_row_index"]),
            "gold_band": rec["gold_band"],
            "gold_label": rec["gold_label"],
            "audit_categories": list(rec.get("audit_categories", [])),
        }
        for rec in no_correct
    ]


def _load_claim_table(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows[int(row["source_row_index"])] = row
    return rows


def _build_predeclared_slice(
    v4_rows: Mapping[int, dict[str, Any]], residual_indices: set[int]
) -> list[int]:
    """Residual rows + first 239 non-residual rows in source order = 250 rows."""
    ordered = sorted(v4_rows)
    non_residual = [i for i in ordered if i not in residual_indices]
    fill = non_residual[: SLICE_SIZE - len(residual_indices)]
    slice_set = set(residual_indices) | set(fill)
    if len(slice_set) != SLICE_SIZE:
        raise ValueError(
            f"predeclared slice is {len(slice_set)} rows, expected {SLICE_SIZE}"
        )
    missing_residual = residual_indices - slice_set
    if missing_residual:
        raise ValueError(f"residual rows missing from slice: {sorted(missing_residual)}")
    missing_records = [i for i in slice_set if not v4_rows[i].get("structured_record")]
    if missing_records:
        raise ValueError(f"slice rows lack structured_record: {sorted(missing_records)}")
    return sorted(slice_set)


# --------------------------------------------------------------------------- #
# Graph rebuild (same conversion as Stage B/C: raw_frequency normalized).
# --------------------------------------------------------------------------- #


def _build_graphs_and_labels(
    v4_rows: Mapping[int, dict[str, Any]], slice_indices: Sequence[int]
) -> tuple[list[ClinicalFrequencyStateGraph], dict[int, dict[str, Any]]]:
    records_by_index = {r.source_row_index: r for r in load_records_for_split("validation")}
    graphs: list[ClinicalFrequencyStateGraph] = []
    labels: dict[int, dict[str, Any]] = {}
    for source_row_index in slice_indices:
        row = v4_rows[source_row_index]
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


def _v3_v4_cross_check(graph_labels: Mapping[int, dict[str, Any]]) -> dict[str, Any]:
    """Rebuild the one overlap residual row (5534) from v3 and compare to v4."""
    overlap = 5534
    if overlap not in graph_labels:
        return {"overlap_row": overlap, "available": False}
    v3_rows = _load_claim_table(V3_OVERLAP_TABLE)
    if overlap not in v3_rows or not v3_rows[overlap].get("structured_record"):
        return {"overlap_row": overlap, "available": False}
    record = next(
        r for r in load_records_for_split("validation") if r.source_row_index == overlap
    )
    claims = atomic_claims_from_structured_record(v3_rows[overlap].get("structured_record"))
    graph = build_state_graph_from_atomic_claims(
        record.note_text,
        claims,
        source_row_index=overlap,
        graph_builder=V3_GRAPH_BUILDER,
    )
    v3_res = resolve_label(graph)
    v4 = graph_labels[overlap]
    return {
        "overlap_row": overlap,
        "available": True,
        "v3_graph_label": v3_res.final_label,
        "v3_graph_kind": v3_res.final_kind.value,
        "v4_graph_label": v4["graph_label"],
        "v4_graph_kind": v4["graph_kind"],
        "purist_equivalent": _monthly_equivalent(v3_res.final_label, v4["graph_label"]),
    }


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
    residual_indices: set[int],
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
                "is_residual": source_row_index in residual_indices,
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


def _summarize(
    rows: Sequence[Mapping[str, Any]],
    residual: Sequence[Mapping[str, Any]],
    slice_indices: Sequence[int],
    cross_check: Mapping[str, Any],
) -> dict[str, Any]:
    total = len(rows)
    by_index = {row["source_row_index"]: row for row in rows}
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
            "changed_label_precision_by_band": _changed_label_precision(rows, posture),
        }

    # Arm 1 over the predeclared residual rows specifically.
    residual_rows = [by_index[rec["source_row_index"]] for rec in residual]
    residual_minted = [
        row for row in residual_rows if row["graph_mints_correct_for_no_correct"]
    ]
    # The crucial realized-vs-available number: of the residual rows where the
    # graph mints a correct component, how many does the *promotion posture* (P2)
    # actually recover at selection time. Corroboration cannot fire where every
    # other component is wrong, so minted (Arm 1) >> recovered (Arm 2) is expected.
    residual_p2_recovered = [
        row
        for row in residual_rows
        if row["postures"][PROMOTION_POSTURE]["transition"] == "W->C"
    ]
    residual_category = _residual_category_breakdown(residual, by_index)

    arm1 = {
        "rows": total,
        "pool_correct_rows": total - len(no_correct),
        "no_correct_pool_rows": len(no_correct),
        "no_correct_source_row_indices": [row["source_row_index"] for row in no_correct],
        "graph_mints_correct_for_no_correct": len(minted),
        "graph_minted_source_row_indices": [row["source_row_index"] for row in minted],
        "predeclared_residual_rows": len(residual_rows),
        "predeclared_residual_indices": [rec["source_row_index"] for rec in residual],
        "graph_mints_correct_for_predeclared_residual": len(residual_minted),
        "predeclared_residual_minted_indices": [
            row["source_row_index"] for row in residual_minted
        ],
        "p2_recovered_predeclared_residual": len(residual_p2_recovered),
        "p2_recovered_predeclared_residual_indices": [
            row["source_row_index"] for row in residual_p2_recovered
        ],
        "by_audit_category": residual_category,
    }
    summary = {
        "rows": total,
        "slice_source_row_indices": list(slice_indices),
        "v09_selected_purist_correct": sum(1 for row in rows if row["selected_correct"]),
        "graph_component_purist_correct": sum(1 for row in rows if row["graph_correct"]),
        "promotion_posture": PROMOTION_POSTURE,
        "arm1_residual_coverage": arm1,
        "arm2_selection_contribution": posture_summary,
        "by_band": _by_band(rows),
        "graph_kind_counts": dict(
            sorted(Counter(row["graph_kind"] for row in rows).items())
        ),
        "v3_v4_cross_check": dict(cross_check),
        "claim_boundary": (
            "Validation-only no-call replay on a predeclared 250-row slice that "
            "contains all 11/750 no-correct residual rows. The graph query is "
            "rebuilt deterministically from the validation750 v4 section "
            "claim-table (raw_frequency normalized, no diary/window arithmetic); "
            "the deterministic/consensus/fresh components and the v0.9 selected "
            "baseline come from the saved v0.9 replay. Gold labels are used only "
            "for post-hoc Purist scoring; no holdout rows are read."
        ),
    }
    summary["decision"] = _decision(summary)
    summary["decision_rationale"] = _decision_rationale(summary)
    return summary


def _residual_category_breakdown(
    residual: Sequence[Mapping[str, Any]],
    by_index: Mapping[int, Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    breakdown: dict[str, dict[str, int]] = defaultdict(lambda: {"rows": 0, "minted": 0})
    for rec in residual:
        row = by_index[rec["source_row_index"]]
        minted = bool(row["graph_mints_correct_for_no_correct"])
        for category in rec["audit_categories"]:
            breakdown[category]["rows"] += 1
            if minted:
                breakdown[category]["minted"] += 1
    return {k: breakdown[k] for k in sorted(breakdown)}


def _regression_bands(rows: Sequence[Mapping[str, Any]], posture: str) -> dict[str, int]:
    bands: Counter[str] = Counter()
    for row in rows:
        if row["postures"][posture]["transition"] == "C->W":
            bands[row["gold_band"]] += 1
    return dict(sorted(bands.items()))


def _changed_label_precision(
    rows: Sequence[Mapping[str, Any]], posture: str
) -> dict[str, dict[str, Any]]:
    """Per band: of the rows the posture overrode, how many landed Purist-correct.

    Changed-label precision is the design-§5 / spec-§5 Stage D metric. The graph
    is only allowed to *change* a baseline label; this measures whether those
    changes are right, per band, with band_weekly and band_unknown the val->test
    regression surface.
    """
    per_band: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["postures"][posture]["override"]:
            grouped[row["gold_band"]].append(row)
    for band in BOUNDARY_BANDS:
        band_rows = grouped.get(band, [])
        if not band_rows:
            continue
        correct = sum(1 for r in band_rows if r["postures"][posture]["final_correct"])
        per_band[band] = {
            "overrides": len(band_rows),
            "correct": correct,
            "precision": round(correct / len(band_rows), 4),
        }
    return per_band


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
            "p2_overrides": sum(
                1 for r in band_rows if r["postures"][PROMOTION_POSTURE]["override"]
            ),
            "p2_wrong_to_correct": sum(
                1
                for r in band_rows
                if r["postures"][PROMOTION_POSTURE]["transition"] == "W->C"
            ),
            "p2_correct_to_wrong": sum(
                1
                for r in band_rows
                if r["postures"][PROMOTION_POSTURE]["transition"] == "C->W"
            ),
        }
    return bands


def _decision(summary: Mapping[str, Any]) -> str:
    """Stage D promotion gate (design §6). The kill metric is P2 correct->wrong.

    - ``promote_clears_validation_ladder`` - P2 is regression-safe (0 C->W),
      shows net Purist uplift, mints >=1 correct component for a predeclared
      residual row, and does not regress band_weekly / band_unknown under P2.
      (Holdout still needs a separate frozen protocol; design §4.)
    - ``revise`` - P2 is regression-safe (0 C->W) but shows no net uplift or
      mints nothing on the residual: the mechanism is not falsified but the
      component-starvation benefit is undemonstrated at scale.
    - ``reject`` - P2 itself regresses (C->W > 0): corroboration gating, the only
      Stage C survivor, breaks band cases the pool already handled at scale.
    """
    arm2 = summary["arm2_selection_contribution"]
    p2 = arm2[PROMOTION_POSTURE]
    arm1 = summary["arm1_residual_coverage"]
    residual_minted = arm1["graph_mints_correct_for_predeclared_residual"]
    p2_bad_bands = {
        band
        for band, n in p2["regression_bands"].items()
        if band in ("band_weekly", "band_unknown") and n > 0
    }

    if p2["correct_to_wrong"] > 0:
        return "reject"
    if p2["net_purist_gain"] > 0 and residual_minted > 0 and not p2_bad_bands:
        return "promote_clears_validation_ladder"
    return "revise"


def _band_precision(posture_info: Mapping[str, Any], band: str) -> str:
    info = posture_info["changed_label_precision_by_band"].get(band)
    if not info:
        return "n/a (no overrides)"
    return f"{info['correct']}/{info['overrides']}={info['precision']:.2f}"


def _decision_rationale(summary: Mapping[str, Any]) -> str:
    arm1 = summary["arm1_residual_coverage"]
    arm2 = summary["arm2_selection_contribution"]
    p1, p2, p3 = (arm2[p] for p in POSTURES)
    decision = summary["decision"]
    head = (
        f"Stage D wires the P2-gated graph component at 250-row scale on a "
        f"predeclared slice containing all {arm1['predeclared_residual_rows']} "
        f"no-correct residual rows. Arm 1: the graph mints a Purist-correct "
        f"component for {arm1['graph_mints_correct_for_predeclared_residual']}/"
        f"{arm1['predeclared_residual_rows']} predeclared residual rows "
        f"(and {arm1['graph_mints_correct_for_no_correct']}/"
        f"{arm1['no_correct_pool_rows']} of all no-correct rows in the slice). "
        f"Arm 2 (P2 corroborated, the only Stage C survivor): W->C "
        f"{p2['wrong_to_correct']}, C->W {p2['correct_to_wrong']} (the §6 kill "
        f"metric), net {p2['net_purist_gain']}; P2 regression bands "
        f"{p2['regression_bands'] or '{}'}. Effect bounds: P1 unilateral net "
        f"{p1['net_purist_gain']} (C->W {p1['correct_to_wrong']}), P3 unknown-only "
        f"net {p3['net_purist_gain']} (C->W {p3['correct_to_wrong']})."
    )
    if decision == "promote_clears_validation_ladder":
        tail = (
            f" P2 is regression-safe (0 C->W, no band_weekly/band_unknown "
            f"regression) with net uplift and band_unknown override precision "
            f"{_band_precision(p2, 'band_unknown')}, and the generator covers "
            f"{arm1['graph_mints_correct_for_predeclared_residual']}/"
            f"{arm1['predeclared_residual_rows']} of the component-starvation "
            "residual (the branch's raison d'etre), so it clears the validation "
            "ladder. Honest realized-vs-available gap: of those "
            f"{arm1['graph_mints_correct_for_predeclared_residual']} newly-minted "
            f"residual components P2 *recovers* only "
            f"{arm1['p2_recovered_predeclared_residual']} at selection time, "
            "because corroboration cannot fire where every other component is "
            "wrong (the defining property of the no-correct residual). The "
            "unrealized residual uplift is a downstream selection-posture problem "
            "(a corroboration-free trust rule for the graph's clean unknown that "
            "avoids P3's regressions), not a generator failure, and is the "
            "explicit next question. This is NOT a holdout authorization: test450 "
            "remains locked and requires a separate frozen protocol (design §4) "
            "that must weigh whether the realized selection uplift justifies the "
            "spend."
        )
    elif decision == "reject":
        tail = (
            " P2 - the only regression-safe Stage C posture - itself regresses at "
            "250-row scale, breaking band cases the pool already handled. That is "
            "the design-§6 reject trigger: the graph layer cannot enter the "
            "selector even under corroboration gating."
        )
    else:
        tail = (
            " P2 is regression-safe but shows no net Purist uplift / mints no "
            "correct residual component on this slice, so the component-starvation "
            "benefit is still undemonstrated at scale. The mechanism is not "
            "falsified (regression-safe under corroboration); the honest decision "
            "is revise, not promote - the graph's raison d'etre remains unproven "
            "where the residual lives, and the only safe integration adds nothing."
        )
    return head + tail


# --------------------------------------------------------------------------- #
# Markdown + registry.
# --------------------------------------------------------------------------- #


def _markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    arm1 = summary["arm1_residual_coverage"]
    arm2 = summary["arm2_selection_contribution"]
    cc = summary["v3_v4_cross_check"]
    lines = [
        "# Gan 2026 State-Graph Ontology Stage D (Promotion Gate)",
        "",
        "Date: 2026-06-15",
        "",
        "Stage D of the KG-grounded component-generation ladder. Wires the "
        "**P2-gated** `resolve_label` graph query as a fourth component to the "
        "frozen v0.9 consensus+fresh selector on a **predeclared 250-row slice "
        "that contains all 11/750 no-correct residual rows**. Validation-only over "
        "`gan2026_split_v1`; no holdout rows, no model calls (the graph is rebuilt "
        "deterministically from the v4 section claim-table).",
        "",
        f"- Predeclared slice: {payload['predeclared_slice']}",
        f"- Source claim-table: `{payload['source_claim_table']}`",
        f"  - {payload['source_claim_table_note']}",
        f"- v0.9 selector replay: `{payload['v09_replay_artifact']}`",
        f"- Residual audit: `{payload['residual_audit_artifact']}`",
        f"- Rebuilt graphs (replay artifact): `{payload['rebuilt_graphs_artifact']}`",
        f"- Per-row accounting: `{payload['rows_artifact']}`",
        f"- Graph builder: `{payload['graph_builder']}`",
        f"- Promotion posture: `{payload['promotion_posture']}`",
        f"- Rows: {summary['rows']}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: hybrid selector / saved-output replay with a rebuilt graph "
        "component, on a predeclared residual-inclusive slice.",
        "- Scorer: Gan-compatible Purist, unchanged.",
        "- Baseline: v0.9 selected label per row.",
        "- Promotion posture: `P2_corroborated` (graph overrides only when an "
        "independent existing candidate is monthly-equivalent) - the only "
        "regression-safe posture from Stage C.",
        "- Stop rule (design §6): the kill metric is P2 correct->wrong; promote "
        "only with net uplift, residual minting, and no band_weekly/band_unknown "
        "regression; reject if P2 itself regresses at scale.",
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
        f"- No-correct pool rows in slice: {arm1['no_correct_pool_rows']}",
        f"- Predeclared residual rows in slice: {arm1['predeclared_residual_rows']} "
        f"(`{arm1['predeclared_residual_indices']}`)",
        f"- Graph mints a correct component for a predeclared residual row: "
        f"**{arm1['graph_mints_correct_for_predeclared_residual']}/"
        f"{arm1['predeclared_residual_rows']}** "
        f"(`{arm1['predeclared_residual_minted_indices']}`)",
        f"- Graph mints a correct component for any no-correct slice row: "
        f"{arm1['graph_mints_correct_for_no_correct']}/{arm1['no_correct_pool_rows']}",
        f"- Of those, P2 (promotion posture) *recovers* at selection time: "
        f"**{arm1['p2_recovered_predeclared_residual']}/"
        f"{arm1['graph_mints_correct_for_predeclared_residual']}** "
        f"(`{arm1['p2_recovered_predeclared_residual_indices']}`) - corroboration "
        "cannot fire where every other component is wrong, so component "
        "availability (Arm 1) exceeds realized selection recovery (Arm 2).",
        "",
        "Residual minting by audit category:",
        "",
        "| Audit category | Residual rows | Minted correct |",
        "| --- | ---: | ---: |",
    ]
    for category, info in arm1["by_audit_category"].items():
        lines.append(f"| `{category}` | {info['rows']} | {info['minted']} |")
    lines.extend(
        [
            "",
            "## Arm 2 - selection contribution under override postures",
            "",
            "Final labels scored against the v0.9 selected baseline. `correct->wrong` "
            "is the design §6 kill metric; `P2_corroborated` is the promotion posture.",
            "",
            "| Posture | Overrides | Final Purist | W->C | C->W | Net | C->W bands |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for posture in POSTURES:
        info = arm2[posture]
        bands = info["regression_bands"]
        bands_text = ", ".join(f"{b}:{n}" for b, n in bands.items()) if bands else "-"
        marker = " (promotion)" if posture == PROMOTION_POSTURE else ""
        lines.append(
            f"| `{posture}`{marker} | {info['overrides']} | "
            f"{info['final_purist_correct']}/{summary['rows']} | "
            f"{info['wrong_to_correct']} | {info['correct_to_wrong']} | "
            f"{info['net_purist_gain']} | {bands_text} |"
        )
    lines.extend(
        [
            "",
            "### P2 changed-label precision by band (design §5 / spec §5)",
            "",
            "Of the rows P2 overrode, the share that landed Purist-correct, per "
            "band. `band_weekly` and `band_unknown` are the val->test regression "
            "surface.",
            "",
            "| Band | P2 overrides | Correct | Precision |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    p2_prec = arm2[PROMOTION_POSTURE]["changed_label_precision_by_band"]
    if p2_prec:
        for band in BOUNDARY_BANDS:
            info = p2_prec.get(band)
            if not info:
                continue
            lines.append(
                f"| `{band}` | {info['overrides']} | {info['correct']} | "
                f"{info['precision']:.2f} |"
            )
    else:
        lines.append("| (no P2 overrides) | 0 | 0 | - |")
    lines.extend(
        [
            "",
            "## Boundary bands",
            "",
            "| Band | Rows | v0.9 sel | Graph | No-correct | P2 ovr | P2 W->C | P2 C->W |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
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
            f"{info['p2_overrides']} | {info['p2_wrong_to_correct']} | "
            f"{info['p2_correct_to_wrong']} |"
        )
    lines.extend(["", "## v3<->v4 cross-check (overlap row 5534)", ""])
    if cc.get("available"):
        lines.append(
            f"- v3 graph: `{cc['v3_graph_label']}` ({cc['v3_graph_kind']}); "
            f"v4 graph: `{cc['v4_graph_label']}` ({cc['v4_graph_kind']}); "
            f"Purist-equivalent: {cc['purist_equivalent']}."
        )
        lines.append(
            "  The v3->v4 extractor change is a declared Stage D confound (only v4 "
            "covers the residual). On the single overlap row the two extractors "
            f"resolve to {'the same' if cc['purist_equivalent'] else 'different'} "
            "Purist class."
        )
    else:
        lines.append("- Overlap cross-check unavailable for row 5534.")
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
    arm1 = summary["arm1_residual_coverage"]
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
                "Stage D promotion gate: rebuilds the resolve_label graph query "
                "deterministically from the validation750 v4 claim-table and feeds "
                "it as a P2-gated fourth component to the frozen v0.9 selector "
                "replay on a predeclared 250-row residual-inclusive slice. No model "
                "calls and no holdout rows are read."
            ),
            mode="no-call replay",
            replay_status="saved_output_replay",
            repair_mode="state_graph_resolve_label_promotion_gate_v1",
            cache_reuse_source=(
                f"claim_table:{SOURCE_CLAIM_TABLE.name};selector:{V09_REPLAY.name};"
                f"residual_audit:{RESIDUAL_AUDIT.name}"
            ),
            primary_metrics={
                "rows": summary["rows"],
                "v09_selected_purist_correct": summary["v09_selected_purist_correct"],
                "graph_component_purist_correct": summary["graph_component_purist_correct"],
                "predeclared_residual_rows": arm1["predeclared_residual_rows"],
                "graph_mints_correct_for_predeclared_residual": arm1[
                    "graph_mints_correct_for_predeclared_residual"
                ],
                "no_correct_pool_rows": arm1["no_correct_pool_rows"],
                "graph_mints_correct_for_no_correct": arm1[
                    "graph_mints_correct_for_no_correct"
                ],
                "p2_corroborated_wrong_to_correct": arm2["P2_corroborated"]["wrong_to_correct"],
                "p2_corroborated_correct_to_wrong": arm2["P2_corroborated"]["correct_to_wrong"],
                "p2_corroborated_net_purist_gain": arm2["P2_corroborated"]["net_purist_gain"],
                "p1_unilateral_correct_to_wrong": arm2["P1_unilateral"]["correct_to_wrong"],
                "p3_unknown_only_correct_to_wrong": arm2["P3_unknown_only"]["correct_to_wrong"],
            },
            evidence_validity=(
                "Validation-only saved-output replay on a predeclared 250-row slice "
                "containing all 11/750 no-correct residual rows (residual UNION "
                "first 239 non-residual rows in source order). Gold-free graph "
                "rebuild from the v4 claim-table (raw_frequency normalized, no "
                "diary/window arithmetic; v3->v4 extractor change is a declared "
                "confound held constant across the slice); gold labels used only "
                "for post-hoc Purist scoring. No holdout rows are read and no model "
                "calls are made."
            ),
            decision=REGISTRY_DECISION[payload["decision"]],
            claim_language_notes=(
                "Stage D promotion gate for the graph-as-component generator. Not a "
                "holdout-facing candidate; a promote decision clears the validation "
                "ladder only and test450 remains locked behind a separate frozen "
                "protocol. The graph enters the selector only under independent-"
                "corroboration gating (P2, the Stage C survivor); P1/P3 are effect "
                "bounds. Evaluated where the no-correct residual actually lives."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
