from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from clinical_extraction.tasks.seizure_frequency.gan2026.observatory.api import create_app


def test_observatory_registry_rules_prompts_and_artifacts(tmp_path: Path) -> None:
    repo_root = tmp_path
    experiments = repo_root / "experiments"
    experiments.mkdir()
    artifact_path = experiments / "example.jsonl"
    artifact_path.write_text(
        json.dumps({"source_row_index": 1, "prediction": "2 per month"}) + "\n",
        encoding="utf-8",
    )
    registry_path = experiments / "registry.jsonl"
    registry_path.write_text(
        json.dumps(
            {
                "run_id": "example_run",
                "artifact_paths": ["experiments/example.jsonl"],
                "date": "2026-06-02",
                "pipeline_family": "rules_only",
                "split": "validation",
                "row_count": 1,
                "model": "none",
                "model_role": "deterministic comparator",
                "mode": "rules_only_v1",
                "replay_status": "analysis_only",
                "decision": "historical",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    split_path = repo_root / "splits.json"
    split_path.write_text(
        json.dumps(
            {
                "split_manifest": "unit",
                "splits": {"validation": {"source_row_indices": [1]}},
            }
        ),
        encoding="utf-8",
    )

    client = TestClient(
        create_app(
            repo_root=repo_root,
            split_manifest_path=split_path,
            registry_path=registry_path,
            experiments_dir=experiments,
        )
    )

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/registry").json()["runs"][0]["run_id"] == "example_run"
    assert client.get("/splits/validation").json()["source_row_indices"] == [1]
    assert client.get("/artifacts/example_run").json()["content"][0]["source_row_index"] == 1

    rules = client.get("/rules").json()["rules"]
    assert any(rule["rule_id"].startswith("rate.") for rule in rules)

    prompts = client.get("/prompts").json()["prompts"]
    assert any(prompt["prompt_version"] for prompt in prompts)


def test_observatory_run_note_returns_pipeline_diagnostics() -> None:
    client = TestClient(create_app(repo_root=Path.cwd()))

    response = client.post(
        "/run/note",
        json={
            "note_text": "Current seizures occur twice per month.",
            "pipeline": "rules_only",
            "gold_label": "2 per month",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["output"]["final_value"] == "2 per month"
    assert payload["result"]["diagnostics"]["candidate_events"][0]["start_char"] is not None


def test_observatory_run_ablation_against_tiny_split(tmp_path: Path) -> None:
    repo_root = tmp_path
    data_path = repo_root / "data.json"
    data_path.write_text(
        json.dumps(
            [
                {
                    "source_row_index": 1,
                    "clinic_date": "Current seizures occur twice per month.",
                    "check__Seizure Frequency Number": {
                        "seizure_frequency_number": "2 per month",
                        "reference": "twice per month",
                    },
                    "labels_match_all_categories": True,
                    "quotes_ok_all_categories": True,
                    "row_ok": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    split_path = repo_root / "splits.json"
    split_path.write_text(
        json.dumps({"splits": {"validation": {"source_row_indices": [1]}}}),
        encoding="utf-8",
    )

    client = TestClient(
        create_app(
            repo_root=repo_root,
            data_path=data_path,
            split_manifest_path=split_path,
            registry_path=repo_root / "missing_registry.jsonl",
            experiments_dir=repo_root / "experiments",
        )
    )
    response = client.post("/run/ablation", json={"split": "validation", "limit": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["row_count"] == 1
    assert payload["rows"][0]["prediction_label"] == "2 per month"
    assert payload["summary"]["total"] == 1
