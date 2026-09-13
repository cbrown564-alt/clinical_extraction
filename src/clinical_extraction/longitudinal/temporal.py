"""Inclusive query windows; uncertainty is retained in the input assertions."""

from __future__ import annotations

from datetime import date, timedelta

from .evidence import Record, wording


def bounds(value: Record | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    start = value.get("start") or {}
    end = value.get("end") or {}
    if value["kind"] in ("as_of", "decision", "result_available", "occurrence") and not end:
        end = start
    return start.get("earliest"), end.get("latest")


def before(value: Record | None, last: str) -> bool:
    _, end = bounds(value)
    return bool(end and end <= last)


def within(value: Record | None, first: str, last: str) -> bool:
    if not value:
        return False
    if value["kind"] == "occurrence":
        start, end = bounds(value)
        return bool(start and end and first <= start <= end <= last)
    if value["kind"] == "active_interval":
        start = (value.get("start") or {}).get("latest")
        end = (value.get("end") or {}).get("earliest")
        return bool(start and end and start <= end and start <= last and end >= first)
    return False


def interval(value: Record | None) -> tuple[str, str] | None:
    if not value or value["kind"] != "active_interval":
        return None
    start = (value.get("start") or {}).get("latest")
    end = (value.get("end") or {}).get("earliest")
    return (start, end) if start and end and start <= end else None


def covers(value: Record | None, first: str, last: str) -> bool:
    pair = interval(value)
    return bool(pair and pair[0] <= first <= last <= pair[1])


def union_covers(values: list[Record], first: str, last: str) -> bool:
    """Adjacent inclusive days join; even one missing day prevents a negative."""
    cursor = date.fromisoformat(first)
    for start, end in sorted(pair for a in values if (pair := interval(a.get("time")))):
        if date.fromisoformat(start) > cursor:
            break
        cursor = max(cursor, date.fromisoformat(end) + timedelta(days=1))
        if cursor > date.fromisoformat(last):
            return True
    return False


def holiday_inside(a: Record, documents: Record, first: str, last: str) -> bool:
    """Qualitative inclusion only: require the entire Christmas season well inside.

    December through January is a conservative query envelope, never an assigned
    event date. Unanchored, ambiguous-year and boundary cases remain unknown.
    """
    t = a.get("time") or {}
    text = (t.get("text") or "").casefold()
    if t.get("kind") != "occurrence" or text != "sometime around christmas":
        return False
    anchor = documents.get(t.get("anchor_letter_id") or "")
    if not anchor:
        return False
    visit = date.fromisoformat(anchor["visit_date"])
    if visit.month not in (1, 2, 3):
        return False
    return first <= f"{visit.year - 1}-12-01" and f"{visit.year}-01-31" <= last


def history_scope(a: Record, documents: Record, first: str, last: str) -> str | None:
    """Explicit inventory history wording, separate from positive event timing.

    As-of inventories alone never establish coverage. These bounded development
    rules require a complete inventory plus its historical scope in the quotation.
    """
    if covers(a.get("time"), first, last):
        return "bounded-inventory"
    text = wording(a)
    visit = documents[a["letter_id"]]["visit_date"]
    if last > visit:
        return None
    if "over the past year" in text and "no other event types" in text:
        year_start = (date.fromisoformat(visit) - timedelta(days=365)).isoformat()
        if first >= year_start:
            return "inventory-past-year"
    if (
        "recurring" in text
        and "autumn" in text
        and "christmas" in text
        and "no other seizure patterns" in text
        and date.fromisoformat(visit).month in (1, 2, 3)
        and first >= f"{date.fromisoformat(visit).year - 1}-11-01"
    ):
        return "inventory-recurring-autumn-history"
    # Negative scope of "only ... since November" is a calendar scope; it is
    # distinct from the uncertain day on which the first event occurred.
    t = a.get("time") or {}
    start, end = t.get("start") or {}, t.get("end") or {}
    if (
        "only" in text
        and "since november" in text
        and start.get("earliest", "9999") <= first
        and first[:7] == str(start.get("earliest", ""))[:7]
        and end.get("earliest", "") >= last
    ):
        return "inventory-calendar-scope"
    return None
