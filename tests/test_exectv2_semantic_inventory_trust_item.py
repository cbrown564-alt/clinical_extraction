"""Always-on contract for the v4 trust-item projector.

Governing owner for the Wave 0 remasure: default v4 stays unchanged, and
trust_item applies landed v9 tables only to the emitted item.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    materialize_inventory,
    parse_inventory_json,
)


def _letter(note: str, letter_id: str = "EA0002") -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note)


def _parse(raw: dict[str, object], method: str):
    parsed = parse_inventory_json(json.dumps(raw), method=method)
    assert parsed.record is not None
    return parsed.record


def test_default_projection_still_collapses_typed_focal_rate() -> None:
    letter = _letter("She had 2 to 3 focal seizures in March without change in awareness.")
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "She had 2 to 3 focal seizures in March without change in awareness.",
                    "evidence": (
                        "She had 2 to 3 focal seizures in March without change in awareness."
                    ),
                    "attributes": {
                        "type": "focal",
                        "concept": "focal seizures",
                        "lower_count": "2",
                        "upper_count": "3",
                    },
                }
            ]
        },
        LLM_METHOD,
    )

    result = materialize_inventory(letter, record, method=LLM_METHOD)

    assert result.prediction.mentions[0].text == "seizures"


def test_trust_item_uses_concept_span_not_type_label() -> None:
    letter = _letter("She had 2 to 3 focal seizures in March without change in awareness.")
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "She had 2 to 3 focal seizures in March without change in awareness.",
                    "evidence": (
                        "She had 2 to 3 focal seizures in March without change in awareness."
                    ),
                    "attributes": {
                        "type": "focal",
                        "concept": "focal seizures",
                        "lower_count": "2",
                        "upper_count": "3",
                    },
                }
            ]
        },
        LLM_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=LLM_METHOD, projection="trust_item"
    )

    mention = result.prediction.mentions[0]
    assert mention.text == "focal seizures"
    assert mention.attributes["LowerNumberOfSeizures"] == "2"
    assert mention.attributes["UpperNumberOfSeizures"] == "3"


def test_trust_item_keeps_mri_result_and_drops_ecg() -> None:
    letter = _letter(
        "The 2012 MRI scan showed a subtle high-intensity signal in the left "
        "temporal lobe. ECG was normal."
    )
    record = _parse(
        {
            "facts": [
                {
                    "family": "Investigations",
                    "event": (
                        "The 2012 MRI scan showed a subtle high-intensity signal "
                        "in the left temporal lobe."
                    ),
                    "evidence": (
                        "The 2012 MRI scan showed a subtle high-intensity signal "
                        "in the left temporal lobe."
                    ),
                    "attributes": {"name": "MRI scan", "result": "abnormal"},
                },
                {
                    "family": "Investigations",
                    "event": "ECG was normal.",
                    "evidence": "ECG was normal.",
                    "attributes": {"name": "ECG", "result": "normal"},
                },
            ]
        },
        LLM_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=LLM_METHOD, projection="trust_item"
    )

    assert [mention.text for mention in result.prediction.mentions] == ["MRI"]
    assert result.prediction.mentions[0].attributes["MRI_Results"] == "Abnormal"


def test_trust_item_hybrid_parses_scoped_word_count_not_duration() -> None:
    letter = _letter(
        "She has had four secondary generalised seizures since her last clinic "
        "appointment. No generalised tonic clonic seizures for four years."
    )
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": (
                        "She has had four secondary generalised seizures since "
                        "her last clinic appointment."
                    ),
                    "evidence": (
                        "She has had four secondary generalised seizures since "
                        "her last clinic appointment."
                    ),
                },
                {
                    "family": "SeizureFrequency",
                    "event": "No generalised tonic clonic seizures for four years.",
                    "evidence": "No generalised tonic clonic seizures for four years.",
                },
            ]
        },
        HYBRID_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=HYBRID_METHOD, projection="trust_item"
    )

    counted = next(
        mention
        for mention in result.prediction.mentions
        if mention.text == "secondary generalised seizures"
    )
    assert counted.attributes["NumberOfSeizures"] == "4"
    duration = next(
        mention
        for mention in result.prediction.mentions
        if "tonic" in mention.text.lower() or mention.text == "seizures"
    )
    assert duration.attributes.get("NumberOfSeizures") != "4"


def test_trust_item_hybrid_maps_described_finding_with_list_9() -> None:
    letter = _letter(
        "A 2012 MRI scan showed a subtle high-intensity signal in the left temporal lobe."
    )
    record = _parse(
        {
            "facts": [
                {
                    "family": "Investigations",
                    "event": (
                        "A 2012 MRI scan showed a subtle high-intensity signal "
                        "in the left temporal lobe."
                    ),
                    "evidence": (
                        "A 2012 MRI scan showed a subtle high-intensity signal "
                        "in the left temporal lobe."
                    ),
                }
            ]
        },
        HYBRID_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=HYBRID_METHOD, projection="trust_item"
    )

    assert result.prediction.mentions[0].text == "MRI"
    assert result.prediction.mentions[0].attributes["MRI_Results"] == "Abnormal"


def test_trust_item_keeps_last_clinic_count_and_splits_dated_frame() -> None:
    letter = _letter(
        "Since last being seen, she had two seizures in March."
    )
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "Since last being seen, she had two seizures in March.",
                    "evidence": "Since last being seen, she had two seizures in March.",
                }
            ]
        },
        HYBRID_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=HYBRID_METHOD, projection="trust_item"
    )

    counts = [mention.attributes.get("NumberOfSeizures") for mention in result.prediction.mentions]
    assert counts == ["2", "2"]
    frames = {
        (
            mention.attributes.get("PointInTime"),
            mention.attributes.get("TimeSince_or_TimeOfEvent"),
            mention.attributes.get("MonthDate"),
        )
        for mention in result.prediction.mentions
    }
    assert ("LastClinic", "Since", None) in frames or (
        "LastClinic",
        "Since",
        "",
    ) in frames
    assert any(mention.attributes.get("MonthDate") == "3" for mention in result.prediction.mentions)


def test_trust_item_does_not_emit_uncoded_blackout_as_seizure_frequency() -> None:
    letter = _letter("Approximately 10 blackout events in total.")
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "Approximately 10 blackout events in total",
                    "evidence": "Approximately 10 blackout events in total.",
                }
            ]
        },
        HYBRID_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=HYBRID_METHOD, projection="trust_item"
    )

    assert result.prediction.mentions == ()


def test_trust_item_keeps_hyphenated_tonic_clonic_span() -> None:
    letter = _letter("No generalised tonic-clonic seizures have occurred since July 2016.")
    record = _parse(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": (
                        "No generalised tonic-clonic seizures have occurred "
                        "since July 2016."
                    ),
                    "evidence": (
                        "No generalised tonic-clonic seizures have occurred "
                        "since July 2016."
                    ),
                }
            ]
        },
        HYBRID_METHOD,
    )

    result = materialize_inventory(
        letter, record, method=HYBRID_METHOD, projection="trust_item"
    )

    assert result.prediction.mentions[0].text == "generalised tonic-clonic seizures"
