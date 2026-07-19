from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.trace_explorer.gan2026_comparison import (
    MODEL_CONDITIONS,
    discover_gan2026_validation_runs,
)


def test_discovery_serves_only_complete_validation750_conditions(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    artifact_root = tmp_path / "scratch" / "validation" / "comparison"
    complete_path = artifact_root / "gpt41mini" / "llm_with_rules" / "validation750.rows.jsonl"
    partial_path = artifact_root / "gpt56luna" / "llm_with_rules" / "validation750.rows.jsonl"
    _write_rows(complete_path, range(750), method="llm_with_rules")
    _write_rows(partial_path, range(3), method="llm_with_rules")

    discovery = discover_gan2026_validation_runs(
        config_path,
        expected_indices=set(range(750)),
    )

    families = discovery.catalog["families"]
    complete = next(
        item
        for item in families
        if item["run_id"] == "gan2026_validation750_gpt41mini_llm_with_rules"
    )
    partial = next(
        item
        for item in families
        if item["run_id"] == "gan2026_validation750_gpt56luna_llm_with_rules"
    )
    assert complete["availability"] == "replay"
    assert complete["evidence_scope"] == "validation750_row_level"
    assert complete["metrics"] == {
        "row_count": 750,
        "purist_correct": 375,
        "purist_accuracy": 0.5,
        "pragmatic_correct": 750,
        "pragmatic_accuracy": 1.0,
    }
    assert partial["availability"] == "not_retained"
    assert partial["progress"] == {"completed_rows": 3, "expected_rows": 750}
    assert partial["run_id"] not in discovery.replay_artifacts
    assert set(discovery.replay_artifacts) == {complete["run_id"]}


def test_discovery_rejects_wrong_split_or_trace_schema(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    path = (
        tmp_path
        / "scratch"
        / "validation"
        / "comparison"
        / "gpt41mini"
        / "llm_only"
        / "validation750.rows.jsonl"
    )
    _write_rows(path, range(750), method="llm_only", split="test")

    discovery = discover_gan2026_validation_runs(
        config_path,
        expected_indices=set(range(750)),
    )

    family = next(
        item
        for item in discovery.catalog["families"]
        if item["run_id"].endswith("gpt41mini_llm_only")
    )
    assert family["availability"] == "not_retained"
    assert family["run_id"] not in discovery.replay_artifacts


def test_discovery_treats_a_row_currently_being_written_as_partial(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    path = (
        tmp_path
        / "scratch"
        / "validation"
        / "comparison"
        / "gpt41mini"
        / "llm_with_rules"
        / "validation750.rows.jsonl"
    )
    _write_rows(path, range(3), method="llm_with_rules")
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"source_row_index": 3')

    discovery = discover_gan2026_validation_runs(
        config_path,
        expected_indices=set(range(750)),
    )

    family = next(
        item
        for item in discovery.catalog["families"]
        if item["run_id"].endswith("gpt41mini_llm_with_rules")
    )
    assert family["availability"] == "not_retained"
    assert family["progress"] == {"completed_rows": 3, "expected_rows": 750}


def _write_config(root: Path) -> Path:
    path = root / "configs" / "gan2026" / "six_model_validation_comparison_20260718.json"
    path.parent.mkdir(parents=True)
    payload = {
        "protocol": "docs/protocol.md",
        "artifact_root": "scratch/validation/comparison",
        "conditions": [
            {"slug": condition.slug, "model": condition.route}
            for condition in MODEL_CONDITIONS
        ],
        "methods": [
            {
                "method": "llm_with_rules",
                "prompt_version": "structured-v1",
                "repair_mode": "hybrid_full_stack",
            },
            {
                "method": "llm_only",
                "prompt_version": "llm-only-v1",
                "repair_mode": "model_selected_evidence_benchmark_adapter",
            },
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_rows(
    path: Path,
    indices: range,
    *,
    method: str,
    split: str = "validation",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for index in indices:
            handle.write(
                json.dumps(
                    {
                        "source_row_index": index,
                        "split": split,
                        "split_manifest": "gan2026_split_v1",
                        "row_trace": {
                            "schema_version": "gan2026.row_trace.v1",
                            "method": method,
                        },
                        "comparison": {
                            "purist_correct": index % 2 == 0,
                            "pragmatic_correct": True,
                        },
                    }
                )
                + "\n"
            )
