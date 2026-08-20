from __future__ import annotations

from clinical_extraction.core.shared_reliability_schema import SIX_MODELS
from clinical_extraction.core.six_model_roster import (
    GEMINI_37_FLASH_MODEL,
    HISTORICAL_SIX_MODELS,
    SUCCESSOR_SIX_MODEL_IDS,
)


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
