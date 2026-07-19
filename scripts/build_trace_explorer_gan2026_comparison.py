"""Build the Gan selector from complete governed validation750 artifacts."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.trace_explorer.gan2026_comparison import (
    discover_gan2026_validation_runs,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/gan2026/six_model_validation_comparison_20260718.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("frontend/frontend/public/mock-data/pipeline-families.json"),
    )
    args = parser.parse_args(argv)
    config = (
        args.config if args.config.is_absolute() else args.repo_root / args.config
    )
    output = args.output if args.output.is_absolute() else args.repo_root / args.output
    expected_indices = {
        int(record.source_row_index) for record in load_records_for_split("validation")
    }
    discovery = discover_gan2026_validation_runs(
        config,
        expected_indices=expected_indices,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(discovery.catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
