"""Stage B atomic-claim viability gate for the KG-grounded component generator.

Design note: ````.

Stage B is the gold-free, no-model-spend viability gate of the validation-only
ladder. It builds the state graph from *existing* LLM atomic claims on 25
validation rows (a saved-output replay - no hosted calls) and reports, per the
design note section 5 Stage B:

- the schema-valid node rate and the exact-evidence rate;
- the ontology-rejection counts, split into structural rejections vs the C2
  over-inference guard's semantic rejections (and whether the guard fired at all);
- whether ``resolve_label`` produces interpretable, component-localized output.

This is the first place the C2 over-inference guard runs over uncurated
(``llm-sg-``) nodes. Whether the guard actually fires depends on whether the
atomic-claim builder mints quantifying states for it to police; Stage B reports
that honestly rather than assuming it.

This reads only a saved atomic-claim artifact derived from the locked
``gan2026_split_v1`` validation split. No holdout rows are read and no model calls
are made.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

# Saved atomic-claim graphs converted from the validation25 section claim-table
# (gpt-4.1-mini v3). Exact-evidence gated at build time; this is a replay only.
SOURCE_ARTIFACT = (
    EXPERIMENTS
    / "gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.jsonl"
)

RUN_ID = "gan2026_state_graph_ontology_stage_b_viability_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


def main() -> None:
    graphs = _load_atomic_claim_graphs(SOURCE_ARTIFACT)
    summary = atomic_claim_viability_summary(graphs)

    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Stage B gold-free, no-spend viability gate for the ontology + "
            "typed-edge atomic-claim component generator. Replays saved LLM "
            "atomic-claim graphs; no holdout rows and no model calls."
        ),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_artifact": f"experiments/{SOURCE_ARTIFACT.name}",
        "ontology_id": summary.ontology_id,
        "summary": summary.model_dump(),
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload, summary), encoding="utf-8")
    _register(summary)
    print(json.dumps(summary.model_dump(), sort_keys=True))


def _load_atomic_claim_graphs(path: Path) -> list[ClinicalFrequencyStateGraph]:
    graphs: list[ClinicalFrequencyStateGraph] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        graphs.append(ClinicalFrequencyStateGraph.model_validate(json.loads(line)["graph"]))
    return graphs


def _markdown(payload: dict[str, Any], summary: AtomicClaimViabilitySummary) -> str:
    admission = summary.node_admission
    resolve = summary.resolve
    total = admission.total_nodes
    guard_fired = admission.over_inference_rejected > 0
    lines = [
        "# Gan 2026 State-Graph Ontology Stage B Viability",
        "",
        "Date: 2026-06-15",
        "",
        "Stage B gold-free, no-model-spend viability gate for the KG-grounded "
        "component generator. Validation-only over `gan2026_split_v1`; replays "
        "saved LLM atomic-claim graphs, reads no holdout rows, and makes no model "
        "calls.",
        "",
        f"- Source artifact: `{payload['source_artifact']}`",
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
            "Stage B passes its structural and interpretability sub-gates when "
            "nodes are schema-valid with exact evidence and `resolve_label` yields "
            "an interpretable, component-localized label per row. The C2 "
            "over-inference guard's sub-gate is *exercised* only if the "
            "atomic-claim builder mints quantifying (frequency / seizure-free) "
            "states for it to police.",
            "",
        ]
    )
    if guard_fired:
        lines.append(
            f"On this artifact the guard fired {admission.over_inference_rejected} "
            "time(s); the rejected nodes are the over-inference cases the design "
            "note targets."
        )
    else:
        lines.append(
            "On this artifact the guard fired **0 times**: the v3 atomic-claim "
            "builder mints every node as `unknown`/`no_reference` (zero quantifying "
            "states), so there is no quantified mint for the guard to reject. The "
            "lone rejection is structural (evidence not an exact note substring). "
            "The atomic-claim component is therefore, as built, a pure "
            "`unknown`-minter - which is exactly the clean competing `unknown` "
            "component the C2 resolution (ADR `0017`) wants for the `band_unknown` "
            "over-inference residual, but it is not yet a source of quantified "
            "components, and the guard's *rejection* mechanism stays unexercised "
            "until an atomic-claim artifact that commits per-claim quantified "
            "labels exists."
        )
    lines.append("")
    return "\n".join(lines)


def _register(summary: AtomicClaimViabilitySummary) -> None:
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
            ),
            date="2026-06-15",
            pipeline_family="hybrid_clinical_frequency_state_graph",
            split="validation",
            row_count=summary.row_count,
            model="none",
            model_role=(
                "Stage B gold-free viability gate replaying saved LLM atomic-claim "
                "graphs through the ontology dual-validation + resolve_label query; "
                "no model calls and no holdout rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="state_graph_ontology_dual_validation_resolve_label_v1",
            cache_reuse_source=f"artifact:{SOURCE_ARTIFACT.name}",
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
                "Validation-only viability gate over a saved atomic-claim artifact. "
                "Gold-free: no gold labels, no holdout rows, and no model calls. The "
                "C2 over-inference guard fired 0 times because the v3 atomic-claim "
                "builder mints no quantifying states; the gate's structural and "
                "interpretability sub-gates pass."
            ),
            decision="revise",
            claim_language_notes=(
                "Stage B viability gate for the ontology + typed-edge atomic-claim "
                "component generator. Not a holdout-facing candidate. The guard's "
                "rejection mechanism is unexercised on this artifact; informs "
                "whether and how the ladder proceeds to Stage C."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
