"""Clinical-recovery scorecard for ExECTv2 outputs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    ENTITY_CLINICAL_RECOVERY_CLASSES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    ACTIVE_DETERMINISTIC_ENTITIES,
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.registry_sync import (
    DEFAULT_RUN_INDEX_PATH,
    register_run,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    ClinicalRecoveryPRF1,
    benchmark_config_for,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_benchmark_projection,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)

PIPELINE_FAMILY = "exectv2_clinical_recovery"
MODEL = "(model-independent)"
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
CLASS_A_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
    SEIZURE_FREQUENCY.name,
)
CLASS_B_ENTITIES: tuple[str, ...] = (
    BIRTH_HISTORY.name,
    DIAGNOSIS.name,
    EPILEPSY_CAUSE.name,
    ONSET.name,
    WHEN_DIAGNOSED.name,
)
HEADLINE_ENTITIES: tuple[str, ...] = (*CLASS_A_ENTITIES, *CLASS_B_ENTITIES)
ARTIFACT_LAYER_ENTITIES: tuple[str, ...] = (
    BIRTH_HISTORY.name,
    DIAGNOSIS.name,
    EPILEPSY_CAUSE.name,
    INVESTIGATIONS.name,
    ONSET.name,
    PATIENT_HISTORY.name,
    PRESCRIPTION.name,
    SEIZURE_FREQUENCY.name,
    WHEN_DIAGNOSED.name,
)


def build_scorecard(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
) -> dict[str, Any]:
    """Build the clinical-recovery scorecard above ExECT mention projection."""

    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    headline_scores = _headline_scores(gold_letters, pred_letters)
    projection_scores = {
        "phrase_only": score_overall(
            gold_letters,
            pred_letters,
            ARTIFACT_LAYER_ENTITIES,
            lambda _entity: PHRASE_ONLY,
        ),
        "semantic": score_overall(
            gold_letters,
            pred_letters,
            ARTIFACT_LAYER_ENTITIES,
            semantic_config_for,
        ),
        "benchmark": score_overall(
            gold_letters,
            pred_letters,
            ARTIFACT_LAYER_ENTITIES,
            benchmark_config_for,
        ),
    }
    patient_history = source_near_diagnostic(
        gold_letters,
        pred_letters,
        (PATIENT_HISTORY.name,),
        semantic_config_for,
    )
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "model": MODEL,
        "row_count": len(gold_letters),
        "entity_classes": dict(ENTITY_CLINICAL_RECOVERY_CLASSES),
        "headline_entities": list(HEADLINE_ENTITIES),
        "coverage_diagnostic_entities": [PATIENT_HISTORY.name],
        "active_entities": list(ACTIVE_DETERMINISTIC_ENTITIES),
        "overall_clinical_recovery": _recovery_to_dict(
            _aggregate_recovery(headline_scores.values())
        ),
        "headline_scores": {
            entity: _headline_score_to_dict(score)
            for entity, score in headline_scores.items()
        },
        "patient_history_coverage": {
            "source_near_overlap": _prf1_to_dict(patient_history.overall.overlap),
            "attribute_agreement_rate": round(
                patient_history.overall.attribute_agreement_rate,
                4,
            ),
            "attribute_agreement_tp": patient_history.overall.attribute_agreement_tp,
            "attribute_agreement_total": patient_history.overall.attribute_agreement_total,
        },
        "artifact_projection_scores": {
            name: _overall_to_dict(score) for name, score in projection_scores.items()
        },
    }


def write_scorecard_artifacts(
    *,
    out_json: Path,
    out_md: Path,
    split: str = "dev",
    generated_on: str | None = None,
    registry_path: Path | None = None,
    run_index_path: Path = DEFAULT_RUN_INDEX_PATH,
) -> tuple[Path, Path]:
    generated_on = generated_on or date.today().isoformat()
    gold_letters = load_letters_for_split(split)
    predictions = run_all9_on_letters(gold_letters)
    scorecard = build_scorecard(gold_letters, predictions)
    scorecard.update({"split": split, "generated_on": generated_on})

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(scorecard, json_path=out_json), encoding="utf-8")
    if registry_path is not None:
        register_run(
            _registry_entry(scorecard, json_path=out_json, md_path=out_md),
            registry_path=registry_path,
            run_index_path=run_index_path,
        )
    return out_json, out_md


def _headline_scores(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    prescription = score_prescription_components(gold_letters, pred_letters)
    investigations = score_investigations_components(gold_letters, pred_letters)
    frequency = score_frequency_state(gold_letters, pred_letters)
    scores: dict[str, Any] = {
        PRESCRIPTION.name: {
            "headline_kind": "Clinical Component Score",
            "headline": prescription.clinical_headline,
            "components": prescription,
            "projection": score_prescription_benchmark_projection(gold_letters, pred_letters),
        },
        INVESTIGATIONS.name: {
            "headline_kind": "Clinical Component Score",
            "headline": investigations.clinical_headline,
            "components": investigations,
        },
        SEIZURE_FREQUENCY.name: {
            "headline_kind": "Frequency State Recovery",
            "headline": frequency.clinical_headline,
            "components": frequency,
        },
    }
    for entity in CLASS_B_ENTITIES:
        concept = score_concept_identity(gold_letters, pred_letters, entity)
        scores[entity] = {
            "headline_kind": "Concept-Identity Headline",
            "headline": concept.concept_assertion,
            "concept_only": concept.concept_only,
            "concept_assertion": concept.concept_assertion,
        }
    return scores


def _headline_score_to_dict(score: Mapping[str, Any]) -> dict[str, Any]:
    out = {
        "headline_kind": score["headline_kind"],
        "headline": _score_to_dict(score["headline"]),
    }
    if "components" in score:
        out["components"] = _model_scores_to_dict(score["components"])
    if "projection" in score:
        out["projection"] = _model_scores_to_dict(score["projection"])
    if "concept_only" in score:
        out["concept_only"] = _score_to_dict(score["concept_only"])
        out["concept_assertion"] = _score_to_dict(score["concept_assertion"])
    return out


def _aggregate_recovery(scores: Sequence[Mapping[str, Any]]) -> ClinicalRecoveryPRF1:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        headline = score["headline"]
        recovery = _as_recovery(headline)
        precision_tp += recovery.precision_tp
        recall_tp += recovery.recall_tp
        pred_count += recovery.pred_count
        gold_count += recovery.gold_count
    return _recovery_from_counts(
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        pred_count=pred_count,
        gold_count=gold_count,
    )


def _as_recovery(score: Any) -> ClinicalRecoveryPRF1:
    if isinstance(score, ClinicalRecoveryPRF1):
        return score
    return _recovery_from_counts(
        precision_tp=score.tp,
        recall_tp=score.tp,
        pred_count=score.tp + score.fp,
        gold_count=score.tp + score.fn,
    )


def _recovery_from_counts(
    *,
    precision_tp: int,
    recall_tp: int,
    pred_count: int,
    gold_count: int,
) -> ClinicalRecoveryPRF1:
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return ClinicalRecoveryPRF1(
        tp=recall_tp,
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        fp=max(0, pred_count - precision_tp),
        fn=max(0, gold_count - recall_tp),
        pred_count=pred_count,
        gold_count=gold_count,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def _model_scores_to_dict(model: Any) -> dict[str, Any]:
    return {
        name: _score_to_dict(getattr(model, name))
        for name in type(model).model_fields
    }


def _score_to_dict(score: Any) -> dict[str, Any]:
    if isinstance(score, ClinicalRecoveryPRF1):
        return _recovery_to_dict(score)
    return _prf1_to_dict(score)


def _recovery_to_dict(score: ClinicalRecoveryPRF1) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "precision_tp": score.precision_tp,
        "recall_tp": score.recall_tp,
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": score.pred_count,
        "gold_count": score.gold_count,
    }


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": score.tp + score.fp,
        "gold_count": score.tp + score.fn,
    }


def _overall_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
        "per_entity": {
            entity: {
                "per_item": _prf1_to_dict(entity_score.per_item),
                "per_letter": _prf1_to_dict(entity_score.per_letter),
            }
            for entity, entity_score in score.per_entity.items()
        },
    }


def _render_markdown(scorecard: dict[str, Any], *, json_path: Path) -> str:
    overall = scorecard["overall_clinical_recovery"]
    lines = [
        "# ExECTv2 Clinical-Recovery Scorecard",
        "",
        f"- Generated: `{scorecard['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Split: `{scorecard['split']}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
        f"- Overall clinical-recovery F1: {overall['f1']:.4f}",
        f"- Overall clinical-recovery recall: {overall['recall']:.4f}",
        f"- Overall clinical-recovery precision: {overall['precision']:.4f}",
        "",
        "## Entity Headlines",
        "",
        "| Entity | Headline kind | F1 | Precision | Recall | TP | FP | FN |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity in scorecard["headline_entities"]:
        entry = scorecard["headline_scores"][entity]
        headline = entry["headline"]
        lines.append(
            f"| {entity} | {entry['headline_kind']} | {headline['f1']:.4f} "
            f"| {headline['precision']:.4f} | {headline['recall']:.4f} "
            f"| {headline['tp']} | {headline['fp']} | {headline['fn']} |"
        )
    coverage = scorecard["patient_history_coverage"]
    overlap = coverage["source_near_overlap"]
    lines.extend(
        [
            "",
            "## Coverage Diagnostic",
            "",
            "| Entity | Source-near F1 | Attribute agreement | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {PATIENT_HISTORY.name} | {overlap['f1']:.4f} "
                f"| {coverage['attribute_agreement_rate']:.4f} "
                f"| {overlap['tp']} | {overlap['fp']} | {overlap['fn']} |"
            ),
            "",
            "## Artifact Projection Layer",
            "",
            "| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for layer in ("phrase_only", "semantic", "benchmark"):
        per_item = scorecard["artifact_projection_scores"][layer]["per_item"]
        per_letter = scorecard["artifact_projection_scores"][layer]["per_letter"]
        lines.append(
            f"| {layer} | {per_item['f1']:.4f} | {per_letter['f1']:.4f} "
            f"| {per_item['tp']} | {per_item['fp']} | {per_item['fn']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _registry_entry(
    scorecard: dict[str, Any],
    *,
    json_path: Path,
    md_path: Path,
) -> RunRegistryEntry:
    date_slug = scorecard["generated_on"].replace("-", "")
    overall = scorecard["overall_clinical_recovery"]
    metrics: dict[str, Any] = {
        "clinical_recovery_f1": overall["f1"],
        "clinical_recovery_precision": overall["precision"],
        "clinical_recovery_recall": overall["recall"],
        "headline_entities": list(scorecard["headline_entities"]),
        "coverage_diagnostic_entities": list(scorecard["coverage_diagnostic_entities"]),
    }
    for entity in scorecard["headline_entities"]:
        metrics[f"{entity.lower()}_headline_f1"] = scorecard["headline_scores"][entity][
            "headline"
        ]["f1"]
    return RunRegistryEntry(
        run_id=f"exectv2_clinical_recovery_{scorecard['split']}_{date_slug}",
        artifact_paths=(
            str(json_path).replace("\\", "/"),
            str(md_path).replace("\\", "/"),
        ),
        date=scorecard["generated_on"],
        pipeline_family=PIPELINE_FAMILY,
        split=scorecard["split"],
        row_count=scorecard["row_count"],
        model=MODEL,
        model_role=(
            "ExECTv2 clinical-recovery scorecard; per-entity clinical-fact recovery "
            "headline above the demoted ExECT mention-phrase and CUI projection layer. "
            "Deterministic scorers, no model calls."
        ),
        mode="deterministic",
        replay_status="analysis_only",
        decision="clinical_recovery_reporting",
        primary_metrics=metrics,
        evidence_validity=(
            "Deterministic scorers over existing all-9 prediction artifacts; no model "
            "calls. Headline recovery scored on normalized clinical concepts."
        ),
        claim_language_notes=(
            "Clinical-fact recovery scorecard; ExECT mention phrase and CUI "
            "projection remain separately reported artifact layers."
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 clinical-recovery scorecard",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/exectv2_clinical_recovery_dev_20260618.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/exectv2_clinical_recovery_dev_20260618.md"),
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    parser.add_argument("--no-register", action="store_true")
    args = parser.parse_args()

    json_path, md_path = write_scorecard_artifacts(
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
        registry_path=None if args.no_register else args.registry,
        run_index_path=args.run_index,
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
