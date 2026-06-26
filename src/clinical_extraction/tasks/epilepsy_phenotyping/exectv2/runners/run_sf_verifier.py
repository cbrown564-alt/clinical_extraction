"""CLI runner for the ExECTv2 SeizureFrequency verifier."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    run_verifier_cli,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_verifier as verifier,
)


def main() -> None:
    run_verifier_cli(
        verifier,
        prefix="exectv2_llm_sf_verifier",
        description="ExECTv2 SeizureFrequency verifier over a structured key-entity draft",
        verifier_display_name="SeizureFrequency verifier",
        entity_headline_key="seizure_frequency",
        headline_label="SeizureFrequency",
        default_max_tokens=2400,
    )


if __name__ == "__main__":
    main()
