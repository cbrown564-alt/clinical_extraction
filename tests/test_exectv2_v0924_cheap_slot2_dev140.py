"""Contract tests for the slot-2 cheap-stack three-model dev140 runner."""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_v0924_cheap_slot2_dev140 import (
    CANDIDATE_VERSION,
    MODELS,
    model_spec,
    require_credentials,
    verify_payload,
)

pytestmark = pytest.mark.local_corpus


def test_slot2_payload_check_does_not_change_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["n_rules"] == 54
    assert payload["n_examples"] == 0
    assert payload["drops_research_metadata"] is True
    assert payload["prompt_version"] == CANDIDATE_VERSION
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER


def test_three_model_specs_use_saved_same_model_controls() -> None:
    assert set(MODELS) == {"luna", "gemini", "qwen"}
    luna = model_spec("luna")
    gemini = model_spec("gemini")
    qwen = model_spec("qwen")
    assert luna["model"] == "openai/gpt-5.6-luna"
    assert luna["temperature"] == 1.0
    assert luna["api_key_env"] == "OPENAI_API_KEY"
    assert gemini["model"] == "gemini/gemini-3.7-flash"
    assert gemini["temperature"] == 0.0
    assert gemini["api_key_env"] == "OPENROUTER_API_KEY"
    assert "openrouter.ai" in str(gemini["api_base"])
    assert qwen["model"] == "ollama_chat/qwen3.8:27b"
    assert qwen["temperature"] == 0.0
    assert qwen["api_key_env"] is None
    assert qwen["require_full_control"] is False
    assert luna["require_full_control"] is True
    assert gemini["require_full_control"] is True
    assert luna["control_structured"].is_file()
    assert gemini["control_structured"].is_file()
    for spec in (luna, gemini, qwen):
        assert spec["study_dir"].name.endswith("_dev140_20260817")


def test_qwen_does_not_require_hosted_credentials() -> None:
    require_credentials(model_spec("qwen"))
