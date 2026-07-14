import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_sensitivity import (  # noqa: E501
    build_sensitivity_report,
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_sensitivity_views_adjust_only_the_predeclared_review_rows(tmp_path: Path) -> None:
    ledger_rows = [
        {
            "review_key": "one",
            "direction": "missed",
            "methods": ["rules_only"],
            "review_decision": {
                "triage": "representation",
                "mechanism": "same_cui_representation",
            },
        },
        {
            "review_key": "two",
            "direction": "spurious",
            "methods": ["rules_only", "llm_only"],
            "review_decision": {
                "triage": "representation",
                "mechanism": "likely_gold_omission",
            },
        },
        {
            "review_key": "three",
            "direction": "missed",
            "methods": ["llm_only"],
            "review_decision": {
                "triage": "extraction_error",
                "mechanism": "missed_named_diagnosis",
            },
        },
    ]
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text(
        "".join(json.dumps(row) + "\n" for row in ledger_rows), encoding="utf-8"
    )
    audit_path = tmp_path / "audit.json"
    _write_json(
        audit_path,
        {
            "schema_version": "audit-v1",
            "split": "dev140",
            "methods": {
                "rules_only": {
                    "disagreements": {"missed": 1, "spurious": 1, "total": 2},
                    "scores": {
                        "concept_only": {
                            "gold_count": 10,
                            "pred_count": 10,
                            "recall_tp": 9,
                            "precision_tp": 9,
                            "fn": 1,
                            "fp": 1,
                        }
                    },
                },
                "llm_only": {
                    "disagreements": {"missed": 1, "spurious": 1, "total": 2},
                    "scores": {
                        "concept_only": {
                            "gold_count": 10,
                            "pred_count": 10,
                            "recall_tp": 9,
                            "precision_tp": 9,
                            "fn": 1,
                            "fp": 1,
                        }
                    },
                },
            },
        },
    )

    report = build_sensitivity_report(ledger_jsonl=ledger_path, audit_summary_json=audit_path)

    conservative = report["views"]["multiplicity_and_clinical_granularity"]
    assert conservative["review_rows_in_view"] == 1
    assert conservative["methods"]["rules_only"]["adjustments"] == {
        "forgiven_missed": 1,
        "forgiven_spurious": 0,
    }
    assert conservative["methods"]["rules_only"]["scores"]["recall"] == 1.0
    assert conservative["methods"]["rules_only"]["scores"]["precision"] == 0.9
    assert conservative["methods"]["llm_only"]["adjustments"] == {
        "forgiven_missed": 0,
        "forgiven_spurious": 0,
    }

    reviewed = report["views"]["reviewed_interpretation"]
    assert reviewed["review_rows_in_view"] == 2
    assert reviewed["methods"]["rules_only"]["adjustments"] == {
        "forgiven_missed": 1,
        "forgiven_spurious": 1,
    }
    assert reviewed["methods"]["rules_only"]["scores"]["f1"] == 1.0
    assert reviewed["methods"]["llm_only"]["adjustments"] == {
        "forgiven_missed": 0,
        "forgiven_spurious": 1,
    }


def test_sensitivity_report_rejects_audit_ledger_count_drift(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text(
        json.dumps(
            {
                "review_key": "one",
                "direction": "missed",
                "methods": ["rules_only"],
                "review_decision": {
                    "triage": "extraction_error",
                    "mechanism": "missed_named_diagnosis",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    audit_path = tmp_path / "audit.json"
    _write_json(
        audit_path,
        {
            "methods": {
                "rules_only": {
                    "disagreements": {"missed": 2, "spurious": 0, "total": 2},
                    "scores": {"concept_only": {}},
                }
            }
        },
    )

    with pytest.raises(ValueError, match="disagreement count mismatch"):
        build_sensitivity_report(ledger_jsonl=ledger_path, audit_summary_json=audit_path)
