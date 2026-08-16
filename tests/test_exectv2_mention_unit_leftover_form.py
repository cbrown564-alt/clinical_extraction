"""Always-on contract for the mention-unit leftover-form encoder.

Governing owner for the leftover-form remasure: default landed stays
unchanged, and leftover_form parses leftover count, period, and List 9
results from that item only.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    materialize_mention_unit,
    parse_mention_unit_json,
)


def _letter(note: str, letter_id: str = "EA0002") -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note)


def _parse(items: list[dict[str, str]]):
    parsed = parse_mention_unit_json(json.dumps({"items": items}), method=HYBRID_METHOD)
    assert parsed.record is not None
    return parsed.record


def test_default_encoder_leaves_leftover_count_unparsed() -> None:
    letter = _letter("She has 2 to 3 focal seizures a week. EEG showed no epileptiform activity.")
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": "She has 2 to 3 focal seizures a week.",
            }
        ]
    )

    result = materialize_mention_unit(letter, record, method=HYBRID_METHOD)
    mention = result.prediction.mentions[0]

    assert mention.text == "focal seizures"
    assert "NumberOfSeizures" not in mention.attributes
    assert "LowerNumberOfSeizures" not in mention.attributes
    assert "TimePeriod" not in mention.attributes


def test_leftover_form_recovers_count_and_period_from_evidence() -> None:
    letter = _letter("She has 2 to 3 focal seizures a week. absences 2-3 per day.")
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": "She has 2 to 3 focal seizures a week.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": "absences 2-3 per day.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )
    by_text = {mention.text: mention for mention in result.prediction.mentions}

    assert by_text["focal seizures"].attributes["LowerNumberOfSeizures"] == "2"
    assert by_text["focal seizures"].attributes["UpperNumberOfSeizures"] == "3"
    assert by_text["focal seizures"].attributes["TimePeriod"] == "Week"
    assert by_text["focal seizures"].attributes["NumberOfTimePeriods"] == "1"
    assert by_text["absences"].attributes["LowerNumberOfSeizures"] == "2"
    assert by_text["absences"].attributes["UpperNumberOfSeizures"] == "3"
    assert by_text["absences"].attributes["TimePeriod"] == "Day"
    assert any(
        "leftover_form" in str(trace.get("action", "")) for trace in result.rule_trace
    )


def test_leftover_form_keeps_interval_and_last_event_and_skips_duration_years() -> None:
    letter = _letter(
        "Last seizures in teenage years. She has a seizure every 3 weeks. "
        "She has been seizure-free for four years."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Last seizures in teenage years.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure",
                "evidence": "She has a seizure every 3 weeks.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure-free",
                "evidence": "She has been seizure-free for four years.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )
    by_text = {mention.text: mention for mention in result.prediction.mentions}

    assert by_text["seizures"].attributes["NumberOfSeizures"] == "0"
    assert by_text["seizure"].attributes["NumberOfSeizures"] == "1"
    assert by_text["seizure"].attributes["NumberOfTimePeriods"] == "3"
    assert by_text["seizure"].attributes["TimePeriod"] == "Week"
    assert by_text["seizure-free"].attributes["NumberOfSeizures"] == "0"
    assert by_text["seizure-free"].attributes.get("NumberOfSeizures") != "4"


def test_leftover_form_classifies_list9_result_and_keeps_ecg_out() -> None:
    letter = _letter(
        "ECG was normal. EEG showed no epileptiform activity. MRI is planned."
    )
    record = _parse(
        [
            {
                "clinical_family": "Investigations",
                "clinical_name": "ECG",
                "evidence": "ECG was normal.",
            },
            {
                "clinical_family": "Investigations",
                "clinical_name": "EEG",
                "evidence": "EEG showed no epileptiform activity.",
            },
            {
                "clinical_family": "Investigations",
                "clinical_name": "MRI",
                "evidence": "MRI is planned.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )
    by_text = {mention.text: mention for mention in result.prediction.mentions}

    assert "ECG" not in by_text
    assert "MRI" not in by_text
    assert by_text["EEG"].attributes["EEG_Results"] == "Normal"
    assert any(trace.get("action") == "leftover_form.ix_result" for trace in result.rule_trace)


def test_leftover_form_does_not_search_the_letter() -> None:
    letter = _letter(
        "She takes lamotrigine 100 mg daily. MRI was normal. "
        "In March she had 2 to 3 of her focal seizures a week."
    )
    record = _parse(
        [
            {
                "clinical_family": "Prescription",
                "clinical_name": "lamotrigine",
                "evidence": "She takes lamotrigine 100 mg daily.",
            }
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )

    assert [mention.entity for mention in result.prediction.mentions] == ["Prescription"]
    assert all("MRI" not in str(trace.get("after", {})) for trace in result.rule_trace)
    assert all(mention.entity != "SeizureFrequency" for mention in result.prediction.mentions)
