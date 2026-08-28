"""Descriptive Gan clinical-inventory feasibility helpers.

Protocol: docs/research/gan2026/gan_inventory_feasibility_dev750_n100_protocol_2026-08-28.md
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Mapping, Sequence
from statistics import median
from typing import Any

FAMILIES: tuple[str, ...] = (
    "Diagnosis",
    "Prescription",
    "Investigations",
    "SeizureFrequency",
)
PERMITTED_SPLIT = "dev750"
MACHINE_SPLIT = "validation"
SAMPLE_ID = "gan_inventory_feasibility_dev750_n100_v1"
SAMPLE_SEED = 20260828
SAMPLE_SIZE = 100
PROGRAM_ENTRY = "run_letter"
PROGRAM_CONFIG = "ACCEPTED_THREE_STAGE_CONFIG"
ILLUSTRATION_COUNT = 3
LETTER_EXCERPT_CHARS = 500


def require_permitted_split(split: str) -> None:
    if split != PERMITTED_SPLIT:
        raise ValueError(
            f"Gan inventory feasibility may load {PERMITTED_SPLIT} only; "
            f"refused {split!r} (test450 is locked)."
        )


def select_sample_indices(
    pool: Sequence[int],
    *,
    size: int = SAMPLE_SIZE,
    seed: int = SAMPLE_SEED,
) -> tuple[int, ...]:
    unique_sorted = tuple(sorted({int(index) for index in pool}))
    if size > len(unique_sorted):
        raise ValueError(
            f"Cannot sample {size} letters from a pool of {len(unique_sorted)}"
        )
    selected = random.Random(seed).sample(list(unique_sorted), size)
    return tuple(sorted(selected))


def mention_subtype(
    entity: str,
    text: str,
    attributes: Mapping[str, str] | None = None,
) -> str:
    attrs = dict(attributes or {})
    if entity == "Diagnosis":
        return str(attrs.get("DiagCategory") or attrs.get("CUIPhrase") or text)
    if entity == "Prescription":
        return str(attrs.get("DrugName") or text)
    if entity == "Investigations":
        parts = [
            f"{prefix}:{attrs[key]}"
            for prefix, key in (
                ("MRI", "MRI_Results"),
                ("CT", "CT_Results"),
                ("EEG", "EEG_Results"),
            )
            if attrs.get(key)
        ]
        return "+".join(parts) if parts else text
    if entity == "SeizureFrequency":
        return str(attrs.get("FrequencyChange") or attrs.get("CUIPhrase") or text)
    return text


def _family_counts(mentions: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {family: 0 for family in FAMILIES}
    for mention in mentions:
        entity = str(mention.get("entity", ""))
        if entity in counts:
            counts[entity] += 1
    return counts


def family_summaries(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_letter: dict[str, list[int]] = {family: [] for family in FAMILIES}
    per_letter["any_family"] = []
    subtype_counts: dict[str, Counter[str]] = {family: Counter() for family in FAMILIES}
    for row in rows:
        mentions = list(row.get("mentions") or [])
        counts = _family_counts(mentions)
        for family in FAMILIES:
            per_letter[family].append(counts[family])
        per_letter["any_family"].append(sum(counts.values()))
        for mention in mentions:
            entity = str(mention.get("entity", ""))
            if entity in subtype_counts:
                subtype = str(mention.get("subtype") or "")
                if subtype:
                    subtype_counts[entity][subtype] += 1

    def _pack(values: list[int], subtypes: Counter[str] | None = None) -> dict[str, Any]:
        packed: dict[str, Any] = {
            "letters_with_at_least_one": sum(1 for value in values if value > 0),
            "total_facts": sum(values),
            "median_facts_per_letter": float(median(values)) if values else 0.0,
            "min_facts_per_letter": min(values) if values else 0,
            "max_facts_per_letter": max(values) if values else 0,
        }
        if subtypes is not None:
            packed["common_subtypes"] = [
                {"subtype": label, "count": count}
                for label, count in subtypes.most_common(5)
            ]
        return packed

    summary = {family: _pack(per_letter[family], subtype_counts[family]) for family in FAMILIES}
    summary["any_family"] = _pack(per_letter["any_family"])
    return summary


def choose_illustration_indices(
    rows: Sequence[Mapping[str, Any]],
    *,
    limit: int = ILLUSTRATION_COUNT,
) -> tuple[int, ...]:
    scored: list[tuple[int, int, int]] = []
    for row in rows:
        mentions = list(row.get("mentions") or [])
        counts = _family_counts(mentions)
        families_present = sum(1 for family in FAMILIES if counts[family] > 0)
        scored.append(
            (families_present, sum(counts.values()), int(row["source_row_index"]))
        )
    chosen: list[int] = []
    for family_floor in (3, 2, 1):
        eligible = [
            (facts, index)
            for present, facts, index in scored
            if present >= family_floor and index not in chosen
        ]
        eligible.sort(key=lambda item: (-item[0], item[1]))
        for _, index in eligible:
            if len(chosen) >= limit:
                return tuple(chosen)
            chosen.append(index)
        if len(chosen) >= limit:
            return tuple(chosen)
    return tuple(chosen)


def letter_excerpt(note_text: str, *, limit: int = LETTER_EXCERPT_CHARS) -> str:
    collapsed = " ".join(note_text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:limit].rstrip() + "…"
