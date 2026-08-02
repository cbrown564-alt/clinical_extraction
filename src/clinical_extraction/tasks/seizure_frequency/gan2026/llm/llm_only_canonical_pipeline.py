"""Legacy module identity for the active Gan ``llm`` pipeline."""

import sys

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm as _active

sys.modules[__name__] = _active
