"""CLI entry point for the ExECTv2 calibration-validation report."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.calibration_validation import (
    REPO_ROOT,
    write_report,
)


def main() -> None:
    path = write_report()
    print(path.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    raise SystemExit(main())
