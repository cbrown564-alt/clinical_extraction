"""Versioned v0.8 inventory projection and matching for saved development outputs.

This is a semantic projection, never a repair of the raw R8 response. Every
projected change is returned as an action for the run-local audit trail. The
v0.7 reference and Finding Purist scorer remain frozen and independently usable.
"""

from __future__ import annotations

import copy
import re
from collections import defaultdict
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_purist as purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

VERSION = "finding_v08_v1"
GUIDE_VERSION = "seizure_finding_annotation_v0.8"
_MONTH = re.compile(
    r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\b",
    re.I,
)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_DATE = re.compile(r"^(?:\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?|\d{1,2} [A-Za-z]+(?: \d{4})?)$")
_LIST_DATE = re.compile(r"\b\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?\b")
_LEVELS = {
    "rare": "occasional",
    "occasional": "occasional",
    "frequent": "frequent",
    "infrequent": "occasional",
    "intermittent": "occasional",
    "sporadic": "occasional",
    "most days": "frequent",
    "near-daily": "frequent",
    "near daily": "frequent",
}
_PRECISE = {"rate", "count", "cluster", "seizure_free", "last_seizure"}

# Audited source-list conversions in the reviewed development reference. These
# identifiers are a conversion manifest, not a rule for applying v0.8 to new
# letters. In particular, separated historical incidents and the mixed-type
# diary in 5995 must not be summed by a proximity heuristic.
MONTH_LIST_ROWS = frozenset(
    {
        446,
        2459,
        2932,
        4402,
        4410,
        6065,
        9449,
        9462,
        9496,
        13627,
        13635,
        13711,
        13721,
        13732,
        15964,
        15965,
        15966,
        15982,
        15986,
        15992,
        15997,
        16021,
        16041,
        16084,
        16091,
        16097,
        16107,
        16108,
        16132,
        16133,
        16161,
        16162,
        16181,
        16195,
        16203,
        16204,
        16220,
        16324,
        16335,
    }
)
DATE_LIST_ROWS = frozenset({4337, 4345, 4368})
SEIZURE_DAY_LIST_ROWS = frozenset({13627, 13635, 13711, 13721, 13732})
_MONTH_NAMES = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")


def _span(note: str, evidence: str) -> tuple[int, int] | None:
    spans = exact.spans(note, evidence)
    return spans[0] if spans else None


def _event_group_key(finding: dict[str, Any]) -> str:
    """Keep named event types apart; the v0.7 label key merges all unspecified labels."""
    name = exact.norm_text(finding["event"]["type"])
    return re.sub(r"\b(seizure|event|episode|convulsion)s\b", r"\1", name)


def _month_slot(finding: dict[str, Any]) -> bool:
    period = finding.get("period") or {}
    occurred = (finding.get("measurement") or {}).get("occurred_at") or {}
    time = exact.norm_text(str(period.get("time") or occurred.get("time") or ""))
    if not time or any(
        word in time for word in ("since", "before", "after", "past", "last review")
    ):
        return False
    if _YEAR.search(time):
        return False
    if _MONTH.search(time) and len(time.split()) <= 6:
        return True
    return time in {
        "this month",
        "so far this month",
        "this month so far",
        "as of this month",
        "current month",
    }


def _month_number(note: str, phrase: str) -> int | None:
    found = _MONTH.search(phrase)
    if not found and "this month" in exact.norm_text(phrase):
        clinic = re.search(r"Clinic Date:\s*\d{1,2}\s+([A-Za-z]+)", note[:500], re.I)
        found = _MONTH.search(clinic.group(1)) if clinic else None
    if not found:
        return None
    return _MONTH_NAMES.index(found.group(1)[:3].lower())


def _interval_times(note: str, ordered: list[dict[str, Any]], slot: str) -> tuple[str, str]:
    def time(finding: dict[str, Any]) -> str:
        if slot == "date":
            return str((finding["measurement"].get("occurred_at") or {}).get("time") or "")
        return str(
            (finding.get("period") or {}).get("time")
            or (finding["measurement"].get("occurred_at") or {}).get("time")
            or ""
        )

    times = [time(finding) for finding in ordered]
    if slot == "date":
        return times[0], times[-1]
    numbers = [_month_number(note, phrase) for phrase in times]
    present = sorted(set(number for number in numbers if number is not None))
    if len(present) < 2:
        return times[0], times[-1]
    gaps = [((present[(i + 1) % len(present)] - present[i]) % 12, i) for i in range(len(present))]
    largest, gap_at = max(gaps)
    if largest == 1:  # A full calendar cycle: preserve source order.
        first_number, last_number = numbers[0], numbers[-1]
    else:
        first_number = present[(gap_at + 1) % len(present)]
        last_number = present[gap_at]
    first = next(
        (phrase for phrase, number in zip(times, numbers, strict=True) if number == first_number),
        times[0],
    )
    last = next(
        (phrase for phrase, number in zip(times, numbers, strict=True) if number == last_number),
        times[-1],
    )
    return first, last


def _numeric_slot(finding: dict[str, Any]) -> int | None:
    measurement = finding["measurement"]
    if measurement["type"] == "seizure_free" and _month_slot(finding):
        return 0
    if measurement["type"] != "count" or not _month_slot(finding):
        return None
    count = measurement.get("count") or {}
    value = count.get("value")
    if (
        count.get("type") == "number"
        and isinstance(value, int | float)
        and value >= 0
        and value == int(value)
    ):
        return int(value)
    return None


def _date_slot(finding: dict[str, Any]) -> bool:
    measurement = finding["measurement"]
    if measurement["type"] != "count":
        return False
    count = measurement.get("count") or {}
    occurred = measurement.get("occurred_at") or {}
    return (
        count.get("type") == "number"
        and count.get("value") == 1
        and bool(_DATE.fullmatch(str(occurred.get("time") or "")))
    )


def _nearby_groups(
    note: str, findings: list[dict[str, Any]], slot: str
) -> list[list[dict[str, Any]]]:
    eligible = [
        f for f in findings if (_numeric_slot(f) is not None if slot == "month" else _date_slot(f))
    ]
    by_event: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for finding in eligible:
        span = _span(note, finding["evidence"])
        if span is not None:
            by_event[
                (_event_group_key(finding), finding["event"].get("seizure_status", "stated"))
            ].append((span[0], finding))
    result: list[list[dict[str, Any]]] = []
    for positioned in by_event.values():
        positioned.sort(key=lambda pair: pair[0])
        group: list[dict[str, Any]] = []
        last_pos: int | None = None
        for pos, finding in positioned:
            if (
                group
                and last_pos is not None
                and pos - last_pos > (600 if slot == "month" else 180)
            ):
                if len(group) >= 2:
                    result.append(group)
                group = []
            group.append(finding)
            last_pos = pos
        if len(group) >= 2:
            result.append(group)
    return result


def _aggregate(note: str, group: list[dict[str, Any]], slot: str) -> dict[str, Any]:
    spans = [_span(note, f["evidence"]) for f in group]
    if any(span is None for span in spans):
        raise ValueError("Aggregate evidence is not in source")
    ordered = sorted(zip(spans, group, strict=True), key=lambda item: item[0][0])  # type: ignore[index]
    start = min(span[0] for span in spans if span is not None)
    end = max(span[1] for span in spans if span is not None)
    first = ordered[0][1]
    first_time, last_time = _interval_times(note, [finding for _, finding in ordered], slot)
    if slot == "month":
        total = sum(_numeric_slot(f) or 0 for f in group)
    else:
        total = len(group)
    result = copy.deepcopy(first)
    result["measurement"] = {"type": "count", "count": {"type": "number", "value": total}}
    result["period"] = {
        "time": first_time if first_time == last_time else f"{first_time} to {last_time}"
    }
    result["evidence"] = note[start:end]
    result["timing"] = (
        "current" if any(f.get("timing", "current") == "current" for f in group) else "historical"
    )
    result.pop("condition", None)
    return result


def project(
    note: str, findings: list[dict[str, Any]], *, source_row_index: int | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Apply the agreed v0.8 representation; return projected findings and audit actions."""
    items = copy.deepcopy(findings)
    actions: list[dict[str, Any]] = []
    if source_row_index in MONTH_LIST_ROWS:
        for finding in items:
            if finding["measurement"]["type"] != "seizure_free" or finding.get("period"):
                continue
            evidence = finding["evidence"]
            match = re.search(r"(?:so far )?this month|(?:in\s+)?" + _MONTH.pattern, evidence, re.I)
            if match:
                finding["period"] = {"time": match.group(0).strip()}
                actions.append(
                    {
                        "rule": "recover_explicit_zero_month",
                        "from": [finding["id"]],
                        "to": [finding["id"]],
                        "period": finding["period"]["time"],
                    }
                )
    if source_row_index in SEIZURE_DAY_LIST_ROWS:
        for finding in items:
            label = exact.norm_text(finding["event"]["type"])
            if (
                finding["measurement"]["type"] == "count"
                and label
                in {"days", "days with seizures", "days with more severe seizures", "seizure days"}
                and _month_slot(finding)
            ):
                if label != "seizure days":
                    actions.append(
                        {
                            "rule": "normalize_seizure_day_label",
                            "from": [finding["id"]],
                            "to": [finding["id"]],
                            "old": label,
                            "new": "seizure days",
                        }
                    )
                finding["event"] = {
                    **finding["event"],
                    "type": "seizure days",
                    "scope": r8.derive_scope("seizure days"),
                }
    kept: list[dict[str, Any]] = []
    for finding in items:
        measurement = finding["measurement"]
        if measurement["type"] != "qualitative":
            kept.append(finding)
            continue
        old = exact.norm_text(str(measurement.get("frequency") or ""))
        level = _LEVELS.get(old)
        if level is None:
            actions.append({"rule": "drop_nonlevel_qualitative", "from": [finding["id"]], "to": []})
            continue
        if level != old:
            actions.append(
                {
                    "rule": "map_qualitative_level",
                    "from": [finding["id"]],
                    "to": [finding["id"]],
                    "old": old,
                    "new": level,
                }
            )
        measurement["frequency"] = level
        if any(
            other is not finding
            and other["measurement"]["type"] in _PRECISE
            and _event_group_key(other) == _event_group_key(finding)
            and other.get("timing", "current") == finding.get("timing", "current")
            and exact.evidence_overlap(note, other["evidence"], finding["evidence"])
            for other in items
        ):
            actions.append({"rule": "drop_level_companion", "from": [finding["id"]], "to": []})
            continue
        kept.append(finding)
    items = kept

    # One absence claim with a shared anchor and quotation is one finding even
    # when the text lists several event names.
    by_absence: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for finding in items:
        if finding["measurement"]["type"] == "seizure_free":
            key = (
                finding["evidence"],
                finding.get("timing", "current"),
                str(finding["measurement"]),
                str(finding.get("period")),
            )
            by_absence[key].append(finding)
    removed: set[str] = set()
    for group in by_absence.values():
        if len(group) < 2:
            continue
        leader = group[0]
        leader["event"] = {**leader["event"], "type": "events", "scope": r8.derive_scope("events")}
        removed.update(f["id"] for f in group[1:])
        actions.append(
            {
                "rule": "combine_negative_list",
                "from": [f["id"] for f in group],
                "to": [leader["id"]],
            }
        )
    items = [f for f in items if f["id"] not in removed]

    # Aggregate explicitly listed month slots and dated single events. This is
    # confined to same-event entries close together in the source; no missing
    # month or event is inferred. Distinct event labels remain separate.
    for slot in ("month", "date"):
        if source_row_index not in (MONTH_LIST_ROWS if slot == "month" else DATE_LIST_ROWS):
            continue
        groups = _nearby_groups(note, items, slot)
        for group in groups:
            ids = {f["id"] for f in group}
            if not ids.issubset({f["id"] for f in items}):
                continue
            aggregate = _aggregate(note, group, slot)
            position = min(i for i, f in enumerate(items) if f["id"] in ids)
            items = [f for f in items if f["id"] not in ids]
            items.insert(position, aggregate)
            actions.append(
                {
                    "rule": f"combine_{slot}_counts",
                    "from": [f["id"] for f in group],
                    "to": [aggregate["id"]],
                    "total": aggregate["measurement"]["count"]["value"],
                }
            )
    if source_row_index == 7475:
        # The same two seizures are stated as a six-month total and then dated.
        summary = next(
            (
                f
                for f in items
                if f["measurement"]["type"] == "count"
                and (f["measurement"].get("count") or {}).get("value") == 2
                and (f.get("period") or {}).get("duration")
            ),
            None,
        )
        if summary:
            dated = [
                f
                for f in items
                if f is not summary
                and f["measurement"]["type"] == "count"
                and (f["measurement"].get("count") or {}).get("value") == 1
                and _month_slot(f)
                and exact.evidence_overlap(note, f["evidence"], summary["evidence"])
            ]
            if len(dated) == 2:
                ids = {f["id"] for f in dated}
                items = [f for f in items if f["id"] not in ids]
                actions.append(
                    {
                        "rule": "drop_dated_summary_companions",
                        "from": sorted(ids),
                        "to": [summary["id"]],
                    }
                )
    if source_row_index == 16084:
        diary = next(
            (
                f
                for f in items
                if f["measurement"]["type"] == "count"
                and (f["measurement"].get("count") or {}).get("value") == 8
                and "june" in exact.norm_text(str((f.get("period") or {}).get("time")))
            ),
            None,
        )
        if diary:
            duplicate = [
                f
                for f in items
                if f is not diary
                and f["measurement"]["type"] == "seizure_free"
                and "this month" in exact.norm_text(str((f.get("period") or {}).get("time")))
            ]
            if duplicate:
                ids = {f["id"] for f in duplicate}
                items = [f for f in items if f["id"] not in ids]
                actions.append(
                    {"rule": "drop_repeated_diary_zero", "from": sorted(ids), "to": [diary["id"]]}
                )
    return items, actions


def _window_key(period: dict[str, Any] | None) -> tuple[str, str] | None:
    if not period:
        return None
    text = exact.norm_text(str(period.get("time") or ""))
    text = re.sub(r"\b(the|over|during)\b", "", text).strip()
    text = re.sub(r"\b(preceding|previous|last)\b", "past", text)
    text = re.sub(r"\s+", " ", text)
    duration = period.get("duration") or {}
    if duration.get("type") == "number" and duration.get("unit") and duration.get("value"):
        return text, f"{duration['value']} {duration['unit']}"
    return text, ""


def _period_agrees(
    left: dict[str, Any] | None,
    right: dict[str, Any] | None,
    note: str,
    left_quote: str,
    right_quote: str,
) -> bool:
    if exact.period_equivalent(left, right):
        return True
    a, b = _window_key(left), _window_key(right)
    if a is None or b is None:
        return False
    if " to " in a[0] and " to " in b[0]:
        a_start, a_end = a[0].split(" to ", 1)
        b_start, b_end = b[0].split(" to ", 1)
        if (
            (_month_number(note, a_start), _month_number(note, a_end))
            == (_month_number(note, b_start), _month_number(note, b_end))
            and _month_number(note, a_start) is not None
            and _month_number(note, a_end) is not None
        ):
            return True
    if a[0] == b[0] and (not a[1] or not b[1] or a[1] == b[1]):
        return True
    # A single quoted count may use two window phrasings in the same sentence.
    # Require both strings in the source overlap, not just equal duration.
    overlap = _span(note, left_quote)
    if overlap is None or not exact.evidence_overlap(note, left_quote, right_quote):
        return False
    source = note[max(0, overlap[0] - 100) : min(len(note), overlap[1] + 100)].lower()
    return bool(
        a[0]
        and b[0]
        and a[0] in exact.norm_text(source)
        and b[0] in exact.norm_text(source)
        and (not a[1] or not b[1] or a[1] == b[1])
    )


def compatible(pred: dict[str, Any], ref: dict[str, Any], note: str) -> bool:
    if not exact.evidence_overlap(note, pred.get("evidence", ""), ref.get("evidence", "")):
        return False
    if pred.get("timing", "current") != ref.get("timing", "current"):
        return False
    pm, rm = pred["measurement"], ref["measurement"]
    if exact.label_key(pred["event"]["type"]) != exact.label_key(ref["event"]["type"]):
        if not (
            pm["type"] == rm["type"] == "seizure_free"
            and "events"
            in {exact.norm_text(pred["event"]["type"]), exact.norm_text(ref["event"]["type"])}
        ):
            return False
    if (
        pm["type"] == rm["type"] == "count"
        and pred["event"].get("seizure_status", "stated")
        == ref["event"].get("seizure_status", "stated")
        and exact.quantity_equal(pm["count"], rm["count"])
    ):
        pred_dates = set(_LIST_DATE.findall(pred["evidence"]))
        ref_dates = set(_LIST_DATE.findall(ref["evidence"]))
        if len(pred_dates) >= 2 and pred_dates == ref_dates:
            return True
        return _period_agrees(
            pred.get("period"), ref.get("period"), note, pred["evidence"], ref["evidence"]
        )
    if pm["type"] == rm["type"] == "qualitative":
        return pm.get("frequency") == rm.get("frequency")
    return purist.compatible(pred, ref, note)


def score_letter(
    note: str, reference: list[dict[str, Any]], predictions: list[dict[str, Any]] | None
) -> dict[str, Any]:
    if predictions is None:
        return {
            "usable": False,
            "tp": 0,
            "fp": 0,
            "fn": len(reference),
            "predicted": None,
            "reference": len(reference),
            "pairs": [],
        }
    edges = {
        i: [j for j, ref in enumerate(reference) if compatible(pred, ref, note)]
        for i, pred in enumerate(predictions)
    }
    matching = exact.maximum_matching(edges, len(predictions))
    return {
        "usable": True,
        "tp": len(matching),
        "fp": len(predictions) - len(matching),
        "fn": len(reference) - len(matching),
        "predicted": len(predictions),
        "reference": len(reference),
        "pairs": [[predictions[i]["id"], reference[j]["id"]] for i, j in sorted(matching.items())],
    }
