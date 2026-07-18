from pathlib import Path


def test_smoke_runner_matches_single_call_architecture() -> None:
    source = Path("scripts/smoke_exectv2_six_model_condition.py").read_text(
        encoding="utf-8"
    )

    assert "diagnosis_decomposer.run_split" not in source
    assert 'config.max_tokens["diagnosis_decomposer"]' not in source
    assert '"structured": _status(structured_meta)' in source
    assert "configure_declared_runtime(args.config)" in source
    assert 'parser.add_argument("--output", type=Path)' in source
    assert "progress_every=1" in source
    assert "write_jsonl_rows(structured_rows, output)" in source


def test_targeted_retry_writes_rows_before_merging() -> None:
    source = Path("scripts/retry_exectv2_structured_rows.py").read_text(
        encoding="utf-8"
    )

    retry_write = source.index("write_jsonl_rows(rows, args.output)")
    merge_write = source.index("write_jsonl_rows(merged, target)")
    assert retry_write < merge_write


def test_local_queue_probes_each_model_before_clinical_rows() -> None:
    source = Path("scripts/run_local_model_queue.ps1").read_text(encoding="utf-8")

    qwen_probe = source.index('Invoke-LocalProbe "qwen36_35b" "qwen3.6:35b"')
    qwen_run = source.index('foreach ($rows in 1, 5, 25)')
    gemma_probe = source.index('Invoke-LocalProbe "gemma4_26b" "gemma4:26b"')
    gemma_run = source.index('Invoke-QueueStep "gemma_exect_dev5"')
    assert qwen_probe < qwen_run
    assert gemma_probe < gemma_run

    probe_source = Path("scripts/probe_ollama_structured_output.py").read_text(
        encoding="utf-8"
    )
    assert '"native_schema_constraint"' in probe_source
    assert '"prompt_plus_shared_parser"' in probe_source


def test_holdout_runner_checkpoints_each_row_and_allows_reported_failures() -> None:
    source = Path("scripts/run_hosted_holdout_panel.py").read_text(encoding="utf-8")

    assert '"--progress-every",\n        "1"' in source
    assert '"--allow-row-failures"' in source
