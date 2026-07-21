"""Readable local clinical-extraction handoff API with lazy clinical imports."""

import logging
import os
from typing import Any

from .models import GenerationSettings, ModelClient, ModelResponse

__all__ = [
    "ClinicalExtractor",
    "GenerationSettings",
    "ModelClient",
    "ModelResponse",
    "VLLMClient",
]


def __getattr__(name: str) -> Any:
    if name == "ClinicalExtractor":
        _prepare_internal_import()
        from .extractor import ClinicalExtractor

        _disable_dspy_cache()
        return ClinicalExtractor
    if name == "VLLMClient":
        from .client import VLLMClient

        return VLLMClient
    raise AttributeError(name)


def _prepare_internal_import() -> None:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")
    os.environ.setdefault("DSPY_CACHEDIR", os.devnull)
    logging.getLogger("dspy.clients").setLevel(logging.CRITICAL)


def _disable_dspy_cache() -> None:
    import dspy

    dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=False)
