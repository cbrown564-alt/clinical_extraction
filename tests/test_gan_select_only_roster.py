"""Select-only roster: encode off, living Gemini cell-4 gate."""

from __future__ import annotations

from clinical_extraction.paper.gan_select_only_roster import (
    CITED_GEMINI_CELL4_TEST450,
    REPAIR_MODE,
    measure_select_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
)


def test_llm_select_only_keeps_encode_off() -> None:
    config = StructuredRepairConfig.for_mode(REPAIR_MODE)
    assert not config.encode_enabled()
    assert config.codebook_label_repair is False
    assert config.last_event_well_since_repair is True


def test_gemini_select_only_matches_living_cell4() -> None:
    payload = measure_select_only("gemini37flash", "test450")
    assert payload["select_only"]["purist_correct"] == CITED_GEMINI_CELL4_TEST450
    assert payload["companions"]["hybrid_purist"] == 387
    assert "source_row_index" not in str(payload)
