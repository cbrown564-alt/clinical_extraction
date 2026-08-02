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
    assert all(run["task"] == "exectv2" for run in exect_runs.json()["runs"])
    rules = next(run for run in exect_runs.json()["runs"] if run["run_id"] == "rules")
    assert rules["pipeline_family"] == "rules"
    assert rules["saved_run_id"] == "exectv2_deterministic_all9_dev140"
    assert rules["retained_evidence_id"] == "exectv2_deterministic_all9_dev_20260714"

    hybrid = [
        run
        for run in exect_runs.json()["runs"]
        if run.get("kind") == "llm_with_rules"
    ]
    active_hybrid = [run for run in hybrid if run.get("active_method") == "llm_with_rules"]
    assert len(active_hybrid) == 1
    assert active_hybrid[0]["model"] == "openai/gpt-5.6-sol"
    for alias in ("llm_with_rules", "exectv2_llm_with_rules"):
        selected = client.get(f"/exectv2/runs/{alias}")
        assert selected.status_code == 200
        assert selected.json()["run"]["run_id"] == active_hybrid[0]["run_id"]

    for run_id in (
        "rules",
        "rules_only",
        "exectv2_rules_only",
        "exectv2_deterministic_all9_dev140",
        "exectv2_deterministic_all9_dev_20260714",
    ):
        selected = client.get(f"/exectv2/runs/{run_id}")
        assert selected.status_code == 200
        assert selected.json()["run"]["run_id"] == "rules"

    for run_id in ("deterministic_all9", "exectv2_deterministic_all9"):
        assert client.get(f"/exectv2/runs/{run_id}").status_code == 404

    assert client.get("/exectv2/runs/None").status_code == 404

    scorecard = client.get("/gan2026/reliability-scorecard")
    assert scorecard.status_code == 200
    assert scorecard.json()["dataset"] == "gan2026"


def test_exect_alias_resolution_is_exact_and_collision_safe() -> None:
    from clinical_extraction.trace_explorer.frontend_data import FrontendDataStore

    store = FrontendDataStore(FRONTEND_FIXTURES)
    store._exectv2_payload = {
        "runs": [
            {"run_id": "rules_only", "saved_run_id": "same-alias", "method_id": "llm_with_rules"},
            {"run_id": "llm", "saved_run_id": "same-alias"},
        ],
        "shared_letters": [],
    }

    assert store.exectv2_run("unknown") is None
    assert store.exectv2_run("same-alias") is None

    store._exectv2_payload = {
        "runs": [
            {"run_id": "rules", "saved_run_id": "saved-rules"},
            {"run_id": "llm", "method_id": "rules", "legacy_run_ids": ["rules"]},
        ],
        "shared_letters": [],
    }
    assert store.exectv2_run("rules") is None


def test_exect_architectures_are_the_winning_mode_model_matrix(client: TestClient) -> None:
    response = client.get("/exectv2/runs", headers={"Accept-Encoding": "identity"})

    assert response.status_code == 200
    assert len(response.content) < 100_000
    payload = response.json()
    runs = payload["runs"]
    assert len(runs) == 13

    by_method: dict[str, list[dict[str, object]]] = {}
    for run in runs:
        method = str(run.get("kind") or run.get("active_method") or "")
        by_method.setdefault(method, []).append(run)

    assert {method: len(items) for method, items in by_method.items()} == {
        "llm_with_rules": 6,
        "llm": 6,
        "rules": 1,
    }

    expected_models = {
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    }
    assert {str(run["model"]) for run in by_method["llm_with_rules"]} == expected_models
    assert {str(run["model"]) for run in by_method["llm"]} == expected_models
    assert by_method["rules"][0]["model"] == "(model-independent)"

    sol_final = next(
        run
        for run in by_method["llm_with_rules"]
        if run["model"] == "openai/gpt-5.6-sol"
    )
    sol_raw = next(
        run for run in by_method["llm"] if run["model"] == "openai/gpt-5.6-sol"
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

    by_method: dict[str, list[dict[str, object]]] = {}
    for family in families:
        by_method.setdefault(str(family["kind"]), []).append(family)

    assert {method: len(items) for method, items in by_method.items()} == {
        "llm_with_rules": 6,
        "llm": 6,
        "rules": 1,
    }

    expected_models = [
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    ]
    assert [str(item["model"]) for item in by_method["llm_with_rules"]] == expected_models
    assert [str(item["model"]) for item in by_method["llm"]] == expected_models

    model_runs = [*by_method["llm_with_rules"], *by_method["llm"]]
    assert all(item["split"] == "validation750" for item in model_runs)
    assert all("test450" not in str(item["run_id"]) for item in model_runs)
    assert all(item["availability"] in {"replay", "not_retained"} for item in model_runs)
    for item in model_runs:
        replayable = item["availability"] == "replay"
        assert item["has_replay_artifact"] is replayable
        assert item["evidence_scope"] == (
            "validation750_row_level" if replayable else "incomplete_not_served"
        )

    completed = next(
        (item for item in model_runs if item["availability"] == "replay"),
        None,
    )
    if completed is not None:
        assert completed["metrics"]["row_count"] == 750
        replay = client.get(f"/artifacts/{completed['run_id']}", params={"limit": 2})
        assert replay.status_code == 200
        assert len(replay.json()["content"]) == 2
        assert all(row["split"] == "validation" for row in replay.json()["content"])

    deterministic = by_method["rules"][0]
    assert deterministic["run_id"] == "rules"
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

    replay_record = client.get("/records/validation/1694")
    assert replay_record.status_code == 200
    assert replay_record.json()["source_row_index"] == 1694
    assert replay_record.json()["split"] == "validation"
    assert replay_record.json()["note_text"]

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
    assert body["pipeline"] == "rules"
    assert body["source_row_index"] == 314
    assert body["result"]["output"]["final_value"] == "4 per day"
    assert body["result"]["diagnostics"]["candidate_events"]
    assert body["result"]["diagnostics"]["evidence_valid"] is True

    rejection_messages = []
    for pipeline in ("llm_with_rules", "hybrid_structured_events"):
        model_call = client.post(
            "/run/note",
            json={"note_text": "four seizures per day", "pipeline": pipeline},
        )
        assert model_call.status_code == 400
        assert model_call.json()["error"]["code"] == "model_calls_disabled"
        rejection_messages.append(model_call.json()["error"]["message"])
    assert rejection_messages[0] == rejection_messages[1]


def test_review_decisions_persist_separately_from_trace_data(client: TestClient) -> None:
    reviewer_id = "local-reviewer"
    packets = client.get("/qualified-review/packets", params={"reviewer_id": reviewer_id})
    assert packets.status_code == 200
    packet = packets.json()["packets"][0]
    decision = {
        "attribute_review_id": packet["attribute_review_id"],
        "fact_id": packet["fact_id"],
        "letter_id": packet["letter_id"],
        "attribute_name": packet["attribute_name"],
        "attribute_value": packet["attribute_value"],
        "reviewer_id": reviewer_id,
        "correctness": "correct",
        "review_notes": "The exact source phrase supports the stored value.",
    }
    saved = client.post("/qualified-review/decide", json=decision)
    assert saved.status_code == 200
    assert saved.json()["status"] == "saved"

    decisions = client.get("/qualified-review/decisions", params={"reviewer_id": reviewer_id})
    assert decisions.status_code == 200
    matching = [
        item
        for item in decisions.json()["decisions"]
        if item["attribute_review_id"] == packet["attribute_review_id"]
    ]
    assert len(matching) == 1
    assert matching[0]["review_notes"] == decision["review_notes"]
    assert matching[0]["revision"] == 1

    other_reviewer = client.get(
        "/qualified-review/decisions", params={"reviewer_id": "other-reviewer"}
    )
    assert other_reviewer.json()["count"] == 0

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
            "reviewer_id": "local-reviewer",
            "correctness": "incorrect",
            "review_notes": "Must not be stored.",
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


def test_semantic_support_review_is_blinded_revisioned_and_dev_only(
    client: TestClient,
) -> None:
    reviewer_id = "independent-clinician-a"
    queue = client.get(
        "/semantic-support-review/packets",
        params={"reviewer_id": reviewer_id},
    )

    assert queue.status_code == 200
    payload = queue.json()
    assert payload["protocol_version"] == "exectv2-semantic-support-review-v2"
    assert payload["allowed_values"] == {
        "clinical_support": ["supported", "unsupported", "unclear"]
    }
    assert payload["blinded"] is True
    assert payload["total"] == 48
    assert payload["decided"] == 0
    assert len(payload["packets"]) == 48
    assert all(packet["full_letter_text"] for packet in payload["packets"])
    assert all(packet["letter_id"].startswith("EA") for packet in payload["packets"])
    assert "gold_mentions" not in queue.text
    assert all(
        {"gold_mentions", "gold_correct", "model_correct"}.isdisjoint(packet)
        for packet in payload["packets"]
    )

    packet = payload["packets"][0]
    decision = {
        "review_item_id": packet["review_item_id"],
        "reviewer_id": reviewer_id,
        "clinical_support": "supported",
        "review_notes": "Exact wording supports the extracted finding.",
    }
    first = client.post("/semantic-support-review/decide", json=decision)
    assert first.status_code == 200
    assert first.json()["decision"]["revision"] == 1

    revised = client.post(
        "/semantic-support-review/decide",
        json={**decision, "clinical_support": "unclear"},
    )
    assert revised.status_code == 200
    assert revised.json()["decision"]["revision"] == 2

    own_decisions = client.get(
        "/semantic-support-review/decisions",
        params={"reviewer_id": reviewer_id},
    )
    assert own_decisions.status_code == 200
    assert own_decisions.json()["count"] == 1
    assert own_decisions.json()["decisions"][0]["revision"] == 2

    other_queue = client.get(
        "/semantic-support-review/packets",
        params={"reviewer_id": "independent-clinician-b"},
    )
    assert other_queue.status_code == 200
    assert other_queue.json()["decided"] == 0
    assert not any(packet["has_decision"] for packet in other_queue.json()["packets"])

    export = client.get(
        "/semantic-support-review/export",
        params={"reviewer_id": reviewer_id},
    )
    assert export.status_code == 200
    assert export.json()["completion"]["decided"] == 1
    assert [item["revision"] for item in export.json()["revisions"]] == [1, 2]


def test_semantic_support_review_keeps_notes_optional_for_every_judgment(
    client: TestClient,
) -> None:
    packet = client.get("/semantic-support-review/packets").json()["packets"][0]
    for judgment in ("supported", "unsupported", "unclear"):
        response = client.post(
            "/semantic-support-review/decide",
            json={
                "review_item_id": packet["review_item_id"],
                "reviewer_id": f"independent-clinician-{judgment}",
                "clinical_support": judgment,
            },
        )
        assert response.status_code == 200


def test_semantic_support_review_rejects_the_retired_schema(client: TestClient) -> None:
    packet = client.get("/semantic-support-review/packets").json()["packets"][0]
    response = client.post(
        "/semantic-support-review/decide",
        json={
            "review_item_id": packet["review_item_id"],
            "reviewer_id": "independent-clinician-a",
            "semantic_support": "supported",
        },
    )

    assert response.status_code == 422
