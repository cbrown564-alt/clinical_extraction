"""Invariant-focused tests for gan2026 normalize cluster semantics."""






from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    benchmark_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_with_evidence,
)

validate_benchmark_repair_steps = benchmark_repair.validate_benchmark_repair_steps


def test_repair_prediction_label_with_evidence_repairs_cluster_on_multiple_days() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per month",
            (
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days, each beginning with a brief sense of disconnection"
            ),
        )
        == "multiple cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_recurrence_cluster_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 to 6 per day",
            (
                "He can sometimes go nearly two week without seizures, but when "
                "they recur he tends to have several in one day, often between 4 and 6."
            ),
        )
        == "1 cluster per 2 week, 4 to 6 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_no_definite_events_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            "no definite epileptic events documented in the past two months",
        )
        == "seizure free for 2 month"
    )


def test_repair_prediction_label_with_evidence_repairs_current_non_epileptic_events() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            (
                "Seizure-like episodes are currently non-epileptic in nature and "
                "appear less troublesome."
            ),
        )
        == "seizure free for multiple year"
    )


def test_repair_prediction_label_with_evidence_repairs_plural_daily_events() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 per day",
            "They described daily brief events with preserved awareness.",
        )
        == "multiple per day"
    )


def test_repair_with_evidence_preserves_seizure_free_over_medication_dose() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "seizure free since August 2023",
            "since titration to levetiracetam 1000 mg twice daily in August 2023, "
            "there have been no further events suggestive of seizures.",
        )
        == "seizure free for multiple year"
    )


def test_repair_prediction_label_with_evidence_ignores_rescue_medication_use_limit() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 clusters per week",
            "Clobazam 10 mg at night as required for clusters "
            "(patient-led use, no more than 2-3 nights per week)",
        )
        == "unknown"
    )


def test_repair_prediction_label_with_evidence_preserves_dozens_per_day() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per day",
            "Petit mal occur on a near-daily basis, sometimes dozens in a day.",
        )
        == "multiple per day"
    )


def test_repair_prediction_label_with_evidence_does_not_count_daily_no_event_entries() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "seizure free for 4 month",
            "The diary shows steady daily entries with no recorded spells suggestive of "
            "seizure activity.",
        )
        == "seizure free for 4 month"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per month",
            "events tend to gather into bursts roughly once each month, "
            "with several episodes over a few days",
        )
        == "1 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "Weekly morning clusters reported; number per cluster not documented.",
        )
        == "1 cluster per week, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_quarter_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 clusters per quarter",
            "Patient reports two clusters this quarter with several brief episodes.",
        )
        == "2 cluster per 3 month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "cluster burden increased; now weekly, 2 - 3 per cluster",
        )
        == "1 cluster per week, 2 to 3 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_grouped_weekly_clusters() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "events occurring on 3-4 nights per week, with several brief episodes "
            "grouped together during the night",
        )
        == "3 to 4 cluster per week, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_several_fortnight_clusters() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "clusters arise on several evenings per fortnight, each cluster with about five spells",
        )
        == "multiple cluster per 2 week, 5 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_bursts() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 per month",
            "brief bursts occurring roughly once a month, typically soon after waking",
        )
        == "1 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_days_size_unknown() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 cluster days per month",
            "Seizure diary shows 2 cluster days this month; sizes unrecorded",
        )
        == "2 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_or_more() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "Weekly clusters, usually 6 or more events within ~2 h",
        )
        == "1 cluster per week, 6 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_days_with_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 cluster days per month, 3 to 4 seizures per cluster",
            "Cluster days twice this month; typically three - four seizures in 24 h",
        )
        == "2 cluster per month, 3 to 4 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_times_month() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "3 per month",
            "Morning clusters 3×/month; ~three - four events over 90 min",
        )
        == "3 cluster per month, 3 to 4 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_quarterly_cluster_episode() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per 3 months",
            "Quarterly clusters with one convulsions per episode",
        )
        == "1 cluster per 3 month, 1 per cluster"
    )


def test_repair_prediction_label_with_evidence_uses_clinic_date_for_year_to_date() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "5 per year",
            "just five generalised tonic-clonic seizures documented this year to date",
            context_text="Clinic Date: 24 February 2016",
        )
        == "5 per 2 month"
    )


def test_repair_prediction_label_with_evidence_uses_clinic_date_for_so_far_year() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 per year",
            "four tonic seizures documented in 2015 so far",
            context_text="Clinic Date: 24 January 2015",
        )
        == "4 per month"
    )


def test_repair_prediction_label_with_evidence_does_not_count_window_as_event_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "abs monthly",
            "Over the past six months he describes brief events occurring abs monthly",
        )
        == "1 per month"
    )
