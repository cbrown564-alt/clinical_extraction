#!/usr/bin/env python3
"""Measure Gan extract content recall from saved Gemini extract outputs.

Protocol: docs/research/gan2026/gan_candidate_set_recall_test450_protocol_2026-09-03.md
Report: docs/research/gan2026/gan_extract_content_recall_2026-09-03.md

Zero model calls. Holdout is aggregate-only.

Usage:
  source .venv/bin/activate
  python scripts/measure_gan_extract_content_recall.py
  python scripts/measure_gan_extract_content_recall.py --split test450
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.paper.gan_extract_content_recall import (
    DEFAULT_ARTIFACT,
    measure_and_write,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split",
        choices=("dev750", "test450", "both"),
        default="both",
        help="Split to measure (default: both)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help=f"Aggregate JSON path (default: {DEFAULT_ARTIFACT})",
    )
    args = parser.parse_args()
    splits = ("dev750", "test450") if args.split == "both" else (args.split,)
    path = measure_and_write(splits, path=args.out)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
