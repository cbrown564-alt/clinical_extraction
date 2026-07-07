"""Reconcile Gan run-registry rows with Explorer/Component Impact curation."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.core.registry import (
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_surfacing import (
    reconcile_registry_entries,
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not locate repository root")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=_repo_root() / "experiments" / "registry.jsonl",
        help="Path to experiments/registry.jsonl",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate surfaced replay artifacts after reconcile without writing",
    )
    args = parser.parse_args()
    repo_root = _repo_root()
    entries = load_run_registry(args.registry)
    reconciled = reconcile_registry_entries(entries)
    surfaced = [entry for entry in reconciled if entry.surface_as_architecture]
    validate_run_registry_artifacts(surfaced, repo_root=repo_root)
    if args.check:
        print(f"Validated {len(reconciled)} registry rows at {args.registry}")
        return
    write_run_registry(reconciled, args.registry)
    print(f"Wrote {len(reconciled)} registry rows ({len(surfaced)} surfaced) to {args.registry}")


if __name__ == "__main__":
    main()
