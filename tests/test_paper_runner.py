"""Contract tests for the centralized paper runner."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.cli import run, verify
from clinical_extraction.paper.exect import (
    CANDIDATE_VERSION,
    HOSTED_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    control_path,
    verify_compact,
)
from clinical_extraction.paper.lm import gemini_api_base
from clinical_extraction.paper.methods import LIVE_METHODS, split_for
from clinical_extraction.paper.roster import living_models
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm as gan_llm_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
)

pytestmark = pytest.mark.local_corpus


def test_living_roster_is_the_six_paper_models() -> None:
    slugs = [item["slug"] for item in living_models()]
    assert slugs == [
        "gpt56sol",
        "gpt56luna",
        "gemini37flash",
        "deepseek_v4_flash",
        "qwen38_27b",
        "gemma4_26b",
    ]
    assert tuple(MODELS) == tuple(slugs)
    assert HOSTED_SLUGS == ("gpt56sol", "gpt56luna", "gemini37flash", "deepseek_v4_flash")
    assert LOCAL_SLUGS == ("qwen38_27b", "gemma4_26b")
    assert MODELS["gpt56sol"].model == "openai/gpt-5.6-sol"
    assert MODELS["qwen38_27b"].model == "ollama_chat/qwen3.8:27b"
    assert MODELS["qwen38_27b"].num_ctx == 32768
    assert MODELS["gemma4_26b"].num_ctx == 65536
    assert MODELS["gemini37flash"].credential_env == ("OPENROUTER_API_KEY",)
    assert gemini_api_base(None) == OPENROUTER_OPENAI_BASE


def test_live_methods_are_the_paper_llm_cells() -> None:
    assert set(LIVE_METHODS) == {
        "gan_llm_only",
        "gan_llm_with_rules",
        "exect_llm_with_rules",
    }
    split_for("exect_llm_with_rules", "dev140")
    split_for("gan_llm_with_rules", "test450")
    with pytest.raises(ValueError, match="does not use split"):
        split_for("exect_llm_with_rules", "test450")


def test_verify_compact_does_not_change_the_live_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_compact()
    assert payload["ok"] is True
    assert payload["method"] == "exect_llm_with_rules"
    assert payload["candidate"] == CANDIDATE_VERSION == structured.COMPACT_LEDGER
    assert payload["n_rules"] == 67
    assert payload["n_examples"] == 0
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["split"] == "dev140"
    assert payload["row_policy"] == "development_review_permitted"
    assert payload["hosted"] == list(HOSTED_SLUGS)
    assert payload["local"] == list(LOCAL_SLUGS)
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER


def test_verify_compact_test60_is_aggregate_only() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_compact(split="test60")
    assert payload["ok"] is True
    assert payload["split"] == "test60"
    assert payload["row_count"] == 59
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test60_authorized"] is True
    assert structured.PROMPT_VERSION == before == structured.COMPACT_LEDGER
    for slug in HOSTED_SLUGS:
        path = control_path(slug, "test60")
        assert "exect_test60" in path.as_posix()


def test_verify_cli_reports_paper_gan_identities() -> None:
    only = verify("gan_llm_only", "dev750", "gemma4_26b")
    hybrid = verify("gan_llm_with_rules", "dev750", "gpt56luna")
    assert only["prompt_version"] == gan_llm_only.GAN_LLM_ONLY
    assert hybrid["prompt_version"] == hybrid_structured_events.GAN_LLM_WITH_RULES
    assert only["model"] == "ollama_chat/gemma4:26b"
    with pytest.raises(SystemExit, match="not wired"):
        run("gan_llm_only", "gemma4_26b", "dev750")
