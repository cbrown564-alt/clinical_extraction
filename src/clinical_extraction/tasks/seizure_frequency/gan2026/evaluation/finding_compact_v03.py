"""Strict, source-grounded matching for compact primary seizure findings.

The v0.3 source annotation owns which claims belong in the inventory. This
scorer compares emitted claims without selecting, repairing or deriving them.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as old_match,
)

VERSION = "finding_compact_v03_v2"
COMPONENTS = (
    "event",
    "counted_unit",
    "status",
    "measurement_kind",
    "measurement_value",
    "phase",
    "window",
    "restriction",
)


def text_key(value: str | None) -> str:
    return old_match.norm_text(value)


def event_key(event: dict[str, Any]) -> tuple[str, str]:
    """Use only explicit lexical aliases; preserve the declared population scope."""
    label = text_key(event["label"]).replace("generalized", "generalised")
    label = re.sub(r"\bgtcs?\b", "generalised tonic clonic seizure", label)
    label = re.sub(r"\bseizures\b", "seizure", label)
    label = re.sub(r"\bauras\b", "aura", label)
    label = re.sub(r"\bclusters\b", "cluster", label)
    label = re.sub(r"\bconvulsions\b", "convulsion", label)
    label = re.sub(r"\bepisodes\b", "episode", label)
    return event["scope"], label


def phrase_equal(a: str | None, b: str | None) -> bool:
    def key(value: str | None) -> str:
        text = text_key(value)
        return re.sub(r"^(?:on|in|since|for|over) (?:the )?", "", text)

    x, y = key(a), key(b)
    return bool(x and y) and x == y


def quantity_equal(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if a["kind"] != b["kind"]:
        return False
    kind = a["kind"]
    if kind == "number":
        return a["value"] == b["value"]
    if kind == "range":
        return a["lower"] == b["lower"] and a["upper"] == b["upper"]
    if kind == "bound":
        av, bv = a["value"], b["value"]
        values_equal = (
            quantity_equal(av, bv)
            if isinstance(av, dict) and isinstance(bv, dict)
            else av == bv and not isinstance(av, dict) and not isinstance(bv, dict)
        )
        return a["relation"] == b["relation"] and values_equal
    if kind == "verbatim":
        return text_key(a["text"]) == text_key(b["text"])
    raise ValueError(f"Unexpected quantity kind: {kind}")


def duration_equal(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if a["kind"] != b["kind"]:
        return False
    if a["kind"] == "verbatim":
        return text_key(a["text"]) == text_key(b["text"])
    return a["unit"] == b["unit"] and quantity_equal(
        {key: value for key, value in a.items() if key != "unit"},
        {key: value for key, value in b.items() if key != "unit"},
    )


def measurement_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if a["kind"] != b["kind"]:
        return False
    kind = a["kind"]
    if kind == "rate":
        return quantity_equal(a["quantity"], b["quantity"]) and duration_equal(
            a["per"], b["per"]
        )
    if kind == "observed_count":
        return quantity_equal(a["quantity"], b["quantity"])
    if kind == "cluster":
        return (
            quantity_equal(a.get("count"), b.get("count"))
            and (
                (a.get("cadence") is None and b.get("cadence") is None)
                or (
                    a.get("cadence") is not None
                    and b.get("cadence") is not None
                    and measurement_equal(a["cadence"], b["cadence"])
                )
            )
            and quantity_equal(a.get("seizures_per_cluster"), b.get("seizures_per_cluster"))
        )
    if kind == "seizure_free":
        # When both sides state a duration, its co-stated anchor is context.
        if a.get("duration") is not None or b.get("duration") is not None:
            return duration_equal(a.get("duration"), b.get("duration"))
        return phrase_equal(a.get("since"), b.get("since"))
    if kind == "last_event":
        return phrase_equal(a["occurred_at"], b["occurred_at"])
    if kind == "qualitative":
        return a["level"] == b["level"]
    if kind == "median_interval":
        return duration_equal(a["duration"], b["duration"])
    raise ValueError(f"Unexpected measurement kind: {kind}")


def evidence_overlap(note: str, a: list[str], b: list[str]) -> bool:
    return any(
        old_match.evidence_overlap(note, left, right)
        for left in a
        for right in b
    )


def attribute_diffs(pred: dict[str, Any], ref: dict[str, Any], note: str) -> list[str]:
    diffs = []
    if event_key(pred["event"]) != event_key(ref["event"]):
        diffs.append("event")
    if pred["counted_unit"] != ref["counted_unit"]:
        diffs.append("counted_unit")
    if pred["status"] != ref["status"]:
        diffs.append("status")
    if pred["time"]["phase"] != ref["time"]["phase"]:
        diffs.append("phase")
    if pred["measurement"]["kind"] != ref["measurement"]["kind"]:
        diffs.append("measurement_kind")
    elif not measurement_equal(pred["measurement"], ref["measurement"]):
        diffs.append("measurement_value")
    if pred.get("restriction") is None or ref.get("restriction") is None:
        if pred.get("restriction") != ref.get("restriction"):
            diffs.append("restriction")
    elif text_key(pred["restriction"]) != text_key(ref["restriction"]):
        diffs.append("restriction")
    if pred["time"].get("source") is None or ref["time"].get("source") is None:
        if pred["time"].get("source") != ref["time"].get("source"):
            diffs.append("window")
    elif not phrase_equal(pred["time"]["source"], ref["time"]["source"]):
        diffs.append("window")
    if not evidence_overlap(note, pred["evidence"], ref["evidence"]):
        diffs.append("evidence")
    return diffs


def component_agreement(pred: dict[str, Any], ref: dict[str, Any], note: str) -> dict[str, bool]:
    differences = set(attribute_diffs(pred, ref, note))
    agreement = {name: name not in differences for name in COMPONENTS}
    if not agreement["measurement_kind"]:
        agreement["measurement_value"] = False
    return agreement


def residual_source_pairs(
    note: str,
    reference: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    used_pred: set[int],
    used_ref: set[int],
) -> list[tuple[int, int]]:
    """Maximise evidence-aligned pairs, then the number of agreeing components."""
    remaining_pred = [i for i in range(len(predictions)) if i not in used_pred]
    remaining_ref = [j for j in range(len(reference)) if j not in used_ref]
    if len(remaining_ref) > 20:
        raise ValueError("Residual alignment exceeds the compact reference size limit")
    edges: dict[int, list[tuple[int, int]]] = {}
    for pi in remaining_pred:
        for bit, ri in enumerate(remaining_ref):
            if evidence_overlap(note, predictions[pi]["evidence"], reference[ri]["evidence"]):
                agreement = component_agreement(predictions[pi], reference[ri], note)
                edges.setdefault(pi, []).append((bit, sum(agreement.values())))

    @lru_cache(None)
    def solve(position: int, used: int) -> tuple[int, int, tuple[tuple[int, int], ...]]:
        if position == len(remaining_pred):
            return 0, 0, ()
        best = solve(position + 1, used)
        for bit, agreements in edges.get(remaining_pred[position], []):
            if used & (1 << bit):
                continue
            count, components, pairs = solve(position + 1, used | (1 << bit))
            option = (
                count + 1,
                components + agreements,
                ((remaining_pred[position], remaining_ref[bit]), *pairs),
            )
            if option[:2] > best[:2]:
                best = option
        return best

    return list(solve(0, 0)[2])


def score_letter(
    note: str,
    reference: list[dict[str, Any]],
    predictions: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Maximum one-to-one match; None is an unusable response."""
    if predictions is None:
        return {
            "usable": False,
            "reference": len(reference),
            "predicted": None,
            "tp": 0,
            "fp": 0,
            "fn": len(reference),
            "pairs": [],
            "source_aligned_pairs": [],
        }
    edges = {
        i: [j for j, ref in enumerate(reference) if not attribute_diffs(pred, ref, note)]
        for i, pred in enumerate(predictions)
    }
    matched = old_match.maximum_matching(edges, len(predictions))
    source_pairs = sorted(
        [*matched.items(), *residual_source_pairs(
            note, reference, predictions, set(matched), set(matched.values())
        )]
    )
    return {
        "usable": True,
        "reference": len(reference),
        "predicted": len(predictions),
        "tp": len(matched),
        "fp": len(predictions) - len(matched),
        "fn": len(reference) - len(matched),
        "pairs": [[i, j] for i, j in sorted(matched.items())],
        "source_aligned_pairs": [
            {
                "prediction_index": i,
                "reference_index": j,
                "components": component_agreement(predictions[i], reference[j], note),
                "whole_claim": i in matched,
            }
            for i, j in source_pairs
        ],
    }


def aggregate(scores: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(score["tp"] for score in scores)
    fp = sum(score["fp"] for score in scores)
    fn = sum(score["fn"] for score in scores)
    result = {
        "scorer": VERSION,
        "letters": len(scores),
        "usable_letters": sum(score["usable"] for score in scores),
        "unusable_letters": sum(not score["usable"] for score in scores),
        "reference_findings": sum(score["reference"] for score in scores),
        "predicted_findings_usable": sum(score["predicted"] or 0 for score in scores),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        "exact_inventory": sum(
            score["usable"] and score["fp"] == score["fn"] == 0 for score in scores
        ),
    }
    aligned = sum(len(score["source_aligned_pairs"]) for score in scores)
    result["source_aligned"] = {
        "tp": aligned,
        "fp": result["predicted_findings_usable"] - aligned,
        "fn": result["reference_findings"] - aligned,
        "precision": aligned / result["predicted_findings_usable"]
        if result["predicted_findings_usable"]
        else None,
        "recall": aligned / result["reference_findings"]
        if result["reference_findings"]
        else None,
    }
    result["components"] = {}
    for component in COMPONENTS:
        correct = sum(
            pair["components"][component]
            for score in scores
            for pair in score["source_aligned_pairs"]
        )
        result["components"][component] = {
            "correct_aligned": correct,
            "aligned_pairs": aligned,
            "tp": correct,
            "fp": result["predicted_findings_usable"] - correct,
            "fn": result["reference_findings"] - correct,
            "precision": correct / result["predicted_findings_usable"]
            if result["predicted_findings_usable"]
            else None,
            "recall": correct / result["reference_findings"]
            if result["reference_findings"]
            else None,
            "agreement_on_aligned": correct / aligned if aligned else None,
        }
    return result
