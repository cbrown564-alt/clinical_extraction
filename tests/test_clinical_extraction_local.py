from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from clinical_extraction_local import ClinicalExtractor, ModelResponse, VLLMClient
from clinical_extraction_local.config import EndpointConfig
from clinical_extraction_local.errors import ConfigurationError, InputValidationError
from clinical_extraction_local.input import read_notes


class QueueModel:
    def __init__(self, *responses: str | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def complete_json(self, **request: object) -> ModelResponse:
        self.calls.append(request)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return ModelResponse(
            content=value,
            requested_model="deepseek-v4-flash",
            response_model="deepseek-v4-flash",
        )


GAN_RESPONSE = json.dumps(
    {
        "events": [
            {
                "event_id": "e1",
                "kind": "frequency_rate",
                "raw_value": "two seizures per month",
                "applies_to": "seizures",
                "time_window": "current",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": "two seizures per month",
                "notes": None,
            }
        ],
        "selection": {
            "selected_event_ids": ["e1"],
            "final_kind": "frequency",
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "confidence": "high",
            "rationale": "The note states the current monthly rate.",
        },
    }
)

EXECT_RESPONSE = json.dumps(
    {
        "clinical_events": [
            {
                "family": "diagnosis",
                "anchor_text": "focal epilepsy",
                "evidence": "focal epilepsy",
                "event_state": {"assertion": "present"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "focal epilepsy",
                        "attributes": {"assertion": "present"},
                    }
                ],
                "confidence": "high",
                "rationale": "",
            }
        ]
    }
)


def test_config_rejects_disagreeing_primary_and_alias() -> None:
    with pytest.raises(ConfigurationError):
        EndpointConfig.from_env(
            {
                "VLLM_BASE_URL": "http://one/v1",
                "CLINICAL_LLM_BASE_URL": "http://two/v1",
                "VLLM_API_KEY": "secret",
            }
        )


def test_public_config_never_contains_the_api_key() -> None:
    config = EndpointConfig.from_env(
        {
            "VLLM_BASE_URL": "http://user:password@localhost:8000/v1?token=secret",
            "VLLM_API_KEY": "top-secret",
            "VLLM_MODEL": "deepseek-v4-flash",
        }
    )
    rendered = json.dumps(config.public_dict())
    assert "top-secret" not in rendered
    assert "password" not in rendered
    assert "token=secret" not in rendered


def test_input_rejects_unknown_fields_before_any_model_call(tmp_path: Path) -> None:
    path = tmp_path / "notes.jsonl"
    path.write_text('{"id":"n1","text":"private","patient_name":"hidden"}\n')
    with pytest.raises(InputValidationError):
        read_notes(path)


def test_input_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "notes.jsonl"
    path.write_text(
        '{"id":"n1","text":"first"}\n{"id":"n1","text":"second"}\n'
    )
    with pytest.raises(InputValidationError):
        read_notes(path)


def test_seizure_frequency_uses_real_schema_and_keeps_exact_evidence() -> None:
    model = QueueModel(GAN_RESPONSE)
    result = ClinicalExtractor(model).seizure_frequency(
        note_id="synthetic-001", text="She currently has two seizures per month."
    )
    assert result["value"] == "2 per month"
    assert result["evidence_exact"] is True
    assert "events" in model.calls[0]["schema"]["properties"]  # type: ignore[index]


def test_all_preserves_frequency_when_findings_fails() -> None:
    model = QueueModel(GAN_RESPONSE, RuntimeError("private note: should not leak"))
    row = ClinicalExtractor(model).all(
        note_id="synthetic-001", text="She currently has two seizures per month."
    )
    assert row["status"] == "partial"
    assert row["workflows"]["seizure_frequency"]["status"] == "ok"
    error = row["workflows"]["clinical_findings"]["error"]
    assert "private note" not in json.dumps(error)


def test_clinical_findings_runs_one_model_call_and_groups_families() -> None:
    model = QueueModel(EXECT_RESPONSE)
    result = ClinicalExtractor(model).clinical_findings(
        note_id="synthetic-002", text="Assessment: focal epilepsy."
    )
    assert len(model.calls) == 1
    assert result["diagnoses"][0]["evidence"] == "focal epilepsy"
    assert result["seizure_frequencies"] == []


def test_parseable_schema_failure_gets_one_value_preserving_format_retry() -> None:
    event = json.loads(EXECT_RESPONSE)["clinical_events"][0]
    malformed = json.dumps({"clinical_events": {"event0": event}})
    model = QueueModel(malformed, EXECT_RESPONSE)
    result = ClinicalExtractor(model).clinical_findings(
        note_id="synthetic-003", text="Assessment: focal epilepsy."
    )
    assert len(model.calls) == 2
    assert result["diagnoses"][0]["value"] == "focal epilepsy"
    assert "Keep every clinical fact and value unchanged" in model.calls[1]["messages"][0][
        "content"
    ]


def test_vllm_client_places_thinking_and_schema_in_endpoint_adapter() -> None:
    config = EndpointConfig.from_env(
        {
            "VLLM_BASE_URL": "http://127.0.0.1:8000/v1",
            "VLLM_API_KEY": "EMPTY",
            "VLLM_MODEL": "deepseek-v4-flash",
            "VLLM_THINKING": "true",
        }
    )
    requests: list[dict[str, object]] = []

    def create(**kwargs: object) -> object:
        requests.append(kwargs)
        message = SimpleNamespace(content='{"ok":true}', model_extra={})
        choice = SimpleNamespace(message=message, finish_reason="stop")
        return SimpleNamespace(choices=[choice], model="deepseek-v4-flash", usage=None)

    client = object.__new__(VLLMClient)
    client.config = config
    completions = SimpleNamespace(create=create)
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    response = client.complete_json(
        messages=[{"role": "user", "content": "synthetic"}],
        schema={"type": "object"},
        settings=config.settings,
    )
    assert response.structured_output_mode == "json_schema"
    assert requests[0]["extra_body"] == {
        "chat_template_kwargs": {"enable_thinking": True}
    }
    assert requests[0]["response_format"]["json_schema"]["schema"] == {  # type: ignore[index]
        "type": "object"
    }
