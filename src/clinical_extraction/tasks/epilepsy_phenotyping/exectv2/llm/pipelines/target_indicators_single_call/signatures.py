"""DSPy signature and module for the target-indicators single-call extractor.

Pure relocation from ``llm_target_indicators_single_call``.
"""

from __future__ import annotations

import dspy


class ExECTv2TargetIndicatorsSignature(dspy.Signature):
    """Extract the four ADR 0030 target indicators from one clinical letter."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and four target-indicator instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"entity\": ..., \"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": \"\"}, ...]}. Do not include prose outside JSON."
        )
    )


class DspyTargetIndicatorsExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2TargetIndicatorsSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)
