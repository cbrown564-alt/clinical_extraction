#!/usr/bin/env python3
"""Replay all six retained architecture cells without model calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.core.retained_evidence import load_retained_evidence_manifest
from clinical_extraction.reference_evidence_verification import verify_reference_cells


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
    results = verify_reference_cells(
        load_retained_evidence_manifest(manifest_path), repo_root=root
    )
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
