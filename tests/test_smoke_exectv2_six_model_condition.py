from pathlib import Path


def test_smoke_runner_matches_single_call_architecture() -> None:
    source = Path("scripts/smoke_exectv2_six_model_condition.py").read_text(
        encoding="utf-8"
    )

    assert "diagnosis_decomposer.run_split" not in source
    assert 'config.max_tokens["diagnosis_decomposer"]' not in source
    assert '"structured": _status(structured_meta)' in source


def test_targeted_retry_writes_rows_before_merging() -> None:
    source = Path("scripts/retry_exectv2_structured_rows.py").read_text(
        encoding="utf-8"
    )

    retry_write = source.index("write_jsonl_rows(rows, args.output)")
    merge_write = source.index("write_jsonl_rows(merged, target)")
    assert retry_write < merge_write
