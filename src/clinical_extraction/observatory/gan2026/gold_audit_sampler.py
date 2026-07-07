"""Active-sampling helpers for the Gan 2026 gold audit worklist."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

AUDIT_CLASSES = ("correct", "ambiguous", "wrong")
MIN_MODELLED_DECISIONS = 20


@dataclass(frozen=True)
class GoldAuditSamplingModel:
    """Transparent smoothed model over human audit decisions."""

    total_decisions: int
    class_counts: Mapping[str, int]
    feature_class_counts: Mapping[str, Mapping[str, int]]
    feature_counts: Mapping[str, int]
    global_probs: Mapping[str, float]
    is_calibrated_enough: bool

    def score_row(self, row: Mapping[str, Any]) -> dict[str, Any]:
        """Return predicted class probabilities and active-sampling priority."""

        probs = _predict_class_probs(row, self)
        entropy = _normalized_entropy(probs)
        rejection_prob = probs["ambiguous"] + probs["wrong"]
        novelty = _novelty_score(row, self.feature_counts)
        balance = _class_balance_bonus(probs, self.class_counts, self.total_decisions)
        heuristic = _heuristic_review_score(row)
        active_score = 100.0 * (
            0.34 * entropy
            + 0.25 * rejection_prob
            + 0.15 * novelty
            + 0.10 * balance
            + 0.16 * heuristic
        )
        if self.total_decisions < MIN_MODELLED_DECISIONS:
            active_score *= 0.75
        return {
            "predicted_simple_class": max(AUDIT_CLASSES, key=lambda c: probs[c]),
            "predicted_correct_prob": round(probs["correct"], 4),
            "predicted_ambiguous_prob": round(probs["ambiguous"], 4),
            "predicted_wrong_prob": round(probs["wrong"], 4),
            "prediction_confidence": round(max(probs.values()), 4),
            "prediction_uncertainty": round(entropy, 4),
            "active_learning_score": round(active_score, 2),
            "active_learning_reason": _score_reason(row, probs, entropy, novelty, balance),
        }

    def summary(self) -> dict[str, Any]:
        """Summarise current audit confidence for the UI or reports."""

        intervals = {}
        for class_name in AUDIT_CLASSES:
            count = int(self.class_counts.get(class_name, 0))
            intervals[class_name] = _wilson_interval(count, self.total_decisions)
        projected = {
            str(n): {
                class_name: _wilson_interval(
                    int(self.class_counts.get(class_name, 0)),
                    max(n, self.total_decisions),
                )
                for class_name in AUDIT_CLASSES
            }
            for n in (50, 75, 100)
        }
        return {
            "model_kind": "smoothed_feature_naive_bayes_active_sampler",
            "decision_count": self.total_decisions,
            "minimum_modelled_decisions": MIN_MODELLED_DECISIONS,
            "is_calibrated_enough": self.is_calibrated_enough,
            "class_counts": dict(self.class_counts),
            "global_probs": dict(self.global_probs),
            "class_rate_intervals_95": intervals,
            "projected_class_rate_intervals_95": projected,
            "claim_language": (
                "Validation worklist triage only. These predictions rank rows for human "
                "review; they do not change gold labels, scorer policy, benchmark claims, "
                "or locked-test behavior."
            ),
        }


def build_sampling_model(
    rows: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> GoldAuditSamplingModel:
    """Fit a small transparent model from audited rows and decisions."""

    row_by_key = {_decision_key(row): row for row in rows}
    keyed_decisions = latest_decisions(decisions)
    class_counts: Counter[str] = Counter()
    feature_class_counts: dict[str, Counter[str]] = defaultdict(Counter)
    feature_counts: Counter[str] = Counter()

    for key, decision in keyed_decisions.items():
        row = row_by_key.get(key)
        class_name = str(decision.get("simple_class", ""))
        if row is None or class_name not in AUDIT_CLASSES:
            continue
        class_counts[class_name] += 1
        for feature in row_features(row):
            feature_counts[feature] += 1
            feature_class_counts[feature][class_name] += 1

    total = sum(class_counts.values())
    alpha = 1.0
    denom = total + alpha * len(AUDIT_CLASSES)
    global_probs = {
        class_name: (class_counts[class_name] + alpha) / denom for class_name in AUDIT_CLASSES
    }
    return GoldAuditSamplingModel(
        total_decisions=total,
        class_counts={class_name: class_counts[class_name] for class_name in AUDIT_CLASSES},
        feature_class_counts={
            feature: {class_name: counts[class_name] for class_name in AUDIT_CLASSES}
            for feature, counts in feature_class_counts.items()
        },
        feature_counts=dict(feature_counts),
        global_probs=global_probs,
        is_calibrated_enough=total >= MIN_MODELLED_DECISIONS,
    )


def enrich_rows_for_active_sampling(
    rows: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attach model predictions and active-sampling scores to worklist rows."""

    model = build_sampling_model(rows, decisions)
    decided = set(latest_decisions(decisions))
    enriched = []
    for row in rows:
        payload = dict(row)
        key = _decision_key(row)
        payload["has_decision"] = key in decided
        payload.update(model.score_row(row))
        enriched.append(payload)
    return enriched, model.summary()


def row_features(row: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract transparent categorical features from an audit CSV row."""

    features = [
        f"kind={_clean(row.get('gold_label_kind'))}",
        f"initial={_clean(row.get('codex_initial_ambiguity_label'))}",
        f"ref_found={_bool_text(row.get('reference_found_in_note'))}",
        f"labels_match={_bool_text(row.get('labels_match_all_categories'))}",
        f"quotes_ok={_bool_text(row.get('quotes_ok_all_categories'))}",
        f"row_ok={_bool_text(row.get('row_ok'))}",
        f"monthly_bucket={_monthly_bucket(row.get('gold_monthly_frequency'))}",
        f"reason_count={_reason_count_bucket(row.get('codex_ambiguity_reasons'))}",
        f"reference_len={_length_bucket(row.get('gold_reference'))}",
        f"note_len={_length_bucket(row.get('note_text_single_line'))}",
    ]
    label = str(row.get("gold_label", "")).lower()
    reference = str(row.get("gold_reference", "")).lower()
    combined = f"{label} {reference}"
    for token in _reason_tokens(row.get("codex_ambiguity_reasons")):
        features.append(f"reason={token}")
    for pattern in (
        "multiple",
        "unknown",
        "seizure free",
        "cluster",
        "diary",
        "range",
        "month",
        "week",
        "year",
        "day",
    ):
        if pattern in combined:
            features.append(f"text_has={pattern.replace(' ', '_')}")
    return tuple(features)


def _predict_class_probs(
    row: Mapping[str, Any],
    model: GoldAuditSamplingModel,
) -> dict[str, float]:
    if model.total_decisions == 0:
        return {class_name: 1.0 / len(AUDIT_CLASSES) for class_name in AUDIT_CLASSES}

    beta = 1.0
    log_probs = {}
    features = row_features(row)
    for class_name in AUDIT_CLASSES:
        class_count = int(model.class_counts.get(class_name, 0))
        log_p = math.log(float(model.global_probs[class_name]))
        for feature in features:
            counts = model.feature_class_counts.get(feature, {})
            feature_class_count = int(counts.get(class_name, 0))
            log_p += math.log((feature_class_count + beta) / (class_count + 2.0 * beta))
        log_probs[class_name] = log_p

    max_log = max(log_probs.values())
    weights = {
        class_name: math.exp(log_probs[class_name] - max_log) for class_name in AUDIT_CLASSES
    }
    total_weight = sum(weights.values())
    return {class_name: weights[class_name] / total_weight for class_name in AUDIT_CLASSES}


def latest_decisions(
    decisions: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, int], Mapping[str, Any]]:
    """Return the latest decision per (split, source_row_index)."""

    latest: dict[tuple[str, int], Mapping[str, Any]] = {}
    for decision in decisions:
        latest[_decision_key(decision)] = decision
    return latest


def _decision_key(row: Mapping[str, Any]) -> tuple[str, int]:
    return (str(row.get("split", "")), int(row.get("source_row_index", 0)))


def _normalized_entropy(probs: Mapping[str, float]) -> float:
    entropy = -sum(p * math.log(p) for p in probs.values() if p > 0)
    return entropy / math.log(len(AUDIT_CLASSES))


def _novelty_score(row: Mapping[str, Any], feature_counts: Mapping[str, int]) -> float:
    features = row_features(row)
    if not features:
        return 1.0
    sparse = sorted(int(feature_counts.get(feature, 0)) for feature in features)[:5]
    return sum(1.0 / math.sqrt(count + 1.0) for count in sparse) / len(sparse)


def _class_balance_bonus(
    probs: Mapping[str, float],
    class_counts: Mapping[str, int],
    total_decisions: int,
) -> float:
    if total_decisions == 0:
        return 1.0
    target = total_decisions / len(AUDIT_CLASSES)
    if target <= 0:
        return 0.0
    return sum(
        probs[class_name] * max(0.0, target - float(class_counts.get(class_name, 0))) / target
        for class_name in AUDIT_CLASSES
    )


def _heuristic_review_score(row: Mapping[str, Any]) -> float:
    """Bootstrap score used before the learned model has much evidence."""

    reasons = str(row.get("codex_ambiguity_reasons", "")).lower()
    label = str(row.get("codex_initial_ambiguity_label", "")).lower()
    kind = str(row.get("gold_label_kind", "")).lower()
    ref_found = _bool_text(row.get("reference_found_in_note"))
    labels_match = _bool_text(row.get("labels_match_all_categories"))
    score = 0.0

    if label == "ambiguous":
        score += 4.0
    if kind == "unresolved_multiple":
        score += 3.0
    if ref_found == "false":
        score += 2.5
    for reason, weight in {
        "reference_does_not_explicitly_support_frequency": 2.5,
        "range_or_upper_bound": 2.0,
        "vague_count_or_period": 2.0,
        "calendar_or_diary_arithmetic": 1.5,
        "unknown_gold_boundary": 1.5,
        "cluster_or_per_cluster_convention": 1.5,
    }.items():
        if reason in reasons:
            score += weight
    if labels_match == "false":
        score += 1.5
    return min(1.0, score / 10.0)


def _score_reason(
    row: Mapping[str, Any],
    probs: Mapping[str, float],
    entropy: float,
    novelty: float,
    balance: float,
) -> str:
    parts = []
    if probs["ambiguous"] + probs["wrong"] >= 0.45:
        parts.append("high predicted non-correct yield")
    if entropy >= 0.65:
        parts.append("uncertain class prediction")
    if novelty >= 0.55:
        parts.append("sparse feature bucket")
    if balance >= 0.25:
        parts.append("helps under-sampled class balance")
    if not parts:
        parts.append("baseline coverage row")
    reasons = str(row.get("codex_ambiguity_reasons", ""))
    first_reason = next((reason for reason in reasons.split(";") if reason), "")
    if first_reason:
        parts.append(first_reason.replace("_", " "))
    return "; ".join(parts[:3])


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float]:
    if total <= 0:
        return {"count": successes, "n": total, "rate": 0.0, "low": 0.0, "high": 1.0}
    p = successes / total
    denom = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denom
    margin = z * math.sqrt((p * (1.0 - p) / total) + (z * z / (4.0 * total * total))) / denom
    return {
        "count": successes,
        "n": total,
        "rate": round(p, 4),
        "low": round(max(0.0, centre - margin), 4),
        "high": round(min(1.0, centre + margin), 4),
    }


def _clean(value: Any) -> str:
    text = str(value if value is not None else "").strip().lower()
    return text or "missing"


def _bool_text(value: Any) -> str:
    text = _clean(value)
    if text in {"true", "1", "yes"}:
        return "true"
    if text in {"false", "0", "no"}:
        return "false"
    return "missing"


def _reason_tokens(value: Any) -> tuple[str, ...]:
    return tuple(token for token in str(value or "").lower().split(";") if token)


def _reason_count_bucket(value: Any) -> str:
    count = len(_reason_tokens(value))
    if count == 0:
        return "0"
    if count == 1:
        return "1"
    if count == 2:
        return "2"
    return "3plus"


def _length_bucket(value: Any) -> str:
    length = len(str(value or ""))
    if length < 40:
        return "short"
    if length < 160:
        return "medium"
    if length < 1200:
        return "long"
    return "very_long"


def _monthly_bucket(value: Any) -> str:
    try:
        monthly = float(value)
    except (TypeError, ValueError):
        return "missing"
    if monthly < 0:
        return "negative_sentinel"
    if monthly == 0:
        return "zero"
    if monthly < 0.25:
        return "very_infrequent"
    if monthly < 1:
        return "infrequent"
    if monthly < 4:
        return "monthly"
    if monthly < 30:
        return "frequent"
    return "sentinel_or_very_high"
