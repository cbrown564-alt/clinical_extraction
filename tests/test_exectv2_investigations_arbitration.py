from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_arbitration as arbitration,
)


def test_investigations_arbitration_drops_pending_tests_miscast_as_no() -> None:
    mentions = [
        _mention(
            "MRI scan of his brain",
            "I will arrange an MRI scan of his brain as well as an ECG.",
            {"MRI_Performed": "No", "MRI_Results": "Unknown"},
            rationale=(
                "The MRI is planned but not completed; planned tests without "
                "completed tests are omitted, so MRI_Performed is No."
            ),
        ),
        _mention(
            "EEG",
            "she is awaiting an appointment for an EEG",
            {"EEG_Performed": "No"},
            rationale="EEG is planned but not yet performed.",
        ),
    ]

    kept, actions = arbitration.arbitrate_investigations_mentions(mentions)

    assert kept == []
    assert [action["rule_id"] for action in actions] == [
        "drop_pending_or_planned_investigation",
        "drop_pending_or_planned_investigation",
    ]
    assert {action["category"] for action in actions} == {"clinical_epilepsy"}


def test_investigations_arbitration_keeps_completed_result_mentions() -> None:
    mentions = [
        _mention(
            "MRI 2019",
            "Investigations: MRI 2019 normal",
            {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
        _mention(
            "EEG",
            "EEG 2019: generalised spike and wave with photosensitivity",
            {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
        ),
    ]

    kept, actions = arbitration.arbitrate_investigations_mentions(mentions)

    assert [(mention["text"], mention["attributes"]) for mention in kept] == [
        ("MRI 2019", {"MRI_Performed": "Yes", "MRI_Results": "Normal"}),
        ("EEG", {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"}),
    ]
    assert actions == []


def test_investigations_arbitration_keeps_since_last_appointment_results() -> None:
    mentions = [
        _mention(
            "eeg",
            "and a normal eeg since her last appointment",
            {"EEG_Performed": "Yes", "EEG_Results": "Normal"},
        )
    ]

    kept, actions = arbitration.arbitrate_investigations_mentions(mentions)

    assert [mention["text"] for mention in kept] == ["eeg"]
    assert actions == []


def test_investigations_arbitration_drops_requested_unknown_mentions() -> None:
    mentions = [
        _mention(
            "EEG",
            "I wil request an up to date EEG",
            {"EEG_Performed": "Yes", "EEG_Results": "Unknown"},
            rationale="EEG is planned but no result is available.",
        ),
        _mention(
            "MRI",
            "At the time an MRI showed a small hyperintensity",
            {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
        ),
    ]

    kept, actions = arbitration.arbitrate_investigations_mentions(mentions)

    assert [mention["text"] for mention in kept] == ["MRI"]
    assert [action["rule_id"] for action in actions] == [
        "drop_requested_unknown_investigation"
    ]


def _mention(
    text: str,
    evidence: str,
    attributes: dict[str, str],
    *,
    rationale: str = "",
) -> dict:
    return {
        "entity": "Investigations",
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
        "confidence": "high",
        "rationale": rationale,
    }
