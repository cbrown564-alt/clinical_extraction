"""Tests for the shared per-family transition instrumentation.

These cover the three things the next-phase brief depends on: multi-label
fan-out (a row counts toward every family it belongs to), the gap-decomposition
math (per-family baseline/candidate correctness, net gain, changed-label
precision), and graceful degradation when note text is unavailable.
"""

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_transitions import (
    CONSENSUS_PATHS,
    note_text_from_rules_row,
    summarize_transitions_by_family,
    tag_hidden_families,
)


def test_note_text_prefers_attached_field() -> None:
    assert note_text_from_rules_row({"note_text": "clinic letter"}) == "clinic letter"


def test_note_text_parsed_from_prompt_input_json_string() -> None:
    payload = json.dumps({"note_text": "seizures in clusters nightly"})
    assert (
        note_text_from_rules_row({"prompt_input_json": payload})
        == "seizures in clusters nightly"
    )


def test_note_text_degrades_to_empty_string() -> None:
    assert note_text_from_rules_row({}) == ""
    assert note_text_from_rules_row({"prompt_input_json": "not json"}) == ""


def test_tag_hidden_families_uses_baseline_label_and_handles_none() -> None:
    families = tag_hidden_families(
        note_text="seizures recorded in a diary, clustered nightly",
        gold_label="unknown",
        baseline_label=None,
    )
    assert "unknown_boundary" in families
    assert "cluster_burden" in families
    assert "diary_or_log_aggregation" in families


def test_summarize_transitions_by_family_multilabel_and_math() -> None:
    rows = [
        # In two families; a genuine wrong->correct fix.
        {
            "hidden_families": ["cluster_burden", "diary_or_log_aggregation"],
            "consensus_transition": {
                "purist_transition": "wrong_to_correct",
                "label_changed": True,
            },
            "baseline_comparison": {"purist_correct": False},
            "consensus_comparison": {"purist_correct": True},
        },
        # Same single family as the first row's first family; a regression.
        {
            "hidden_families": ["cluster_burden"],
            "consensus_transition": {
                "purist_transition": "correct_to_wrong",
                "label_changed": True,
            },
            "baseline_comparison": {"purist_correct": True},
            "consensus_comparison": {"purist_correct": False},
        },
        # Untouched correct row in a third family.
        {
            "hidden_families": ["seizure_free_duration"],
            "consensus_transition": {
                "purist_transition": "correct_to_correct",
                "label_changed": False,
            },
            "baseline_comparison": {"purist_correct": True},
            "consensus_comparison": {"purist_correct": True},
        },
    ]

    result = summarize_transitions_by_family(rows, **CONSENSUS_PATHS)
    families = result["families"]

    # Multi-label: total counts overlap and exceed the row count.
    assert result["total_rows"] == 3
    assert sum(stats["rows"] for stats in families.values()) == 4
    assert "multilabel_note" in result

    cluster = families["cluster_burden"]
    assert cluster["rows"] == 2
    assert cluster["wrong_to_correct"] == 1
    assert cluster["correct_to_wrong"] == 1
    assert cluster["net_purist_gain"] == 0
    assert cluster["changed_labels"] == 2
    assert cluster["changed_label_precision"] == 0.5
    assert cluster["baseline_purist_correct"] == 1
    assert cluster["candidate_purist_correct"] == 1

    diary = families["diary_or_log_aggregation"]
    assert diary["rows"] == 1
    assert diary["net_purist_gain"] == 1
    assert diary["changed_label_precision"] == 1.0

    free = families["seizure_free_duration"]
    assert free["changed_labels"] == 0
    assert free["changed_label_precision"] is None


def test_summarize_transitions_defaults_missing_families_to_unclassified() -> None:
    rows = [
        {
            "consensus_transition": {
                "purist_transition": "wrong_to_correct",
                "label_changed": True,
            },
            "baseline_comparison": {"purist_correct": False},
            "consensus_comparison": {"purist_correct": True},
        }
    ]

    result = summarize_transitions_by_family(rows, **CONSENSUS_PATHS)
    assert set(result["families"]) == {"unclassified"}
    assert result["families"]["unclassified"]["wrong_to_correct"] == 1
