"""Build the ExECTv2 aggregate calibration validation audit."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    calibration_validation,
)


def main() -> None:
    path = calibration_validation.write_report()
    print(f"Calibration validation audit: {path}")


if __name__ == "__main__":
    main()
