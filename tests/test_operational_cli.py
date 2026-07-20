from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from clinical_extraction.operational.cli import main
from clinical_extraction.operational.exect import _assemble
from clinical_extraction.operational.io import read_notes
from clinical_extraction.operational.provider import probe_endpoint
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter


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


@pytest.mark.parametrize(
    "payload",
    [
        "not json\n",
        '{"id":"n1"}\n',
        '{"id":"n1","text":""}\n',
        '{"id":"n1","text":"first"}\n{"id":"n1","text":"second"}\n',
    ],
)
def test_read_notes_rejects_invalid_rows(tmp_path: Path, payload: str) -> None:
    source = tmp_path / "notes.jsonl"
    source.write_text(payload, encoding="utf-8")

    with pytest.raises(ValueError):
        read_notes(source)


def test_runtime_config_uses_neutral_openai_compatible_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLINICAL_LLM_BASE_URL", "http://localhost:8000/v1/")
    monkeypatch.setenv("CLINICAL_LLM_API_KEY", "secret")
    monkeypatch.setenv("CLINICAL_LLM_MODEL", "deepseek-v4-flash")

    config = RuntimeConfig.from_environment()

    assert config.base_url == "http://localhost:8000/v1"
    assert config.api_key == "secret"
    assert config.model == "openai/deepseek-v4-flash"
    assert "secret" not in repr(config)


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
            "--api-key",
            "test-key",
            "--model",
            "deepseek-v4-flash",
        ]
    )

    assert exit_code == 0
    row = json.loads(target.read_text(encoding="utf-8"))
    assert row["id"] == "n1"
    assert row["prediction"]["seizure_frequency"] == "2 per month"


def test_cli_refuses_to_overwrite_output(tmp_path: Path) -> None:
    source = tmp_path / "notes.jsonl"
    target = tmp_path / "predictions.jsonl"
    source.write_text('{"id":"n1","text":"Text"}\n', encoding="utf-8")
    target.write_text("existing\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        main(
            [
                "gan",
                "--input",
                str(source),
                "--output",
                str(target),
                "--base-url",
                "http://localhost:8000/v1",
                "--api-key",
                "test-key",
            ]
        )

    assert target.read_text(encoding="utf-8") == "existing\n"


def test_probe_uses_chat_completions_without_disclosing_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    class Message:
        content = '{"ok":true}'
        model_extra: dict = {}

    class Response:
        model = "deepseek-v4-flash"
        choices = [type("Choice", (), {"message": Message()})()]

    class Completions:
        def create(self, **kwargs: object) -> Response:
            captured.update(kwargs)
            return Response()

    class Client:
        def __init__(self, **kwargs: object) -> None:
            captured["client"] = kwargs
            self.chat = type("Chat", (), {"completions": Completions()})()

    monkeypatch.setattr("openai.OpenAI", Client)
    runtime = RuntimeConfig(
        base_url="http://localhost:8000/v1",
        api_key="secret",
        model="openai/deepseek-v4-flash",
    )

    result = probe_endpoint(runtime)

    assert captured["model"] == "deepseek-v4-flash"
    assert captured["response_format"] == {"type": "json_object"}
    assert result["status"] == "ok"
    assert "secret" not in json.dumps(result)


def test_exect_empty_model_result_survives_selected_deterministic_assembly() -> None:
    source_row = {
        "letter_id": "n1",
        "split": "operational",
        "prompt_version": "exectv2_key_entities_structured_v0.8",
        "prompt_profile": "full",
        "pipeline_family": "exectv2_key_entities_structured",
        "model": "openai/deepseek-v4-flash",
        "mode": "live",
        "prompt_input_json": "{}",
        "raw_output": "{}",
        "call_error": None,
        "initial_parse_errors": [],
        "parse_errors": [],
        "structured_output_failure_codes": [],
        "format_retry_output": "",
        "format_retry_notes": [],
        "gate_warnings": [],
        "n_events_raw": 0,
        "n_mentions_raw": 0,
        "n_mentions_scored": 0,
        "n_evidence_invalid": 0,
        "structured_events": [],
        "predicted_mentions": [],
        "gold_mentions": [],
    }

    assembled = _assemble([ExectLetter("n1", "No relevant findings.")], [source_row])

    assert assembled["n1"]["predicted_mentions"] == []
    assert set(assembled["n1"]["lanes"]) == {
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    }


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
