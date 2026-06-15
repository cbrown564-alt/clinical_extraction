from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    consensus_fresh_agreement_selector as selector,
)


def test_accepts_consensus_only_when_fresh_evidence_agrees() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", False, gold_monthly_frequency=30.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per day", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 per day", True),
        ],
    )

    assert rows[0]["selector_action"] == "accept_consensus_fresh_agreement"
    assert rows[0]["selected_label"] == "1 per day"
    assert rows[0]["transition_vs_deterministic"] == {
        "label_changed": True,
        "purist": "wrong_to_correct",
    }


def test_keeps_deterministic_when_fresh_evidence_disagrees_with_consensus() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per day", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "2 per day", False),
        ],
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selected_label"] == "unknown"
    assert rows[0]["transition_vs_deterministic"] == {
        "label_changed": False,
        "purist": "unchanged_correct",
    }


def test_summary_reports_selector_precision_and_boundary_bands() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", False, gold_monthly_frequency=30.0),
            _det_row(2, "1 per month", True, gold_monthly_frequency=1.0),
            _det_row(3, "seizure free", True, gold_monthly_frequency=0.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per day", True),
            _consensus_row(2, "2 per month", False),
            _consensus_row(3, "seizure free", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 per day", True),
            _fresh_row(2, "2 per month", False),
            _fresh_row(3, "unknown", False),
        ],
    )

    summary = selector.summarize_rows(rows)

    assert summary["deterministic_purist_correct"] == 2
    assert summary["selected_purist_correct"] == 2
    assert summary["changed_labels"] == 2
    assert summary["wrong_to_correct"] == 1
    assert summary["correct_to_wrong"] == 1
    assert summary["changed_label_precision"] == 0.5
    assert summary["summary_by_band"]["band_daily"]["net_purist_gain"] == 1
    assert summary["summary_by_band"]["band_monthly"]["net_purist_gain"] == -1
    assert summary["summary_by_band"]["band_zero"]["changed_labels"] == 0


def test_v02_suppresses_no_reference_origin_switches() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "no seizure frequency reference",
                True,
                gold_monthly_frequency=None,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "multiple per week", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "multiple per week", False),
        ],
        policy="nonboundary_precision_v0_2",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_2_VERSION
    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert (
        rows[0]["selector_gate"]
        == "nonboundary_precision_v0_2:deterministic_no_reference_origin"
    )
    assert rows[0]["selected_label"] == "no seizure frequency reference"


def test_v02_suppresses_unknown_and_seizure_free_replacements() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "2 per month", True, gold_monthly_frequency=2.0),
            _det_row(2, "2 per month", True, gold_monthly_frequency=2.0),
        ],
        consensus_rows=[
            _consensus_row(1, "unknown", False),
            _consensus_row(2, "seizure free", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "unknown", False),
            _fresh_row(2, "seizure free", False),
        ],
        policy="nonboundary_precision_v0_2",
    )

    assert [row["selector_action"] for row in rows] == [
        "keep_deterministic_baseline",
        "keep_deterministic_baseline",
    ]
    assert [row["selector_gate"] for row in rows] == [
        "nonboundary_precision_v0_2:boundary_replacement:unknown",
        "nonboundary_precision_v0_2:boundary_replacement:seizure_free",
    ]


def test_v02_allows_nonboundary_fresh_agreed_consensus_switch() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per year", False, gold_monthly_frequency=30.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per day", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 per day", True),
        ],
        policy="nonboundary_precision_v0_2",
    )

    assert rows[0]["selector_action"] == "accept_consensus_fresh_agreement"
    assert rows[0]["selector_gate"] == "nonboundary_precision_v0_2"
    assert rows[0]["selected_label"] == "1 per day"


def test_v03_suppresses_deterministic_unknown_origin_switches() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "2 per month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "2 per month", False),
        ],
        policy="specific_label_precision_v0_3",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_3_VERSION
    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert (
        rows[0]["selector_gate"]
        == "specific_label_precision_v0_3:deterministic_boundary_origin:unknown"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v03_suppresses_ambiguous_other_replacements() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "2 per month", True, gold_monthly_frequency=2.0),
        ],
        consensus_rows=[
            _consensus_row(1, "2 per 5 months", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "2 per 5 months", False),
        ],
        policy="specific_label_precision_v0_3",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert (
        rows[0]["selector_gate"]
        == "specific_label_precision_v0_3:uncertain_or_ambiguous_replacement:other"
    )
    assert rows[0]["selected_label"] == "2 per month"


def test_v03_allows_specific_fresh_agreed_consensus_switch() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per year", False, gold_monthly_frequency=30.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per day", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 per day", True),
        ],
        policy="specific_label_precision_v0_3",
    )

    assert rows[0]["selector_action"] == "accept_consensus_fresh_agreement"
    assert rows[0]["selector_gate"] == "specific_label_precision_v0_3"
    assert rows[0]["selected_label"] == "1 per day"


def test_v04_suppresses_cluster_label_demotions() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "3 cluster per month, multiple per cluster",
                True,
                gold_monthly_frequency=6.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "3 per month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "3 per month", False),
        ],
        policy="cluster_cadence_precision_v0_4",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_4_VERSION
    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == "cluster_cadence_precision_v0_4:cluster_label_demoted"
    assert rows[0]["selected_label"] == "3 cluster per month, multiple per cluster"


def test_v04_suppresses_cluster_cadence_changes() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "5 cluster per month, multiple per cluster",
                True,
                gold_monthly_frequency=10.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "1 cluster per month, multiple per cluster", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 cluster per month, multiple per cluster", False),
        ],
        policy="cluster_cadence_precision_v0_4",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert (
        rows[0]["selector_gate"]
        == "cluster_cadence_precision_v0_4:cluster_cadence_changed"
    )
    assert rows[0]["selected_label"] == "5 cluster per month, multiple per cluster"


def test_v04_allows_same_cadence_cluster_burden_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "2 to 3 cluster per month, multiple per cluster",
                False,
                gold_monthly_frequency=12.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "2 to 3 cluster per month, 5 per cluster", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "2 to 3 cluster per month, 5 per cluster", True),
        ],
        policy="cluster_cadence_precision_v0_4",
    )

    assert rows[0]["selector_action"] == "accept_consensus_fresh_agreement"
    assert rows[0]["selector_gate"] == "cluster_cadence_precision_v0_4"
    assert rows[0]["selected_label"] == "2 to 3 cluster per month, 5 per cluster"


def test_v05_rescues_deterministic_seizure_free_overreach_to_unknown() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "seizure free for multiple year",
                False,
                gold_monthly_frequency=None,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "seizure free for multiple year", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "unknown", True),
        ],
        policy="fresh_boundary_rescue_v0_5",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_5_VERSION
    assert rows[0]["selector_action"] == "accept_fresh_boundary_rescue"
    assert rows[0]["selector_gate"] == (
        "fresh_boundary_rescue_v0_5:"
        "deterministic_seizure_free_to_fresh_uncertain_boundary"
    )
    assert rows[0]["selected_label"] == "unknown"
    assert rows[0]["score_layers"]["selected"]["source"] == "fresh_evidence"
    assert rows[0]["transition_vs_deterministic"]["purist"] == "wrong_to_correct"


def test_v05_rescues_deterministic_seizure_free_overreach_to_no_reference() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "seizure free for 8 month",
                False,
                gold_monthly_frequency=None,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "seizure free for 8 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "no seizure frequency reference", True),
        ],
        policy="fresh_boundary_rescue_v0_5",
    )

    assert rows[0]["selector_action"] == "accept_fresh_boundary_rescue"
    assert rows[0]["selected_label"] == "no seizure frequency reference"


def test_v05_rescues_no_reference_origin_to_fresh_seizure_free() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "no seizure frequency reference",
                False,
                gold_monthly_frequency=0.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "no seizure frequency reference", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "seizure free for multiple year", True),
        ],
        policy="fresh_boundary_rescue_v0_5",
    )

    assert rows[0]["selector_action"] == "accept_fresh_boundary_rescue"
    assert rows[0]["selector_gate"] == (
        "fresh_boundary_rescue_v0_5:"
        "deterministic_no_reference_to_fresh_seizure_free"
    )
    assert rows[0]["selected_label"] == "seizure free for multiple year"


def test_v05_keeps_v04_cluster_cadence_protection() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "5 cluster per month, multiple per cluster",
                True,
                gold_monthly_frequency=10.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "1 cluster per month, multiple per cluster", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "1 cluster per month, multiple per cluster", False),
        ],
        policy="fresh_boundary_rescue_v0_5",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert (
        rows[0]["selector_gate"]
        == "fresh_boundary_rescue_v0_5:cluster_cadence_changed"
    )
    assert rows[0]["selected_label"] == "5 cluster per month, multiple per cluster"


def test_v05_does_not_relax_unknown_origin_to_specific_rate() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "2 per month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(1, "2 per month", False),
        ],
        policy="fresh_boundary_rescue_v0_5",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "fresh_boundary_rescue_v0_5:deterministic_boundary_origin:unknown"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v06_allows_profile_supported_seizure_free_to_unknown_rescue() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "seizure free for 8 month",
                False,
                gold_monthly_frequency=None,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "seizure free for 8 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "unknown",
                True,
                boundary_profile=["last_event_only", "not seizure_free"],
            ),
        ],
        policy="profile_guard_boundary_rescue_v0_6",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_6_VERSION
    assert rows[0]["selector_action"] == "accept_fresh_boundary_rescue"
    assert rows[0]["selector_gate"] == (
        "profile_guard_boundary_rescue_v0_6:"
        "seizure_free_to_uncertain_supported"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v06_blocks_fresh_unknown_when_profile_affirms_seizure_free() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "seizure free for 6 month",
                True,
                gold_monthly_frequency=0.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "seizure free for 6 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "unknown",
                False,
                boundary_profile=[
                    "explicit seizure-free duration",
                    "zero-event interval stated",
                ],
            ),
        ],
        policy="profile_guard_boundary_rescue_v0_6",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "profile_guard_boundary_rescue_v0_6:profile_affirms_seizure_free"
    )
    assert rows[0]["selected_label"] == "seizure free for 6 month"


def test_v06_allows_profile_supported_no_reference_to_seizure_free_rescue() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "no seizure frequency reference",
                False,
                gold_monthly_frequency=0.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "no seizure frequency reference", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "seizure free for multiple year",
                True,
                boundary_profile=[
                    "no_reference boundary",
                    "no current or recent epileptic seizure frequency evidence",
                ],
            ),
        ],
        policy="profile_guard_boundary_rescue_v0_6",
    )

    assert rows[0]["selector_action"] == "accept_fresh_boundary_rescue"
    assert rows[0]["selector_gate"] == (
        "profile_guard_boundary_rescue_v0_6:"
        "no_reference_to_seizure_free_supported"
    )
    assert rows[0]["selected_label"] == "seizure free for multiple year"


def test_v06_blocks_no_reference_to_seizure_free_from_absence_only_profile() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "no seizure frequency reference",
                True,
                gold_monthly_frequency=None,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "no seizure frequency reference", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "seizure free for multiple year",
                False,
                boundary_profile=["no positive seizure-frequency evidence"],
            ),
        ],
        policy="profile_guard_boundary_rescue_v0_6",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "profile_guard_boundary_rescue_v0_6:profile_only_no_reference_absence"
    )
    assert rows[0]["selected_label"] == "no seizure frequency reference"


def test_v07_allows_unknown_origin_with_explicit_count_and_usable_window() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", False, gold_monthly_frequency=1.0),
        ],
        consensus_rows=[
            _consensus_row(1, "2 per 2 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "2 per 2 month",
                True,
                boundary_profile=[
                    "explicit count plus usable follow-up period",
                    "defined observation period",
                ],
            ),
        ],
        policy="unknown_count_window_rescue_v0_7",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_7_VERSION
    assert rows[0]["selector_action"] == "accept_unknown_count_window_rescue"
    assert rows[0]["selector_gate"] == (
        "unknown_count_window_rescue_v0_7:explicit_count_window_supported"
    )
    assert rows[0]["selected_label"] == "2 per 2 month"
    assert rows[0]["transition_vs_deterministic"]["purist"] == "wrong_to_correct"


def test_v07_blocks_unknown_origin_last_event_only_rate() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per 4 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "1 per 4 month",
                False,
                boundary_profile=[
                    "explicit last event date",
                    "none since",
                    "duration since last event is approximately 4 months",
                ],
            ),
        ],
        policy="unknown_count_window_rescue_v0_7",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v07_blocks_unknown_origin_open_ended_since_starting_rate() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "3 per month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "3 per month",
                False,
                boundary_profile=[
                    "explicit count plus window attempted",
                    "since starting ketogenic diet",
                    "start date unclear",
                ],
            ),
        ],
        policy="unknown_count_window_rescue_v0_7",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v07_blocks_unknown_origin_vague_count_rate() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", True, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "multiple per month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "multiple per month",
                True,
                boundary_profile=[
                    "usable observation period",
                    "vague count several seizures",
                ],
            ),
        ],
        policy="unknown_count_window_rescue_v0_7",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v07_requires_consensus_and_fresh_agreement_for_unknown_rescue() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "unknown", False, gold_monthly_frequency=1.0),
        ],
        consensus_rows=[
            _consensus_row(1, "2 per 2 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "3 per 3 month",
                True,
                boundary_profile=[
                    "explicit count plus usable follow-up period",
                    "defined observation period",
                ],
            ),
        ],
        policy="unknown_count_window_rescue_v0_7",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "unknown_count_window_rescue_v0_7:fresh_consensus_disagree"
    )
    assert rows[0]["selected_label"] == "unknown"


def test_v08_accepts_parseable_denominator_window_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per 5 to 7 day", False, gold_monthly_frequency=3.5),
        ],
        consensus_rows=[
            _consensus_row(1, "11 per 3 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "11 per 3 month",
                True,
                boundary_profile=[
                    "current/recent frequency",
                    "denominator/window",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_8_VERSION
    assert rows[0]["selector_action"] == "accept_parseable_denominator_window_refinement"
    assert rows[0]["selector_gate"] == (
        "parseable_denominator_window_refinement_v0_8:"
        "profile_supported_parseable_refinement"
    )
    assert rows[0]["selected_label"] == "11 per 3 month"
    assert rows[0]["transition_vs_deterministic"]["purist"] == "wrong_to_correct"


def test_v08_accepts_explicit_current_frequency_range_denominator_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per day", False, gold_monthly_frequency=0.6),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per 6 to 8 week", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "1 per 6 to 8 week",
                True,
                boundary_profile=[
                    "explicit current frequency",
                    "no seizure-free or unknown boundary",
                    "cluster/seizure frequency clearly stated",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_action"] == "accept_parseable_denominator_window_refinement"
    assert rows[0]["selected_label"] == "1 per 6 to 8 week"


def test_v08_accepts_explicit_count_window_cluster_count_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "3 per week", False, gold_monthly_frequency=3.0),
        ],
        consensus_rows=[
            _consensus_row(1, "4 per 2 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "4 per 2 month",
                True,
                boundary_profile=[
                    "explicit count of 5 events over approximately 6 weeks",
                    "no evidence for seizure-free, unknown, or no_reference",
                    "highest current/recent frequency is cluster count",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_action"] == "accept_parseable_denominator_window_refinement"
    assert rows[0]["selected_label"] == "4 per 2 month"


def test_v08_blocks_highest_active_semiology_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "3 to 4 per 15 month", True, gold_monthly_frequency=0.23),
        ],
        consensus_rows=[
            _consensus_row(1, "2 to 3 per 15 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "2 to 3 per 15 month",
                False,
                boundary_profile=[
                    "current/recent frequency",
                    "highest active semiology",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "parseable_denominator_window_refinement_v0_8:"
        "unsafe_parseable_refinement_profile"
    )
    assert rows[0]["selected_label"] == "3 to 4 per 15 month"


def test_v08_blocks_seizure_free_interval_refinement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "9 per 3 month", True, gold_monthly_frequency=3.0),
        ],
        consensus_rows=[
            _consensus_row(1, "8 per 2 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "8 per 2 month",
                False,
                boundary_profile=[
                    "explicit recent seizure counts",
                    "no seizure-free interval",
                    "current/recent frequency evidence",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "parseable_denominator_window_refinement_v0_8:"
        "unsafe_parseable_refinement_profile"
    )
    assert rows[0]["selected_label"] == "9 per 3 month"


def test_v08_blocks_unparseable_consensus_replacement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per day", True, gold_monthly_frequency=30.0),
        ],
        consensus_rows=[
            _consensus_row(1, "several per month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "several per month",
                False,
                boundary_profile=[
                    "current/recent frequency",
                    "denominator/window",
                ],
            ),
        ],
        policy="parseable_denominator_window_refinement_v0_8",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "parseable_denominator_window_refinement_v0_8:"
        "replacement_not_parseable_specific_rate"
    )
    assert rows[0]["selected_label"] == "1 per day"


def test_v09_accepts_normalized_equivalent_consensus_fresh_disagreement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "12 per month", False, gold_monthly_frequency=1.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per 1 month", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "1 per month",
                True,
                boundary_profile=[
                    "explicit last event date",
                    "explicit seizure-free interval",
                    "duration since last event is just over 4 weeks",
                    "no conflicting current/recent frequency evidence",
                ],
            ),
        ],
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )

    assert rows[0]["selector_version"] == selector.SELECTOR_V0_9_VERSION
    assert rows[0]["selector_action"] == "accept_normalized_equivalent_agreement"
    assert rows[0]["selector_gate"] == (
        "semantic_equiv_unknown_uncertainty_v0_9:"
        "normalized_equivalent_consensus_fresh"
    )
    assert rows[0]["selected_label"] == "1 per month"
    assert rows[0]["transition_vs_deterministic"]["purist"] == "wrong_to_correct"


def test_v09_blocks_non_equivalent_consensus_fresh_disagreement() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "2 per week", True, gold_monthly_frequency=8.0),
        ],
        consensus_rows=[
            _consensus_row(1, "1 per 3 month", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "2 per week",
                True,
                boundary_profile=[
                    "highest current clinically active burden",
                    "explicit numeric frequency for absence seizures",
                    "multiple active semiologies",
                ],
            ),
        ],
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == "fresh_evidence_disagrees_with_consensus"
    assert rows[0]["selected_label"] == "2 per week"


def test_v09_accepts_specific_rate_to_unknown_uncertainty_rescue() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(1, "1 per 5 day", False, gold_monthly_frequency=None),
        ],
        consensus_rows=[
            _consensus_row(1, "unknown", True),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "unknown",
                True,
                boundary_profile=[
                    "unknown_frequency",
                    "no explicit count or rate",
                    "device logs suggest clusters but no counts",
                    "patient unsure if episodes correspond to device alerts",
                ],
            ),
        ],
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )

    assert rows[0]["selector_action"] == "accept_unknown_uncertainty_rescue"
    assert rows[0]["selector_gate"] == (
        "semantic_equiv_unknown_uncertainty_v0_9:"
        "specific_rate_to_unknown_uncertainty_supported"
    )
    assert rows[0]["selected_label"] == "unknown"
    assert rows[0]["transition_vs_deterministic"]["purist"] == "wrong_to_correct"


def test_v09_blocks_unknown_rescue_when_cluster_burden_fully_specified() -> None:
    rows = selector.build_selector_rows(
        deterministic_rows=[
            _det_row(
                1,
                "3 cluster per 6 week, 2 to 4 per cluster",
                True,
                gold_monthly_frequency=9.0,
            ),
        ],
        consensus_rows=[
            _consensus_row(1, "unknown", False),
        ],
        fresh_evidence_rows=[
            _fresh_row(
                1,
                "unknown",
                False,
                boundary_profile=[
                    "cluster burden present",
                    "cluster frequency and events per cluster both specified",
                    "no explicit recurring rate for clusters or events",
                ],
            ),
        ],
        policy="semantic_equiv_unknown_uncertainty_v0_9",
    )

    assert rows[0]["selector_action"] == "keep_deterministic_baseline"
    assert rows[0]["selector_gate"] == (
        "semantic_equiv_unknown_uncertainty_v0_9:"
        "unknown_uncertainty_profile_blocked"
    )
    assert rows[0]["selected_label"] == "3 cluster per 6 week, 2 to 4 per cluster"


def _det_row(
    source_row_index: int,
    final_label: str,
    purist_correct: bool,
    *,
    gold_monthly_frequency: float | None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "final_label": final_label,
        "comparison": {"purist_correct": purist_correct},
        "reference": {
            "gold_label": final_label,
            "gold_monthly_frequency": gold_monthly_frequency,
            "row_ok": True,
        },
    }


def _consensus_row(
    source_row_index: int,
    final_label: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "consensus_final_label": final_label,
        "consensus_comparison": {"purist_correct": purist_correct},
        "consensus_decision": {"reason": "accepted_unanimous_exact_label"},
    }


def _fresh_row(
    source_row_index: int,
    final_label: str,
    purist_correct: bool,
    *,
    boundary_profile: list[str] | None = None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "fresh_evidence_decision_record": {
            "action": "replace_with_fresh_evidence_final",
            "boundary_profile": boundary_profile or ["synthetic test profile"],
            "uncertainty": "low",
        },
        "decision_record": {"final_label": final_label},
        "score_layers": {
            "final": {"comparison": {"purist_correct": purist_correct}},
        },
    }
