from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.core import mlflow_tracking
from clinical_extraction.core.mlflow_tracking import (
    MLFLOW_PARENT_RUN_TAG,
    MlflowRunPayload,
    configure_mlflow_from_env,
    mirror_payload_to_mlflow,
    normalized_metrics,
    normalized_params,
    normalized_tags,
    registry_entry_to_mlflow_payload,
    safe_artifact_paths,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
)


def test_normalizes_payload_values_for_mlflow() -> None:
    payload = MlflowRunPayload(
        experiment_name="clinical-extraction/exectv2",
        run_name="example",
        params={"row_count": 140, "enabled": True, "unset": None},
        metrics={"overall_f1": 0.85, "bad_bool": True, "nan": float("nan")},
        tags={"registry_canonical": True, "raw_trace_policy": "disabled", "unset": None},
    )

    assert normalized_params(payload) == {"row_count": "140", "enabled": "true"}
    assert normalized_metrics(payload) == {"overall_f1": 0.85}
    assert normalized_tags(payload) == {
        "registry_canonical": "true",
        "raw_trace_policy": "disabled",
    }


def test_registry_entry_payload_preserves_claim_boundary_defaults() -> None:
    entry = RunRegistryEntry(
        run_id="exectv2_same_core_full200",
        artifact_paths=("experiments/report.md",),
        date="2026-06-25",
        pipeline_family="llm_only_canonical",
        split="full200_aggregate",
        row_count=200,
        model="deepseek/deepseek-reasoner",
        model_role="extractor",
        mode="replay",
        replay_status="saved_output_replay",
        decision="revise",
        primary_metrics={"clinical_headline_f1": 0.8566, "schema_note": "1 failure"},
        comparison_role="diagnostic",
    )

    payload = registry_entry_to_mlflow_payload(entry, task="exectv2")

    assert payload.experiment_name == "clinical-extraction/exectv2"
    assert payload.run_name == "exectv2_same_core_full200"
    assert normalized_params(payload)["registry_run_id"] == "exectv2_same_core_full200"
    assert normalized_metrics(payload) == {"clinical_headline_f1": 0.8566}
    assert normalized_tags(payload)["claim_status"] == "diagnostic"
    assert normalized_tags(payload)["claim_boundary"] == "full200_aggregate_only"
    assert normalized_tags(payload)["row_inspection_policy"] == "aggregate_only"
    assert normalized_tags(payload)["restricted_surface"] == "true"


def test_safe_artifact_paths_keep_only_existing_files_under_repo(tmp_path: Path) -> None:
    report = tmp_path / "experiments" / "report.md"
    report.parent.mkdir()
    report.write_text("# Report\n", encoding="utf-8")
    outside = tmp_path.parent / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    payload = MlflowRunPayload(
        experiment_name="clinical-extraction/exectv2",
        run_name="example",
        artifact_paths=(Path("experiments/report.md"), Path("missing.md"), outside),
    )

    assert safe_artifact_paths(payload, repo_root=tmp_path) == (report.resolve(),)


def test_disabled_env_skips_mlflow_import(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CLINICAL_EXTRACTION_MLFLOW_DISABLED", "1")
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: pytest.fail("unexpected import"))

    result = mirror_payload_to_mlflow(
        MlflowRunPayload("clinical-extraction/scratch", "disabled"), repo_root=tmp_path
    )

    assert result is None


def test_missing_mlflow_returns_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: False)

    result = mirror_payload_to_mlflow(
        MlflowRunPayload("clinical-extraction/scratch", "missing"), repo_root=tmp_path
    )

    assert result is None


def test_configure_mlflow_uses_repo_local_tracking_uri(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeMlflow()
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    configure_mlflow_from_env(tmp_path)

    assert fake.tracking_uri == f"file:{(tmp_path.resolve() / 'mlruns').as_posix()}"


def test_mirror_payload_logs_safe_metadata_and_artifacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report = tmp_path / "report.md"
    report.write_text("# Report\n", encoding="utf-8")
    fake = _FakeMlflow()
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    run_id = mirror_payload_to_mlflow(
        MlflowRunPayload(
            experiment_name="clinical-extraction/exectv2",
            run_name="run",
            params={"row_count": 1},
            metrics={"overall_f1": 0.5},
            tags={"registry_canonical": True},
            artifact_paths=(Path("report.md"),),
            parent_run_id="parent",
        ),
        repo_root=tmp_path,
    )

    assert run_id == "fake-run-id"
    assert fake.experiment_name == "clinical-extraction/exectv2"
    assert fake.started["run_name"] == "run"
    assert fake.started["tags"][MLFLOW_PARENT_RUN_TAG] == "parent"
    assert fake.params == {"row_count": "1"}
    assert fake.metrics == {"overall_f1": 0.5}
    assert fake.artifacts == [str(report.resolve())]


def test_non_strict_mlflow_error_returns_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FailingMlflow()
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    assert (
        mirror_payload_to_mlflow(
            MlflowRunPayload("clinical-extraction/scratch", "broken"), repo_root=tmp_path
        )
        is None
    )


def test_strict_mlflow_error_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake = _FailingMlflow()
    monkeypatch.setenv("CLINICAL_EXTRACTION_MLFLOW_STRICT", "1")
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    with pytest.raises(RuntimeError, match="boom"):
        mirror_payload_to_mlflow(
            MlflowRunPayload("clinical-extraction/scratch", "broken"), repo_root=tmp_path
        )


class _FakeRunInfo:
    run_id = "fake-run-id"


class _FakeRun:
    info = _FakeRunInfo()

    def __enter__(self) -> _FakeRun:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeMlflow:
    def __init__(self) -> None:
        self.tracking_uri = ""
        self.experiment_name = ""
        self.started: dict = {}
        self.params: dict = {}
        self.metrics: dict = {}
        self.artifacts: list[str] = []

    def set_tracking_uri(self, uri: str) -> None:
        self.tracking_uri = uri

    def set_experiment(self, name: str) -> None:
        self.experiment_name = name

    def start_run(self, *, run_name: str, tags: dict[str, str]) -> _FakeRun:
        self.started = {"run_name": run_name, "tags": tags}
        return _FakeRun()

    def log_params(self, params: dict[str, str]) -> None:
        self.params = params

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.metrics = metrics

    def log_artifact(self, path: str) -> None:
        self.artifacts.append(path)


class _FailingMlflow(_FakeMlflow):
    def set_experiment(self, name: str) -> None:
        raise RuntimeError("boom")
