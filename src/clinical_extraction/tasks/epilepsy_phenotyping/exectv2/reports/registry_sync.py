"""Canonical run-registry registration for ExECTv2 scorecards.

ExECTv2 shares the Gan 2026 run registry (``experiments/registry.jsonl``) and its
rendered human index (``experiments/RUN_INDEX.md``). RUN_INDEX.md is a pure render
of the JSONL — it must never be hand-edited. This helper performs the canonical
register-and-render cycle used by every Gan 2026 driver: load the typed registry,
replace any row with the same ``run_id``, append the new typed entry, write the
JSONL back, and re-render the Markdown index from it.
"""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
DEFAULT_RUN_INDEX_PATH = Path("experiments/RUN_INDEX.md")


def register_run(
    entry: RunRegistryEntry,
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    run_index_path: Path = DEFAULT_RUN_INDEX_PATH,
    repo_root: Path = REPO_ROOT,
) -> None:
    """Register ``entry`` in the JSONL registry and re-render RUN_INDEX.md.

    The new entry's artifact paths are checked for existence; legacy rows are not
    re-validated so a single backfilled or shorthand artifact path cannot block a
    fresh registration.
    """

    validate_run_registry_artifacts([entry], repo_root=repo_root)
    entries = [
        existing
        for existing in load_run_registry(registry_path)
        if existing.run_id != entry.run_id
    ]
    entries.append(entry)
    write_run_registry(entries, registry_path)
    write_run_registry_markdown(load_run_registry(registry_path), run_index_path)
