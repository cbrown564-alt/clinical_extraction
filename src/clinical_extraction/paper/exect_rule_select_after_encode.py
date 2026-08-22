"""Replay accepted Select rules on a saved later-stage ExECT encode ledger."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence, Set
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.exect_later_stage import (
    CITED_SLUG,
    LATER_STAGE_SCORER,
    encode_work_rows_path,
)
from clinical_extraction.paper.methods import (
    exect_machine_split,
    exect_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    ACCEPTED_SELECT_RULE_IDS,
    apply_select_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    exact_clinical_headline_scores,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
STUDY_DIR = ROOT / "experiments/exectv2_rule_select_after_llm_encode_20260822"


def apply_rule_select_after_llm_encode(
    encoded_mentions: Sequence[Mapping[str, Any]],
    extract_mentions: Sequence[Mapping[str, Any]],
    note_text: str,
    enabled_rule_ids: Set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run accepted Select rules on later-stage encoded mentions."""

    return apply_select_rules(
        encoded_mentions,
        source_mentions=extract_mentions,
        note_text=note_text,
        enabled_rule_ids=(
            frozenset(ACCEPTED_SELECT_RULE_IDS)
            if enabled_rule_ids is None
            else enabled_rule_ids
        ),
    )


def replay_rule_select_after_llm_encode(split: str) -> dict[str, Any]:
    """Score encode-then-rule-select on the saved Gemini later-stage encode rows."""

    holdout = holdout_is_aggregate_only(split)
    rows_path = encode_work_rows_path(split)
    if not rows_path.is_file():
        raise RuntimeError(f"missing later-stage encode rows: {rows_path}")
    letters = letters_for_split(split)
    expected = exect_row_count(split)
    if len(letters) != expected:
        raise RuntimeError(f"{split} has {len(letters)} letters, expected {expected}")
    by_id = {str(row.get("letter_id") or ""): row for row in load_jsonl_rows(rows_path)}
    encode_letters: list[ExectLetter] = []
    select_letters: list[ExectLetter] = []
    action_count = 0
    for letter in letters:
        row = by_id.get(letter.letter_id)
        if row is None:
            raise RuntimeError(f"missing encode row for {letter.letter_id}")
        encoded = list(row.get("encoded_mentions") or [])
        extract = list(row.get("extract_mentions") or [])
        selected, actions = apply_rule_select_after_llm_encode(
            encoded,
            extract,
            letter.note_text,
        )
        action_count += len(actions)
        encode_letters.append(
            ExectLetter(
                letter_id=letter.letter_id,
                note_text=letter.note_text,
                annotations=tuple(annotation_from_mapping(dict(m)) for m in encoded),
            )
        )
        select_letters.append(
            ExectLetter(
                letter_id=letter.letter_id,
                note_text=letter.note_text,
                annotations=tuple(annotation_from_mapping(m) for m in selected),
            )
        )
    encode_family = exact_clinical_headline_scores(letters, encode_letters)
    select_family = exact_clinical_headline_scores(letters, select_letters)
    encode_overall = aggregate_scores(encode_family.values())
    select_overall = aggregate_scores(select_family.values())
    artifact: dict[str, Any] = {
        "schema_version": "paper.exect_rule_select_after_llm_encode.v1",
        "generated_on": datetime.now(UTC).date().isoformat(),
        "method": "exect_rule_select_after_llm_encode",
        "extract_source": "exect_llm_only",
        "encode_source": "exect_llm_encode",
        "select_rules": sorted(ACCEPTED_SELECT_RULE_IDS),
        "model_slug": CITED_SLUG,
        "split": split,
        "split_machine": exect_machine_split(split),
        "row_count": len(letters),
        "row_policy": (
            "aggregate_only" if holdout else "development_review_permitted"
        ),
        "call_state": "no_call",
        "scorer": LATER_STAGE_SCORER,
        "encode_stop": {
            "clinical_headline": encode_family,
            "summary": encode_overall,
            "four_family_headline_f1": encode_overall["f1"],
        },
        "select_stop": {
            "clinical_headline": select_family,
            "summary": select_overall,
            "four_family_headline_f1": select_overall["f1"],
            "select_action_count": action_count,
        },
        "claim_boundary": (
            "ExECT aggregate-only test60 cell-4 replay. Do not inspect holdout rows."
            if holdout
            else "ExECT development cell-4 replay. Not holdout."
        ),
    }
    out_dir = STUDY_DIR / split
    out_dir.mkdir(parents=True, exist_ok=True)
    comparison_path = out_dir / "comparison.json"
    comparison_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    artifact["artifact_path"] = str(comparison_path)
    return artifact
