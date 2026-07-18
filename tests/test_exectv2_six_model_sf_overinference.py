from scripts.build_exectv2_six_model_sf_overinference import (
    classify_gold_band,
    classify_transition,
    state_set,
)


def _mention(**attributes: str) -> dict[str, object]:
    return {"entity": "SeizureFrequency", "attributes": attributes}


def test_state_set_uses_change_aware_existing_transform() -> None:
    mentions = [
        _mention(NumberOfSeizures="3", TimePeriod="Month"),
        _mention(NumberOfSeizures="0"),
        _mention(FrequencyChange="Increased"),
        _mention(CUI="C0036572"),
        {"entity": "Diagnosis", "attributes": {}},
    ]

    assert state_set(mentions) == {
        "active-rate",
        "seizure-free",
        "changed",
        "unknown",
    }


def test_empty_gold_is_separate_from_primary_unknown_only_band() -> None:
    assert classify_gold_band(set()) == "empty_gold"
    assert classify_gold_band({"unknown"}) == "unknown_only"
    assert classify_gold_band({"seizure-free"}) == "seizure_free_containing"
    assert classify_gold_band({"changed"}) == "changed_only"
    assert classify_gold_band({"active-rate", "changed"}) == "active_rate_containing"


def test_transition_classifies_overread_rescue_and_correctness_direction() -> None:
    rescued = classify_transition(
        gold={"unknown"},
        comparator={"active-rate"},
        candidate={"unknown"},
    )
    introduced = classify_transition(
        gold={"unknown"},
        comparator={"unknown"},
        candidate={"active-rate"},
    )

    assert rescued == {
        "candidate_changed": True,
        "overread_transition": "overread_rescued",
        "correctness_transition": "wrong_to_correct",
    }
    assert introduced == {
        "candidate_changed": True,
        "overread_transition": "overread_introduced",
        "correctness_transition": "correct_to_wrong",
    }


def test_transition_does_not_call_empty_gold_a_primary_overread() -> None:
    transition = classify_transition(
        gold=set(),
        comparator=set(),
        candidate={"active-rate"},
    )

    assert transition["overread_transition"] == "not_primary_band"
    assert transition["correctness_transition"] == "correct_to_wrong"
