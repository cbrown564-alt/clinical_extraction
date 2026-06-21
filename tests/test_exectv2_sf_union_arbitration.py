from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_sf_union_arbitration import (
    arbitrate_sf_mentions,
)


def test_sf_union_arbitration_suppresses_short_and_non_target_noise() -> None:
    current_mentions = [
        _mention(
            "dissociative seizures",
            "Currently he his having dissociative seizures around twice every week.",
            {"NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Week"},
        ),
        _mention(
            "focal seizures",
            "In March she had 2 to 3 of her focal seizures without change in awareness.",
            {
                "CUI": "C0751495",
                "CUIPhrase": "focal seizures",
                "LowerNumberOfSeizures": "2",
                "UpperNumberOfSeizures": "3",
                "MonthDate": "3",
            },
        ),
    ]
    deterministic_mentions = [
        _mention(
            "seizures",
            "seizures",
            {"CUI": "C0036572", "CUIPhrase": "seizures", "NumberOfSeizures": "2"},
        )
    ]

    mentions, actions = arbitrate_sf_mentions(
        current_mentions=current_mentions,
        deterministic_mentions=deterministic_mentions,
    )

    assert [mention["text"] for mention in mentions] == ["focal seizures"]
    assert {action["rule_id"] for action in actions} == {
        "drop_non_target_event",
        "drop_det_short_generic_anchor",
    }
    assert {action["category"] for action in actions} == {"seizure_frequency"}


def test_sf_union_arbitration_applies_benchmark_surface_rewrites() -> None:
    current_mentions = [
        _mention("cluster of 3", "last month there was a cluster of 3 in a single day", {}),
        _mention(
            "absences",
            (
                "His brother said that he has had three generalised tonic clonic seizures "
                "and more of his typical absences since the last clinic appointment."
            ),
            {
                "CUI": "C0563606",
                "CUIPhrase": "absences",
                "FrequencyChange": "Increased",
            },
        ),
        _mention(
            "focal dyscognitive seizures",
            "Last week she had around 10-15 of these seizures over 2 days",
            {
                "CUI": "C0270834",
                "CUIPhrase": "focal dyscognitive seizures",
                "LowerNumberOfSeizures": "10",
                "UpperNumberOfSeizures": "15",
                "NumberOfTimePeriods": "2",
                "TimePeriod": "Day",
            },
        ),
        _mention(
            "focal to bilateral convulsive seizures",
            (
                "The focal to bilateral convulsive seizures occur less often, perhaps "
                "up to 2 or 3 times per month."
            ),
            {
                "CUI": "C0877017",
                "CUIPhrase": "focal to bilateral convulsive seizures",
                "LowerNumberOfSeizures": "2",
                "UpperNumberOfSeizures": "3",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
    ]

    mentions, actions = arbitrate_sf_mentions(
        current_mentions=current_mentions,
        deterministic_mentions=[],
    )

    assert [
        (mention["text"], mention["attributes"].get("CUI"))
        for mention in mentions
    ] == [
        ("seizure cluster", "C3203523"),
        ("typical absences", "C4316903"),
        ("seizures", "C0036572"),
        ("focal to bilateral convulsive seizures", "C0877017"),
    ]
    assert mentions[3]["attributes"]["LowerNumberOfSeizures"] == "0"
    assert {action["rule_id"] for action in actions} == {
        "rewrite_cluster_of_3_to_seizure_cluster",
        "rewrite_absences_to_typical_absences",
        "rewrite_anaphoric_named_to_generic_seizures",
        "rewrite_up_to_range_lower_zero",
    }
    assert {action["category"] for action in actions} == {"benchmark_format"}


def _mention(
    text: str,
    evidence: str,
    attributes: dict[str, str],
) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
        "confidence": "high",
        "rationale": "",
    }
