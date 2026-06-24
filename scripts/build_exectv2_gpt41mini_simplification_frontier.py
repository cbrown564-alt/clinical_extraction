"""Build the ExECTv2 GPT-4.1-mini simplification frontier artifacts."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.simplification_frontier import (
    write_simplification_frontier_artifacts,
)


def main() -> None:
    paths = write_simplification_frontier_artifacts()
    print(f"Frontier JSON: {paths['json']}")
    print(f"Frontier report: {paths['markdown']}")
    for path in paths["candidate_json"]:
        print(f"Candidate JSON: {path}")


if __name__ == "__main__":
    main()
