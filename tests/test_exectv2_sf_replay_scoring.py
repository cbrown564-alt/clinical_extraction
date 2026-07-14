"""Tests for retained SeizureFrequency replay-row scoring."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.sf_replay_scoring import (
    summarize_sf_rows,
)


def test_summarize_sf_rows_reports_recovery_and_candidate_counts() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 1,
            "n_candidate_spans": 3,
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "seizures",
                    "attributes": {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "FrequencyChange": "Increased",
                    },
                }
            ],
            "predicted_mentions": [
                {
                    "text": "seizures",
                    "attributes": {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "FrequencyChange": "Increased",
                    },
                    "evidence": "the seizures have returned",
                }
            ],
        }
    ]

    summary = summarize_sf_rows(rows)

    assert summary["clinical_recovery"]["seizure_frequency"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_candidate_spans"] == 3


def test_summarize_sf_rows_accepts_empty_input() -> None:
    assert summarize_sf_rows([]) == {"examples": 0}
