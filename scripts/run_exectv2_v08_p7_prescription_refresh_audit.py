"""Measure the P7 Rx weight-context fix's effect through the full v08 hybrid
assembly, on both dev140 and full-200.

P7 (docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md,
hypothesis rx_weight_context_whole_evidence_producer_bug_2026-07-02) scoped
deterministic/all_entities/prescription.py's weight-based-context search to
each dose's own clause instead of the whole evidence string. That producer
feeds the v08 hybrid pipeline's Prescription lane (prescription_repair_v03),
so its cited headline numbers could move -- deliberately left unmeasured in
the original P7 pass pending this explicit follow-up.

Zero new LLM calls: the Prescription producer is regenerated deterministically
(the fixed code, over the same static gold-letter text); every other producer
(structured/diagnosis/SF/investigations) is reused UNCHANGED from its existing
cached artifact. Never overwrites an archived artifact in place -- writes new
dated files and swaps only the prescription_repair_v03 producer via
dataclasses.replace, so the archived 20260621/20260624 files (and the five
other manifests that share the dev140 one) are untouched.

For each split, builds BOTH a baseline assembly (unmodified manifest, original
Prescription artifact) and a treatment assembly (only Prescription swapped)
through the SAME current-code scorer today, so the reported delta isolates
P7's effect and is not confounded by the scorer having changed since whatever
date the historically-cited number was computed.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
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
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)

RUN_DATE = date.today().isoformat().replace("-", "")
OUT_DIR = Path("experiments")
REPORT_DIR = Path("docs/experiments/exectv2/reliability")
DEV_MANIFEST_PATH = Path(
    "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml"
)
FULL200_PRESCRIPTION_BASELINE = OUT_DIR / (
    "exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_20260624.jsonl"
)
FULL200_ASSEMBLY_BASELINE = OUT_DIR / (
    "exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl"
)


def main() -> None:
    print("=== dev140 ===")
    dev_letters = load_letters_for_split("dev")
    dev_prescription_jsonl = OUT_DIR / (
        f"exectv2_deterministic_prescription_repair_v03_dev140_p7fix_{RUN_DATE}.jsonl"
    )
    _run_prescription_deterministic(dev_letters, dev_prescription_jsonl, split="dev")

    dev_base_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
    print("\n-- dev140 baseline (unmodified manifest, archived Prescription artifact) --")
    dev_baseline = _run_assembly(
        dev_letters,
        base_manifest=dev_base_manifest,
        prescription_jsonl=None,
        candidate_id="exectv2_holistic_finding_assembly_v08_dev140_p7_baseline",
        split="dev",
        claim_boundary=(
            "P7 follow-up baseline: unmodified v08 dev140 manifest re-run through "
            "today's current-code scorer for an apples-to-apples P7 delta (not "
            "necessarily identical to the historically-cited 0.9155 figure, which "
            "predates several since-landed scorer fixes)."
        ),
        assembly_stem=f"exectv2_holistic_finding_assembly_v08_dev140_p7_baseline_{RUN_DATE}",
    )

    print("\n-- dev140 treatment (P7-fixed Prescription artifact only) --")
    dev_treatment = _run_assembly(
        dev_letters,
        base_manifest=dev_base_manifest,
        prescription_jsonl=dev_prescription_jsonl,
        candidate_id="exectv2_holistic_finding_assembly_v08_dev140_p7_treatment",
        split="dev",
        claim_boundary=(
            "P7 follow-up treatment: v08 dev140 manifest with ONLY "
            "prescription_repair_v03 swapped for a P7-fixed regeneration "
            "(deterministic/all_entities/prescription.py weight-context clause "
            "scope). Every other producer is the unchanged archived artifact -- "
            "zero new LLM calls."
        ),
        assembly_stem=f"exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_{RUN_DATE}",
    )

    print("\n=== full-200 ===")
    full_letters = load_letters()
    full_prescription_jsonl = OUT_DIR / (
        f"exectv2_deterministic_prescription_repair_v03_full200_p7fix_{RUN_DATE}.jsonl"
    )
    _run_prescription_deterministic(
        full_letters, full_prescription_jsonl, split="full_200_authorized"
    )

    full_base_manifest = _full200_base_manifest(full_letters)
    print("\n-- full-200 baseline (unmodified 20260624 currentcode manifest) --")
    full_baseline = _run_assembly(
        full_letters,
        base_manifest=full_base_manifest,
        prescription_jsonl=None,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_p7_baseline",
        split="full_200_authorized",
        claim_boundary=(
            "P7 follow-up baseline: the archived 2026-06-24 full-200 currentcode "
            "manifest re-run through today's current-code scorer, zero new LLM "
            "calls (reuses every 20260624 producer artifact unchanged)."
        ),
        assembly_stem=f"exectv2_holistic_finding_assembly_v08_full200_p7_baseline_{RUN_DATE}",
    )

    print("\n-- full-200 treatment (P7-fixed Prescription artifact only) --")
    full_treatment = _run_assembly(
        full_letters,
        base_manifest=full_base_manifest,
        prescription_jsonl=full_prescription_jsonl,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_p7_treatment",
        split="full_200_authorized",
        claim_boundary=(
            "P7 follow-up treatment: the archived 2026-06-24 full-200 currentcode "
            "manifest with ONLY prescription_repair_v03 swapped for a P7-fixed "
            "regeneration. Every other producer is the unchanged 20260624 "
            "artifact -- zero new LLM calls."
        ),
        assembly_stem=f"exectv2_holistic_finding_assembly_v08_full200_p7_treatment_{RUN_DATE}",
    )

    print("\n\n=== SUMMARY ===")
    _print_delta("dev140", dev_baseline, dev_treatment)
    _print_delta("full-200", full_baseline, full_treatment)


def _run_prescription_deterministic(
    letters: list[ExectLetter], jsonl_path: Path, *, split: str
) -> None:
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
                or "deterministic:prescription_regimen:current_code_p7fix"
            )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": "exectv2_deterministic_prescription_repair_v03",
                "prompt_version": "deterministic_prescription_repair_v03_current_code_p7fix",
                "model": "none",
                "mode": "no-call",
                "component_owner": "deterministic_prescription_repair_v03_current_code_p7fix",
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
    print(
        f"[prescription deterministic, P7-fixed, {split}] rows={len(rows)} mentions={mention_count}"
    )


def _full200_base_manifest(letters: list[ExectLetter]):
    dev_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
    producers = {
        "key_entities_structured_current": ProducerManifest(
            producer_id="key_entities_structured_current",
            kind="saved_jsonl",
            artifact=OUT_DIR
            / "exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl",
            ownership_label="single_gpt_key_family_event_ledger_current_code",
            source_lane="single_gpt_structured_current_code",
            label="current-code GPT-4.1-mini structured key-family event ledger",
        ),
        "diagnosis_reconciler_v01": replace(
            dev_manifest.producers["diagnosis_reconciler_v01"],
            artifact=OUT_DIR
            / "exectv2_v08_full200_currentcode_diagnosis_reconciler_gpt41mini_20260624.jsonl",
        ),
        "sf_union_arbitration_v08": replace(
            dev_manifest.producers["sf_union_arbitration_v08"],
            artifact=OUT_DIR
            / "exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl",
        ),
        "prescription_repair_v03": replace(
            dev_manifest.producers["prescription_repair_v03"],
            artifact=FULL200_PRESCRIPTION_BASELINE,
        ),
        "investigations_arbitration_v02": replace(
            dev_manifest.producers["investigations_arbitration_v02"],
            artifact=OUT_DIR
            / "exectv2_v08_full200_currentcode_investigations_arbitration_20260624.jsonl",
        ),
    }
    lenses = {
        DIAGNOSIS.name: dev_manifest.lenses[DIAGNOSIS.name],
        SEIZURE_FREQUENCY.name: dev_manifest.lenses[SEIZURE_FREQUENCY.name],
        PRESCRIPTION.name: dev_manifest.lenses[PRESCRIPTION.name],
        INVESTIGATIONS.name: dev_manifest.lenses[INVESTIGATIONS.name],
    }
    return replace(
        dev_manifest,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini",
        split="full_200_authorized",
        row_count=len(letters),
        producers=producers,
        lenses=lenses,
        baseline_producer="key_entities_structured_current",
        focused_comparator_artifact=None,
        promotion_decision="full-200-current-code-readout",
    )


def _run_assembly(
    letters: list[ExectLetter],
    *,
    base_manifest,
    prescription_jsonl: Path | None,
    candidate_id: str,
    split: str,
    claim_boundary: str,
    assembly_stem: str,
) -> dict[str, Any]:
    producers = dict(base_manifest.producers)
    if prescription_jsonl is not None:
        producers["prescription_repair_v03"] = replace(
            base_manifest.producers["prescription_repair_v03"],
            artifact=prescription_jsonl,
        )
    manifest = replace(
        base_manifest,
        candidate_id=candidate_id,
        split=split,
        row_count=len(letters),
        claim_boundary=claim_boundary,
        producers=producers,
    )
    run = build_finding_assembly(manifest, gold_loader=lambda _split: letters)

    assembly_jsonl = OUT_DIR / f"{assembly_stem}.jsonl"
    assembly_json = assembly_jsonl.with_suffix(".json")
    assembly_md = REPORT_DIR / f"{assembly_stem}.md"
    assembly_jsonl.parent.mkdir(parents=True, exist_ok=True)
    assembly_md.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, assembly_jsonl)
    assembly_json.write_text(
        json.dumps(run.report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown = render_finding_assembly_markdown(
        run.report, json_path=assembly_json, jsonl_path=assembly_jsonl
    )
    assembly_md.write_text(markdown, encoding="utf-8")

    headline = run.report["score_ladder"]["headline_target"]
    overall = headline["overall"]
    print(
        f"[{candidate_id}] "
        f"F1={overall['f1']:.4f} P={overall['precision']:.4f} "
        f"R={overall['recall']:.4f} TP={overall['tp']} FP={overall['fp']} FN={overall['fn']}"
    )
    for entity in (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name):
        row = headline["by_indicator"][entity]
        print(
            f"  {entity}: F1={row['f1']:.4f} P={row['precision']:.4f} "
            f"R={row['recall']:.4f} TP={row['tp']} FP={row['fp']} FN={row['fn']}"
        )
    return headline


def _print_delta(label: str, baseline: dict[str, Any], treatment: dict[str, Any]) -> None:
    b = baseline["overall"]
    t = treatment["overall"]
    print(f"\n{label}: overall F1 {b['f1']:.4f} -> {t['f1']:.4f} (delta {t['f1'] - b['f1']:+.4f})")
    for entity in (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name):
        bi = baseline["by_indicator"][entity]
        ti = treatment["by_indicator"][entity]
        print(
            f"  {entity}: F1 {bi['f1']:.4f} -> {ti['f1']:.4f} "
            f"(delta {ti['f1'] - bi['f1']:+.4f}, tp {bi['tp']}->{ti['tp']}, "
            f"fp {bi['fp']}->{ti['fp']}, fn {bi['fn']}->{ti['fn']})"
        )


if __name__ == "__main__":
    main()
