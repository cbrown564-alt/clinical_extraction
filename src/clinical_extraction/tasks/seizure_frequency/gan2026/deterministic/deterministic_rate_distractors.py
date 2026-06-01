from __future__ import annotations

import re


def is_medication_or_dose_rate_distractor(match: re.Match[str], text: str) -> bool:
    preceding = text[max(0, match.start() - 80) : match.start()].lower()
    following = text[match.end() : match.end() + 80].lower()
    surrounding = f"{preceding} {match.group(0).lower()} {following}"
    dose_pattern = re.compile(
        r"\b(?:dose|dosing|current treatment|current medication|medication|"
        r"levetiracetam|lamotrigine|carbamazepine|brivaracetam|lacosamide|"
        r"valproate|epilim|topiramate|zonisamide|sumatriptan)\b"
        r".{0,80}(?:\b\d+\s*(?:mg|g|micrograms?|mcg|µg)\b|"
        r"\b(?:mg|g|micrograms?|mcg|µg)\b)",
        re.IGNORECASE,
    )
    if dose_pattern.search(surrounding):
        return True
    if re.search(r"\b(?:migraine|headache|prn)\b", surrounding) and re.search(
        r"\bper\s+(?:day|week|month|year)\b", match.group(0), re.IGNORECASE
    ):
        return True
    return False
