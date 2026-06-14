from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.cli import (
    frozen_test_preflight,
    frozen_test_readout,
)


def test_frozen_test_preflight_passes_when_protocol_and_artifacts_match(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    monkeypatch.setattr(
        frozen_test_preflight,
        "pipeline_specs",
        lambda: {
            "fresh_evidence_reasoner": SimpleNamespace(default_max_tokens=2800),
        },
    )
    monkeypatch.setattr(
        frozen_test_preflight,
        "load_split_manifest",
        lambda: {"name": "gan2026_split_v1", "splits": {"test": {"count": 450}}},
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is True
    assert report.failures == ()


def test_frozen_test_preflight_rejects_hash_drift(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("first\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    frozen_file.write_text("second\n", encoding="utf-8")
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any("hash mismatch" in failure for failure in report.failures)


def test_frozen_test_preflight_rejects_existing_test_outputs(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    test_jsonl = tmp_path / "test.jsonl"
    test_jsonl.write_text('{"source_row_index": 1}\n', encoding="utf-8")
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=test_jsonl,
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any("test output already exists" in failure for failure in report.failures)


def test_frozen_test_preflight_rejects_existing_test_resume_part_outputs(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    test_jsonl = tmp_path / "test.jsonl"
    resume_part = tmp_path / "test.resume-part.jsonl"
    resume_part.write_text('{"source_row_index": 1}\n', encoding="utf-8")
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=test_jsonl,
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any("test.resume-part.jsonl" in failure for failure in report.failures)


def test_frozen_test_preflight_rejects_partial_test_command(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(
        tmp_path,
        {str(frozen_file): _sha256(frozen_file)},
        command_extra="  --limit 25 `\n",
    )
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any(
        "authorized command must not include --limit" in failure
        for failure in report.failures
    )


def test_frozen_test_preflight_rejects_output_path_drift(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(
        tmp_path,
        {str(frozen_file): _sha256(frozen_file)},
        jsonl_path=Path("experiments/not_the_frozen_output.jsonl"),
    )
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any("authorized command missing JSONL path" in failure for failure in report.failures)


def test_frozen_test_preflight_rejects_unfrozen_command_modifiers(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(
        tmp_path,
        {str(frozen_file): _sha256(frozen_file)},
        command_extra=(
            "  --overwrite-existing `\n"
            "  --temperature 0.2 `\n"
            "  --mode prompt-only `\n"
        ),
    )
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any(
        "authorized command must not include --overwrite-existing" in failure
        for failure in report.failures
    )
    assert any(
        "authorized command must not include --temperature" in failure
        for failure in report.failures
    )
    assert any(
        "authorized command must not include --mode prompt-only" in failure
        for failure in report.failures
    )


def test_frozen_test_preflight_rejects_duplicate_singleton_command_option(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(
        tmp_path,
        {str(frozen_file): _sha256(frozen_file)},
        command_extra="  --model openai/gpt-4.1-mini `\n",
    )
    _patch_valid_spec_and_manifest(monkeypatch)

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any(
        "authorized command must include --model exactly once; found 2" in failure
        for failure in report.failures
    )


def test_frozen_test_preflight_rejects_cli_frozen_launch_path_drift(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    _patch_valid_spec_and_manifest(monkeypatch)
    monkeypatch.setattr(
        frozen_test_preflight,
        "FROZEN_TEST_PIPELINE_LAUNCH_SPECS",
        {
            "fresh_evidence_reasoner": SimpleNamespace(
                model="openai/gpt-4.1",
                max_tokens=2800,
                jsonl_path=Path("experiments/alternate.jsonl"),
                report_path=frozen_test_preflight.DEFAULT_TEST_REPORT_PATH,
            )
        },
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any(
        "fresh_evidence_reasoner frozen JSONL path drifted" in failure
        for failure in report.failures
    )


def test_frozen_test_preflight_rejects_unredacted_test_summary(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    _patch_valid_spec_and_manifest(monkeypatch)

    def leaky_summary(rows, *, split=None):
        del rows, split
        return {
            "rows": 1,
            "fresh_evidence_profiles": {
                frozen_test_preflight.SYNTHETIC_HOLDOUT_PROFILE: 1
            },
            "final_labels": {frozen_test_preflight.SYNTHETIC_HOLDOUT_LABEL: 1},
            "aggregate_only_omitted_fields": [],
        }

    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "summarize_rows",
        leaky_summary,
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert "V12 test summary exposes fresh_evidence_profiles" in report.failures
    assert "V12 test summary exposes final_labels" in report.failures


def test_frozen_test_preflight_rejects_unparseable_aggregate_readout(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    _patch_valid_spec_and_manifest(monkeypatch)

    monkeypatch.setattr(
        frozen_test_readout,
        "read_aggregate_report",
        lambda path: SimpleNamespace(
            ok=False,
            metrics={},
            failures=("synthetic readout failure",),
        ),
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any(
        "V12 test report is not parseable by aggregate readout helper: "
        "synthetic readout failure" in failure
        for failure in report.failures
    )


def test_frozen_test_preflight_rejects_prompt_input_forbidden_context(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    _patch_valid_spec_and_manifest(monkeypatch)

    def leaky_prompt(record, agent_rows):
        del record, agent_rows
        return (
            f"{frozen_test_preflight.SYNTHETIC_PROMPT_ROW_ID} "
            "source_row_index "
            f"{frozen_test_preflight.SYNTHETIC_PROMPT_GOLD_LABEL} "
            "gold_label "
            "gan2026_split_v1 "
            "deterministic_top "
            f"{frozen_test_preflight.SYNTHETIC_PROMPT_RAW_SECRET} "
            "row_ok"
        )

    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "build_prompt_input",
        leaky_prompt,
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert "V12 prompt input exposes source row index" in report.failures
    assert "V12 prompt input exposes gold label value" in report.failures
    assert "V12 prompt input exposes split manifest" in report.failures
    assert "V12 prompt input exposes deterministic top token" in report.failures
    assert "V12 prompt input exposes raw secret" in report.failures


def test_frozen_test_preflight_rejects_test_report_row_detail_leak(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    _patch_valid_spec_and_manifest(monkeypatch)

    def leaky_report(rows, metadata, path, *, jsonl_path):
        del rows, metadata, jsonl_path
        path.write_text(
            "## Rows\n"
            f"{frozen_test_preflight.SYNTHETIC_HOLDOUT_ROW_ID}\n"
            f"{frozen_test_preflight.SYNTHETIC_HOLDOUT_PROFILE}\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "write_report",
        leaky_report,
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            check_test_source_artifacts=False,
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert "V12 test report exposes row table heading" in report.failures
    assert "V12 test report exposes synthetic row id" in report.failures
    assert "V12 test report exposes synthetic profile" in report.failures


def test_frozen_test_preflight_rejects_test_source_coverage_drift(
    tmp_path: Path, monkeypatch
) -> None:
    frozen_file = tmp_path / "frozen.py"
    frozen_file.write_text("frozen = True\n", encoding="utf-8")
    gpt_source = tmp_path / "gpt_test.jsonl"
    qwen_source = tmp_path / "qwen_test.jsonl"
    deepseek_placeholder = tmp_path / "missing_deepseek_test.jsonl"
    gpt_source.write_text('{"source_row_index": 1, "split": "test"}\n', encoding="utf-8")
    qwen_source.write_text(
        '{"source_row_index": 1, "split": "test"}\n'
        '{"source_row_index": 2, "split": "test"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(frozen_test_preflight, "EXPECTED_TEST_ROW_COUNT", 2)
    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "TEST_GPT_STRUCTURED_EVENT_JSONL_PATH",
        gpt_source,
    )
    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH",
        qwen_source,
    )
    monkeypatch.setattr(
        frozen_test_preflight.fresh_evidence_reasoner,
        "TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH",
        deepseek_placeholder,
    )
    monkeypatch.setattr(
        frozen_test_preflight,
        "EXPECTED_TEST_SOURCE_ARTIFACTS",
        (("gpt", gpt_source), ("qwen", qwen_source)),
    )
    protocol = _write_protocol(tmp_path, {str(frozen_file): _sha256(frozen_file)})
    monkeypatch.setattr(
        frozen_test_preflight,
        "pipeline_specs",
        lambda: {
            "fresh_evidence_reasoner": SimpleNamespace(default_max_tokens=2800),
        },
    )
    monkeypatch.setattr(
        frozen_test_preflight,
        "load_split_manifest",
        lambda: {
            "name": "gan2026_split_v1",
            "splits": {"test": {"count": 2, "source_row_indices": [1, 2]}},
        },
    )

    report = frozen_test_preflight.run_preflight(
        frozen_test_preflight.PreflightConfig(
            protocol_path=protocol,
            test_jsonl_path=tmp_path / "missing_test.jsonl",
            test_report_path=tmp_path / "missing_test.md",
            required_hash_paths=(str(frozen_file),),
        )
    )

    assert report.ok is False
    assert any("gpt test source coverage drifted" in failure for failure in report.failures)


def _patch_valid_spec_and_manifest(monkeypatch) -> None:
    monkeypatch.setattr(
        frozen_test_preflight,
        "pipeline_specs",
        lambda: {
            "fresh_evidence_reasoner": SimpleNamespace(default_max_tokens=2800),
        },
    )
    monkeypatch.setattr(
        frozen_test_preflight,
        "load_split_manifest",
        lambda: {"name": "gan2026_split_v1", "splits": {"test": {"count": 450}}},
    )


def _write_protocol(
    tmp_path: Path,
    hashes: dict[str, str],
    *,
    command_extra: str = "",
    jsonl_path: Path = frozen_test_preflight.DEFAULT_TEST_JSONL_PATH,
    markdown_path: Path = frozen_test_preflight.DEFAULT_TEST_REPORT_PATH,
) -> Path:
    hash_lines = "\n".join(f"{digest}  {path}" for path, digest in hashes.items())
    gpt_source = (
        frozen_test_preflight.fresh_evidence_reasoner
        .TEST_GPT_STRUCTURED_EVENT_JSONL_PATH
        .as_posix()
    )
    qwen_source = (
        frozen_test_preflight.fresh_evidence_reasoner
        .TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH
        .as_posix()
    )
    protocol = tmp_path / "protocol.md"
    protocol.write_text(
        f"""# Protocol

Pipeline `fresh_evidence_reasoner`
Model `openai/gpt-4.1`
Prompt `gan2026_fresh_evidence_reasoner_v0_4`
Gate `gan2026_fresh_evidence_safety_gate_v0_3`
Target `383/450`
Use aggregate-only readout.
No deterministic final-label fallback.
Post-run aggregate readout uses frozen_test_readout.
GPT source `{gpt_source}`
Qwen source `{qwen_source}`
DeepSeek test450 structured-event artifact is unavailable.

```text
{hash_lines}
```

```powershell
.\\.venv\\Scripts\\python.exe -m gan2026.llm_pipeline_cli `
  --pipeline fresh_evidence_reasoner `
  --split test `
  --mode live `
  --model openai/gpt-4.1 `
  --max-tokens 2800 `
  --confirm-test-audit `
  --jsonl {jsonl_path} `
  --markdown {markdown_path} `
  --progress-every 0 `
{command_extra}  --escalation-reason "user-authorized frozen aggregate audit"
```
""",
        encoding="utf-8",
    )
    return protocol


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
