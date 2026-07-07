from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.self_consistency import (
    build_self_consistency_report,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    path.with_suffix(".json").write_text(
        json.dumps(
            {
                "score_ladder": {
                    "headline_target": {
                        "overall": {"f1": 1.0},
                        "by_indicator": {},
                    }
                }
            }
        ),
        encoding="utf-8",
    )


def test_self_consistency_report_computes_family_cell_agreement_and_entropy(
    tmp_path: Path,
) -> None:
    letters = [
        ExectLetter(
            letter_id="EA1",
            note_text="Diagnosis: focal epilepsy. Lamotrigine 100mg bd.",
            annotations=(
                ExectAnnotation(
                    entity="Diagnosis",
                    text="focal epilepsy",
                    attributes={"Negation": "Affirmed"},
                ),
            ),
        )
    ]
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    base_row = {
        "candidate_name": "candidate",
        "letter_id": "EA1",
        "predicted_mentions": [
            {
                "entity": "Diagnosis",
                "text": "focal epilepsy",
                "attributes": {"Negation": "Affirmed"},
            }
        ],
        "gold_mentions": [],
    }
    _write_jsonl(first, [base_row])
    changed = {
        **base_row,
        "predicted_mentions": [
            {
                "entity": "Diagnosis",
                "text": "generalised epilepsy",
                "attributes": {"Negation": "Affirmed"},
            }
        ],
    }
    _write_jsonl(second, [changed])

    report = build_self_consistency_report(
        assembly_jsonl_paths=[first, second],
        panel_id="fixture",
        generated_on="2026-06-25",
        letters=letters,
    )

    assert report["repeat_count"] == 2
    assert report["family_cell_count"] == 4
    assert report["pairwise_agreement"]["exact_family_cell_agreement_rate"] == 0.75
    assert report["semantic_entropy"]["nonzero_entropy_cells"] == 1
    diagnosis = next(
        row for row in report["semantic_entropy"]["by_family"] if row["family"] == "Diagnosis"
    )
    assert diagnosis["nonzero_entropy_cells"] == 1
