"""CLI for replaying Gan 2026 ClinicalAssessment projection/render mechanics."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_selector_schema_probe as selector_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_projection_render as projection_render,
)

DEFAULT_ASSESSMENT_JSONL_PATH = projection_render.DEFAULT_ASSESSMENT_JSONL_PATH
DEFAULT_CANDIDATE_SET_JSONL_PATH = projection_render.DEFAULT_CANDIDATE_SET_JSONL_PATH
DEFAULT_JSONL_PATH = projection_render.DEFAULT_JSONL_PATH
DEFAULT_JSON_PATH = projection_render.DEFAULT_JSON_PATH
DEFAULT_REPORT_PATH = projection_render.DEFAULT_REPORT_PATH


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Replay Gan 2026 ClinicalAssessment projection/render mechanics.",
    )
    parser.add_argument("--assessment-jsonl", type=Path, default=DEFAULT_ASSESSMENT_JSONL_PATH)
    parser.add_argument(
        "--candidate-set-jsonl",
        type=Path,
        default=DEFAULT_CANDIDATE_SET_JSONL_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--disable-ablation-switch",
        action="append",
        default=[],
        help="Named reset-stage ablation switch to disable for this replay.",
    )
    args = parser.parse_args(argv)

    candidate_sets = selector_probe.load_candidate_sets(args.candidate_set_jsonl)
    rows, metadata = projection_render.build_projection_render_artifact(
        load_jsonl_rows(args.assessment_jsonl),
        candidate_sets=candidate_sets,
        assessment_artifact_path=str(args.assessment_jsonl),
        candidate_set_artifact_path=str(args.candidate_set_jsonl),
        disabled_ablation_switches=set(args.disable_ablation_switch),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    projection_render.write_summary_json(metadata, args.json_path)
    projection_render.write_report(
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
