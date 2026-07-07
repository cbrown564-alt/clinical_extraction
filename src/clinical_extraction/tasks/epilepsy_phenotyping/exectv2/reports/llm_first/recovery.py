"""Clinical recovery scoring helpers for the LLM-first essential evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    ESSENTIAL_ATOMIC_CONCEPT_ONLY,
    ESSENTIAL_CLINICAL_ENTITIES,
)


def score_for_primary(entity: str, scorecard: dict[str, Any]) -> dict[str, Any]:
    score = scorecard["headline_scores"][entity]
    if entity in ESSENTIAL_ATOMIC_CONCEPT_ONLY:
        return score["concept_only"]
    return score["headline"]


def aggregate_score_dicts(scores: Sequence[dict[str, Any]]) -> dict[str, Any]:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        tp = int(score.get("tp", 0))
        precision_tp += int(score.get("precision_tp", tp))
        recall_tp += int(score.get("recall_tp", tp))
        pred_default = tp + int(score.get("fp", 0))
        gold_default = tp + int(score.get("fn", 0))
        pred_count += int(score.get("pred_count", pred_default))
        gold_count += int(score.get("gold_count", gold_default))
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": recall_tp,
        "precision_tp": precision_tp,
        "recall_tp": recall_tp,
        "fp": max(0, pred_count - precision_tp),
        "fn": max(0, gold_count - recall_tp),
        "pred_count": pred_count,
        "gold_count": gold_count,
    }


def primary_recovery(
    scorecard: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    scores = {
        entity: score_for_primary(entity, scorecard) for entity in ESSENTIAL_CLINICAL_ENTITIES
    }
    return aggregate_score_dicts(tuple(scores.values())), scores


def evidence_validation_summary(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    entities: Sequence[str] = ESSENTIAL_CLINICAL_ENTITIES,
) -> dict[str, Any]:
    """Summarize exact evidence-substring validity for prediction mentions."""

    note_by_id = {letter.letter_id: letter.note_text or "" for letter in gold_letters}
    entity_set = set(entities)
    per_entity: dict[str, dict[str, int]] = {
        e: {"predicted_mentions": 0, "evidence_present": 0, "exact_evidence": 0} for e in entities
    }
    for pred in pred_letters:
        note = note_by_id.get(pred.letter_id, "")
        for mention in pred.mentions:
            if mention.entity not in entity_set:
                continue
            stats = per_entity[mention.entity]
            stats["predicted_mentions"] += 1
            evidence = mention.evidence.strip()
            if not evidence:
                continue
            stats["evidence_present"] += 1
            if note and evidence in note:
                stats["exact_evidence"] += 1

    totals = {"predicted_mentions": 0, "evidence_present": 0, "exact_evidence": 0}
    out: dict[str, Any] = {}
    for entity, stats in per_entity.items():
        for key in totals:
            totals[key] += stats[key]
        pred_n = stats["predicted_mentions"]
        invalid = pred_n - stats["exact_evidence"]
        out[entity] = {
            **stats,
            "invalid_evidence": invalid,
            "evidence_present_rate": round(stats["evidence_present"] / pred_n, 4)
            if pred_n
            else 0.0,
            "exact_evidence_rate": round(stats["exact_evidence"] / pred_n, 4) if pred_n else 0.0,
            "invalid_evidence_rate": round(invalid / pred_n, 4) if pred_n else 0.0,
        }
    pred_n = totals["predicted_mentions"]
    invalid = pred_n - totals["exact_evidence"]
    out["overall"] = {
        **totals,
        "invalid_evidence": invalid,
        "evidence_present_rate": round(totals["evidence_present"] / pred_n, 4) if pred_n else 0.0,
        "exact_evidence_rate": round(totals["exact_evidence"] / pred_n, 4) if pred_n else 0.0,
        "invalid_evidence_rate": round(invalid / pred_n, 4) if pred_n else 0.0,
    }
    return out


def error_taxonomy_summary(
    primary_scores: dict[str, dict[str, Any]],
    evidence_summary: dict[str, Any],
) -> dict[str, Any]:
    """Coarse corpus-level error taxonomy for the LLM-first report."""

    per_entity: dict[str, dict[str, int]] = {}
    totals = {"candidate_miss": 0, "wrong_detail_selection": 0, "evidence_failure": 0}
    for entity in ESSENTIAL_CLINICAL_ENTITIES:
        score = primary_scores[entity]
        evidence = evidence_summary[entity]
        row = {
            "candidate_miss": int(score["fn"]),
            "wrong_detail_selection": int(score["fp"]),
            "evidence_failure": int(evidence["predicted_mentions"] - evidence["exact_evidence"]),
        }
        per_entity[entity] = row
        for key in totals:
            totals[key] += row[key]
    return {
        "note": (
            "Coarse diagnostic taxonomy; categories can overlap and do not replace "
            "row-level adjudication."
        ),
        "overall": totals,
        "per_entity": per_entity,
    }


def clinical_fidelity_companions(scorecard: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Surface clinical-fidelity companions next to the lenient headline."""

    headline_scores = scorecard.get("headline_scores", {})
    out: dict[str, dict[str, Any]] = {}
    diagnosis = headline_scores.get(DIAGNOSIS.name, {})
    if "concept_negation" in diagnosis:
        headline_f1 = float(diagnosis["concept_only"]["f1"])
        companion_f1 = float(diagnosis["concept_negation"]["f1"])
        out[DIAGNOSIS.name] = {
            "companion": "concept_negation",
            "forgives": "Negation (negated vs affirmed)",
            "headline_f1": headline_f1,
            "companion_f1": companion_f1,
            "fidelity_gap": round(headline_f1 - companion_f1, 4),
        }
    frequency = headline_scores.get(SEIZURE_FREQUENCY.name, {})
    components = frequency.get("components", {})
    if "active_rate_fidelity" in components:
        headline_f1 = float(components["clinical_headline"]["f1"])
        companion_f1 = float(components["active_rate_fidelity"]["f1"])
        out[SEIZURE_FREQUENCY.name] = {
            "companion": "active_rate_fidelity",
            "forgives": "rate magnitude among active states",
            "headline_f1": headline_f1,
            "companion_f1": companion_f1,
            "fidelity_gap": round(headline_f1 - companion_f1, 4),
        }
    return out
