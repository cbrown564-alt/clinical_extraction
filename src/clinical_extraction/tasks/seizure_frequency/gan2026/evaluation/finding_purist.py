"""Finding Purist inventory score. The exact matcher stays ``finding_matching_v07``.

A prediction matches a reference finding when the quotations overlap, the event
labels are equivalent, timing agrees, and the measurement agrees by one of these
rules:

- both render to Gan labels in the same native Purist band (a rate, a count with
  a numeric window, or a cluster the existing label parser accepts);
- both are qualitative and agree after the v0.7 closed-list map;
- both are seizure-free and the duration and since anchor agree, using the exact
  matcher's time-point spelling tolerance;
- both are last-seizure findings and that time comparison agrees;
- or the exact matcher already matches them.

Seizure status, condition, approximation, inclusivity and the period string are
not compared when the Purist band, qualitative value, seizure-free anchor or
last-seizure time decides the match. A count whose only window is prose does not
receive a band, so a different prose window still fails. Seizure-free findings
do not collapse to zero unless ``collapse_seizure_free`` is set, and that result
is a named companion rather than this score.
"""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

MATCHING_VERSION = "finding_purist_v1"
COLLAPSED_VERSION = "finding_purist_v1_seizure_free_collapsed"

# Guide v0.7 closed list, including the source-wording map in the annotation guide.
_QUALITATIVE = {
    "rare": "rare",
    "occasional": "occasional",
    "infrequent": "occasional",
    "intermittent": "occasional",
    "sporadic": "occasional",
    "frequent": "frequent",
    "most days": "frequent",
    "near-daily": "frequent",
    "near daily": "frequent",
    "increased": "increased",
    "more frequent": "increased",
    "worsening frequency": "increased",
    "decreased": "decreased",
    "less frequent": "decreased",
    "reduced": "decreased",
    "unchanged": "unchanged",
    "variable": "variable",
    "unknown": "unknown",
    "not documented": "unknown",
    "unable to quantify": "unknown",
}
_RATE_UNITS = {"day", "week", "month", "year"}


def qualitative_value(finding: dict[str, Any]) -> str | None:
    """Closed-list value, or None when the finding is not a mapped qualitative."""
    measurement = finding.get("measurement") or {}
    if measurement.get("type") != "qualitative":
        return None
    return _QUALITATIVE.get(exact.norm_text(str(measurement.get("frequency") or "")))


def purist_band(finding: dict[str, Any]) -> str | None:
    """Native Purist band for a projectable rate, numeric-window count or cluster."""
    label = _gan_label(finding)
    if label is None:
        return None
    try:
        monthly = label_to_frequency_record(label).monthly_frequency
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    if monthly == 1000 or monthly < 0:
        return None
    band = str(map_purist(monthly))
    if band == "seizure_freq_unknown":
        return None
    return band


def _fmt(value: float) -> str:
    return str(int(value)) if value == int(value) else str(value)


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _quantity_text(quantity: dict[str, Any] | None) -> str | None:
    if not quantity:
        return None
    kind = quantity.get("type")
    if kind == "number":
        value = _number(quantity.get("value"))
        return None if value is None else _fmt(value)
    if kind == "range":
        lower, upper = _number(quantity.get("lower")), _number(quantity.get("upper"))
        if lower is None or upper is None:
            return None
        return f"{_fmt(lower)} to {_fmt(upper)}"
    if kind == "qualitative":
        text = exact.norm_text(str(quantity.get("quantity") or ""))
        return "multiple" if text == "multiple" else None
    if kind == "bound":
        inner = quantity.get("value")
        number = _quantity_text(inner) if isinstance(inner, dict) else None
        if number is None:
            value = _number(inner)
            number = None if value is None else _fmt(value)
        if number is None:
            return None
        if quantity.get("relation") in {"at_least", "more_than"}:
            return f"{number} or more"
        return number
    return None


def _duration_text(duration: dict[str, Any] | None) -> str | None:
    """Render a numeric duration. Ranges stay ranges so the label parser midpoints them."""
    if not duration or duration.get("type") == "qualitative":
        return None
    unit = duration.get("unit")
    if unit == "quarter" or unit not in _RATE_UNITS:
        return None
    kind = duration.get("type")
    if kind == "number":
        value = _number(duration.get("value"))
        if value is None:
            return None
        return unit if value == 1 else f"{_fmt(value)} {unit}"
    if kind == "range":
        lower, upper = _number(duration.get("lower")), _number(duration.get("upper"))
        if lower is None or upper is None:
            return None
        return f"{_fmt(lower)} to {_fmt(upper)} {unit}"
    if kind == "bound":
        inner = duration.get("value")
        if isinstance(inner, dict):
            rendered = _quantity_text(inner)
            if rendered is None:
                return None
            return f"{rendered.removesuffix(' or more')} {unit}"
        return _duration_text({**duration, "type": "number", "value": inner})
    return None


def _gan_label(finding: dict[str, Any]) -> str | None:
    """Gan label for band comparison. Seizure-free findings are not collapsed to zero."""
    measurement = finding.get("measurement") or {}
    kind = measurement.get("type")
    if kind == "rate":
        count = _quantity_text(measurement.get("count"))
        per = _duration_text(measurement.get("per"))
        return f"{count} per {per}" if count and per else None
    if kind == "count":
        count = _quantity_text(measurement.get("count"))
        per = _duration_text((finding.get("period") or {}).get("duration"))
        return f"{count} per {per}" if count and per else None
    if kind == "cluster":
        rate = measurement.get("rate") or {}
        count = _quantity_text(rate.get("count")) if rate else None
        per = _duration_text(rate.get("per")) if rate else None
        size = _quantity_text(measurement.get("seizures_per_cluster"))
        if count and per and size:
            return f"{count} cluster per {per}, {size} per cluster"
        if count and per:
            return f"{count} per {per}"
        return None
    return None


def _anchors_agree(pred: dict[str, Any], ref: dict[str, Any], *, collapse: bool) -> bool:
    left, right = pred.get("measurement") or {}, ref.get("measurement") or {}
    if left.get("type") == "qualitative" and right.get("type") == "qualitative":
        value = qualitative_value(pred)
        return value is not None and value == qualitative_value(ref)
    if left.get("type") == "seizure_free" and right.get("type") == "seizure_free":
        return collapse or exact.measurement_equal(left, right)
    if left.get("type") == "last_seizure" and right.get("type") == "last_seizure":
        return exact.time_equivalent(left.get("occurred_at"), right.get("occurred_at"))
    return False


def compatible(
    pred: dict[str, Any],
    ref: dict[str, Any],
    note: str,
    *,
    collapse_seizure_free: bool = False,
) -> bool:
    if not exact.evidence_overlap(note, pred.get("evidence", ""), ref.get("evidence", "")):
        return False
    if exact.label_key(pred["event"]["type"]) != exact.label_key(ref["event"]["type"]):
        return False
    if pred.get("timing", "current") != ref.get("timing", "current"):
        return False
    left, right = purist_band(pred), purist_band(ref)
    if left is not None and left == right:
        return True
    if _anchors_agree(pred, ref, collapse=collapse_seizure_free):
        return True
    return not exact.attribute_diffs(pred, ref, note)


def _reasons(pred: dict[str, Any], ref: dict[str, Any], note: str, *, collapse: bool) -> list[str]:
    reasons: list[str] = []
    if not exact.evidence_overlap(note, pred.get("evidence", ""), ref.get("evidence", "")):
        reasons.append("evidence")
    try:
        same_event = exact.label_key(pred["event"]["type"]) == exact.label_key(ref["event"]["type"])
    except (KeyError, TypeError):
        same_event = False
    if not same_event:
        reasons.append("event")
    if pred.get("timing", "current") != ref.get("timing", "current"):
        reasons.append("timing")
    if not compatible(pred, ref, note, collapse_seizure_free=collapse):
        if "evidence" not in reasons and "event" not in reasons and "timing" not in reasons:
            reasons.append("measurement")
    return reasons


def score_letter(
    note: str,
    reference: list[dict[str, Any]],
    predictions: list[dict[str, Any]] | None,
    *,
    collapse_seizure_free: bool = False,
) -> dict[str, Any]:
    """TP/FP/FN for one letter. ``predictions=None`` is an unusable inventory."""
    if predictions is None:
        return {
            "usable": False,
            "tp": 0,
            "fp": 0,
            "fn": len(reference),
            "predicted": None,
            "reference": len(reference),
            "pairs": [],
            "unmatched_diagnostics": [],
        }
    edges: dict[int, list[int]] = {}
    for i, pred in enumerate(predictions):
        for j, ref in enumerate(reference):
            if compatible(pred, ref, note, collapse_seizure_free=collapse_seizure_free):
                edges.setdefault(i, []).append(j)
    matched = exact.maximum_matching(edges, len(predictions))
    diagnostics = []
    for i, pred in enumerate(predictions):
        if i in matched:
            continue
        best = min(
            (
                _reasons(pred, ref, note, collapse=collapse_seizure_free)
                for j, ref in enumerate(reference)
                if j not in matched.values()
            ),
            key=len,
            default=["no_reference_candidate"],
        )
        diagnostics.append({"prediction": pred.get("id"), "closest_diffs": best})
    return {
        "usable": True,
        "tp": len(matched),
        "fp": len(predictions) - len(matched),
        "fn": len(reference) - len(matched),
        "predicted": len(predictions),
        "reference": len(reference),
        "pairs": [
            [predictions[i].get("id"), reference[j].get("id")] for i, j in sorted(matched.items())
        ],
        "unmatched_diagnostics": diagnostics,
    }


def aggregate(
    letters: list[dict[str, Any]], *, collapse_seizure_free: bool = False
) -> dict[str, Any]:
    """Same accounting as the exact matcher, under this score's name."""
    summary = exact.aggregate(letters)
    summary["matching_version"] = COLLAPSED_VERSION if collapse_seizure_free else MATCHING_VERSION
    return summary
