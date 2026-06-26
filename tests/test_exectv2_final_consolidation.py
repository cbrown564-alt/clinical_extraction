"""Tests for Phase 3 final-consolidation report/scorecard builders."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from clinical_extraction.observatory.api import create_app
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    REPO_ROOT,
    build_gan_reliability_scorecard_payload,
    build_reliability_scorecard_payload,
)


def test_reliability_scorecard_payload_parses_final_reports() -> None:
    payload = build_reliability_scorecard_payload()

    assert payload["source_scorecard"].endswith(
        "exectv2_cross_model_reliability_scorecard_2026-06-22.md"
    )
    assert len(payload["dimensions"]) == 10
    assert payload["weak_dimensions"] == []
    assert len(payload["evidence_set"]) == 7
    assert len(payload["comparison_rows"]) == 4
    assert payload["computed_reliability"]["latest_run_check"]["surfaces"][0][
        "replacement_policy"
    ] == "same-surface comparators retained"
    assert payload["computed_reliability"]["review_routing"]["caught_error_cells"] > 0
    balanced_route = next(
        item
        for item in payload["computed_reliability"]["review_routing"][
            "operating_points"
        ]
        if item["id"] == "balanced_dev_candidate"
    )
    assert balanced_route["review_burden"] < 0.8
    assert balanced_route["catch_rate"] > 0.8

    v08 = next(
        row
        for row in payload["comparison_rows"]
        if row["candidate"] == "exectv2_holistic_finding_assembly_v08_dev140"
    )
    assert v08["overall_f1"] == 0.9152
    assert v08["diagnosis_f1"] == 0.9083
    assert v08["exact_evidence_rate"] == 1.0
    deepseek = next(
        row
        for row in payload["comparison_rows"]
        if row["candidate"] == "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140"
    )
    assert deepseek["overall_f1"] == 0.9174
    assert deepseek["seizure_frequency_f1"] == 0.9017


def test_static_frontend_scorecard_matches_builder_contract() -> None:
    static_path = (
        REPO_ROOT
        / "frontend"
        / "public"
        / "mock-data"
        / "exectv2"
        / "reliability-scorecard.json"
    )
    static_payload = json.loads(static_path.read_text(encoding="utf-8"))
    built_payload = build_reliability_scorecard_payload()

    assert static_payload["source_scorecard"] == built_payload["source_scorecard"]
    assert static_payload["source_cross_model_report"] == built_payload["source_cross_model_report"]
    assert static_payload["dimensions"] == built_payload["dimensions"]
    assert static_payload["comparison_rows"] == built_payload["comparison_rows"]
    assert static_payload["computed_reliability"] == built_payload["computed_reliability"]


def test_gan_reliability_scorecard_payload_parses_master_scorecard() -> None:
    payload = build_gan_reliability_scorecard_payload()

    assert payload["dataset"] == "gan2026"
    assert payload["source_scorecard"] == (
        "experiments/gan2026_reliability_master_scorecard_2026-06-17.md"
    )
    assert len(payload["dimensions"]) == 10
    assert payload["dimensions"][0]["dimension"] == "Task correctness"
    assert payload["dimensions"][0]["coverage"] == 4
    assert payload["dimensions"][0]["coverage_max"] == 5
    assert payload["weak_dimensions"] == []


def test_static_gan_scorecard_matches_builder_contract() -> None:
    static_path = (
        REPO_ROOT
        / "frontend"
        / "public"
        / "mock-data"
        / "gan2026"
        / "reliability-scorecard.json"
    )
    static_payload = json.loads(static_path.read_text(encoding="utf-8"))
    built_payload = build_gan_reliability_scorecard_payload()

    assert static_payload["source_scorecard"] == built_payload["source_scorecard"]
    assert static_payload["dimensions"] == built_payload["dimensions"]


def test_observatory_serves_exectv2_reliability_scorecard() -> None:
    client = TestClient(create_app(repo_root=REPO_ROOT))

    response = client.get("/exectv2/reliability-scorecard")

    assert response.status_code == 200
    payload = response.json()
    calibration = next(
        item for item in payload["dimensions"] if item["id"] == "calibration"
    )
    assert calibration["coverage"] == 4
    assert payload["evidence_set"][0]["role"] == "Performance control"
    assert payload["computed_reliability"]["active_llm_only_readout"][1][
        "model_label"
    ] == "DeepSeek chat"


def test_observatory_serves_gan_reliability_scorecard() -> None:
    client = TestClient(create_app(repo_root=REPO_ROOT))

    response = client.get("/gan2026/reliability-scorecard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset"] == "gan2026"
    assert payload["dimensions"][2]["dimension"] == "Faithfulness"
