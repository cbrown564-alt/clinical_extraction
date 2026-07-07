"""Row scoring and risk-feature helpers for reliability analysis."""

from __future__ import annotations

from typing import Any

from clinical_extraction.core.scoring import PRF1, multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    _FAMILY_BASE_RISK,
    _PLAN_LANGUAGE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)


def ann(mention: dict[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention.get("entity", "")),
        text=str(mention.get("text", "")),
        attributes={
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value is not None
        },
    )


def letters_for_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[ExectLetter], list[ExectLetter]]:
    gold_letters = []
    pred_letters = []
    for row in rows:
        gold_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(ann(mention) for mention in row.get("gold_mentions", [])),
            )
        )
        pred_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(ann(mention) for mention in row.get("predicted_mentions", [])),
            )
        )
    return gold_letters, pred_letters


def clinical_headline_scores(
    gold_letters: list[ExectLetter],
    pred_letters: list[ExectLetter],
) -> dict[str, dict[str, Any]]:
    return {
        "Diagnosis": score_dict(
            score_concept_identity(gold_letters, pred_letters, "Diagnosis").concept_only
        ),
        "SeizureFrequency": score_dict(
            score_frequency_state(gold_letters, pred_letters).clinical_headline
        ),
        "Prescription": score_dict(
            score_prescription_components(gold_letters, pred_letters).clinical_headline
        ),
        "Investigations": score_dict(
            score_investigations_components(gold_letters, pred_letters).clinical_headline
        ),
    }


def score_dict(score: Any) -> dict[str, Any]:
    pred_count = int(getattr(score, "pred_count", score.tp + score.fp))
    gold_count = int(getattr(score, "gold_count", score.tp + score.fn))
    return {
        "tp": score.tp,
        "precision_tp": int(getattr(score, "precision_tp", score.tp)),
        "recall_tp": int(getattr(score, "recall_tp", score.tp)),
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": pred_count,
        "gold_count": gold_count,
        "precision": score.precision,
        "recall": score.recall,
        "f1": score.f1,
    }


def aggregate_scores(scores: Any) -> dict[str, Any]:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        precision_tp += int(score.get("precision_tp", score.get("tp", 0)))
        recall_tp += int(score.get("recall_tp", score.get("tp", 0)))
        pred_default = int(score.get("tp", 0)) + int(score.get("fp", 0))
        gold_default = int(score.get("tp", 0)) + int(score.get("fn", 0))
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


def headline_keys(
    row: dict[str, Any],
    family: str,
    *,
    field: str = "predicted_mentions",
) -> list[str]:
    mentions = [
        ann(mention) for mention in row.get(field, []) if str(mention.get("entity", "")) == family
    ]
    return [repr(key) for key in clinical_headline_unit_keys(family, mentions)]


def surface_headline_keys(
    row: dict[str, Any],
    family: str,
    surface: str,
) -> list[str]:
    mentions = [
        ann(mention)
        for mention in (row.get("prediction_surfaces", {}).get(surface) or [])
        if str(mention.get("entity", "")) == family
    ]
    return [repr(key) for key in clinical_headline_unit_keys(family, mentions)]


def row_family_score(row: dict[str, Any], family: str) -> PRF1:
    return multiset_prf1(
        headline_keys(row, family, field="gold_mentions"),
        headline_keys(row, family),
    )


def risk_features(row: dict[str, Any], family: str) -> dict[str, Any]:
    mentions = [
        mention
        for mention in row.get("predicted_mentions", [])
        if str(mention.get("entity", "")) == family
    ]
    evidence_invalid = any(not bool(mention.get("evidence_valid", True)) for mention in mentions)
    low_confidence = any(
        str(mention.get("confidence", "high")).lower() not in {"", "high"} for mention in mentions
    )
    deterministic_actions = deterministic_action_count(mentions)
    source_final_delta = (
        surface_headline_keys(row, family, "source_scored")
        != surface_headline_keys(row, family, "final")
        if row.get("prediction_surfaces")
        else False
    )
    active_rate = any(
        mention.get("attributes", {}).get("NumberOfSeizures")
        or mention.get("attributes", {}).get("LowerNumberOfSeizures")
        or mention.get("attributes", {}).get("UpperNumberOfSeizures")
        for mention in mentions
    )
    plan_language = any(
        _PLAN_LANGUAGE.search(str(mention.get("evidence", "")))
        or _PLAN_LANGUAGE.search(str(mention.get("text", "")))
        for mention in mentions
    )
    result_state = any(
        key.endswith("_Results") or key.endswith("_Performed")
        for mention in mentions
        for key in (mention.get("attributes") or {})
    )
    return {
        "evidence_invalid": evidence_invalid,
        "low_confidence": low_confidence,
        "deterministic_action_count": deterministic_actions,
        "source_final_delta": source_final_delta,
        "active_rate": active_rate,
        "plan_language": plan_language,
        "result_state": result_state,
        "prediction_count": len(mentions),
    }


def risk_score(family: str, features: dict[str, Any]) -> float:
    score = _FAMILY_BASE_RISK.get(family, 0.18)
    if features["evidence_invalid"]:
        score += 0.25
    if features["source_final_delta"]:
        score += 0.12
    if int(features["deterministic_action_count"]) > 0:
        score += 0.10
    if features["low_confidence"]:
        score += 0.08
    if family == "SeizureFrequency" and features["active_rate"]:
        score += 0.08
    if family == "Prescription" and features["plan_language"]:
        score += 0.08
    if family == "Investigations" and features["result_state"]:
        score += 0.04
    return round(min(score, 0.95), 4)


def review_triggers(cell: dict[str, Any]) -> list[str]:
    family = str(cell["family"])
    features = cell["features"]
    triggers = []
    if float(cell["risk_score"]) >= 0.35:
        triggers.append("high_proxy_risk")
    if features["evidence_invalid"]:
        triggers.append("evidence_invalid")
    if family == "Diagnosis" and int(features["deterministic_action_count"]) > 0:
        triggers.append("diagnosis_convention_or_assertion_repair")
    if family == "SeizureFrequency" and (features["source_final_delta"] or features["active_rate"]):
        triggers.append("sf_state_or_rate_fidelity")
    if family == "Prescription" and (
        features["plan_language"] or int(features["deterministic_action_count"]) > 0
    ):
        triggers.append("prescription_current_vs_plan")
    if family == "Investigations" and (
        features["result_state"] and int(features["deterministic_action_count"]) > 0
    ):
        triggers.append("investigations_result_state")
    return sorted(set(triggers))


def deterministic_action_count(mentions: list[dict[str, Any]]) -> int:
    count = 0
    for mention in mentions:
        for event in mention.get("provenance") or []:
            action = str(event.get("action", "")).lower()
            owner = str(event.get("owner", "")).lower()
            if (
                "repair" in action
                or "suppress" in action
                or "added" in action
                or "recovery" in action
                or "deterministic" in owner
            ):
                count += 1
    return count


def confidence_bin(confidence: float) -> str:
    if confidence >= 0.78:
        return "very_high"
    if confidence >= 0.65:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def round_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def row_has_call_error(row: dict[str, Any]) -> bool:
    if row.get("call_error") or row.get("generation_call_error") or row.get("selection_call_error"):
        return True
    family_errors = row.get("dedup_fact_call_errors_by_family") or {}
    return any(family_errors.values())


def row_parse_error_count(row: dict[str, Any]) -> int:
    fields = (
        "parse_errors",
        "generation_parse_errors",
        "inventory_parse_errors",
        "selection_parse_errors",
        "adapter_parse_errors",
    )
    return sum(len(row.get(field) or []) for field in fields)


def prompt_metadata(rows: list[dict[str, Any]]) -> tuple[str, str, str]:
    if not rows:
        return "unknown", "unknown", "unknown"
    first = rows[0]
    return (
        str(first.get("prompt_version") or "unknown"),
        str(first.get("prompt_profile") or "unknown"),
        str(first.get("temperature") or first.get("sampling_temperature") or "not_recorded"),
    )


def row_mode(rows: list[dict[str, Any]]) -> str:
    modes = {str(row.get("mode") or "unknown") for row in rows}
    if len(modes) == 1:
        return next(iter(modes))
    return "mixed"


def seed_label(run: ReliabilityRun, rows: list[dict[str, Any]]) -> str:
    seeds = {
        str(row.get("seed") or row.get("sampling_seed") or row.get("repeat_id") or "")
        for row in rows
    }
    seeds.discard("")
    if len(seeds) == 1:
        return next(iter(seeds))
    if len(seeds) > 1:
        return "mixed"
    return run.candidate
