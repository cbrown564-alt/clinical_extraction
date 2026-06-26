"""CLI entry point for the ExECTv2 focused-lane component-evidence replay."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.focused_lane_component_evidence import (
    DEFAULT_CONTROL_ARTIFACT,
    DEFAULT_DIAGNOSIS_ARTIFACT,
    DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    DEFAULT_OUT_JSON,
    DEFAULT_OUT_JSONL,
    DEFAULT_OUT_MD,
    DEFAULT_SF_ARTIFACT,
    write_focused_lane_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 focused-lane component-evidence no-call replay",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--row-count", type=int, default=140)
    parser.add_argument("--control-artifact", type=Path, default=DEFAULT_CONTROL_ARTIFACT)
    parser.add_argument("--diagnosis-artifact", type=Path, default=DEFAULT_DIAGNOSIS_ARTIFACT)
    parser.add_argument("--sf-artifact", type=Path, default=DEFAULT_SF_ARTIFACT)
    parser.add_argument(
        "--focused-comparator-artifact",
        type=Path,
        default=DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    )
    parser.add_argument("--out-jsonl", type=Path, default=DEFAULT_OUT_JSONL)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    outputs = write_focused_lane_outputs(
        out_jsonl=args.out_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
        row_count=args.row_count,
        control_artifact=args.control_artifact,
        diagnosis_artifact=args.diagnosis_artifact,
        sf_artifact=args.sf_artifact,
        focused_comparator_artifact=args.focused_comparator_artifact,
    )
    for name, path in outputs.items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
