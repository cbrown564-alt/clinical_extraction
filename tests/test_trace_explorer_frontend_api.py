from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from clinical_extraction.trace_explorer.api.app import create_app
from clinical_extraction.trace_explorer.frontend_data import FrontendDataStore
from clinical_extraction.trace_explorer.index import build_index

TRACE_FIXTURE = (
    Path("src")
    / "clinical_extraction"
    / "trace_explorer"
    / "fixtures"
    / "syn_014.json"
)
FRONTEND_FIXTURES = Path("frontend") / "public" / "mock-data"
EXECT_SPLIT_MANIFEST = Path("data") / "ExECTv2 (2025)" / "splits" / "exectv2_split_v2.json"
GAN_SPLIT_MANIFEST = Path("data") / "Gan (2026)" / "splits" / "gan2026_split_v1.json"

pytestmark = pytest.mark.local_corpus


def _official_split_ids() -> tuple[set[str], set[str], set[str], set[str]]:
    gan = json.loads(GAN_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    exect = json.loads(EXECT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    return (
        {str(index) for index in gan["splits"]["test"]["source_row_indices"]},
        {str(letter_id) for letter_id in exect["splits"]["test"]["letter_ids"]},
        {str(index) for index in gan["splits"]["validation"]["source_row_indices"]},
        {str(letter_id) for letter_id in exect["splits"]["dev"]["letter_ids"]},
    )


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
    assert any(run["pipeline_family"] == "rules" for run in registry.json()["runs"])

    families = client.get("/pipeline-families")
    assert families.status_code == 200
    assert any(family["run_id"] == "rules" for family in families.json()["families"])

    exect_runs = client.get("/exectv2/runs")
    assert exect_runs.status_code == 200
    body = exect_runs.json()
    assert body["split"] == "dev140"
    run_ids = {run["run_id"] for run in body["runs"]}
    assert "rules" in run_ids
    assert "exectv2_winning_mode_gpt56sol_llm_plus_rules_dev140" not in run_ids
    hybrid = [
        run
        for run in body["runs"]
        if run.get("kind") == "llm_with_rules"
    ]
    active_hybrid = [run for run in hybrid if run.get("active_method") == "llm_with_rules"]
    models = {run["model"] for run in active_hybrid}
    if active_hybrid:
        assert "openai/gpt-5.6-sol" not in models


def test_locked_test_records_are_not_enumerable(client: TestClient) -> None:
    for split in ("test", "test450", "test60"):
        response = client.get(f"/records/{split}")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "aggregate_only"
        assert "source_row_index" not in response.text

    guessed = client.get("/records/test/79")
    assert guessed.status_code == 403
    error = guessed.json()["error"]
    assert "79" not in error["message"]
    assert error["details"] == {}


def test_gan_hybrid_workbench_marks_retired_dev750_trees_not_retained(
    client: TestClient,
) -> None:
    families = client.get("/pipeline-families")
    assert families.status_code == 200
    catalog = families.json()["families"]
    models = {family["model"] for family in catalog}
    assert "xai/grok-4.6" in models
    assert "openai/gpt-5.6-luna" in models
    assert "gemini/gemini-3.7-flash" in models
    assert "openai/gpt-5.6-sol" not in models
    assert "ollama_chat/qwen3.6:35b" not in models
    grok = next(
        family
        for family in catalog
        if family["run_id"] == "gan2026_validation750_grok46_llm_with_rules"
    )
    assert grok["label"] == "Grok 4.6"
    assert grok["availability"] == "replay"
    luna = next(
        family
        for family in catalog
        if family["run_id"] == "gan2026_validation750_gpt56luna_llm_with_rules"
    )
    assert luna["availability"] == "replay"
    pending = next(
        family
        for family in catalog
        if family["run_id"] == "gan2026_validation750_qwen38_27b_llm_with_rules"
    )
    assert pending["availability"] == "not_retained"


def test_paper_gan_raw_row_hydrates_structured_trace(client: TestClient) -> None:
    run_id = "gan2026_validation750_gpt56luna_llm_with_rules"
    response = client.get(f"/artifacts/{run_id}", params={"letter_id": "103"})
    assert response.status_code == 200
    row = response.json()["content"][0]
    assert row["source_row_index"] == 103
    assert row["structured_record"]["selection"]["final_label"]
    assert row["normalized_events"]
    assert row["row_trace"]["schema_version"] == "gan2026.row_trace.v1"
    assert row["row_trace"]["method"] == "llm_with_rules"


def test_saved_artifact_replay_is_allowlisted_and_bounded(client: TestClient) -> None:
    run_id = "gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05"
    response = client.get(f"/artifacts/{run_id}", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()["content"]) == 2

    missing = client.get("/artifacts/not-a-real-run")
    assert missing.status_code == 404
    assert "not-a-real-run" not in missing.text


def test_letter_catalogs_cover_the_development_splits(client: TestClient) -> None:
    gan_holdout, exect_holdout, gan_dev, exect_dev = _official_split_ids()

    gan = client.get("/datasets/gan2026/letters")
    assert gan.status_code == 200
    gan_body = gan.json()
    assert gan_body["dataset"] == "gan2026"
    assert gan_body["split"] == "dev750"
    assert gan_body["count"] == 750
    assert gan_body["letters"][0]["id"] == "10"
    gan_ids = {letter["id"] for letter in gan_body["letters"]}
    assert gan_ids == gan_dev
    assert gan_ids.isdisjoint(gan_holdout)

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
    assert letter_ids == exect_dev
    assert letter_ids.isdisjoint(exect_holdout)
    assert len(letter_ids) == 140


def test_holdout_letters_are_not_fetchable(client: TestClient) -> None:
    gan_holdout, exect_holdout, _, _ = _official_split_ids()
    gan_test_id = next(iter(sorted(gan_holdout, key=int)))
    exect_test_id = next(iter(sorted(exect_holdout)))

    gan = client.get(f"/datasets/gan2026/letters/{gan_test_id}")
    assert gan.status_code == 403
    assert gan.json()["error"]["code"] == "aggregate_only"
    assert gan_test_id not in gan.text

    exect = client.get(f"/datasets/exectv2/letters/{exect_test_id}")
    assert exect.status_code == 403
    assert exect.json()["error"]["code"] == "aggregate_only"
    assert exect_test_id not in exect.text

    run = client.get("/datasets/exectv2/runs/rules")
    assert run.status_code == 200
    shared_ids = {letter["letter_id"] for letter in run.json()["shared_letters"]}
    assert exect_test_id not in shared_ids
    assert len(shared_ids) == 140


def test_review_queues_and_writes_enforce_development_row_policy(client: TestClient) -> None:
    gan_rows = client.get("/gold-audit/rows", params={"dataset": "gan2026"})
    assert gan_rows.status_code == 200
    assert gan_rows.json()["total"] == 750
    assert {row["source_row_index"] for row in gan_rows.json()["rows"][:3]} == {
        "10",
        "40",
        "79",
    }
    assert "note_text_single_line" not in gan_rows.json()["rows"][0]
    assert "note_text" not in gan_rows.json()["rows"][0]

    exect_rows = client.get("/gold-audit/rows", params={"dataset": "exectv2"})
    assert exect_rows.status_code == 200
    assert exect_rows.json()["total"] == 140
    assert "full_letter_text" not in exect_rows.json()["rows"][0]
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

    _, exect_holdout, _, _ = _official_split_ids()
    gold_ids = {row["letter_id"] for row in exect_rows.json()["rows"]}
    assert gold_ids.isdisjoint(exect_holdout)


def test_run_note_executes_the_real_deterministic_pipeline(client: TestClient) -> None:
    response = client.post(
        "/run/note",
        json={
            "note_text": "She currently reports four seizures per day.",
            "pipeline": "rules",
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


def test_frontend_store_drops_holdout_ids_even_when_payloads_include_them() -> None:
    _, exect_holdout, _, _ = _official_split_ids()
    holdout_id = next(iter(sorted(exect_holdout)))
    store = FrontendDataStore(FRONTEND_FIXTURES)
    store._exectv2_payload = {
        **store._exectv2_payload,
        "shared_letters": [
            *store._exect_shared_letters(),
            {
                "letter_id": holdout_id,
                "split": "test60",
                "letter_text": "REDACTED",
                "gold_mentions": [],
            },
        ],
    }

    catalog_ids = {letter["id"] for letter in store.letters("exectv2")["letters"]}
    shared_ids = {letter["letter_id"] for letter in store._exect_shared_letters()}
    assert holdout_id not in catalog_ids
    assert holdout_id not in shared_ids
    assert store.is_locked_letter("exectv2", holdout_id)
    assert store.letter("exectv2", holdout_id) is None
    assert len(catalog_ids) == 140


def test_frontend_api_serves_the_living_gan_dev750_panel(client: TestClient) -> None:
    panel = client.get("/paper/gan/dev750")
    assert panel.status_code == 200
    body = panel.json()
    assert body["split"] == "dev750"
    assert body["method_identity"] == "grok46"
    assert len(body["cells"]) == 12
    grok = client.get("/paper/gan/dev750/gan_llm_with_rules/grok46/scored")
    assert grok.status_code == 200
    scored = grok.json()
    assert scored["count"] == 750
    assert scored["rows"][0]["letter_id"] == str(scored["rows"][0]["source_row_index"])
    letters = client.get("/datasets/gan2026/letters")
    assert letters.status_code == 200
    letter_ids = {letter["id"] for letter in letters.json()["letters"]}
    scored_ids = {row["letter_id"] for row in scored["rows"]}
    assert letter_ids
    assert scored_ids & letter_ids
    pending = client.get("/paper/gan/dev750/gan_llm_only/qwen38_27b/scored")
    assert pending.status_code == 404


def test_exect_workbench_run_uses_living_paper_raws(client: TestClient) -> None:
    run_id = "exectv2_dev140_gpt56luna_llm_plus_rules"
    response = client.get(f"/exectv2/runs/{run_id}")
    assert response.status_code == 200
    run = response.json()["run"]
    assert run["model"] == "openai/gpt-5.6-luna"
    letter = next(item for item in run["letters"] if item["letter_id"] == "EA0002")
    assert letter["predicted_mentions"]
    entities = {item["entity"] for item in letter["predicted_mentions"]}
    assert "Diagnosis" in entities


def test_frontend_api_serves_the_living_exect_dev140_panel(client: TestClient) -> None:
    panel = client.get("/paper/exect/dev140")
    assert panel.status_code == 200
    body = panel.json()
    assert body["split"] == "dev140"
    assert body["method_identity"] == "grok46"
    assert body["methods"] == [
        "rules_only",
        "llm_schema",
        "llm_encode",
        "llm_revise",
        "llm_pre_post",
    ]
    assert len(body["cells"]) == 30
    grok = client.get("/paper/exect/dev140/exect_llm_pre_post/grok46/scored")
    assert grok.status_code == 200
    scored = grok.json()
    assert scored["method"] == "exect_llm_pre_post"
    assert scored["count"] == 140
    llm_only = client.get("/paper/exect/dev140/exect_llm_only/grok46/scored")
    assert llm_only.status_code == 200
    assert llm_only.json()["method"] == "exect_llm_only"
    assert llm_only.json()["count"] == 140
    letters = client.get("/datasets/exectv2/letters")
    assert letters.status_code == 200
    letter_ids = {letter["id"] for letter in letters.json()["letters"]}
    scored_ids = {row["letter_id"] for row in scored["rows"]}
    assert letter_ids
    assert scored_ids & letter_ids
    pending = client.get("/paper/exect/dev140/exect_llm_only/qwen38_27b/scored")
    assert pending.status_code == 404
    alias = client.get("/paper/exect/dev140/grok46/scored")
    assert alias.status_code == 200
    assert alias.json()["method"] == "exect_llm_pre_post"
