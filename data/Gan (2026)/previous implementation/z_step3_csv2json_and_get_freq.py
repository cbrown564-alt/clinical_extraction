# -*- coding: utf-8 -*-
"""
Rule summary:
- Use upper bound to compute per_year (consistent with previous logic):
  * "2 to 4 per day"              -> 4 * 365
  * "2 to 4 per month"            -> 4 / 30 * 365
  * "2 to 4 per 2 to 4 month"     -> 4 / (2 * 30) * 365
  * "2 to 4 per week"             -> 4 / 7 * 365
  * "X per year"                  -> X
  * "1 cluster per month, 7 to 8 per cluster" / "1 cluster per 3 to 4 month, ...":
      Ignore everything after "per cluster"; count clusters only -> 1/30*365, 1/(3*30)*365 respectively
  * "seizure free" -> 0; "unknown" -> -1; "multiple per ..." -> -1
- Also compute lower bound min_per_year:
  * Symmetric to upper bound: numerator takes the minimum, denominator (if range) takes the maximum.
- Parse failure -> assert False
- month = 30 days, week = 7 days, year = 365 days
"""

import sys
import re
import pandas as pd
from collections import defaultdict

DAY_IN_YEAR = 365.0
DAYS_PER = {
    "day": 1.0,
    "week": 7.0,
    "month": 30.0,
    "year": 365.0
}

def clean_label(text: str) -> str:

    if " or more cluster " in text:
        text = text.replace(" or more cluster ", " cluster ")
    if " or more day," in text:
        text = text.replace(" or more day,", " day,")
    if " or more month," in text:
        text = text.replace(" or more month,", " month,")
    if " or more year," in text:
        text = text.replace(" or more year,", " year,")

    """Normalize label: lowercase, unify connectors, remove trailing 'per cluster' details."""
    s = (text or "").strip().lower()

    # Drop trailing ', ... per cluster ...' tail segment
    s = re.sub(r',\s*[^,]*?\bper\s+cluster\b.*$', '', s)

    # 2-4 / 2 – 4 / 2—4 -> "2 to 4"
    s = re.sub(r'(\d+)\s*[-–—]\s*(\d+)', r'\1 to \2', s)

    # Normalize multiple whitespaces
    s = re.sub(r'\s+', ' ', s)

    # Remove irrelevant words (do not affect counting units)
    # Do not remove 'per' and time-unit words
    s = re.sub(r'\b(clusters?)\b', '', s)  # '1 cluster per month' -> '1 per month'
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def _pick_max_num(a: str, b: str) -> float:
    """Upper bound of range; if b is missing, take a."""
    if b is None or b == '':
        return float(a)
    return max(float(a), float(b))

def _pick_min_num(a: str, b: str, default_if_both_none = None) -> float:
    """Lower bound of range; if a/b are both None, return default_if_both_none (used for denominator default 1)."""
    if a is None and b is None:
        if default_if_both_none is None:
            raise AssertionError("both numbers are None and no default provided")
        return float(default_if_both_none)
    if b is None or b == '':
        return float(a)
    return min(float(a), float(b))

def _pick_max_num_with_default(a: str, b: str, default_if_both_none: float) -> float:
    """Upper bound of range; if a/b are both None return default (used for denominator max default 1)."""
    if a is None and b is None:
        return float(default_if_both_none)
    if b is None or b == '':
        return float(a)
    return max(float(a), float(b))

def parse_label_bounds(label: str) -> tuple[float, float]:
    """
    Parse label and return (min_per_year, max_per_year).
    Raise AssertionError if parsing fails.
    """
    if not isinstance(label, str):
        raise AssertionError(f"label is not a string: {label!r}")

    raw = label
    s = clean_label(label)

    # 特例
    if "seizure free" in s:
        return 0.0, 0.0
    if "unknown" in s or s.startswith("multiple per"):
        return -1.0, -1.0
    if "no seizure frequency reference" in s:
        return -2.0, -2.0
    if " per multiple week" in s or " per multiple month" in s or " per multiple year" in s or " per multiple day" in s:
        return -1.0, -1.0

    DEC = r'(?:\d+(?:\.\d+)?)'  # Allow integers or decimals, e.g., 1, 1.5, 0.25

    pattern = re.compile(
        r'^'
        rf'(?P<n1>{DEC})(?:\s*to\s*(?P<n2>{DEC}))?'         # Numerator: n or n to m
        r'\s+per\s+'
        rf'(?:(?P<d1>{DEC})(?:\s*to\s*(?P<d2>{DEC}))?\s+)?' # Optional denominator: d or d to e
        r'(?P<period>day|week|month|year)s?'                # Unit
        r'$',
        re.IGNORECASE
    )

    m = pattern.match(s)
    if m:
        n1, n2 = m.group("n1"), m.group("n2")
        d1, d2 = m.group("d1"), m.group("d2")
        period = m.group("period")
        days = DAYS_PER[period]

        # Bounds
        n_min = _pick_min_num(n1, n2)                          # Numerator min
        n_max = _pick_max_num(n1, n2)                          # Numerator max
        d_min = _pick_min_num(d1, d2, default_if_both_none=1)  # Denominator min (default 1)
        d_max = _pick_max_num_with_default(d1, d2, 1)          # Denominator max (default 1)

        max_per_year = n_max * DAY_IN_YEAR / (d_min * days)    # Upper bound (backward-compatible)
        min_per_year = n_min * DAY_IN_YEAR / (d_max * days)    # Lower bound
        return float(min_per_year), float(max_per_year)
    
    if "or more per" in s:
        s = s.replace(" or more per ", " per ")
    if "to multiple per" in s:
        s = s.replace(" to multiple per ", " per ")

    # Fallback: X per <period> (no range)
    m2 = re.match(r'^(?P<n>\d+(?:\.\d+)?)\s+per\s+(?P<period>day|week|month|year)s?$',    s)
    if m2:
        n = float(m2.group("n"))
        days = DAYS_PER[m2.group("period")]
        val = n * DAY_IN_YEAR / days
        return float(val), float(val)

    raise AssertionError(f"Unparsable label (raw: {raw!r} / normalized: {s!r})")

def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "data/1to52.csv"
    # in_path = sys.argv[1] if len(sys.argv) > 1 else "data/1to52-v0.delete.csv"
    out_csv = sys.argv[2] if len(sys.argv) > 2 else "data/1to52-final.csv"
    out_json = sys.argv[3] if len(sys.argv) > 3 else "data/1to52-final.json"

    df = pd.read_csv(in_path, encoding="utf-8-sig")
    if "label" not in df.columns:
        raise AssertionError("Input CSV must contain column: label")

    # Compute bounds
    min_list, max_list = [], []
    per_year = []
    min_per_year = []
    description_count_list = []
    description_count = defaultdict(int)
    for (i, s), desc_ in zip(enumerate(df["label"].astype(str).tolist()), df["description"].astype(str).tolist()):
        mn, mx = parse_label_bounds(s)
        min_per_year.append(mn)
        per_year.append(mx)  # Keep upper bound for per_year (backward-compatible)
        description_count[desc_] += 1
        description_count_list.append(description_count[desc_])


    df["min_per_year"] = min_per_year
    df["per_year"] = per_year
    df["per_year_rounded"] = [int(round(x)) if x >= 0 else int(x) for x in df["per_year"]]
    df["description_count"] = description_count_list

    # Export
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    df.to_json(out_json, orient="records", force_ascii=False, indent=2)

    # Preview
    print(f"Wrote: {out_csv} and {out_json}")
    print(df[["label", "min_per_year", "per_year", "per_year_rounded"]].head(20).to_string(index=False))

if __name__ == "__main__":
    main()
