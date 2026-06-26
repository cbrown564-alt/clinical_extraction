"""Markdown and error-ledger writers for the LLM-first essential evaluation report."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first import (
    OWNERSHIP_HYBRID,
    OWNERSHIP_LLM_FIRST,
    OWNERSHIP_RULES_ONLY,
    align_predictions_to_gold,
    architecture_report,
    predicted_by_id_from_artifact,
)

_LLM_FIRST_ARTIFACT = Path(
    "experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl"
)
_HYBRID_ARTIFACT = Path(
    "experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl"
)


def build_evaluation(
    *,
    split: str = "dev",
    llm_first_artifact: Path = _LLM_FIRST_ARTIFACT,
    hybrid_artifact: Path = _HYBRID_ARTIFACT,
) -> dict[str, Any]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
        run_all9_on_letters,
    )

    gold = load_letters_for_split(split)

    rules_pred = run_all9_on_letters(gold)
    llm_pred = align_predictions_to_gold(
        gold, predicted_by_id_from_artifact(llm_first_artifact)
    )
    hybrid_pred = align_predictions_to_gold(
        gold, predicted_by_id_from_artifact(hybrid_artifact)
    )

    architectures = [
        architecture_report(
            name="deterministic_all9",
            ownership=OWNERSHIP_RULES_ONLY,
            gold_letters=gold,
            pred_letters=rules_pred,
        ),
        architecture_report(
            name="llm_only_all_entities (single pass)",
            ownership=OWNERSHIP_LLM_FIRST,
            gold_letters=gold,
            pred_letters=llm_pred,
            include_row_error_ledger=True,
        ),
        architecture_report(
            name="hybrid_all_entities (candidate-set + verify)",
            ownership=OWNERSHIP_HYBRID,
            gold_letters=gold,
            pred_letters=hybrid_pred,
        ),
    ]
    return {
        "plan": "docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md",
        "split": split,
        "row_count": len(gold),
        "generated_on": date.today().isoformat(),
        "no_model_calls": True,
        "sources": {
            "rules_only": "generated (run_all9_on_letters)",
            "llm_first": str(llm_first_artifact).replace("\\", "/"),
            "hybrid": str(hybrid_artifact).replace("\\", "/"),
        },
        "architectures": architectures,
    }


def _f(x: float) -> str:
    return f"{x:.3f}"


def render_markdown(report: dict[str, Any]) -> str:
    archs = report["architectures"]
    headline_entities = list(archs[0]["clinical_recovery"]["primary_entities"])
    lines: list[str] = [
        "# ExECTv2 LLM-First Essential Clinical Evaluation",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- Split: `{report['split']}` ({report['row_count']} letters)",
        f"- Plan: `{report['plan']}`",
        "- Mode: **analysis-only, no model calls** (existing artifacts replayed).",
        "",
        "Architectures and ownership (plan §Evaluation Contract):",
        "",
        "| Architecture | Ownership | Source |",
        "| --- | --- | --- |",
    ]
    for a in archs:
        source = report["sources"].get(a["ownership"], "")
        lines.append(f"| {a['name']} | `{a['ownership']}` | {source} |")

    lines += [
        "",
        "## 5. Baseline and hybrid comparator — essential clinical-recovery headline",
        "",
        "Clinical-fact recovery over the five essential families only "
        "(Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, "
        "Investigations). The primary headline is CUI-free; certainty remains "
        "a deterministic projection layer and is reported separately from the "
        "LLM-owned clinical headline.",
        "",
        "| Architecture | Ownership | Recovery F1 | Precision | Recall |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for a in archs:
        o = a["clinical_recovery"]["overall"]
        lines.append(
            f"| {a['name']} | `{a['ownership']}` | {_f(o['f1'])} "
            f"| {_f(o['precision'])} | {_f(o['recall'])} |"
        )

    lines += [
        "",
        "CUI-projected companion score (reported because the legacy "
        "SeizureFrequency state key can use CUI as seizure-type identity):",
        "",
        "| Architecture | CUI-projected essential F1 | Precision | Recall |",
        "| --- | ---: | ---: | ---: |",
    ]
    for a in archs:
        co = a["clinical_recovery"]["cui_projected_overall"]
        lines.append(
            f"| {a['name']} | {_f(co['f1'])} | {_f(co['precision'])} "
            f"| {_f(co['recall'])} |"
        )

    lines += [
        "",
        "### Per-entity clinical-recovery headline F1",
        "",
        "| Entity | " + " | ".join(a["name"].split(" ")[0] for a in archs) + " |",
        "| --- | " + " | ".join("---:" for _ in archs) + " |",
    ]
    for entity in headline_entities:
        cells = []
        for a in archs:
            h = a["clinical_recovery"]["headline_scores"][entity]
            cells.append(_f(h["f1"]))
        lines.append(f"| {entity} | " + " | ".join(cells) + " |")

    llm = next((a for a in archs if a["ownership"] == OWNERSHIP_LLM_FIRST), None)
    if llm is not None:
        o = llm["clinical_recovery"]["overall"]
        lines += [
            "",
            "## 4. LLM-first single-call report",
            "",
            f"Single all-entities pass (`{llm['name']}`), ownership `llm_first`. "
            f"Overall clinical recovery F1 **{_f(o['f1'])}** "
            f"(P {_f(o['precision'])} / R {_f(o['recall'])}).",
            "",
            "Per-entity reading (which families clear, which collapse):",
            "",
            "| Entity | Recovery F1 | Precision | Recall |",
            "| --- | ---: | ---: | ---: |",
        ]
        for entity in headline_entities:
            h = llm["clinical_recovery"]["headline_scores"][entity]
            lines.append(
                f"| {entity} | {_f(h['f1'])} | {_f(h['precision'])} | {_f(h['recall'])} |"
            )

        evidence = llm["evidence_validation"]["overall"]
        errors = llm["error_taxonomy"]["overall"]
        lines += [
            "",
            "### Evidence validation and error taxonomy",
            "",
            "Evidence policy: exact source-substring evidence is required when a "
            "prediction emits evidence text. Error categories are coarse diagnostics "
            "and can overlap.",
            "Invalid evidence counts emitted mentions without exact source-substring "
            "evidence, including missing evidence.",
            "",
            f"- evidence present: **{evidence['evidence_present_rate']:.3f}** "
            f"({evidence['evidence_present']}/{evidence['predicted_mentions']})",
            f"- exact evidence: **{evidence['exact_evidence_rate']:.3f}** "
            f"({evidence['exact_evidence']}/{evidence['predicted_mentions']})",
            f"- candidate_miss: **{errors['candidate_miss']}**",
            f"- wrong_detail_selection: **{errors['wrong_detail_selection']}**",
            f"- evidence_failure: **{errors['evidence_failure']}**",
            "",
            "Evidence-validity by essential family for the single-pass LLM artifact:",
            "",
            "| Entity | Predictions | Evidence present | Present rate | Exact evidence "
            "| Exact rate | Invalid evidence | Invalid rate |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for entity in headline_entities:
            ev = llm["evidence_validation"][entity]
            lines.append(
                f"| {entity} | {ev['predicted_mentions']} | {ev['evidence_present']} "
                f"| {ev['evidence_present_rate']:.3f} | {ev['exact_evidence']} "
                f"| {ev['exact_evidence_rate']:.3f} | {ev['invalid_evidence']} "
                f"| {ev['invalid_evidence_rate']:.3f} |"
            )

    cert = (llm or archs[0])["certainty_audit"]
    co = cert["overall"]
    lines += [
        "",
        "## 2. Certainty projection audit",
        "",
        f"{cert['note']}",
        "",
        f"Certainty-only benchmark loss is **{_f(co['certainty_only_f1_gain_if_dropped'])} F1** "
        f"({co['certainty_only_tp_gain_if_dropped']} TP) — measured on CUI-projected "
        "predictions so the residual is owned by `Certainty`/`Negation`, not missing CUI.",
        "",
        "Guideline-rule projection now uses ExECT v9 List 2 certainty triggers, "
        "default affirmed negation, and the PatientHistory febrile-negation "
        "exception. It is scored after the clinical concept is selected.",
        "",
        f"Limitation: {cert['limitations']}",
        "",
        "Gold distribution and default-projection ceiling (fraction correct if a rule "
        "assigned the dominant value):",
        "",
        "| Entity | Certainty present | distinct | default ceiling "
        "| Negation present | distinct | default ceiling |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity, e in cert["per_entity"].items():
        c = e["certainty"]
        n = e["negation"]
        lines.append(
            f"| {entity} | {c['present_rate']:.2f} | {c['distinct_values']} "
            f"| {c['default_projection_ceiling']:.2f} "
            f"| {n['present_rate']:.2f} | {n['distinct_values']} "
            f"| {n['default_projection_ceiling']:.2f} |"
        )

    lines += [
        "",
        "Guideline projection accuracy over gold rows:",
        "",
        "| Entity | Certainty coverage | Certainty accuracy "
        "| Negation coverage | Negation accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for entity, e in cert["per_entity"].items():
        gp = e["guideline_projection"]
        c = gp["Certainty"]
        n = gp["Negation"]
        lines.append(
            f"| {entity} | {c['coverage']:.2f} | {c['accuracy']:.2f} "
            f"| {n['coverage']:.2f} | {n['accuracy']:.2f} |"
        )

    cui = (llm or archs[0])["cui_audit"]
    cuo = cui["overall"]
    buckets = cui["concept_buckets"]
    proj = cui["deterministic_projection"]["__overall__"]
    lines += [
        "",
        "## 3. CUI projection audit",
        "",
        f"{cui['note']}",
        "",
        f"- Raw LLM benchmark F1 (no CUI emitted): **{_f(cuo['benchmark_f1_raw_llm'])}**",
        f"- After deterministic CUI projection: **{_f(cuo['benchmark_f1_after_cui_projection'])}** "
        f"(projection recovers +{_f(cuo['cui_projection_recovers_f1'])} F1)",
        f"- CUI-free semantic surface: **{_f(cuo['semantic_f1'])}** "
        f"(residual CUI loss after projection: {_f(cuo['residual_cui_loss_vs_semantic'])})",
        "",
        "Concept bucket ledger (over gold concepts carrying a CUI):",
        "",
        "| Bucket | Concepts | Mentions |",
        "| --- | ---: | ---: |",
    ]
    for bucket in ("one_to_one", "result_conditioned", "gold_inconsistent"):
        lines.append(
            f"| {bucket} | {buckets['bucket_concepts'].get(bucket, 0)} "
            f"| {buckets['bucket_mentions'].get(bucket, 0)} |"
        )
    missing = cui["deterministic_projection"]["__missing_mapping__"]
    lines.append(
        f"| missing_mapping | {missing['concept_count']} | {missing['mention_count']} |"
    )
    lines += [
        "",
        "Deterministic projection over gold (CUI stripped first, then re-attached — "
        "an in-sample lexicon lookup):",
        "",
        f"- coverage **{proj['coverage']:.3f}** "
        f"({proj['projected']}/{proj['gold_with_cui']})",
        f"- correctness **{proj['correctness']:.3f}** "
        f"({proj['projected_correct']}/{proj['projected']})",
        f"- missing_mapping mentions: **{proj['missing_mapping']}**",
    ]

    lines += [
        "",
        "## 6. Benchmark projection gap ledger",
        "",
        "Per architecture, the artifact projection layers from the clinical-recovery "
        "scorecard (per-item F1): phrase-only -> semantic (CUI dropped) -> benchmark "
        "(CUI kept). The phrase->semantic step is attribute/format loss; the "
        "semantic->benchmark step is CUI projection loss.",
        "",
        "| Architecture | phrase_only | semantic | benchmark |",
        "| --- | ---: | ---: | ---: |",
    ]
    for a in archs:
        ap = a["clinical_recovery"]["artifact_projection_scores"]
        lines.append(
            f"| {a['name']} | {_f(ap['phrase_only']['per_item']['f1'])} "
            f"| {_f(ap['semantic']['per_item']['f1'])} "
            f"| {_f(ap['benchmark']['per_item']['f1'])} |"
        )

    lines += [
        "",
        "## 1. Essential clinical scorer specification",
        "",
        "The essential clinical scorer is assembled in "
        "`reports/llm_first/` from the existing "
        "`clinical_recovery_scorecard.py` / `scoring.py` primitives. It aggregates "
        "only Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, and "
        "Investigations. The primary surface strips CUI from gold and predictions "
        "before scoring; Diagnosis and EpilepsyCause use concept-only recovery so "
        "`Certainty`/`Negation` do not drive the LLM-owned headline. CUI-projected "
        "and certainty-dropped scores are reported as diagnostic projection layers.",
        "",
    ]
    return "\n".join(lines)


_LEDGER_COLUMNS: tuple[str, ...] = (
    "split",
    "architecture",
    "ownership",
    "letter_id",
    "family",
    "error_type",
    "count",
    "gold_count",
    "pred_count",
    "primary_tp",
    "candidate_miss",
    "wrong_detail_selection",
    "projection_gap",
    "evidence_failure",
    "semantic_tp",
    "projected_benchmark_tp",
    "raw_benchmark_tp",
    "evidence_predicted",
    "exact_evidence",
    "gold_examples",
    "pred_examples",
    "evidence_examples",
)


def llm_first_error_ledger_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return dev-only LLM-first row-level error ledger rows."""

    if report["split"] != "dev":
        raise ValueError("Plan 11 row-level error ledgers are dev-only by split protocol")
    llm = next(a for a in report["architectures"] if a["ownership"] == OWNERSHIP_LLM_FIRST)
    return [
        {"split": report["split"], **row}
        for row in llm.get("row_error_ledger", [])
    ]


def write_error_ledger_csv(rows: list[dict[str, Any]], out_csv: Path) -> Path:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_LEDGER_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return out_csv


def render_error_ledger_markdown(rows: list[dict[str, Any]]) -> str:
    totals: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (str(row["family"]), str(row["error_type"]))
        totals[key] = totals.get(key, 0) + int(row["count"])

    lines = [
        "# ExECTv2 LLM-First Essential Family Error Ledger",
        "",
        "Canonical row-level artifact: CSV generated from existing dev artifacts; "
        "no model calls. Rows are split by `letter_id`, `family`, and `error_type`.",
        "",
        "Error types: `candidate_miss`, `wrong_detail_selection`, "
        "`projection_gap`, `evidence_failure`.",
        "",
        "## Summary",
        "",
        "| Family | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    families = sorted({str(row["family"]) for row in rows})
    for family in families:
        lines.append(
            f"| {family} | "
            f"{totals.get((family, 'candidate_miss'), 0)} | "
            f"{totals.get((family, 'wrong_detail_selection'), 0)} | "
            f"{totals.get((family, 'projection_gap'), 0)} | "
            f"{totals.get((family, 'evidence_failure'), 0)} |"
        )

    lines += [
        "",
        "## Rows",
        "",
        "| Letter | Family | Error type | Count | Gold | Pred | Primary TP "
        "| Semantic TP | Projected benchmark TP | Evidence exact/pred |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['letter_id']} | {row['family']} | {row['error_type']} "
            f"| {row['count']} | {row['gold_count']} | {row['pred_count']} "
            f"| {row['primary_tp']} | {row['semantic_tp']} "
            f"| {row['projected_benchmark_tp']} "
            f"| {row['exact_evidence']}/{row['evidence_predicted']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_error_ledger_markdown(rows: list[dict[str, Any]], out_md: Path) -> Path:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_error_ledger_markdown(rows), encoding="utf-8")
    return out_md
