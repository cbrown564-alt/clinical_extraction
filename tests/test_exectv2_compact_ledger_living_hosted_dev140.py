"""Contract tests for the living Compact hosted remasure runner."""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
)
from scripts.run_exectv2_compact_ledger_living_hosted_dev140 import (
    CANDIDATE_VERSION,
    HOSTED_SLUGS,
    MODELS,
    PROTOCOL,
    ROOT,
    STUDY_DIR,
    TEST60_PROTOCOL,
    TEST60_SCRATCH_DIR,
    TEST60_STUDY_DIR,
    gemini_api_base,
    verify_study,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    CANDIDATE_VERSION as DUMP_CANDIDATE_VERSION,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    STUDY_DIR as DUMP_STUDY_DIR,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    TEST60_CONTROLS,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    TEST60_STUDY_DIR as DUMP_TEST60_STUDY_DIR,
)

pytestmark = pytest.mark.local_corpus


def test_living_compact_is_the_candidate_and_stays_off_the_dump_study() -> None:
    assert CANDIDATE_VERSION == structured.COMPACT_LEDGER
    assert DUMP_CANDIDATE_VERSION == (
        structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
    )
    assert STUDY_DIR != DUMP_STUDY_DIR
    assert STUDY_DIR.name == "exectv2_compact_ledger_living_hosted_dev140_20260817"
    assert PROTOCOL.endswith("compact_ledger_living_hosted_dev140_protocol_2026-08-17.md")


def test_hosted_roster_is_sol_gemini_and_deepseek() -> None:
    assert HOSTED_SLUGS == ("gpt56sol", "gemini37flash", "deepseek_v4_flash")
    assert tuple(MODELS) == HOSTED_SLUGS
    assert MODELS["gpt56sol"].model == "openai/gpt-5.6-sol"
    assert MODELS["gemini37flash"].model == "gemini/gemini-3.7-flash"
    assert MODELS["deepseek_v4_flash"].model == "deepseek/deepseek-v4-flash"
    assert MODELS["deepseek_v4_flash"].provider_revision == "DeepSeek-V4-Flash-0731"
    for spec in MODELS.values():
        assert spec.candidate_structured is None
        assert spec.control_structured.is_file()
        assert "test60" not in spec.control_structured.as_posix()


def test_gemini_is_wired_to_openrouter() -> None:
    gemini = MODELS["gemini37flash"]
    assert gemini.credential_env == ("OPENROUTER_API_KEY",)
    assert gemini.reasoning_effort == "low"
    assert gemini_api_base(None) == OPENROUTER_OPENAI_BASE
    assert "openrouter.ai" in gemini_api_base(None)


def test_verify_study_uses_authored_compact_and_does_not_change_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study()
    assert payload["ok"] is True
    assert payload["candidate"] == structured.COMPACT_LEDGER
    assert payload["n_rules"] == 67
    assert payload["n_examples"] == 0
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["split"] == "dev140"
    assert payload["test60_authorized"] is False
    assert payload["protocol"] == PROTOCOL
    assert payload["study_dir"] == STUDY_DIR.relative_to(ROOT).as_posix()
    assert payload["hosted"] == list(HOSTED_SLUGS)
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER


def test_test60_verify_is_aggregate_only_living_compact() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_study(split="test60")
    assert payload["ok"] is True
    assert payload["candidate"] == structured.COMPACT_LEDGER
    assert payload["split"] == "test60"
    assert payload["row_count"] == 59
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test60_authorized"] is True
    assert payload["protocol"] == TEST60_PROTOCOL
    assert payload["study_dir"] == TEST60_STUDY_DIR.relative_to(ROOT).as_posix()
    assert payload["scratch_dir"] == TEST60_SCRATCH_DIR.relative_to(ROOT).as_posix()
    assert TEST60_STUDY_DIR != DUMP_TEST60_STUDY_DIR
    assert payload["hosted"] == list(HOSTED_SLUGS)
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["default_prompt_version"] == structured.COMPACT_LEDGER
    for slug in HOSTED_SLUGS:
        assert TEST60_CONTROLS[slug].is_file()
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER
