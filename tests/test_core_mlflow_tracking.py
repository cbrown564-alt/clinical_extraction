from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from clinical_extraction.core import mlflow_tracking
from clinical_extraction.core.mlflow_tracking import (
    MLFLOW_PARENT_RUN_TAG,
    MlflowRunPayload,
    configure_mlflow_from_env,
    find_existing_mlflow_run_id,
    lookup_keys_for_payload,
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
    assert normalized_tags(payload)["registry_run_id"] == "exectv2_same_core_full200"


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
    monkeypatch.delenv("MLFLOW_ALLOW_FILE_STORE", raising=False)
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    configure_mlflow_from_env(tmp_path)

    assert fake.tracking_uri == f"file:{(tmp_path.resolve() / 'mlruns').as_posix()}"
    assert "MLFLOW_ALLOW_FILE_STORE" in fake.env_snapshot


def test_configure_mlflow_does_not_override_explicit_tracking_uri(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeMlflow()
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    monkeypatch.delenv("MLFLOW_ALLOW_FILE_STORE", raising=False)
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)

    configure_mlflow_from_env(tmp_path)

    assert fake.tracking_uri == "sqlite:///mlflow.db"
    assert "MLFLOW_ALLOW_FILE_STORE" not in fake.env_snapshot


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

    assert run_id == "fake-run-1"
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


def test_lookup_keys_for_payload_prefers_registry_then_comparison() -> None:
    payload = MlflowRunPayload(
        experiment_name="clinical-extraction/exectv2",
        run_name="child",
        params={"registry_run_id": "child-run"},
        tags={"comparison_id": "parent-group"},
    )

    assert lookup_keys_for_payload(payload) == (
        ("registry_run_id", "child-run"),
        ("comparison_id", "parent-group"),
    )


def test_mirror_payload_reuses_existing_registry_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report = tmp_path / "report.md"
    report.write_text("# Report\n", encoding="utf-8")
    fake = _FakeMlflow()
    fake.registered_runs["existing-run"] = {
        "experiment_name": "clinical-extraction/exectv2",
        "tags": {"registry_run_id": "run-a"},
        "params": {},
        "metrics": {},
        "artifacts": [],
    }
    monkeypatch.setattr(mlflow_tracking, "mlflow_available", lambda: True)
    monkeypatch.setattr(mlflow_tracking, "_load_mlflow", lambda: fake)
    payload = MlflowRunPayload(
        experiment_name="clinical-extraction/exectv2",
        run_name="run-a",
        params={"registry_run_id": "run-a"},
        metrics={"overall_f1": 0.9},
        tags={"registry_canonical": True},
        artifact_paths=(Path("report.md"),),
    )

    run_id = mirror_payload_to_mlflow(payload, repo_root=tmp_path)

    assert run_id == "existing-run"
    assert fake.created_run_count == 0
    assert fake.resumed_run_ids == ["existing-run"]
    assert fake.metrics == {"overall_f1": 0.9}


def test_find_existing_mlflow_run_id_matches_param_fallback() -> None:
    fake = _FakeMlflow()
    fake.registered_runs["legacy-run"] = {
        "experiment_name": "clinical-extraction/exectv2",
        "tags": {},
        "params": {"registry_run_id": "legacy"},
        "metrics": {},
        "artifacts": [],
    }

    assert (
        find_existing_mlflow_run_id(
            fake,
            experiment_name="clinical-extraction/exectv2",
            tag_key="registry_run_id",
            tag_value="legacy",
        )
        == "legacy-run"
    )


class _FakeRunInfo:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id


class _FakeRun:
    def __init__(self, run_id: str = "fake-run-id") -> None:
        self.info = _FakeRunInfo(run_id)

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
        self.env_snapshot: dict[str, str] = {}
        self.registered_runs: dict[str, dict[str, Any]] = {}
        self.created_run_count = 0
        self.resumed_run_ids: list[str] = []
        self._next_run_id = 1

    def set_tracking_uri(self, uri: str) -> None:
        import os

        self.tracking_uri = uri
        self.env_snapshot = dict(os.environ)

    def set_experiment(self, name: str) -> None:
        self.experiment_name = name

    def start_run(
        self,
        *,
        run_name: str | None = None,
        tags: dict[str, str] | None = None,
        run_id: str | None = None,
    ) -> _FakeRun:
        if run_id is not None:
            self.resumed_run_ids.append(run_id)
            run = self.registered_runs.setdefault(
                run_id,
                {
                    "experiment_name": self.experiment_name,
                    "tags": {},
                    "params": {},
                    "metrics": {},
                    "artifacts": [],
                },
            )
            if tags:
                run["tags"].update(tags)
            return _FakeRun(run_id)

        run_id = f"fake-run-{self._next_run_id}"
        self._next_run_id += 1
        self.created_run_count += 1
        self.started = {"run_name": run_name, "tags": tags or {}}
        self.registered_runs[run_id] = {
            "experiment_name": self.experiment_name,
            "tags": dict(tags or {}),
            "params": {},
            "metrics": {},
            "artifacts": [],
        }
        return _FakeRun(run_id)

    def log_params(self, params: dict[str, str]) -> None:
        self.params = params
        if self.resumed_run_ids:
            self.registered_runs[self.resumed_run_ids[-1]]["params"] = params

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.metrics = metrics
        if self.resumed_run_ids:
            self.registered_runs[self.resumed_run_ids[-1]]["metrics"] = metrics

    def log_artifact(self, path: str) -> None:
        self.artifacts.append(path)
        if self.resumed_run_ids:
            self.registered_runs[self.resumed_run_ids[-1]]["artifacts"].append(path)

    def set_tag(self, key: str, value: str) -> None:
        if self.resumed_run_ids:
            self.registered_runs[self.resumed_run_ids[-1]]["tags"][key] = value

    def search_runs(
        self,
        *,
        experiment_names: list[str],
        filter_string: str,
        order_by: list[str],
        max_results: int,
    ) -> _FakeSearchResults:
        matches: list[tuple[str, dict[str, Any]]] = []
        for run_id, run in self.registered_runs.items():
            if run["experiment_name"] not in experiment_names:
                continue
            if _matches_filter(filter_string, run):
                matches.append((run_id, run))
        matches = matches[:max_results]
        return _FakeSearchResults([run_id for run_id, _ in matches])


class _FakeSearchResults:
    def __init__(self, run_ids: list[str]) -> None:
        self._run_ids = run_ids

    @property
    def empty(self) -> bool:
        return not self._run_ids

    @property
    def iloc(self) -> _FakeIloc:
        return _FakeIloc(self._run_ids)


class _FakeIloc:
    def __init__(self, run_ids: list[str]) -> None:
        self._run_ids = run_ids

    def __getitem__(self, index: int) -> dict[str, str]:
        return {"run_id": self._run_ids[index]}


def _matches_filter(filter_string: str, run: dict[str, Any]) -> bool:
    clauses = [clause.strip() for clause in filter_string.split(" OR ")]
    for clause in clauses:
        if clause.startswith("tags.") and " = " in clause:
            key, raw_value = clause[len("tags.") :].split(" = ", 1)
            value = raw_value.strip("'")
            if run["tags"].get(key) == value:
                return True
        if clause.startswith("params.") and " = " in clause:
            key, raw_value = clause[len("params.") :].split(" = ", 1)
            value = raw_value.strip("'")
            if run["params"].get(key) == value:
                return True
    return False


class _FailingMlflow(_FakeMlflow):
    def set_experiment(self, name: str) -> None:
        raise RuntimeError("boom")
