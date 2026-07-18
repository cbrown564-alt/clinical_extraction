from __future__ import annotations

import json
from types import SimpleNamespace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured,
)

runner = key_entities_structured.runner


def test_local_schema_failure_gets_one_value_preserving_format_retry(monkeypatch) -> None:
    event = {
        "family": "diagnosis",
        "anchor_text": "epilepsy",
        "evidence": "Diagnosis: epilepsy",
        "event_state": {},
        "mentions": [
            {
                "entity": "Diagnosis",
                "text": "epilepsy",
                "attributes": {"Negation": "Affirmed"},
            }
        ],
        "confidence": "high",
        "rationale": "",
    }
    malformed_shape = json.dumps({"clinical_events": event})
    repaired_shape = json.dumps({"clinical_events": [event]})

    class Extractor:
        def __call__(self, **_kwargs):
            return SimpleNamespace(extraction_json=malformed_shape)

    class Retry:
        def __call__(self, **_kwargs):
            return SimpleNamespace(repaired_json=repaired_shape)

    monkeypatch.setattr(runner, "DspyKeyEntitiesStructuredExtractor", Extractor)
    monkeypatch.setattr(runner, "FormatOnlyJsonRetry", Retry)
    monkeypatch.setattr(runner.dspy, "configure", lambda **_kwargs: None)
    monkeypatch.setattr(runner, "build_dspy_lm", lambda *_args, **_kwargs: object())

    rows, metadata = runner.run_split(
        [ExectLetter(letter_id="TEST001", note_text="Diagnosis: epilepsy")],
        split="dev",
        model="ollama_chat/gemma4:26b",
        temperature=0,
        max_tokens=100,
        mode="live",
        dspy_cache=False,
    )

    assert rows[0]["raw_output"] == malformed_shape
    assert rows[0]["format_retry_output"] == repaired_shape
    assert rows[0]["initial_parse_errors"][0].startswith("schema_validation_error:")
    assert rows[0]["parse_errors"] == ["format_retry_applied"]
    assert rows[0]["structured_output_failure_codes"] == ["schema_validation_error"]
    assert metadata["summary"]["initial_parse_failures"] == 1
    assert metadata["summary"]["parse_failures"] == 0
    assert metadata["summary"]["format_retries_applied"] == 1
