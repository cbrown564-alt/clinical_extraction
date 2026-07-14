from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cli.diagnosis_component_comparison import (  # noqa: E501
    build_parser,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_component_comparison import (  # noqa: E501
    summarize_residual_changes,
)


def test_summarize_residual_changes_separates_reviewed_fixes_and_new_residuals() -> None:
    baseline = {
        ("A", "missed", "focal epilepsy"),
        ("B", "spurious", "stroke"),
    }
    candidate = {
        ("B", "spurious", "stroke"),
        ("C", "spurious", "tonic clonic seizures"),
    }
    decisions = {
        ("A", "missed", "focal epilepsy"): {
            "triage": "extraction_error",
            "mechanism": "missed_named_diagnosis",
        },
        ("B", "spurious", "stroke"): {
            "triage": "representation",
            "mechanism": "likely_gold_omission",
        },
    }

    summary = summarize_residual_changes(
        baseline_keys=baseline,
        candidate_keys=candidate,
        decisions=decisions,
    )

    assert summary["resolved_review_rows"] == 1
    assert summary["remaining_review_rows"] == 1
    assert summary["new_residual_rows"] == 1
    assert summary["resolved_triage_counts"] == {"extraction_error": 1}
    assert summary["resolved_mechanism_counts"] == {"missed_named_diagnosis": 1}
    assert summary["new_residuals"] == [
        {
            "letter_id": "C",
            "direction": "spurious",
            "concept": "tonic clonic seizures",
        }
    ]


def test_component_comparison_cli_defaults_to_the_frozen_dev140_artifacts() -> None:
    args = build_parser().parse_args([])

    assert args.audit_summary_json.name.endswith("20260714.json")
    assert args.llm_candidate_jsonl.name.startswith(
        "exectv2_diagnosis_llm_only_candidate_dev140"
    )
