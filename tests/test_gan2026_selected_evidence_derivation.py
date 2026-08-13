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
