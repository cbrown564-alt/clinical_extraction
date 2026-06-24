"""Render the ExECTv2 reliability scorecard JSON used by the frontend fallback."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    REPO_ROOT,
    build_gan_reliability_scorecard_payload,
    build_reliability_scorecard_payload,
)


def main() -> None:
    outputs = {
        "exectv2": build_reliability_scorecard_payload(),
        "gan2026": build_gan_reliability_scorecard_payload(),
    }
    for dataset, payload in outputs.items():
        out_path = (
            REPO_ROOT
            / "frontend"
            / "public"
            / "mock-data"
            / dataset
            / "reliability-scorecard.json"
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"Wrote {dataset} reliability scorecard fallback: "
            f"{out_path.relative_to(REPO_ROOT).as_posix()}"
        )
        print(
            f"  Dimensions: {len(payload['dimensions'])}; "
            f"comparison rows: {len(payload['comparison_rows'])}"
        )


if __name__ == "__main__":
    main()
