"""Stable observatory-facing facade for Gan 2026 cached report builders and registry readers.

Observatory routers should import from this module rather than deep-importing
``artifact_analysis/*`` monoliths or cross-task report modules. Both the live
API routes and static frontend mock generators can depend on this surface so
served data and committed dev fallbacks stay aligned.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    cached_gan_reliability_scorecard_json,
    cached_gan_reliability_scorecard_payload,
)
from clinical_extraction.core.registry import (
    load_run_registry,
)

_MOCK_DATA_DIR = discover_repo_root() / "frontend" / "public" / "mock-data" / "gan2026"


def _load_mock_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def cached_component_stage_ladder_payload() -> dict[str, Any]:
    return _load_mock_payload(_MOCK_DATA_DIR / "component-ablation.json")


@lru_cache(maxsize=1)
def cached_component_stage_ladder_json() -> str:
    return json.dumps(cached_component_stage_ladder_payload(), ensure_ascii=False)


@lru_cache(maxsize=1)
def cached_component_transitions_payload() -> dict[str, Any]:
    return _load_mock_payload(_MOCK_DATA_DIR / "component-transitions.json")


@lru_cache(maxsize=1)
def cached_component_transitions_json() -> str:
    return json.dumps(cached_component_transitions_payload(), ensure_ascii=False)


__all__ = [
    "cached_component_stage_ladder_json",
    "cached_component_stage_ladder_payload",
    "cached_component_transitions_json",
    "cached_component_transitions_payload",
    "cached_gan_reliability_scorecard_json",
    "cached_gan_reliability_scorecard_payload",
    "load_run_registry",
]
