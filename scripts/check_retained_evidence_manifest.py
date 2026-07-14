#!/usr/bin/env python3
"""Validate the paper-facing retained-evidence manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.core.retained_evidence import (
    load_retained_evidence_manifest,
    validate_retained_evidence_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("docs/experiments/retained_evidence_manifest.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    manifest = load_retained_evidence_manifest(manifest_path)
    validate_retained_evidence_manifest(
        manifest,
        repo_root=root,
        registry_path=root / "experiments" / "registry.jsonl",
    )
    print(f"retained evidence manifest valid: {manifest_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
