#!/usr/bin/env python3
"""No-call transfer audit for ExECT same-fact encode rules on saved dev140 raws."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)
from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.exect_cell_replay import FAMILIES, _family_keys
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.format_stack import (  # noqa: E501
    DEFAULT_FORMAT_RULES,
    apply_format_stack,
    assign_flatten_mention_ids,
    mention_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing import (  # noqa: E501
    mentions_from_events,
    parse_structured_events_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
OUT_DIR = ROOT / "experiments/exectv2_encode_rule_development_20260821"
SourceSchema = Literal["compact_events", "event_mentions"]
Confidence = Literal["low", "medium", "high"]
CONFIDENCE_VALUES: dict[str, Confidence] = {
    "low": "low",
    "medium": "medium",
    "high": "high",
}
SOURCES: dict[str, tuple[Path, SourceSchema]] = {
    **{
        f"llm_only/{model}": (
            ROOT
            / "paper_experiments/exect/exect_llm_only"
            / model
            / "dev140/structured.jsonl",
            "compact_events",
        )
        for model in (
            "deepseek_v4_flash",
            "gemini37flash",
            "gpt56luna",
            "grok46",
        )
    },
    **{
        f"llm_pre_post/{model}": (
            ROOT
            / "paper_experiments/exect/exect_llm_pre_post"
            / model
            / "dev140/structured.jsonl",
            "event_mentions",
        )
        for model in (
            "deepseek_v4_flash",
            "gemini37flash",
            "gemma4_26b",
            "gpt56luna",
            "grok46",
        )
    },
}


def _mentions_from_raw(
    raw_output: str,
    schema: SourceSchema,
) -> tuple[list[PredictedMention], list[str]]:
    if schema == "compact_events":
        record, notes = parse_structured_events_json(raw_output)
        return (mentions_from_events(record) if record is not None else []), notes

    try:
        payload, notes = parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return [], [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, Mapping):
        return [], [*notes, "invalid_payload: expected object"]
    events = payload.get("clinical_events")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        return [], [*notes, "invalid_payload: missing clinical_events"]
    if any(isinstance(event, Mapping) and event.get("fact") for event in events):
        record, compact_notes = parse_structured_events_json(raw_output)
        return (
            mentions_from_events(record) if record is not None else [],
            [*notes, "auto_compact_events", *compact_notes],
        )
    mentions: list[PredictedMention] = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        evidence = str(event.get("evidence") or "")
        event_mentions = event.get("mentions")
        if not isinstance(event_mentions, Sequence) or isinstance(
            event_mentions, (str, bytes)
        ):
            continue
        for mention in event_mentions:
            if not isinstance(mention, Mapping):
                continue
            attrs = mention.get("attributes")
            attributes = attrs if isinstance(attrs, Mapping) else {}
            mentions.append(
                PredictedMention(
                    entity=str(mention.get("entity") or ""),
                    text=str(mention.get("text") or ""),
                    attributes={
                        str(key): str(value)
                        for key, value in attributes.items()
                        if value is not None
                    },
                    evidence=evidence,
                    confidence=CONFIDENCE_VALUES.get(
                        str(event.get("confidence") or "medium").lower(), "medium"
                    ),
                    rationale=str(event.get("rationale") or ""),
                )
            )
    return mentions, notes


def _render(
    letter: ExectLetter,
    mentions: Sequence[PredictedMention],
    rules: frozenset[str],
) -> list[dict[str, Any]]:
    formatted, _warnings = apply_format_stack(
        mentions,
        letter.note_text,
        letter_id=letter.letter_id,
        enabled_rules=rules,
    )
    return assign_flatten_mention_ids([mention_row(mention) for mention in formatted])


def _gold_keys(letter: ExectLetter) -> dict[str, Counter[Hashable]]:
    return {
        family: Counter(
            clinical_headline_unit_keys(
                family,
                [annotation for annotation in letter.annotations if annotation.entity == family],
                letter.note_text,
            )
        )
        for family in FAMILIES
    }


def _counts(gold: Counter[Hashable], prediction: Counter[Hashable]) -> Counter[str]:
    return Counter(
        {
            "tp": sum((gold & prediction).values()),
            "fp": sum((prediction - gold).values()),
            "fn": sum((gold - prediction).values()),
        }
    )


def _score(
    letters: Mapping[str, ExectLetter],
    predictions: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    family_scores: dict[str, dict[str, float | int]] = {}
    total: Counter[str] = Counter()
    for family in FAMILIES:
        counts: Counter[str] = Counter()
        for letter_id, letter in letters.items():
            counts.update(
                _counts(
                    _gold_keys(letter)[family],
                    _family_keys(letter, predictions[letter_id])[family],
                )
            )
        family_scores[family] = _prf(counts)
        total.update(counts)
    return {"clinical_fact": _prf(total), "family": family_scores}


def _prf(counts: Mapping[str, int]) -> dict[str, float | int]:
    tp, fp, fn = (int(counts.get(key, 0)) for key in ("tp", "fp", "fn"))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def main() -> None:
    letters = {letter.letter_id: letter for letter in letters_for_split("dev140")}
    all_summaries: dict[str, Any] = {}
    all_changes: list[dict[str, Any]] = []

    for source_name, (path, schema) in SOURCES.items():
        raw_rows = {str(row["letter_id"]): row for row in load_jsonl_rows(path)}
        if set(raw_rows) != set(letters) or len(raw_rows) != 140:
            raise RuntimeError(f"{source_name}: saved raws do not match dev140")
        parsed: dict[str, list[PredictedMention]] = {}
        parse_notes: Counter[str] = Counter()
        parse_failure_rows: list[str] = []
        for letter_id, row in raw_rows.items():
            mentions, notes = _mentions_from_raw(str(row.get("raw_output") or ""), schema)
            parsed[letter_id] = mentions
            note_kinds = [note.split(":", 1)[0] for note in notes]
            parse_notes.update(note_kinds)
            if {"invalid_json", "invalid_payload"}.intersection(note_kinds):
                parse_failure_rows.append(letter_id)

        baseline = {
            letter_id: _render(letter, parsed[letter_id], frozenset())
            for letter_id, letter in letters.items()
        }
        candidate = {
            letter_id: _render(letter, parsed[letter_id], DEFAULT_FORMAT_RULES)
            for letter_id, letter in letters.items()
        }
        directions: Counter[str] = Counter()
        correct_regressions: list[dict[str, str]] = []
        exact_rescues: list[dict[str, str]] = []
        for letter_id, letter in letters.items():
            gold = _gold_keys(letter)
            base_keys = _family_keys(letter, baseline[letter_id])
            candidate_keys = _family_keys(letter, candidate[letter_id])
            for family in FAMILIES:
                if base_keys[family] == candidate_keys[family]:
                    continue
                base_counts = _counts(gold[family], base_keys[family])
                cand_counts = _counts(gold[family], candidate_keys[family])
                base_error = base_counts["fp"] + base_counts["fn"]
                cand_error = cand_counts["fp"] + cand_counts["fn"]
                direction = (
                    "better"
                    if cand_error < base_error
                    else "worse"
                    if cand_error > base_error
                    else "same"
                )
                directions[f"{family}:{direction}"] += 1
                base_exact = base_error == 0
                candidate_exact = cand_error == 0
                if base_exact and not candidate_exact:
                    correct_regressions.append(
                        {"letter_id": letter_id, "family": family}
                    )
                if candidate_exact and not base_exact:
                    exact_rescues.append({"letter_id": letter_id, "family": family})
                all_changes.append(
                    {
                        "schema_version": "exectv2.encode_transfer_change.dev140.v1",
                        "dataset": "ExECTv2",
                        "split": "dev140",
                        "source": source_name,
                        "source_schema": schema,
                        "letter_id": letter_id,
                        "family": family,
                        "direction": direction,
                        "baseline_counts": dict(base_counts),
                        "candidate_counts": dict(cand_counts),
                        "error_delta": cand_error - base_error,
                    }
                )

        all_summaries[source_name] = {
            "source": path.relative_to(ROOT).as_posix(),
            "source_schema": schema,
            "row_count": len(raw_rows),
            "raw_mentions": sum(len(mentions) for mentions in parsed.values()),
            "parse_note_counts": dict(parse_notes),
            "parse_failure_count": len(parse_failure_rows),
            "parse_failure_rows": sorted(parse_failure_rows),
            "baseline": _score(letters, baseline),
            "candidate": _score(letters, candidate),
            "changed_family_error_directions": dict(directions),
            "family_exact_rescues": exact_rescues,
            "comparator_exact_regressions": correct_regressions,
        }

    summary = {
        "schema_version": "exectv2.encode_rule_transfer.dev140.v2",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "development_review_permitted",
        "holdout_policy": "test60_not_loaded_or_inspected",
        "model_calls": 0,
        "rules": sorted(DEFAULT_FORMAT_RULES),
        "source_count": len(SOURCES),
        "sources": all_summaries,
        "claim_boundary": (
            "No-call transfer across saved dev140 raw-output distributions; "
            "not holdout evidence or clinical validation."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "transfer_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_jsonl_rows(all_changes, OUT_DIR / "transfer_changes.jsonl")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
