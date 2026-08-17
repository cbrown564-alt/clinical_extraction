"""Contract tests for the centralized paper runner."""

from __future__ import annotations

from typing import Any

import pytest

from clinical_extraction.paper.cli import run
from clinical_extraction.paper.exect import (
    CANDIDATE_VERSION,
    HOSTED_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    control_path,
    verify_compact,
)
from clinical_extraction.paper.gan import run_gan, verify_gan
from clinical_extraction.paper.lm import (
    AI_GATEWAY_OPENAI_BASE,
    SOL_MODEL,
    build_paper_lm,
    gemini_api_base,
    resolve_paper_api_base,
    sol_api_base,
)
from clinical_extraction.paper.methods import LIVE_METHODS, gan_machine_split, split_for
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
    assert MODELS["gpt56sol"].model == SOL_MODEL
    assert MODELS["gpt56sol"].credential_env == ("AI_GATEWAY_API_KEY",)
    assert MODELS["gpt56luna"].credential_env == ("OPENAI_API_KEY",)
    assert MODELS["qwen38_27b"].model == "ollama_chat/qwen3.8:27b"
    assert MODELS["qwen38_27b"].num_ctx == 32768
    assert MODELS["gemma4_26b"].num_ctx == 65536
    assert MODELS["gemini37flash"].credential_env == ("OPENROUTER_API_KEY",)
    assert gemini_api_base(None) == OPENROUTER_OPENAI_BASE
    assert sol_api_base(None) == AI_GATEWAY_OPENAI_BASE == "https://ai-gateway.vercel.sh/v1"
    assert resolve_paper_api_base("gpt56sol", None) == AI_GATEWAY_OPENAI_BASE
    assert resolve_paper_api_base("gpt56luna", None) is None


def test_sol_paper_lm_uses_vercel_ai_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("clinical_extraction.paper.lm.dspy.LM", fake_lm)
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "gateway-test-key")

    build_paper_lm(SOL_MODEL, temperature=1.0, max_tokens=5000, cache=False)

    assert captured["model"] == SOL_MODEL
    assert captured["model_type"] == "responses"
    assert captured["api_base"] == AI_GATEWAY_OPENAI_BASE
    assert captured["api_key"] == "gateway-test-key"
    assert captured["temperature"] == 1.0
    assert captured["max_tokens"] == 5000
    assert captured["cache"] is False


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


def test_verify_gan_pins_paper_identities_without_changing_defaults() -> None:
    before_only = gan_llm_only.PROMPT_VERSION
    before_hybrid = hybrid_structured_events.PROMPT_VERSION
    only = verify_gan("gan_llm_only", "dev750", "gemma4_26b")
    hybrid = verify_gan("gan_llm_with_rules", "dev750", "gpt56luna")
    assert only["ok"] is True
    assert only["method"] == "gan_llm_only"
    assert only["prompt_version"] == gan_llm_only.GAN_LLM_ONLY
    assert only["split"] == "dev750"
    assert only["split_machine"] == "validation" == gan_machine_split("dev750")
    assert only["row_count"] == 750
    assert only["row_policy"] == "development_review_permitted"
    assert only["model"] == "ollama_chat/gemma4:26b"
    assert only["max_tokens"] == 1200
    assert hybrid["ok"] is True
    assert hybrid["method"] == "gan_llm_with_rules"
    assert hybrid["prompt_version"] == hybrid_structured_events.GAN_LLM_WITH_RULES
    assert hybrid["drops_research_metadata"] is True
    assert hybrid["max_tokens"] == 5000
    assert gan_llm_only.PROMPT_VERSION == before_only == gan_llm_only.GAN_LLM_ONLY
    assert (
        hybrid_structured_events.PROMPT_VERSION
        == before_hybrid
        == hybrid_structured_events.GAN_LLM_WITH_RULES
    )


def test_verify_gan_test450_is_aggregate_only() -> None:
    payload = verify_gan("gan_llm_with_rules", "test450")
    assert payload["ok"] is True
    assert payload["split"] == "test450"
    assert payload["split_machine"] == "test"
    assert payload["row_count"] == 450
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test450_authorized"] is True
    assert "incorrect_source_row_indices" not in payload


def test_cli_dispatches_gan_live(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(
        method: str,
        slug: str,
        *,
        live: bool,
        split: str,
        overwrite: bool = False,
        api_base: str | None = None,
        timeout: int | None = None,
        progress_every: int = 1,
    ) -> dict[str, object]:
        captured.update(method=method, slug=slug, live=live, split=split)
        return {"ok": True, "method": method}

    monkeypatch.setattr("clinical_extraction.paper.cli.run_gan", fake_run)
    payload = run("gan_llm_only", "qwen38_27b", "dev750")
    assert payload == {"ok": True, "method": "gan_llm_only"}
    assert captured == {
        "method": "gan_llm_only",
        "slug": "qwen38_27b",
        "live": True,
        "split": "dev750",
    }
    with pytest.raises(RuntimeError, match="requires live=True"):
        run_gan("gan_llm_with_rules", "gpt56luna", live=False, split="dev750")
