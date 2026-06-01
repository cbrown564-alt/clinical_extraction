from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

DAY_IN_YEAR = 365.0
DAYS_PER = {
    "day": 1.0,
    "week": 7.0,
    "month": 30.0,
    "year": 365.0,
}


class FrequencyLabelKind(StrEnum):
    FREQUENCY = "frequency"
    SEIZURE_FREE = "seizure_free"
    UNKNOWN = "unknown"
    NO_REFERENCE = "no_reference"
    UNRESOLVED_MULTIPLE = "unresolved_multiple"


@dataclass(frozen=True)
class FrequencyLabelRecord:
    raw_label: str
    normalized_label: str
    kind: FrequencyLabelKind
    yearly_bounds: tuple[float, float] | None
    monthly_frequency: float


def normalize_frequency_label(label: str) -> str:
    """Normalize label text before Gan-compatible parsing."""
    return " ".join(label.strip().lower().split())


def label_to_frequency_record(label: str) -> FrequencyLabelRecord:
    """Convert a normalized Gan label while retaining pre-scoring semantics."""
    normalized = normalize_frequency_label(label)
    if normalized == "unknown":
        return FrequencyLabelRecord(
            raw_label=label,
            normalized_label=normalized,
            kind=FrequencyLabelKind.UNKNOWN,
            yearly_bounds=None,
            monthly_frequency=1000.0,
        )
    if normalized == "no seizure frequency reference":
        return FrequencyLabelRecord(
            raw_label=label,
            normalized_label=normalized,
            kind=FrequencyLabelKind.NO_REFERENCE,
            yearly_bounds=None,
            monthly_frequency=1000.0,
        )

    scoring_label = normalized
    if "cluster" in scoring_label:
        if "unknown" in scoring_label:
            return FrequencyLabelRecord(
                raw_label=label,
                normalized_label=normalized,
                kind=FrequencyLabelKind.UNKNOWN,
                yearly_bounds=None,
                monthly_frequency=1000.0,
            )
        scoring_label = _expand_cluster_label(scoring_label)

    min_per_year, max_per_year = parse_label_bounds(scoring_label)
    if min_per_year == max_per_year == 0:
        kind = FrequencyLabelKind.SEIZURE_FREE
    elif min_per_year < 0 or max_per_year < 0:
        kind = _sentinel_kind(min_per_year, max_per_year)
    else:
        kind = FrequencyLabelKind.FREQUENCY

    monthly_frequency = (
        1000.0
        if min_per_year < 0 or max_per_year < 0
        else ((min_per_year + max_per_year) / 2) / 12
    )
    return FrequencyLabelRecord(
        raw_label=label,
        normalized_label=normalized,
        kind=kind,
        yearly_bounds=(min_per_year, max_per_year),
        monthly_frequency=monthly_frequency,
    )


def parse_label_bounds(label: str) -> tuple[float, float]:
    """Parse a Gan label into yearly lower and upper bounds.

    This follows the author CSV-preparation parser. It normalizes cluster labels by
    counting cluster events and dropping the trailing per-cluster detail.
    """
    if not isinstance(label, str):
        raise ValueError(f"label is not a string: {label!r}")

    raw = label
    normalized = _clean_label_for_bounds(label)

    if "seizure free" in normalized:
        return 0.0, 0.0
    if (
        "unknown" in normalized
        or normalized.startswith("multiple per")
        or " per multiple " in normalized
    ):
        return -1.0, -1.0
    if "no seizure frequency reference" in normalized:
        return -2.0, -2.0

    pattern = re.compile(
        r"^"
        r"(?P<n1>\d+(?:\.\d+)?)(?:\s*to\s*(?P<n2>\d+(?:\.\d+)?))?"
        r"\s+per\s+"
        r"(?:(?P<d1>\d+(?:\.\d+)?)(?:\s*to\s*(?P<d2>\d+(?:\.\d+)?))?\s+)?"
        r"(?P<period>day|week|month|year)s?"
        r"$",
        re.IGNORECASE,
    )
    match = pattern.match(normalized)
    if not match:
        normalized = normalized.replace(" or more per ", " per ")
        normalized = normalized.replace(" to multiple per ", " per ")
        match = pattern.match(normalized)
    if not match:
        raise ValueError(f"Unparsable label (raw: {raw!r} / normalized: {normalized!r})")

    n1, n2 = match.group("n1"), match.group("n2")
    d1, d2 = match.group("d1"), match.group("d2")
    period = match.group("period")

    n_min = _pick_min(n1, n2)
    n_max = _pick_max(n1, n2)
    d_min = _pick_min(d1, d2, default=1.0)
    d_max = _pick_max(d1, d2, default=1.0)
    days = DAYS_PER[period]

    min_per_year = n_min * DAY_IN_YEAR / (d_max * days)
    max_per_year = n_max * DAY_IN_YEAR / (d_min * days)
    return float(min_per_year), float(max_per_year)


def label_to_monthly_frequency(label: str) -> float:
    """Convert a Gan label to the monthly numeric value used by evaluation.

    The evaluation script uses the midpoint of yearly bounds divided by 12. Sentinel
    values for unknown and no-reference are both scored as the unknown category.
    """
    return label_to_frequency_record(label).monthly_frequency


def _sentinel_kind(min_per_year: float, max_per_year: float) -> FrequencyLabelKind:
    if min_per_year == max_per_year == -2.0:
        return FrequencyLabelKind.NO_REFERENCE
    if min_per_year == max_per_year == -1.0:
        return FrequencyLabelKind.UNRESOLVED_MULTIPLE
    return FrequencyLabelKind.UNKNOWN


def _clean_label_for_bounds(label: str) -> str:
    text = label
    for source, replacement in (
        (" or more cluster ", " cluster "),
        (" or more day,", " day,"),
        (" or more month,", " month,"),
        (" or more year,", " year,"),
    ):
        text = text.replace(source, replacement)

    normalized = normalize_frequency_label(text)
    normalized = re.sub(r",\s*[^,]*?\bper\s+cluster\b.*$", "", normalized)
    normalized = re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", normalized)
    normalized = re.sub(r"\bclusters?\b", "", normalized)
    return " ".join(normalized.split())


def _expand_cluster_label(label: str) -> str:
    normalized = label.replace("multiple per cluster", "2 per cluster")
    normalized = _replace_multiple_cluster_count(normalized)

    cluster_match = re.search(r"(\d+(?:\s*to\s*\d+)?)\s*clusters?\b", normalized)
    per_cluster_match = re.search(
        r"(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\b",
        normalized,
    )
    if not cluster_match or not per_cluster_match:
        raise ValueError(f"Unparsable cluster label: {label!r}")

    cluster_min, cluster_max = _parse_range(cluster_match.group(1))
    per_cluster_min, per_cluster_max = _parse_range(per_cluster_match.group(1))
    min_frequency = cluster_min * per_cluster_min
    max_frequency = cluster_max * per_cluster_max

    period_match = re.search(r"per\s+(.+?)(?:,|$)", normalized)
    period = period_match.group(1).strip() if period_match else "month"
    period = _normalize_period(period)

    frequency = (
        str(int(min_frequency))
        if min_frequency == max_frequency
        else f"{int(min_frequency)} to {int(max_frequency)}"
    )
    return f"{frequency} per {period}"


def _replace_multiple_cluster_count(label: str) -> str:
    if label.endswith("week") or "week," in label:
        return label.replace("multiple cluster per ", "2 cluster per ")
    if label.endswith("month") or "month," in label:
        return label.replace("multiple cluster per ", "8 cluster per ")
    if label.endswith("year") or "year," in label:
        return label.replace("multiple cluster per ", "18 cluster per ")
    if label.endswith("day") or "day," in label:
        return label.replace("multiple cluster per ", "2 cluster per ")
    return label


def _normalize_period(period: str) -> str:
    normalized = re.sub(r"\s*(?:-|–)\s*", " to ", period.strip().lower())
    normalized = " ".join(normalized.split())
    for unit in ("week", "day", "month", "year"):
        normalized = re.sub(rf"\b{unit}s\b", unit, normalized)
    return normalized


def _parse_range(token: str) -> tuple[int, int]:
    match = re.match(r"^(\d+)\s*(?:to|-|–)\s*(\d+)$", token.strip().lower())
    if match:
        left, right = int(match.group(1)), int(match.group(2))
        return min(left, right), max(left, right)
    match = re.match(r"^(\d+)$", token.strip().lower())
    if match:
        value = int(match.group(1))
        return value, value
    raise ValueError(f"Malformed range: {token!r}")


def _pick_min(left: str | None, right: str | None, default: float | None = None) -> float:
    if left is None and right is None:
        if default is None:
            raise ValueError("missing numeric bound")
        return default
    if left is None:
        assert right is not None
        return float(right)
    if right is None:
        return float(left)
    return min(float(left), float(right))


def _pick_max(left: str | None, right: str | None, default: float | None = None) -> float:
    if left is None and right is None:
        if default is None:
            raise ValueError("missing numeric bound")
        return default
    if left is None:
        assert right is not None
        return float(right)
    if right is None:
        return float(left)
    return max(float(left), float(right))
