from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_score as projection_score,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_score_rendered_label_uses_existing_purist_category_mapping() -> None:
    score = projection_score.score_rendered_label(
        source_row_index=10,
        rendered_label="30 per month",
        gold_record=_gold_record(10, "1 per day"),
    )

    assert score.score_status == "scored"
    assert score.predicted_normalized_label == "30 per month"
    assert score.gold_normalized_label == "1 per day"
    assert score.exact_normalized_label_match is False
    assert score.purist_correct is True
    assert score.pragmatic_correct is True
    assert score.predicted_purist_category == score.gold_purist_category


def test_score_rendered_label_keeps_null_render_non_scored() -> None:
    score = projection_score.score_rendered_label(
        source_row_index=11,
        rendered_label=None,
        gold_record=_gold_record(11, "seizure free for 3 months"),
    )

    assert score.score_status == "not_scored_null_rendered_label"
    assert score.purist_correct is None
    assert score.gold_purist_category == "currently_no_seizure"
    assert score.score_issues == ["rendered_label_null"]


def test_score_rendered_label_keeps_unparseable_render_non_scored() -> None:
    score = projection_score.score_rendered_label(
        source_row_index=12,
        rendered_label="several seizures lately",
        gold_record=_gold_record(12, "unknown"),
    )

    assert score.score_status == "not_scored_unparseable_rendered_label"
    assert score.purist_correct is None
    assert score.gold_normalized_label == "unknown"
    assert score.score_issues[0].startswith("rendered_label_unparseable:")


def test_build_scoring_artifact_summarizes_statuses() -> None:
    project_render_rows = [
        _project_render_row(20, "2 per month"),
        _project_render_row(21, None),
    ]

    rows, metadata = projection_score.build_scoring_artifact(
        project_render_rows,
        gold_records={
            20: _gold_record(20, "2 per month"),
            21: _gold_record(21, "unknown"),
        },
        project_render_artifact_path="test.jsonl",
    )

    assert rows[0]["score"]["purist_correct"] is True
    assert rows[1]["score"]["score_status"] == "not_scored_null_rendered_label"
    assert metadata["summary"]["scored_rows"] == 1
    assert metadata["summary"]["non_scored_rows"] == 1
    assert metadata["summary"]["purist_accuracy_on_scored"] == 1.0


def _project_render_row(source_row_index: int, rendered_label: str | None) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "schema_version": "gan2026_projection_render_v0",
        "projection_policy_id": "gan2026_clinical_assessment_projection_v0",
        "render_policy_id": "gan2026_final_label_renderer_v0",
        "projection_decision": None,
        "final_rendered_label": {"rendered_label": rendered_label},
    }


def _gold_record(source_row_index: int, gold_label: str) -> GanFrequencyRecord:
    parsed = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text="",
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=parsed.normalized_label,
        gold_label_kind=parsed.kind,
        gold_yearly_bounds=parsed.yearly_bounds,
        gold_monthly_frequency=parsed.monthly_frequency,
    )
