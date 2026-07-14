"""Generic runner for a YAML/JSON finding-assembly manifest.

Loads a manifest, builds the no-call finding assembly over its frozen producer
artifacts, writes JSONL/JSON/markdown, and prints the ``headline_target`` score
view (overall plus per-family) for quick comparison against prior versions.

Usage::

    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.\
        run_finding_assembly \
        --manifest configs/exectv2/finding_assembly/\
exectv2_holistic_finding_assembly_v08_p7_dev140.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    load_finding_assembly_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    write_artifact_bundle,
)

_ENTITIES = (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name)


def _default_out(candidate_id: str, suffix: str) -> Path:
    return Path("experiments") / f"{candidate_id}_20260621.{suffix}"


def _print_surface(name: str, surface: dict) -> None:
    overall = surface["overall"]
    by = surface["by_indicator"]
    print(
        f"\n[{name}] overall F1={overall['f1']:.4f} "
        f"P={overall['precision']:.4f} R={overall['recall']:.4f} "
        f"(TP={overall['tp']} FP={overall['fp']} FN={overall['fn']})",
        flush=True,
    )
    for entity in _ENTITIES:
        row = by[entity]
        print(
            f"  {entity:<17} F1={row['f1']:.4f} P={row['precision']:.4f} "
            f"R={row['recall']:.4f} (TP={row['tp']} FP={row['fp']} FN={row['fn']})",
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a finding-assembly manifest")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--diagnosis-resolution-candidate",
        action="store_true",
        help="Opt into the unpromoted dev140 Diagnosis resolution rules.",
    )
    args = parser.parse_args()

    manifest = load_finding_assembly_manifest(args.manifest)
    out_jsonl = args.out_jsonl or _default_out(manifest.candidate_id, "jsonl")
    out_json = args.out_json or _default_out(manifest.candidate_id, "json")
    out_md = args.out_md or _default_out(manifest.candidate_id, "md")

    run = build_finding_assembly(
        manifest,
        diagnosis_resolution_candidate=args.diagnosis_resolution_candidate,
    )
    report = run.report

    write_artifact_bundle(
        {
            out_jsonl: "\n".join(json.dumps(row, sort_keys=True) for row in run.rows) + "\n",
            out_json: json.dumps(report, indent=2, sort_keys=True) + "\n",
            out_md: render_finding_assembly_markdown(
                report, json_path=out_json, jsonl_path=out_jsonl
            ),
        }
    )

    ladder = report["score_ladder"]
    print(f"Candidate: {manifest.candidate_id}  rows={report['row_count']}", flush=True)
    print(f"Gate decision: {report['gate_decision']['decision']}", flush=True)
    _print_surface("headline_target", ladder["headline_target"])
    _print_surface("evidence_valid_score", ladder["evidence_valid_score"])
    benchmark = ladder["benchmark"]
    print(
        f"\nBenchmark raw={benchmark['raw']:.4f} "
        f"after_cui_projection={benchmark['after_cui_projection']:.4f}",
        flush=True,
    )
    print(f"\nOutputs: {out_jsonl}  {out_json}  {out_md}", flush=True)


if __name__ == "__main__":
    main()
