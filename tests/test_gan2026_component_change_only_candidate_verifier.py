from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    change_only_candidate_verifier,
)


def test_change_verifier_switches_only_when_all_strict_fields_pass() -> None:
    row = {
        "clinical_text": "The patient reports seizures every week.",
        "current_label": "unknown",
        "proposed_label": "1 per week",
        "gold_label": "1 per week",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["seizures every week"],
          "reason": "The proposed label is directly supported."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert errors == []
    assert decision["action"] == "switch_to_proposed"
    assert decision["label"] == "1 per week"
    assert decision["purist_correct"] is True


def test_change_verifier_keeps_current_when_any_strict_field_fails() -> None:
    row = {
        "clinical_text": "The patient reports seizures every week.",
        "current_label": "unknown",
        "proposed_label": "1 per week",
        "gold_label": "1 per week",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": false,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["seizures every week"],
          "reason": "Another event may be higher."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["action"] == "switch_to_proposed"
    assert decision["label"] == "unknown"
    assert decision["purist_correct"] is False


def test_change_verifier_requires_exact_quote_for_switch() -> None:
    row = {
        "clinical_text": "The patient reports seizures every week.",
        "current_label": "unknown",
        "proposed_label": "1 per week",
        "gold_label": "1 per week",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["weekly seizures"],
          "reason": "Paraphrased evidence."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "unknown"
    assert decision["all_evidence_quotes_exact"] is False


def test_change_verifier_requires_parseable_proposed_label_for_switch() -> None:
    row = {
        "clinical_text": "The patient reports seizures every six days.",
        "current_label": "1 per 6 day",
        "proposed_label": "every six days",
        "gold_label": "1 per 6 day",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["seizures every six days"],
          "reason": "The proposed wording is directly supported."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["action"] == "switch_to_proposed"
    assert decision["label"] == "1 per 6 day"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_unknown_over_seizure_free_duration_only() -> None:
    row = {
        "clinical_text": "There have been no definite seizures since the last review.",
        "current_label": "seizure free for multiple year",
        "proposed_label": "unknown",
        "gold_label": "seizure free for multiple month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["no definite seizures since the last review"],
          "reason": "The duration is less precise than multiple years."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "seizure free for multiple year"
    assert decision["purist_correct"] is True


def test_change_verifier_allows_unknown_over_seizure_free_with_active_event() -> None:
    row = {
        "clinical_text": "The patient reports myoclonic jerks and tongue soreness.",
        "current_label": "seizure free for multiple year",
        "proposed_label": "unknown",
        "gold_label": "unknown",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["myoclonic jerks and tongue soreness"],
          "reason": "Active seizure-like events are present but unquantified."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "unknown"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_subtype_narrowing_benchmark_convention() -> None:
    row = {
        "clinical_text": "The letter reports four absences and one myoclonic seizure.",
        "current_label": "5 per month",
        "proposed_label": "4 per month",
        "gold_label": "5 per month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["four absences and one myoclonic seizure"],
          "reason": "The proposed label refers only to the absence seizures."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "5 per month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_uncertain_seizure_free_override() -> None:
    row = {
        "clinical_text": "The patient has brief moments without clear seizures.",
        "current_label": "seizure free for multiple year",
        "proposed_label": "1 per multiple week",
        "gold_label": "seizure free for multiple month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["brief moments without clear seizures"],
          "reason": "These are suggestive of possible seizure activity."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "seizure free for multiple year"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_partial_window_narrowing() -> None:
    row = {
        "clinical_text": "Typical frequency is one per month despite a downward trend.",
        "current_label": "1 per month",
        "proposed_label": "1 per 8 week",
        "gold_label": "1 per month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["downward trend"],
          "reason": "The most recent calendar month has fewer events."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "1 per month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_named_semiology_narrowing() -> None:
    row = {
        "clinical_text": (
            "Generalised tonic-clonic seizures are rare, typically 3 events per year. "
            "Focal sensory seizures occur several times each week."
        ),
        "current_label": "multiple per week",
        "proposed_label": "3 per year",
        "gold_label": "multiple per week",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": [
            "Generalised tonic-clonic seizures are rare, typically 3 events per year."
          ],
          "reason": "The proposed label accurately reflects generalised tonic-clonic seizures."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "multiple per week"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_single_event_unknown_to_rate() -> None:
    row = {
        "clinical_text": (
            "Outside of nights with curtailed rest, no events have occurred in the past "
            "eight weeks. The last event was on 10 September."
        ),
        "current_label": "unknown",
        "proposed_label": "1 per month",
        "gold_label": "unknown",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["The last event was on 10 September."],
          "reason": "Only one seizure in the past eight weeks supports 1 per month."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "unknown"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_imprecise_cluster_candidate_when_count_exact() -> None:
    row = {
        "clinical_text": "This month he had two clusters; each ~five focal seizures.",
        "current_label": "5 per month",
        "proposed_label": "2 cluster per month, multiple per cluster",
        "gold_label": "5 per month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["This month he had two clusters; each ~five focal seizures."],
          "reason": "Each ~five per cluster is clinically relevant."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "5 per month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_arithmetic_contradiction() -> None:
    row = {
        "clinical_text": "She experiences two generalised tonic-clonic seizures every 2 months.",
        "current_label": "2 per week",
        "proposed_label": "1 per 2 month",
        "gold_label": "2 per week",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": [
            "She experiences two generalised tonic-clonic seizures every 2 months."
          ],
          "reason": "This equates to 1 per month, so the proposed label is best."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "2 per week"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_history_only_unknown_override() -> None:
    row = {
        "clinical_text": "There have been no further events since medication started.",
        "current_label": "5 per 4 month",
        "proposed_label": "unknown",
        "gold_label": "5 per 4 month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["There have been no further events since medication started."],
          "reason": "There is no current/recent seizure frequency to report."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "5 per 4 month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_clinically_more_significant_narrowing() -> None:
    row = {
        "clinical_text": "Focal aware seizures occur every few days; two impaired events.",
        "current_label": "1 per 3 to 4 day",
        "proposed_label": "2 per month",
        "gold_label": "1 per 3 to 4 day",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["two impaired events"],
          "reason": "The proposed label captures clinically more significant events."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "1 per 3 to 4 day"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_recent_month_diary_narrowing() -> None:
    row = {
        "clinical_text": "The six-month diary totals four focal seizures.",
        "current_label": "4 per 6 month",
        "proposed_label": "1 to 2 per month",
        "gold_label": "4 per 6 month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["The six-month diary totals four focal seizures."],
          "reason": "The most recent month supports 1 to 2 per month."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "4 per 6 month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_exact_label_reformulation() -> None:
    row = {
        "clinical_text": "He recorded three in September, four in August, and three in July.",
        "current_label": "10 per 3 month",
        "proposed_label": "3 to 5 per month",
        "gold_label": "10 per 3 month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": [
            "He recorded three in September, four in August, and three in July."
          ],
          "reason": "The current label is less precise than the monthly rate."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "10 per 3 month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_unclear_this_month_override() -> None:
    row = {
        "clinical_text": "Last month she had four clusters. Cluster frequency unclear this month.",
        "current_label": "4 cluster per month, multiple per cluster",
        "proposed_label": "unknown",
        "gold_label": "4 cluster per month, multiple per cluster",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["Cluster frequency unclear this month"],
          "reason": "The current label is based on last month, not this month."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "4 cluster per month, multiple per cluster"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_uncertain_reporting_override() -> None:
    row = {
        "clinical_text": "The diary reports 76 seizure days over 12 months.",
        "current_label": "76 per 12 month",
        "proposed_label": "unknown",
        "gold_label": "76 per 12 month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": ["The diary reports 76 seizure days over 12 months."],
          "reason": "This assumes one seizure per seizure day and is not reliable or verifiable."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "76 per 12 month"
    assert decision["purist_correct"] is True


def test_change_verifier_blocks_composite_then_seizure_free_label() -> None:
    row = {
        "clinical_text": "He had two seizures in the following week. No further seizures.",
        "current_label": "2 per month",
        "proposed_label": "2 seizures in last week then seizure free",
        "gold_label": "2 per month",
    }
    parsed, errors = change_only_candidate_verifier.parse_output(
        """
        {
          "recommendation": "switch_to_proposed",
          "proposed_supported": true,
          "proposed_best_current_answer": true,
          "current_label_has_material_error": true,
          "confidence": "high",
          "evidence_quotes": [
            "He had two seizures in the following week. No further seizures."
          ],
          "reason": "The proposed label accurately summarizes the recent seizure-free period."
        }
        """
    )

    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=errors,
    )

    assert decision["label"] == "2 per month"
    assert decision["purist_correct"] is True


def test_change_verifier_summary_reports_transitions() -> None:
    summary = change_only_candidate_verifier.summarize_rows(
        [
            {
                "transition": "W_to_C",
                "recommendation": "switch_to_proposed",
                "current_purist_correct": False,
            },
            {
                "transition": "C_to_C",
                "recommendation": "keep_current",
                "current_purist_correct": True,
            },
        ]
    )

    assert summary["base_correct_rows"] == 1
    assert summary["projected_correct_rows"] == 2
    assert summary["transition_counts"] == {"C_to_C": 1, "W_to_C": 1}
    assert summary["decision"] == "promote_candidate"
