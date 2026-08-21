from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_monthly_diary import (
    monthly_diary_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_monthly_diary as monthly_diary,
)

_JAN_JUL_LOG = "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1."


def test_selected_evidence_derives_vague_count_over_period() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "many generalized convulsions in past month"
        )
        == "multiple per month"
    )


def test_selected_evidence_derives_explicit_times_per_day() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "He still has simple partial seizures 4 times per day, drop attacks "
            "occurring in batches, and tonic-clonic seizures 2 times per month."
        )
        == "4 per day"
    )


def test_selected_evidence_prefers_recent_yesterday_count_over_lower_weekly_rate() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Yesterday he experienced three tonic-clonic seizures yesterday; "
            "He describes interictal brief auras occurring approximately once "
            "or twice per week without progression."
        )
        == "1 per day"
    )


def test_calendar_log_counts_each_month_once_when_the_same_log_is_repeated() -> None:
    assert monthly_diary.monthly_diary_label_from_text(_JAN_JUL_LOG) == "7 per 7 month"
    assert (
        monthly_diary.monthly_diary_label_from_text(f"{_JAN_JUL_LOG} {_JAN_JUL_LOG}")
        == "7 per 7 month"
    )
    assert (
        monthly_diary.monthly_diary_label_from_text("2021: Jan x1, Dec x1. 2022: Jan x2")
        == "4 per 3 month"
    )


def test_monthly_diary_event_join_does_not_double_identical_evidence_and_raw_value() -> None:
    event = SimpleNamespace(
        kind="frequency_rate",
        assertion_status="asserted",
        evidence=_JAN_JUL_LOG,
        raw_value=_JAN_JUL_LOG,
        time_window=None,
        notes=None,
    )
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=[event]), note_text=None)
        == "7 per 7 month"
    )


def _diary_event(**overrides: object) -> SimpleNamespace:
    payload = {
        "kind": "frequency_rate",
        "assertion_status": "asserted",
        "evidence": "",
        "raw_value": None,
        "time_window": None,
        "notes": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_monthly_diary_does_not_double_count_subset_month_events() -> None:
    """A full July line plus its nocturnal fragment is 8, not 3+8.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    events = [
        _diary_event(
            evidence="In Jun he had a nocturnal seizure",
            raw_value="a nocturnal seizure",
            time_window="June",
        ),
        _diary_event(
            evidence="In July he had three nocturnal seizures",
            raw_value="three nocturnal seizures",
            time_window="July",
        ),
        _diary_event(
            evidence="In July he had three nocturnal seizures and 5 while awake",
            raw_value="5 while awake",
            time_window="July",
        ),
    ]
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=None)
        == "9 per 2 month"
    )


def test_monthly_diary_does_not_double_identical_raw_and_evidence_counts() -> None:
    """The same '5 while awake' in evidence and raw_value is one five.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    events = [
        _diary_event(
            evidence="In Mar she had five seizures during sleep",
            raw_value="five seizures during sleep",
            time_window="In Mar",
        ),
        _diary_event(
            evidence="5 while awake",
            raw_value="5 while awake",
            time_window="In Mar",
            notes="March frequency",
        ),
        _diary_event(
            evidence="In May she had no in sleep",
            raw_value="no in sleep",
            time_window="In May",
        ),
        _diary_event(
            evidence="one while awake",
            raw_value="one while awake",
            time_window="In May",
        ),
    ]
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=None)
        == "11 per 3 month"
    )


def test_monthly_diary_keeps_one_count_when_the_same_month_sentence_is_split() -> None:
    """Two events quoting the same October sentence stay at 5, not 5+0.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    october = "In Oct he had no nocturnal seizures but 5 daytime events."
    december = "In December he had two nocturnal seizures and two while awake."
    events = [
        _diary_event(evidence=october, raw_value="5 daytime events", time_window="October"),
        _diary_event(evidence=october, raw_value="no nocturnal seizures", time_window="October"),
        _diary_event(
            evidence=december,
            raw_value="two nocturnal seizures",
            time_window="December",
        ),
        _diary_event(evidence=december, raw_value="two while awake", time_window="December"),
    ]
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=None)
        == "9 per 3 month"
    )


def test_monthly_diary_sums_split_sleep_and_awake_month_events() -> None:
    """Sum every stated month when nocturnal and awake counts are split.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    combined = (
        "In Jun he had a nocturnal seizure but no daytime events. "
        "In July he had three nocturnal seizures and 5 while awake."
    )
    events = [
        _diary_event(
            evidence="In Jun he had a nocturnal seizure",
            raw_value="a nocturnal seizure in Jun",
            time_window="Jun",
        ),
        _diary_event(
            evidence="In July he had three nocturnal seizures",
            raw_value="three nocturnal seizures in July",
            time_window="July",
        ),
        _diary_event(
            evidence="5 while awake",
            raw_value="5 while awake in July",
            time_window="July",
        ),
        _diary_event(
            evidence=combined,
            raw_value=(
                "a nocturnal seizure in Jun; three nocturnal seizures "
                "and 5 while awake in July"
            ),
            time_window="Jun to July",
            notes="Aggregate across the stated June-July interval: 9 seizures total.",
        ),
    ]
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=None)
        == "9 per 2 month"
    )


def test_monthly_diary_keeps_zero_month_and_so_far_in_month() -> None:
    """Count Sep/Aug/Jul when one month is 'so far' and another is zero.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    evidence = (
        "2 generalised tonic-clonic seizures so far in Sep, one in Aug, and 0 in Jul"
    )
    events = [
        _diary_event(
            evidence=evidence,
            raw_value=evidence,
            time_window="Jul-Sep 2011",
        )
    ]
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=None)
        == "3 per 3 month"
    )


def test_monthly_diary_date_list_is_count_over_dated_span() -> None:
    """Three MM-DD dates are 3 per 3 month, not a dense rate from the day numbers.

    Family: monthly_diary / diary.date_list. Portability: seizure_frequency.
    """
    events = [
        _diary_event(
            evidence=(
                "Seizure events on 06-03, 06-13, 09-23 as recorded in the "
                "patient's diary"
            ),
            raw_value="Seizure events on 06-03, 06-13, 09-23",
            time_window="June to September, before 5 October 2021",
            notes="Three documented seizure events before the 5 October 2021 clinic visit.",
        ),
        _diary_event(
            kind="seizure_free",
            evidence="prior to June they had no events for several months",
            raw_value="no events for several months",
            time_window="Several months before June",
        ),
        _diary_event(
            kind="last_event_only",
            evidence="The September event on 09-23 occurred after intercurrent viral illness",
            raw_value="09-23",
            time_window="September, before 5 October 2021",
            notes="Most recent documented event date.",
        ),
    ]
    note = (
        "Clinic Date: 5 October 2021\n"
        "Seizure events on 06-03, 06-13, 09-23 as recorded in the patient's diary."
    )
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=note)
        == "3 per 3 month"
    )


def test_monthly_diary_sums_this_month_and_were_in_month() -> None:
    """Add this-month, 'were in Aug', and 'four in Jul' as one span.

    Family: monthly_diary. Portability: seizure_frequency.
    """
    events = [
        _diary_event(
            evidence="This month, she has had seven convulsions",
            raw_value="seven convulsions",
            time_window="this month",
        ),
        _diary_event(
            evidence="seven were in Aug",
            raw_value="seven",
            time_window="Aug",
        ),
        _diary_event(
            evidence="four in Jul",
            raw_value="four",
            time_window="Jul",
        ),
    ]
    note = (
        "Clinic Date: 15 September 2011\n"
        "This month, she has had seven convulsions; seven were in Aug and four in Jul."
    )
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=note)
        == "11 per 2 month"
    )


def test_this_month_does_not_borrow_clinic_month_from_the_letter() -> None:
    events = [
        _diary_event(
            evidence="This month she has had two seizures",
            raw_value="two seizures",
            time_window="this month",
        )
    ]
    note = (
        "Clinic Date: 15 September 2011\n"
        "This month she has had two seizures."
    )
    assert (
        monthly_diary_label_from_events(SimpleNamespace(events=events), note_text=note)
        is None
    )
