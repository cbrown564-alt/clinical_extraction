from __future__ import annotations

from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from scripts import check_exectv2_gpt41mini_single_call_diagnosis_ablation as ablation


def test_change_direction_distinguishes_rescue_regression_and_changed_error() -> None:
    gold = Counter({("Diagnosis", "epilepsy", "Affirmed"): 1})
    correct = Counter(gold)
    wrong_a = Counter({("Diagnosis", "focal epilepsy", "Affirmed"): 1})
    wrong_b = Counter({("Diagnosis", "tonic clonic seizures", "Affirmed"): 1})

    assert ablation.change_direction(wrong_a, correct, gold) == "wrong_to_correct"
    assert ablation.change_direction(correct, wrong_a, gold) == "correct_to_wrong"
    assert ablation.change_direction(wrong_a, wrong_b, gold) == "changed_still_wrong"
    assert ablation.change_direction(correct, correct, gold) == "unchanged_correct"
    assert ablation.change_direction(wrong_a, wrong_a, gold) == "unchanged_wrong"


def test_retained_single_call_config_is_attributable_and_uses_one_model_pass() -> None:
    config = model_swap.load_model_swap_config(ablation.CANDIDATE_CONFIG_PATH)

    assert Path(config.path) == ablation.CANDIDATE_CONFIG_PATH
    assert config.calls_per_letter == 1
    assert config.live_call_components == ("structured_key_family_event_ledger",)
    assert (
        config.assembly.lenses["Diagnosis"].producer
        == "structured_key_family_event_ledger"
    )
    assert model_swap.validate_model_led_architecture(config)["status"] == "pass"
