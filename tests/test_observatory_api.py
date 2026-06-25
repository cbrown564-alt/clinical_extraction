from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from clinical_extraction.observatory.api import create_app


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
        "\n".join(
            [
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
                ),
                json.dumps(
                    {
                        "run_id": "retired_run",
                        "artifact_paths": ["experiments/example.jsonl"],
                        "date": "2026-06-02",
                        "pipeline_family": "llm_only_claim_table_selector",
                        "split": "validation",
                        "row_count": 1,
                        "model": "openai/gpt-4.1-mini",
                        "model_role": "retired claim-table selector",
                        "mode": "historical",
                        "replay_status": "analysis_only",
                        "decision": "historical",
                    }
                ),
                json.dumps(
                    {
                        "run_id": "retained_comparator",
                        "artifact_paths": ["experiments/example.jsonl"],
                        "date": "2026-06-02",
                        "pipeline_family": "llm_heavy_clinical_frequency_reasoner",
                        "split": "validation",
                        "row_count": 1,
                        "model": "openai/gpt-4.1-mini",
                        "model_role": "retained comparator",
                        "mode": "historical",
                        "replay_status": "analysis_only",
                        "decision": "historical",
                    }
                ),
                json.dumps(
                    {
                        "run_id": "unknown_family",
                        "artifact_paths": ["experiments/example.jsonl"],
                        "date": "2026-06-02",
                        "pipeline_family": "unreviewed_old_family",
                        "split": "validation",
                        "row_count": 1,
                        "model": "openai/gpt-4.1-mini",
                        "model_role": "unreviewed family",
                        "mode": "historical",
                        "replay_status": "analysis_only",
                        "decision": "historical",
                    }
                ),
            ]
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
    family_values = {
        family["run_id"] for family in client.get("/pipeline-families").json()["families"]
    }
    # Explorer dropdown is registry-driven: one entry per curated comparator run.
    assert family_values == {
        "rules_only",
        "gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07",
        "gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08",
        "gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08",
        "gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07",
        "gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08",
        "gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08",
    }
    assert "llm_only_claim_table_selector" not in family_values
    assert "unreviewed_old_family" not in family_values
    assert "llm_heavy_clinical_frequency_reasoner" not in family_values
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


def test_gold_audit_endpoints(tmp_path: Path) -> None:
    repo_root = tmp_path
    experiments = repo_root / "experiments"
    experiments.mkdir()

    # Create a tiny ambiguity review CSV
    csv_path = experiments / "gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv"
    import csv
    fieldnames = [
        "manual_ambiguity_label", "manual_notes", "manual_corrected_gold_label",
        "validation_order", "source_row_index", "split", "gold_label", "gold_label_kind",
        "gold_reference", "codex_initial_ambiguity_label", "codex_ambiguity_reasons",
        "codex_ambiguity_rationale", "gold_monthly_frequency", "gold_yearly_bounds",
        "row_ok", "labels_match_all_categories", "quotes_ok_all_categories",
        "reference_found_in_note", "reference_context", "note_text_single_line",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerow({
            "manual_ambiguity_label": "",
            "manual_notes": "",
            "manual_corrected_gold_label": "",
            "validation_order": "1",
            "source_row_index": "42",
            "split": "validation",
            "gold_label": "2 per month",
            "gold_label_kind": "frequency",
            "gold_reference": "twice per month",
            "codex_initial_ambiguity_label": "ambiguous",
            "codex_ambiguity_reasons": "range_or_upper_bound",
            "codex_ambiguity_rationale": "Initial screen: range or upper bound.",
            "gold_monthly_frequency": "2.0",
            "gold_yearly_bounds": "24.0 to 24.0",
            "row_ok": "True",
            "labels_match_all_categories": "True",
            "quotes_ok_all_categories": "True",
            "reference_found_in_note": "True",
            "reference_context": "...twice per month...",
            "note_text_single_line": "Current seizures occur twice per month.",
        })
        writer.writerow({
            "manual_ambiguity_label": "",
            "manual_notes": "",
            "manual_corrected_gold_label": "",
            "validation_order": "2",
            "source_row_index": "99",
            "split": "validation",
            "gold_label": "unknown",
            "gold_label_kind": "unknown",
            "gold_reference": "frequency unknown",
            "codex_initial_ambiguity_label": "clear",
            "codex_ambiguity_reasons": "",
            "codex_ambiguity_rationale": (
                "Initial screen: gold label and reference look directly reviewable without an "
                "obvious ambiguity flag."
            ),
            "gold_monthly_frequency": "-1.0",
            "gold_yearly_bounds": "-1.0 to -1.0",
            "row_ok": "True",
            "labels_match_all_categories": "True",
            "quotes_ok_all_categories": "True",
            "reference_found_in_note": "False",
            "reference_context": "",
            "note_text_single_line": "No frequency mentioned.",
        })

    split_path = repo_root / "splits.json"
    split_path.write_text(
        json.dumps({"splits": {"validation": {"source_row_indices": [42, 99]}}}),
        encoding="utf-8",
    )

    client = TestClient(
        create_app(
            repo_root=repo_root,
            split_manifest_path=split_path,
            registry_path=repo_root / "missing_registry.jsonl",
            experiments_dir=experiments,
        )
    )

    # Rows endpoint
    r = client.get("/gold-audit/rows?split=validation")
    assert r.status_code == 200
    payload = r.json()
    assert payload["total"] == 2
    assert payload["decided"] == 0
    assert payload["sampling_model"]["model_kind"] == "smoothed_feature_naive_bayes_active_sampler"
    assert payload["sampling_model"]["decision_count"] == 0
    rows = payload["rows"]
    assert len(rows) == 2
    assert rows[0]["source_row_index"] == "42"
    assert rows[0]["priority_score"] == rows[0]["active_learning_score"]
    assert rows[0]["predicted_simple_class"] in {"correct", "ambiguous", "wrong"}
    assert rows[0]["priority_score"] > rows[1]["priority_score"]  # ambiguous scores higher

    # Next endpoint
    r = client.get("/gold-audit/next?split=validation")
    assert r.status_code == 200
    next_row = r.json()["row"]
    assert next_row is not None
    assert next_row["source_row_index"] == "42"

    # Decisions endpoint (empty)
    r = client.get("/gold-audit/decisions?split=validation")
    assert r.status_code == 200
    assert r.json()["count"] == 0

    # Save a decision
    r = client.post("/gold-audit/decide", json={
        "source_row_index": 42,
        "split": "validation",
        "simple_class": "ambiguous",
        "rq10_class": "benchmark_convention_dominated",
        "notes": "test note",
        "benchmark_convention_flag": True,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "saved"
    assert r.json()["decision"]["simple_class"] == "ambiguous"
    assert r.json()["decision"]["rq10_class"] == "benchmark_convention_dominated"

    # Decisions endpoint (one saved)
    r = client.get("/gold-audit/decisions?split=validation")
    assert r.status_code == 200
    assert r.json()["count"] == 1

    r = client.get("/gold-audit/rows?split=validation")
    assert r.status_code == 200
    payload = r.json()
    assert payload["decided"] == 1
    assert payload["sampling_model"]["decision_count"] == 1
    assert payload["rows"][0]["has_decision"] is True

    # Next should now return the other row
    r = client.get("/gold-audit/next?split=validation")
    assert r.status_code == 200
    next_row = r.json()["row"]
    assert next_row is not None
    assert next_row["source_row_index"] == "99"

    # Save second decision
    r = client.post("/gold-audit/decide", json={
        "source_row_index": 99,
        "split": "validation",
        "simple_class": "wrong",
        "rq10_class": "possible_gold_weakness",
        "notes": "",
    })
    assert r.status_code == 200

    # Next should now return None
    r = client.get("/gold-audit/next?split=validation")
    assert r.status_code == 200
    assert r.json()["row"] is None
