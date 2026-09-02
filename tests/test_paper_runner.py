"""Contract tests for the centralized paper runner."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from clinical_extraction.paper.cli import run
from clinical_extraction.paper.exect import (
    CANDIDATE_VERSION,
    GROK46_SLUG,
    HOSTED_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    apply_temperature,
    cell3_thinking_max_tokens,
    paper_work_suffix,
    run_compact,
    run_compact_reasoning_ablation,
    thinking_work_segment,
    verify_compact,
    verify_llm_only,
)
from clinical_extraction.paper.gan import _max_tokens_for, run_gan, verify_gan
from clinical_extraction.paper.lm import (
    AI_GATEWAY_OPENAI_BASE,
    GROK46_LITELLM_MODEL,
    GROK46_MODEL,
    SOL_MODEL,
    build_paper_lm,
    gemini_api_base,
    grok_api_base,
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
        "gemini37flash",
        "grok46",
        "gpt56luna",
        "deepseek_v4_flash",
        "qwen38_27b",
        "gemma4_26b",
    ]
    assert living_models()[0]["method_identity"] is True
    assert tuple(MODELS) == tuple(slugs)
    assert HOSTED_SLUGS == ("grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash")
    assert LOCAL_SLUGS == ("qwen38_27b", "gemma4_26b")
    assert "gpt56sol" not in MODELS
    assert MODELS["grok46"].model == GROK46_MODEL == "xai/grok-4.6"
    assert MODELS["grok46"].credential_env == ("AI_GATEWAY_API_KEY",)
    assert MODELS["grok46"].reasoning_effort == "low"
    assert MODELS["grok46"].timeout == 600
    assert MODELS["grok46"].temperature == 0.0
    assert MODELS["gpt56luna"].credential_env == ("OPENAI_API_KEY",)
    assert MODELS["gpt56luna"].reasoning_effort == "low"
    assert MODELS["gpt56luna"].model == "openai/gpt-5.6-luna"
    assert MODELS["qwen38_27b"].model == "ollama_chat/qwen3.8:27b"
    assert MODELS["qwen38_27b"].num_ctx == 32768
    assert MODELS["gemma4_26b"].num_ctx == 65536
    assert MODELS["gemini37flash"].credential_env == ("OPENROUTER_API_KEY",)
    assert MODELS["gemini37flash"].reasoning_effort == "low"
    assert gemini_api_base(None) == OPENROUTER_OPENAI_BASE
    assert sol_api_base(None) == AI_GATEWAY_OPENAI_BASE == "https://ai-gateway.vercel.sh/v1"
    assert resolve_paper_api_base("gpt56sol", None) == AI_GATEWAY_OPENAI_BASE
    assert resolve_paper_api_base("gpt56luna", None) is None
    assert grok_api_base(None) == AI_GATEWAY_OPENAI_BASE
    assert resolve_paper_api_base(GROK46_SLUG, None) == AI_GATEWAY_OPENAI_BASE
    assert MODELS["deepseek_v4_flash"].reasoning_effort == "low"
    assert MODELS["deepseek_v4_flash"].thinking_type == "enabled"
    assert thinking_work_segment(MODELS["deepseek_v4_flash"]) is None
    assert (
        thinking_work_segment(replace(MODELS["deepseek_v4_flash"], thinking_type="disabled"))
        == "thinking_disabled"
    )
    assert paper_work_suffix(MODELS["deepseek_v4_flash"]) is None
    assert (
        paper_work_suffix(replace(MODELS["deepseek_v4_flash"], reasoning_effort="high"))
        == "reasoning_high"
    )
    assert paper_work_suffix(MODELS["gpt56luna"]) is None
    assert (
        paper_work_suffix(replace(MODELS["gpt56luna"], reasoning_effort="medium"))
        == "reasoning_medium"
    )
    assert (
        paper_work_suffix(replace(MODELS["gpt56luna"], reasoning_effort="high"))
        == "reasoning_high"
    )
    assert paper_work_suffix(MODELS["qwen38_27b"]) is None
    assert (
        paper_work_suffix(replace(MODELS["qwen38_27b"], temperature=1.0))
        == "temperature_1"
    )
    assert (
        paper_work_suffix(
            replace(MODELS["gpt56luna"], reasoning_effort="high", temperature=0.0)
        )
        == "reasoning_high_temperature_0"
    )
    assert paper_work_suffix(MODELS["grok46"]) is None
    assert (
        paper_work_suffix(replace(MODELS["grok46"], temperature=1.0)) == "temperature_1"
    )
    assert apply_temperature(MODELS["grok46"], None) is MODELS["grok46"]
    assert apply_temperature(MODELS["grok46"], 1.0).temperature == 1.0
    with pytest.raises(RuntimeError, match="living paper setting"):
        apply_temperature(MODELS["grok46"], 0.0)


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
        "gan_llm_extract_raw",
        "gan_llm_encode",
        "gan_llm_select",
        "gan_llm_select_from_extract",
        "gan_llm_extract",
        "gan_llm_extract_no_examples",
        "gan_llm_extract_holgate_like",
        "gan_llm_extract_holgate_label",
        "gan_llm_extract_no_evidence",
        "gan_llm_extract_examples_only",
        "gan_llm_extract_encode_select",
        "gan_llm_and_rules_extract",
        "exect_llm_pre_post",
        "exect_llm_with_rules",
        "exect_llm_extract",
        "exect_llm_extract_and_select",
        "exect_llm_extract_filtered",
        "exect_llm_only",
        "exect_llm_inventory",
        "exect_llm_encode",
        "exect_llm_select",
    }
    split_for("exect_llm_pre_post", "dev140")
    split_for("exect_llm_with_rules", "dev140")
    split_for("exect_llm_only", "dev140")
    split_for("exect_llm_extract", "dev140")
    split_for("exect_llm_extract_filtered", "dev140")
    split_for("gan_llm_extract_raw", "test450")
    with pytest.raises(ValueError, match="does not use split"):
        split_for("exect_llm_with_rules", "test450")


def test_verify_compact_does_not_change_the_live_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_compact()
    assert payload["ok"] is True
    assert payload["method"] == "exect_llm_pre_post"
    assert payload["candidate"] == CANDIDATE_VERSION == structured.EXECT_LLM_PRE_POST
    assert payload["n_rules"] == 50
    assert payload["n_examples"] == 5
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["split"] == "dev140"
    assert payload["row_policy"] == "development_review_permitted"
    assert payload["hosted"] == list(HOSTED_SLUGS)
    assert payload["local"] == list(LOCAL_SLUGS)
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_verify_llm_only_does_not_change_the_live_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_llm_only(split="dev140", slug=GROK46_SLUG)
    assert payload["ok"] is True
    assert payload["method"] == "exect_llm_extract_and_select"
    assert payload["prompt_version"] == structured.EXECT_LLM_EXTRACT_AND_SELECT
    assert payload["n_rules"] == 52
    assert payload["n_examples"] == 0
    assert payload["authored_order"] is True
    assert payload["drops_research_metadata"] is True
    assert payload["work_root"] == "experiments/paper/exect_llm_extract_filtered"
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_verify_compact_test60_is_aggregate_only() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_compact(split="test60")
    assert payload["ok"] is True
    assert payload["split"] == "test60"
    assert payload["row_count"] == 59
    assert payload["row_policy"] == "aggregate_only"
    assert payload["test60_authorized"] is True
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_verify_gan_pins_paper_identities_without_changing_defaults() -> None:
    before_only = gan_llm_only.PROMPT_VERSION
    before_hybrid = hybrid_structured_events.PROMPT_VERSION
    only = verify_gan("gan_llm_only", "dev750", "gemma4_26b")
    hybrid = verify_gan("gan_llm_extract_raw", "dev750", "grok46")
    assert only["ok"] is True
    assert only["method"] == "gan_llm_only"
    assert only["prompt_version"] == gan_llm_only.GAN_LLM_ONLY
    assert only["split"] == "dev750"
    assert only["split_machine"] == "validation" == gan_machine_split("dev750")
    assert only["row_count"] == 750
    assert only["row_policy"] == "development_review_permitted"
    assert only["model"] == "ollama_chat/gemma4:26b"
    assert only["max_tokens"] == 1200
    deepseek_only = verify_gan("gan_llm_only", "dev750", "deepseek_v4_flash")
    assert deepseek_only["max_tokens"] == 24000
    assert _max_tokens_for("gan_llm_only", "gpt56luna") == 1200
    assert _max_tokens_for("gan_llm_only", "gpt56luna", "low") == 1200
    assert _max_tokens_for("gan_llm_only", "gpt56luna", "medium") == 1200
    assert _max_tokens_for("gan_llm_only", "gpt56luna", "high") == 16000
    assert _max_tokens_for("gan_llm_extract", "gemini37flash") == 5000
    assert _max_tokens_for("gan_llm_extract", "gemini37flash", "low") == 5000
    assert _max_tokens_for("gan_llm_extract", "gemini37flash", "medium") == 10000
    assert _max_tokens_for("gan_llm_extract", "gemini37flash", "high") == 10000
    assert cell3_thinking_max_tokens(16000, None) == 16000
    assert cell3_thinking_max_tokens(16000, "low") == 16000
    assert cell3_thinking_max_tokens(16000, "medium") == 32000
    assert cell3_thinking_max_tokens(16000, "high") == 32000
    assert hybrid["ok"] is True
    assert hybrid["model"] == "xai/grok-4.6"
    assert hybrid["method"] == "gan_llm_extract_raw"
    assert hybrid["prompt_version"] == hybrid_structured_events.GAN_LLM_EXTRACT_RAW
    assert only["authored_keys"] == list(gan_llm_only.LLM_ONLY_AUTHORED_KEYS)
    assert hybrid["authored_keys"] == list(hybrid_structured_events.LLM_WITH_RULES_AUTHORED_KEYS)
    assert hybrid["max_tokens"] == 5000
    assert gan_llm_only.PROMPT_VERSION == before_only == gan_llm_only.GAN_LLM_ONLY
    assert (
        hybrid_structured_events.PROMPT_VERSION
        == before_hybrid
        == hybrid_structured_events.GAN_LLM_EXTRACT_RAW
    )


def test_verify_gan_test450_is_aggregate_only() -> None:
    payload = verify_gan("gan_llm_extract_raw", "test450")
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
        thinking: str | None = None,
        reasoning_effort: str | None = None,
        row_limit: int | None = None,
        slice_name: str | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        captured.update(
            method=method,
            slug=slug,
            live=live,
            split=split,
            reasoning_effort=reasoning_effort,
        )
        return {"ok": True, "method": method}

    monkeypatch.setattr("clinical_extraction.paper.cli.run_gan", fake_run)
    payload = run("gan_llm_only", "qwen38_27b", "dev750")
    assert payload == {"ok": True, "method": "gan_llm_only"}
    assert captured == {
        "method": "gan_llm_only",
        "slug": "qwen38_27b",
        "live": True,
        "split": "dev750",
        "reasoning_effort": None,
    }
    with pytest.raises(RuntimeError, match="requires live=True"):
        run_gan("gan_llm_extract_raw", "gpt56luna", live=False, split="dev750")


def test_grok46_paper_lm_uses_vercel_ai_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.llm_config.dspy.LM",
        fake_lm,
    )
    monkeypatch.setenv("AI_GATEWAY_API_KEY", "gateway-test-key")

    build_paper_lm(
        GROK46_MODEL,
        temperature=1.0,
        max_tokens=16000,
        cache=False,
        reasoning_effort="low",
    )

    assert captured["model"] == GROK46_LITELLM_MODEL == "openai/xai/grok-4.6"
    assert captured.get("model_type") != "responses"
    assert captured["api_base"] == AI_GATEWAY_OPENAI_BASE
    assert captured["api_key"] == "gateway-test-key"
    assert captured["temperature"] == 1.0
    assert captured["max_tokens"] == 16000
    assert captured["cache"] is False
    assert "reasoning_effort" not in captured
    assert captured["extra_body"] == {"reasoning": {"effort": "low"}}


def test_grok46_is_living_compact() -> None:
    before = structured.PROMPT_VERSION
    assert GROK46_SLUG in MODELS
    payload = verify_compact(split="dev140", slug=GROK46_SLUG)
    assert payload["ok"] is True
    holdout = verify_compact(split="test60", slug=GROK46_SLUG)
    assert holdout["ok"] is True
    assert holdout["row_policy"] == "aggregate_only"
    with pytest.raises(RuntimeError, match="requires live=True"):
        run_compact(GROK46_SLUG, live=False, split="dev140")
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_cli_dispatches_grok46_compact(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_compact(
        slug: str,
        *,
        live: bool,
        split: str,
        overwrite: bool = False,
        api_base: str | None = None,
        timeout: int | None = None,
        progress_every: int = 1,
        thinking: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict[str, object]:
        captured.update(slug=slug, live=live, split=split, reasoning_effort=reasoning_effort)
        return {"ok": True, "method": "exect_llm_with_rules"}

    monkeypatch.setattr("clinical_extraction.paper.cli.run_compact", fake_compact)
    monkeypatch.setattr(
        "clinical_extraction.paper.cli.run_llm_extract_filtered",
        lambda *args, **kwargs: {"ok": True, "method": "exect_llm_extract_filtered"},
    )
    payload = run("exect_llm_with_rules", GROK46_SLUG, "dev140")
    assert payload == {"ok": True, "method": "exect_llm_with_rules"}
    assert run("exect_llm_only", GROK46_SLUG, "dev140") == {
        "ok": True,
        "method": "exect_llm_extract_filtered",
    }
    assert captured == {
        "slug": GROK46_SLUG,
        "live": True,
        "split": "dev140",
        "reasoning_effort": None,
    }


def test_gemini_reasoning_ablation_is_dev140_medium_only() -> None:
    before = structured.PROMPT_VERSION
    with pytest.raises(RuntimeError, match="development-only"):
        run_compact_reasoning_ablation(
            "gemini37flash",
            effort="medium",
            live=True,
            split="test60",
        )
    with pytest.raises(RuntimeError, match="living paper setting"):
        run_compact_reasoning_ablation(
            "gemini37flash",
            effort="low",
            live=True,
            split="dev140",
        )
    with pytest.raises(RuntimeError, match="requires live=True"):
        run_compact_reasoning_ablation(
            "gemini37flash",
            effort="medium",
            live=False,
            split="dev140",
        )
    assert MODELS["gemini37flash"].reasoning_effort == "low"
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_cli_dispatches_non_living_effort_to_live_runners(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compact: dict[str, object] = {}
    gan: dict[str, object] = {}

    def fake_compact(
        slug: str,
        *,
        live: bool,
        split: str,
        overwrite: bool = False,
        api_base: str | None = None,
        timeout: int | None = None,
        progress_every: int = 1,
        thinking: str | None = None,
        reasoning_effort: str | None = None,
    ) -> dict[str, object]:
        compact.update(slug=slug, split=split, reasoning_effort=reasoning_effort)
        return {"ok": True, "method": "exect_llm_with_rules"}

    def fake_gan(
        method: str,
        slug: str,
        *,
        live: bool,
        split: str,
        overwrite: bool = False,
        api_base: str | None = None,
        timeout: int | None = None,
        progress_every: int = 1,
        thinking: str | None = None,
        reasoning_effort: str | None = None,
        row_limit: int | None = None,
        slice_name: str | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        gan.update(
            method=method,
            slug=slug,
            split=split,
            reasoning_effort=reasoning_effort,
        )
        return {"ok": True, "method": method}

    monkeypatch.setattr("clinical_extraction.paper.cli.run_compact", fake_compact)
    monkeypatch.setattr("clinical_extraction.paper.cli.run_gan", fake_gan)
    assert run(
        "exect_llm_with_rules",
        "gpt56luna",
        "test60",
        reasoning_effort="high",
    ) == {"ok": True, "method": "exect_llm_with_rules"}
    assert compact == {
        "slug": "gpt56luna",
        "split": "test60",
        "reasoning_effort": "high",
    }
    assert run(
        "gan_llm_extract_raw",
        "gpt56luna",
        "dev750",
        reasoning_effort="medium",
    ) == {"ok": True, "method": "gan_llm_extract_raw"}
    assert gan == {
        "method": "gan_llm_extract_raw",
        "slug": "gpt56luna",
        "split": "dev750",
        "reasoning_effort": "medium",
    }
    with pytest.raises(RuntimeError, match="living paper setting"):
        run_gan("gan_llm_only", "gpt56luna", live=True, split="dev750", reasoning_effort="low")
    with pytest.raises(RuntimeError, match="living paper setting"):
        run_compact("gpt56luna", live=True, split="dev140", reasoning_effort="low")


def test_luna_paper_lm_sends_explicit_low_reasoning_effort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.llm_config.dspy.LM",
        fake_lm,
    )

    build_paper_lm(
        "openai/gpt-5.6-luna",
        temperature=1.0,
        max_tokens=16000,
        cache=False,
        reasoning_effort="low",
    )

    assert captured["model"] == "openai/gpt-5.6-luna"
    assert captured["reasoning_effort"] == "low"
    assert "extra_body" not in captured
    assert captured["temperature"] == 1.0
    assert captured.get("model_type") != "responses"


def test_luna_living_low_is_not_an_ablation() -> None:
    before = structured.PROMPT_VERSION
    with pytest.raises(RuntimeError, match="living paper setting"):
        run_compact_reasoning_ablation(
            "gpt56luna",
            effort="low",
            live=True,
            split="dev140",
        )
    with pytest.raises(RuntimeError, match="not an allowed"):
        run_compact_reasoning_ablation(
            "gpt56luna",
            effort="medium",
            live=True,
            split="dev140",
        )
    assert MODELS["gpt56luna"].reasoning_effort == "low"
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST
