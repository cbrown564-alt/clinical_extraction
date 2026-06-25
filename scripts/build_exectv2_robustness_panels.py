"""Build ExECTv2 deterministic robustness panel preflight artifacts."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.robustness_panels import (
    write_robustness_panel_artifacts,
)


def main() -> None:
    paths = write_robustness_panel_artifacts()
    print(f"Robustness panel JSON: {paths['json']}")
    print(f"Robustness panel report: {paths['markdown']}")


if __name__ == "__main__":
    main()
