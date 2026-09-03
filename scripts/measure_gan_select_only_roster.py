#!/usr/bin/env python3
"""Measure six-model rule select without encode on Gan test450.

Protocol: docs/research/gan2026/gan_select_only_roster_test450_protocol_2026-09-03.md
Report: docs/research/gan2026/gan_select_only_roster_test450_2026-09-03.md

Zero model calls. Holdout is aggregate-only.

Usage:
  source .venv/bin/activate
  python scripts/measure_gan_select_only_roster.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.paper.gan_select_only_roster import (
    DEFAULT_ARTIFACT,
    measure_and_write,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help=f"Aggregate JSON path (default: {DEFAULT_ARTIFACT})",
    )
    args = parser.parse_args()
    path = measure_and_write(path=args.out)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
