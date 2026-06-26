"""Scorecard for the ExECTv2 deterministic all-entity baseline."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
    PATIENT_HISTORY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.validate import (
    validate_letter,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.scorecard_core import (
    overall_to_dict,
    prf1_to_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_overall,
    score_prescription_benchmark_projection,
    score_prescription_components,
    semantic_config_for,
)
from clinical_extraction.core.registry import (
    RunRegistryEntry,
)

DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
PIPELINE_FAMILY = "exectv2_deterministic_all9"
MODEL = "(model-independent)"
ALL_ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)
PRESCRIPTION_CLINICAL_HEADLINE = "clinical_headline"
PRESCRIPTION_DIAGNOSTIC_ORDER: tuple[str, ...] = (
    "name",
    "dose",
    "frequency",
    "source_stated_frequency",
    "guideline_defaulted_frequency",
    "complete",
    "ordinary_complete",
    "rescue_regimen",
    "future_medication",
    "weight_based_dosing",
)
PRESCRIPTION_BENCHMARK_PROJECTION_ORDER: tuple[str, ...] = (
    "phrase_scope",
    "semantic_without_cui",
    "benchmark_with_cui",
    "clinical_medication_identity",
    "drugname_cui_projection",
    "source_stated_frequency",
    "guideline_defaulted_frequency",
)


def build_scorecard(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
) -> dict[str, Any]:
    """Summarize scores and reliability gates for deterministic all-entity output."""

    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    scores = {
        "phrase_only": score_overall(
            gold_letters,
            pred_letters,
            ALL_ENTITY_NAMES,
            lambda _entity: PHRASE_ONLY,
        ),
        "semantic": score_overall(
            gold_letters,
            pred_letters,
            ALL_ENTITY_NAMES,
            semantic_config_for,
        ),
        "benchmark": score_overall(
            gold_letters,
            pred_letters,
            ALL_ENTITY_NAMES,
            benchmark_config_for,
        ),
    }
    prescription_components = score_prescription_components(gold_letters, pred_letters)
    prescription_projection = score_prescription_benchmark_projection(gold_letters, pred_letters)
    validation = _validation_summary(gold_letters, predictions)
    mentions_total = sum(len(prediction.mentions) for prediction in predictions)
    mentions_with_cui = sum(
        1
        for prediction in predictions
        for mention in prediction.mentions
        if "CUI" in mention.attributes
    )
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "model": MODEL,
        "row_count": len(gold_letters),
        "active_entities": list(ACTIVE_DETERMINISTIC_ENTITIES),
        "scored_entities": list(ALL_ENTITY_NAMES),
        "mentions_total": mentions_total,
        "mentions_with_cui": mentions_with_cui,
        "cui_attachment_rate": round(mentions_with_cui / mentions_total, 4)
        if mentions_total
        else 1.0,
        "call_failures": 0,
        "parse_failures": 0,
        "routing_count": 0,
        "schema_repairs": 0,
        "validation": validation,
        "scores": {name: overall_to_dict(score) for name, score in scores.items()},
        "prescription_component_scores": _prescription_components_to_dict(
            prescription_components
        ),
        "prescription_benchmark_projection_scores": _prescription_projection_to_dict(
            prescription_projection
        ),
        "patient_history_error_ledger": _patient_history_error_ledger(
            gold_letters,
            pred_letters,
            scores,
        ),
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
    """Run, write JSON/Markdown artifacts, and optionally register the run."""

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


def _validation_summary(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
) -> dict[str, Any]:
    error_count = 0
    warning_count = 0
    evidence_not_substring = 0
    for gold, prediction in zip(gold_letters, predictions, strict=True):
        result = validate_letter(prediction, source_text=gold.note_text)
        for issue in result.issues:
            if issue.severity == "error":
                error_count += 1
            else:
                warning_count += 1
            if issue.code == "evidence_not_substring":
                evidence_not_substring += 1
    mentions_total = sum(len(prediction.mentions) for prediction in predictions)
    return {
        "schema_error_count": error_count,
        "warning_count": warning_count,
        "evidence_not_substring_count": evidence_not_substring,
        "evidence_validity_rate": round(
            (mentions_total - evidence_not_substring) / mentions_total,
            4,
        )
        if mentions_total
        else 1.0,
    }


def _prescription_components_to_dict(score: Any) -> dict[str, Any]:
    names = (PRESCRIPTION_CLINICAL_HEADLINE, *PRESCRIPTION_DIAGNOSTIC_ORDER)
    return {name: prf1_to_dict(getattr(score, name)) for name in names}


def _prescription_projection_to_dict(score: Any) -> dict[str, Any]:
    return {
        name: prf1_to_dict(getattr(score, name))
        for name in PRESCRIPTION_BENCHMARK_PROJECTION_ORDER
    }


def _patient_history_error_ledger(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    scores: dict[str, Any],
) -> dict[str, Any]:
    phrase = scores["phrase_only"].per_entity[PATIENT_HISTORY.name].per_item
    semantic = scores["semantic"].per_entity[PATIENT_HISTORY.name].per_item
    benchmark = scores["benchmark"].per_entity[PATIENT_HISTORY.name].per_item
    gold_mentions = [
        annotation
        for letter in gold_letters
        for annotation in letter.entities(PATIENT_HISTORY.name)
    ]
    pred_mentions = [
        annotation
        for letter in pred_letters
        for annotation in letter.entities(PATIENT_HISTORY.name)
    ]
    temporal_attrs = {
        "Age",
        "AgeLower",
        "AgeUpper",
        "AgeUnit",
        "DayDate",
        "MonthDate",
        "YearDate",
        "NumberOfTimePeriods",
        "TimePeriod",
        "PointInTime",
    }
    return {
        "gold_mentions": len(gold_mentions),
        "predicted_mentions": len(pred_mentions),
        "predicted_with_cui": sum(1 for mention in pred_mentions if "CUI" in mention.attributes),
        "predicted_with_temporal_attributes": sum(
            1
            for mention in pred_mentions
            if temporal_attrs.intersection(mention.attributes)
        ),
        "predicted_negated": sum(
            1
            for mention in pred_mentions
            if mention.attributes.get("Negation") == "Negated"
        ),
        "gap_families": {
            "phrase_scope_or_missing": {
                "fn": phrase.fn,
                "fp": phrase.fp,
                "note": "Phrase-only misses and over-emissions before attributes or CUI.",
            },
            "attribute_bundle": {
                "additional_fn_vs_phrase": max(0, semantic.fn - phrase.fn),
                "additional_fp_vs_phrase": max(0, semantic.fp - phrase.fp),
                "note": "Temporal, negation, and certainty mismatches after phrase match.",
            },
            "cui_projection": {
                "additional_fn_vs_semantic": max(0, benchmark.fn - semantic.fn),
                "additional_fp_vs_semantic": max(0, benchmark.fp - semantic.fp),
                "note": "Benchmark-format gap from CUI/CUIPhrase projection.",
            },
        },
    }


def _render_markdown(scorecard: dict[str, Any], *, json_path: Path) -> str:
    validation = scorecard["validation"]
    lines = [
        "# ExECTv2 Deterministic All-9 Baseline Scorecard",
        "",
        f"- Generated: `{scorecard['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Split: `{scorecard['split']}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
        f"- Active deterministic entities: {', '.join(scorecard['active_entities'])}",
        f"- Scored entities: {', '.join(scorecard['scored_entities'])}",
        "",
        "## Reliability",
        "",
        f"- Call failures: {scorecard['call_failures']}",
        f"- Parse failures: {scorecard['parse_failures']}",
        f"- Schema errors: {validation['schema_error_count']}",
        f"- Schema repairs: {scorecard['schema_repairs']}",
        f"- Evidence-not-substring warnings: {validation['evidence_not_substring_count']}",
        f"- Evidence validity rate: {validation['evidence_validity_rate']:.4f}",
        f"- Mentions emitted: {scorecard['mentions_total']}",
        f"- CUI attachment: {scorecard['mentions_with_cui']}/"
        f"{scorecard['mentions_total']} ({scorecard['cui_attachment_rate']:.4f})",
        f"- Routed/abstained mentions: {scorecard['routing_count']}",
        "",
        "## Overall Scores",
        "",
        "| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for layer in ("phrase_only", "semantic", "benchmark"):
        per_item = scorecard["scores"][layer]["per_item"]
        per_letter = scorecard["scores"][layer]["per_letter"]
        lines.append(
            f"| {layer} | {per_item['f1']:.4f} | {per_letter['f1']:.4f} "
            f"| {per_item['tp']} | {per_item['fp']} | {per_item['fn']} |"
        )

    lines.extend(["", "## Per-Entity Benchmark F1", ""])
    lines.append("| Entity | Item F1 | Letter F1 | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for entity in scorecard["scored_entities"]:
        entry = scorecard["scores"]["benchmark"]["per_entity"][entity]
        per_item = entry["per_item"]
        per_letter = entry["per_letter"]
        lines.append(
            f"| {entity} | {per_item['f1']:.4f} | {per_letter['f1']:.4f} "
            f"| {per_item['tp']} | {per_item['fp']} | {per_item['fn']} |"
        )

    lines.extend(["", "## Prescription Clinical Headline", ""])
    lines.append("| Score | Item F1 | Precision | Recall | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    entry = scorecard["prescription_component_scores"][PRESCRIPTION_CLINICAL_HEADLINE]
    lines.append(
        f"| clinical_headline | {entry['f1']:.4f} | {entry['precision']:.4f} "
        f"| {entry['recall']:.4f} | {entry['tp']} | {entry['fp']} | {entry['fn']} |"
    )

    lines.extend(["", "## Prescription Diagnostics", ""])
    lines.append("| Diagnostic | Item F1 | Precision | Recall | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for component in PRESCRIPTION_DIAGNOSTIC_ORDER:
        entry = scorecard["prescription_component_scores"][component]
        lines.append(
            f"| {component} | {entry['f1']:.4f} | {entry['precision']:.4f} "
            f"| {entry['recall']:.4f} | {entry['tp']} | {entry['fp']} | {entry['fn']} |"
        )

    lines.extend(["", "## Prescription Benchmark Projection", ""])
    lines.append("| Projection layer | Item F1 | Precision | Recall | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for layer in PRESCRIPTION_BENCHMARK_PROJECTION_ORDER:
        entry = scorecard["prescription_benchmark_projection_scores"][layer]
        lines.append(
            f"| {layer} | {entry['f1']:.4f} | {entry['precision']:.4f} "
            f"| {entry['recall']:.4f} | {entry['tp']} | {entry['fp']} | {entry['fn']} |"
        )

    patient_history = scorecard["patient_history_error_ledger"]
    lines.extend(["", "## PatientHistory Error Ledger", ""])
    lines.extend(
        [
            f"- Gold mentions: {patient_history['gold_mentions']}",
            f"- Predicted mentions: {patient_history['predicted_mentions']}",
            f"- Predicted with CUI: {patient_history['predicted_with_cui']}",
            (
                "- Predicted with temporal attributes: "
                f"{patient_history['predicted_with_temporal_attributes']}"
            ),
            f"- Predicted negated: {patient_history['predicted_negated']}",
            "",
            "| Gap family | FN / additional FN | FP / additional FP | Note |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    gap_families = patient_history["gap_families"]
    phrase_gap = gap_families["phrase_scope_or_missing"]
    lines.append(
        f"| phrase_scope_or_missing | {phrase_gap['fn']} | {phrase_gap['fp']} "
        f"| {phrase_gap['note']} |"
    )
    attribute_gap = gap_families["attribute_bundle"]
    lines.append(
        f"| attribute_bundle | {attribute_gap['additional_fn_vs_phrase']} "
        f"| {attribute_gap['additional_fp_vs_phrase']} | {attribute_gap['note']} |"
    )
    cui_gap = gap_families["cui_projection"]
    lines.append(
        f"| cui_projection | {cui_gap['additional_fn_vs_semantic']} "
        f"| {cui_gap['additional_fp_vs_semantic']} | {cui_gap['note']} |"
    )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            (
                "This is the first rules_only all-entity substrate: it scores all "
                "nine entities. Prescription, Investigations, Diagnosis, "
                "Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, and "
                "SeizureFrequency now sit beside a conservative PatientHistory "
                "substrate with explicit phrase, attribute, and CUI gap families."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _registry_entry(
    scorecard: dict[str, Any],
    *,
    json_path: Path,
    md_path: Path,
) -> RunRegistryEntry:
    date_slug = scorecard["generated_on"].replace("-", "")
    return RunRegistryEntry(
        run_id=f"exectv2_deterministic_all9_{scorecard['split']}_{date_slug}",
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
            "ExECTv2 deterministic all-9 baseline; active rules for Prescription, "
            "Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, "
            "EpilepsyCause, PatientHistory, and SeizureFrequency."
        ),
        mode="deterministic",
        replay_status="analysis_only",
        decision="inform_architecture_loop",
        primary_metrics=_primary_metrics(scorecard),
        evidence_validity="exact source substring validation summarized in scorecard.",
        claim_language_notes=(
            "First GPT-first rules_only all-9 substrate. Not freeze-ready; incomplete "
            "entity coverage remains explicit in per-entity scores."
        ),
    )


def _primary_metrics(scorecard: dict[str, Any]) -> dict[str, Any]:
    """Flat registry-summary metrics.

    Nested component/ledger breakdowns live in the scorecard JSON artifact; the
    registry keeps only scalar (and flat-list) summary metrics so the row stays
    loadable by the typed run registry.
    """

    validation = scorecard["validation"]
    metrics: dict[str, Any] = {
        "prompt_version": "n/a (deterministic rules)",
        "call_failures": scorecard["call_failures"],
        "parse_failures": scorecard["parse_failures"],
        "schema_error_count": validation["schema_error_count"],
        "schema_repairs": scorecard["schema_repairs"],
        "evidence_not_substring_count": validation["evidence_not_substring_count"],
        "evidence_validity_rate": validation["evidence_validity_rate"],
        "mentions_total": scorecard["mentions_total"],
        "mentions_with_cui": scorecard["mentions_with_cui"],
        "cui_attachment_rate": scorecard["cui_attachment_rate"],
        "routing_count": scorecard["routing_count"],
        "active_entities": scorecard["active_entities"],
        "prescription_clinical_headline_f1": scorecard["prescription_component_scores"][
            "clinical_headline"
        ]["f1"],
        "prescription_benchmark_with_cui_f1": scorecard[
            "prescription_benchmark_projection_scores"
        ]["benchmark_with_cui"]["f1"],
    }
    for layer in ("phrase_only", "semantic", "benchmark"):
        metrics[f"{layer}_per_item_f1"] = scorecard["scores"][layer]["per_item"]["f1"]
        metrics[f"{layer}_per_letter_f1"] = scorecard["scores"][layer]["per_letter"]["f1"]
    return metrics
