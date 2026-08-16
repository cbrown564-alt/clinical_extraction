"""Catalog empty-gold SeizureFrequency extras from saved mention-unit v2 rows."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_empty_gold_sf_extras_luna_dev140_protocol_2026-08-16.md"
)
STUDY_DIR = ROOT / (
    "experiments/exectv2_mention_unit_v2_empty_gold_sf_extras_luna_dev140_20260816"
)
V2_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
V4_ROWS = (
    ROOT
    / "experiments/exectv2_semantic_inventory_v4_projection_damage_luna_dev140_20260816"
    / "rows.jsonl"
)
FAMILY = "SeizureFrequency"
FREQUENCY_ATTRS = {
    "FrequencyChange",
    "LowerNumberOfSeizures",
    "MonthDate",
    "NumberOfSeizures",
    "NumberOfTimePeriods",
    "PointInTime",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "UpperNumberOfSeizures",
    "YearDate",
}
FREQUENCY_WORD_RE = re.compile(
    r"\b(twice|couple|few|several|occasional|rare|frequent|week|month|year|"
    r"seizure[- ]free|not had|no further|stopped|times|episodes?)\b",
    re.IGNORECASE,
)
FEBRILE_RE = re.compile(r"\bfebrile\b|\bage of\b|\bat the ages?\b", re.IGNORECASE)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _sf_mentions(row: dict[str, Any]) -> list[dict[str, Any]]:
    prediction = PredictedLetter.model_validate(row["methods"]["llm"]["prediction"])
    extras: list[dict[str, Any]] = []
    for mention in prediction.mentions:
        if mention.entity != FAMILY:
            continue
        extras.append(
            {
                "text": mention.text,
                "evidence": mention.evidence or "",
                "attributes": dict(mention.attributes or {}),
            }
        )
    return extras


def _classify(item: dict[str, Any]) -> str:
    haystack = f"{item['text']} {item['evidence']}"
    if FEBRILE_RE.search(haystack):
        return "remote_childhood"
    if FREQUENCY_ATTRS.intersection(item["attributes"]) or FREQUENCY_WORD_RE.search(haystack):
        return "frequency_statement"
    if item["text"].strip():
        return "seizure_story"
    return "other"


def _extras_by_letter(
    rows: list[dict[str, Any]],
    empty_gold: set[str],
) -> dict[str, list[dict[str, Any]]]:
    found: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        letter_id = row["letter_id"]
        if letter_id not in empty_gold:
            continue
        mentions = _sf_mentions(row)
        if mentions:
            found[letter_id] = mentions
    return found


def main() -> None:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    empty_gold = {
        letter_id
        for letter_id, letter in letters.items()
        if not letter.entities(FAMILY)
    }
    v2_by_letter = _extras_by_letter(_load_rows(V2_ROWS), empty_gold)
    v4_by_letter = (
        _extras_by_letter(_load_rows(V4_ROWS), empty_gold) if V4_ROWS.exists() else {}
    )

    catalog: list[dict[str, Any]] = []
    for letter_id, mentions in sorted(v2_by_letter.items()):
        evidence_counts = Counter(_norm(item["evidence"]) for item in mentions)
        for item in mentions:
            catalog.append(
                {
                    "letter_id": letter_id,
                    "clinical_name": item["text"],
                    "evidence": item["evidence"],
                    "attributes": item["attributes"],
                    "class": _classify(item),
                    "same_evidence_copy": evidence_counts[_norm(item["evidence"])] > 1,
                    "also_on_v4_letter": letter_id in v4_by_letter,
                }
            )

    class_counts = Counter(item["class"] for item in catalog)
    v2_letters = set(v2_by_letter)
    v4_letters = set(v4_by_letter)
    if class_counts["seizure_story"] or class_counts["other"]:
        verdict = "revise"
        mechanism = "mixed_or_unclassified"
    elif len(v2_letters) > len(v4_letters):
        verdict = "answer"
        mechanism = "more_empty_gold_letters"
    else:
        verdict = "answer"
        mechanism = "more_frequency_statements_on_shared_empty_gold_letters"

    payload = {
        "protocol": PROTOCOL,
        "status": "complete",
        "verdict": verdict,
        "mechanism": mechanism,
        "model_calls": 0,
        "finished_utc": datetime.now(UTC).isoformat(),
        "empty_gold_sf_letters": len(empty_gold),
        "v2_llm": {
            "letters": len(v2_letters),
            "mentions": len(catalog),
            "same_evidence_copy": sum(1 for item in catalog if item["same_evidence_copy"]),
            "class_counts": dict(class_counts),
            "only_letters": sorted(v2_letters - v4_letters),
        },
        "v4_llm": {
            "letters": len(v4_letters),
            "mentions": sum(len(items) for items in v4_by_letter.values()),
            "only_letters": sorted(v4_letters - v2_letters),
        },
        "shared_letters": sorted(v2_letters & v4_letters),
        "extras": catalog,
        "claim_boundary": (
            "Development catalog of mention-unit v2 empty-gold SeizureFrequency extras. "
            "Not clinical validation, holdout evidence, or a Decision 0050 change."
        ),
    }
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    (STUDY_DIR / "extras_catalog.json").write_text(json.dumps(payload, indent=2) + "\n")
    summary = {
        key: payload[key]
        for key in ("verdict", "mechanism", "model_calls", "v2_llm", "v4_llm")
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
