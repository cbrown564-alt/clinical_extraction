"""Stage B (rebuilt) atomic-claim viability gate that exercises the C2 guard.

Design note: ````.

The first Stage B pass replayed the 2026-06-02 atomic-claim graphs, where every
node had been minted as ``unknown`` because the conversion dropped each claim's
``raw_frequency``; the C2 over-inference guard had nothing to police and fired 0
times. This runner rebuilds the graphs from the *same* validation25 section
claim-table source (gpt-4.1-mini v3), but normalizes each claim's
``raw_frequency`` into a Gan-compatible label via the project's scorer-facing
grammar (``state_graph/claim_table.py``). That mints quantifying (frequency /
seizure-free) states wherever the source-near evidence warrants one, so the guard
is finally exercised over uncurated (``llm-sg-``) over-inference.

The rebuilt graphs are persisted to a JSONL artifact so the viability scoring is a
pure replay. Validation-only over ``gan2026_split_v1``: no holdout rows are read
and no model calls are made (label normalization is deterministic).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    AtomicClaimViabilitySummary,
    ClinicalFrequencyStateGraph,
    atomic_claim_viability_summary,
    atomic_claims_from_structured_record,
    build_state_graph_from_atomic_claims,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

# The same v3 section claim-table source the 2026-06-02 conversion used, but here
# re-converted with raw_frequency normalization so quantifying states are minted.
SOURCE_CLAIM_TABLE = (
    EXPERIMENTS / "gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.jsonl"
)

GRAPH_BUILDER = "llm_atomic_claim_graph_builder_v3_raw_frequency_normalized"

RUN_ID = "gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15"
GRAPHS_PATH = EXPERIMENTS / f"{RUN_ID}_graphs.jsonl"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


def main() -> None:
    graphs = _rebuild_graphs()
    _write_graphs_artifact(graphs)
    summary = atomic_claim_viability_summary(graphs)

    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Stage B (rebuilt) viability gate. Re-converts the validation25 v3 "
            "section claim-table with raw_frequency normalization so the ontology "
            "over-inference guard is exercised on quantifying atomic-claim mints. "
            "Validation-only; no holdout rows and no model calls."
        ),
        "split": "validation",
        "split_manifest": split_manifest,
        "source_claim_table": f"experiments/{SOURCE_CLAIM_TABLE.name}",
        "rebuilt_graphs_artifact": f"experiments/{GRAPHS_PATH.name}",
        "graph_builder": GRAPH_BUILDER,
        "ontology_id": summary.ontology_id,
        "summary": summary.model_dump(),
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload, summary), encoding="utf-8")
    _register(summary, split_manifest)
    print(json.dumps(summary.model_dump(), sort_keys=True))


def _rebuild_graphs() -> list[ClinicalFrequencyStateGraph]:
    records_by_index = {r.source_row_index: r for r in load_records_for_split("validation")}
    graphs: list[ClinicalFrequencyStateGraph] = []
    for line in SOURCE_CLAIM_TABLE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        source_row_index = int(row["source_row_index"])
        record = records_by_index[source_row_index]
        claims = atomic_claims_from_structured_record(row.get("structured_record"))
        graphs.append(
            build_state_graph_from_atomic_claims(
                record.note_text,
                claims,
                source_row_index=source_row_index,
                graph_builder=GRAPH_BUILDER,
            )
        )
    return graphs


def _write_graphs_artifact(graphs: list[ClinicalFrequencyStateGraph]) -> None:
    lines = [
        json.dumps(
            {"source_row_index": graph.source_row_index, "graph": graph.model_dump(mode="json")},
            sort_keys=True,
        )
        for graph in graphs
    ]
    GRAPHS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _markdown(payload: dict[str, Any], summary: AtomicClaimViabilitySummary) -> str:
    admission = summary.node_admission
    resolve = summary.resolve
    total = admission.total_nodes
    guard_fired = admission.over_inference_rejected > 0
    lines = [
        "# Gan 2026 State-Graph Ontology Stage B (Rebuilt, raw_frequency-normalized)",
        "",
        "Date: 2026-06-15",
        "",
        "Stage B viability gate, rebuilt from the v3 section claim-table with "
        "`raw_frequency` normalization so the ontology over-inference guard is "
        "exercised on quantifying mints. Validation-only over `gan2026_split_v1`; "
        "no holdout rows, no model calls (label normalization is deterministic).",
        "",
        f"- Source claim-table: `{payload['source_claim_table']}`",
        f"- Rebuilt graphs (replay artifact): `{payload['rebuilt_graphs_artifact']}`",
        f"- Graph builder: `{payload['graph_builder']}`",
        f"- Ontology: `{summary.ontology_id}`",
        f"- Rows: {summary.row_count}",
        "",
        "## Node admission (schema + evidence + ontology gate)",
        "",
        f"- Total atomic-claim nodes: {total}",
        f"- Schema-valid (structural): {admission.structural_valid}/{total}",
        f"- Exact-evidence (located span): {admission.exact_evidence}/{total}",
        f"- Semantic-valid (ontology assignment): {admission.semantic_valid}/{total}",
        f"- Admitted as components: {admission.admitted}/{total}",
        f"- Structural rejections: {admission.structural_rejected}",
        f"- Over-inference (C2 guard) rejections: {admission.over_inference_rejected}",
        "",
        "### Rejection reasons",
        "",
    ]
    if admission.rejection_reasons:
        lines.append("| Reason | Count |")
        lines.append("| --- | ---: |")
        for reason, count in admission.rejection_reasons.items():
            lines.append(f"| `{reason}` | {count} |")
    else:
        lines.append("_No nodes rejected._")
    lines.extend(
        [
            "",
            "### Evidence-shape distribution",
            "",
            "| Shape | Count |",
            "| --- | ---: |",
        ]
    )
    for shape, count in admission.evidence_shape_counts.items():
        lines.append(f"| `{shape}` | {count} |")
    lines.extend(
        [
            "",
            "## resolve_label interpretability",
            "",
            f"- Rows with a decision trace: {resolve.rows_with_decision_trace}/{resolve.row_count}",
            f"- Rows component-localized (label attributed to admitted nodes): "
            f"{resolve.rows_with_localized_selection}/{resolve.row_count}",
            f"- Rows defaulted to no-reference (nothing admitted): "
            f"{resolve.rows_defaulted_no_admission}/{resolve.row_count}",
            "",
            "### Final-kind distribution",
            "",
            "| Final kind | Rows |",
            "| --- | ---: |",
        ]
    )
    for kind, count in resolve.final_kind_counts.items():
        lines.append(f"| `{kind}` | {count} |")
    lines.extend(
        [
            "",
            "## Gate reading",
            "",
            "With `raw_frequency` normalized, the atomic-claim graph now mints "
            "quantifying states and the final-kind distribution is no longer "
            "uniformly `unknown` - so the component pool can contribute genuine "
            "frequency / seizure-free candidates, not only the clean `unknown`.",
            "",
        ]
    )
    if guard_fired:
        lines.append(
            f"The C2 over-inference guard is now **exercised**: it fired "
            f"{admission.over_inference_rejected} time(s), and every firing is an "
            "`over_inference_out_of_unknown:<shape>` rejection - a node whose "
            "`raw_frequency` parsed to a rate/seizure-free duration but whose "
            "evidence shape is unknown-only (e.g. a `last_event_only` mention). "
            "The rejected nodes are retained with provenance, never silently "
            "dropped, and the row falls through to its other admitted components."
        )
    else:
        lines.append(
            "The guard still fired 0 times even after normalization: no uncurated "
            "node committed a quantifying state out of an unknown-only evidence "
            "shape. This is a finding, not a pass - see the design note."
        )
    lines.append("")
    return "\n".join(lines)


def _register(summary: AtomicClaimViabilitySummary, split_manifest: str) -> None:
    admission = summary.node_admission
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
            ),
            date="2026-06-15",
            pipeline_family="hybrid_clinical_frequency_state_graph",
            split="validation",
            row_count=summary.row_count,
            model="none",
            model_role=(
                "Stage B (rebuilt) viability gate: re-converts the v3 claim-table "
                "with deterministic raw_frequency normalization, then runs the "
                "ontology dual-validation + resolve_label query. No model calls and "
                "no holdout rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="state_graph_ontology_dual_validation_resolve_label_v1",
            cache_reuse_source=f"claim_table:{SOURCE_CLAIM_TABLE.name}",
            primary_metrics={
                "total_nodes": admission.total_nodes,
                "structural_valid": admission.structural_valid,
                "exact_evidence": admission.exact_evidence,
                "admitted": admission.admitted,
                "over_inference_rejected": admission.over_inference_rejected,
                "structural_rejected": admission.structural_rejected,
                "rows_component_localized": summary.resolve.rows_with_localized_selection,
            },
            evidence_validity=(
                "Validation-only viability gate over rebuilt atomic-claim graphs. "
                "Gold-free: no gold labels, no holdout rows, and no model calls. "
                "raw_frequency is normalized with the project scorer-facing grammar "
                "(no diary/window arithmetic). The C2 over-inference guard fired "
                f"{admission.over_inference_rejected} time(s) on uncurated "
                "quantifying mints out of unknown-only evidence shapes."
            ),
            decision="revise",
            claim_language_notes=(
                "Stage B (rebuilt) gate for the ontology + typed-edge atomic-claim "
                "component generator. Not a holdout-facing candidate. The guard is "
                "now exercised; informs whether the ladder proceeds to Stage C."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
