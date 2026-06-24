"""Run the current-code ExECTv2 v08-shape full-200 GPT-4.1-mini no-verifier audit.

This ablation is explicitly full-200 authorized. It reuses the shared
current-code v08 producer surfaces where possible, skips the Diagnosis and
Investigations verifier lanes, runs Diagnosis reconciliation with decomposer
candidates only, and feeds Investigations directly from the structured extractor.
It does not create row-level failure ledgers for the full-200 surface.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    LensManifest,
    ProducerManifest,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter, load_letters
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from scripts.run_exectv2_v08_full200_gpt41mini_audit import (
    MANIFEST_PATH,
    MODEL,
    OUT_DIR,
    REPORT_DIR,
    RUN_DATE,
    _run_dx_decomposer,
    _run_dx_reconciler,
    _run_prescription_deterministic,
    _run_sf_adjudicator,
    _run_sf_projection,
    _run_sf_suppression,
    _run_sf_union,
    _run_structured,
)


def main() -> None:
    letters = load_letters()
    print(
        "Running current-code v08-shape GPT-4.1-mini no-verifier full-200 "
        f"over {len(letters)} letters"
    )

    structured_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_structured_gpt41mini_{RUN_DATE}.jsonl"
    )
    structured_rows = _run_structured(
        letters,
        structured_jsonl,
        structured_jsonl.with_suffix(".md"),
    )

    dx_decomposer_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_diagnosis_decomposer_gpt41mini_{RUN_DATE}.jsonl"
    )
    dx_decomposer_rows = _run_dx_decomposer(letters, structured_rows, dx_decomposer_jsonl)

    dx_no_verifier_jsonl = OUT_DIR / (
        "exectv2_v08_full200_currentcode_diagnosis_reconciler_no_verifier_"
        f"gpt41mini_{RUN_DATE}.jsonl"
    )
    _run_dx_reconciler(
        letters,
        verifier_rows=[],
        decomposer_rows=dx_decomposer_rows,
        jsonl_path=dx_no_verifier_jsonl,
    )

    sf_adjudicator_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_sf_state_adjudicator_gpt41mini_{RUN_DATE}.jsonl"
    )
    _run_sf_adjudicator(letters, structured_rows, sf_adjudicator_jsonl)

    sf_projection_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_sf_state_projection_combined_{RUN_DATE}.jsonl"
    )
    _run_sf_projection(sf_adjudicator_jsonl, sf_projection_jsonl)

    sf_suppression_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_sf_unknown_suppression_{RUN_DATE}.jsonl"
    )
    _run_sf_suppression(sf_projection_jsonl, sf_suppression_jsonl)

    sf_union_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_sf_union_arbitration_{RUN_DATE}.jsonl"
    )
    _run_sf_union(letters, sf_suppression_jsonl, sf_union_jsonl)

    inv_direct_jsonl = OUT_DIR / (
        "exectv2_v08_full200_currentcode_investigations_structured_direct_no_verifier_"
        f"gpt41mini_{RUN_DATE}.jsonl"
    )
    _write_investigations_structured_direct(letters, structured_rows, inv_direct_jsonl)

    prescription_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_{RUN_DATE}.jsonl"
    )
    _run_prescription_deterministic(letters, prescription_jsonl)

    assembly_jsonl = OUT_DIR / (
        "exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_"
        f"gpt41mini_{RUN_DATE}.jsonl"
    )
    assembly_json = assembly_jsonl.with_suffix(".json")
    assembly_md = REPORT_DIR / (
        "exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_"
        f"gpt41mini_{RUN_DATE}.md"
    )
    _run_no_verifier_assembly(
        letters,
        structured_jsonl=structured_jsonl,
        diagnosis_jsonl=dx_no_verifier_jsonl,
        sf_jsonl=sf_union_jsonl,
        prescription_jsonl=prescription_jsonl,
        investigations_jsonl=inv_direct_jsonl,
        assembly_jsonl=assembly_jsonl,
        assembly_json=assembly_json,
        assembly_md=assembly_md,
    )
    print(f"Done. Assembly JSONL: {assembly_jsonl}")
    print(f"Done. Assembly JSON: {assembly_json}")
    print(f"Done. Assembly report: {assembly_md}")


def _write_investigations_structured_direct(
    letters: list[ExectLetter],
    structured_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    letter_by_id = {letter.letter_id: letter for letter in letters}
    rows: list[dict[str, Any]] = []
    for row in structured_rows:
        letter_id = str(row["letter_id"])
        letter = letter_by_id[letter_id]
        mentions = [
            _investigations_mention(mention)
            for mention in row.get("predicted_mentions", [])
            if str(mention.get("entity")) == INVESTIGATIONS.name
        ]
        rows.append(
            {
                "letter_id": letter_id,
                "split": "full_200_authorized",
                "prompt_version": "structured_direct_no_verifier_v01",
                "pipeline_family": "exectv2_structured_direct_no_verifier_investigations",
                "model": MODEL,
                "mode": "no-call projection from structured extractor",
                "source_pipeline_family": row.get("pipeline_family", ""),
                "source_prompt_version": row.get("prompt_version", ""),
                "predicted_mentions": mentions,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(mentions),
                "n_evidence_invalid": 0,
                "raw_output": json.dumps({"mentions": mentions}, sort_keys=True),
                "call_error": None,
                "parse_errors": [],
                "gold_mentions": [
                    {
                        "entity": annotation.entity,
                        "text": annotation.text,
                        "attributes": dict(annotation.attributes),
                    }
                    for annotation in letter.annotations
                    if annotation.entity == INVESTIGATIONS.name
                ],
            }
        )
    write_jsonl(rows, jsonl_path)
    mention_count = sum(len(row["predicted_mentions"]) for row in rows)
    print(f"[investigations structured direct] rows={len(rows)} mentions={mention_count}")
    return rows


def _investigations_mention(mention: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity": INVESTIGATIONS.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
        "component_owner": "single_gpt_structured_no_verifier",
    }


def _run_no_verifier_assembly(
    letters: list[ExectLetter],
    *,
    structured_jsonl: Path,
    diagnosis_jsonl: Path,
    sf_jsonl: Path,
    prescription_jsonl: Path,
    investigations_jsonl: Path,
    assembly_jsonl: Path,
    assembly_json: Path,
    assembly_md: Path,
) -> None:
    base_manifest = load_finding_assembly_manifest(MANIFEST_PATH)
    producers = {
        "key_entities_structured_current": ProducerManifest(
            producer_id="key_entities_structured_current",
            kind="saved_jsonl",
            artifact=structured_jsonl,
            ownership_label="single_gpt_key_family_event_ledger_current_code",
            source_lane="single_gpt_structured_current_code",
            label="current-code GPT-4.1-mini structured key-family event ledger",
        ),
        "diagnosis_reconciler_v01": replace(
            base_manifest.producers["diagnosis_reconciler_v01"],
            artifact=diagnosis_jsonl,
            ownership_label="diagnosis_decomposer_only_reconciler_no_verifier",
            source_lane="diagnosis_decomposer_only_no_verifier",
            label="Diagnosis reconciler with empty verifier input and decomposer candidates only",
        ),
        "sf_union_arbitration_v08": replace(
            base_manifest.producers["sf_union_arbitration_v08"],
            artifact=sf_jsonl,
        ),
        "prescription_repair_v03": replace(
            base_manifest.producers["prescription_repair_v03"],
            artifact=prescription_jsonl,
        ),
        "investigations_arbitration_v02": replace(
            base_manifest.producers["investigations_arbitration_v02"],
            artifact=investigations_jsonl,
            ownership_label="single_gpt_structured_no_verifier",
            source_lane="structured_direct_investigations_no_verifier",
            label="Investigations direct from structured extractor; no Investigations verifier",
        ),
    }
    lenses: dict[str, LensManifest] = {
        DIAGNOSIS.name: replace(
            base_manifest.lenses[DIAGNOSIS.name],
            source_lane="diagnosis_decomposer_only_no_verifier",
            ownership_label="diagnosis_decomposer_only_reconciler_no_verifier",
        ),
        SEIZURE_FREQUENCY.name: base_manifest.lenses[SEIZURE_FREQUENCY.name],
        PRESCRIPTION.name: base_manifest.lenses[PRESCRIPTION.name],
        INVESTIGATIONS.name: replace(
            base_manifest.lenses[INVESTIGATIONS.name],
            source_lane="structured_direct_investigations_no_verifier",
            ownership_label="single_gpt_structured_no_verifier",
        ),
    }
    manifest = replace(
        base_manifest,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_currentcode_no_verifiers_gpt41mini",
        split="full_200_authorized_no_verifiers",
        row_count=len(letters),
        claim_boundary=(
            "Authorized full-200 aggregate no-verifier ablation. Diagnosis verifier and "
            "Investigations verifier lanes are omitted; Diagnosis reconciliation uses "
            "decomposer candidates only and Investigations comes directly from the "
            "structured extractor. Current-code v08-shape run, not byte-identical to "
            "archived dev140 prompt/module versions."
        ),
        producers=producers,
        lenses=lenses,
        baseline_producer="key_entities_structured_current",
        focused_comparator_artifact=None,
        promotion_decision="full-200-current-code-no-verifier-readout",
    )
    run = build_finding_assembly(manifest, gold_loader=lambda _split: letters)
    assembly_jsonl.parent.mkdir(parents=True, exist_ok=True)
    assembly_json.parent.mkdir(parents=True, exist_ok=True)
    assembly_md.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, assembly_jsonl)
    assembly_json.write_text(
        json.dumps(run.report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown = render_finding_assembly_markdown(
        run.report,
        json_path=assembly_json,
        jsonl_path=assembly_jsonl,
    ).replace(
        (
            "This replay builds a per-letter clinical finding store, applies entity-specific "
            "lenses, and renders scoring views from the same final findings. It is a "
            "structural replay over frozen artifacts; it introduces no live model calls."
        ),
        (
            "This replay builds a per-letter clinical finding store, applies entity-specific "
            "lenses, and renders scoring views from the same final findings. The final "
            "assembly stage is structural and introduces no live model calls; the "
            "Diagnosis no-verifier reconciler was generated live from decomposer-only "
            "candidates, while the other reused or no-call surfaces are named in the "
            "producer table."
        ),
    )
    assembly_md.write_text(markdown, encoding="utf-8")
    headline = run.report["score_ladder"]["headline_target"]
    overall = headline["overall"]
    print(
        "[assembly headline] "
        f"F1={overall['f1']:.4f} P={overall['precision']:.4f} "
        f"R={overall['recall']:.4f} TP={overall['tp']} FP={overall['fp']} FN={overall['fn']}"
    )
    for entity in (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name):
        row = headline["by_indicator"][entity]
        print(
            f"  {entity}: F1={row['f1']:.4f} P={row['precision']:.4f} "
            f"R={row['recall']:.4f} TP={row['tp']} FP={row['fp']} FN={row['fn']}"
        )


if __name__ == "__main__":
    main()
