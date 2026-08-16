"""Catalog mention-unit v2 hybrid encoder leftover from saved dev140 rows."""

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
    "mention_unit_v2_hybrid_encoder_damage_luna_dev140_protocol_2026-08-16.md"
)
STUDY_DIR = ROOT / (
    "experiments/exectv2_mention_unit_v2_hybrid_encoder_damage_luna_dev140_20260816"
)
V2_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
COUNT_ATTRS = {
    "LowerNumberOfSeizures",
    "NumberOfSeizures",
    "UpperNumberOfSeizures",
}
RESULT_ATTRS = ("MRI_Results", "EEG_Results", "CT_Results")


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def _load_rows() -> list[dict[str, Any]]:
    return [json.loads(line) for line in V2_ROWS.read_text().splitlines() if line.strip()]


def _mentions(row: dict[str, Any], method: str, family: str) -> list[Any]:
    prediction = PredictedLetter.model_validate(row["methods"][method]["prediction"])
    return [mention for mention in prediction.mentions if mention.entity == family]


def _has_count(mention: Any) -> bool:
    return bool(COUNT_ATTRS.intersection(mention.attributes or {}))


def _ix_result(mention: Any) -> str:
    for key in RESULT_ATTRS:
        value = (mention.attributes or {}).get(key)
        if value:
            return str(value)
    return ""


def _gold_sf_texts(letter: Any) -> list[str]:
    return [entity.text for entity in letter.entities("SeizureFrequency")]


def main() -> None:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    rows = _load_rows()
    items: list[dict[str, Any]] = []
    counts = {
        "llm_sf_mentions": 0,
        "hybrid_sf_mentions": 0,
        "llm_sf_with_count": 0,
        "hybrid_sf_with_count": 0,
        "llm_ix_known": 0,
        "llm_ix_unknown": 0,
        "hybrid_ix_known": 0,
        "hybrid_ix_unknown": 0,
        "hybrid_sf_name_kept": 0,
        "hybrid_sf_name_rewritten": 0,
        "last_event_zero": 0,
    }

    for row in rows:
        letter_id = row["letter_id"]
        gold_sf = _gold_sf_texts(letters[letter_id])
        hybrid = row["methods"]["llm_with_rules"]
        warnings = hybrid.get("warnings") or []
        for mention in _mentions(row, "llm", "SeizureFrequency"):
            counts["llm_sf_mentions"] += 1
            counts["llm_sf_with_count"] += int(_has_count(mention))
        for mention in _mentions(row, "llm_with_rules", "SeizureFrequency"):
            counts["hybrid_sf_mentions"] += 1
            counts["hybrid_sf_with_count"] += int(_has_count(mention))
            if not _has_count(mention):
                items.append(
                    {
                        "letter_id": letter_id,
                        "class": "count_unparsed",
                        "clinical_name": mention.text,
                        "evidence": mention.evidence,
                    }
                )
        for mention in _mentions(row, "llm", "Investigations"):
            result = _ix_result(mention)
            if result == "Unknown":
                counts["llm_ix_unknown"] += 1
            elif result:
                counts["llm_ix_known"] += 1
        for mention in _mentions(row, "llm_with_rules", "Investigations"):
            result = _ix_result(mention)
            if result == "Unknown":
                counts["hybrid_ix_unknown"] += 1
                items.append(
                    {
                        "letter_id": letter_id,
                        "class": "result_unknown",
                        "clinical_name": mention.text,
                        "result": result,
                        "evidence": mention.evidence,
                    }
                )
            elif result:
                counts["hybrid_ix_known"] += 1
        for fact in hybrid.get("semantic_facts") or []:
            if fact.get("family") != "SeizureFrequency":
                continue
            name = str(fact.get("clinical_name") or fact.get("text") or "")
            scorer = str(fact.get("scorer_text") or "")
            if scorer and _norm(scorer) == _norm(name):
                counts["hybrid_sf_name_kept"] += 1
            elif scorer:
                counts["hybrid_sf_name_rewritten"] += 1
                items.append(
                    {
                        "letter_id": letter_id,
                        "class": "name_rewritten",
                        "clinical_name": name,
                        "scorer_text": scorer,
                    }
                )
            index = fact.get("fact_index")
            if any(f"item[{index}]: text_not_substring" in warning for warning in warnings):
                items.append(
                    {
                        "letter_id": letter_id,
                        "class": "text_not_substring_drop",
                        "clinical_name": name,
                        "gold_sf": gold_sf,
                    }
                )
        for trace in hybrid.get("rule_trace") or []:
            action = trace.get("action")
            if action == "encoding.last_event_zero":
                counts["last_event_zero"] += 1
            if action != "suppress_uncoded_or_noise_sf":
                continue
            name = str((trace.get("before") or {}).get("text") or "")
            items.append(
                {
                    "letter_id": letter_id,
                    "class": "suppress_uncoded_sf",
                    "clinical_name": name,
                    "evidence": trace.get("evidence"),
                    "gold_sf": gold_sf,
                    "gold_has_name": any(
                        _norm(name) in _norm(unit) or _norm(unit) in _norm(name)
                        for unit in gold_sf
                    ),
                }
            )

    class_counts = Counter(item["class"] for item in items)
    suppress_gold = sum(
        1 for item in items if item["class"] == "suppress_uncoded_sf" and item.get("gold_has_name")
    )
    if (
        counts["hybrid_sf_with_count"] < counts["llm_sf_with_count"] / 2
        and counts["hybrid_ix_unknown"] > counts["llm_ix_unknown"]
        and class_counts["name_rewritten"] <= 2
    ):
        verdict = "answer"
        mechanism = "count_and_result_unparsed"
    else:
        verdict = "revise"
        mechanism = "mixed_or_name_loss"

    payload = {
        "protocol": PROTOCOL,
        "status": "complete",
        "verdict": verdict,
        "mechanism": mechanism,
        "model_calls": 0,
        "finished_utc": datetime.now(UTC).isoformat(),
        "counts": counts,
        "class_counts": dict(class_counts),
        "suppress_uncoded_matching_gold": suppress_gold,
        "items": items,
        "claim_boundary": (
            "Development catalog of mention-unit v2 hybrid encoder leftover. "
            "Not clinical validation, holdout evidence, or a Decision 0050 change."
        ),
    }
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    (STUDY_DIR / "damage_catalog.json").write_text(json.dumps(payload, indent=2) + "\n")
    summary = {
        key: payload[key]
        for key in (
            "verdict",
            "mechanism",
            "model_calls",
            "counts",
            "class_counts",
            "suppress_uncoded_matching_gold",
        )
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
