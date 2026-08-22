"""Select-authority SF type and recurrence rewrites stay off encode."""

from __future__ import annotations

from clinical_extraction.paper.rule_records import RULE_BY_NAME
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as sf_encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection,
)


def test_sf_local_evidence_select_rules_are_rewrites() -> None:
    named = RULE_BY_NAME["selection.sf_named_type_from_evidence"]
    bound = RULE_BY_NAME["selection.sf_explicit_recurrence_lower_bound"]
    for row in (named, bound):
        assert row.task == "exectv2"
        assert row.runs_at == "llm_select"
        assert row.authority == "rewrite"
    assert "seizure_frequency" in named.notes
    assert "seizure_frequency" in bound.notes
    encode = RULE_BY_NAME["encoding.sf_local_evidence"]
    assert encode.runs_at == "llm_encode"
    assert "seizure-free" in encode.notes


def test_select_refines_one_unambiguous_named_type_from_local_evidence() -> None:
    mentions, actions = sf_encoding.apply_sf_select_local_evidence(
        [
            {
                "entity": SEIZURE_FREQUENCY.name,
                "text": "seizure",
                "attributes": {"NumberOfSeizures": "1"},
                "evidence": "She had a recent generalised tonic chronic seizure at home.",
            },
            {
                "entity": SEIZURE_FREQUENCY.name,
                "text": "absences",
                "attributes": {"FrequencyChange": "Increased"},
                "evidence": (
                    "He has had three generalised tonic clonic seizures and more "
                    "of his typical absences since clinic."
                ),
            },
            {
                "entity": SEIZURE_FREQUENCY.name,
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "3", "TimePeriod": "Month"},
                "evidence": (
                    "She has focal seizures and generalised tonic clonic "
                    "seizures every month."
                ),
            },
        ]
    )

    assert [mention["text"] for mention in mentions] == [
        "generalised tonic clonic seizures",
        "typical absences",
        "seizures",
    ]
    assert {action["rule_id"] for action in actions} == {
        "selection.sf_named_type_from_evidence"
    }


def test_select_encodes_explicit_recurrence_as_a_lower_bound() -> None:
    mentions, actions = sf_encoding.apply_sf_select_local_evidence(
        [
            {
                "entity": SEIZURE_FREQUENCY.name,
                "text": "generalised tonic clonic seizures",
                "attributes": {"PointInTime": "LastClinic"},
                "evidence": (
                    "He has had further generalised tonic clonic seizures since "
                    "I last saw him."
                ),
            }
        ]
    )

    assert mentions[0]["attributes"]["LowerNumberOfSeizures"] == "1"
    assert actions[0]["rule_id"] == "selection.sf_explicit_recurrence_lower_bound"


def test_select_projection_applies_local_evidence_rewrites() -> None:
    row = sf_state_projection.project_row(
        {
            "letter_id": "EA0139",
            "predicted_mentions": [
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "seizure",
                    "attributes": {"NumberOfSeizures": "1"},
                    "evidence": (
                        "She had a recent generalised tonic chronic seizure at home."
                    ),
                },
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "generalised tonic clonic seizures",
                    "attributes": {"PointInTime": "LastClinic"},
                    "evidence": (
                        "He has had further generalised tonic clonic seizures "
                        "since I last saw him."
                    ),
                },
            ],
        },
        ablation="combined",
    )

    texts = [mention["text"] for mention in row["predicted_mentions"]]
    assert "generalised tonic clonic seizures" in texts
    assert any(
        mention.get("attributes", {}).get("LowerNumberOfSeizures") == "1"
        for mention in row["predicted_mentions"]
    )
    rule_ids = {action["rule_id"] for action in row["projection_actions"]}
    assert "selection.sf_named_type_from_evidence" in rule_ids
    assert "selection.sf_explicit_recurrence_lower_bound" in rule_ids
