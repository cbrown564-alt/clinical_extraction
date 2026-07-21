from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction_local import ClinicalExtractor, ModelResponse
from clinical_extraction_local.batch import run_batch
from clinical_extraction_local.config import EndpointConfig
from clinical_extraction_local.input import InputNote

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


class InterruptingModel:
    def __init__(self, responses: list[str | BaseException]) -> None:
        self.responses = responses
        self.config = type("Config", (), {"model": "deepseek-v4-flash"})()

    def complete_json(self, **_: object) -> ModelResponse:
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return ModelResponse(content=value, requested_model="deepseek-v4-flash")


def _config() -> EndpointConfig:
    return EndpointConfig.from_env(
        {
            "VLLM_BASE_URL": "http://127.0.0.1:8000/v1",
            "VLLM_API_KEY": "EMPTY",
            "VLLM_MODEL": "deepseek-v4-flash",
        }
    )


def test_interrupted_run_resumes_without_repeating_success(tmp_path: Path) -> None:
    notes = [
        InputNote("one", "Currently two seizures per month."),
        InputNote("two", "Currently two seizures per month."),
    ]
    output = tmp_path / "results.jsonl"
    first_model = InterruptingModel([GAN_RESPONSE, KeyboardInterrupt()])
    try:
        run_batch(
            extractor=ClinicalExtractor(first_model),
            config=_config(),
            notes=notes,
            workflows=("seizure_frequency",),
            output=output,
        )
    except KeyboardInterrupt:
        pass
    partial = tmp_path / ".results.jsonl.partial.jsonl"
    assert len(partial.read_text(encoding="utf-8").splitlines()) == 1

    second_model = InterruptingModel([GAN_RESPONSE])
    summary = run_batch(
        extractor=ClinicalExtractor(second_model),
        config=_config(),
        notes=notes,
        workflows=("seizure_frequency",),
        output=output,
        resume=True,
    )
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert [row["id"] for row in rows] == ["one", "two"]
    assert len(second_model.responses) == 0
    assert summary["ok"] == 2
    assert not partial.exists()


def test_default_output_excludes_raw_note_and_model_response(tmp_path: Path) -> None:
    private_text = "PRIVATE MARKER: two seizures per month."
    output = tmp_path / "results.jsonl"
    run_batch(
        extractor=ClinicalExtractor(InterruptingModel([GAN_RESPONSE])),
        config=_config(),
        notes=[InputNote("one", private_text)],
        workflows=("seizure_frequency",),
        output=output,
    )
    rendered = output.read_text(encoding="utf-8")
    assert "PRIVATE MARKER" not in rendered
    assert '"raw_model_response"' not in rendered
