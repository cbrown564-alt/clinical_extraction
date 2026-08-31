"""Live Holgate-like find on the frozen 250-letter development sample."""

from __future__ import annotations

import json

from clinical_extraction.paper.gan import run_gan
from clinical_extraction.paper.gan_holgate_dev250 import (
    SAMPLE_ID,
    draw_holgate_dev250_indices,
)


def main() -> None:
    indices = draw_holgate_dev250_indices()
    result = run_gan(
        "gan_llm_extract_holgate_like",
        "gemini37flash",
        live=True,
        split="dev750",
        source_row_indices=indices,
        work_leaf=SAMPLE_ID,
        progress_every=25,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
