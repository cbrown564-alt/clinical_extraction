"""Project raw GLiNER2 output onto the one-call answer and finding shapes.

Raw output is saved unchanged; this module is the separable projection step. It
maps the model-facing answer label to its native Purist band, reads the evidence
span, and turns each ``seizure_frequency_finding`` record into a finding that
validates against the locked expanded schema. Missing optional attributes take the
annotation guide's stated defaults (``unspecified`` scope, ``stated`` status,
``individual_seizure`` or ``not_applicable`` unit, ``past_or_unclear`` phase), and
every default is counted. A record without an evidence span in the note, a
measurement kind, or a required qualitative level is dropped and counted.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

from clinical_extraction.tasks.seizure_frequency.gan2026.gliner import normalize, schema
from clinical_extraction.tasks.seizure_frequency.gan2026.one_call.prompts import EXPANDED_SCHEMA

PROJECTION = "gliner_projection_v1"
NOT_APPLICABLE_UNIT = {"seizure_free", "last_event", "median_interval"}
# Pragmatic is a coarsening of the Purist bands (shared cut at 1.1 per month).
PURIST_TO_PRAGMATIC = {
    "currently_no_seizure": "currently_no_seizure",
    "seizure_freq_unknown": "seizure_freq_unknown",
    "seizure_freq_1_per_yr": "seizure_infrequent",
    "seizure_freq_1_per_6mon": "seizure_infrequent",
    "seizure_freq_more1per6mon_less1mon": "seizure_infrequent",
    "seizure_freq_1_per_mon": "seizure_infrequent",
    "seizure_freq_more1mon_less1week": "seizure_frequent",
    "seizure_freq_1_per_week": "seizure_frequent",
    "seizure_freq_more1week_less1day": "seizure_frequent",
    "seizure_freq_1ormore_daily": "seizure_frequent",
}
_FINDING = Draft202012Validator({"$defs": EXPANDED_SCHEMA["$defs"], "$ref": "#/$defs/finding"})


def _span(value: Any) -> dict[str, Any] | None:
    """A GLiNER span record, or None. Choice fields have no offsets."""
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict) and isinstance(value.get("text"), str) and value["text"].strip():
        return value
    if isinstance(value, str) and value.strip():
        return {"text": value}
    return None


def _text(value: Any) -> str | None:
    span = _span(value)
    return span["text"].strip() if span else None


def answer(raw: dict[str, Any], note: str) -> dict[str, Any]:
    decided = raw.get(schema.ANSWER_TASK)
    label = decided.get("label") if isinstance(decided, dict) else decided
    purist = schema.LABEL_TO_PURIST.get(label) if isinstance(label, str) else None
    evidence = _span((raw.get("entities") or {}).get(schema.EVIDENCE_ENTITY))
    quote = evidence["text"] if evidence else None
    failure = None
    if purist is None:
        failure = "invalid_target_label"
    elif purist != "seizure_freq_unknown" and not quote:
        # Unknown merges Gan "unknown" (evidence required) and no-reference (null
        # evidence), so evidence can only be required for the other bands.
        failure = "absent_required_evidence"
    return {
        "label": label,
        "confidence": decided.get("confidence") if isinstance(decided, dict) else None,
        "categories": (
            {"purist": purist, "pragmatic": PURIST_TO_PRAGMATIC[purist]} if purist else None
        ),
        "evidence": quote,
        "evidence_span": (
            [evidence["start"], evidence["end"]] if evidence and "start" in evidence else None
        ),
        "evidence_exact": quote is not None and quote in note,
        "failure": failure,
    }


def _measurement(kind: str, record: dict[str, Any], evidence: str) -> dict[str, Any] | None:
    amount = normalize.quantity(_text(record.get("quantity")))
    per = normalize.duration(_text(record.get("per")))
    window_text = _text(record.get("window"))
    window = normalize.duration(window_text)
    fallback = {"kind": "verbatim", "text": evidence}
    if kind == "rate":
        return {"kind": kind, "quantity": amount or fallback, "per": per or window or fallback}
    if kind == "observed_count":
        return {"kind": kind, "quantity": amount or fallback}
    if kind == "median_interval":
        return {"kind": kind, "duration": per or window or fallback}
    if kind == "cluster":
        cluster: dict[str, Any] = {"kind": kind}
        if amount:
            cluster["count"] = amount
        per_cluster = normalize.quantity(_text(record.get("seizures_per_cluster")))
        if per_cluster:
            cluster["seizures_per_cluster"] = per_cluster
        if len(cluster) == 1:
            cluster["count"] = fallback
        return cluster
    if kind == "seizure_free":
        if window and window["kind"] != "verbatim":
            return {"kind": kind, "duration": window}
        return {"kind": kind, "since": window_text or evidence}
    if kind == "last_event":
        return {"kind": kind, "occurred_at": window_text or evidence}
    if kind == "qualitative":
        level = _text(record.get("level"))
        return {"kind": kind, "level": level} if level in ("occasional", "frequent") else None
    return None


def finding(record: dict[str, Any], note: str, tally: Counter[str]) -> dict[str, Any] | None:
    spans = [_text(record.get(name)) for name in ("evidence", "quantity", "per", "window")]
    evidence = [s for s in spans[:1] if s and s in note] or [
        s for s in spans[1:] if s and s in note
    ]
    if not evidence:
        tally["dropped_no_evidence"] += 1
        return None
    kind = _text(record.get("kind"))
    if kind not in schema.KINDS:
        tally["dropped_no_kind"] += 1
        return None
    measurement = _measurement(kind, record, evidence[0])
    if measurement is None:
        tally["dropped_no_level"] += 1
        return None

    def choice(name: str, allowed: list[str], default: str) -> str:
        value = _text(record.get(name))
        if value in allowed:
            return value
        tally[f"default_{name}"] += 1
        return default

    unit_default = "not_applicable" if kind in NOT_APPLICABLE_UNIT else "individual_seizure"
    result: dict[str, Any] = {
        "event": {
            "label": _text(record.get("event")) or evidence[0],
            "scope": choice("scope", schema.SCOPES, "unspecified"),
        },
        "counted_unit": choice("counted_unit", schema.COUNTED_UNITS, unit_default),
        "status": choice("status", schema.STATUSES, "stated"),
        "measurement": measurement,
        "time": {"phase": choice("phase", schema.PHASES, "past_or_unclear")},
        "evidence": evidence,
    }
    window = _text(record.get("window"))
    if window:
        result["time"]["source"] = window
    restriction = _text(record.get("restriction"))
    if restriction:
        result["restriction"] = restriction
    if any(True for _ in _FINDING.iter_errors(result)):
        tally["dropped_schema_invalid"] += 1
        return None
    tally["kept"] += 1
    return result


def findings(raw: dict[str, Any], note: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    tally: Counter[str] = Counter()
    records = raw.get(schema.FINDING) or []
    tally["records"] = len(records)
    projected = [f for r in records if (f := finding(r, note, tally)) is not None]
    return projected, dict(tally)


def claim_indices(
    answer_span: list[int] | None, projected: list[dict[str, Any]], note: str
) -> list[int]:
    """Findings whose evidence overlaps the answer evidence; a diagnostic link only."""
    if not answer_span:
        return []
    start, end = answer_span
    linked = []
    for i, item in enumerate(projected):
        for quote in item["evidence"]:
            at = note.find(quote)
            while at >= 0:
                if at < end and start < at + len(quote):
                    linked.append(i)
                    break
                at = note.find(quote, at + 1)
            if linked and linked[-1] == i:
                break
    return linked
