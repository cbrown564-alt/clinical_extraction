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


def test_leftover_form_v1_leaves_intervening_word_count_unparsed() -> None:
    letter = _letter(
        "She had 2 febrile seizures at the age of 2 months. "
        "She has been seizure-free for four years."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizures",
                "evidence": "She had 2 febrile seizures at the age of 2 months.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure-free",
                "evidence": "She has been seizure-free for four years.",
            },
        ]
    )

    baseline = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )
    by_text = {mention.text: mention for mention in baseline.prediction.mentions}
    assert "NumberOfSeizures" not in by_text["febrile seizures"].attributes
    assert by_text["seizure-free"].attributes["NumberOfSeizures"] == "0"


def test_leftover_form_intervening_recovers_near_count_not_duration() -> None:
    letter = _letter(
        "She had 2 febrile seizures at the age of 2 months. "
        "She has had four in the last three weeks. "
        "They can happen several times a day. "
        "She has been seizure-free for four years."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizures",
                "evidence": "She had 2 febrile seizures at the age of 2 months.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "She has had four in the last three weeks.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "They can happen several times a day.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure-free",
                "evidence": "She has been seizure-free for four years.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_intervening"
    )
    mentions = result.prediction.mentions
    febrile = next(mention for mention in mentions if mention.text == "febrile seizures")
    window = next(
        mention
        for mention in mentions
        if mention.evidence == "She has had four in the last three weeks."
    )
    rate = next(
        mention
        for mention in mentions
        if mention.evidence == "They can happen several times a day."
    )
    free = next(mention for mention in mentions if mention.text == "seizure-free")

    assert febrile.attributes["NumberOfSeizures"] == "2"
    assert window.attributes["NumberOfSeizures"] == "4"
    assert window.attributes["TimePeriod"] == "Week"
    assert window.attributes["NumberOfTimePeriods"] == "3"
    assert rate.attributes["NumberOfSeizures"] == "3"
    assert rate.attributes["TimePeriod"] == "Day"
    assert free.attributes["NumberOfSeizures"] == "0"
    assert free.attributes.get("NumberOfSeizures") != "4"


def test_leftover_form_implicit_period_fills_bare_every_and_daily() -> None:
    letter = _letter(
        "seizures have happened roughly every year since the age of 15. "
        "Myoclonic jerks daily. She has a seizure every 3 weeks."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "seizures have happened roughly every year since the age of 15.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Myoclonic jerks",
                "evidence": "Myoclonic jerks daily.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure",
                "evidence": "She has a seizure every 3 weeks.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_implicit_period"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}

    yearly = by_evidence["seizures have happened roughly every year since the age of 15."]
    daily = by_evidence["Myoclonic jerks daily."]
    interval = by_evidence["She has a seizure every 3 weeks."]
    assert yearly.attributes["NumberOfSeizures"] == "1"
    assert yearly.attributes["TimePeriod"] == "Year"
    assert daily.attributes["NumberOfSeizures"] == "1"
    assert daily.attributes["TimePeriod"] == "Day"
    assert interval.attributes["NumberOfSeizures"] == "1"
    assert interval.attributes["NumberOfTimePeriods"] == "3"
    assert interval.attributes["TimePeriod"] == "Week"


def test_leftover_form_casefold_keeps_case_only_name_not_paraphrase() -> None:
    letter = _letter(
        "Focal to bilateral convulsive seizures once a week. "
        "She remains seizure free."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal to bilateral convulsive seizures",
                "evidence": "Focal to bilateral convulsive seizures once a week.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "myoclonic jerks",
                "evidence": "She remains seizure free.",
            },
        ]
    )

    baseline = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form"
    )
    candidate = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_casefold"
    )

    assert [mention.text for mention in baseline.prediction.mentions] == []
    assert [mention.text for mention in candidate.prediction.mentions] == [
        "focal to bilateral convulsive seizures"
    ]
    assert all(mention.text != "myoclonic jerks" for mention in candidate.prediction.mentions)


def test_leftover_form_last_event_widens_cues_not_qualitative_change() -> None:
    letter = _letter(
        "He had a seizure last month. He remains seizrue free. "
        "There has been an increase in her seizures."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure",
                "evidence": "He had a seizure last month.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizrue free",
                "evidence": "He remains seizrue free.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "There has been an increase in her seizures.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_last_event"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}

    assert by_evidence["He had a seizure last month."].attributes["NumberOfSeizures"] == "0"
    assert by_evidence["He remains seizrue free."].attributes["NumberOfSeizures"] == "0"
    change = by_evidence["There has been an increase in her seizures."]
    assert "NumberOfSeizures" not in change.attributes


def test_leftover_form_intervening_v3_recovers_near_count() -> None:
    letter = _letter(
        "She had 2 febrile seizures at the age of 2 months. "
        "She has had four in the last three weeks. "
        "She had a couple of focal impaired awareness seizures. "
        "She has had 1 since previous appointment."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizures",
                "evidence": "She had 2 febrile seizures at the age of 2 months.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "She has had four in the last three weeks.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal impaired awareness seizures",
                "evidence": "She had a couple of focal impaired awareness seizures.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "She has had 1 since previous appointment.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_intervening_v3"
    )
    mentions = result.prediction.mentions
    febrile = next(mention for mention in mentions if mention.text == "febrile seizures")
    window = next(
        mention
        for mention in mentions
        if mention.evidence == "She has had four in the last three weeks."
    )
    couple = next(
        mention
        for mention in mentions
        if mention.text == "focal impaired awareness seizures"
    )
    since = next(
        mention
        for mention in mentions
        if mention.evidence == "She has had 1 since previous appointment."
    )

    assert febrile.attributes["NumberOfSeizures"] == "2"
    assert window.attributes["NumberOfSeizures"] == "4"
    assert window.attributes["TimePeriod"] == "Week"
    assert window.attributes["NumberOfTimePeriods"] == "3"
    assert couple.attributes["NumberOfSeizures"] == "2"
    assert since.attributes["NumberOfSeizures"] == "1"
    assert since.attributes["TimeSince_or_TimeOfEvent"] == "Since"


def test_leftover_form_intervening_v3_blocks_age_duration_date() -> None:
    letter = _letter(
        "He had a febrile seizure at the age of 3. "
        "He has been 6 months without having seizures. "
        "The third episode happened two weeks ago. "
        "He hasn't had any seizures now for around three weeks. "
        "He had an event on 22 December."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizure",
                "evidence": "He had a febrile seizure at the age of 3.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He has been 6 months without having seizures.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "The third episode happened two weeks ago.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He hasn't had any seizures now for around three weeks.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He had an event on 22 December.",
            },
        ]
    )

    unsafe = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_intervening"
    )
    unsafe_by_evidence = {
        mention.evidence: mention for mention in unsafe.prediction.mentions
    }
    assert unsafe_by_evidence[
        "He had a febrile seizure at the age of 3."
    ].attributes["NumberOfSeizures"] == "3"
    assert unsafe_by_evidence[
        "He had an event on 22 December."
    ].attributes["NumberOfSeizures"] == "22"

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_intervening_v3"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}

    assert "NumberOfSeizures" not in by_evidence[
        "He had a febrile seizure at the age of 3."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "He has been 6 months without having seizures."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "The third episode happened two weeks ago."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "He hasn't had any seizures now for around three weeks."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "He had an event on 22 December."
    ].attributes


def test_leftover_form_episodes_v4_recovers_range_not_collapse_or_date() -> None:
    letter = _letter(
        "His seizures continue. "
        "He has had three or four further episodes. "
        "He had a collapse episode whilst in college. "
        "Sodium valproate has stopped the episodes. "
        "He had an event on 22 December."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He has had three or four further episodes.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He had a collapse episode whilst in college.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Sodium valproate has stopped the episodes.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He had an event on 22 December.",
            },
        ]
    )

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_episodes_v4"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}
    recovered = by_evidence["He has had three or four further episodes."]

    assert recovered.attributes["LowerNumberOfSeizures"] == "3"
    assert recovered.attributes["UpperNumberOfSeizures"] == "4"
    assert "NumberOfSeizures" not in by_evidence[
        "He had a collapse episode whilst in college."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "Sodium valproate has stopped the episodes."
    ].attributes
    assert "NumberOfSeizures" not in by_evidence[
        "He had an event on 22 December."
    ].attributes


def test_leftover_form_implicit_v4_fills_bare_period_not_ago_or_rate() -> None:
    letter = _letter(
        "Myoclonic jerks daily. "
        "His seizures have happened roughly every year. "
        "His seizure control had been good until about a week ago. "
        "The seizures can happen 2 or 3 times per month."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Myoclonic jerks",
                "evidence": "Myoclonic jerks daily.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "His seizures have happened roughly every year.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "His seizure control had been good until about a week ago.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "The seizures can happen 2 or 3 times per month.",
            },
        ]
    )

    unsafe = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_implicit_period"
    )
    unsafe_by_evidence = {
        mention.evidence: mention for mention in unsafe.prediction.mentions
    }
    assert unsafe_by_evidence[
            "His seizure control had been good until about a week ago."
        ].attributes["NumberOfSeizures"] == "1"
    assert unsafe_by_evidence[
        "The seizures can happen 2 or 3 times per month."
    ].attributes["NumberOfSeizures"] == "1"

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_implicit_v4"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}
    daily = by_evidence["Myoclonic jerks daily."]
    yearly = by_evidence["His seizures have happened roughly every year."]
    ago = by_evidence["His seizure control had been good until about a week ago."]
    rate = by_evidence["The seizures can happen 2 or 3 times per month."]

    assert daily.attributes["NumberOfSeizures"] == "1"
    assert daily.attributes["TimePeriod"] == "Day"
    assert yearly.attributes["NumberOfSeizures"] == "1"
    assert yearly.attributes["TimePeriod"] == "Year"
    assert "NumberOfSeizures" not in ago.attributes
    assert rate.attributes["NumberOfSeizures"] == "3"
    assert rate.attributes["TimePeriod"] == "Month"


def test_leftover_form_last_event_v4_zeros_evidence_not_glued_cluster() -> None:
    letter = _letter(
        "He remains seizrue free. "
        "Current seizure frequency: No events since surgery. "
        "He had a seizure last month. "
        "Last month, Joan had a cluster of 5. "
        "There has been an increase in her seizures."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He remains seizrue free.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Current seizure frequency: No events since surgery.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "He had a seizure last month.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Last month, Joan had a cluster of 5.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "There has been an increase in her seizures.",
            },
        ]
    )

    unsafe = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_last_event"
    )
    unsafe_cluster = next(
        mention
        for mention in unsafe.prediction.mentions
        if mention.evidence == "Last month, Joan had a cluster of 5."
    )
    assert unsafe_cluster.attributes["NumberOfSeizures"] == "0"

    result = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_last_event_v4"
    )
    by_evidence = {mention.evidence: mention for mention in result.prediction.mentions}

    assert by_evidence["He remains seizrue free."].attributes["NumberOfSeizures"] == "0"
    assert by_evidence[
        "Current seizure frequency: No events since surgery."
    ].attributes["NumberOfSeizures"] == "0"
    assert by_evidence["He had a seizure last month."].attributes["NumberOfSeizures"] == "0"
    assert by_evidence["Last month, Joan had a cluster of 5."].attributes[
        "NumberOfSeizures"
    ] == "5"
    assert "NumberOfSeizures" not in by_evidence[
        "There has been an increase in her seizures."
    ].attributes


def test_span_fold_keeps_hyphen_and_case_names_that_are_in_the_letter() -> None:
    letter = _letter(
        "2 generalised tonic clonic seizures 2014, absence like seizures 2014. "
        "His last seizures were in his teenage years."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absence-like seizures",
                "evidence": "absence like seizures 2014",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Seizures",
                "evidence": "His last seizures were in his teenage years.",
            },
        ]
    )

    landed = materialize_mention_unit(letter, record, method=HYBRID_METHOD)
    folded = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_v5"
    )

    assert [mention.text for mention in landed.prediction.mentions] == []
    assert {mention.text for mention in folded.prediction.mentions} == {
        "absence-like seizures",
        "Seizures",
    }


def test_span_fold_does_not_keep_plural_or_unrelated_names() -> None:
    letter = _letter(
        "Diagnosis: single focal seizure. History is consistent with "
        "Juvenile Myoclonic Epilepsy."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": "Diagnosis: single focal seizure.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "myoclonic jerks",
                "evidence": "History is consistent with Juvenile Myoclonic Epilepsy.",
            },
        ]
    )

    folded = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_v5"
    )

    assert [mention.text for mention in folded.prediction.mentions] == []


def test_history_v6_drops_childhood_febrile_and_keeps_current() -> None:
    letter = _letter(
        "He had 2 febrile seizures at the age of 8 months and 18 months. "
        "The focal seizures were occurring more frequently, perhaps once per day. "
        "Febrile seizures continue once a month."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Febrile seizures",
                "evidence": "He had 2 febrile seizures at the age of 8 months and 18 months.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Focal seizures",
                "evidence": (
                    "The focal seizures were occurring more frequently, "
                    "perhaps once per day."
                ),
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Febrile seizures",
                "evidence": "Febrile seizures continue once a month.",
            },
        ]
    )

    folded = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_v5"
    )
    history = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_history_v6"
    )

    assert {mention.text for mention in folded.prediction.mentions} == {
        "Febrile seizures",
        "Focal seizures",
    }
    assert [mention.text for mention in history.prediction.mentions] == [
        "Focal seizures",
        "Febrile seizures",
    ]
    current = next(
        mention
        for mention in history.prediction.mentions
        if mention.evidence == "Febrile seizures continue once a month."
    )
    assert current.attributes["NumberOfSeizures"] == "1"


def test_cluster_v7_rewrites_generic_cluster_of_seizures_only() -> None:
    letter = _letter(
        "Currently she get around 2-4 seizures per month. "
        "a cluster of seizures in August, 2017 where she had 6-9 seizures "
        "every week for 3 weeks. "
        "Last month, Joan had a cluster of 5. "
        "The focal seizures were occurring more frequently, perhaps once per day."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Currently she get around 2-4 seizures per month.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": (
                    "a cluster of seizures in August, 2017 where she had "
                    "6-9 seizures every week for 3 weeks."
                ),
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "Last month, Joan had a cluster of 5.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": (
                    "The focal seizures were occurring more frequently, "
                    "perhaps once per day."
                ),
            },
        ]
    )

    history = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_history_v6"
    )
    clustered = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_cluster_v7"
    )
    history_by = {mention.evidence: mention for mention in history.prediction.mentions}
    cluster_by = {mention.evidence: mention for mention in clustered.prediction.mentions}
    cluster_evidence = (
        "a cluster of seizures in August, 2017 where she had "
        "6-9 seizures every week for 3 weeks."
    )

    assert history_by[cluster_evidence].text == "seizures"
    assert cluster_by[cluster_evidence].text == "cluster of seizures"
    assert cluster_by[cluster_evidence].attributes["CUI"] == "C3203523"
    assert cluster_by["Currently she get around 2-4 seizures per month."].text == "seizures"
    assert cluster_by["Last month, Joan had a cluster of 5."].text == "seizures"
    assert cluster_by[
        "The focal seizures were occurring more frequently, perhaps once per day."
    ].text == "focal seizures"


def test_awareness_v8_recovers_qualifier_not_without_change() -> None:
    letter = _letter(
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks. "
        "In March she had 2 to 3 of her focal seizures without change in awareness. "
        "a cluster of seizures in August, 2017 where she had 6-9 seizures every week."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": (
                    "Seizure type and frequency: focal seizures with altered "
                    "awareness every 3 weeks."
                ),
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": (
                    "In March she had 2 to 3 of her focal seizures without "
                    "change in awareness."
                ),
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": (
                    "a cluster of seizures in August, 2017 where she had "
                    "6-9 seizures every week."
                ),
            },
        ]
    )

    clustered = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_cluster_v7"
    )
    aware = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_awareness_v8"
    )
    cluster_by = {mention.evidence: mention for mention in clustered.prediction.mentions}
    aware_by = {mention.evidence: mention for mention in aware.prediction.mentions}
    heading = (
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
    )
    without = (
        "In March she had 2 to 3 of her focal seizures without change in awareness."
    )
    cluster_evidence = (
        "a cluster of seizures in August, 2017 where she had 6-9 seizures every week."
    )

    assert cluster_by[heading].text == "focal seizures"
    assert aware_by[heading].text == "focal seizures with altered awareness"
    assert aware_by[heading].attributes["CUI"] == "C0270834"
    assert aware_by[without].text == "focal seizures"
    assert aware_by[cluster_evidence].text == "cluster of seizures"


def test_negation_v9_drops_unused_resemblance_not_last_event() -> None:
    letter = _letter(
        "Generalised tonic clonic seizure-last event July 2016. "
        "he has had roughly two seizures per year since then. "
        "He has not had any events which resemble absences, myoclonus or "
        "focal seizures. "
        "He has not had any further seizures since his last appointment. "
        "The focal seizures were occurring more frequently, perhaps once per day."
    )
    resemblance = (
        "He has not had any events which resemble absences, myoclonus or "
        "focal seizures."
    )
    last_event = "He has not had any further seizures since his last appointment."
    current = (
        "The focal seizures were occurring more frequently, perhaps once per day."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Generalised tonic clonic seizure",
                "evidence": "Generalised tonic clonic seizure-last event July 2016.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "he has had roughly two seizures per year since then.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": resemblance,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "myoclonus",
                "evidence": resemblance,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": resemblance,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": last_event,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": current,
            },
        ]
    )

    aware = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_awareness_v8"
    )
    negated = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_negation_v9"
    )
    aware_names = [mention.text for mention in aware.prediction.mentions]
    negated_by = {mention.evidence: mention for mention in negated.prediction.mentions}

    assert "absences" in aware_names
    assert "myoclonus" in aware_names
    assert resemblance not in negated_by
    assert {mention.text for mention in negated.prediction.mentions} == {
        "Generalised tonic clonic seizure",
        "seizures",
        "focal seizures",
    }
    assert negated_by[last_event].text == "seizures"
    assert negated_by[current].text == "focal seizures"


def test_fortnight_v10_encodes_rate_not_dose_titration() -> None:
    letter = _letter(
        "Focal seizures with altered awareness approximately 1 per fortnight. "
        "Increase the levetiracetam by 250 mg every fortnight. "
        "He has not had any events which resemble absences."
    )
    rate = "Focal seizures with altered awareness approximately 1 per fortnight."
    dose = "Increase the levetiracetam by 250 mg every fortnight."
    resemblance = "He has not had any events which resemble absences."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Focal seizures with altered awareness",
                "evidence": rate,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": dose,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": resemblance,
            },
        ]
    )

    negated = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_negation_v9"
    )
    fortnight = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_fortnight_v10"
    )
    negated_by = {mention.evidence: mention for mention in negated.prediction.mentions}
    fortnight_by = {mention.evidence: mention for mention in fortnight.prediction.mentions}

    assert negated_by[rate].attributes["NumberOfSeizures"] == "1"
    assert "TimePeriod" not in negated_by[rate].attributes
    assert fortnight_by[rate].attributes["NumberOfSeizures"] == "1"
    assert fortnight_by[rate].attributes["TimePeriod"] == "Week"
    assert fortnight_by[rate].attributes["NumberOfTimePeriods"] == "2"
    assert resemblance not in fortnight_by
    assert "TimePeriod" not in fortnight_by[dose].attributes
    assert fortnight_by[dose].attributes.get("NumberOfTimePeriods") != "2"


def test_implicit_v12_on_stack_fills_bare_period_keeps_fortnight() -> None:
    letter = _letter(
        "Myoclonic jerks daily. "
        "Focal seizures with altered awareness approximately 1 per fortnight. "
        "His seizure control had been good until about a week ago. "
        "The seizures can happen 2 or 3 times per month. "
        "He has not had any events which resemble absences."
    )
    daily = "Myoclonic jerks daily."
    rate = "Focal seizures with altered awareness approximately 1 per fortnight."
    ago = "His seizure control had been good until about a week ago."
    times = "The seizures can happen 2 or 3 times per month."
    resemblance = "He has not had any events which resemble absences."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Myoclonic jerks",
                "evidence": daily,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Focal seizures with altered awareness",
                "evidence": rate,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": ago,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": times,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": resemblance,
            },
        ]
    )

    stacked = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_fortnight_v10",
    )
    implicit = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_implicit_v12",
    )
    stacked_by = {mention.evidence: mention for mention in stacked.prediction.mentions}
    implicit_by = {mention.evidence: mention for mention in implicit.prediction.mentions}

    assert "NumberOfSeizures" not in stacked_by[daily].attributes
    assert implicit_by[daily].attributes["NumberOfSeizures"] == "1"
    assert implicit_by[daily].attributes["TimePeriod"] == "Day"
    assert implicit_by[rate].attributes["NumberOfSeizures"] == "1"
    assert implicit_by[rate].attributes["TimePeriod"] == "Week"
    assert implicit_by[rate].attributes["NumberOfTimePeriods"] == "2"
    assert "NumberOfSeizures" not in implicit_by[ago].attributes
    assert implicit_by[times].attributes["NumberOfSeizures"] == "3"
    assert resemblance not in implicit_by


def test_absences_v13_keeps_coded_absences_drops_history_and_drop_attacks() -> None:
    letter = _letter(
        "The absences continue to happen maybe every week. "
        "Occasional absences. "
        "There's no history of absences. "
        "they haven't happened in adulthood. "
        "Focal seizures with altered awareness approximately 1 per fortnight. "
        "He has not had any events which resemble absences."
    )
    weekly = "The absences continue to happen maybe every week."
    occasional = "Occasional absences."
    history = "There's no history of absences."
    drop_attacks = "they haven't happened in adulthood."
    fortnight = "Focal seizures with altered awareness approximately 1 per fortnight."
    resemblance = "He has not had any events which resemble absences."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": weekly,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": occasional,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": history,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "drop attacks",
                "evidence": drop_attacks,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Focal seizures with altered awareness",
                "evidence": fortnight,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": resemblance,
            },
        ]
    )

    control = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_implicit_v12",
    )
    candidate = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_absences_v13",
    )
    control_by = {mention.evidence: mention for mention in control.prediction.mentions}
    candidate_by = {mention.evidence: mention for mention in candidate.prediction.mentions}

    assert weekly in control_by
    assert occasional not in control_by
    assert occasional in candidate_by
    assert candidate_by[weekly].attributes["NumberOfSeizures"] == "1"
    assert candidate_by[weekly].attributes["TimePeriod"] == "Week"
    assert "NumberOfSeizures" not in candidate_by[occasional].attributes
    assert history not in candidate_by
    assert drop_attacks not in candidate_by
    assert resemblance not in candidate_by
    assert candidate_by[fortnight].attributes["NumberOfSeizures"] == "1"
    assert candidate_by[fortnight].attributes["TimePeriod"] == "Week"
    assert candidate_by[fortnight].attributes["NumberOfTimePeriods"] == "2"


def test_febrile_v14_widens_age_cue_keeps_current_and_absences() -> None:
    letter = _letter(
        "She did have a febrile seizure the age of four years. "
        "3 febrile seizures between the ages of 3 and 5. "
        "He had 2 febrile seizures at the age of 8 months and 18 months. "
        "Febrile seizures continue once a month. "
        "The absences continue to happen maybe every week. "
        "Jennifer's seizures started at the age of 2 years."
    )
    missing_at = "She did have a febrile seizure the age of four years."
    ages_plural = "3 febrile seizures between the ages of 3 and 5."
    current_cue = "He had 2 febrile seizures at the age of 8 months and 18 months."
    current_febrile = "Febrile seizures continue once a month."
    weekly = "The absences continue to happen maybe every week."
    onset = "Jennifer's seizures started at the age of 2 years."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizure",
                "evidence": missing_at,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizures",
                "evidence": ages_plural,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizures",
                "evidence": current_cue,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Febrile seizures",
                "evidence": current_febrile,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": weekly,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": onset,
            },
        ]
    )

    control = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_absences_v13",
    )
    candidate = materialize_mention_unit(
        letter,
        record,
        method=HYBRID_METHOD,
        encoder="leftover_form_span_fold_febrile_v14",
    )
    control_by = {mention.evidence: mention for mention in control.prediction.mentions}
    candidate_by = {mention.evidence: mention for mention in candidate.prediction.mentions}

    assert missing_at in control_by
    assert ages_plural in control_by
    assert current_cue not in control_by
    assert missing_at not in candidate_by
    assert ages_plural not in candidate_by
    assert current_cue not in candidate_by
    assert current_febrile in candidate_by
    assert candidate_by[current_febrile].attributes["NumberOfSeizures"] == "1"
    assert candidate_by[weekly].attributes["NumberOfSeizures"] == "1"
    assert candidate_by[weekly].attributes["TimePeriod"] == "Week"
    assert onset in candidate_by


def test_returned_v11_encodes_change_not_zero() -> None:
    letter = _letter(
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks. "
        "Unfortunately after the period of seizure freedom the seizures have returned. "
        "He has not had any further seizures since the last clinic. "
        "His seizures are worse. "
        "She has quite a number of seizures."
    )
    returned = (
        "Unfortunately after the period of seizure freedom the seizures have returned."
    )
    last_event = "He has not had any further seizures since the last clinic."
    worse = "His seizures are worse."
    quite = "She has quite a number of seizures."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": returned,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": last_event,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": worse,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": quite,
            },
        ]
    )

    negated = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_negation_v9"
    )
    returned_enc = materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, encoder="leftover_form_span_fold_returned_v11"
    )
    negated_by = {mention.evidence: mention for mention in negated.prediction.mentions}
    returned_by = {mention.evidence: mention for mention in returned_enc.prediction.mentions}

    assert negated_by[returned].attributes.get("NumberOfSeizures") == "0"
    assert returned_by[returned].attributes.get("FrequencyChange") == "Increased"
    assert "NumberOfSeizures" not in returned_by[returned].attributes
    assert returned_by[returned].text == "seizures"
    assert returned_by[last_event].attributes.get("NumberOfSeizures") == "0"
    assert returned_by[worse].attributes.get("FrequencyChange") != "Increased"
    assert returned_by[quite].attributes.get("FrequencyChange") != "Increased"
