from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_diagnosis_decomposer import (  # noqa: E501
    _resume_runtime_usage,
    build_parser,
)


def test_diagnosis_decomposer_runner_has_fixed_candidate_defaults() -> None:
    args = build_parser().parse_args([])

    assert args.split == "dev"
    assert args.model == "openai/gpt-4.1-mini"
    assert args.temperature == 0.0
    assert args.max_tokens == 3200
    assert args.mode == "live"
    assert args.draft_jsonl is None
    assert args.out_jsonl == Path(
        "experiments/exectv2_diagnosis_llm_only_candidate_dev140_20260714.jsonl"
    )


def test_resume_preserves_recorded_usage_when_no_new_calls_run(tmp_path: Path) -> None:
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(
        '{"runtime_usage": {"history_entries": 140, "reported_cost": 0.3}}',
        encoding="utf-8",
    )

    usage = _resume_runtime_usage(
        {"history_entries": 0, "reported_cost": 0.0},
        metadata_path=metadata_path,
        resume=True,
    )

    assert usage == {"history_entries": 140, "reported_cost": 0.3}
