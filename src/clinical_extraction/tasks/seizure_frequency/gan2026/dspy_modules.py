from __future__ import annotations

"""DSPy module placeholders for the initial seizure-frequency pipeline."""


class SeizureEventExtractor:
    """Extract all seizure-frequency events from a clinical note."""

    def __call__(self, note_text: str) -> list[dict[str, str]]:
        raise NotImplementedError


class ClinicalReasoner:
    """Select or aggregate extracted events into one benchmark-facing answer."""

    def __call__(self, note_text: str, events: list[dict[str, str]]) -> dict[str, str]:
        raise NotImplementedError

