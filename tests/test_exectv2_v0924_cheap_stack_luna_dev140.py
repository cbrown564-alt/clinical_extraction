"""Contract tests for the authorized v0.9.24 cheap-stack Luna dev140 runner."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    decide_arm,
    topology_failures,
    verify_payload,
)

_FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")


def _hybrid(
    *,
    headline: float,
    family: dict[str, float],
    wins: int,
    losses: int,
) -> dict[str, object]:
    return {
        "headline_f1_delta": headline,
        "family_f1_delta": {name: family.get(name, 0.0) for name in _FAMILIES},
        "four_family_letter_exact_wins": wins,
        "four_family_letter_exact_losses": losses,
        "four_family_letter_exact_net": wins - losses,
    }


def test_cheap_stack_payload_check_does_not_change_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["n_rules"] == 67
    assert payload["n_examples"] == 0
    assert payload["has_scaffold"] is True
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_low_value_when_all_stop_bars_hold() -> None:
    hybrid = _hybrid(
        headline=-0.0168,
        family={"SeizureFrequency": -0.07},
        wins=1,
        losses=2,
    )
    assert topology_failures(hybrid) == []
    assert decide_arm(hybrid, {"parse": 0, "schema": 0}) == "low_value"


def test_load_bearing_when_family_bar_fails() -> None:
    hybrid = _hybrid(
        headline=-0.0168,
        family={"SeizureFrequency": -0.0929},
        wins=1,
        losses=2,
    )
    failures = topology_failures(hybrid)
    assert failures == ["hybrid SeizureFrequency F1 drop -0.0929"]
    assert decide_arm(hybrid, {"parse": 0, "schema": 0}) == "load_bearing"


def test_revise_when_parse_or_schema_fails() -> None:
    hybrid = _hybrid(headline=-0.01, family={}, wins=0, losses=0)
    assert decide_arm(hybrid, {"parse": 1, "schema": 0}) == "revise"
    assert decide_arm(hybrid, {"parse": 0, "schema": 2}) == "revise"
