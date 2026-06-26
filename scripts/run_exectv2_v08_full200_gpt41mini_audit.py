"""Run the current-code ExECTv2 v08-shape full-200 GPT-4.1-mini audit.

This is an explicitly authorized full-200 run. It avoids the normal dev-only
CLI guardrails by calling the underlying runner functions directly, writes
checkpointed lane artifacts, and emits aggregate assembly outputs. It does not
create row-level failure ledgers for the full-200 surface.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_decomposer as dx_decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_reconciler as dx_reconciler,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_verifier as dx_verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_arbitration as inv_arbitration,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as inv_verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_adjudicator as sf_adjudicator,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as sf_union,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)

MODEL = "openai/gpt-4.1-mini"
RUN_DATE = date.today().isoformat().replace("-", "")
OUT_DIR = Path("experiments")
REPORT_DIR = Path("docs/experiments/exectv2/reliability")
MANIFEST_PATH = Path(
    "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml"
)


def main() -> None:
    letters = load_letters()
    print(f"Running current-code v08-shape GPT-4.1-mini full-200 over {len(letters)} letters")

    structured_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_structured_gpt41mini_{RUN_DATE}.jsonl"
    )
    structured_md = structured_jsonl.with_suffix(".md")
    structured_rows = _run_structured(letters, structured_jsonl, structured_md)

    dx_verifier_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_diagnosis_verifier_gpt41mini_{RUN_DATE}.jsonl"
    )
    dx_verifier_rows = _run_dx_verifier(letters, structured_rows, dx_verifier_jsonl)

    dx_decomposer_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_diagnosis_decomposer_gpt41mini_{RUN_DATE}.jsonl"
    )
    dx_decomposer_rows = _run_dx_decomposer(letters, structured_rows, dx_decomposer_jsonl)

    dx_reconciler_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_diagnosis_reconciler_gpt41mini_{RUN_DATE}.jsonl"
    )
    _run_dx_reconciler(
        letters,
        dx_verifier_rows,
        dx_decomposer_rows,
        dx_reconciler_jsonl,
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

    inv_verifier_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_investigations_verifier_gpt41mini_{RUN_DATE}.jsonl"
    )
    _run_inv_verifier(letters, structured_rows, inv_verifier_jsonl)

    inv_arbitration_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_investigations_arbitration_{RUN_DATE}.jsonl"
    )
    _run_inv_arbitration(inv_verifier_jsonl, inv_arbitration_jsonl)

    prescription_jsonl = OUT_DIR / (
        f"exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_{RUN_DATE}.jsonl"
    )
    _run_prescription_deterministic(letters, prescription_jsonl)

    assembly_jsonl = OUT_DIR / (
        f"exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_{RUN_DATE}.jsonl"
    )
    assembly_json = assembly_jsonl.with_suffix(".json")
    assembly_md = REPORT_DIR / (
        f"exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_{RUN_DATE}.md"
    )
    _run_assembly(
        letters,
        structured_jsonl=structured_jsonl,
        diagnosis_jsonl=dx_reconciler_jsonl,
        sf_jsonl=sf_union_jsonl,
        prescription_jsonl=prescription_jsonl,
        investigations_jsonl=inv_arbitration_jsonl,
        assembly_jsonl=assembly_jsonl,
        assembly_json=assembly_json,
        assembly_md=assembly_md,
    )
    print(f"Done. Assembly JSONL: {assembly_jsonl}")
    print(f"Done. Assembly JSON: {assembly_json}")
    print(f"Done. Assembly report: {assembly_md}")


def _run_structured(
    letters: list[ExectLetter],
    jsonl_path: Path,
    report_path: Path,
) -> list[dict[str, Any]]:
    rows, metadata = structured.run_split(
        letters,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=6000,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
        prompt_profile="full",
    )
    write_jsonl(rows, jsonl_path)
    structured.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("structured", metadata)
    return rows


def _run_dx_verifier(
    letters: list[ExectLetter],
    draft_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    report_path = jsonl_path.with_suffix(".md")
    rows, metadata = dx_verifier.run_split(
        letters,
        draft_rows=draft_rows,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=2400,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
    )
    write_jsonl(rows, jsonl_path)
    dx_verifier.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("diagnosis verifier", metadata)
    return rows


def _run_dx_decomposer(
    letters: list[ExectLetter],
    draft_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    report_path = jsonl_path.with_suffix(".md")
    rows, metadata = dx_decomposer.run_split(
        letters,
        draft_rows=draft_rows,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=2600,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
    )
    write_jsonl(rows, jsonl_path)
    dx_decomposer.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("diagnosis decomposer", metadata)
    return rows


def _run_dx_reconciler(
    letters: list[ExectLetter],
    verifier_rows: list[dict[str, Any]],
    decomposer_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    report_path = jsonl_path.with_suffix(".md")
    rows, metadata = dx_reconciler.run_split(
        letters,
        verifier_rows=verifier_rows,
        decomposer_rows=decomposer_rows,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=2600,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
    )
    write_jsonl(rows, jsonl_path)
    dx_reconciler.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("diagnosis reconciler", metadata)
    return rows


def _run_sf_adjudicator(
    letters: list[ExectLetter],
    draft_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    report_path = jsonl_path.with_suffix(".md")
    rows, metadata = sf_adjudicator.run_split(
        letters,
        draft_rows=draft_rows,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=2600,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
    )
    write_jsonl(rows, jsonl_path)
    sf_adjudicator.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("sf adjudicator", metadata)
    return rows


def _run_sf_projection(input_jsonl: Path, jsonl_path: Path) -> None:
    metadata = sf_projection.write_rows_and_report(
        sf_projection.read_rows(input_jsonl),
        ablation="combined",
        jsonl_path=jsonl_path,
        report_path=jsonl_path.with_suffix(".md"),
    )
    _print_summary("sf projection", metadata)


def _run_sf_suppression(input_jsonl: Path, jsonl_path: Path) -> None:
    metadata = sf_suppression.write_rows_and_report(
        sf_suppression.read_rows(input_jsonl),
        jsonl_path=jsonl_path,
        report_path=jsonl_path.with_suffix(".md"),
    )
    _print_summary("sf suppression", metadata)


def _run_sf_union(letters: list[ExectLetter], current_jsonl: Path, jsonl_path: Path) -> None:
    metadata = sf_union.write_rows_and_report(
        sf_union.read_rows(current_jsonl),
        sf_union.deterministic_rows_from_letters(letters, split="full_200_authorized"),
        jsonl_path=jsonl_path,
        report_path=jsonl_path.with_suffix(".md"),
    )
    _print_summary("sf union", metadata)


def _run_inv_verifier(
    letters: list[ExectLetter],
    draft_rows: list[dict[str, Any]],
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    report_path = jsonl_path.with_suffix(".md")
    rows, metadata = inv_verifier.run_split(
        letters,
        draft_rows=draft_rows,
        split="full_200_authorized",
        model=MODEL,
        temperature=0.0,
        max_tokens=1800,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        resume=True,
    )
    write_jsonl(rows, jsonl_path)
    inv_verifier.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    _print_summary("investigations verifier", metadata)
    return rows


def _run_inv_arbitration(input_jsonl: Path, jsonl_path: Path) -> None:
    metadata = inv_arbitration.write_rows_and_report(
        inv_arbitration.read_rows(input_jsonl),
        jsonl_path=jsonl_path,
        report_path=jsonl_path.with_suffix(".md"),
    )
    _print_summary("investigations arbitration", metadata)


def _run_prescription_deterministic(letters: list[ExectLetter], jsonl_path: Path) -> None:
    predictions = run_all9_on_letters(letters)
    rows = []
    for letter, prediction in zip(letters, predictions, strict=True):
        mentions = [
            mention.model_dump()
            for mention in prediction.mentions
            if mention.entity == PRESCRIPTION.name
        ]
        for mention in mentions:
            mention["component_owner"] = (
                mention.get("component_owner")
                or "deterministic:prescription_regimen:current_code"
            )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": "full_200_authorized",
                "pipeline_family": "exectv2_deterministic_prescription_repair_v03",
                "prompt_version": "deterministic_prescription_repair_v03_current_code",
                "model": "none",
                "mode": "no-call",
                "component_owner": "deterministic_prescription_repair_v03_current_code",
                "call_error": None,
                "parse_errors": [],
                "gate_warnings": [],
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(mentions),
                "n_evidence_invalid": 0,
                "predicted_mentions": mentions,
                "raw_output": json.dumps({"mentions": mentions}, ensure_ascii=False),
                "gold_mentions": [
                    {
                        "entity": annotation.entity,
                        "text": annotation.text,
                        "attributes": dict(annotation.attributes),
                    }
                    for annotation in letter.annotations
                    if annotation.entity == PRESCRIPTION.name
                ],
            }
        )
    write_jsonl(rows, jsonl_path)
    mention_count = sum(len(row["predicted_mentions"]) for row in rows)
    print(f"[prescription deterministic] rows={len(rows)} mentions={mention_count}")


def _run_assembly(
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
        ),
    }
    lenses: dict[str, LensManifest] = {
        DIAGNOSIS.name: base_manifest.lenses[DIAGNOSIS.name],
        SEIZURE_FREQUENCY.name: base_manifest.lenses[SEIZURE_FREQUENCY.name],
        PRESCRIPTION.name: base_manifest.lenses[PRESCRIPTION.name],
        INVESTIGATIONS.name: base_manifest.lenses[INVESTIGATIONS.name],
    }
    manifest = replace(
        base_manifest,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini",
        split="full_200_authorized",
        row_count=len(letters),
        claim_boundary=(
            "Authorized full-200 aggregate audit. Current-code v08-shape run; "
            "not byte-identical to the archived dev140 prompt/module versions."
        ),
        producers=producers,
        lenses=lenses,
        baseline_producer="key_entities_structured_current",
        focused_comparator_artifact=None,
        promotion_decision="full-200-current-code-readout",
    )
    run = build_finding_assembly(
        manifest,
        gold_loader=lambda _split: letters,
    )
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
            "assembly stage is structural and introduces no live model calls; the upstream "
            "producer artifacts were generated by this authorized full-200 current-code "
            "GPT-4.1-mini runner with checkpoint/reuse semantics."
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


def _print_summary(label: str, metadata: dict[str, Any]) -> None:
    summary = metadata.get("summary", metadata)
    print(
        f"[{label}] rows={summary.get('examples', summary.get('row_count', 'n/a'))} "
        f"calls={summary.get('call_failures', 0)} "
        f"parse={summary.get('parse_failures', 0)}"
    )


if __name__ == "__main__":
    main()
