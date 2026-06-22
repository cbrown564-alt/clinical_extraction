"""Tests for the index-driven ExECTv2 frontend mock-data generator (Phase B)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = ROOT / "scripts" / "build_exectv2_frontend_mock_data.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_exectv2_frontend_mock_data", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


SAMPLE_INDEX = """# Final Artifact Index

## Canonical Artifact Groups

### Gan 2026 Reliability Package

| Field | Value |
| --- | --- |
| Candidate | Gan 2026 reliability master scorecard |
| Model | GPT-4.1-mini plus comparators |
| Split and row count | Validation and locked-test |

### ExECTv2 v08 Dev140 Control

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v08_dev140` |
| Model | GPT-4.1-mini-family source lanes plus deterministic assembly |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml` |
| JSON | `experiments/v08.json` |
| JSONL | `experiments/v08.jsonl` |
| Claim boundary | Dev-only component-attributed architecture evidence; not a benchmark claim |
| Promotion decision | Current ExECTv2 performance control |

Stable hashes:

| Path | SHA-256 |
| --- | --- |
| `experiments/v08.json` | `deadbeef` |

### ExECTv2 DeepSeek v0.9.16 Dev140 Diagnostic

| Field | Value |
| --- | --- |
| Candidate | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` |
| Model | `deepseek/deepseek-chat` source artifact; no-call reparse |
| Split and row count | `dev140`, 140 letters |
| Scorer/view | `headline_target` clinical headline |
| Config | `configs/x/v0916.yaml` |
| Source JSONL | `experiments/source_deepseek.jsonl` |
| JSON | `experiments/v0916.json` |
| JSONL | `experiments/v0916.jsonl` |
| Claim boundary | `diagnostic-same-raw-deepseek-dev140` |
| Promotion decision | Final diagnostic comparator; do not promote |

## Non-Canonical, Scratch, Or Superseded Artifacts

### ExECTv2 Superseded Thing

| Field | Value |
| --- | --- |
| Candidate | `exectv2_should_not_appear_dev25` |
| JSON | `experiments/nope.json` |
| JSONL | `experiments/nope.jsonl` |
"""


def test_parses_only_canonical_exectv2_sections():
    runs = mod.parse_canonical_exectv2_runs(SAMPLE_INDEX)
    run_ids = [r["run_id"] for r in runs]
    # Gan (prose candidate) and the non-canonical section are excluded.
    assert run_ids == [
        "exectv2_holistic_finding_assembly_v08_dev140",
        "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140",
    ]


def test_control_spec_field_mapping():
    runs = mod.parse_canonical_exectv2_runs(SAMPLE_INDEX)
    v08 = runs[0]
    assert v08["decision"] == "control"
    assert v08["label"] == "v08 Dev140 Control"
    assert v08["split"] == "dev140"
    assert v08["model"] == "openai/gpt-4.1-mini"
    assert v08["scorer_view"] == "headline_target"
    assert v08["summary_path"] == "experiments/v08.json"
    assert v08["assembly_jsonl_path"] == "experiments/v08.jsonl"
    assert v08["promotion_decision"] == "performance-control"
    # No "Source JSONL" row -> falls back to the canonical dev140 text source.
    assert v08["text_source_paths"] == mod.FALLBACK_TEXT_SOURCES["dev140"]
    # The trailing hashes table must not leak into fields.
    assert "deadbeef" not in str(v08)


def test_diagnostic_spec_uses_index_source_then_fallback():
    runs = mod.parse_canonical_exectv2_runs(SAMPLE_INDEX)
    deepseek = runs[1]
    assert deepseek["decision"] == "diagnostic"
    assert deepseek["model"] == "deepseek/deepseek-chat"
    assert deepseek["promotion_decision"] == "diagnostic-comparator"
    assert deepseek["architecture_family"] == "deepseek_reparse"
    # Index "Source JSONL" comes first, then the split fallback.
    assert deepseek["text_source_paths"][0] == "experiments/source_deepseek.jsonl"
    assert mod.FALLBACK_TEXT_SOURCES["dev140"][0] in deepseek["text_source_paths"]
    # Kebab claim boundary is humanised for display.
    assert deepseek["claim_boundary"] == "diagnostic same raw deepseek dev140"


def test_helper_units():
    assert mod._decision_from_heading("ExECTv2 v09 Partial Hybrid Simplification") == "simplification"
    assert mod._decision_from_heading("ExECTv2 Foo Diagnostic") == "diagnostic"
    assert mod._decision_from_heading("ExECTv2 Bar Control") == "control"
    # Precedence: simplicity beats performance when both appear.
    assert mod._promotion_slug("Simplicity control, not performance control") == "simplicity-control"
    assert mod._architecture_family("exectv2_holistic_finding_assembly_v08_dev140", "dev140") == "holistic_finding_assembly"
    assert (
        mod._architecture_family("exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140", "dev140")
        == "qwencompact_residualrepair"
    )


def test_real_index_parses_to_known_runs():
    index_path = mod.find_index_path()
    runs = mod.load_run_specs_from_index(index_path)
    run_ids = {r["run_id"] for r in runs}
    assert "exectv2_holistic_finding_assembly_v08_dev140" in run_ids
    assert "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140" in run_ids
    assert "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140" in run_ids
    # Every parsed run must carry the required render inputs.
    for run in runs:
        assert run["summary_path"] and run["assembly_jsonl_path"]
        assert run["split"] and run["decision"] and run["scorer_view"]


def test_validate_specs_flags_missing_artifacts():
    bad = [{"run_id": "x", "summary_path": "experiments/does_not_exist.json", "assembly_jsonl_path": None}]
    with pytest.raises(SystemExit) as exc:
        mod.validate_specs(bad)
    assert "does_not_exist" in str(exc.value)
