"""Finding correctness and completeness against a guide v0.7 reference.

Whole-match rule (frozen before any R8 evaluation): a prediction matches a reference
finding when the event label is equivalent, ``seizure_status`` and ``timing`` are
equal, the measurement is equal component by component, the period/date anchors are
equivalent and the evidence spans overlap in the source. ``condition`` is recorded,
not compared. ``event.scope`` is derived from the label on both sides, so it is
implied by label equivalence. Matching is maximum-cardinality one-to-one with stable
ID order; each prediction and reference contributes at most one true positive.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

MATCHING_VERSION = "finding_matching_v07_v1"
_WS = re.compile(r"\s+")
_DASH = re.compile(r"[‐‑‒–—―]")


def norm_text(value: str | None) -> str:
    if not value:
        return ""
    text = _DASH.sub("-", value).lower().strip()
    text = re.sub(r"[.,;:!?\"“”'’]+", " ", text)
    return _WS.sub(" ", text).strip()


def label_key(label: str) -> tuple[str, str]:
    """Scope plus the sorted lemmatised type words; unspecified labels share one key."""
    scope = r8.derive_scope(label)
    if scope == "unspecified":
        return ("unspecified", "")
    words = sorted({_lemma(w) for w in r8.TYPE_WORDS.findall(label)})
    return (scope, " ".join(words))


def _lemma(word: str) -> str:
    w = word.lower().replace("-", " ").replace("generalized", "generalised")
    w = {"auras": "aura", "absences": "absence", "jerks": "jerk", "spasms": "spasm"}.get(w, w)
    if w.endswith("s") and w not in {"status", "gtcs", "tcs"}:
        w = w[:-1]
    return {
        "gtc": "generalised tonic clonic",
        "tc": "tonic clonic",
        "gtcs": "generalised tonic clonic",
        "tcs": "tonic clonic",
    }.get(w, w)


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, int | float) else None


def quantity_equal(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if a.get("type") != b.get("type"):
        return False
    kind = a["type"]
    if kind == "number":
        return _number(a.get("value")) == _number(b.get("value"))
    if kind == "range":
        return _number(a.get("lower")) == _number(b.get("lower")) and _number(
            a.get("upper")
        ) == _number(b.get("upper"))
    if kind == "bound":
        if a.get("relation") != b.get("relation"):
            return False
        av, bv = a.get("value"), b.get("value")
        if isinstance(av, dict) or isinstance(bv, dict):
            return isinstance(av, dict) and isinstance(bv, dict) and quantity_equal(av, bv)
        return _number(av) == _number(bv)
    if kind == "qualitative":
        return norm_text(a.get("quantity")) == norm_text(b.get("quantity"))
    return False


def duration_equal(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return a.get("unit") == b.get("unit") and quantity_equal(
        {k: v for k, v in a.items() if k != "unit"}, {k: v for k, v in b.items() if k != "unit"}
    )


def time_equivalent(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    """Time points match when one normalised expression contains the other."""
    if a is None or b is None:
        return a is None and b is None
    x, y = norm_text(a.get("time")), norm_text(b.get("time"))
    return bool(x and y) and (x in y or y in x)


def period_equivalent(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if a.get("duration") is not None and b.get("duration") is not None:
        return duration_equal(a["duration"], b["duration"])
    return time_equivalent({"time": a.get("time")}, {"time": b.get("time")})


def measurement_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if a.get("type") != b.get("type"):
        return False
    kind = a["type"]
    if kind == "rate":
        return quantity_equal(a.get("count"), b.get("count")) and duration_equal(
            a.get("per"), b.get("per")
        )
    if kind == "count":
        return quantity_equal(a.get("count"), b.get("count")) and time_equivalent(
            a.get("occurred_at"), b.get("occurred_at")
        )
    if kind == "cluster":
        ra, rb = a.get("rate"), b.get("rate")
        rate_ok = (ra is None and rb is None) or (
            ra is not None
            and rb is not None
            and quantity_equal(ra.get("count"), rb.get("count"))
            and duration_equal(ra.get("per"), rb.get("per"))
        )
        return (
            rate_ok
            and quantity_equal(a.get("count"), b.get("count"))
            and quantity_equal(a.get("seizures_per_cluster"), b.get("seizures_per_cluster"))
            and time_equivalent(a.get("occurred_at"), b.get("occurred_at"))
        )
    if kind == "seizure_free":
        return duration_equal(a.get("duration"), b.get("duration")) and time_equivalent(
            a.get("since"), b.get("since")
        )
    if kind == "last_seizure":
        return time_equivalent(a.get("occurred_at"), b.get("occurred_at"))
    if kind == "qualitative":
        return a.get("frequency") == b.get("frequency")
    return False


def spans(note: str, quote: str) -> list[tuple[int, int]]:
    found = []
    start = note.find(quote)
    while start >= 0:
        found.append((start, start + len(quote)))
        start = note.find(quote, start + 1)
    return found


def evidence_overlap(note: str, a: str, b: str) -> bool:
    return any(x0 < y1 and y0 < x1 for x0, x1 in spans(note, a) for y0, y1 in spans(note, b))


def attribute_diffs(pred: dict[str, Any], ref: dict[str, Any], note: str) -> list[str]:
    diffs = []
    if label_key(pred["event"]["type"]) != label_key(ref["event"]["type"]):
        diffs.append("event")
    if pred["event"].get("seizure_status", "stated") != ref["event"].get(
        "seizure_status", "stated"
    ):
        diffs.append("seizure_status")
    if pred.get("timing", "current") != ref.get("timing", "current"):
        diffs.append("timing")
    if pred["measurement"].get("type") != ref["measurement"].get("type"):
        diffs.append("measurement_type")
    elif not measurement_equal(pred["measurement"], ref["measurement"]):
        diffs.append("measurement_value")
    if not period_equivalent(pred.get("period"), ref.get("period")):
        diffs.append("period")
    if not evidence_overlap(note, pred.get("evidence", ""), ref.get("evidence", "")):
        diffs.append("evidence")
    return diffs


def maximum_matching(edges: dict[int, list[int]], n_pred: int) -> dict[int, int]:
    """Augmenting-path maximum bipartite matching; deterministic in index order."""
    match_ref: dict[int, int] = {}

    def try_assign(p: int, seen: set[int]) -> bool:
        for r in edges.get(p, []):
            if r in seen:
                continue
            seen.add(r)
            if r not in match_ref or try_assign(match_ref[r], seen):
                match_ref[r] = p
                return True
        return False

    for p in range(n_pred):
        try_assign(p, set())
    return {p: r for r, p in match_ref.items()}


def score_letter(
    note: str, reference: list[dict[str, Any]], predictions: list[dict[str, Any]] | None
) -> dict[str, Any]:
    """TP/FP/FN and diagnostics for one letter; ``predictions=None`` means unusable output."""
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
            if not attribute_diffs(pred, ref, note):
                edges.setdefault(i, []).append(j)
    matched = maximum_matching(edges, len(predictions))
    tp = len(matched)
    diagnostics: list[dict[str, Any]] = []
    for i, pred in enumerate(predictions):
        if i in matched:
            continue
        best = min(
            (
                attribute_diffs(pred, ref, note)
                for j, ref in enumerate(reference)
                if j not in matched.values()
            ),
            key=len,
            default=["no_reference_candidate"],
        )
        diagnostics.append({"prediction": pred.get("id"), "closest_diffs": best})
    return {
        "usable": True,
        "tp": tp,
        "fp": len(predictions) - tp,
        "fn": len(reference) - tp,
        "predicted": len(predictions),
        "reference": len(reference),
        "pairs": [
            [predictions[i].get("id"), reference[j].get("id")] for i, j in sorted(matched.items())
        ],
        "unmatched_diagnostics": diagnostics,
    }


def aggregate(letters: list[dict[str, Any]]) -> dict[str, Any]:
    """Micro precision/recall/F1 over adjudicable letters plus inventory-level rates."""
    tp = sum(x["tp"] for x in letters)
    fp = sum(x["fp"] for x in letters)
    fn = sum(x["fn"] for x in letters)
    usable = [x for x in letters if x["usable"]]
    exact = sum(1 for x in usable if x["fp"] == 0 and x["fn"] == 0)
    empty_ref = [x for x in letters if x["reference"] == 0]
    empty_correct = sum(1 for x in empty_ref if x["usable"] and x["predicted"] == 0)
    diag: Counter[str] = Counter()
    for x in letters:
        for d in x["unmatched_diagnostics"]:
            for a in d["closest_diffs"]:
                diag[a] += 1

    def ratio(num: int, den: int) -> float | str:
        return num / den if den else "not estimable"

    return {
        "matching_version": MATCHING_VERSION,
        "letters": len(letters),
        "usable_letters": len(usable),
        "unusable_letters": len(letters) - len(usable),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "exact_inventory": exact,
        "exact_inventory_rate": ratio(exact, len(letters)),
        "empty_reference_letters": len(empty_ref),
        "empty_state_correct": empty_correct,
        "unmatched_prediction_diagnostics": dict(diag),
    }
