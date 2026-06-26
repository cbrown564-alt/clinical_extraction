"""CLI runner for the ExECTv2 Diagnosis verifier."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    run_verifier_cli,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_verifier as verifier,
)


def main() -> None:
    run_verifier_cli(
        verifier,
        prefix="exectv2_llm_diagnosis_verifier",
        description="ExECTv2 Diagnosis verifier over a structured key-entity draft",
        verifier_display_name="diagnosis verifier",
        entity_headline_key="diagnosis",
        headline_label="Diagnosis",
        default_max_tokens=2400,
    )


if __name__ == "__main__":
    main()
