#!/usr/bin/env python3
"""Score Gemini ExECT LLM-only raw lane from existing one-call sidecars.

No model calls. test60 is aggregate-only: do not print letter ids.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing import (  # noqa: E501
    MentionForEvidence,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection import (  # noqa: E501
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FAMILIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
SOURCES = {
    "dev140": (
        "dev",
        140,
        REPO_ROOT
        / "experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813_structured.jsonl",
    ),
    "test60": (
        "test",
        59,
        REPO_ROOT / "experiments/current_stack/sidecars/exect_test60/gemini37flash.jsonl",
    ),
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _flatten(row: dict[str, Any]) -> list[MentionForEvidence]:
    mentions: list[MentionForEvidence] = []
    for event in row.get("structured_events") or []:
        if not isinstance(event, dict):
            continue
        evidence = str(event.get("evidence") or "")
        confidence = str(event.get("confidence") or "medium")
        rationale = str(event.get("rationale") or "")
        for mention in event.get("mentions") or []:
            if not isinstance(mention, dict):
                continue
            entity = str(mention.get("entity") or event.get("family") or "")
            if entity not in FAMILIES:
                continue
            attrs = mention.get("attributes") or {}
            mentions.append(
                MentionForEvidence(
                    entity=entity,
                    text=str(mention.get("text") or ""),
                    attributes={str(k): str(v) for k, v in dict(attrs).items()},
                    evidence=evidence,
                    confidence=confidence,
                    rationale=rationale,
                )
            )
    return mentions


def _pred_letter(letter_id: str, mentions: list[dict[str, Any]]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(
            annotation_from_mapping(m)
            for m in mentions
            if m.get("entity") in FAMILIES
        ),
    )


def score_split(split_name: str) -> dict[str, Any]:
    machine_split, expected_n, path = SOURCES[split_name]
    letters = {letter.letter_id: letter for letter in load_letters_for_split(machine_split)}
    rows = _read_jsonl(path)
    if len(letters) != expected_n or len(rows) != expected_n:
        raise ValueError(f"{split_name}: letters={len(letters)} rows={len(rows)}")
    gold_letters: list[ExectLetter] = []
    pred_letters: list[ExectLetter] = []
    empty_events = 0
    for row in rows:
        letter_id = str(row["letter_id"])
        letter = letters[letter_id]
        if not (row.get("structured_events") or []):
            empty_events += 1
            predicted: list[dict[str, Any]] = []
        else:
            projected, _warnings = to_predicted_letter(
                letter_id,
                _flatten(row),
                note_text=letter.note_text,
            )
            predicted = [
                {
                    "entity": mention.entity,
                    "text": mention.text,
                    "attributes": dict(mention.attributes),
                    "evidence": mention.evidence,
                }
                for mention in projected.mentions
            ]
        gold_letters.append(letter)
        pred_letters.append(_pred_letter(letter_id, predicted))
    family = clinical_headline_scores(gold_letters, pred_letters)
    overall = aggregate_scores(family.values())
    return {
        "split": split_name,
        "n": expected_n,
        "empty_structured_events": empty_events,
        "f1": overall["f1"],
        "precision": overall["precision"],
        "recall": overall["recall"],
        "by_family": {name: family[name]["f1"] for name in FAMILIES},
        "source": path.relative_to(REPO_ROOT).as_posix(),
    }


def main() -> None:
    payload = {
        "schema_version": "exectv2.gemini37flash.llm_only.raw_lane.v1",
        "protocol": "docs/research/exectv2/gemini37flash_llm_only_raw_lane_protocol_2026-08-14.md",
        "model": "gemini/gemini-3.7-flash",
        "thinking": "reasoning_effort=low",
        "surface": "raw_candidate / raw_lane_score",
        "call_mode": "saved_structured_no_call",
        "cells": {name: score_split(name) for name in ("dev140", "test60")},
        "claim_boundary": (
            "No-call raw-lane readout of existing one-call sidecars. "
            "test60 is aggregate-only. Not Decision 0046 Sol identity. "
            "Not a hybrid fill."
        ),
    }
    out = REPO_ROOT / "experiments/exectv2_gemini37flash_llm_only_raw_lane_20260814.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
