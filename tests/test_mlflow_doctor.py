from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from clinical_extraction.core import mlflow_doctor
from clinical_extraction.core.mlflow_doctor import (
    build_doctor_report,
    main,
    render_doctor_report,
)


def test_doctor_report_flags_missing_mlflow_and_registry(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CLINICAL_EXTRACTION_MLFLOW_DISABLED", raising=False)
    monkeypatch.delenv("CLINICAL_EXTRACTION_MLFLOW_STRICT", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    # mlflow is a declared dev/runtime dependency, so it is installed in the
    # project's own environment. Pin the "not installed" code path under test
    # rather than depending on the real install state (matches the pattern in
    # test_core_mlflow_tracking.py).
    monkeypatch.setattr(mlflow_doctor, "mlflow_available", lambda: False)

    report = build_doctor_report(repo_root=tmp_path)

    assert report.mlflow_installed is False
    assert report.registry_exists is False
    assert report.ready_for_sync is False
    assert any("MLflow is not installed" in warning for warning in report.warnings)
    assert any("Registry file is missing" in warning for warning in report.warnings)


def test_doctor_report_uses_default_local_tracking_uri(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    registry = tmp_path / "experiments" / "registry.jsonl"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"run_id": "example"}\n', encoding="utf-8")

    report = build_doctor_report(repo_root=tmp_path)

    assert report.tracking_uri_source == "default_repo_local"
    assert report.tracking_uri == f"file:{(tmp_path / 'mlruns').as_posix()}"
    assert report.registry_row_count == 1


def test_render_doctor_report_includes_guardrails(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    report = build_doctor_report(repo_root=tmp_path)
    rendered = render_doctor_report(report)

    assert "claim-of-record" in rendered
    assert "docs/runbooks/mlflow_local_tracking.md" in rendered


def test_doctor_cli_json_output(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(mlflow_doctor, "_repo_root", lambda: tmp_path)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    buffer = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buffer)

    with pytest.raises(SystemExit) as excinfo:
        main(["--json"])

    assert excinfo.value.code == 1
    data = json.loads(buffer.getvalue())
    assert data["ready_for_sync"] is False
    assert data["repo_root"] == str(tmp_path.resolve())
