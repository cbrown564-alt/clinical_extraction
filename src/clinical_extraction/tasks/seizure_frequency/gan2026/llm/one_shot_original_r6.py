"""R6 uses the historical prompt/schema and parser, without a v2 translation."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as original,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DspyStructuredExtractor,
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)

VERSION = "one_shot_original_r6"
RUNTIME = {
    "model": "deepseek/deepseek-flash",
    "temperature": 0.0,
    "max_tokens": 24000,
    "thinking_type": "enabled",
    "reasoning_effort": "low",
    "cache": False,
}


def messages(record: GanFrequencyRecord) -> list[dict[str, object]]:
    return DspyStructuredExtractor().render_messages(
        prompt_input_json=original.build_llm_extract_encode_select_prompt_input(record)
    )


def parse(raw: str, record: GanFrequencyRecord) -> Any:
    return parse_structured_json_with_trace(
        raw, note_text=record.note_text, repair_config=StructuredRepairConfig.for_mode("raw_model")
    )[0]
