"""Per-family transition reporting shared across agentic replay surfaces.

This module decomposes a replay's baseline -> candidate transitions by hidden
clinical family so a freeze decision can see *where* gains and losses
concentrate, instead of reading a single scalar accuracy. It is the
instrumentation called for in the 2026-06-14 next-phase brief: the
validation750 -> test450 gap is currently optimized as one number against a
target it cannot decompose.

The aggregation is schema-agnostic: callers pass key paths into their own row
dicts, so the same decomposition serves the structured-event consensus replay
and the V12 fresh-evidence reasoner even though their rows differ. Convenience
path presets for both are provided below.

Families come from ``labels.classify_hidden_families`` and are multi-label: a
row can belong to several families, so per-family counts intentionally do not
partition the total row count. ``summarize_transitions_by_family`` returns that
caveat alongside the counts so the result is never misread as a partition.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    classify_hidden_families,
)

# Key-path presets for the two replay row schemas this module currently serves.
CONSENSUS_PATHS: dict[str, tuple[str, ...]] = {
    "transition_path": ("consensus_transition", "purist_transition"),
    "label_changed_path": ("consensus_transition", "label_changed"),
    "baseline_correct_path": ("baseline_comparison", "purist_correct"),
    "candidate_correct_path": ("consensus_comparison", "purist_correct"),
}
FRESH_EVIDENCE_PATHS: dict[str, tuple[str, ...]] = {
    "transition_path": ("transition_vs_v0", "purist_transition"),
    "label_changed_path": ("transition_vs_v0", "label_changed"),
    "baseline_correct_path": ("v0_reference", "comparison", "purist_correct"),
    "candidate_correct_path": ("score_layers", "final", "comparison", "purist_correct"),
}

_MULTILABEL_NOTE = (
    "rows are multi-label; per-family counts overlap and do not partition "
    "total_rows"
)


def note_text_from_rules_row(
    row: Mapping[str, Any],
    *,
    note_text_keys: Sequence[str] = ("note_text",),
    prompt_input_key: str = "prompt_input_json",
) -> str:
    """Best-effort note text for family tagging.

    Prefers an already-attached ``note_text`` field, then parses it out of the
    ``prompt_input_json`` payload carried by the rules/structured-event source
    rows, then degrades to an empty string. An empty string is safe: family
    classification simply falls back to gold/predicted-label-derived families.
    """

    for key in note_text_keys:
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    payload = row.get(prompt_input_key)
    if isinstance(payload, str) and payload:
        try:
            parsed = json.loads(payload)
        except (ValueError, TypeError):
            return ""
        if isinstance(parsed, Mapping):
            note_text = parsed.get("note_text")
            if isinstance(note_text, str):
                return note_text
    elif isinstance(payload, Mapping):
        note_text = payload.get("note_text")
        if isinstance(note_text, str):
            return note_text
    return ""


def tag_hidden_families(
    *,
    note_text: str,
    gold_label: str | None,
    baseline_label: str | None,
) -> tuple[str, ...]:
    """Stable family membership for a row.

    Classification uses ``baseline_label`` (the floor / V0 prediction) rather
    than the candidate label so a row's family set does not shift when the
    candidate flips it. That keeps per-family wrong/correct attribution
    unambiguous across the baseline and candidate columns.
    """

    return classify_hidden_families(
        note_text=note_text,
        gold_label=str(gold_label) if gold_label is not None else "",
        predicted_label=str(baseline_label) if baseline_label is not None else "",
    )


def _dig(row: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = row
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def summarize_transitions_by_family(
    rows: Sequence[Mapping[str, Any]],
    *,
    transition_path: Sequence[str],
    label_changed_path: Sequence[str],
    baseline_correct_path: Sequence[str],
    candidate_correct_path: Sequence[str],
    families_path: Sequence[str] = ("hidden_families",),
) -> dict[str, Any]:
    """Decompose baseline -> candidate transitions by hidden family.

    Returns a structured result with a ``families`` map plus a ``total_rows``
    count and an explicit multi-label caveat, so per-family overlap is never
    read as a partition of the whole.
    """

    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        families = _dig(row, families_path) or ("unclassified",)
        baseline_correct = _dig(row, baseline_correct_path) is True
        candidate_correct = _dig(row, candidate_correct_path) is True
        label_changed = _dig(row, label_changed_path) is True
        transition = _dig(row, transition_path)
        for family in families:
            counter = by_family[str(family)]
            counter["rows"] += 1
            counter["baseline_purist_correct"] += int(baseline_correct)
            counter["candidate_purist_correct"] += int(candidate_correct)
            counter["changed_labels"] += int(label_changed)
            if transition == "wrong_to_correct":
                counter["wrong_to_correct"] += 1
            elif transition == "correct_to_wrong":
                counter["correct_to_wrong"] += 1

    families_summary: dict[str, dict[str, Any]] = {}
    for family, counter in sorted(by_family.items()):
        changed = counter["changed_labels"]
        wrong_to_correct = counter["wrong_to_correct"]
        correct_to_wrong = counter["correct_to_wrong"]
        families_summary[family] = {
            "rows": counter["rows"],
            "baseline_purist_correct": counter["baseline_purist_correct"],
            "candidate_purist_correct": counter["candidate_purist_correct"],
            "changed_labels": changed,
            "wrong_to_correct": wrong_to_correct,
            "correct_to_wrong": correct_to_wrong,
            "net_purist_gain": wrong_to_correct - correct_to_wrong,
            "changed_label_precision": (
                round(wrong_to_correct / changed, 4) if changed else None
            ),
        }

    return {
        "families": families_summary,
        "total_rows": len(rows),
        "multilabel_note": _MULTILABEL_NOTE,
    }
