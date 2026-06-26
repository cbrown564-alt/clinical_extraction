"""Validation-set extraction patterns for Gan2026 pipeline v1.

Cluster, shorthand, saturation, and scoring tests split from test_gan2026_pipeline_v1.py.
"""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_frequency_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)


def _record(note_text: str, gold_label: str = "unknown") -> GanRecord:
    return GanRecord(
        source_row_index=1,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Over the past fortnight she describes a run of brief events, "
            "with three short episodes occurring on separate days.",
            "1 cluster per 2 week, 3 per cluster",
            (
                "Over the past fortnight she describes a run of brief events, "
                "with three short episodes occurring on separate days"
            ),
        ),
        (
            "Over the past month, the patient reports a cluster of short events on multiple days.",
            "multiple cluster per month, multiple per cluster",
            ("Over the past month, the patient reports a cluster of short events on multiple days"),
        ),
        (
            "Over the past four weeks he reports 2 clusters this month; "
            "each approx five absences in the morning.",
            "2 cluster per month, 5 per cluster",
            "2 clusters this month; each approx five absences",
        ),
        (
            "Cluster burden increased since 07/Dec/2023; now weekly, five per cluster.",
            "1 cluster per week, 5 per cluster",
            "weekly, five per cluster",
        ),
        (
            "Since his last review, he reports brief episodes after work with clusters on "
            "several mornings each week, sometimes repeating two or three times within the "
            "same morning.",
            "multiple cluster per week, 2 to 3 per cluster",
            "on several mornings each week",
        ),
        (
            "Over the past six weeks, he has brief nocturnal bunching on 3-4 nights "
            "per week, with several brief episodes grouped together during the night.",
            "3 to 4 cluster per week, multiple per cluster",
            "on 3-4 nights per week",
        ),
        (
            "He has been having clusters on several evenings per fortnight, and on "
            "average each cluster involves roughly five brief spells.",
            "multiple cluster per 2 week, 5 per cluster",
            "on several evenings per fortnight",
        ),
        (
            "Monthly clusters, typically 6 to 7 seizures over 24 h.",
            "1 cluster per month, 6 to 7 per cluster",
            "Monthly clusters, typically 6 to 7 seizures over 24 h",
        ),
        (
            "New nocturnal clustering with early-morning spillover; two nocturnal "
            "clusters this month; each ~four - five events.",
            "2 cluster per month, 4 to 5 per cluster",
            "two nocturnal clusters this month; each ~four - five events",
        ),
        (
            "There have been three nocturnal clusters this month; each ~4 - 5 events.",
            "3 cluster per month, 4 to 5 per cluster",
            "three nocturnal clusters this month; each ~4 - 5 events",
        ),
        (
            "She reports 1 Travel-related clusters this month; ~4 - 6 events per episode.",
            "1 cluster per month, 4 to 6 per cluster",
            "1 Travel-related clusters this month; ~4 - 6 events per episode",
        ),
    ],
)
def test_pipeline_extracts_validation_cluster_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Seizure days: 8/30 this month.",
            "8 per month",
            "Seizure days: 8/30 this month",
        ),
        (
            "About three seizure days per week are reported.",
            "3 per week",
            "About three seizure days per week",
        ),
        # GAN-shorthand generalized forms (digit counts, no special separators):
        (
            "Clinic shorthand says TC 5/mo.",
            "5 per month",
            "TC 5/mo",
        ),
        (
            "Current frequency reported as: sz 2/wk.",
            "2 per week",
            "sz 2/wk",
        ),
        (
            "Seizures worsen, up to seven in bad weeks.",
            "7 per week",
            "up to seven in bad weeks",
        ),
        (
            "Diary shorthand says abs monthly.",
            "1 per month",
            "abs monthly",
        ),
        (
            "On their calendar, abs 8 monthly over the past three months.",
            "8 per month",
            "abs 8 monthly",
        ),
        (
            "The current clinic shorthand is q2 - 3wk.",
            "1 per 2 to 3 week",
            "q2 - 3wk",
        ),
        (
            "The current clinic shorthand is q1 - 2d.",
            "1 per 1 to 2 day",
            "q1 - 2d",
        ),
        (
            "Recent diary: seven to eight absence seizures this quarter.",
            "7 to 8 per 3 month",
            "seven to eight absence seizures this quarter",
        ),
        (
            "There were nineteen episode of status epilepticus in the past week.",
            "19 per week",
            "nineteen episode of status epilepticus in the past week",
        ),
        (
            "The diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
            "5 per 2 month",
            "Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24",
        ),
        (
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1.",
            "7 per 7 month",
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1",
        ),
    ],
)
def test_pipeline_extracts_validation_shorthand_frequency_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_kind", "expected_evidence"),
    [
        (
            "Clinic Date: 05 July 2018. Importantly, Liam has been seizure-free since 29/09/2017. "
            "Earlier in the year she had five seizures during sleep.",
            "seizure free for 9 month",
            FrequencyLabelKind.SEIZURE_FREE,
            "seizure-free since 29/09/2017",
        ),
        (
            "Clinic Date: 12 January 2019. Prior to the current improvement he had "
            "4-5 seizures per week. "
            "Last seizure on 03-Sep-2017.",
            "seizure free for 16 month",
            FrequencyLabelKind.SEIZURE_FREE,
            "Last seizure on 03-Sep-2017",
        ),
        (
            "Since the last appointment, the patient reports no definite seizure events.",
            "seizure free for multiple year",
            FrequencyLabelKind.SEIZURE_FREE,
            "no definite seizure events",
        ),
        (
            "Patient reports focal aware sensory episodes only when significantly short on sleep. "
            "The last event was on 10 September 2025 after an overnight shift.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "only when significantly short on sleep",
        ),
        (
            "Seizures happen when perimenstrual only (days -3 to +3). "
            "Outside this window she reports no events over the last six months.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "Seizures happen when perimenstrual only (days -3 to +3)",
        ),
        (
            # Phase 2 de-overfitting: note updated to use generalized notation (no asterisk)
            "Summary mentions smoker, rolled tobacco, ~3 per day. Seizures occur abs monthly.",
            "1 per month",
            FrequencyLabelKind.FREQUENCY,
            "abs monthly",
        ),
        (
            "Current medication is lamotrigine twice daily. "
            "Seizures: Seizure days: 8/30 this month.",
            "8 per month",
            FrequencyLabelKind.FREQUENCY,
            "Seizure days: 8/30 this month",
        ),
        (
            "Maintain daily seizure diary entries. Present Seizure Frequency: "
            "roughly one brief absence episode "
            "in a typical month.",
            "1 per month",
            FrequencyLabelKind.FREQUENCY,
            "one brief absence episode in a typical month",
        ),
        (
            # Phase 2 de-overfitting: note updated to use generalized notation (digit q-interval)
            "Currently events are occurring q1-2d on workdays, with near-daily auras.",
            "1 per 1 to 2 day",
            FrequencyLabelKind.FREQUENCY,
            "q1-2d",
        ),
        (
            "The median inter-seizure interval ≈ two months, with occasional clustering "
            "when sleep is restricted offshore. "
            "Warning symptoms may occur weekly.",
            "1 per 2 month",
            FrequencyLabelKind.FREQUENCY,
            "median inter-seizure interval ≈ two months",
        ),
        (
            "Possible auras and one episode of anxiety were reviewed. "
            "She describes her seizure control as "
            "Better over the past seven months.",
            "unknown",
            FrequencyLabelKind.UNKNOWN,
            "Better over the past seven months",
        ),
    ],
)
def test_pipeline_handles_late_validation_saturation_patterns(
    note_text: str,
    expected_label: str,
    expected_kind: FrequencyLabelKind,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == expected_kind
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_handles_cluster_size_with_unknown_frequency() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Clusters characterized by two focal impaired-awareness seizures; frequency unclear."
        )
    )

    assert result.output.final_value == "unknown, 2 per cluster"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.UNKNOWN


def test_pipeline_can_score_a_small_known_row_subset() -> None:
    records = {
        record.source_row_index: record
        for record in load_records_with_monthly_frequency()
        if record.source_row_index in {11118, 12383, 5555, 13485, 11434}
    }
    pipeline = Gan2026PipelineV1()
    scored_rows = []
    for record in records.values():
        result = pipeline.run(record)
        scored_rows.append(
            {
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "prediction": result.diagnostics["final_selection"]["monthly_frequency"],
            }
        )

    metrics = evaluate_frequency_records(scored_rows, prediction_key="prediction", method="purist")

    assert metrics["micro"]["accuracy"] >= 0.8
