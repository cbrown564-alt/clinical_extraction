"""Behavior tests for the scorer-edit predeclaration gate (Phase-4 guardrail)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

# Load the gate script by path so the test does not depend on repo root being on
# sys.path (the `scripts/` dir is not an installed package under pytest).
_GATE_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "check_scorer_edit_predeclaration.py"
)
_spec = importlib.util.spec_from_file_location("check_scorer_edit_predeclaration", _GATE_PATH)
_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gate)

evaluate = _gate.evaluate
guard_reason = _gate.guard_reason
load_hypothesis_ids = _gate.load_hypothesis_ids

_SCORING = "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py"
_UNGUARDED = "docs/research/some_note.md"

_KNOWN_IDS = {
    "rx_future_medication_regex_scope_bug_2026-07-02",
    "sf_zero_count_precedence_2026-07-02",
}


def test_guarded_paths_are_detected() -> None:
    assert guard_reason(_SCORING) is not None
    assert guard_reason(_SCORING.replace("/", "\\")) is not None


def test_unguarded_paths_pass_through() -> None:
    assert guard_reason(_UNGUARDED) is None
    assert guard_reason("README.md") is None


def test_guarded_file_without_message_blocks() -> None:
    code, report = evaluate([_SCORING], "", _KNOWN_IDS)
    assert code == 1
    assert any("BLOCKED" in line for line in report)


def test_guarded_file_with_predeclaration_and_replay_passes() -> None:
    message = (
        "Fix rx_future_medication_regex_scope_bug_2026-07-02 by clause-scoping the "
        "future/weight regex. dev140 replay: Prescription clinical_headline "
        "0.8766 -> 0.9073, no regressions."
    )
    code, report = evaluate([_SCORING, _UNGUARDED], message, _KNOWN_IDS)
    assert code == 0
    assert any("predeclaration satisfied" in line for line in report)


def test_gate_reads_the_real_registry() -> None:
    """The live registry parses and contains the seed-bug hypothesis id."""

    registry = Path(__file__).resolve().parent.parent / "experiments" / "hypothesis_registry.jsonl"
    ids = load_hypothesis_ids(registry)
    assert "rx_future_medication_regex_scope_bug_2026-07-02" in ids
