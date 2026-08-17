"""Always-on contract for mention-unit form recovery.

Default materialization copies the emitted name. form_recovery=True
reads leftover count, period, and test-result words from that item,
may drop remote history, rewrite a name, or split two stated
once-daily doses. It does not search the letter.
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


def _recover(letter: ExectLetter, record):
    return materialize_mention_unit(
        letter, record, method=HYBRID_METHOD, form_recovery=True
    )


def test_default_materialization_leaves_leftover_count_unparsed() -> None:
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


def test_form_recovery_recovers_count_and_period_from_evidence() -> None:
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
    by_text = {mention.text: mention for mention in _recover(letter, record).prediction.mentions}

    assert by_text["focal seizures"].attributes["LowerNumberOfSeizures"] == "2"
    assert by_text["focal seizures"].attributes["UpperNumberOfSeizures"] == "3"
    assert by_text["focal seizures"].attributes["TimePeriod"] == "Week"
    assert by_text["absences"].attributes["LowerNumberOfSeizures"] == "2"
    assert by_text["absences"].attributes["TimePeriod"] == "Day"


def test_form_recovery_drops_remote_last_event_keeps_interval_and_zero() -> None:
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
    by_text = {mention.text: mention for mention in _recover(letter, record).prediction.mentions}

    assert "seizures" not in by_text
    assert by_text["seizure"].attributes["NumberOfSeizures"] == "1"
    assert by_text["seizure"].attributes["NumberOfTimePeriods"] == "3"
    assert by_text["seizure"].attributes["TimePeriod"] == "Week"
    assert by_text["seizure-free"].attributes["NumberOfSeizures"] == "0"


def test_form_recovery_classifies_list9_result_and_keeps_ecg_out() -> None:
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
    result = _recover(letter, record)
    by_text = {mention.text: mention for mention in result.prediction.mentions}

    assert "ECG" not in by_text
    assert "MRI" not in by_text
    assert by_text["EEG"].attributes["EEG_Results"] == "Normal"


def test_form_recovery_does_not_search_the_letter() -> None:
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
    result = _recover(letter, record)

    assert [mention.entity for mention in result.prediction.mentions] == ["Prescription"]
    assert all(mention.entity != "SeizureFrequency" for mention in result.prediction.mentions)


def test_form_recovery_recovers_guarded_intervening_counts() -> None:
    letter = _letter(
        "The seizures continue. She has had four in the last three weeks. "
        "They can happen several times a day. "
        "She has been seizure-free for four years."
    )
    record = _parse(
        [
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
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    window = by_evidence["She has had four in the last three weeks."]
    rate = by_evidence["They can happen several times a day."]
    free = by_evidence["She has been seizure-free for four years."]
    assert window.attributes["NumberOfSeizures"] == "4"
    assert window.attributes["TimePeriod"] == "Week"
    assert rate.attributes["NumberOfSeizures"] == "3"
    assert rate.attributes["TimePeriod"] == "Day"
    assert free.attributes["NumberOfSeizures"] == "0"


def test_form_recovery_blocks_age_duration_and_date_counts() -> None:
    letter = _letter(
        "He had a febrile seizure at the age of 3. "
        "She has been seizure-free for four years. "
        "On 12 March 2019 she had 2 seizures."
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
                "clinical_name": "seizure-free",
                "evidence": "She has been seizure-free for four years.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": "On 12 March 2019 she had 2 seizures.",
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert "He had a febrile seizure at the age of 3." not in by_evidence
    assert by_evidence["She has been seizure-free for four years."].attributes[
        "NumberOfSeizures"
    ] == "0"
    date = by_evidence["On 12 March 2019 she had 2 seizures."]
    assert date.attributes.get("NumberOfSeizures") != "12"


def test_form_recovery_fills_implicit_period_not_ago() -> None:
    letter = _letter(
        "Myoclonic jerks daily. She has a seizure every 3 weeks. "
        "The last seizure was two years ago."
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
                "clinical_name": "seizure",
                "evidence": "She has a seizure every 3 weeks.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizure",
                "evidence": "The last seizure was two years ago.",
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert by_evidence["Myoclonic jerks daily."].attributes["NumberOfSeizures"] == "1"
    assert by_evidence["Myoclonic jerks daily."].attributes["TimePeriod"] == "Day"
    assert by_evidence["She has a seizure every 3 weeks."].attributes["NumberOfTimePeriods"] == "3"
    ago = by_evidence["The last seizure was two years ago."]
    assert ago.attributes.get("NumberOfSeizures") != "2"


def test_form_recovery_span_fold_keeps_hyphen_and_case_names() -> None:
    letter = _letter(
        "Absence-like seizures twice a week. FOCAL seizures once a month. "
        "She has no history of drop attacks."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absence-like seizures",
                "evidence": "Absence-like seizures twice a week.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "FOCAL seizures",
                "evidence": "FOCAL seizures once a month.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "drop attack",
                "evidence": "She has no history of drop attacks.",
            },
        ]
    )
    names = {mention.text for mention in _recover(letter, record).prediction.mentions}

    assert "absence-like seizures" in names
    assert "FOCAL seizures" in names
    assert "drop attack" not in names


def test_form_recovery_drops_childhood_febrile_keeps_current() -> None:
    letter = _letter(
        "She did have a febrile seizure the age of four years. "
        "Febrile seizures continue once a month."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "febrile seizure",
                "evidence": "She did have a febrile seizure the age of four years.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "Febrile seizures",
                "evidence": "Febrile seizures continue once a month.",
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert "She did have a febrile seizure the age of four years." not in by_evidence
    current = by_evidence["Febrile seizures continue once a month."]
    assert current.attributes["NumberOfSeizures"] == "1"


def test_form_recovery_rewrites_cluster_and_awareness_names() -> None:
    letter = _letter(
        "a cluster of seizures in August, 2017 where she had 6-9 seizures "
        "every week for 3 weeks. "
        "Focal seizures with altered awareness approximately 1 per fortnight. "
        "focal seizures without loss of awareness once a month."
    )
    cluster = (
        "a cluster of seizures in August, 2017 where she had 6-9 seizures "
        "every week for 3 weeks."
    )
    awareness = "Focal seizures with altered awareness approximately 1 per fortnight."
    without = "focal seizures without loss of awareness once a month."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": cluster,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": awareness,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": without,
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert by_evidence[cluster].text == "cluster of seizures"
    assert by_evidence[awareness].text == "focal seizures with altered awareness"
    assert by_evidence[without].text == "focal seizures"


def test_form_recovery_drops_unused_resemblance() -> None:
    letter = _letter(
        "He has not had any events which resemble absences. "
        "He has not had any further seizures since the last clinic."
    )
    unused = "He has not had any events which resemble absences."
    last_event = "He has not had any further seizures since the last clinic."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": unused,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": last_event,
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert unused not in by_evidence
    assert by_evidence[last_event].attributes["NumberOfSeizures"] == "0"


def test_form_recovery_encodes_fortnight_rate_not_dose_titration() -> None:
    letter = _letter(
        "Focal seizures with altered awareness approximately 1 per fortnight. "
        "Increase lamotrigine by 25 mg every fortnight."
    )
    rate = "Focal seizures with altered awareness approximately 1 per fortnight."
    titration = "Increase lamotrigine by 25 mg every fortnight."
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal seizures",
                "evidence": rate,
            },
            {
                "clinical_family": "Prescription",
                "clinical_name": "lamotrigine",
                "evidence": titration,
            },
        ]
    )
    result = _recover(letter, record)
    sf = next(
        mention
        for mention in result.prediction.mentions
        if mention.entity == "SeizureFrequency"
    )
    rx = next(
        mention
        for mention in result.prediction.mentions
        if mention.entity == "Prescription"
    )

    assert sf.attributes["NumberOfSeizures"] == "1"
    assert sf.attributes["TimePeriod"] == "Week"
    assert sf.attributes["NumberOfTimePeriods"] == "2"
    assert rx.attributes.get("Frequency") != "2"


def test_form_recovery_keeps_coded_absences() -> None:
    letter = _letter(
        "The absences continue to happen maybe every week. "
        "There's no history of absences. "
        "they haven't happened in adulthood. drop attacks."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": "The absences continue to happen maybe every week.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "absences",
                "evidence": "There's no history of absences.",
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "drop attacks",
                "evidence": "they haven't happened in adulthood.",
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    kept = by_evidence["The absences continue to happen maybe every week."]
    assert kept.text == "absences"
    assert kept.attributes["NumberOfSeizures"] == "1"
    assert kept.attributes["TimePeriod"] == "Week"
    assert "There's no history of absences." not in by_evidence
    assert "they haven't happened in adulthood." not in by_evidence


def test_form_recovery_drops_remote_history_keeps_onset() -> None:
    letter = _letter(
        "His last seizures were in his teenage years where he probably "
        "had around 3 or 4 focal to bilateral convulsive seizures. "
        "Jennifer's seizures started at the age of 2 years and have "
        "continued every since."
    )
    teenage = (
        "His last seizures were in his teenage years where he probably "
        "had around 3 or 4 focal to bilateral convulsive seizures."
    )
    onset = (
        "Jennifer's seizures started at the age of 2 years and have "
        "continued every since."
    )
    record = _parse(
        [
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "focal to bilateral convulsive seizures",
                "evidence": teenage,
            },
            {
                "clinical_family": "SeizureFrequency",
                "clinical_name": "seizures",
                "evidence": onset,
            },
        ]
    )
    by_evidence = {
        mention.evidence: mention for mention in _recover(letter, record).prediction.mentions
    }

    assert teenage not in by_evidence
    assert onset in by_evidence


def test_form_recovery_splits_once_daily_unequal_doses() -> None:
    letter = _letter(
        "Current antiepileptic medication: levetiracetam 750mg mane, 500 mg nocte. "
        "Please start Sodium Valproate 300mgs once a day, increasing after 2 weeks "
        "to 300mgs am and 500mgs pm."
    )
    split = "Current antiepileptic medication: levetiracetam 750mg mane, 500 mg nocte."
    titration = (
        "Please start Sodium Valproate 300mgs once a day, increasing after 2 weeks "
        "to 300mgs am and 500mgs pm."
    )
    record = _parse(
        [
            {
                "clinical_family": "Prescription",
                "clinical_name": "levetiracetam",
                "evidence": split,
            },
            {
                "clinical_family": "Prescription",
                "clinical_name": "Sodium Valproate",
                "evidence": titration,
            },
        ]
    )
    default = materialize_mention_unit(letter, record, method=HYBRID_METHOD)
    recovered = _recover(letter, record)
    default_split = [
        mention
        for mention in default.prediction.mentions
        if mention.entity == "Prescription" and mention.evidence == split
    ]
    recovered_split = [
        mention
        for mention in recovered.prediction.mentions
        if mention.entity == "Prescription" and mention.evidence == split
    ]
    recovered_titration = [
        mention
        for mention in recovered.prediction.mentions
        if mention.entity == "Prescription" and mention.evidence == titration
    ]

    assert len(default_split) == 1
    assert {mention.attributes["DrugDose"] for mention in recovered_split} == {
        "750",
        "500",
    }
    assert all(mention.attributes["Frequency"] == "1" for mention in recovered_split)
    assert all(
        mention.attributes.get("DrugDose") != "500" for mention in recovered_titration
    )
