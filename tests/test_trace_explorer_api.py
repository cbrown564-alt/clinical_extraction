from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from clinical_extraction.trace_explorer.api.app import create_app
from clinical_extraction.trace_explorer.index import build_index

FIXTURE = (
    Path("src")
    / "clinical_extraction"
    / "trace_explorer"
    / "fixtures"
    / "syn_014.json"
)


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    output = tmp_path / ".trace_explorer"
    build_index(artifacts=[FIXTURE], output=output, approved_roots=[Path.cwd()])
    return TestClient(create_app(index_dir=output))


def test_catalog_trace_stage_ledger_graph_and_comparison_routes(client: TestClient) -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["index_ready"] is True
    assert health.headers["cache-control"] == "no-store"
    assert health.headers["x-frame-options"] == "DENY"

    catalog = client.get("/api/v1/catalog").json()
    assert catalog["policy_counts"] == {
        "aggregate_only": 1,
        "development_row_level": 0,
        "denied": 0,
        "illustrative": 2,
    }

    runs = client.get("/api/v1/runs").json()["items"]
    assert [run["run_id"] for run in runs] == [
        "syn-aggregate-only",
        "syn-exect-014",
        "syn-gan-014",
    ]

    trace = client.get("/api/v1/runs/syn-exect-014/records/SYN-014/trace")
    assert trace.status_code == 200
    trace_body = trace.json()
    assert trace_body["source"]["source_id"] == "SYN-014"
    assert trace_body["stages"][3]["stage_id"] == "schedule-normalization"

    stage = client.get(
        "/api/v1/runs/syn-exect-014/records/SYN-014/stages/schedule-normalization"
    ).json()
    assert stage["stage"]["changes"][0]["after_value"] == "BID"

    ledger = client.get(
        "/api/v1/runs/syn-exect-014/records/SYN-014/ledger",
        params={"category": "deterministic_semantic"},
    ).json()
    assert [row["operation"] for row in ledger["items"]] == [
        "Normalize the supported schedule phrase to BID"
    ]

    graph = client.get("/api/v1/runs/syn-gan-014/records/SYN-014/graph").json()
    assert len(graph["nodes"]) == 7
    assert len(graph["edges"]) == 6

    comparison = client.post(
        "/api/v1/comparisons/resolve",
        json={
            "left_trace_id": trace_body["trace_id"],
            "right_trace_id": client.get(
                "/api/v1/runs/syn-gan-014/records/SYN-014/trace"
            ).json()["trace_id"],
        },
    )
    assert comparison.status_code == 200
    assert comparison.json()["mode"] == "task_explanation"
    assert any(
        item["semantic_role"] == "evidence_validation"
        for item in comparison.json()["stages"]
    )


def test_aggregate_only_run_has_no_enumerable_record_surface(client: TestClient) -> None:
    run = client.get("/api/v1/runs/syn-aggregate-only")
    assert run.status_code == 200
    assert run.json()["row_policy"] == "aggregate_only"
    assert "source" not in run.text.lower()

    records = client.get("/api/v1/runs/syn-aggregate-only/records")
    assert records.status_code == 403
    assert records.json()["error"]["code"] == "aggregate_only"

    guessed = client.get(
        "/api/v1/runs/syn-aggregate-only/records/SYN-014/trace"
    )
    assert guessed.status_code == 403
    assert guessed.json()["error"]["code"] == "aggregate_only"
    assert "SYN-014" not in guessed.text

    missing = client.get("/api/v1/runs/syn-exect-014/records/UNKNOWN/trace")
    assert missing.status_code == 404
    assert "UNKNOWN" not in missing.text


def test_server_rejects_non_loopback_bind() -> None:
    with pytest.raises(ValueError, match="loopback"):
        create_app(host="0.0.0.0")
