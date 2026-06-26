"""CLI runner for the ExECTv2 Investigations verifier."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    run_verifier_cli,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as verifier,
)


def main() -> None:
    run_verifier_cli(
        verifier,
        prefix="exectv2_llm_investigations_verifier",
        description="ExECTv2 Investigations verifier over a structured key-entity draft",
        verifier_display_name="Investigations verifier",
        entity_headline_key="investigations",
        headline_label="Investigations",
        default_max_tokens=1800,
    )


if __name__ == "__main__":
    main()
