from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from clinical_extraction.trace_explorer.api.app import create_app
from clinical_extraction.trace_explorer.index import build_index

TRACE_FIXTURE = (
    Path("src")
    / "clinical_extraction"
    / "trace_explorer"
    / "fixtures"
    / "syn_014.json"
)
FRONTEND_FIXTURES = Path("frontend") / "public" / "mock-data"


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    index_dir = tmp_path / ".trace_explorer"
    build_index(
        artifacts=[TRACE_FIXTURE],
        output=index_dir,
        approved_roots=[Path.cwd()],
    )
    return TestClient(
        create_app(
            index_dir=index_dir,
            frontend_fixture_root=FRONTEND_FIXTURES,
            review_db_path=tmp_path / "reviews.sqlite3",
        )
    )


def test_frontend_catalog_and_read_only_surfaces_use_the_live_api(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "index_ready": True}

    registry = client.get("/registry")
    assert registry.status_code == 200
    assert any(run["pipeline_family"] == "rules_only" for run in registry.json()["runs"])

    families = client.get("/pipeline-families")
    assert families.status_code == 200
    assert any(family["run_id"] == "rules" for family in families.json()["families"])

    exect_runs = client.get("/exectv2/runs")
    assert exect_runs.status_code == 200
    assert exect_runs.json()["runs"]
    hybrid = [
        run
        for run in exect_runs.json()["runs"]
        if run.get("kind") == "llm_with_rules"
    ]
    active_hybrid = [run for run in hybrid if run.get("active_method") == "llm_with_rules"]
    assert len(active_hybrid) == 1
    assert active_hybrid[0]["model"] == "openai/gpt-5.6-sol"


def test_locked_test_records_are_not_enumerable(client: TestClient) -> None:
    response = client.get("/records/test")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "aggregate_only"
    assert "source_row_index" not in response.text

    guessed = client.get("/records/test/79")
    assert guessed.status_code == 403
    error = guessed.json()["error"]
    assert "79" not in error["message"]
    assert error["details"] == {}


def test_gan_hybrid_workbench_serves_current_stack_dev750_rows(
    client: TestClient,
) -> None:
    run_id = "gan2026_validation750_gpt56sol_llm_with_rules"
    families = client.get("/pipeline-families")
    assert families.status_code == 200
    sol = next(family for family in families.json()["families"] if family["run_id"] == run_id)
    assert sol["availability"] == "replay"
    assert sol["metrics"]["purist_correct"] == 671
    models = {family["model"] for family in families.json()["families"]}
    assert "gemini/gemini-3.7-flash" in models
    assert "openai/gpt-4.1-mini" not in models

    artifact = client.get(f"/artifacts/{run_id}", params={"limit": 1})
    assert artifact.status_code == 200
    path = artifact.json()["artifact_path"]
    assert path.startswith(
        "experiments/gan2026_six_model_current_stack_dev750_replay_20260813/"
    )

    selected = client.get(f"/artifacts/{run_id}", params={"letter_id": "446"})
    assert selected.status_code == 200
    assert len(selected.json()["content"]) == 1
    assert int(selected.json()["content"][0]["source_row_index"]) == 446

    row_path = Path(path)
    found: dict | None = None
    with row_path.open(encoding="utf-8") as handle:
        for line in handle:
            value = json.loads(line)
            if int(value["source_row_index"]) == 446:
                found = value
                break
    assert found is not None
    assert found["structured_record"]["selection"]["final_label"] == "2 per week"
    assert found["row_trace"]["model_prediction"]["record"]["selection"]["final_label"] == (
        "up to 2 per week"
    )


def test_saved_artifact_replay_is_allowlisted_and_bounded(client: TestClient) -> None:
    run_id = "gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05"
    response = client.get(f"/artifacts/{run_id}", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()["content"]) == 2

    missing = client.get("/artifacts/not-a-real-run")
    assert missing.status_code == 404
    assert "not-a-real-run" not in missing.text


def test_letter_catalogs_cover_the_development_splits(client: TestClient) -> None:
    gan = client.get("/datasets/gan2026/letters")
    assert gan.status_code == 200
    gan_body = gan.json()
    assert gan_body["dataset"] == "gan2026"
    assert gan_body["split"] == "dev750"
    assert gan_body["count"] == 750
    assert gan_body["letters"][0]["id"] == "10"

    gan_letter = client.get("/datasets/gan2026/letters/10")
    assert gan_letter.status_code == 200
    assert "KINGS NEUROSCIENCES CENTRE" in gan_letter.json()["note_text"]

    records = client.get("/records/validation")
    assert records.status_code == 200
    assert records.json()["count"] == 750

    exect = client.get("/datasets/exectv2/letters")
    assert exect.status_code == 200
    exect_body = exect.json()
    assert exect_body["dataset"] == "exectv2"
    assert exect_body["split"] == "dev140"
    assert exect_body["count"] == 140
    letter_ids = {letter["id"] for letter in exect_body["letters"]}
    assert "EA0002" in letter_ids
    assert len(letter_ids) == 140


def test_review_queues_and_writes_enforce_development_row_policy(client: TestClient) -> None:
    gan_rows = client.get("/gold-audit/rows", params={"dataset": "gan2026"})
    assert gan_rows.status_code == 200
    assert gan_rows.json()["total"] == 750
    assert {row["source_row_index"] for row in gan_rows.json()["rows"][:3]} == {
        "10",
        "40",
        "79",
    }

    exect_rows = client.get("/gold-audit/rows", params={"dataset": "exectv2"})
    assert exect_rows.status_code == 200
    assert exect_rows.json()["total"] == 140
    assert {row["letter_id"] for row in exect_rows.json()["rows"]} == {
        letter["id"] for letter in client.get("/datasets/exectv2/letters").json()["letters"]
    }

    locked = client.post(
        "/gold-audit/decide",
        json={
            "dataset": "gan2026",
            "source_row_index": 10,
            "split": "test",
            "notes": "Must not be stored.",
        },
    )
    assert locked.status_code == 403
    assert locked.json()["error"]["code"] == "aggregate_only"


def test_run_note_executes_the_real_deterministic_pipeline(client: TestClient) -> None:
    response = client.post(
        "/run/note",
        json={
            "note_text": "She currently reports four seizures per day.",
            "pipeline": "rules_only",
            "source_row_index": 314,
            "gold_label": "4 per day",
            "gold_reference": "four seizures per day",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pipeline"] == "rules"
    assert body["source_row_index"] == 314
    assert body["result"]["output"]["final_value"] == "4 per day"
    assert body["result"]["diagnostics"]["candidate_events"]
    assert body["result"]["diagnostics"]["evidence_valid"] is True
