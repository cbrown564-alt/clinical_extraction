from __future__ import annotations

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
FRONTEND_FIXTURES = Path("frontend") / "frontend" / "public" / "mock-data"


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
    assert any(family["run_id"] == "rules_only" for family in families.json()["families"])

    exect_runs = client.get("/exectv2/runs")
    assert exect_runs.status_code == 200
    assert exect_runs.json()["runs"]
    assert all(run["task"] == "exectv2" for run in exect_runs.json()["runs"])

    scorecard = client.get("/gan2026/reliability-scorecard")
    assert scorecard.status_code == 200
    assert scorecard.json()["dataset"] == "gan2026"


def test_exect_architectures_are_the_winning_mode_model_matrix(client: TestClient) -> None:
    response = client.get("/exectv2/runs", headers={"Accept-Encoding": "identity"})

    assert response.status_code == 200
    assert len(response.content) < 100_000
    payload = response.json()
    runs = payload["runs"]
    assert len(runs) == 13

    by_mode: dict[str, list[dict[str, object]]] = {}
    for run in runs:
        by_mode.setdefault(str(run["comparison_mode"]), []).append(run)

    assert {mode: len(items) for mode, items in by_mode.items()} == {
        "llm_plus_rules": 6,
        "llm_only": 6,
        "deterministic_only": 1,
    }

    expected_models = {
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    }
    assert {str(run["model"]) for run in by_mode["llm_plus_rules"]} == expected_models
    assert {str(run["model"]) for run in by_mode["llm_only"]} == expected_models
    assert by_mode["deterministic_only"][0]["model"] == "(model-independent)"

    sol_final = next(
        run
        for run in by_mode["llm_plus_rules"]
        if run["model"] == "openai/gpt-5.6-sol"
    )
    sol_raw = next(
        run for run in by_mode["llm_only"] if run["model"] == "openai/gpt-5.6-sol"
    )
    assert sol_final["metrics"]["overall_f1"] == 0.892  # type: ignore[index]
    assert sol_raw["metrics"]["overall_f1"] == 0.8097  # type: ignore[index]

    for run in runs:
        assert run["split"] == "dev140"
        assert run["row_count"] == 140
        assert run["letters"] == []

    detail = client.get(
        "/exectv2/runs/exectv2_winning_mode_gpt56sol_llm_only_dev140",
        headers={"Accept-Encoding": "identity"},
    )
    assert detail.status_code == 200
    assert len(detail.content) < 2_000_000
    detail_payload = detail.json()
    assert len(detail_payload["shared_letters"]) == 140
    assert len(detail_payload["run"]["letters"]) == 140
    assert all(letter["split"] == "dev" for letter in detail_payload["run"]["letters"])
    assert all(letter["stage"] == "dev140" for letter in detail_payload["run"]["letters"])
    assert all("letter_text" not in letter for letter in detail_payload["run"]["letters"])
    assert all("gold_mentions" not in letter for letter in detail_payload["run"]["letters"])


def test_gan_architectures_use_the_same_six_model_comparison_matrix(
    client: TestClient,
) -> None:
    response = client.get("/pipeline-families")

    assert response.status_code == 200
    families = response.json()["families"]
    assert len(families) == 13

    by_mode: dict[str, list[dict[str, object]]] = {}
    for family in families:
        by_mode.setdefault(str(family["comparison_mode"]), []).append(family)

    assert {mode: len(items) for mode, items in by_mode.items()} == {
        "llm_plus_rules": 6,
        "llm_only": 6,
        "deterministic_only": 1,
    }

    expected_models = [
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    ]
    assert [str(item["model"]) for item in by_mode["llm_plus_rules"]] == expected_models
    assert [str(item["model"]) for item in by_mode["llm_only"]] == expected_models

    model_runs = [*by_mode["llm_plus_rules"], *by_mode["llm_only"]]
    assert all(item["split"] == "validation750" for item in model_runs)
    assert all("test450" not in str(item["run_id"]) for item in model_runs)
    assert all(
        item["availability"] in {"replay", "not_retained"}
        and item["evidence_scope"]
        in {"validation750_row_level", "incomplete_not_served"}
        for item in model_runs
    )
    assert any(item["availability"] == "replay" for item in model_runs)
    assert all(
        item["has_replay_artifact"] is (item["availability"] == "replay")
        for item in model_runs
    )

    completed = next(item for item in model_runs if item["availability"] == "replay")
    assert completed["metrics"]["row_count"] == 750
    replay = client.get(f"/artifacts/{completed['run_id']}", params={"limit": 2})
    assert replay.status_code == 200
    assert len(replay.json()["content"]) == 2
    assert all(row["split"] == "validation" for row in replay.json()["content"])

    incomplete = next(item for item in model_runs if item["availability"] == "not_retained")
    assert incomplete["progress"]["completed_rows"] < 750
    assert client.get(f"/artifacts/{incomplete['run_id']}").status_code == 404

    deterministic = by_mode["deterministic_only"][0]
    assert deterministic["run_id"] == "rules_only"
    assert deterministic["availability"] == "live"
    assert deterministic["model"] == "(model-independent)"


def test_permitted_validation_records_support_the_restored_workbench(client: TestClient) -> None:
    records = client.get("/records/validation")
    assert records.status_code == 200
    assert records.json()["count"] == 15
    assert {record["source_row_index"] for record in records.json()["records"]} >= {10, 79}

    record = client.get("/records/validation/79")
    assert record.status_code == 200
    assert record.json()["source_row_index"] == 79
    assert "6 to 7 per year" in record.json()["note_text"]

    missing = client.get("/records/validation/999999")
    assert missing.status_code == 404
    assert "999999" not in missing.text


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


def test_saved_artifact_replay_is_allowlisted_and_bounded(client: TestClient) -> None:
    run_id = "gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05"
    response = client.get(f"/artifacts/{run_id}", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()["content"]) == 2

    missing = client.get("/artifacts/not-a-real-run")
    assert missing.status_code == 404
    assert "not-a-real-run" not in missing.text


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
    assert body["pipeline"] == "rules_only"
    assert body["source_row_index"] == 314
    assert body["result"]["output"]["final_value"] == "4 per day"
    assert body["result"]["diagnostics"]["candidate_events"]
    assert body["result"]["diagnostics"]["evidence_valid"] is True

    model_call = client.post(
        "/run/note",
        json={"note_text": "four seizures per day", "pipeline": "hybrid_structured_events"},
    )
    assert model_call.status_code == 400
    assert "model" in model_call.json()["error"]["message"].lower()


def test_review_decisions_persist_separately_from_trace_data(client: TestClient) -> None:
    packets = client.get("/qualified-review/packets")
    assert packets.status_code == 200
    packet = packets.json()["packets"][0]
    decision = {
        "attribute_review_id": packet["attribute_review_id"],
        "fact_id": packet["fact_id"],
        "letter_id": packet["letter_id"],
        "attribute_name": packet["attribute_name"],
        "attribute_value": packet["attribute_value"],
        "attribute_entailment": "entailed",
        "value_verdict": "correct",
        "reviewer_rationale": "The exact source phrase says twice daily.",
        "reviewer_confidence": "high",
        "auditor": "local-reviewer",
    }
    saved = client.post("/qualified-review/decide", json=decision)
    assert saved.status_code == 200
    assert saved.json()["status"] == "saved"

    decisions = client.get("/qualified-review/decisions")
    assert decisions.status_code == 200
    matching = [
        item
        for item in decisions.json()["decisions"]
        if item["attribute_review_id"] == packet["attribute_review_id"]
    ]
    assert len(matching) == 1
    assert matching[0]["reviewer_rationale"] == decision["reviewer_rationale"]

    trace = client.get("/api/v1/runs/syn-exect-014/records/SYN-014/trace")
    assert trace.status_code == 200
    assert packet["attribute_review_id"] not in trace.text


def test_review_queues_and_writes_enforce_development_row_policy(client: TestClient) -> None:
    exect_rows = client.get("/gold-audit/rows", params={"dataset": "exectv2"})
    assert exect_rows.status_code == 200
    assert {row["letter_id"] for row in exect_rows.json()["rows"]} == {"EA0002"}

    packets = client.get("/qualified-review/packets")
    assert packets.status_code == 200
    assert packets.json()["packets"]
    assert all(packet["letter_id"] != "EA0032" for packet in packets.json()["packets"])

    ungoverned = client.post(
        "/qualified-review/decide",
        json={
            "attribute_review_id": "not-in-the-governed-queue",
            "reviewer_rationale": "Must not be stored.",
        },
    )
    assert ungoverned.status_code == 404
    assert "not-in-the-governed-queue" not in ungoverned.text

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
