import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_review_workbench import (  # noqa: E501
    build_review_workbench,
)


def test_build_review_workbench_embeds_rows_and_has_no_external_dependencies(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "review.html"
    row = {
        "review_key": "EA0001|missed|focal epilepsy",
        "letter_id": "EA0001",
        "direction": "missed",
        "normalized_concept": "focal epilepsy",
        "methods": ["llm_only"],
        "note_text": "Diagnosis: focal epilepsy",
        "gold_diagnosis_mentions": [],
        "method_records": {},
    }
    audit_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    summary_path.write_text(
        json.dumps({"gold_sha256": "gold-digest", "union": {"review_row_count": 1}}),
        encoding="utf-8",
    )

    build_review_workbench(
        audit_jsonl=audit_path,
        summary_json=summary_path,
        out_html=output_path,
    )

    html = output_path.read_text(encoding="utf-8")
    assert "EA0001|missed|focal epilepsy" in html
    assert 'id="audit-data"' in html
    assert 'id="audit-summary"' in html
    assert 'id="case-queue"' in html
    assert 'id="decision-form"' in html
    assert "localStorage" in html
    assert "https://" not in html
    assert "http://" not in html
