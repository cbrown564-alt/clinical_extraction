"""Lenient, descriptive agreement between returned findings and the dev750 reference.

The native answer is the primary endpoint. This score only describes how much of the
reference inventory the returned findings recover. A predicted finding matches one
reference finding when all three hold:

1. some predicted and reference evidence quotations overlap in the note;
2. the measurements belong to the same family (rate, observed count and median
   interval form one frequency family; cluster, seizure-free, last event and
   qualitative are each their own);
3. their values agree: rates and median intervals fall in the same native Purist
   band, counts and cluster sizes overlap as intervals, qualitative levels are equal.
   Seizure-free durations and last-event times are not compared, as in native Purist.
   A value that cannot be compared (verbatim wording, sub-day units) does not block
   a match.

Event wording, scope, counted unit, status, phase, window wording and restriction
are never required; their agreement among matched pairs is reported descriptively.
Matching is one-to-one and maximum-cardinality, filling core reference findings
before supporting ones. The rule is fixed; do not version or tune it.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

SCORER = "seizure_frequency_findings_lenient"
FREQUENCY_FAMILY = {"rate", "observed_count", "median_interval"}
LABEL_UNITS = {
    "day": ("day", 1.0),
    "week": ("week", 1.0),
    "month": ("month", 1.0),
    "quarter": ("month", 3.0),
    "year": ("year", 1.0),
}
ATTRIBUTES = ("kind", "scope", "counted_unit", "status", "phase", "restriction_stated")

Interval = tuple[float, float]


def _interval(quantity: Any) -> Interval | None:
    if not isinstance(quantity, dict):
        return None
    kind = quantity.get("kind")
    if kind == "number":
        return float(quantity["value"]), float(quantity["value"])
    if kind == "range":
        return float(quantity["lower"]), float(quantity["upper"])
    if kind == "bound":
        value = quantity["value"]
        low, high = (
            (float(value["lower"]), float(value["upper"]))
            if isinstance(value, dict)
            else (float(value), float(value))
        )
        return (low, math.inf) if quantity["relation"] in ("at_least", "more_than") else (0.0, high)
    return None


def _midpoint(value: Any) -> float | None:
    """Range midpoint; a bound uses its stated value, as the native label rules do."""
    if isinstance(value, dict) and value.get("kind") == "bound":
        value = value["value"]
        if not isinstance(value, dict):
            return float(value)
    interval = _interval(value)
    return None if interval is None else sum(interval) / 2


def _band(count: float | None, duration: Any) -> str | None:
    """Native Purist band of count per duration, or None when not comparable."""
    per = _midpoint(duration)
    unit = LABEL_UNITS.get(duration.get("unit", "")) if isinstance(duration, dict) else None
    if count is None or per is None or unit is None or count <= 0 or per <= 0:
        return None
    name, scale = unit
    monthly = label_to_frequency_record(f"{count:g} per {per * scale:g} {name}").monthly_frequency
    return str(map_purist(monthly))


def _rate_band(measurement: dict[str, Any]) -> str | None:
    if measurement["kind"] == "rate":
        return _band(_midpoint(measurement["quantity"]), measurement["per"])
    if measurement["kind"] == "median_interval":
        return _band(1.0, measurement["duration"])
    return None


def _overlap(a: Interval | None, b: Interval | None) -> bool:
    return a is None or b is None or (a[0] <= b[1] and b[0] <= a[1])


def values_agree(predicted: dict[str, Any], reference: dict[str, Any]) -> bool:
    p, r = predicted["kind"], reference["kind"]
    if p in FREQUENCY_FAMILY and r in FREQUENCY_FAMILY:
        if "observed_count" in (p, r):
            if "median_interval" in (p, r):
                return True
            return _overlap(_interval(predicted["quantity"]), _interval(reference["quantity"]))
        bands = _rate_band(predicted), _rate_band(reference)
        return None in bands or bands[0] == bands[1]
    if p != r:
        return False
    if p == "qualitative":
        return bool(predicted["level"] == reference["level"])
    if p == "cluster":
        for key in ("count", "seizures_per_cluster"):
            if key in predicted and key in reference:
                if not _overlap(_interval(predicted[key]), _interval(reference[key])):
                    return False
        if "cadence" in predicted and "cadence" in reference:
            bands = _rate_band(predicted["cadence"]), _rate_band(reference["cadence"])
            return None in bands or bands[0] == bands[1]
    return True


def _spans(note: str, fragments: list[str]) -> list[Interval]:
    spans = []
    for fragment in fragments:
        start = note.find(fragment) if fragment else -1
        while start >= 0:
            spans.append((float(start), float(start + len(fragment))))
            start = note.find(fragment, start + 1)
    return spans


def _evidence_overlaps(a: list[Interval], b: list[Interval]) -> bool:
    return any(x[0] < y[1] and y[0] < x[1] for x in a for y in b)


def match_letter(
    note: str, predicted: list[dict[str, Any]], reference: list[dict[str, Any]]
) -> list[tuple[int, int]]:
    """Maximum one-to-one (reference index, prediction index) pairs, core first."""
    predicted_spans = [_spans(note, f["evidence"]) for f in predicted]
    reference_spans = [_spans(note, f["evidence"]) for f in reference]
    edges = [
        [
            j
            for j, p in enumerate(predicted)
            if _evidence_overlaps(reference_spans[i], predicted_spans[j])
            and values_agree(p["measurement"], r["measurement"])
        ]
        for i, r in enumerate(reference)
    ]
    owner: dict[int, int] = {}

    def augment(i: int, seen: set[int]) -> bool:
        for j in edges[i]:
            if j not in seen:
                seen.add(j)
                if j not in owner or augment(owner[j], seen):
                    owner[j] = i
                    return True
        return False

    order = sorted(range(len(reference)), key=lambda i: reference[i]["tier"] != "core")
    for i in order:
        augment(i, set())
    return sorted((i, j) for j, i in owner.items())


def _attributes(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": finding["measurement"]["kind"],
        "scope": finding["event"]["scope"],
        "counted_unit": finding["counted_unit"],
        "status": finding["status"],
        "phase": finding["time"]["phase"],
        "restriction_stated": "restriction" in finding,
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def score(
    letters: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Each letter: ``note``, ``reference`` findings and ``predicted`` findings or None.

    ``predicted`` is None for an unusable response; its reference findings count as
    misses and it contributes no predictions.
    """
    totals: Counter[str] = Counter()
    agreement: Counter[str] = Counter()
    by_phase: Counter[str] = Counter()
    predicted_kinds: Counter[str] = Counter()
    per_letter = []
    for letter in letters:
        reference = letter["reference"]
        predicted = letter["predicted"]
        pairs = match_letter(letter["note"], predicted, reference) if predicted else []
        matched = {i for i, _ in pairs}
        totals["letters"] += 1
        totals["usable"] += predicted is not None
        totals["predicted"] += len(predicted or [])
        totals["matched_predicted"] += len(pairs)
        for i, finding in enumerate(reference):
            tier, phase = finding["tier"], finding["time"]["phase"]
            totals[f"{tier}_reference"] += 1
            totals[f"{tier}_matched"] += i in matched
            by_phase[f"{tier}:{phase}:reference"] += 1
            by_phase[f"{tier}:{phase}:matched"] += i in matched
        for finding in predicted or []:
            predicted_kinds[f"{finding['measurement']['kind']}:{finding['time']['phase']}"] += 1
        for i, j in pairs:
            ref, pred = _attributes(reference[i]), _attributes((predicted or [])[j])
            for name in ATTRIBUTES:
                agreement[name] += ref[name] == pred[name]
        per_letter.append(
            {
                "source_row_index": letter["source_row_index"],
                "usable": predicted is not None,
                "pairs": pairs,
                "reference": len(reference),
                "predicted": len(predicted or []),
            }
        )
    core, supporting = totals["core_reference"], totals["supporting_reference"]
    matched_reference = totals["core_matched"] + totals["supporting_matched"]
    summary = {
        "scorer": SCORER,
        "letters": totals["letters"],
        "usable_responses": totals["usable"],
        "predicted_findings": totals["predicted"],
        "reference_findings": {"core": core, "supporting": supporting},
        "precision": _ratio(totals["matched_predicted"], totals["predicted"]),
        "recall_core": _ratio(totals["core_matched"], core),
        "recall_all": _ratio(matched_reference, core + supporting),
        "counts": dict(totals),
        "recall_by_tier_and_phase": {
            key.removesuffix(":reference"): _ratio(by_phase[key.replace("reference", "matched")], n)
            for key, n in sorted(by_phase.items())
            if key.endswith(":reference")
        },
        "matched_pair_attribute_agreement": {
            name: _ratio(agreement[name], totals["matched_predicted"]) for name in ATTRIBUTES
        },
        "predicted_kind_by_phase": dict(sorted(predicted_kinds.items())),
    }
    return summary, per_letter
