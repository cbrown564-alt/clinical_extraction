"""Descriptive Gan clinical-inventory feasibility helpers.

Protocol: docs/research/gan2026/gan_inventory_feasibility_dev750_n100_protocol_2026-08-28.md
"""

from __future__ import annotations

import json
import random
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from statistics import median
from typing import Any

from clinical_extraction.core.paths import discover_repo_root

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
CLAIM_BOUNDARY = (
    "Descriptive output on 100 Gan dev750 letters. "
    "No inventory gold. Not scored. Not ExECT benchmark performance."
)
EXPERIMENT_DIR_NAME = "experiments/gan_inventory_feasibility_dev750_n100_20260828"
PAPER_DIR_NAME = "paper_experiments/gan/inventory_feasibility_dev750_n100"


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


def inventory_artifact_dir(*, start: Path | None = None) -> Path:
    root = discover_repo_root(start=start or Path(__file__))
    for relative in (EXPERIMENT_DIR_NAME, PAPER_DIR_NAME):
        candidate = root / relative
        if (candidate / "summary.json").is_file() and (candidate / "rows.jsonl").is_file():
            return candidate
    raise FileNotFoundError(
        "Gan inventory feasibility artifact is not on disk "
        f"({EXPERIMENT_DIR_NAME} or {PAPER_DIR_NAME})"
    )


def load_inventory_panel(*, artifact_dir: Path | None = None) -> dict[str, Any]:
    """Load the frozen 100-letter descriptive inventory for the frontend.

    Mentions only. Letter text stays on the existing Gan letter endpoint.
    """

    directory = artifact_dir if artifact_dir is not None else inventory_artifact_dir()
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise ValueError("inventory summary must be a JSON object")
    require_permitted_split(str(summary.get("split", "")))
    selected = tuple(int(index) for index in summary.get("selected_source_row_indices") or [])
    selected_set = set(selected)
    rows: list[dict[str, Any]] = []
    for line in (directory / "rows.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        index = int(row["source_row_index"])
        if index not in selected_set:
            raise ValueError(
                f"inventory row {index} is unsampled; refused to serve outside the 100-letter set"
            )
        mentions = [
            {
                "entity": mention.get("entity"),
                "text": mention.get("text"),
                "subtype": mention.get("subtype"),
                "attributes": dict(mention.get("attributes") or {}),
                "evidence": mention.get("evidence"),
            }
            for mention in list(row.get("mentions") or [])
        ]
        rows.append({"source_row_index": index, "mentions": mentions})
    row_indices = {int(row["source_row_index"]) for row in rows}
    if row_indices != selected_set:
        raise ValueError("inventory rows do not match the selected sample")
    letters = sorted(rows, key=lambda item: int(item["source_row_index"]))
    illustrations = [
        int(index) for index in summary.get("illustration_source_row_indices") or []
    ]
    return {
        "schema_version": str(summary.get("schema_version") or "gan_inventory_feasibility.v1"),
        "study": str(summary.get("study") or SAMPLE_ID),
        "split": PERMITTED_SPLIT,
        "sample_size": int(summary.get("sample_size") or len(letters)),
        "sample_seed": int(summary.get("sample_seed") or SAMPLE_SEED),
        "selected_source_row_indices": [int(row["source_row_index"]) for row in letters],
        "illustration_source_row_indices": illustrations,
        "program_entry": str(summary.get("program_entry") or PROGRAM_ENTRY),
        "program_config": str(summary.get("program_config") or PROGRAM_CONFIG),
        "scorer": summary.get("scorer"),
        "claim_boundary": CLAIM_BOUNDARY,
        "family_summaries": summary.get("family_summaries") or family_summaries(letters),
        "letters": letters,
    }
