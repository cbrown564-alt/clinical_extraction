"""Write the ExECTv2 deterministic dev140 published-metric reproduction."""

from __future__ import annotations

import argparse
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    published_metric_reproduction,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--generated-on", default="2026-07-14")
    args = parser.parse_args()
    report = published_metric_reproduction.write_deterministic_dev140_reproduction(
        out_json=args.out_json,
        out_md=args.out_md,
        generated_on=args.generated_on,
    )
    scores = report["development_result"]["scores"]
    print(
        "all_features macro per-item F1: "
        f"{scores['all_features']['macro_per_item']['f1']:.4f}"
    )


if __name__ == "__main__":
    main()
