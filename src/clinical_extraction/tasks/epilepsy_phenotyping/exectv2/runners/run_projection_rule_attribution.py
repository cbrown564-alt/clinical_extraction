"""Build an ExECTv2 projection-rule attribution sidecar from saved JSONL rows."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.projection_rule_attribution import (  # noqa: E501
    build_projection_rule_sidecar,
    read_jsonl_rows,
    render_projection_rule_sidecar_markdown,
)

DEFAULT_SOURCE_JSONLS = (
    Path(
        "experiments/"
        "exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_"
        "ollama_cpu_ctx16384_20260619.jsonl"
    ),
    Path(
        "experiments/"
        "exectv2_target_indicators_single_call_v040_reproject_v039live_dev25_qwen36_35b_"
        "ollama_cpu_ctx16384_20260619.jsonl"
    ),
    Path(
        "experiments/"
        "exectv2_target_indicators_single_call_v041_reproject_v040live_dev25_qwen36_35b_"
        "ollama_cpu_ctx16384_20260619.jsonl"
    ),
    Path(
        "experiments/"
        "exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_"
        "ollama_cpu_ctx16384_20260619.jsonl"
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-jsonl",
        type=Path,
        action="append",
        default=None,
        help="Saved target-indicator JSONL artifact. May be repeated.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    source_paths = tuple(args.source_jsonl or DEFAULT_SOURCE_JSONLS)
    missing = [path for path in source_paths if not path.exists()]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing source JSONL artifact(s): {joined}")

    rows = [row for path in source_paths for row in read_jsonl_rows(path)]
    sidecar = build_projection_rule_sidecar(rows)

    today = date.today().isoformat().replace("-", "")
    out_json = args.out_json or Path(
        f"experiments/exectv2_projection_rule_attribution_sidecar_dev25_{today}.json"
    )
    out_md = args.out_md or Path(
        "docs/experiments/exectv2/key_entities/"
        f"exectv2_projection_rule_attribution_sidecar_dev25_{today}.md"
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_projection_rule_sidecar_markdown(sidecar), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
