from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.core.shared_reliability_schema import SIX_MODELS
from clinical_extraction.core.six_model_roster import (
    GEMINI_37_FLASH_MODEL,
    HISTORICAL_SIX_MODELS,
    SUCCESSOR_SIX_MODEL_IDS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap

ROOT = Path(__file__).resolve().parents[1]
EXECT_CONFIG = ROOT / "configs/exectv2/six_model_comparison/gemini37flash_dev140.json"
GAN_CONFIG = ROOT / "configs/gan2026/six_model_successor_gemini37flash_20260813.json"


def test_historical_roster_stays_the_completed_six() -> None:
    assert HISTORICAL_SIX_MODELS == tuple(SIX_MODELS)
    assert "openai/gpt-4.1-mini" in SIX_MODELS
    assert GEMINI_37_FLASH_MODEL not in SIX_MODELS


def test_successor_roster_replaces_mini_with_gemini() -> None:
    assert GEMINI_37_FLASH_MODEL in SUCCESSOR_SIX_MODEL_IDS
    assert "openai/gpt-4.1-mini" not in SUCCESSOR_SIX_MODEL_IDS
    assert len(SUCCESSOR_SIX_MODEL_IDS) == 6
    assert SUCCESSOR_SIX_MODEL_IDS[0] == "openai/gpt-5.6-luna"
    assert SUCCESSOR_SIX_MODEL_IDS[1] == GEMINI_37_FLASH_MODEL
    assert SUCCESSOR_SIX_MODEL_IDS[2] == "openai/gpt-5.6-sol"


def test_exect_gemini_config_is_decision_0040_ready() -> None:
    config = model_swap.load_model_swap_config(EXECT_CONFIG)
    assert config.model == GEMINI_37_FLASH_MODEL
    assert config.model_label == "Gemini 3.7 Flash"
    assert model_swap.validate_model_led_architecture(config)["status"] == "pass"


def test_gan_successor_config_names_the_same_six_models() -> None:
    payload = json.loads(GAN_CONFIG.read_text(encoding="utf-8"))
    models = tuple(condition["model"] for condition in payload["conditions"])
    assert models == SUCCESSOR_SIX_MODEL_IDS
    gemini = next(
        condition
        for condition in payload["conditions"]
        if condition["slug"] == "gemini37flash"
    )
    assert gemini["status"] == "pending_live"
    assert gemini["execution_group"] == "hosted_gemini"
