"""Stage A oracle-uplift gate for the KG-grounded component generator.

Design note: ````.

Stage A is the no-model-spend gate of the validation-only ladder. It builds the
deterministic state graph for every validation row, dual-validates it under the
admissible-state ontology, and reports - broken out by frequency-boundary band -
whether the ontology + typed-edge enrichment lets ``resolve_label`` mint a
Purist-correct label where the un-gated projection over-infers. If Stage A shows
no uplift over the no-correct residual (concentrated in ``band_unknown`` and
``band_weekly``) and breaks no bands the baseline already handled, the mechanism
is wrong and the branch spends nothing further.

This reads only the locked ``gan2026_split_v1`` validation split. No holdout rows
are read and no model calls are made.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ontology_coverage_summary,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

RUN_ID = "gan2026_state_graph_ontology_oracle_uplift_stage_a_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


def main() -> None:
    records = load_records_for_split("validation")
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    summary = ontology_coverage_summary(records)

    payload = {
        "run_id": RUN_ID,
        "date": "2026-06-15",
        "purpose": (
            "Stage A no-spend oracle-uplift gate for the ontology + typed-edge "
            "state-graph component generator. Validation-only; no holdout rows "
            "and no model calls."
        ),
        "split": "validation",
        "split_manifest": split_manifest,
        "ontology_id": summary.ontology_id,
        "summary": _summary_payload(summary),
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary.row_count, payload["summary"], split_manifest)
    print(json.dumps(payload["summary"], sort_keys=True))


def _summary_payload(summary: Any) -> dict[str, Any]:
    return {
        "row_count": summary.row_count,
        "baseline_representable": summary.baseline_representable,
        "admitted_representable": summary.admitted_representable,
        "projection_correct": summary.projection_correct,
        "resolve_correct": summary.resolve_correct,
        "resolve_minus_projection": summary.resolve_minus_projection,
        "resolve_gain_rows": list(summary.resolve_gain_source_row_indices),
        "resolve_regression_rows": list(summary.resolve_regression_source_row_indices),
        "by_band": {
            band: {
                "total": cov.total,
                "baseline_representable": cov.baseline_representable,
                "admitted_representable": cov.admitted_representable,
                "projection_correct": cov.projection_correct,
                "resolve_correct": cov.resolve_correct,
            }
            for band, cov in summary.by_band.items()
        },
    }


def _markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gan 2026 State-Graph Ontology Oracle Uplift (Stage A)",
        "",
        "Date: 2026-06-15",
        "",
        "Stage A no-model-spend gate for the KG-grounded component generator. "
        "Validation-only over `gan2026_split_v1`; no holdout rows are read and no "
        "model calls are made.",
        "",
        "## Summary",
        "",
        f"- Ontology: `{payload['ontology_id']}`",
        f"- Rows: {summary['row_count']}",
        f"- Baseline oracle representable: {summary['baseline_representable']}/{summary['row_count']}",
        f"- Admitted (dual-validated) representable: "
        f"{summary['admitted_representable']}/{summary['row_count']}",
        f"- Projection Purist correct: {summary['projection_correct']}/{summary['row_count']}",
        f"- resolve_label Purist correct: {summary['resolve_correct']}/{summary['row_count']}",
        f"- resolve_label - projection: {summary['resolve_minus_projection']:+d} rows",
        f"- resolve gains (wrong->correct): {summary['resolve_gain_rows']}",
        f"- resolve regressions (correct->wrong): {summary['resolve_regression_rows']}",
        "",
        "## By boundary band",
        "",
        "| Band | Rows | Baseline repr. | Admitted repr. | Projection correct | "
        "resolve_label correct |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for band, cov in summary["by_band"].items():
        lines.append(
            f"| `{band}` | {cov['total']} | {cov['baseline_representable']} | "
            f"{cov['admitted_representable']} | {cov['projection_correct']} | "
            f"{cov['resolve_correct']} |"
        )
    lines.extend(
        [
            "",
            "## Gate reading",
            "",
            "Stage A passes only if `resolve_label` lifts Purist correctness over "
            "the no-correct-component residual (especially `band_unknown` and "
            "`band_weekly`) with near-zero correct->wrong regressions. A "
            "non-trivial regression count, or no net gain, stops the branch per "
            "the design-note stop rule.",
            "",
        ]
    )
    return "\n".join(lines)


def _register(row_count: int, summary: dict[str, Any], split_manifest: str) -> None:
    entries = [entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID]
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
            row_count=row_count,
            model="none",
            model_role=(
                "Stage A no-spend oracle-uplift gate over the deterministic state "
                "graph; no model calls and no holdout rows are read."
            ),
            mode="analysis-only",
            replay_status="analysis_only",
            repair_mode="state_graph_ontology_dual_validation_resolve_label_v1",
            cache_reuse_source=f"split:{split_manifest}",
            primary_metrics={
                "baseline_representable": summary["baseline_representable"],
                "admitted_representable": summary["admitted_representable"],
                "projection_correct": summary["projection_correct"],
                "resolve_correct": summary["resolve_correct"],
                "resolve_minus_projection": summary["resolve_minus_projection"],
            },
            evidence_validity=(
                "Validation-only oracle-uplift gate. Gold labels are used only for "
                "post-hoc Purist correctness and band breakdown; no holdout rows "
                "are read and no model is called."
            ),
            decision="revise",
            claim_language_notes=(
                "Stage A viability gate for the ontology + typed-edge component "
                "generator. Not a holdout-facing candidate; informs whether the "
                "validation-only ladder proceeds to Stage B."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
