"""Compatibility wrapper for the ExECTv2 focused-lane replay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly import (
    FindingAssemblyManifest,
    LensManifest,
    ProducerManifest,
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)

PIPELINE_FAMILY = "exectv2_focused_lane_component_evidence"
CANDIDATE_NAME = "focused_lane_component_evidence_v01_dev140"
OWNERSHIP = "component_attributed_focused_lane_replay"
DEFAULT_CONTROL_ARTIFACT = Path(
    "experiments/"
    "exectv2_target_indicators_single_call_v042_live_default_quarantine_"
    "dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl"
)
DEFAULT_DIAGNOSIS_ARTIFACT = Path(
    "experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_SF_ARTIFACT = Path(
    "experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl"
)
DEFAULT_FOCUSED_COMPARATOR_ARTIFACT = Path(
    "experiments/"
    "exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_OUT_JSONL = Path(
    "experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.jsonl"
)
DEFAULT_OUT_JSON = Path(
    "experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.json"
)
DEFAULT_OUT_MD = Path(
    "docs/experiments/exectv2/key_entities/"
    "exectv2_focused_lane_component_evidence_v01_dev140_20260620.md"
)


def build_focused_lane_replay(
    *,
    split: str = "dev",
    row_count: int = 140,
    control_artifact: Path = DEFAULT_CONTROL_ARTIFACT,
    diagnosis_artifact: Path = DEFAULT_DIAGNOSIS_ARTIFACT,
    sf_artifact: Path = DEFAULT_SF_ARTIFACT,
    focused_comparator_artifact: Path | None = DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    generated_on: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the frozen component replay rows and summary report without calls."""

    manifest = _focused_lane_manifest(
        split=split,
        row_count=row_count,
        control_artifact=control_artifact,
        diagnosis_artifact=diagnosis_artifact,
        sf_artifact=sf_artifact,
        focused_comparator_artifact=focused_comparator_artifact,
    )
    run = build_finding_assembly(
        manifest,
        generated_on=generated_on,
        gold_loader=load_letters_for_split,
    )
    return run.rows, run.report


def write_focused_lane_outputs(
    *,
    out_jsonl: Path = DEFAULT_OUT_JSONL,
    out_json: Path = DEFAULT_OUT_JSON,
    out_md: Path = DEFAULT_OUT_MD,
    split: str = "dev",
    row_count: int = 140,
    control_artifact: Path = DEFAULT_CONTROL_ARTIFACT,
    diagnosis_artifact: Path = DEFAULT_DIAGNOSIS_ARTIFACT,
    sf_artifact: Path = DEFAULT_SF_ARTIFACT,
    focused_comparator_artifact: Path | None = DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
) -> dict[str, Path]:
    """Write the JSONL, JSON, and markdown focused-lane replay artifacts."""

    rows, report = build_focused_lane_replay(
        split=split,
        row_count=row_count,
        control_artifact=control_artifact,
        diagnosis_artifact=diagnosis_artifact,
        sf_artifact=sf_artifact,
        focused_comparator_artifact=focused_comparator_artifact,
    )
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(
        render_focused_lane_markdown(report, json_path=out_json, jsonl_path=out_jsonl),
        encoding="utf-8",
    )
    return {"jsonl": out_jsonl, "json": out_json, "md": out_md}


def render_focused_lane_markdown(
    report: dict[str, Any],
    *,
    json_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> str:
    """Render the focused-lane replay through the finding-assembly renderer."""

    return render_finding_assembly_markdown(
        report,
        json_path=json_path,
        jsonl_path=jsonl_path,
    )


def _focused_lane_manifest(
    *,
    split: str,
    row_count: int,
    control_artifact: Path,
    diagnosis_artifact: Path,
    sf_artifact: Path,
    focused_comparator_artifact: Path | None,
) -> FindingAssemblyManifest:
    producers = {
        "control": ProducerManifest(
            producer_id="control",
            kind="saved_jsonl",
            artifact=control_artifact,
            ownership_label="llm_first_control",
            source_lane="v0.42_control",
            label="v0.42 default-quarantine local-Qwen",
        ),
        "diagnosis": ProducerManifest(
            producer_id="diagnosis",
            kind="saved_jsonl",
            artifact=diagnosis_artifact,
            ownership_label="hybrid_diagnosis_route",
            source_lane="focused_diagnosis_reconciler_v01",
            label="focused Diagnosis reconciler v0.1",
        ),
        "sf": ProducerManifest(
            producer_id="sf",
            kind="saved_jsonl",
            artifact=sf_artifact,
            ownership_label="hybrid_sf_route",
            source_lane="focused_sf_unknown_suppression_v07",
            label="focused SF unknown suppression v0.7",
        ),
    }
    return FindingAssemblyManifest(
        candidate_id=CANDIDATE_NAME,
        pipeline_family=PIPELINE_FAMILY,
        ownership=OWNERSHIP,
        split=split,
        row_count=row_count,
        claim_boundary="dev_only_component_evidence",
        producers=producers,
        lenses={
            DIAGNOSIS.name: LensManifest(
                entity=DIAGNOSIS.name,
                producer="diagnosis",
                lens="diagnosis_hierarchy_negation_v01",
                source_lane="focused_diagnosis_reconciler_v01",
                ownership_label="hybrid_diagnosis_route",
                portability="clinical_epilepsy",
            ),
            SEIZURE_FREQUENCY.name: LensManifest(
                entity=SEIZURE_FREQUENCY.name,
                producer="sf",
                lens="sf_state_adjudication_v01",
                source_lane="focused_sf_unknown_suppression_v07",
                ownership_label="hybrid_sf_route",
                portability="seizure_frequency",
            ),
            PRESCRIPTION.name: LensManifest(
                entity=PRESCRIPTION.name,
                producer="control",
                lens="prescription_regimen_v01",
                source_lane="v0.42_control",
                ownership_label="llm_first_control",
                portability="clinical_epilepsy",
            ),
            INVESTIGATIONS.name: LensManifest(
                entity=INVESTIGATIONS.name,
                producer="control",
                lens="investigations_result_v01",
                source_lane="v0.42_control",
                ownership_label="llm_first_control",
                portability="clinical_epilepsy",
            ),
        },
        views=(
            "raw_candidate",
            "evidence_valid",
            "clinical_headline",
            "fidelity_companion",
            "benchmark_cui",
        ),
        baseline_producer="control",
        focused_comparator_artifact=focused_comparator_artifact,
        promotion_decision="promote-dev-focused-lane-architecture",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 focused-lane component-evidence no-call replay",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--row-count", type=int, default=140)
    parser.add_argument("--control-artifact", type=Path, default=DEFAULT_CONTROL_ARTIFACT)
    parser.add_argument("--diagnosis-artifact", type=Path, default=DEFAULT_DIAGNOSIS_ARTIFACT)
    parser.add_argument("--sf-artifact", type=Path, default=DEFAULT_SF_ARTIFACT)
    parser.add_argument(
        "--focused-comparator-artifact",
        type=Path,
        default=DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    )
    parser.add_argument("--out-jsonl", type=Path, default=DEFAULT_OUT_JSONL)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    outputs = write_focused_lane_outputs(
        out_jsonl=args.out_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
        row_count=args.row_count,
        control_artifact=args.control_artifact,
        diagnosis_artifact=args.diagnosis_artifact,
        sf_artifact=args.sf_artifact,
        focused_comparator_artifact=args.focused_comparator_artifact,
    )
    for name, path in outputs.items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    main()
