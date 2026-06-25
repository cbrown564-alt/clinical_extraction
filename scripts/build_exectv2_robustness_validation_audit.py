"""Build the ExECTv2 aggregate robustness validation audit."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    robustness_validation,
)


def main() -> None:
    path = robustness_validation.write_report()
    print(f"Robustness validation audit: {path}")


if __name__ == "__main__":
    main()
