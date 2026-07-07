"""Behavior tests for the scorer-edit predeclaration gate (Phase-4 guardrail)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
guarded_files = _gate.guarded_files
load_hypothesis_ids = _gate.load_hypothesis_ids
mentions_dev140_replay = _gate.mentions_dev140_replay
referenced_hypothesis_ids = _gate.referenced_hypothesis_ids

_SCORING = "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py"
_CONVENTION = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/"
    "deterministic/conventions/prescription.py"
)
_SF_PROJECTION = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/"
    "deterministic/sf_state_projection.py"
)
_LEXICON = "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/contract/drug_lexicon.py"
_UNGUARDED = "docs/research/some_note.md"

_KNOWN_IDS = {
    "rx_future_medication_regex_scope_bug_2026-07-02",
    "sf_zero_count_precedence_2026-07-02",
}


@pytest.mark.parametrize(
    "path",
    [_SCORING, _CONVENTION, _SF_PROJECTION, _LEXICON, _SCORING.replace("/", "\\")],
)
def test_guarded_paths_are_detected(path: str) -> None:
    assert guard_reason(path) is not None


@pytest.mark.parametrize("path", [_UNGUARDED, "tests/test_scorer_scope_invariants.py", "README.md"])
def test_unguarded_paths_pass_through(path: str) -> None:
    assert guard_reason(path) is None


def test_generic_projection_filename_is_guarded() -> None:
    assert guard_reason("src/.../deterministic/target_projection/foo_projection.py") is not None
    assert guard_reason("src/.../benchmark_projection.py") is not None


def test_no_guarded_files_passes_without_message() -> None:
    code, report = evaluate([_UNGUARDED, "README.md"], "", _KNOWN_IDS)
    assert code == 0
    assert any("OK" in line for line in report)


def test_guarded_file_without_message_blocks() -> None:
    code, report = evaluate([_SCORING], "", _KNOWN_IDS)
    assert code == 1
    assert any("BLOCKED" in line for line in report)


def test_guarded_file_with_unknown_hypothesis_id_blocks() -> None:
    message = "made scoring stricter; dev140 replay shows no change. hypothesis_id: not_a_real_id"
    code, report = evaluate([_SCORING], message, _KNOWN_IDS)
    assert code == 1
    assert any("references no hypothesis_id" in line for line in report)


def test_guarded_file_with_hypothesis_but_no_replay_blocks() -> None:
    message = "rx_future_medication_regex_scope_bug_2026-07-02: clause-scope the future regex."
    code, report = evaluate([_SCORING], message, _KNOWN_IDS)
    assert code == 1
    assert any("dev140 replay" in line for line in report)


def test_guarded_file_with_predeclaration_and_replay_passes() -> None:
    message = (
        "Fix rx_future_medication_regex_scope_bug_2026-07-02 by clause-scoping the "
        "future/weight regex. dev140 replay: Prescription clinical_headline "
        "0.8766 -> 0.9073, no regressions."
    )
    code, report = evaluate([_SCORING, _UNGUARDED], message, _KNOWN_IDS)
    assert code == 0
    assert any("predeclaration satisfied" in line for line in report)


@pytest.mark.parametrize(
    "message, expected",
    [
        ("dev140 replay shows +0.01", True),
        ("dev-140 re-scored clean", True),
        ("replayed on dev 140", True),
        ("dev140 numbers cited", False),  # no replay verb
        ("replayed the run", False),  # no dev140 token
        ("full-200 replay", False),
    ],
)
def test_dev140_replay_detection(message: str, expected: bool) -> None:
    assert mentions_dev140_replay(message) is expected


def test_referenced_ids_substring_match() -> None:
    message = "closes rx_future_medication_regex_scope_bug_2026-07-02 (see registry)"
    assert referenced_hypothesis_ids(message, _KNOWN_IDS) == [
        "rx_future_medication_regex_scope_bug_2026-07-02"
    ]


def test_gate_reads_the_real_registry() -> None:
    """The live registry parses and contains the seed-bug hypothesis id."""

    registry = Path(__file__).resolve().parent.parent / "experiments" / "hypothesis_registry.jsonl"
    ids = load_hypothesis_ids(registry)
    assert "rx_future_medication_regex_scope_bug_2026-07-02" in ids


def test_guarded_files_reports_reasons() -> None:
    reported = guarded_files([_SCORING, _LEXICON, _UNGUARDED])
    reported_paths = {path for path, _reason in reported}
    assert _UNGUARDED.replace("\\", "/") not in reported_paths
    assert len(reported) == 2
