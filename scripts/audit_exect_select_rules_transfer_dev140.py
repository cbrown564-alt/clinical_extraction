#!/usr/bin/env python3
"""No-call transfer audit for accepted ExECT Select rules on saved dev140 raws."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from analyze_exect_select_rules_dev140 import (
    OUT_DIR,
    ROOT,
    _apply_arm,
    _change_summary,
    _current_select,
    _family_changes,
    _rule_encode,
    _score,
)
from audit_exect_encode_rules_transfer_dev140 import SOURCES, _mentions_from_raw

from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    ACCEPTED_SELECT_RULE_IDS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)


def main() -> None:
    letters = {letter.letter_id: letter for letter in letters_for_split("dev140")}
    source_summaries: dict[str, Any] = {}
    all_changes: list[dict[str, Any]] = []

    for source_name, (path, schema) in SOURCES.items():
        raw_rows = {str(row["letter_id"]): row for row in load_jsonl_rows(path)}
        if set(raw_rows) != set(letters) or len(raw_rows) != 140:
            raise RuntimeError(f"{source_name}: saved raws do not match dev140")

        parsed: dict[str, list[Any]] = {}
        parse_notes: Counter[str] = Counter()
        parse_failure_rows: list[str] = []
        for letter_id, row in raw_rows.items():
            mentions, notes = _mentions_from_raw(str(row.get("raw_output") or ""), schema)
            parsed[letter_id] = mentions
            note_kinds = [note.split(":", 1)[0] for note in notes]
            parse_notes.update(note_kinds)
            if {"invalid_json", "invalid_payload"}.intersection(note_kinds):
                parse_failure_rows.append(letter_id)

        encoded = {
            letter_id: _rule_encode(letter, parsed[letter_id])
            for letter_id, letter in letters.items()
        }
        comparator = {
            letter_id: _current_select(letter, encoded[letter_id])
            for letter_id, letter in letters.items()
        }
        candidate, actions = _apply_arm(
            letters,
            comparator,
            encoded,
            frozenset(ACCEPTED_SELECT_RULE_IDS),
        )
        changes = _family_changes(
            arm_name=f"transfer:{source_name}",
            letters=letters,
            comparator=comparator,
            candidate=candidate,
        )
        rules_by_letter: dict[str, set[str]] = defaultdict(set)
        for action in actions:
            rules_by_letter[str(action["letter_id"])].add(str(action["rule_id"]))
        all_changes.extend(
            {
                **row,
                "source": source_name,
                "rule_ids": sorted(rules_by_letter[str(row["letter_id"])]),
            }
            for row in changes
        )
        action_counts = Counter(str(row["rule_id"]) for row in actions)
        evidence_status = Counter(str(row["evidence_status"]) for row in actions)
        source_summaries[source_name] = {
            "source": path.relative_to(ROOT).as_posix(),
            "source_schema": schema,
            "row_count": len(raw_rows),
            "raw_mentions": sum(len(mentions) for mentions in parsed.values()),
            "parse_note_counts": dict(parse_notes),
            "parse_failure_count": len(parse_failure_rows),
            "parse_failure_rows": sorted(parse_failure_rows),
            "comparator": _score(letters, comparator),
            "candidate": _score(letters, candidate),
            "action_counts": dict(action_counts),
            "evidence_status": dict(evidence_status),
            **_change_summary(changes),
        }

    summary = {
        "schema_version": "exectv2.select_rule_transfer.dev140.v1",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "development_review_permitted",
        "holdout_policy": "test60_not_loaded_or_inspected",
        "model_calls": 0,
        "accepted_rule_ids": list(ACCEPTED_SELECT_RULE_IDS),
        "source_count": len(SOURCES),
        "sources": source_summaries,
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
