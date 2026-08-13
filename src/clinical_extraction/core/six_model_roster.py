"""Six-model comparison rosters.

``SIX_MODELS`` in ``shared_reliability_schema`` remains the completed
Decision 0039 set that produced the selected current-stack fills.

``SUCCESSOR_SIX_MODELS`` is the Decision 0051 lineup for new six-model
calls. It is not a score and does not replace historical artifacts.
"""

from __future__ import annotations

from typing import TypedDict


class SixModelCondition(TypedDict):
    slug: str
    model: str
    label: str
    availability_class: str
    execution_group: str


# Completed Decision 0039 roster. Keep this list aligned with SIX_MODELS.
HISTORICAL_SIX_MODELS: tuple[str, ...] = (
    "openai/gpt-4.1-mini",
    "openai/gpt-5.6-luna",
    "openai/gpt-5.6-sol",
    "deepseek/deepseek-v4-flash",
    "ollama_chat/qwen3.6:35b",
    "ollama_chat/gemma4:26b",
)

SUCCESSOR_SIX_MODELS: tuple[SixModelCondition, ...] = (
    {
        "slug": "gpt56luna",
        "model": "openai/gpt-5.6-luna",
        "label": "GPT-5.6 Luna",
        "availability_class": "closed_weight",
        "execution_group": "hosted_openai",
    },
    {
        "slug": "gemini37flash",
        "model": "gemini/gemini-3.7-flash",
        "label": "Gemini 3.7 Flash",
        "availability_class": "closed_weight",
        "execution_group": "hosted_gemini",
    },
    {
        "slug": "gpt56sol",
        "model": "openai/gpt-5.6-sol",
        "label": "GPT-5.6 Sol",
        "availability_class": "closed_weight",
        "execution_group": "hosted_openai",
    },
    {
        "slug": "deepseek_v4_flash",
        "model": "deepseek/deepseek-v4-flash",
        "label": "DeepSeek V4 Flash",
        "availability_class": "open_weight",
        "execution_group": "hosted_deepseek",
    },
    {
        "slug": "qwen36_35b",
        "model": "ollama_chat/qwen3.6:35b",
        "label": "Qwen 3.6:35B",
        "availability_class": "open_weight",
        "execution_group": "local",
    },
    {
        "slug": "gemma4_26b",
        "model": "ollama_chat/gemma4:26b",
        "label": "Gemma 4 26B",
        "availability_class": "open_weight",
        "execution_group": "local",
    },
)

SUCCESSOR_SIX_MODEL_IDS: tuple[str, ...] = tuple(
    condition["model"] for condition in SUCCESSOR_SIX_MODELS
)
GEMINI_37_FLASH_MODEL = "gemini/gemini-3.7-flash"
RESERVED_FUTURE_OPEN_WEIGHT = "qwen3.8-27b"
