from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist


Mapper = Callable[[float], str]


def convert_to_categories(values: Sequence[float], method: str = "purist") -> list[str]:
    mapper: Mapper
    if method == "purist":
        mapper = map_purist
    elif method == "pragmatic":
        mapper = map_pragmatic
    else:
        raise ValueError("method must be 'purist' or 'pragmatic'")
    return [str(mapper(value)) for value in values]


def evaluate_predictions(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    method: str = "purist",
) -> dict[str, dict[str, float]]:
    y_true_cat = convert_to_categories(y_true, method=method)
    y_pred_cat = convert_to_categories(y_pred, method=method)

    if len(y_true_cat) != len(y_pred_cat):
        raise ValueError("y_true and y_pred must have the same length")

    labels = sorted(set(y_true_cat) | set(y_pred_cat))
    support = Counter(y_true_cat)
    per_label = [_label_metrics(label, y_true_cat, y_pred_cat) for label in labels]
    accuracy = sum(t == p for t, p in zip(y_true_cat, y_pred_cat, strict=True)) / len(y_true_cat)

    total_tp = sum(metrics["tp"] for metrics in per_label)
    total_fp = sum(metrics["fp"] for metrics in per_label)
    total_fn = sum(metrics["fn"] for metrics in per_label)

    micro_precision = _safe_div(total_tp, total_tp + total_fp)
    micro_recall = _safe_div(total_tp, total_tp + total_fn)
    micro_f1 = _f1(micro_precision, micro_recall)

    macro_precision = sum(metrics["precision"] for metrics in per_label) / len(per_label)
    macro_recall = sum(metrics["recall"] for metrics in per_label) / len(per_label)
    macro_f1 = sum(metrics["f1"] for metrics in per_label) / len(per_label)

    total_support = sum(support.values())
    weighted_precision = sum(metrics["precision"] * support[metrics["label"]] for metrics in per_label)
    weighted_recall = sum(metrics["recall"] * support[metrics["label"]] for metrics in per_label)
    weighted_f1 = sum(metrics["f1"] * support[metrics["label"]] for metrics in per_label)

    results: dict[str, dict[str, float]] = {
        "micro": _rounded_metrics(micro_precision, micro_recall, micro_f1, accuracy),
        "macro": _rounded_metrics(macro_precision, macro_recall, macro_f1, accuracy),
        "weighted": _rounded_metrics(
            _safe_div(weighted_precision, total_support),
            _safe_div(weighted_recall, total_support),
            _safe_div(weighted_f1, total_support),
            accuracy,
        ),
    }
    return results


def _label_metrics(label: str, y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, float | str]:
    tp = sum(t == label and p == label for t, p in zip(y_true, y_pred, strict=True))
    fp = sum(t != label and p == label for t, p in zip(y_true, y_pred, strict=True))
    fn = sum(t == label and p != label for t, p in zip(y_true, y_pred, strict=True))
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    return {
        "label": label,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
    }


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return _safe_div(2 * precision * recall, precision + recall)


def _rounded_metrics(
    precision: float,
    recall: float,
    f1: float,
    accuracy: float,
) -> dict[str, float]:
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }
