from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_abstention_review_predeclaration,
)


def _rq10_row(
    *,
    source_row_index: int = 101,
    primary_class: str = "underdetermined_note",
    clinically_defensible: bool = False,
    possible_gold_weakness: bool = False,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "rq10_primary_class": primary_class,
        "clinically_defensible_alternative": clinically_defensible,
        "benchmark_convention_flag": primary_class == "benchmark_convention_dominated",
        "possible_gold_weakness": possible_gold_weakness,
        "likely_gold_defect": False,
        "hidden_families": ["unknown_boundary"],
        "selected_evidence": "No clear current seizure frequency is documented.",
        "selected_evidence_exact": True,
        "selected_source_ids_valid": True,
        "primary_predicted_label": "unknown",
        "gold_label": "1 per month",
        "gold_reference": "monthly events",
        "primary_purist_correct": False,
        "primary_pragmatic_correct": False,
        "first_failure_owner": "candidate_generation",
        "first_failure_reason": "gold state absent from candidate set",
        "adjudication_rationale": "Gold/reference is underdetermined.",
    }


def test_rq9_predeclaration_routes_rq10_classes_to_distinct_actions() -> None:
    rows, metadata = rq9_abstention_review_predeclaration.build_rq9_predeclaration_rows(
        [
            _rq10_row(source_row_index=1, primary_class="underdetermined_note"),
            _rq10_row(source_row_index=2, primary_class="benchmark_convention_dominated"),
            _rq10_row(source_row_index=3, primary_class="true_extraction_failure"),
            _rq10_row(
                source_row_index=4,
                primary_class="benchmark_convention_dominated",
                clinically_defensible=True,
            ),
            _rq10_row(
                source_row_index=5,
                primary_class="underdetermined_note",
                possible_gold_weakness=True,
            ),
        ]
    )

    actions_by_index = {row["source_row_index"]: row["routing_action"] for row in rows}
    assert actions_by_index == {
        1: "abstain_or_route_unknown",
        2: "human_review_benchmark_convention",
        3: "extraction_error_analysis",
        4: "human_review_clinical_convention",
        5: "human_review_gold_reference",
    }
    assert metadata["metrics"]["prediction_blocked_rows"] == 4
    assert metadata["metrics"]["extraction_error_analysis_rows"] == 1


def test_review_packet_omits_gold_and_development_accounting_fields() -> None:
    rows, _metadata = rq9_abstention_review_predeclaration.build_rq9_predeclaration_rows(
        [_rq10_row(clinically_defensible=True)]
    )

    row = rows[0]
    review_packet = row["review_packet"]
    assert review_packet["review_bucket"] == "clinically_defensible_alternative"
    assert "gold_label" not in review_packet
    assert "gold_reference" not in review_packet
    assert "primary_purist_correct" not in review_packet
    assert row["development_accounting"]["gold_label"] == "1 per month"
    assert row["prediction_blocked_pending_review_or_abstention"] is True
