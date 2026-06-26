"""CLI entry point for the ExECTv2 component-transition examples artifacts."""

from __future__ import annotations

from datetime import date

# ``frontend_review`` anchors the reports <-> frontend_review re-export cycle
# (frontend_review re-exports the cached report builders at its bottom). Importing
# it first lets the report module below resolve cleanly when this CLI is imported
# or run standalone.
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2 import (  # noqa: F401
    frontend_review as _frontend_review,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_transition_examples import (
    write_component_transitions_artifacts,
)


def main() -> None:
    paths = write_component_transitions_artifacts(generated_on=date.today().isoformat())
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
