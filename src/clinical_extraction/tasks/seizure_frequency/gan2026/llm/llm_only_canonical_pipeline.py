"""Legacy import compatibility for the active Gan ``llm`` pipeline."""

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm as _active

globals().update(
    {
        name: value
        for name, value in vars(_active).items()
        if name not in {"__name__", "__package__", "__loader__", "__spec__"}
    }
)
