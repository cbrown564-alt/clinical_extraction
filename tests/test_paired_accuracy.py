"""Exact McNemar on paired letter correctness."""

import json
from pathlib import Path

from clinical_extraction.paper.gan_paired_contrasts import aligned_correctness
from clinical_extraction.paper.paired_accuracy import paired_accuracy_test

ROOT = Path(__file__).resolve().parents[1]
PAIRED_ARTIFACT = (
    ROOT
    / "paper_experiments/gan/paired_significance/gemini37flash/test450/comparison.json"
)


def test_mcnemar_is_one_when_no_discordant_pairs() -> None:
    left = (True, True, False, False)
    result = paired_accuracy_test(left, left)
    assert result.n == 4
    assert result.correct_a == 2
    assert result.correct_b == 2
    assert result.a_only == 0
    assert result.b_only == 0
    assert result.p_value == 1.0
    assert result.accuracy_delta == 0.0
    assert result.delta_ci_low == 0.0
    assert result.delta_ci_high == 0.0


def test_mcnemar_detects_one_sided_rescues() -> None:
    # 5 letters: A correct on all, B correct on the first two only.
    left = (True, True, True, True, True)
    right = (True, True, False, False, False)
    result = paired_accuracy_test(left, right)
    assert result.correct_a == 5
    assert result.correct_b == 2
    assert result.a_only == 3
    assert result.b_only == 0
    assert result.p_value == 0.25
    assert result.accuracy_delta == 0.6


def test_mcnemar_is_symmetric_in_the_two_sides() -> None:
    left = (True, False, True, False)
    right = (False, True, True, False)
    forward = paired_accuracy_test(left, right)
    reverse = paired_accuracy_test(right, left)
    assert forward.a_only == reverse.b_only == 1
    assert forward.b_only == reverse.a_only == 1
    assert forward.p_value == reverse.p_value == 1.0
    assert forward.accuracy_delta == -reverse.accuracy_delta


def test_aligned_correctness_uses_the_caller_expected_n() -> None:
    left, right = aligned_correctness(
        {10: True, 11: False},
        {10: False, 11: False},
        expected=2,
        split="dev750",
    )
    assert left == (True, False)
    assert right == (False, False)


def test_paired_significance_artifact_keeps_predeclared_contrasts() -> None:
    payload = json.loads(PAIRED_ARTIFACT.read_text(encoding="utf-8"))
    assert payload["n_test450"] == 450
    assert payload["n_dev750"] == 750
    assert payload["scorer"] == "purist"
    assert set(payload["contrasts"]) == {
        "cell3_vs_rules",
        "cell3_vs_cell5",
        "gemini_temperature_0_vs_1_test450",
        "gemini_temperature_0_vs_1_dev750",
        "gemini_thinking_low_vs_high",
    }
    rules = payload["contrasts"]["cell3_vs_rules"]
    assert rules["correct_a"] == 387
    assert rules["correct_b"] == 325
    assert rules["a_right_b_wrong"] + rules["a_wrong_b_right"] == 136
    temp_dev = payload["contrasts"]["gemini_temperature_0_vs_1_dev750"]
    assert temp_dev["split"] == "dev750"
    assert temp_dev["n"] == 750
    assert temp_dev["correct_a"] == 656
    assert temp_dev["correct_b"] == 656
