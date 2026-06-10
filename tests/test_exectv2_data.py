from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    load_letters,
)


def test_load_letters_smoke() -> None:
    letters = load_letters()
    assert len(letters) == 200
    assert [letter.letter_id for letter in letters[:3]] == ["EA0001", "EA0002", "EA0003"]
    assert all(letter.note_text for letter in letters)


def test_seizure_frequency_corpus_shape() -> None:
    letters = load_letters()
    sf_mentions = [m for letter in letters for m in letter.entities(SEIZURE_FREQUENCY)]
    letters_with_sf = [letter for letter in letters if letter.entities(SEIZURE_FREQUENCY)]

    assert len(sf_mentions) == 263
    assert len(letters_with_sf) == 142


def test_ea0006_seizure_frequency_annotations() -> None:
    letters = {letter.letter_id: letter for letter in load_letters()}
    sf = letters["EA0006"].entities(SEIZURE_FREQUENCY)

    assert len(sf) == 3
    first = sf[0]
    assert first.text == "generalised-tonic-clonic-seizures-2014"
    assert first.attributes["NumberOfSeizures"] == "2"
    assert first.attributes["YearDate"] == "2014"
    assert first.attributes["TimeSince_or_TimeOfEvent"] == "During"
    assert first.attributes["CUI"] == "C0494475"


def test_seizure_free_assertions_present_as_zero_count() -> None:
    letters = load_letters()
    zero_count = [
        m
        for letter in letters
        for m in letter.entities(SEIZURE_FREQUENCY)
        if m.attributes.get("NumberOfSeizures") == "0"
    ]
    assert len(zero_count) == 92
