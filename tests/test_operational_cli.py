from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from clinical_extraction.operational.cli import main
from clinical_extraction.operational.gan import run_gan_notes, score_projection
from clinical_extraction.operational.io import InputNote, read_notes
from clinical_extraction.operational.runtime import RuntimeConfig


def test_read_notes_accepts_jsonl_id_and_text(tmp_path: Path) -> None:
    source = tmp_path / "notes.jsonl"
    source.write_text(
        '{"id":"n1","text":"No seizures since March."}\n'
        '{"id":"n2","text":"Two seizures per month."}\n',
        encoding="utf-8",
    )

    notes = read_notes(source)

    assert [(note.note_id, note.text) for note in notes] == [
        ("n1", "No seizures since March."),
        ("n2", "Two seizures per month."),
    ]


def test_read_notes_rejects_invalid_rows(tmp_path: Path) -> None:
    source = tmp_path / "notes.jsonl"
    source.write_text('{"id":"n1","text":""}\n', encoding="utf-8")

    with pytest.raises(ValueError):
        read_notes(source)


def test_runtime_accepts_vllm_environment_names() -> None:
    runtime = RuntimeConfig.from_environment(
        environment={
            "VLLM_BASE_URL": "https://vllm.example/v1/",
            "VLLM_API_KEY": "secret",
            "VLLM_MODEL": "deepseek-v4-flash",
        }
    )

    assert runtime.base_url == "https://vllm.example/v1"
    assert runtime.model == "vllm/deepseek-v4-flash"
    assert runtime.api_model == "deepseek-v4-flash"


def test_runtime_defaults_to_empty_api_key_for_keyless_vllm() -> None:
    runtime = RuntimeConfig.from_environment(
        environment={
            "VLLM_BASE_URL": "http://127.0.0.1:8000/v1",
            "VLLM_MODEL": "deepseek-v4-flash",
        }
    )

    assert runtime.base_url == "http://127.0.0.1:8000/v1"
    assert runtime.api_key == "EMPTY"
    assert runtime.model == "vllm/deepseek-v4-flash"


def test_runtime_accepts_gemini_key_without_explicit_base_url() -> None:
    runtime = RuntimeConfig.from_environment(
        environment={"GEMINI_API_KEY": "gemini-secret"},
        model="gemini/gemini-3.7-flash",
    )

    assert runtime.base_url == "https://generativelanguage.googleapis.com/v1beta/openai"
    assert runtime.model == "gemini/gemini-3.7-flash"
    assert runtime.api_model == "gemini-3.7-flash"
    assert runtime.api_key == "gemini-secret"


def test_runtime_prefers_openrouter_for_gemini_when_key_present() -> None:
    runtime = RuntimeConfig.from_environment(
        environment={
            "OPENROUTER_API_KEY": "openrouter-secret",
            "GEMINI_API_KEY": "gemini-secret",
        },
        model="gemini/gemini-3.7-flash",
    )

    assert runtime.base_url == "https://openrouter.ai/api/v1"
    assert runtime.model == "gemini/gemini-3.7-flash"
    assert runtime.api_model == "gemini-3.7-flash"
    assert runtime.api_key == "openrouter-secret"


def test_runtime_still_requires_api_key_for_non_vllm_provider() -> None:
    with pytest.raises(ValueError, match="No API key configured"):
        RuntimeConfig.from_environment(
            environment={"CLINICAL_LLM_BASE_URL": "https://api.example/v1"},
            model="openai/example-model",
        )


def test_runtime_rejects_disagreeing_endpoint_aliases() -> None:
    with pytest.raises(ValueError, match="CLINICAL_LLM_BASE_URL and VLLM_BASE_URL disagree"):
        RuntimeConfig.from_environment(
            environment={
                "CLINICAL_LLM_BASE_URL": "https://one.example/v1",
                "VLLM_BASE_URL": "https://two.example/v1",
                "VLLM_API_KEY": "secret",
            }
        )


def test_score_projection_maps_monthly_rate_to_purist_category() -> None:
    projection = score_projection("2 per month")

    assert projection is not None
    assert projection["normalized_label"] == "2 per month"
    assert projection["kind"] == "frequency"
    assert projection["monthly_frequency"] == pytest.approx(2.03, abs=0.05)
    assert projection["purist_category"] == "seizure_freq_more1mon_less1week"
    assert projection["pragmatic_category"] == "seizure_frequent"
    assert "purist_correct" not in projection


def test_score_projection_maps_unknown_without_gold_comparison() -> None:
    projection = score_projection("unknown")

    assert projection is not None
    assert projection["kind"] == "unknown"
    assert projection["purist_category"] == "seizure_freq_unknown"
    assert "gold_purist_category" not in projection


def test_run_gan_notes_includes_normalized_events_and_score_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_result = SimpleNamespace(
        output=SimpleNamespace(
            final_value="2 per month",
            evidence="two seizures per month",
            rationale="stated rate",
        ),
        diagnostics={
            "parse_errors": [],
            "structured_record": {"events": [], "selection": {}},
            "normalized_events": [
                {
                    "event_id": "evt_1",
                    "normalized_label": "2 per month",
                    "semantic_kind": "frequency",
                    "monthly_frequency": 2.0,
                    "yearly_bounds": [24.0, 24.0],
                    "repair_applied": False,
                    "validation_errors": [],
                }
            ],
        },
    )
    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm_with_rules.run_record",
        lambda *args, **kwargs: fake_result,
    )

    rows = run_gan_notes(
        [InputNote("n1", "Two seizures per month.")],
        RuntimeConfig(
            base_url="http://127.0.0.1:8000/v1",
            api_key="EMPTY",
            model="vllm/deepseek-v4-flash",
        ),
    )

    assert rows[0]["normalized_events"][0]["normalized_label"] == "2 per month"
    assert rows[0]["score_projection"]["purist_category"] == (
        "seizure_freq_more1mon_less1week"
    )


def test_cli_writes_one_result_per_input_note(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "notes.jsonl"
    target = tmp_path / "predictions.jsonl"
    source.write_text('{"id":"n1","text":"Two seizures per month."}\n', encoding="utf-8")

    monkeypatch.setattr(
        "clinical_extraction.operational.cli.run_gan_notes",
        lambda notes, runtime: [
            {
                "id": notes[0].note_id,
                "task": "gan",
                "status": "ok",
                "prediction": {"seizure_frequency": "2 per month"},
            }
        ],
    )

    exit_code = main(
        [
            "gan",
            "--input",
            str(source),
            "--output",
            str(target),
            "--base-url",
            "http://localhost:8000/v1",
            "--model",
            "vllm/deepseek-v4-flash",
        ]
    )

    assert exit_code == 0
    row = json.loads(target.read_text(encoding="utf-8"))
    assert row["id"] == "n1"
    assert row["prediction"]["seizure_frequency"] == "2 per month"


def test_exect_operational_import_does_not_load_research_assembly() -> None:
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import clinical_extraction.operational.exect; "
                "assert 'clinical_extraction.tasks.epilepsy_phenotyping.exectv2."
                "assembly.pipeline' not in sys.modules"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stderr
