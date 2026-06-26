"""CLI runner for the ExECTv2 Prescription/Investigations verifier."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli.common import (
    run_verifier_cli,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_med_inv_verifier as verifier,
)


def _print_med_inv_headlines(summary: dict) -> None:
    clinical = summary.get("clinical_recovery", {})
    for entity in verifier.TARGET_ENTITIES:
        score = clinical.get(entity, {})
        print(
            f"{entity} clinical headline: "
            f"P={score.get('precision', 0):.3f} "
            f"R={score.get('recall', 0):.3f} "
            f"F1={score.get('f1', 0):.3f}",
            flush=True,
        )


def main() -> None:
    run_verifier_cli(
        verifier,
        prefix="exectv2_llm_med_inv_verifier",
        description="ExECTv2 Prescription/Investigations verifier over a structured draft",
        verifier_display_name="Prescription/Investigations verifier",
        default_max_tokens=2600,
        print_headlines=_print_med_inv_headlines,
    )


if __name__ == "__main__":
    main()
