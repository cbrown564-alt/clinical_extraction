"""Write the ADR 0030 target-indicator report from an existing routed JSON."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    build_target_indicator_report,
    render_target_indicator_markdown,
)

DEFAULT_SOURCE_JSON = Path(
    "experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-json", type=Path, default=DEFAULT_SOURCE_JSON)
    parser.add_argument("--target-f1", type=float, default=0.9)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    today = date.today().isoformat().replace("-", "")
    out_json = args.out_json or Path(
        f"experiments/exectv2_adr0030_target_indicator_report_dev140_{today}.json"
    )
    out_md = args.out_md or Path(
        "docs/experiments/exectv2/key_entities/"
        f"exectv2_adr0030_target_indicator_report_{today}.md"
    )
    source_report = json.loads(args.source_json.read_text(encoding="utf-8"))
    report = build_target_indicator_report(source_report, threshold=args.target_f1)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_target_indicator_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

