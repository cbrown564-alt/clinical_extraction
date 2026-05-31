from clinical_extraction.tasks.seizure_frequency.gan2026.schema_repair import (
    repair_decision_payload,
)


def test_repair_decision_payload_handles_common_schema_aliases() -> None:
    payload = repair_decision_payload(
        {
            "assertion_status": "present",
            "uncertainty": "certain",
            "normalized_rate": 2.0,
            "answer_kind": "patient self-report",
            "confidence": 0.9,
        }
    )

    assert payload == {
        "assertion_status": "asserted",
        "uncertainty": "low",
        "normalized_rate": "2.0",
        "answer_kind": "frequency",
        "confidence": "high",
    }


def test_repair_decision_payload_handles_llm_answer_kind_variants() -> None:
    for answer_kind in (
        "count and window",
        "count per time window",
        "direct statement",
        "direct_extraction",
        "electrographic seizure frequency",
        "patient-reported count",
    ):
        assert repair_decision_payload({"answer_kind": answer_kind}) == {
            "answer_kind": "frequency"
        }
