"""CLI entry point for the ExECTv2 prescription projection pilot."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.prescription_projection_pilot import (
    build_prescription_projection_pilot,
    read_jsonl_rows,
    write_pilot_json,
    write_pilot_markdown,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 prescription projection pilot report",
    )
    parser.add_argument("--input-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args(argv)

    rows = read_jsonl_rows(args.input_jsonl)
    pilot = build_prescription_projection_pilot(
        rows,
        source_artifact=args.input_jsonl.as_posix(),
    )
    write_pilot_json(pilot, args.output_json)
    write_pilot_markdown(pilot, args.output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
